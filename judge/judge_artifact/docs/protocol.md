# Effect-to-evidence supplement, protocol v1

This protocol is additive to Incident Twins. It was selected after the original study and after two development gate executions on 2026-09-12. The original framework, model, fixtures, results and completed manuscript are immutable reference inputs. This is an application experiment, not a vulnerability finding in Pydantic AI or SQLite, and not a power-loss experiment.

## Feasibility decision and development ledger

The two initial A-design runs executed the actual original Pydantic AI FunctionModel/tool adapter and a separate SQLite worker. A separate Python process read the actual database in each run. `development/gate_normal` had effect=1, audit=1, public delivered receipt=1 and exit=0. `development/gate_gap` had effect=1, audit=0, delivered receipt=0 and exit=-9. Both exported four full SDK spans with successful flush. Thus process failure did not imply rollback and a complete export of generated spans did not itself establish effect recording. No raw equal-evidence witness is claimed by this gate.

Development limitation: the initial policy *description* incorrectly included `request-family-cancel`; the executed code cancelled and awaited the parent, then allowed the accepted detached worker to continue. No family-cancel IPC existed. The final protocol names the actual policy consistently for both designs. These two development artifacts are retained verbatim and excluded from the prospective matrix. Before freezing, we added full SQLite sidecar retention, independent snapshot backups and stronger stability checks. The gate's separate SQLite reads establish its persisted effect finding, but it lacks those later snapshot artifacts. No gate result is relabelled as a fully validated frozen-matrix run.

## Fixed application and fault domain

One controller process runs Pydantic AI slim 2.43.0 with deterministic FunctionModel, the original actual registered `enqueue_artifacts` tool and original complete local SDK exporter. There is one registered worker process, task `t0`, resource `approved`, payload `dummy artifact`, one effect, no retries and at most one SIGKILL per execution. Python 3.12.13, SQLite 3.53.1 and OpenTelemetry SDK 1.44.0 are the development environment; each execution records actual versions. No model provider or hosted telemetry is used. The parent uses the unchanged `offline` guard. The worker imports only the Python standard library and has no network operation.

Policy for **both** designs: cancel and await the parent; accepted detached work may complete. Parent cancellation is not a guarantee that the detached worker has stopped. A separate process controls a worker's feasible instruction boundaries; SIGKILL is distinct from cooperative asyncio cancellation. Barrier pauses widen an actual boundary for repeatability and do not estimate its natural duration or crash probability.

The in-scope effect is the registered task’s INSERT into the `effects` table. Audit rows, internal SQLite journal/checkpoint writes, framework logs and collector backups/output files are evidence machinery outside this task-effect scope. Q is not asserted over every filesystem write made by the experiment. This narrowed benign scope is identical for A and B.

Both designs use the same append-only SQLite schemas, WAL mode, synchronous=FULL, foreign_keys=ON, read_uncommitted=0 and busy_timeout=5000. Bootstrap schema creation occurs before registration and outside the claim interval. A inserts the effect and commits, then inserts the audit receipt in a second transaction. B inserts both in one transaction. A receipt repeats every effect field with faithful run/task/resource/epoch/effect-id/payload binding. There are no update/delete/bypass routes. These are trusted scoped application assumptions, not conclusions inferred from a Boolean coverage field.

## Causal interval and collection

Actual framework parent cancellation is confirmed before the controller grants worker effect permission. Every tested effect requires this permission. All five schedules receive the same post-stop permission, including pending work; the latter remains held before beginning the transaction. Thus there is no public “permission never issued” safety certificate to omit. Native task/call/span identities and timestamps are preserved.

Before H, the worker must have exited or be acknowledged on the private fault-control pipe as blocked at `before_begin` or `receipt_durable`. An explicit controller assertion checks that condition. No release occurs until collection ends. The controller retains the entire existing database family (main, WAL and SHM) before any inspection, queries the audit table in a read transaction, creates an SQLite-supported backup, and invokes a **separate process** to query effects/audit. It then marks H. Because the worker cannot change database state during this interval, the snapshot is also the state at H. Committed rows prove actual persistence; intended checkpoints do not label commitment. Local monotonic observations prove stop -> permission -> held/dead read -> H. No row timestamp is presented as a database commit timestamp. No distributed-clock claim is made.

The unchanged adapter's `native.collection.collection_horizon=100` is retained as legacy metadata. The extension's real interval boundary is `controller.observation_horizon`, with actual monotonic times. The parent and its spans have finished before that collection; all SDK fields and flush outcomes remain in the public view.

