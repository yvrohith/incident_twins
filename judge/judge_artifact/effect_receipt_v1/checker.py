"""Public-evidence-only versioned checker and two deliberately simple baselines."""
import argparse
import json
from pathlib import Path

try:
    from .model import MODEL_VERSION, enumerate_histories, projection
except ImportError:
    from model import MODEL_VERSION, enumerate_histories, projection

SCHEMA = 'effect-receipt-checker/1'
TARGET = ('run', 'task', 'resource')
INTERVAL = '(parent_stop_confirmed, observation_horizon]'
POLICY = 'cancel-and-await-parent; accepted detached worker may complete; no retries'


class Unsupported(ValueError):
    pass


class Inconsistent(ValueError):
    pass


def result(profile, status, verdict=None, reasons=(), **fields):
    return {'schema': SCHEMA, 'model': MODEL_VERSION, 'profile': profile,
            'status': status, 'verdict': verdict, 'reasons': list(reasons), **fields}


def same_scope(row, claim):
    return isinstance(row, dict) and all(row.get(k) == claim[k] for k in TARGET)


def bound(row, claim):
    return same_scope(row, claim) and row.get('epoch') == claim['epoch']


def validate_public(public, profile):
    if profile not in ('native', 'journal'):
        raise Unsupported('unknown evidence profile')
    if public.get('schema') != 'effect-receipt/1' or public.get('design') not in ('A', 'B'):
        raise Unsupported('unrecognized schema or generation design')
    claim = public.get('claim', {})
    if any(not isinstance(claim.get(k), str) or not claim[k] for k in (*TARGET, 'epoch')):
        raise Unsupported('missing claim binding')
    if claim.get('interval') != INTERVAL:
        raise Unsupported('unsupported interval')
    if not isinstance(public.get('controller'), list) or not isinstance(public.get('worker'), dict):
        raise Unsupported('missing controller or native worker source')
    kinds = ('registered', 'parent_stop_requested', 'parent_stop_confirmed',
             'post_stop_permission', 'observation_horizon')
    events = public['controller']
    selected = []
    for kind in kinds:
        matches = [e for e in events if e.get('kind') == kind]
        if len(matches) != 1:
            raise Unsupported('missing or nonunique controller boundary: ' + kind)
        selected.append(matches[0])
    registered, requested, stopped, permission, horizon = selected
    if requested.get('policy') != POLICY:
        raise Unsupported('stop policy differs from the pinned supplement contract')
    ns = [e.get('mono_ns') for e in selected]
    if not all(isinstance(t, int) and t >= 0 for t in ns) or ns != sorted(ns) or len(set(ns)) != len(ns):
        raise Inconsistent('controller causal ordering is invalid')
    if not same_scope(registered, claim):
        raise Inconsistent('registration does not bind the target')
    if any(e.get('epoch') != claim['epoch'] for e in (stopped, permission, horizon)):
        raise Unsupported('controller epoch does not cover claim')
    if stopped.get('cancel_accepted') is not True or stopped.get('task_cancelled') is not True:
        raise Unsupported('parent stop was not confirmed')
    if horizon.get('quiescent') is not True:
        raise Unsupported('no quiescent local horizon boundary')
    begin, end = horizon.get('snapshot_start_ns'), horizon.get('snapshot_end_ns')
    if not isinstance(begin, int) or not isinstance(end, int) or not permission['mono_ns'] < begin <= end <= horizon['mono_ns']:
        raise Inconsistent('snapshot does not lie in the post-stop interval')
    worker = public['worker']
    if registered.get('worker_pid') != worker.get('pid') or not isinstance(worker.get('events'), list):
        raise Inconsistent('worker identity or event list is invalid')
    if worker.get('exit_at_h') not in (None, -9, 0):
        raise Unsupported('process outcome is outside the declared fault model')
    if 'exit_at_h' not in worker or 'stderr_at_h' not in worker:
        raise Unsupported('missing lifecycle source')
    if worker['stderr_at_h']:
        raise Unsupported('worker error requires separate failure investigation')
    # The real framework tool return establishes the one accepted task binding.
    native = public.get('native')
    if not isinstance(native, dict) or not isinstance(native.get('messages'), dict) or not isinstance(native.get('spans'), list):
        raise Unsupported('missing complete retained framework source')
    parts = [part for message in native['messages'].get('root', []) for part in message.get('parts', [])]
    calls = [part for part in parts if part.get('part_kind') == 'tool-call']
    if len(calls) != 1 or calls[0].get('tool_name') != 'enqueue_artifacts' or calls[0].get('args') != {'payload': 'dummy artifact'}:
        raise Unsupported('framework tool calls differ from the pinned route')
    returns = [part for message in native['messages'].get('root', []) for part in message.get('parts', [])
               if part.get('part_kind') == 'tool-return' and part.get('tool_name') == 'enqueue_artifacts']
    if len(returns) != 1:
        raise Unsupported('expected one native accepted-task return')
    content = returns[0].get('content', {})
    receipts = content.get('receipts', []) if isinstance(content, dict) else []
    if content.get('run') != claim['run'] or len(receipts) != 1 or not all(
            receipts[0].get(k) == claim[k] for k in ('task', 'resource')) or receipts[0].get('accepted') is not True or receipts[0].get('owner') != 'root':
        raise Inconsistent('framework accepted-task return has incorrect binding')
    if not calls[0].get('tool_call_id') or calls[0].get('tool_call_id') != returns[0].get('tool_call_id'):
        raise Inconsistent('framework call and return identities disagree')
    names = sorted(span.get('name', '') for span in native['spans'])
    if names != sorted(['chat function:model:', 'chat function:model:', 'execute_tool enqueue_artifacts', 'invoke_agent artifact_parent']):
        raise Unsupported('native span inventory differs from the pinned integration')
    tool_span = next(span for span in native['spans'] if span['name'] == 'execute_tool enqueue_artifacts')
    attrs = tool_span.get('attributes', {})
    try:
        span_result = json.loads(attrs.get('gen_ai.tool.call.result', 'null'))
    except (TypeError, ValueError) as exc:
        raise Inconsistent('malformed native tool span result') from exc
    if span_result != content or attrs.get('gen_ai.tool.call.id') != calls[0]['tool_call_id'] or attrs.get('gen_ai.tool.name') != 'enqueue_artifacts':
        raise Inconsistent('native span and framework task return disagree')
    collection = public.get('collection', {})
    if 'recovery' in public and (public['recovery'].get('original_epoch') != claim['epoch'] or
            public['recovery'].get('new_effect_permission') is not False or
            collection.get('interval_sealed_at_h') is not True):
        raise Unsupported('later retrieval lacks a sealed original interval')
    if profile == 'journal':
        if not isinstance(public.get('audit_snapshot'), list):
            raise Unsupported('missing audit source; metadata alone is not a snapshot')
        if collection.get('epoch') != claim['epoch'] or not same_scope(collection.get('scope'), claim):
            raise Unsupported('stale or incorrectly scoped collection certificate')
        for flag in ('snapshot_complete_over_audit_rows', 'interval_closed_at_h',
                     'all_effect_routes_registered', 'worker_stable_during_snapshot'):
            if collection.get(flag) is not True:
                raise Unsupported('unsupported collection assumption: ' + flag)
        if collection.get('fault_model') != 'process-interruption-v1':
            raise Unsupported('wrong fault domain')
        if collection.get('atomic_generation') is not (public['design'] == 'B'):
            raise Unsupported('generation guarantee disagrees with pinned design')
    return claim, horizon


