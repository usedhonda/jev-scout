# Decision quality from seam to final action

Use this for a leading proposal or a request for deeper analysis. It turns a promising pattern into a testable system decision. Apply only the steps that can change the candidate's adoption decision; do not manufacture data, thresholds or a workflow that the repository lacks.

## Trace the whole policy

Write the actual path as `observation -> existing proxy -> call selector -> candidate set -> Jev judgment -> code validation/fallback -> consumer/action`. Some paths have no candidate set or selector; mark them absent rather than inventing one. For each boundary, locate its code or documented workflow and ask what wrong final result it can create.

- **Observation:** Can the permitted input distinguish the desired outcomes? If claimed and unclaimed cases produce the same visible evidence, stop at information insufficiency. If a source is blocked, missing or stale, do not relabel that as model uncertainty.
- **Call selector:** For selective use on no-match, conflict or uncertain cases, evaluate the selector over the *whole* workload. A confidently wrong deterministic result never reaches Jev; conditional Jev accuracy cannot repair it. Compare always-on only where latency, privacy and cost make it a plausible alternative.
- **Candidate generation:** If code extracts IDs, spans, documents or operations for Choice, measure whether the correct one enters the set. Keep `none` when the set may contain only wrong choices, even if it has one item. Missing gold candidate, unsuitable present candidate, invalid model ID and provider failure require different diagnoses.
- **Judgment and composition:** Ask one bounded property at a time. Independent questions may share state; dependent questions need the earlier answer first. Keep arithmetic, permission, source lookup and exact validation in code. Do not equate Choice probability, Noul probability, Score and confidence.
- **Action:** Recheck current source revision, ID, permissions and invariants before a side effect. Name a concrete action for absent evidence, uncertainty, malformed answer, service unavailability and stale source. A fallback is only safe if its *actual downstream behavior* is safe; returning to a keyword filter that silently suppresses an important alert is not an adequate description.

If the consumer is a destructive or hard-to-reverse action, consider whether Jev should only withhold, queue or advise, not authorize. Examples: prevent doubtful issue closure without allowing additional closure; prioritize reviews without granting approval; rank tests without skipping mandatory security checks. Conversely an advisory ranking may be the final product, not a mandatory step toward automation.

## Construct a comparison that can reject the idea

Compare the current path, the cheapest meaningful deterministic improvement, and the proposed Jev placement on the **same** cases. Add the existing LLM with stricter structured output or a hybrid when an active generative call already makes the bounded decision. For no-match-only use, compare `improved rule` and `improved rule + Jev`; a weak straw-man rule does not establish Jev's value. If the target demands a canonical result, exact proof or hard real-time response, those contracts may rule out a remote semantic call even where the subject sounds subjective.

Specify at least one plausible input that would **falsify** the candidate: identical observations, an omitted gold candidate, a confident wrong baseline outside the selected subset, a provider outage that changes the final action, or a cheap rule matching the proposed gain. Pick the cases relevant to this repository, not all examples. Define the adoption/rejection criterion *before* examining experiment results; thresholds require the target's labeled data and loss policy, not copied constants.

Measure three levels separately when applicable:

1. **Candidate or retrieval recall:** Was the correct source/ID available to choose?
2. **Conditional judgment:** Given sufficient evidence and an available correct candidate, was the bounded decision right or appropriately uncertain?
3. **End-to-end outcome:** Across called and uncalled cases, did the user-visible action meet the goal after validation, fallback and side effects?

Define the population (all changed pages, all eligible issues, all search requests, etc.). Build development and held-out sets separately. For high-impact boundaries, include both ordinary and hard cases, stratified by the actual failure mechanism: site/response type, language/client, last actor, source revision, explicit/implicit rule, or candidate omission. Do not use existing product output as unquestioned ground truth; obtain independent labels for disputed cases, preferably without showing the model's answer, and record genuine label disagreement. A synthetic fixture can test wiring and failure behavior but cannot establish production accuracy.

Write a small loss table for the final action before selecting metrics. Missed important notifications versus extra alerts, lost new reply text versus retained quotes, wrongful close versus extra review, wrong memory DELETE versus redundant ADD, and missed failing tests versus extra CI time are not symmetric. Track abstention, severe errors (especially high-confidence ones), human-review burden and corrections rather than only mean accuracy. For source selection, record both proposed and final corrected outcome; a consistency invariant may reject an impossible source-label pair but cannot prove semantic truth.

Measure burden over the entire pipeline: candidate generation, requests per item, input size, network/retries, validation, fallback, review, p50/p95 end-to-end latency and observed charges where available. Offline replay estimates call counts, not production latency or billing. Published savings from another codebase are topology examples, not target predictions. Distinguish API success, conditional model quality, application integration and actual user outcome as separate evidence levels.

## Production boundary if the candidate wins

For each sent field, establish the allowed data category, minimum excerpt, exclusions, provider retention/region requirements if relevant, and whether the user authorized this transfer. A key's presence is not data authorization. Treat repository text, email, comments and documents as untrusted *data*, including embedded instructions; include adversarial text in evaluation. Store only permitted redacted operational evidence, never raw credentials.

Keep `EVIDENCE_MISSING`, `UNCERTAIN`, `INVALID_RESPONSE`, `SERVICE_UNAVAILABLE` and `STALE_SOURCE` distinguishable in application behavior and telemetry when those states exist. Record question/model/source versions, selection reason, fallback reason and final action without logging raw private state. Re-evaluate on a frozen set when questions, candidate generation, model version, thresholds or application policy change. Choose the smallest valuable rollout for the consequence: shadow or hold for irreversible actions, possibly advisory as the permanent form for human work. Do not prescribe the same rollout ladder to every product.
