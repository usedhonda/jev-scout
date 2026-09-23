# Synthetic exploration workbench

These independent functions are teaching fixtures, not a product, model evaluation, or throughput claim. `retrieve_notes` supplies a shortlist to a researcher, `choose_draft` picks a generated draft for human review, and `next_step` returns a bounded operation and existing target ID for a dispatcher that rechecks permission and target freshness. A shortlist can omit a relevant paraphrase; a draft can cite many irrelevant sources; an operation can be right while its target is wrong.

`beam_route` is a separate search-control surface: `graph` supplies only legal successors and exact edge costs, and an exact goal ID ends the route. Text overlap with `goal_text` orders the frontier before width pruning. A plausible branch can be pruned, so this bounded beam search makes no optimality or completeness claim. A semantic prior could change branch priority, not legal moves, costs, goal proof, or any requirement for an exact-optimal solver.

`utterance_complete` ends speech capture after a fixed pause. Speakers sometimes pause mid-thought, and waiting longer also delays a completed request. The output is an endpoint hint, not a transcript or permission to act. No latency target or labeled speech set is supplied.

`parse_command` accepts only two words and a known ID; for this finite grammar, exact parsing is adequate. `emergency_stop` must remain immediate and local. `artifact_matches` compares a cryptographic digest exactly. These are negative controls for adoption, not reasons to ignore adjacent user-facing decisions.

Assess shortlist recall, frontier ordering, evaluator independence, operation/target decomposition, and endpointing tradeoffs only where a semantic judgment might change the consumer's outcome. Compare a deterministic improvement, Jev, and an LLM or hybrid where appropriate. Specify failures and an offline falsifiable comparison; do not invent production benefit or put a network call on the hard real-time or integrity paths.
