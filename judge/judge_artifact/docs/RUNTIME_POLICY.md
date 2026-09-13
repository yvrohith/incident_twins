# Saved-evidence runtime policy

Normal replay permits final CPython 3.12.x and 3.13.x. Strict replay permits only 3.12.13, 3.12.14, 3.13.5 and 3.13.15. Retained records report 199/199 saved-answer checks with isolated scientific imports on each of those four versions. Their source paths and digests are in `historical_runtime_validation.json`. Further successful normal-mode runs do not silently expand the strict list.

A permitted but unlisted final patch, such as CPython 3.12.3, is accepted normally and rejected by strict mode. Runtime permission alone does not establish compatibility. Actual command results are recorded separately from policy tests in the author validation logs.

`release_runtime.py` supplies one policy to `replay.py`, `run_demo.py`, `replay_original.py` and `replay_extension.py`. The demo launches each child with its own interpreter, the isolation flags, explicit JSON mode and the requested strict flag. It checks that child runtime provenance agrees. Runtime provenance records the actual implementation, full version string, release level, permitted family, exact historical validation status and strict request.

Version-tuple simulations test rejection and acceptance branches. They are labeled `simulated_policy` and are not interpreter compatibility runs. Actual CLI checks are labeled separately. The complete demonstration’s 199 answer comparisons are a third denominator, unrelated to the scientific execution counts.

All supported commands require `-I -S -B`. No site packages, editable installation or PYTHONPATH is needed. Each child reads named public inputs only. The manifest records bytes but does not authenticate their issuer.

No experimental generation pin changed. Recreating framework/worker experiments still requires the original pinned generation environment described in `SCIENTIFIC_REGENERATION.md`.
