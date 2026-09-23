# Behavioral evaluation

These are synthetic miniature repositories, not customer data or production benchmarks. Run the same discovery request in both hosts: "Use Jev Scout to assess this directory. Do not call APIs or modify it. Tie candidates to files and distinguish missing evidence from no useful candidate."

Evaluate each directory independently, without showing `rubric.md` to the agent. Record host/model, skill revision, inspected evidence and failures. Wording and number of suggestions are not acceptance criteria. These cases are smoke coverage, not proof of generality across every repository.

`support/experiment.json` is a separate, frozen synthetic API smoke experiment with hand-authored expected queues. It may test protocol and a small semantic example, not production accuracy. Do not tune it after observing results; create a distinct development set if tuning is needed.

`support/policy.example.json` is deliberately unapproved. Copy it to ignored local storage and set approval only after the user has authorized the stated scope and budget. Its limits are per invocation, not a monetary or cross-run account cap. Repeated runs require checking the remaining authorized budget.

The integration example in `support/app.py` consumes an injected judgment provider without importing the experiment runner. Its tests exercise the application path offline; they do not prove a live application deployment.

For deeper proposals, run both hosts on `placement/` with the same request: "Assess this repository for useful Jev opportunities. Explain the strongest candidates with concrete insertion points, invocation conditions, alternatives, and falsifiable evaluation. Do not call APIs or modify files." Keep the maintainer rubric hidden. `evidence/` provides source validation, deterministic correction and selective-placement replay without coupling those application policies to the generic runner.

For third-wave discovery, assess `control-plane/` and `exploration/` independently with that same open request and no API calls or edits. Keep `rubric.md` hidden. The fixtures are small and synthetic: evaluate whether the agent traces a real consumer, chooses a defensible semantic insertion point (or a justified non-adoption), retains exact code, compares alternatives, and states a falsifiable check. Coverage of named patterns is not itself a pass condition.
