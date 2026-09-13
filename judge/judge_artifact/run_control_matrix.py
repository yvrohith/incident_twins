"""Characterize existing controls across methods; matching known defects is not a correctness certification."""
import argparse
from collections import Counter
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from release_runtime import actual_runtime, answer_exit_status, provenance

if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
    raise SystemExit('Use Python with -I -S -B.')

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--strict-runtime', action='store_true', help='require an exact historically validated CPython version, including in each child')
parser.add_argument('--output', type=Path, required=True, help='fresh directory for actual outputs and comparisons')
args = parser.parse_args()
root = Path(__file__).resolve().parent
runtime = actual_runtime(args.strict_runtime)
if not runtime['accepted']:
    print(json.dumps(provenance(runtime, runtime['error']), sort_keys=True), file=sys.stderr)
    raise SystemExit(2)
if Path(__file__).is_symlink() or any(p.is_symlink() for p in root.rglob('*')):
    print(json.dumps(provenance(runtime, 'Symlinks are not supported.'), sort_keys=True), file=sys.stderr)
    raise SystemExit(2)
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
spec = json.loads((root / 'expected' / 'control_matrix.json').read_bytes())
records = []
for example in spec['checks']:
    command = [sys.executable, '-I', '-S', '-B', str(root / 'replay.py'), example['study'],
               '--evidence', str(root / example['evidence']), '--format', 'json']
    if args.strict_runtime:
        command += ['--strict-runtime']
    if example['study'] == 'original':
        command += ['--model', str(root / example['model'])]
        required = {'check_evidence', 'incident_twins', 'incident_twins.contracts',
                    'incident_twins.instruments', 'incident_twins.model',
                    'incident_twins.observations', 'incident_twins.verdicts'}
    else:
        command += ['--method', example['method']]
        required = {'effect_receipt_v1', 'effect_receipt_v1.checker', 'effect_receipt_v1.model'}
        if example.get('max_histories') is not None:
            command += ['--max-histories', str(example['max_histories'])]
    failure = None
    with tempfile.TemporaryDirectory(prefix='incident-twins-empty-') as empty_cwd:
        try:
            proc = subprocess.run(command, cwd=empty_cwd, capture_output=True,
                                  text=True, timeout=60, check=False)
            stdout, stderr, returncode = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = (exc.stdout or b'').decode() if isinstance(exc.stdout, bytes) else exc.stdout or ''
            stderr = (exc.stderr or b'').decode() if isinstance(exc.stderr, bytes) else exc.stderr or ''
            returncode, failure = None, 'timeout after 60 seconds'
        record_cwd = empty_cwd
    (out / (example['id'] + '.stdout.json')).write_text(stdout)
    (out / (example['id'] + '.stderr.json')).write_text(stderr)
    try:
        actual = json.loads(stdout)
        origin_report = json.loads(stderr)
    except (ValueError, TypeError) as exc:
        actual, origin_report = {}, {}
        failure = str(exc)
    if example['comparison'] == 'full_answer':
        differences = {} if actual == example['expected'] else {'full_answer': {'expected': example['expected'], 'actual': actual}}
    else:
        differences = {k: {'expected': value, 'actual': actual.get(k)}
                       for k, value in example['expected'].items() if actual.get(k) != value}
    origins = origin_report.get('packaged_module_origins', {})
    origins_valid = set(origins) == required and all(
        Path(p).resolve().is_relative_to(root) for p in origins.values())
    flags_valid = all(origin_report.get(k) is True for k in ('isolated', 'site_disabled', 'bytecode_disabled'))
    expected_returncode = answer_exit_status(example['expected'])
    child_runtime = origin_report.get('runtime', {})
    runtime_valid = (child_runtime.get('accepted') is True
                     and child_runtime.get('strict_runtime_requested') == args.strict_runtime
                     and child_runtime.get('implementation') == runtime['implementation']
                     and child_runtime.get('version') == runtime['version'])
    row = {'id': example['id'], 'group': example['group'], 'command': command,
           'cwd': record_cwd, 'returncode': returncode, 'expected_returncode': expected_returncode,
           'child_runtime_policy_verified': runtime_valid, 'verdict': actual.get('verdict'),
           'status': actual.get('status', actual.get('analysis_status')), 'error': failure,
           'differences': differences, 'import_origins_verified': origins_valid,
           'isolation_flags_verified': flags_valid,
           'passed': returncode == expected_returncode and not failure and not differences and origins_valid and flags_valid and runtime_valid}
    records.append(row)
    print(example['id'] + ': ' + ('PASS' if row['passed'] else 'FAIL'))
summary = {'scope': 'Post-hoc 36-cell existing-control replay; complete-search defaults; no new evidence or worker execution',
           'runtime': {**runtime, 'platform': platform.platform()},
           'checks': len(records), 'passed': sum(r['passed'] for r in records),
           'failed': sum(not r['passed'] for r in records), 'skipped': 0,
           'groups': dict(Counter(r['group'] for r in records)),
           'expected_labels_passed_to_investigator': False,
           'private_runtime_validation_repeated': False, 'adversarial_os_sandbox': False,
           'records': records}
(out / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
summary['known_baseline_limitation'] = 'control-001: journal inconsistent / direct_query complete ESTABLISHED'
summary['passing_means_observed_output_reproduced_not_valid_conclusion'] = True
summary['original_control002_zero_cap_test_is_separate'] = True
summary['journal_direct_status_verdict_agreement'] = ({'agree': 8, 'controls': 9, 'scope': 'status and verdict, full-search settings'} if not summary['failed'] else {'verified': False})
(out / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
print('Known limitation retained: direct query establishes the contradictory control; journal refuses a verdict.')
print(json.dumps({k: summary[k] for k in ('checks', 'passed', 'failed', 'skipped', 'groups')}, sort_keys=True))
print(json.dumps(provenance(runtime), sort_keys=True), file=sys.stderr)
raise SystemExit(1 if summary['failed'] else 0)
