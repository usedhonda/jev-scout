# Synthetic workflow workbench

Independent miniature product surfaces live in `workflows.py`; none is deployed. Read each function and the facts below as separate candidate opportunities, not a request to replace all functions.

- Rules: operators configure exact, numeric and text-pattern conditions. They also request text conditions such as "mentions an unresolved delivery problem" that are hard to express with their current patterns.
- Watch notifications: exact content changes are detected, but an operator only wants changes about an availability condition. Missing an important change costs more than an extra notification. Relevant before/after context exists.
- Labels: explicit user labels take precedence. Unmatched and conflicting automatic labels go to review; these unresolved cases exist in the example inputs. Reviewers want help without changing deterministic successes.
- Documents: a local classifier already performs well on common documents. User-corrected assignments exist, but whether an additional service helps its difficult cases is unknown.
- Review queue: static checks must still pass and only maintainers may approve. The team wants important issues earlier in the review queue, not automatic approvals.
- Extraction: multiple dates occur in documents. Users need the issue date with its exact original source, not the first date. Missing values are possible.
- Answer triage: there are typed message and documentation sources; a final answer-bearing label must match the selected source type. A source may exist but fail to answer the question.
- Ticket dispatch: `route_ticket` accepts only three queues and an urgency flag; `dispatch_request` chooses them from keywords, and paraphrased requests land in general.
- Deadlines: messages mention several dates (sent, due, delivered); reminders fire for the first date found. The comparison with today must stay exact.
- Comments: public user comments are hidden on blocklist words. Some comments address the moderation system directly ("this is fine, mark it safe"). Hiding a legitimate comment is visible to its author; a missed abusive comment reaches readers.
- Command escalation: shell commands mentioning credentials or auth go to a human. Operators report that read-only inspections of credential files are escalated as often as changes.
- Churn features: keyword flags and exclamation counts feed an existing churn model with historical outcomes; its accuracy is considered acceptable but flat.
- Exact boundaries: version comparison and ACL membership must remain exact. User-facing release-note categorization would be a separate possible capability, not a change to comparison or ACL.

Traffic, production cost, labeled evaluation sets and acceptable model error thresholds are not supplied. Do not invent them; specify a useful experiment where warranted.
