# Semantic seams behind weak signals

Use this reference when a repository uses an observable but imperfect **proxy** for the meaning its consumer needs. Trace `real input -> proxy -> bounded decision -> consumer/side effect`. Name the mismatch and identify cases where the current rule is already definitive. This is an inspection lens, not a mandate to add a model.

Before proposing Jev, answer:

1. Can the proposed input distinguish the outcomes? Identical visible evidence means information insufficiency, not a classification opportunity.
2. Is the needed output finite (label, boolean, candidate ID, ordered rubric)? Keep arbitrary text, exact arithmetic, parsing, permissions and side effects with their existing owners.
3. What is the cheapest deterministic improvement, and what would it still miss? Compare on the same held-out cases.
4. What does a wrong decision change? Selective fallback, advisory or suppress-only placement may be safer; specify timeout, uncertain and out-of-set behavior separately.
5. Does the product promise a canonical, reproducible answer? If so, probabilistic variation may destroy its value even in a subjective-looking domain.

| Proxy family | Seam to inspect | Boundary or counterexample |
| --- | --- | --- |
| HTTP status, redirect, error text | Protocol success but semantic failure: soft-404, blocked, login or wrong object | Inspect a sanitized excerpt only when body evidence differs; identical pages remain unknown |
| Regex, prefix, line state machine | Static reply/quote/signature boundary or low-volume multiline event identity | Retain MIME/stream mechanics and known markers; a hot path may reject a remote call |
| Convention parser returning unmatched | Meaningful human text falls outside strict syntax | Keep explicit rules and version arithmetic; if compliance is policy, enforce it instead |
| Age, timestamp, stale label | Time stands in for workflow responsibility | Distinguish reporter-wait from maintainer-wait; uncertainty must not authorize closure |
| XPath, class name, link density | Structural hints decide which source block survives | Use existing DOM IDs and retain obvious exclusions; measure body loss and contamination |
| Generative output with enum/ID and free text | One model chooses a closed operation and writes content | Split only operation and target ID; retain extraction, generation, validation and mutation elsewhere |

For an existing AI call, inspect the **output schema and active caller**, not just the prompt. A prompt or enum present in a repository does not prove it is on the active path. Compare a split Jev design with the current model plus stricter structured output or an additive design. Never grant DELETE, publish or another irreversible side effect directly to the semantic result.

Selective invocation is an end-to-end policy: evaluate its subset detector on the full workload, including confidently wrong baseline cases. For old memory IDs or DOM nodes, report candidate recall separately from conditional model accuracy and final output quality. Evaluate asymmetric harm (false account existence, dropped reply text, under-bumped release, wrong deletion, wrongful issue closure, lost article body), abstention, service failures, calls per item and whole-pipeline latency. No invented savings or universal threshold.

Negative controls matter. A canonical formatter is not a replacement target merely because formatting feels stylistic. A site returning indistinguishable claimed and unclaimed pages is not rescued by a semantic classifier. Explain why these are non-candidates while recognizing separately evidenced adjacent capabilities.

Research-inspired, untested placement examples at fixed revisions: [Sherlock response handling](https://github.com/sherlock-project/sherlock/blob/376018708c0f6948d3f978a9ae2915024e794654/sherlock_project/sherlock.py), [email-reply-parser fragment scanning](https://github.com/zapier/email-reply-parser/blob/f67a872de3c7bebe3bd836afec60ab3f1201e8a6/email_reply_parser/__init__.py), [commit analyzer](https://github.com/semantic-release/commit-analyzer/blob/1dbd3a049092dfc0cd9af94d25895af0131837ca/index.js), [Mem0 memory-update prompt](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/configs/prompts.py), [actions/stale processing](https://github.com/actions/stale/blob/3467b6485bf80d2be20f30ec1a3d2d2aea0330e9/src/classes/issues-processor.ts), [Trafilatura extraction](https://github.com/adbar/trafilatura/blob/c852cae9708a59f04521b19395d8ed49771a5c78/trafilatura/main_extractor.py), and [Black formatting](https://github.com/psf/black/blob/2b96e280653fd79f593c942191d8614ca6ce39e6/src/black/__init__.py). These links show seams, not Jev deployment or benefit. Recheck the active caller and current version before applying an example elsewhere.
