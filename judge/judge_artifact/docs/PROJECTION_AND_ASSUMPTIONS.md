# Evidence boundary in plain language

An empty record set is useful only when the relevant effects must have produced records and those records were collected completely for the right run, resource, and interval. Generation and collection are different requirements. A successful trace flush covers generated trace records; it does not prove every effect produced an audit record.

The extension's public JSON retains framework messages and spans, raw times and identities, worker output through H, process identity and exit status, controller boundaries, and collection metadata. The journal observation adds audit rows. The investigator does not read the private effect table, independent destination labels, or the laboratory fault-control pipe.

Before projection, the checker validates run/task/resource/epoch bindings, controller ordering, the accepted framework tool call and return, the expected four-span route, matched span/tool identities, worker identity and supported event kinds. Its at-H native projection is exactly:

1. the worker event-kind sequence;
2. the worker's exit status at H;
3. the number of qualifying delivered receipts.

The journal projection adds the number of qualifying audit rows. Later retrieval may add qualifying recovered receipts only with a sealed original interval and no new effect permission. Raw span values stay in the files; the checker does not model every arbitrary attribute. Equality under this projection is weaker than equality of the complete raw files. The extension's raw files differ. The original exact pair has a separate construction and claim.

The private checkpoint pipe allows the controller to place a process interruption. Its checkpoint names can distinguish the chosen before-commit and after-commit cuts. Giving that trusted channel to an investigator changes the evidence contract and can resolve the selected ambiguity. Its exclusion is consequential, disclosed, and a principal validity limit.

Design A writes the effect and the audit row in separate SQLite transactions. A process can stop after the effect commits but before the audit row exists. Complete collection of audit rows cannot recover a record that was never generated. Design B commits both rows in the same transaction. The model contains no B cut that commits only the effect.

For B, absence establishes the interval claim only under faithful atomic records for every in-scope effect, no bypass or deletion, correct attribution and ordering, and a trusted complete scoped snapshot. The experiments concern process interruption in the pinned local setup, not power loss, damaged storage, retries, or arbitrary effects made atomic by SQLite. The model has one task, one worker, one resource, at most one effect, and at most one interruption. Its 22 A and 16 B histories are exhaustive only within those bounds.

The direct query shares public-input validation with the richer checker. Their agreement tests the inference rule, not an independent implementation of evidence semantics. The separate database/trajectory audit checks actual retained effects, but is not rerun by this public-input archive. Synthetic malformed-evidence controls are separately labelled and do not count as process runs.

The original checker uses `UNDETERMINED`; the extension uses `UNRESOLVED`. Both indicate opposing compatible property values in a complete search. Incomplete, unsupported, inconsistent, and input-error results remain distinct. The launcher does not translate these statuses or alter any verdict logic.
