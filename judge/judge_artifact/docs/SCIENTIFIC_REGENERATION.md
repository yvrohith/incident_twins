# Optional scientific regeneration

The default judge walkthrough analyzes saved JSON only. It does not require Pydantic AI, OpenTelemetry, pytest, or a matching SQLite runtime. Do not install the generation lock merely to run the saved checker.

**The commands below are archival instructions for holders of the separate research repository; they are not runnable from this public replay package.** References to `Codebase` in the copied model notes and source provenance identify original source locations, not a second repository required for saved replay. Use QUICKSTART or the release README for runnable public-package commands.

Recreating the experiment is a separate task that needs the retained full `Codebase` repository. This public-input package does not contain the generator, worker, private databases, or realized fault logs. Local assembly does not provide an approved external access route to that full repository.

The recorded generation environment remains CPython 3.12.13, SQLite 3.53.1, Pydantic AI slim 2.43.0, OpenTelemetry SDK 1.44.0, and pytest 9.1.1 in the tested local POSIX environment. `provenance/generation_requirements.lock` is copied unchanged from the repository. It pins Python packages, not the SQLite library compiled into Python. Saved-replay compatibility on a different Python version does not validate framework execution or database persistence on that version. The scientific manifest deliberately rejects changed generation inputs or runtime versions.

From the complete repository's `Codebase`, with the matching environment already available, inspect retained results without launching new workers:

```sh
.venv/bin/python research_extensions/effect_receipt_v1/freeze.py --out artifacts/effect_receipt_v1/frozen_manifest.json --verify
.venv/bin/python research_extensions/effect_receipt_v1/independent_validate.py artifacts/effect_receipt_v1/matrix
.venv/bin/python -m pytest research_extensions/effect_receipt_v1 -q
```

To recreate the capped matrix in fresh directories:

```sh
.venv/bin/python research_extensions/effect_receipt_v1/matrix.py --manifest artifacts/effect_receipt_v1/frozen_manifest.json --out artifacts/effect_receipt_v1/reproduction_local
.venv/bin/python research_extensions/effect_receipt_v1/evaluate.py --manifest artifacts/effect_receipt_v1/frozen_manifest.json --matrix artifacts/effect_receipt_v1/reproduction_local --out artifacts/effect_receipt_v1/reproduction_evaluation_local
.venv/bin/python research_extensions/effect_receipt_v1/controls.py --manifest artifacts/effect_receipt_v1/frozen_manifest.json --matrix artifacts/effect_receipt_v1/reproduction_local --out artifacts/effect_receipt_v1/reproduction_controls_local
```

Use new names if these output directories exist. Never regenerate the canonical frozen manifest or overwrite retained results. The matrix permits at most 30 attempts, including failures/timeouts. These optional commands were not executed as part of this packaging pass. Experiments remain local, with scripted model responses and no paid inference or hosted telemetry.

The original study's own reproduction commands and fixed model remain in the retained repository's README and research notes. Its frozen source, evidence, model and results are unchanged by this package. A copied manifest documents expected hashes and chronology; it does not externally authenticate the study or establish historical attestation.
