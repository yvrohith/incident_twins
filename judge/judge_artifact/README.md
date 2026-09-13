> **Known baseline limitation, preserved for comparison:** the direct query concludes `ESTABLISHED` on contradictory control-001, while the native and journal checkers return `inconsistent`. Its 30-run agreement does not extend to all controls. See `docs/CONTROL_DIAGNOSTIC.md`; do not use the frozen query alone to authorize containment or resumption.

# Incident Twins: combined local judge artifact

This package checks saved evidence from the original study and the later effect/receipt extension. It uses the unchanged scientific checkers. The release launcher selects a checker and reads the named public JSON input. It prints the original JSON answer by default, or a plain-text view with --format human. No model service, agent framework, worker, database effect, or network request runs during saved replay. No pip install is needed.

The package includes ten original evidence examples, 30 extension views at the observation horizon, 30 later retrieval views, and nine existing evidence controls. The controls are deliberately modified inputs, not additional worker executions. All scientific code and public input files were copied byte for byte. See `source_provenance.json` for their original paths and hashes.

## Run the saved checks

Normal saved replay permits final CPython 3.12.x and 3.13.x. Being permitted does not mean that an exact patch has been tested. Add `--strict-runtime` to require an exact validated version: 3.12.13, 3.12.14, 3.13.5, or 3.13.15. Retained reports record 199/199 saved-answer checks on each of these four versions; `historical_runtime_validation.json` records their sources and hashes. Other implementations, minor versions and prereleases are rejected. `runtime_policy.json` fixes this policy and the strict list. These are saved-JSON checks; scientific generation pins remain unchanged.

After extracting the ZIP, run from the directory containing `judge_artifact/`. Replace `python3` with the executable for a permitted version if necessary:

```sh
python3 -I -S -B judge_artifact/verify_manifest.py
python3 -I -S -B judge_artifact/run_demo.py --output judge-results
```

Choose a new output name if `judge-results` already exists. The walkthrough runs 199 separate checks: ten original checks, 120 at-horizon extension checks across four methods, 60 later-retrieval native/journal checks, and nine controls. It saves each actual answer, import and runtime report, command, process status, and comparison. Error, unsupported, and inconsistent answers produce exit 2; the outer demo expects those nonzero statuses for the relevant saved controls. An incomplete analysis keeps its actual nonconclusive answer. No saved answer is changed to make a check pass. Expected answers are read only by the outer comparison program, after the child checker runs. They are not checker inputs. Original answer comparisons omit execution time; extension comparisons use the full saved answer.

The flags `-I -S -B` disable environment-supplied import paths, site initialization, and bytecode writes. The launcher adds only its packaged code directory and verifies scientific module locations. Each demonstration check runs in a fresh empty working directory. This checks import separation; it is not an adversarial operating-system sandbox or independent implementation of the scientific rules.

## Inspect an individual answer

For the original-study evidence-only workflow, use the first command below or `replay_original.py`. `check_evidence.py` is the retained frozen implementation, not the isolated command-line launcher. A direct `python3 -I -S -B check_evidence.py ...` call cannot import its sibling package; this unsupported invocation is not a substitute for the release command.

```sh
python3 -I -S -B judge_artifact/replay.py original --evidence judge_artifact/inputs/original/e01-native-0/evidence.json --model judge_artifact/inputs/original/e01-native-0/public_model.json
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/extension/input-001.json --method journal
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/extension/input-001.json --method native
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/extension/input-001.json --method direct-query
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/extension/input-001.json --method conservative
python3 -I -S -B judge_artifact/replay.py model
```

The extension's direct query calls the existing `direct_query()` function. It shares evidence validation with the richer checker; it is a comparison of inference rules, not an independent evidence interpreter. The conservative method refutes on a qualifying delivered receipt and otherwise leaves the claim unresolved. The native and journal methods also accept `--max-histories N`. A partial search cannot justify a universal conclusion. The original route retains `--max-histories` and optional `--anchor`; these options are not part of the ten-example demonstration. `replay_original.py` and `replay_extension.py` are individual release entry points with the same runtime, format, and isolation rules. The copied `check_evidence.py` and package modules remain unchanged scientific implementations; use the release entry points to get release policy and provenance.

## Read an answer in plain language

`--format json` is the default. JSON mode writes exactly one answer document to stdout and one structured provenance document to stderr. Runtime details are in provenance, not added to the scientific answer. Human mode changes stdout only; stderr remains structured JSON and the process status is unchanged. The display uses the checker’s own verdict and available counts. Missing analysis metadata is `not reported`. Direct query and the conservative baseline do not enumerate histories.

