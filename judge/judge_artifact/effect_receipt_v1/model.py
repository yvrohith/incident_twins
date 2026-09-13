"""Finite, process-fault-aware supplement model; no imports from the frozen model."""
from dataclasses import asdict, dataclass, replace
from collections import defaultdict

MODEL_VERSION = 'effect-receipt-model/1'


@dataclass(frozen=True)
class State:
    phase: str = 'accepted'
    worker: str = 'active'
    effect: bool = False
    receipt: bool = False
    delivered: bool = False
    crashed: bool = False
    cancelled: bool = False


def successors(state, design):
    """Only committed database changes survive process interruption."""
    if state.worker != 'active':
        return ()
    out = [('interrupt', replace(state, worker='dead', crashed=True))]
    # A graceful process exit is also not an effect rollback certificate.
    out.append(('cancel', replace(state, worker='done', cancelled=True)))
    if state.phase == 'accepted':
        out.append(('start', replace(state, phase='started')))
    elif state.phase == 'started':
        out.append(('prepare_transaction', replace(state, phase='prepared')))
    elif state.phase == 'prepared':
        if design == 'A':
            out.append(('commit_effect', replace(state, phase='effect_committed', effect=True)))
        else:
            out.append(('commit_effect_and_receipt', replace(state, phase='receipt_durable', effect=True, receipt=True)))
    elif state.phase == 'effect_committed':
        out.append(('prepare_audit', replace(state, phase='audit_prepared')))
    elif state.phase == 'audit_prepared':
        out.append(('commit_receipt', replace(state, phase='receipt_durable', receipt=True)))
    elif state.phase == 'receipt_durable':
        out.append(('deliver_receipt', replace(state, phase='delivered', delivered=True)))
    elif state.phase == 'delivered':
        out.append(('finish', replace(state, phase='completed', worker='done')))
    return tuple(out)


def enumerate_histories(design):
    """Every acyclic prefix is a possible horizon; no sampling or search cutoff."""
    if design not in ('A', 'B'):
        raise ValueError('design must be A or B')
    result = []
    def visit(state, transitions):
        result.append({'design': design, 'transitions': list(transitions) + ['horizon'],
                       'state': asdict(state), 'Q': not state.effect})
        for action, target in successors(state, design):
            visit(target, (*transitions, action))
    visit(State(), ('registered', 'parent_stop_confirmed', 'post_stop_permission'))
    return result


def projection(history, profile='native'):
    """Declared semantic projection; timestamps/IDs are not raw-equated by this."""
    if profile not in ('native', 'journal'):
        raise ValueError('unknown profile')
    state = history['state']
    transitions = history['transitions']
    events = ['worker_accepted']
    if 'start' in transitions:
        events.append('worker_started')
    if state['delivered']:
        events.append('receipt_delivered')
    if state['cancelled']:
        events.append('worker_cancelled')
    elif state['phase'] == 'completed':
        events.append('worker_completed')
    exit_at_h = -9 if state['worker'] == 'dead' else 0 if state['worker'] == 'done' else None
    answer = {'events': events, 'exit_at_h': exit_at_h,
              'target_delivered_receipts': int(state['delivered'])}
    if profile == 'journal':
        answer['target_audit_rows'] = int(state['receipt'])
    return answer


def exhaustive_report():
    """Check the identifiability criterion over all enumerated history pairs."""
    import json
    answer = {'schema': MODEL_VERSION, 'equality': 'declared semantic projection only',
              'horizon': 'every finite prefix; all effect transitions after permission and before H',
              'criterion_check': 'exhaustive history enumeration and grouping by full declared projection; not a literal pair loop',
              'bounds': {'tasks': 1, 'workers': 1, 'resources': 1, 'effects': 1, 'interruptions': 1,
                         'retries': 0}, 'designs': {}}
    for design in ('A', 'B'):
        histories = enumerate_histories(design)
        profiles = {}
        for profile in ('native', 'journal'):
            groups = defaultdict(list)
            for history in histories:
                groups[json.dumps(projection(history, profile), sort_keys=True)].append(history)
            mixed = [group for group in groups.values() if len({h['Q'] for h in group}) == 2]
            witness = None
            if mixed:
                # Prefer a process interruption, the empirical fault of interest.
                group = next((g for g in mixed if projection(g[0], profile)['exit_at_h'] == -9), mixed[0])
                witness = {'observation': projection(group[0], profile),
                           'Q_true': next(h for h in group if h['Q']),
                           'Q_false': next(h for h in group if not h['Q'])}
            profiles[profile] = {'observation_groups': len(groups), 'mixed_Q_groups': len(mixed),
                                 'claim_sufficient': not mixed, 'semantic_witness': witness,
                                 'ordered_pairs_covered_by_partition': len(histories) ** 2}
        answer['designs'][design] = {'histories': len(histories),
            'effect_without_receipt_histories': sum(h['state']['effect'] and not h['state']['receipt'] for h in histories),
            'atomic_effect_receipt_invariant': all(h['state']['effect'] == h['state']['receipt'] for h in histories),
            'profiles': profiles}
    return answer


if __name__ == '__main__':
    import json
    print(json.dumps(exhaustive_report(), indent=2, sort_keys=True))
