# Existing-control diagnostic (post-hoc)

## Result and limits

Nine pre-existing public evidence inputs were replayed with four unchanged methods: native, journal, direct-query and conservative. No new worker run, evidence fixture, or baseline correction was introduced. Expectations were recorded after observing outputs: this is diagnostic characterization, not a prospective evaluation or independent semantic validation.

At complete-search settings, journal and direct-query agree on status and verdict for 8/9 inputs. On control-001, native and journal return `status=inconsistent`, `verdict=null`; direct-query returns `status=complete`, `verdict=ESTABLISHED`; conservative returns `UNRESOLVED`. The input asserts a completed worker, no delivered receipt and an empty complete audit snapshot. Under the declared lifecycle, these cannot all be true. The finite checker rejects the compatible-history set; the direct query omits that coherence check. This demonstrates a limitation of this frozen baseline, not an effect committed in a real contradictory execution or a general superiority result for model checking.

The scientific implementations are preserved. Do not use the frozen direct query as a standalone containment authorization service. Use the supported consistency-checking analysis and investigate inconsistent evidence; the artifact does not authenticate source assertions or justify resumption.

## Counts

| Method | Inconsistent | Established | Unresolved | Unsupported |
|---|---:|---:|---:|---:|
| Native | 1 | 0 | 7 | 1 |
| Journal | 1 | 1 | 2 | 5 |
| Direct query | 0 | 2 | 2 | 5 |
| Conservative | 0 | 0 | 8 | 1 |

The nine original selected-profile checks remain in `run_demo.py`. In particular, original control-002 deliberately caps journal enumeration at zero and returns `incomplete`. The new matrix uses the same input with ordinary complete-search settings. Direct-query and conservative methods do not enumerate and cannot be given an equivalent search cap. Never replace or relabel the original incomplete result as established.

## Reproduce

From the directory containing `judge_artifact/`:

```sh
python3 -I -S -B judge_artifact/run_control_matrix.py --output control-results
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/controls/input-001.json --method journal --format human
python3 -I -S -B judge_artifact/replay.py extension --evidence judge_artifact/inputs/controls/input-001.json --method direct-query --format human
```

Journal inconsistency exits 2, which is an expected refusal to conclude; direct-query exits 0 on this known deficient baseline behavior. The matrix harness treats both as recorded output shapes, not two correct substantive answers. A 36/36 match confirms reproduction of the limitation, not its repair. `--strict-runtime` has the same meaning as in the existing launcher.

`run_demo.py` keeps 199 original checks unchanged. `run_control_matrix.py` has 36 post-hoc cells, including overlap with eight original complete-search checks. Do not report their sum as 235 independent cases. No new interpreter validation is implied by compatibility policy.
