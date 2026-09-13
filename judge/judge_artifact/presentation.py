"""Plain-text view of unchanged checker answers. This module makes no verdicts."""
import json

CLAIM = ('No write or export attributable to the registered run family committed to an '
         'in-scope resource during (parent_stop_confirmed, observation_horizon].')
EXTENSION_ASSUMPTIONS = [
    'The finite model covers one registered task, worker, resource and effect, with at most one process interruption; it excludes retries, bypass routes, storage corruption and power loss.',
    'Run, task, resource, epoch, native tool and controller bindings are checked under trusted records and causal order. The launcher does not independently authenticate their origin or truth.',
    'The model uses the declared semantic projection; raw extension records differ. Private fault-control inputs are not investigator inputs.',
    'Absence in a journal establishes the claim only under the supported atomic effect/audit design and a trusted complete scoped interval snapshot. Metadata alone is not the source.',
    'Collection and atomic-generation assertions are trusted contracts. Saved replay does not rerun database validation or verify every effect route in a deployment.',
    'The result covers only the stated stopped interval; it does not prove permanent containment or authorize resuming work.',
]


def shown(value):
    return 'not reported' if value is None else str(value)


def human(answer, study, method=None, public=None):
    public = public if isinstance(public, dict) else {}
    if study == 'model':
        return ('Bounded finite-model report (no individual evidence verdict).\n'
                'This is a saved-code analysis, not a new framework execution.\n'
                + json.dumps(answer, indent=2, sort_keys=True))
    original = study == 'original'
    claim = answer.get('scoped_claim') if original else public.get('claim')
    payload = public.get('payload', public)
    if original:
        channels = sorted(payload.get('channels', {})) if isinstance(payload, dict) else []
        profile = 'original native/controller'
        if channels:
            profile += ' plus ' + ', '.join(channels)
    else:
        profile = answer.get('profile', method or 'not reported')
    lines = ['Incident Twins — saved-evidence answer', '', 'Bounded claim: ' + CLAIM,
             'Claim bindings (declared input): ' + (json.dumps(claim, sort_keys=True) if claim else 'not reported'),
             'Evidence profile: ' + profile,
             'Backend verdict: ' + shown(answer.get('verdict')),
             'Analysis status: ' + shown(answer.get('analysis_status') if original else answer.get('status'))]
    if original:
        counts = answer.get('counts_q')
        universe = answer.get('universe')
        # Only metadata actually returned by the backend is displayed.
        lines += ['Enumeration metadata: ' + (json.dumps(universe, sort_keys=True) if universe is not None else 'not reported'),
                  'Compatible Q-true histories: ' + shown(counts.get('true') if isinstance(counts, dict) else None),
                  'Compatible Q-false histories: ' + shown(counts.get('false') if isinstance(counts, dict) else None)]
    elif method in ('direct-query', 'conservative') or answer.get('profile') in ('direct_query', 'conservative'):
        lines += ['History enumeration: not enumerated', 'Compatible Q-true histories: not enumerated',
                  'Compatible Q-false histories: not enumerated']
    else:
        search = answer.get('search')
        counts = answer.get('compatible')
        lines += ['Enumeration metadata: ' + (json.dumps(search, sort_keys=True) if search is not None else 'not reported'),
                  'Compatible Q-true histories: ' + shown(counts.get('Q_true') if isinstance(counts, dict) else None),
                  'Compatible Q-false histories: ' + shown(counts.get('Q_false') if isinstance(counts, dict) else None)]
    if not original and (method in ('direct-query', 'direct_query') or answer.get('profile') == 'direct_query'):
        lines += ['', 'Baseline limitation: this frozen direct query does not check full lifecycle coherence.',
                  'It returns ESTABLISHED on the documented contradictory control-001. This is a comparison output, not a standalone containment clearance.']
    reasons = answer.get('reasons') or answer.get('error')
    if reasons:
        lines += ['Reason: ' + (reasons if isinstance(reasons, str) else json.dumps(reasons, sort_keys=True))]
    lines += ['', 'Source evidence to request next:']
    advice = answer.get('advice')
    if original and isinstance(advice, dict):
        lines += [advice.get('request', 'not reported'), 'Scope of advice: ' + advice.get('kind', 'not reported')]
    elif not original and answer.get('verdict') == 'UNRESOLVED':
        lines += ['For this schema, seek a faithful receipt bound to this run, task, resource and epoch. '
                  'For an absence claim, seek the actual complete scoped audit snapshot and support for atomic effect/audit recording. '
                  'Separate transactions can leave no receipt to recover.']
    elif not original and answer.get('status') in ('unsupported', 'inconsistent'):
        lines += ['Investigate the stated missing, unsupported or inconsistent source or binding; the current input supports no conclusive verdict.']
    elif answer.get('analysis_status', answer.get('status')) == 'incomplete':
        lines += ['Complete the bounded analysis before using a one-sided search as an absence claim.']
    else:
        lines += ['No further request is reported by this answer.']
    lines += ['This is schema-specific guidance, not a synthesized minimum or a promise that a suggested record resolves every case.',
              '', 'Trust and scope limits:']
    assumptions = answer.get('trust_assumptions') if original else EXTENSION_ASSUMPTIONS
    lines += ['- ' + item for item in assumptions] if assumptions else ['- not reported']
    return '\n'.join(lines)
