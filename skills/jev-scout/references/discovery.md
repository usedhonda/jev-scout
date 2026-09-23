# Discovery lenses and evidence

Search terms (regex, keywords, routing, scoring, ranking, manual review, prompt/parse) are entrypoints, not findings. Follow actual callers and data availability. Stop expanding inspection once additional files cannot change the leading recommendations; state coverage honestly.

| Surface | Useful hypothesis | Counterexample / boundary |
| --- | --- | --- |
| Web service | Semantic ticket routing beyond keyword matches | Authorization and refund execution remain deterministic |
| Mobile application | Prioritize text notifications or classify feedback | Offline-only UX cannot silently acquire a cloud dependency |
| CLI/library | Select among ambiguous human-language candidates | Exact checksums, parsers and arithmetic rarely need Jev |
| Data pipeline | Rerank retrieved records or label textual features | Do not send an entire corpus when filtered evidence suffices |
| AI application | Replace structured decisions or check specific claims | Free-form generation still needs another mechanism |
| Documents/operations | Sort documented review queues | A policy document alone does not prove review volume or pain |

Also look for newly useful actions supported by stored information, not only replacements. For each new capability identify the real dataset, prospective consumer, and unverified demand. Do not invent UI, database access, labeling availability, or ownership.

Check candidate recall before proposing reranking: if keyword retrieval omits the relevant document, scoring the same shortlist cannot recover it. Compare broader candidate retrieval as well as reranking when the reported failure is missing paraphrases.

An existing deterministic improvement is an alternative, not proof that the problem is solved. Read available representative tests before claiming it covers the gap. Missing production volumes should qualify a promising experiment, not automatically suppress it. Do not require users to implement every deterministic alternative before testing Jev; compare the cheapest meaningful baseline alongside it.

Follow unmatched paths, rule conflicts, user-corrected assignments, source spans, diff-to-notification boundaries and predicate registries. Consider latent product value (for example user-defined semantic watch conditions), not only cost reduction. Consult [integration patterns](integration-patterns.md) when these seams exist. Do not treat a hash/parser/ACL negative signal as rejection of every feature in that product.

Also follow these seams when they exist:

- **Typed actions behind language parsing:** a function with closed arguments (enum, `Literal`, boolean, known IDs) is called after keyword or regex interpretation of natural language. Map only the bounded arguments to Choice/Noul; keep free text, arbitrary numbers and the call itself in code.
- **Repeated agent action selection:** an agent or tool loop repeatedly asks a generative model which known tool, operation or on-screen element to use. Consider Jev selecting operation and target IDs from a runtime-indexed closed set, with the executor revalidating freshness and permissions and a generative model used only when text must be written.
- **Handcrafted text features in a classical model:** keyword flags or counts feed an existing predictor. Consider Noul/Score probabilities as additional features rather than replacing the predictor; this needs offline labeled data and a comparison against the current features.

Do a separate, bounded control-plane pass when the repository has iterative work, costly computation, state retention, streams, or generated candidates. Follow the code that decides **stop/continue**, **keep/evict**, **run/skip**, **commit/wait**, or **which branch/candidate to examine next**. Search terms such as `max_rounds`, `retry`, `compact`, `affectedTests`, `silenceTimeout`, `heuristic`, and `best_of_n` are entrypoints, not findings. Trace the actual state, downstream consequence and hard constraints; then read [control-plane patterns](control-plane.md). Do not spend this pass on repositories with no such seam or invent a workload from a keyword match.

## Report card example

**Candidate:** ticket queue selection in `router.route`, consuming `ticket.text`.
**Observed:** English keyword routing sends paraphrases to general review in supplied tests.
**Proposal:** Choice over existing queue identifiers, including general review; no permission or payment changes.
**Alternatives:** extend the small bilingual dictionary first; Jev only helps if phrasing varies enough to justify a service.
**Evidence:** fixture behavior, not production benefit. Traffic and manual triage cost unknown.
**Evaluation:** held-out labeled tickets, severe misroutes and review rate, whole-pipeline latency; reject if the simple baseline is equally effective at lower burden.

Do not copy this conclusion onto repositories without the corresponding evidence.
