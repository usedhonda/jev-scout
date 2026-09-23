# Incident intake: decision-depth fixture

This is a synthetic, undeployed intake service. `incidents.py` routes report text and its consumer stores the selected route, then calls an injected security notifier only for reports routed to `security`. No customer data, model calls, or live notifications are included.

The current rules recognize literal `breach`/`leak`, `billing`/`invoice`, and `outage`/`down`, in that order. Reports with no match wait in a general review queue. A billing queue is routinely reviewed in batches; a security notification is examined promptly. Security staff can handle false alarms, but each interruption has a cost. A missed external exposure can persist until a later review. The team has not established traffic, error rates, review delays, acceptable risk, or API budget.

Illustrative reports (not a labeled benchmark):

- "The invoice dashboard lets an outside visitor download customer PDFs." The current billing match prevents a security notification.
- "A partner can see customer exports without signing in." The current no-match route waits for general review.
- "The billing outage is preventing payment." This legitimately matches billing first, although operations might need it sooner.
- "The incident note says 'no breach'; the user is asking about an invoice." Literal security matching can produce an unnecessary security notification.

Assess this directory for useful Jev opportunities. Explain the strongest candidate with an insertion point, alternatives, and a falsifiable evaluation; identify justified non-adoptions. Do not modify files or call APIs.
