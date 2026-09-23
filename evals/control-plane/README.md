# Synthetic control-plane workbench

`workflows.py` is an isolated sketch, not a deployed agent or a benchmark. Read the caller's returned value as the consumer of each decision; the supplied facts below are local fixture assumptions, not production measurements.

- `find_support` ranks local records by word overlap and reads at most three. A record may be an answer, a correction, or background; a late correction can contradict an early answer, while more retrieval spends time. The operator wants a supported answer or an explicit need for more evidence. Record IDs and the read limit are available; no model is called.
- `ci_for_change` maps changed paths to focused tests. Some cross-module behavior is not represented by path owners. An unmapped change or a failing focused run invokes the full suite, and mandatory protected checks are outside this helper. The team wants a smaller successful CI path without hiding failures; no run frequency or savings data exists.
- `task_context` passes a short note bundle to a planner. Notes can be old, superseded, or relevant despite age. The cache is cheap but keyed only by task ID and may serve an earlier revision. The planner must still inspect exact files before edits; no cache hit proves freshness.
- `review_proposal` compares user-request terms with proposed text before a human reviews a plan. Paraphrases can look missing and copied terms can conceal changed intent. `required_approvals` are exact booleans; this screen cannot grant approval or execute work.

Consider each workflow separately. For a promising semantic placement, identify the existing input and consumer, when it would run, which code and exact gates stay, a simpler alternative, provider/uncertainty behavior, and a check that could disprove value. Do not assume that every workflow merits Jev.
