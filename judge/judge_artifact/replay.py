"""Release-only saved-JSON and human launcher. Scientific APIs and answers are unchanged."""
import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from release_runtime import actual_runtime, answer_exit_status, provenance


class CLIError(ValueError):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CLIError(message)


def parse(argv):
    # These release flags are accepted before or after the study name.
    shared = Parser(add_help=False)
    shared.add_argument('--format', choices=('json', 'human'), default='json')
    shared.add_argument('--strict-runtime', action='store_true')
    options, rest = shared.parse_known_args(argv)
    parser = Parser(description=__doc__, parents=[shared])
    sub = parser.add_subparsers(dest='study', required=True)
    original = sub.add_parser('original', help='Read the original study public evidence and model')
    original.add_argument('--evidence', type=Path, required=True)
    original.add_argument('--model', type=Path, required=True)
    original.add_argument('--anchor', type=Path)
    original.add_argument('--max-histories', type=int)
    extension = sub.add_parser('extension', help='Read one extension public JSON file')
    extension.add_argument('--evidence', type=Path, required=True)
    extension.add_argument('--method', choices=('native', 'journal', 'direct-query', 'conservative'), default='journal')
    extension.add_argument('--max-histories', type=int)
    sub.add_parser('model', help='Print the unchanged finite extension model report')
    args = parser.parse_args(rest)
    args.format, args.strict_runtime = options.format, options.strict_runtime
    if args.study == 'extension' and args.max_histories is not None and args.method in ('direct-query', 'conservative'):
        raise CLIError('--max-histories applies only to native or journal enumeration')
    return args


def backend(args):
    if args.study == 'model':
        from effect_receipt_v1.model import exhaustive_report
        return exhaustive_report(), 0
    if args.study == 'original':
        import check_evidence
        argv = ['--evidence', str(args.evidence), '--model', str(args.model)]
        if args.anchor:
            argv += ['--anchor', str(args.anchor)]
        if args.max_histories is not None:
            argv += ['--max-histories', str(args.max_histories)]
        output = io.StringIO()
        with redirect_stdout(output):
            status = check_evidence.main(argv)
        return json.loads(output.getvalue()), status
    from effect_receipt_v1 import checker
    try:
        public = json.loads(args.evidence.read_bytes())
        if not isinstance(public, dict):
            raise ValueError('public evidence must be a JSON object')
        if args.method in ('native', 'journal'):
            answer = checker.analyze(public, args.method, args.max_histories)
        elif args.method == 'direct-query':
            answer = checker.direct_query(public)
        else:
            answer = checker.conservative(public)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        answer = {'schema': 'incident-twins-replay-input-error/1',
                  'status': 'error', 'verdict': None, 'error': str(exc)}
    return answer, answer_exit_status(answer)


def main():
    strict = '--strict-runtime' in sys.argv[1:]
    runtime = actual_runtime(strict)
    error = None
    try:
        if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
            raise CLIError('Use Python with -I -S -B for isolated saved-evidence replay.')
        if Path(__file__).is_symlink() or any(p.is_symlink() for p in ROOT.rglob('*')):
            raise CLIError('Symlinks are not supported in this isolated package.')
        if not runtime['accepted']:
            raise CLIError(runtime['error'])
        args = parse(sys.argv[1:])
        answer, status = backend(args)
        if args.format == 'human':
            from presentation import human
            try:
                public = json.loads(args.evidence.read_bytes()) if hasattr(args, 'evidence') else None
            except (OSError, ValueError):
                public = None
            print(human(answer, args.study, getattr(args, 'method', None), public))
        else:
            print(json.dumps(answer, sort_keys=True))
        return status
    except (CLIError, OSError, ValueError) as exc:
        error = str(exc)
        print(json.dumps({'schema': 'incident-twins-replay-release-error/1',
                          'status': 'error', 'verdict': None, 'error': error}, sort_keys=True))
        return 2
    finally:
        print(json.dumps(provenance(runtime, error), sort_keys=True), file=sys.stderr)


if __name__ == '__main__':
    raise SystemExit(main())