def semantic_observation(public, profile='native'):
    """Interpret declared fields without altering or returning the input's raw view."""
    claim, horizon = validate_public(public, profile)
    worker = public['worker']
    selected = []
    positives = []
    recovered = []
    allowed = {'worker_accepted', 'worker_started', 'receipt_delivered', 'worker_completed', 'worker_cancelled'}
    previous = -1
    for event in worker['events']:
        if not isinstance(event, dict) or not isinstance(event.get('mono_ns'), int):
            raise Inconsistent('malformed worker event')
        if event['mono_ns'] < previous:
            raise Inconsistent('worker event order is inconsistent')
        previous = event['mono_ns']
        if event['mono_ns'] > horizon['mono_ns']:
            if 'recovery' not in public:
                raise Inconsistent('at-H view includes a later worker event')
            if same_scope(event, claim) and event.get('pid') == worker['pid'] and event.get('kind') == 'receipt_delivered' and bound(event.get('receipt'), claim):
                _validate_row(event['receipt'])
                recovered.append(event['receipt'])
            continue
        if not same_scope(event, claim):
            continue
        if event.get('pid') != worker['pid']:
            raise Inconsistent('worker event PID does not bind registered worker')
        kind = event.get('kind')
        if kind not in allowed:
            raise Unsupported('unmodeled operational worker observation')
        if kind in ('worker_started', 'receipt_delivered') and event['mono_ns'] <= next(
                e['mono_ns'] for e in public['controller'] if e['kind'] == 'post_stop_permission'):
            raise Inconsistent('worker effect activity predates its permission')
        if kind == 'worker_started' and event.get('epoch') != claim['epoch']:
            raise Inconsistent('worker start is in a different epoch')
        if kind == 'receipt_delivered':
            row = event.get('receipt')
            if not bound(row, claim):
                # A positive about another target is not a positive about this claim.
                continue
            _validate_row(row)
            positives.append(row)
        selected.append(kind)
    observation = {'events': selected, 'exit_at_h': worker['exit_at_h'],
                   'target_delivered_receipts': len(positives)}
    if recovered:
        observation['recovered_target_receipts'] = len(recovered)
    if profile == 'journal':
        rows = [row for row in public['audit_snapshot'] if bound(row, claim)]
        for row in rows:
            _validate_row(row)
        if len(rows) > 1 or len({row['effect_id'] for row in rows}) != len(rows):
            raise Inconsistent('more than one target effect in a one-effect model')
        if recovered and rows and recovered[0] != rows[0]:
            raise Inconsistent('late delivery disagrees with the retained original-interval record')
        if positives and rows and positives[0] != rows[0]:
            raise Inconsistent('delivery and snapshot disagree about the effect record')
        observation['target_audit_rows'] = len(rows)
    return observation


