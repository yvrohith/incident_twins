# Fault-aware model and evidence checker, version 1

This is an additive finite model for the process-interruption supplement. It neither edits nor falsifies the frozen model. It does not establish a framework vulnerability, a new dual-write mechanism, or novelty for transactional audit/outbox designs.

## State space and boundary

`model.py` has one accepted task, one worker, one target resource, no retry, at most one effect, and at most one process interruption. Every effect transition occurs after the controller's confirmed stop and subsequent permission and before the chosen horizon. Every prefix is an admissible horizon; this is a finite acyclic enumeration, not a sampled search.

The state separates:

- committed effect;
- committed faithful receipt;
- delivered receipt;
- transaction phase;
- worker active, dead, or done;
- interruption and graceful cancellation.

An uncommitted SQL insert does not set the effect bit. In A, effect commitment, audit preparation, and audit commitment are different transitions. In B, one transition commits both effect and audit. There is no modeled B transition that commits only the effect. An interruption preserves already committed state and rolls back uncommitted state. A graceful cancellation can also follow commitment and therefore does not prove its absence. Delivery is a later transition in both designs.

B's post-joint-commit and receipt-durable fault checkpoints correspond to the same durable abstract state. The controller's intervening resume is a stuttering step, not an extra atomicity cut. Opening a transaction, performing its inserts, and waiting before commit can similarly have the same public semantic observation despite different uncommitted state.

The enumerator yields **22 A histories** and **16 B histories**, including all prefixes and all modeled interruption/cancellation choices. It covers only this route and fault domain; it is not exhaustive over programs, operating systems, storage failures, worker retries, or arbitrary SQL behavior.

## Investigator boundary and equality

The checker consumes a supplied public JSON value. Its file CLI reads only the nominated public JSON file. It does not open an effect database, read a fault schedule, or query the independent validator. Tests confirm that adding private schedule/outcome keys does not change its answer. The caller must preserve this boundary; the checker is not a sandbox against a malicious caller.

All raw framework messages, spans, timestamps, IDs, PID, operational worker events, exit status, and collection records remain in the retained artifacts. The adapter checks the one accepted framework task, matched tool-call/return identities, expected four-span inventory, matching tool-span result and identity, controller binding and order, the pinned policy, worker identity, and the recognized operational event kinds. An additional tool call or unexpected span inventory is unsupported. It interprets worker receipt payloads and separately declared journal snapshots as effect evidence.

It does **not** interpret every arbitrary tracing attribute or prove a general semantic equivalence over opaque raw span content. Its finite observation consists of the at-H worker event-kind sequence, lifecycle outcome, and number of qualifying delivered receipts; the journal profile additionally contains the number of qualifying audit rows. Run/task/resource/epoch are validated as bindings before that projection. IDs and timestamps are not normalized to claim a full-view match. The raw-equality and binding-preserving-isomorphism checks belong to the separate independent audit. A model witness here is **equality under this declared semantic projection only**, never an exact-evidence executable twin.

The private fault-control pipe is not a native operational log. Its checkpoints support fault injection and independent trajectory validation, not the investigator verdict. Any result obtained by giving that channel to the investigator would concern another, stronger evidence contract.

For recovery, at-H worker events and exit status remain at H. A later delivered, correctly bound receipt is a separate `recovered_target_receipts` constraint on the at-H durable receipt state. This is admitted only with a declared sealed original interval, matching original epoch, and no new effect permission. It does not rewrite the delivery timestamp into the original interval. A same-epoch label alone is insufficient. The runtime/independent validator must establish that post-H actions can only deliver or cancel and that destination/journal state did not change; the Boolean certificate is trusted input, not self-authenticating proof.

## Conditional sufficiency statements

Let Q mean that the target effect did not commit in the registered interval. Let H_F be the histories admitted by this finite fault model. Claim sufficiency for an observation O means that every pair in H_F with equal O has equal Q. `exhaustive_report()` enumerates every history and groups by the complete declared projection; checking whether each group has one Q value checks the pair criterion without a literal nested pair loop.

**Separate-write counterexample.** Suppose an effect can commit without a recoverable receipt and the permitted evidence can also arise without the effect. Then that evidence cannot establish Q: the compatible effect history makes Q false while the compatible no-effect history makes Q true. In this model, interrupting a started worker before transaction commit and interrupting it after A's effect commit but before its audit commit produce the same native event sequence and dead-worker status. Both complete audit snapshots are empty. Their Q values differ. This is a direct constructive argument; absence of a receipt is not being created by deleting a record.

**Atomic-generation plus complete-snapshot sufficiency.** Suppose every qualifying effect has a faithful, correctly bound receipt committed in the same transaction, and the investigator receives a trustworthy complete snapshot of all such receipts in the relevant interval. Atomic generation gives effect implies receipt; faithfulness gives receipt implies effect. Complete interval collection makes absence of a qualifying snapshot row equivalent to absence of a qualifying receipt. Combining these implications establishes Q when the snapshot is empty and refutes Q when it contains a qualifying receipt. This implication holds in every enumerated B history, including interrupted histories.

