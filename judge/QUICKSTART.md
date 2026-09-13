# Quickstart

This package replays saved public evidence with the frozen scientific code and expected answers. The direct query is a research baseline with a documented lifecycle-consistency limitation.

After extracting `Incident_Twins_Judge_Artifact.zip`, run:

```sh
python3 -I -S -B judge_artifact/verify_manifest.py
python3 -I -S -B judge_artifact/run_demo.py --output judge-results
python3 -I -S -B judge_artifact/run_control_matrix.py --output control-results
```

Choose fresh result directories. Normal saved replay permits final CPython 3.12.x and 3.13.x. The strict runtime list is CPython 3.12.13, 3.12.14, 3.13.5 and 3.13.15; each has a retained 199/199 saved-answer validation record. Use `--strict-runtime` to require that list. No pip install or live framework/worker is needed. JSON remains default and human formatting does not alter a backend answer.

## Inspect original-study evidence

Run from the directory containing `judge_artifact/` (in this repository, `judge/`):

```sh
python3 -I -S -B judge_artifact/replay.py original --evidence judge_artifact/inputs/original/e01-native-0/evidence.json --model judge_artifact/inputs/original/e01-native-0/public_model.json --format human 2> original-provenance.json
```

This is the supported isolated evidence-only entrypoint. The frozen `check_evidence.py` is loaded by the release launcher; running it directly with `-I` is unsupported and fails to find its sibling package. Use the launcher rather than changing import environment or removing isolation.

## Observe the limitation directly

```sh
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/controls/input-001.json --method journal --format human 2> journal-provenance.json
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/controls/input-001.json --method direct-query --format human 2> direct-query-provenance.json
```

The first command returns `status=inconsistent`, no verdict and exit 2. The second returns `ESTABLISHED`, exit 0, plus an explicit human-display warning about the frozen query. Do not interpret this query output as permission to resume or a containment clearance.

Human output goes to stdout; structured provenance already goes to stderr. The commands above save it to separate files so the answer is the first thing shown. Omit the redirection to display both streams in the terminal.

## Read counts correctly

The 199 checks preserve all original expectations, including a capped zero-history search. The separate 36 cells are nine pre-existing inputs crossed with four methods under complete-search defaults. Eight of those method/input/settings combinations overlap the original checks. In particular, control-002's capped and uncapped results are not interchangeable. A matching replay of the known deficient answer is reproduction of a limitation, not a successful safety test or a repaired comparator. The nine control inputs are not additional worker executions.

Journal/direct status-verdict agreement in the full-search matrix is 8/9: one agreement is ESTABLISHED, two are UNRESOLVED and five are unsupported. The remaining contradictory input is INCONSISTENT for journal and ESTABLISHED for direct-query. Complete raw outputs and assumptions are in `judge_artifact/docs/CONTROL_DIAGNOSTIC.md` and the replay result directory.