def _validate_row(row):
    if row.get('effect_id') != 'effect-0' or row.get('payload') != 'dummy artifact':
        raise Inconsistent('receipt content conflicts with the pinned one-effect route')


def analyze(public, profile='native', max_histories=None):
    if max_histories is not None and (not isinstance(max_histories, int) or isinstance(max_histories, bool) or max_histories < 0):
        return result(profile, 'unsupported', reasons=['invalid search cap'])
    try:
        observed = semantic_observation(public, profile)
    except Unsupported as exc:
        return result(profile, 'unsupported', reasons=[str(exc)])
    except (Inconsistent, KeyError, TypeError, AttributeError) as exc:
        return result(profile, 'inconsistent', reasons=[str(exc)])
    histories = enumerate_histories(public['design'])
    searched = histories if max_histories is None else histories[:max_histories]
    complete = len(searched) == len(histories)
    at_h = {key: value for key, value in observed.items() if key != 'recovered_target_receipts'}
    compatible = [h for h in searched if projection(h, profile) == at_h and
                  (not observed.get('recovered_target_receipts') or h['state']['receipt'])]
    counts = {'Q_true': sum(h['Q'] for h in compatible), 'Q_false': sum(not h['Q'] for h in compatible)}
    witnesses = {key: next((h for h in compatible if h['Q'] == q), None)
                 for key, q in (('Q_true', True), ('Q_false', False))}
    extra = {'search': {'enumerated': len(searched), 'total_bounded_histories': len(histories), 'complete': complete},
             'compatible': counts, 'semantic_observation': observed,
             'witness_equality': 'declared semantic projection only', 'witnesses': witnesses}
    if not complete:
        # A witnessed opposing pair is sufficient for ambiguity; uniform prefixes are not proofs.
        verdict = 'UNRESOLVED' if counts['Q_true'] and counts['Q_false'] else None
        return result(profile, 'incomplete', verdict, ['bounded search cap reached'], **extra)
    if not compatible:
        return result(profile, 'inconsistent', reasons=['no compatible history in declared fault domain'], **extra)
    verdict = 'UNRESOLVED' if counts['Q_true'] and counts['Q_false'] else 'ESTABLISHED' if counts['Q_true'] else 'REFUTED'
    return result(profile, 'complete', verdict, **extra)


def conservative(public):
    """A faithful scoped delivered receipt refutes; absence is an abstention."""
    try:
        observation = semantic_observation(public, 'native')
        verdict = 'REFUTED' if (observation['target_delivered_receipts'] or observation.get('recovered_target_receipts')) else 'UNRESOLVED'
        return result('conservative', 'complete', verdict)
    except Unsupported as exc:
        return result('conservative', 'unsupported', reasons=[str(exc)])
    except (Inconsistent, KeyError, TypeError, AttributeError) as exc:
        return result('conservative', 'inconsistent', reasons=[str(exc)])


def direct_query(public):
    """Direct scoped audit query under the same supported atomic/source contract."""
    try:
        observation = semantic_observation(public, 'journal')
        if observation['target_audit_rows']:
            verdict = 'REFUTED'
        elif public['design'] == 'B':
            verdict = 'ESTABLISHED'
        else:
            verdict = 'UNRESOLVED'
        if (observation['target_delivered_receipts'] or observation.get('recovered_target_receipts')) and not observation['target_audit_rows']:
            return result('direct_query', 'inconsistent', reasons=['faithful delivery is absent from a complete retained audit source'])
        return result('direct_query', 'complete', verdict)
    except Unsupported as exc:
        return result('direct_query', 'unsupported', reasons=[str(exc)])
    except (Inconsistent, KeyError, TypeError, AttributeError) as exc:
        return result('direct_query', 'inconsistent', reasons=[str(exc)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('public', type=Path)
    parser.add_argument('--profile', choices=('native', 'journal'), default='journal')
    parser.add_argument('--max-histories', type=int)
    args = parser.parse_args()
    print(json.dumps(analyze(json.loads(args.public.read_text()), args.profile, args.max_histories), indent=2, sort_keys=True))