The assumptions are substantive: SQLite transaction atomicity in the supported local database; both writes in that transaction; all effect routes registered; no bypasses, retries, hidden tasks, deletion, mutation, fabricated receipts, or detached external effect; correct attribution and payload; trustworthy local stop/permission/horizon order; a consistent complete scoped snapshot; and no post-H effect permitted to contaminate a recovered original-interval query. These experiments concern process interruption, not power loss, media corruption, hostile storage, or arbitrary filesystem/network operations made atomic by SQLite.

A successful trace exporter flush is not used as an effect-generation guarantee. A complete snapshot over audit rows is still insufficient for A because no audit row may have been generated. The original model's conditional completeness assumptions have not been silently reinterpreted.

## Exhaustive finite results

| Design | Histories | Native groups | Native mixed-Q groups | Journal groups | Journal mixed-Q groups |
|---|---:|---:|---:|---:|---:|
| A | 22 | 10 | 3 | 13 | 3 |
| B | 16 | 10 | 3 | 13 | 0 |

The partitions cover 484 ordered A pairs and 256 ordered B pairs per profile. These are model comparisons, not process-run counts. The model JSON retains an explicit opposing witness wherever a mixed group exists. B satisfies effect/receipt equivalence in every modeled state; A does not. Native evidence alone is not claim-sufficient across either entire modeled domain because durable receipts can remain undelivered.

## Verdicts, failures, and baselines

`analyze(public, profile='native'|'journal', max_histories=None)` reports `complete`, `incomplete`, `unsupported`, or `inconsistent` separately from the verdict. Complete nonempty uniform compatible sets yield `ESTABLISHED` or `REFUTED`; opposing compatible histories yield `UNRESOLVED`. An empty complete set is semantic inconsistency, not proof. With a cap, a found opposing pair can justify `UNRESOLVED`, but a uniform prefix cannot justify either conclusive verdict. Unsupported stale/missing scope, source, generation, horizon, policy, or recovery assumptions yield no verdict.

A properly bound receipt about another run, resource, or epoch is not a target positive. An out-of-scope row can coexist with a complete target-scoped query and is ignored for this target. Missing audit rows with a correctly bound delivered receipt contradict the asserted complete append-only source and are reported as inconsistent.

`conservative(public)` refutes only upon a qualifying delivered receipt, including an admissible later recovered receipt, and otherwise abstains. `direct_query(public)` selects qualifying audit rows: a positive refutes; B's supported atomic complete empty snapshot establishes; A's empty snapshot abstains. It shares input validation with the richer checker and is therefore a comparison of inference rules, **not an independently implemented evaluator**. No accuracy advantage is expected or required over this correctly scoped query. The independent runtime validator is separate code.

## Deterministic development tests and reproduction

The first test command failed during import with `SyntaxError: closing parenthesis ']' does not match opening parenthesis '{' on line 31` in the newly written test fixture; **zero tests executed**. The bracket typo was corrected without changing any runtime evidence. Subsequent invocations of the same command passed 19/19, then 23/23 after stronger checks/recovery tests, and finally 24/24 after policy validation. These are incremental development checks, not 66 independent scientific cases. No skipped tests occurred in those invocations.

The original two development gate bundles contained an inaccurate policy description mentioning a family-cancel request. The implementation did not send that request. The final checker requires the corrected, prospectively frozen detached-worker policy and reports those old metadata bundles as unsupported; they remain preserved as development evidence and are not silently rewritten. Runtime gate persistence can be independently validated despite this labeling defect. Frozen matrix inputs must use the corrected policy.

The final 24 tests comprise four model tests and twenty evidence-control/test methods. The ten design-by-schedule semantic fixture combinations inside one test are synthetic unit inputs, not extra process executions. Controls cover stale epoch, unclosed horizon, missing source, wrong run/resource positives, incomplete searches, generation/policy mismatches, contradictory receipt/snapshot evidence, identity/order errors, ignored private input keys, retained recovery timing, and missing recovery seals.

From `Codebase`:

```sh
.venv/bin/python -m unittest research_extensions.effect_receipt_v1.test_model -v
.venv/bin/python -m research_extensions.effect_receipt_v1.model
.venv/bin/python -m research_extensions.effect_receipt_v1.checker PATH_TO_PUBLIC_AT_H_JSON --profile journal
```

The checked-in `model_report.json` is the deterministic output of the second command. Fresh reproduction should print or write to a new path rather than overwrite the frozen report. Model outputs alone do not certify that a measured execution maps to the model: the independently implemented trajectory validator checks the real persistence and transition evidence separately.
