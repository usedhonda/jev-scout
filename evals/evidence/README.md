# Evidence-aware comparison

Four frozen synthetic English/Japanese cases ask for an outcome and a separate source ID. Source offsets use Python Unicode code-point indexing, not UTF-8 byte offsets. `decisions.py` checks provenance and enforces only the source-type invariant; a cited source may still be irrelevant. The .8 demo confidence threshold is not calibrated.

Before any authorized API run, validate each case with `validate_candidates`. The generic runner does not know this application's source contract. The experiment includes local `baseline_hits`, which the runner does not send. The saved-result comparator verifies the exact experiment hash and compares original decisions, final outcomes, and always/no-hit/conflict invocation via offline replay. It does not claim measured cost or latency savings.

```sh
python3 evals/evidence/compare.py --result /path/to/private/result.json
```

Unit cases separately cover inconsistent labels, absent/out-of-set evidence, changed sources and provider failure. They do not rely on a live model producing errors. Changes to questions or the dataset require a new experiment identity; do not tune the frozen examples to improve the reported score.
