# A short local walkthrough

Run from the directory containing the extracted `judge_artifact/`. Use a final CPython 3.12.x or 3.13.x; strict mode requires one of the four historically validated versions in the runtime policy. No installation or network service is needed.

1. Check the package bytes, then replay the saved answers into a fresh output directory.

```sh
python3 -I -S -B judge_artifact/verify_manifest.py
python3 -I -S -B judge_artifact/run_demo.py --output judge-results
```

The demonstration compares 199 saved answers. It checks expected nonzero exits for unsupported/inconsistent controls. This replays evidence; it does not rerun the agent, worker, database audit or fault schedules.

2. Inspect a complete configured original native/controller view that leaves opposite outcomes possible.

```sh
python3 -I -S -B judge_artifact/replay.py original --evidence judge_artifact/inputs/original/e01-native-0/evidence.json --model judge_artifact/inputs/original/e01-native-0/public_model.json --format human
```

Use this `replay.py original` route for isolated evidence-only execution. The frozen `check_evidence.py` is not a standalone isolated launcher. The original backend says `UNDETERMINED`. The display reports the actual compatible Q-true and Q-false counts and its schema-specific request for bound executor records.

3. Inspect the pending-work supplement, then the same scope with its retained source-coverage input.

```sh
python3 -I -S -B judge_artifact/replay.py original --evidence judge_artifact/inputs/original/supplement-a/evidence.json --model judge_artifact/inputs/original/supplement-a/public_model.json --format human
python3 -I -S -B judge_artifact/replay.py original --evidence judge_artifact/inputs/original/supplement-b/evidence.json --model judge_artifact/inputs/original/supplement-b/public_model.json --format human
```

Coverage is trusted and bound to the stopped interval. An interval conclusion does not prove that pending work can never commit or authorize resuming work.

4. Inspect the extension and its direct-query comparison on the same public input.

```sh
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/extension/input-001.json --method journal --format human
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/extension/input-001.json --method direct-query --format human
```

The richer checker reports its enumeration. The direct query prints `not enumerated`; it shares the extension’s input validation. The extension’s raw records differ, and its ambiguity claim is only under the declared projection. Its verdict `UNRESOLVED` remains distinct from the original vocabulary.

5. Check that replay did not change the package.

```sh
python3 -I -S -B judge_artifact/verify_manifest.py
```

For machine processing, omit `--format human` or request `--format json`. Each answer is one JSON document on stdout. Provenance is one JSON document on stderr. Use `--strict-runtime` for the frozen exact-version policy; a demo passes it to every child.

Rohith YV (Independent author) is the sole author. Core judge code is Apache-2.0. The author-supplied repository location is https://github.com/yvrohith/incident_twins; publication of this local revision and any separate component distribution remain distinct actions.