A terminal may display stdout and stderr together. Append `2> provenance.json` to a human-format command to show the answer on screen while retaining its structured provenance in a separate file. Use a distinct filename for each result you want to keep.

```sh
# Original ambiguous view
python3 -I -S -B judge_artifact/replay.py original --evidence judge_artifact/inputs/original/e01-native-0/evidence.json --model judge_artifact/inputs/original/e01-native-0/public_model.json --format human
# Pending-work supplement
python3 -I -S -B judge_artifact/replay.py original --evidence judge_artifact/inputs/original/supplement-a/evidence.json --model judge_artifact/inputs/original/supplement-a/public_model.json --format human
# Extension journal and direct-query baseline
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/extension/input-001.json --method journal --format human
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/extension/input-001.json --method direct-query --format human
# Strict mode also reaches every child check
python3 -I -S -B judge_artifact/run_demo.py --output judge-results-strict --strict-runtime
```

The original checker says `UNDETERMINED`; the extension says `UNRESOLVED`. Both can describe evidence compatible with opposite outcomes, but their names and model-specific meanings remain unchanged. The display does not relabel either output. Source requests are guidance for these fixed schemas, not a computed minimum or a guarantee that an arbitrary case will be resolved. A coverage assertion is a trusted contract; this launcher cannot authenticate it. A direct query uses the same extension input validation as the richer checker.

`docs/WALKTHROUGH.md` gives a short tour; `docs/RUNTIME_POLICY.md` distinguishes policy tests from real interpreter runs.

## What these checks show

The question is whether no in-scope effect committed after confirmed parent stop through the observation horizon. A result applies only to that interval, the registered run family and resource, and the declared model and trust assumptions. It does not establish permanent containment or authorize resuming work.

The original native pair e01 has exact matching retained evidence from two continuations of one measured stopped-parent prefix. The delegated e05 control retains different native evidence that resolves its two outcomes. The extension uses separate full executions. Its selected opposing executions agree only after the declared semantic projection; their complete raw JSON differs. No exact-view or identifier-isomorphism claim is made for the extension.

Extension native projection: after binding, order, and framework-route checks, retain worker event kinds, at-horizon exit status, and the number of qualifying delivered receipts. Journal projection adds the number of qualifying audit rows. Raw trace values remain in the input files, but the finite model does not interpret every arbitrary span attribute. Read `docs/PROJECTION_AND_ASSUMPTIONS.md` and the unchanged model notes for the boundary.

The extension's separate transactions can leave a committed effect with no audit receipt. In its joint-transaction design, a trustworthy complete scoped audit snapshot resolved all 15 tested runs. The simple direct query matched the journal checker on all 30 measured at-horizon inputs. In the separate post-hoc full-search comparison, journal and direct-query agree on 8/9 existing controls; the contradictory control exposes the frozen query's missing lifecycle-consistency check. This replay checks saved answers; it does not repeat the independent database/trajectory audit or recreate the interruption runs.

## Contents and limits

- `inputs/` contains only public checker inputs. Extension and control filenames carry no fault schedule or outcome label.
- `expected/results.json` contains saved answers for the demonstration, separate from inputs. Model witnesses in those answers are enumerated compatible histories, not private realized histories.
- `docs/` contains the declared projection and unchanged extension protocol/model notes. The protocol describes the study's schedule classes; it is not a realized private fault log.
- `provenance/` contains the unchanged generation manifest and Python dependency lock for reference. These are not setup requirements for saved replay.
- `file_manifest.json` hashes every other packaged file. It detects changed bytes against itself, not an authenticated issuer. Its own digest and the ZIP digest are retained outside the archive.

No private effect database, fault-control log, oracle history, installed environment, cache, external service code, or Python runtime is bundled. Full scientific regeneration needs the retained research repository and exact generation environment; see `docs/SCIENTIFIC_REGENERATION.md`. Saved replay is deliberately usable without that environment.

The original core judge code is licensed under Apache License 2.0; see `LICENSE` and `NOTICE`. This does not license the separately received component code or private author materials. Rohith YV (Independent author) is the sole author. Local packaging does not establish recipient access or authorize publication/submission.

## Cross-method existing-control replay

```sh
python3 -I -S -B judge_artifact/run_control_matrix.py --output control-results
```

This separate 36-cell diagnostic retains the original 199-check demo and its intentional zero-search-cap control. A passing diagnostic replays the known baseline defect, not a corrected comparator. See `docs/CONTROL_DIAGNOSTIC.md`.
