"""Release-only saved-evidence runtime policy; scientific generation pins do not change."""
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parent


def read_policy():
    policy = json.loads((ROOT / 'runtime_policy.json').read_bytes())
    validation = json.loads((ROOT / policy['validated_version_records']).read_bytes())
    exact = {tuple(map(int, row['version'].split('.'))) for row in validation['records']
             if row['implementation'] == 'CPython' and row['checks'] == row['passed']
             and row['checks'] > 0 and row['failed'] == 0 and row['all_child_imports_verified']}
    if exact != {tuple(v) for v in policy['saved_replay_cpython_versions']}:
        raise ValueError('Runtime policy and retained validation records disagree.')
    return policy, exact


def runtime_decision(implementation, version, releaselevel, strict=False, full_version=None):
    """Pure branch decision. Simulated inputs are policy tests, not interpreter runs."""
    policy, exact = read_policy()
    version = tuple(version)
    family = version[:2]
    permitted = (implementation in policy['permitted_implementations']
                 and list(family) in policy['permitted_minor_versions']
                 and releaselevel in policy['permitted_release_levels'])
    validated = implementation == 'CPython' and version in exact and releaselevel == 'final'
    accepted = permitted and (not strict or validated)
    detail = {
        'implementation': implementation,
        'version': '.'.join(map(str, version)),
        'full_version': full_version or '.'.join(map(str, version)),
        'releaselevel': releaselevel,
        'permitted_family': ('CPython ' + '.'.join(map(str, family)) + '.x') if permitted else None,
        'family_permitted': permitted,
        'exact_version_historically_validated': validated,
        'validation_status': 'historically_validated' if validated else 'not_in_frozen_historical_validation_list',
        'validation_records': policy['validated_version_records'],
        'strict_runtime_requested': bool(strict),
        'accepted': accepted,
    }
    if not permitted:
        detail['error'] = ('Use a final CPython 3.12.x or 3.13.x release with -I -S -B. '
                           'Other implementations, minor versions and prereleases are not permitted for saved replay.')
    elif strict and not validated:
        versions = ', '.join('.'.join(map(str, v)) for v in sorted(exact))
        detail['error'] = ('Strict replay requires an exact historically validated version: ' + versions
                           + '. Use one of these, or omit --strict-runtime for normal permitted-family replay; '
                           'permission does not claim that this exact patch was validated.')
    return detail


def actual_runtime(strict=False):
    return runtime_decision(platform.python_implementation(), sys.version_info[:3],
                            sys.version_info.releaselevel, strict, sys.version)


def answer_exit_status(answer):
    """Release process status only; the scientific answer is never rewritten."""
    status = answer.get('status', answer.get('analysis_status'))
    return 2 if status in ('error', 'unsupported', 'inconsistent') else 0


def provenance(runtime, error=None):
    origins = {}
    release_origins = {}
    for name, module in sorted(sys.modules.items()):
        if name == 'check_evidence' or name in ('incident_twins', 'effect_receipt_v1') or name.startswith(('incident_twins.', 'effect_receipt_v1.')):
            path = Path(module.__file__).resolve()
            if not path.is_relative_to(ROOT):
                raise RuntimeError('An investigator import escaped the extracted package')
            origins[name] = str(path)
        elif name in ('release_runtime', 'presentation'):
            path = Path(module.__file__).resolve()
            if not path.is_relative_to(ROOT):
                raise RuntimeError('A release import escaped the extracted package')
            release_origins[name] = str(path)
    result = {'packaged_module_origins': origins, 'release_module_origins': release_origins,
              'isolated': bool(sys.flags.isolated), 'site_disabled': bool(sys.flags.no_site),
              'bytecode_disabled': bool(sys.flags.dont_write_bytecode), 'runtime': runtime}
    if error:
        result['release_error'] = error
    return result
