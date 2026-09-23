# Design valuable insertion points

Start with an actual user outcome and trace available data to its consumer. Keep value separate from placement: a new capability can use an added predicate or an advisory signal rather than replacing anything. Examples below generate hypotheses; they are not recommendations for every repository.

| Observable seam | Candidate placement and value | Compare / retain |
| --- | --- | --- |
| Predicate registry contains exact, numeric and regex checks on text | Add a user-authored semantic condition alongside existing predicates | Keep exact predicates and event execution; compare dictionary and semantic condition |
| Normalized before/after diff precedes notifications | Judge relevance or materiality after exact diff, before delivery | Compare alert misses and noise; do not change diff/checksum semantics |
| Multiple rules disagree or nothing matches | Call Jev only on the ambiguous subset | Compare current precedence, no-hit only, conflict only, and always-on if informative |
| Existing classifier plus corrected labels/top candidates | Complement verified weak cases rather than assume replacement | Measure correlated errors and subset routing; confidence scales may not be comparable |
| Human review queue with existing hard checks | Prioritize what to inspect or attach review hints | Leave security scanners and approval intact; measure important-item recall, not just ranking agreement |
| Parser yields several possible source values | Select an ID and return the original value plus provenance | Check candidate recall, source spans, no-match, and out-of-set rejection |
| Label can be cross-checked against a typed source | Select decision and evidence independently, then enforce a named consistency rule | Compare decision-only vs combined; preserve original decision and correction reason |

## Source-bound selection and evidence consistency

For extraction, preserve candidate ID, source revision, original value and location. Verify the candidate still matches the source before using it. Explicitly handle no-match with a label such as `none` (not an invented JSON-null API primitive). Keep missing candidates distinct from model abstention and provider failure. Don't silently truncate candidates: narrow with documented recall tradeoffs, split the task, or report the limit.

Repeated equal values can occur in different contexts; deduplicating values must not erase the source distinction needed by the question. Test omitted gold candidates separately from wrong model choices. These requirements apply to source selection, not to every Noul or Score.

A single candidate is not automatically a match: the only date might be a due date while the requested issue date is absent. Skip semantic evaluation only if deterministic evidence proves the requested role, otherwise allow `none` even for one candidate. If there are no candidates, report missing evidence rather than fabricate a value.

Example consistency rule: if the model chooses an answer-bearing outcome and an existing source, derive `already_answered` from a message source or `answerable_by_docs` from a documentation source. Preserve proposed outcome, evidence ID, final outcome and reason. An existing source is not necessarily relevant evidence; both model judgments may be wrong. Missing/invalid evidence should abstain or escalate rather than fabricate support. Correction count alone is not improvement; compare final outcomes to independent labels.

## Placement, uncertainty and rollout

Ask what an error changes. For each candidate distinguish unavailable provider, timeout/malformed response, uncertain judgment and insufficient evidence. Preserve a usable baseline when appropriate; otherwise escalate. Notification suppression often favors preserving visibility, but choose based on missed-alert and over-notification consequences rather than a universal fail-open rule. Model output never grants authorization.

Specify the concrete fallback action rather than only saying "fail-open": falling back to a keyword filter that rejects a change does not preserve notification visibility. Name whether to deliver the exact change, queue review, retain a baseline filter, or take no action, and explain the consequence. Likewise a unique candidate or deterministic hit is not evidence of semantic correctness unless the product contract establishes it.

Shadow, advisory, human-assisted and automated modes are choices. Select the smallest mode that demonstrates the benefit at acceptable consequence, not a compulsory four-stage process. For example, ranking an existing queue may be useful without ever becoming an approval gate.

Evaluate selective invocation on the full workload, including subset-detector mistakes and hard cases that were confidently misclassified by the baseline. Compare final accuracy/coverage, serious mistakes and requested calls. Offline replay can estimate calls avoided, not prove latency or billed savings. Conditional questions in the same request cannot see one another's answers: use independent questions with explicit premises, or a second request after fetching dependent evidence.

## Exact scope

For PR/branch review, record base/head commits and read files/diffs from those refs. For local work, record HEAD, dirty scope and a diff identifier; do not describe dirty content as committed evidence. Don't require a hash for every file on ordinary discovery. Update evidence if the relevant source changes before an action.

## Research provenance

These patterns were informed by the supplied September 2026 research, not measured production benefits. Source examples checked at fixed revisions include [source-bound extraction](https://github.com/TypeSafeAI/typesafe-playground/blob/84e99e00265e0467c90dd7ba462e4bf84edad73a/src/extraction/extraction.ts), [evidence-based triage](https://github.com/TypeSafeAI/typesafe-playground/blob/84e99e00265e0467c90dd7ba462e4bf84edad73a/lib/classifyQuestionWithJev.ts), and [Huginn predicates](https://github.com/huginn/huginn/blob/07163d4fbc3e8667dd68d711530e838677f88cf4/app/models/agents/trigger_agent.rb). A source implementation does not establish superiority, calibrated thresholds, or universal API limits. Read live API docs for contracts.
