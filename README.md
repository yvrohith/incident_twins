# Incident Twins

**Rohith YV — Independent author**

Incident Twins asks whether retained evidence establishes that no write or export attributable to a registered run family committed to an in-scope resource during a fixed interval after confirmed parent stop.

The study distinguishes exact equality of a configured evidence view from equality under a declared projection. The replay artifact reproduces bounded evidence verdicts, including unresolved cases and a documented comparator limitation. These verdicts do not establish permanent containment or authorize resumption.

## Report and artifact

- [Research report (PDF)](Incident_Twins_Rohith_YV.pdf)
- [Editable manuscript (DOCX)](Incident_Twins_Rohith_YV.docx)
- [Title and 150-word abstract](TITLE_AND_ABSTRACT.txt)
- [Replay source and documentation](judge/judge_artifact/README.md)
- [Checked judge ZIP](judge/Incident_Twins_Judge_Artifact.zip) and [Quickstart](judge/QUICKSTART.md)

## Inspect one evidence-only answer

From the repository root:

```sh
python3 -I -S -B judge/judge_artifact/replay.py original --evidence judge/judge_artifact/inputs/original/e01-native-0/evidence.json --model judge/judge_artifact/inputs/original/e01-native-0/public_model.json --format human 2> original-provenance.json
```

This reads the named public evidence/model and uses the preserved original investigator. The example returns `UNDETERMINED`: both outcomes remain compatible. It does not read expected answers or private histories as investigator inputs.

Use `replay.py original` or `replay_original.py` with the isolation flags. `check_evidence.py` is the frozen implementation loaded by those launchers. Directly executing that file with `-I` is unsupported and raises a sibling-package import error. The supported launcher supplies the packaged import path and records provenance; neither `PYTHONPATH` nor disabling isolation is required.

## Run the saved-evidence checks

From the repository root, using a final CPython 3.12.x or 3.13.x release:

```sh
python3 -I -S -B verify_public_repo.py
python3 -I -S -B judge/judge_artifact/verify_manifest.py
python3 -I -S -B judge/judge_artifact/run_demo.py --output judge-results
python3 -I -S -B judge/judge_artifact/run_control_matrix.py --output control-results
```

Choose fresh result directories. No package installation, model inference, agent framework, hosted telemetry or network access is required for saved replay. The original demo compares 199 saved answers. The separate 36-cell diagnostic reuses existing controls; these counts overlap and are not additional scientific executions.

The frozen direct query concludes `ESTABLISHED` on contradictory control-001, while the journal checker returns `INCONSISTENT`. A passing replay of that answer reproduces a known limitation, not a valid containment clearance. See the [control diagnostic](judge/judge_artifact/docs/CONTROL_DIAGNOSTIC.md).

Normal replay accepts final CPython 3.12.x and 3.13.x releases. `--strict-runtime` requires one of the four recorded strict-list versions: 3.12.13, 3.12.14, 3.13.5 or 3.13.15. The documentation distinguishes allowed versions from actual historical validation.

## Evidence and repository scope

The repository contains the report, source code, public models/evidence bundles, expected replay answers and the checked judge archive. Scientific inputs, expected answers, runtime policies, generation reference locks and provenance remain intact.

Private validation histories, checkpoints and sinks remain outside the investigator-input boundary. Author notes, prior drafts, local validation workspaces, installed environments and credentials are excluded from Git. The original author-only delivery manifest/verifier are also excluded; `PUBLIC_MANIFEST.json` and `verify_public_repo.py` check this public repository's file scope instead.

The stock-observer component is documented in Appendix B. Its separately received source/derivative and raw recordings are not included in the core artifact. Saved-evidence replay does not independently regenerate those experiments or the private execution histories.

The `.gitignore` uses an explicit top-level allowlist and additional exclusions for local secrets/configuration, macOS metadata, environments and generated outputs. Only the reviewed report files and judge ZIP are excepted from the document/archive exclusions. Review new files deliberately; ignore rules are not a substitute for checking credentials.

## License

The original core judge code is licensed under [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for scope and [third-party notices](judge/judge_artifact/THIRD_PARTY_NOTICES.md). This code license does not extend to the manuscript, separately received component code or private author materials.

## Repository and archive identity

Repository: [github.com/yvrohith/incident_twins](https://github.com/yvrohith/incident_twins). It contains this report and the core saved-evidence replay artifact. Separately received component source and private author records are outside this release.

The report and judge ZIP hashes are listed in [CHECKSUMS.txt](CHECKSUMS.txt). The checked judge ZIP SHA-256 is `560c365b2f6dab16d878e9b481c6af12969bdb325e9e28d316259840748cf9ed`. The exact source revision is the Git commit you check out (`git rev-parse HEAD`).

`CHECKSUMS.txt` lists three deliverables: DOCX, PDF and judge ZIP. `PUBLIC_MANIFEST.json` covers the public repository files except itself. The nested judge manifest covers only the judge package, also excluding itself. These are different file scopes, not different verdict counts.

To build a clean source ZIP from the reviewed public manifest:

```sh
python3 -I -S -B package_source.py --output dist/Incident_Twins_Source.zip
```

The builder refuses changed manifest payloads and excludes Git metadata, Finder metadata, resource forks and private author records. It keeps the checked judge ZIP unchanged. Use this generated source ZIP or the checked judge ZIP for a file upload; a Finder-compressed working folder can add metadata that Git itself would ignore.