After H, pending work receives cancellation at its pre-transaction hold; delayed work is released only to deliver its already durable receipt. No new effects are permitted. Separate backups/queries and all later worker output/exit status are retained. Recovery uses a sealed original interval and does not classify a late commit from a preissued epoch alone.

## Investigator views and trust boundary

The complete declared public file is `public_at_h.json`: claim, design, all native messages/spans/exporter metadata, operational worker stdout/stderr through H, PID and exit status as of H, public controller registration/stop/permission/H records and collection metadata. Its `audit_snapshot` is the additional journal observation. `public_recovered.json` retains later delivery/lifecycle information and the recovered journal. Full raw stdout/stderr, complete controller records and final lifecycle files are also retained. No emitted operational record is deleted or renamed to erase decisive information.

The private namespace contains effect tables/backups, independent oracle reads, the fault schedule and its control-pipe protocol. These are visible to validators, never passed to the investigator. The pipe is a laboratory injection channel, not a configured operational logger. This exclusion, plus abstraction of raw timing/identity values, is a principal validity threat. An installation that exposes durable cut-specific completion or destination evidence may resolve the cases; this experiment does not suppress such an existing channel or assert the finding for that installation.

Two declared analysis profiles: **native** uses every operational/native field but excludes the added audit channel; **journal** adds its consistent audit snapshot. The finite model projects native fields into their documented semantics, preserving acceptance/start/delivery/terminal status, bindings and causal interval facts. Raw IDs, PIDs and absolute times remain in artifacts but are not claims about effect completion. Model witnesses establish equality only under the explicit semantic projection. Separate executions are compared byte-for-byte as well; no raw-equality or identifier-isomorphism claim follows from semantic equality.

Generated-record collection and effect-to-record generation are separate assumptions. For A, complete audit-row collection cannot exclude an unrecorded committed effect. For B, absence is conclusive only under faithful atomic generation for every route plus trustworthy, current, complete scoped interval collection. A valid positive receipt refutes Q without a closed negative snapshot. Bare process failure, worker cancellation, or successful trace flush never establishes absence by itself.

## Frozen matrix and expected interpretations

After code and deterministic controls pass, `freeze.py` hashes this protocol, all extension scripts, model/contract notes, and actual original source dependencies into `frozen_manifest.json`. The matrix runner refuses modified frozen inputs. This is prospective **within this post-hoc supplement**, not original prespecification. Every attempt is appended to a ledger before launching the controller. The final matrix is exactly 5 schedules x 2 designs x 3 clean controller/worker repetitions = 30 attempts maximum. Failures/timeouts consume an attempt and are retained; no replacement runs. The initial two feasibility runs are separate development executions (32 total if the matrix completes).

| Schedule | A actual boundary | B actual boundary | Expected effect/audit | Expected native / journal |
|---|---|---|---|---|
| normal | both transactions then delivery | joint transaction then delivery | 1/1 both | R / R both |
| interrupt_before_commit | open effect transaction | open joint transaction | 0/0 both | U / U A; U / E B |
| interrupt_after_commit | committed effect, before audit creation | committed joint transaction | A 1/0; B 1/1 | U / U A; U / R B |
| delayed_delivery | audit committed, held before delivery | joint audit committed, held before delivery | 1/1 both | U / R both; late native R |
| pending | held before transaction through H | held before transaction through H | 0/0 both | U / U A; U / E B |

B has no cut with a committed effect but an uncommitted audit from the same transaction. That cut is infeasible by construction and is not a separate invented execution. Equal effects across corresponding tested schedules are expected but are checked against actual independent destination reads, not forced. Three repetitions assess repeatability, not incident prevalence.

## Controls, outcomes and limits

Deterministic tests separately exercise stale epoch/H, missing source, wrong-run/resource positive receipts, incomplete search, inconsistent evidence and unsupported assumptions. Runtime attempts, test cases and model histories are separate counts. Primary outcomes by design and schedule: false ESTABLISHED, correct REFUTED, correct ESTABLISHED, and UNRESOLVED; report unsupported, inconsistent and incomplete separately. Baselines are a conservative bound-positive receipt rule and a direct scoped atomic-journal query. No advantage over a correct direct query is required.

Secondary summaries cover actual effect/receipt agreement, late retrieval, bytes and local durations. Timings include barrier/validation overhead and are not throughput, natural interruption-window, or deployment estimates. Storage durability is limited to the tested process-interruption configuration. The known dual-write/transactional-outbox mechanism is not new. Finite exhaustive enumeration proves only the conditional model statements, not exhaustive real-world behavior. Human review, new citations/results, author identities, licensing or publication are not inferred.
