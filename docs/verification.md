# v1 verification

## Host compatibility

Claude Code 2.1.278 (Sonnet) and Codex CLI 0.155.1 (GPT-5.6 Luna) loaded the same `jev-scout` skill through their supported discovery locations. Both assessed the same support and pipeline source/README inputs and returned grounded alternatives and missing-evidence statements rather than automatic adoption. Additional host checks covered library/operations (CC) and mobile/AI app (Cdx).

- Library: exact hashing was rejected as a Jev use case.
- Mobile: offline-only behavior was preserved as a constraint.
- Operations: missing incident data, volumes and labels were identified.
- AI app: closed tool selection was separated from prose generation and permissions.
- Support: both compared a bilingual dictionary before claiming benefit.
- Pipeline: both suggested filtered reranking with evaluation gaps. They did not explicitly flag candidate-recall limits, so the discovery reference now explains that reranking cannot recover omitted candidates.

These are bounded behavioral smoke checks, not exhaustive cross-model evaluations. The final recall clarification was source-checked, not followed by another model run. CC's first plan-mode probe created its own host plan artifact despite a read-only request; the subsequent normal-mode probe did not. No product source or credential was changed by these probes. An unrelated optional MCP authentication warning appeared in the Codex process; Skill loading and assessment completed.

## Synthetic live API comparison

Only the six hand-authored English/Japanese cases in `evals/support/experiment.json` were sent. Limits were six requests, 16,000 serialized request bytes, 60 seconds, no retries. Actual body bytes: 3,203. The dedicated key stayed local.

| Method | Correct synthetic labels |
| --- | --- |
| Original English keyword rule | 2 / 6 |
| Bilingual dictionary improvement | 4 / 6 |
| Jev | 6 / 6 |
| Application replay of recorded Jev answers | 6 / 6 |

Actual model: `jev-1.13.0`. Usage: 2,356 input tokens and 228 output tokens. Per-request elapsed times: 1,204.141, 1,212.533, 1,258.000, 942.169, 851.558, 833.920 ms. These are client-observed sequential call times, not production latency percentiles or full-workflow benchmarks. No price/invoice claim is made.

This proves live protocol/authentication and these six judgments. The example application replay tests the integration's consumer and fallback, not a deployed application making live requests. The confidence threshold in the demonstration is illustrative, not calibrated. Production adoption still needs representative held-out data, error-cost criteria and application-level measurements.

## Reproduce without spending

Run `python3 -m unittest discover -s tests -v` and the README preview command. `python3 evals/support/compare.py` evaluates the two deterministic baselines. Passing an existing private runner result with `--result` verifies its experiment hash and replays it without an API call. The original result is deliberately not distributed.

## Deeper-placement revision verification

The additional research was compared against implemented v1 rather than copied wholesale. Shared instructions now separate user value from placement and add selective invocation, source-bound selection, explicit evidence invariants and consequence-based rollout. Both hosts used the same open request on `evals/placement`, without the maintainer rubric.

- CC proposed semantic predicates, post-diff materiality and no-hit/conflict label resolution with concrete insertion points.
- Cdx proposed semantic predicates, post-diff relevance and source-bound date selection. Both retained exact comparison/ACL operations and stated missing production evidence.
- Initial outputs exposed two actual guidance gaps: CC called fallback to a suppressing keyword rule "fail-open"; Cdx assumed one candidate requires no semantic check. Instructions were narrowed to reject these shortcuts.
- On targeted follow-up probes both hosts rejected using a sole due date as the requested issue date and preserved notification visibility when timeout plus high missed-alert cost required it. These targeted probes are evidence for those boundaries, not a second blind evaluation of all patterns.

Offline acceptance: 20 tests passed; Skill frontmatter validation passed. The old support experiment preview remained valid. Both installed host paths resolve the shared runner from a different working directory, with dedicated-key configuration detected without printing the secret.

### New live experiment limit

Four frozen synthetic decision/evidence cases were attempted with a new policy: four requests, total 16,000-byte limit, 60 seconds, zero retries. Actual request-body total was 4,334 bytes. All four returned `http_error`; none supplied a usable judgment. The then-current result format did not retain numeric HTTP codes, so the specific cause is unresolved. No extra calls were made after the budget was consumed. This is not evidence of model inaccuracy or zero cost.

The result comparator now reports no semantic accuracy, placement comparison or reported usage when judgments are unavailable. Numeric HTTP status is now retained without error bodies for future diagnosis. Original experiment results were not rewritten. Local tests separately prove source mismatch rejection, missing/out-of-set evidence handling, deterministic source-type correction, service-failure distinction and selective-placement replay. Live decision/evidence quality remains unverified; the earlier v1 six-case result is historical, not substituted for this experiment.

## Access-denial diagnosis (2026-09-23)

One additional request used the first frozen synthetic evidence case and the existing fixed endpoint/transport. The response was HTTP 403, 17 bytes, matching the fixed marker `error code: 1010`. Neither the credential nor arbitrary response content was printed or saved. No further live requests, client-identity changes or endpoint substitutions were made. This identifies the current access denial, not the precise cause of the earlier unclassified four failures.

[Cloudflare's official 1010 documentation](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-1xxx-errors/error-1010/) describes client-identification-based denial and directs resolution to the site owner. Credential invalidity, schema invalidity and model quality cannot be concluded from this evidence. Service access remains unresolved; no live judgment was obtained in this diagnosis.

The runner now stops the whole experiment on either 401 or 403, records a fixed allowlisted diagnostic only for the narrowly matched 1010 response, and emits explicit incomplete/complete summaries with valid-case counts. Mocked regression checks cover a two-case denial making exactly one request, poisoned-response exclusion and incomplete CLI reporting. These establish local failure handling, not restored API access.

## Working-client compatibility (2026-09-23)

A known-working integration used Node's standard fetch. Its non-secret call implementation was compared with this runner: endpoint, Bearer authentication, JSON Content-Type and request shape matched. One controlled compatibility request then used this runner's existing dedicated key and the identical serialized first synthetic evidence case through Node v24.2.0 fetch, without a custom User-Agent. It returned HTTP 200, model `jev-1.13.0`, and answers accepted by the existing strict validator.

This proves the current key works with that standard client. It does not isolate whether the earlier rejection depended on headers, TLS behavior, timing or other edge policy. No key replacement, browser impersonation, proxy or alternate endpoint was involved. Provider escalation was premature before checking the known-working client.

The bundled runner now uses a Node 22+ fetch helper, with the key and request supplied through subprocess stdin. Python-only discovery/status/preview remain available. Both hosts still resolve the same canonical skill and private key binding; no host-specific transport is introduced.

The integrated CLI then ran all four unchanged frozen evidence cases with a new private policy: four requests, 16000-byte/60-second caps, zero retries. All four produced valid responses (`complete`, exit 0). Raw decision accuracy was 3/4, and application outcome accuracy was also 3/4. The prior-message case was misclassified as documentation; the illustrative confidence policy routed it to human review rather than correcting it. No questions or labels were tuned after seeing these results.

Reported usage was 2274 input tokens and 329 output tokens. Offline placement replay scored never 1/4, always 3/4 with four selected cases, no-hit 3/4 with two selected cases, and conflict 2/4 with one selected case. These four synthetic cases do not establish production accuracy or actual selective-call savings. This turn made five live requests total including the initial compatibility probe; the new four-case private result was saved separately from the previous failures.

Worker validation: 25 repository tests passed before final boundary fixes; four affected focused tests passed after those fixes, with Python/Node syntax checks. Parent independently inspected the integrated transport and ran the live four-case CLI plus saved-result comparison. Shared Skill validation passed. Canonical helper resolution also covers CC/Cdx symlink entrypoints without extra API calls.

## Blind placement evaluation for publication (2026-09-23)

Claude Code and Codex CLI independently assessed the same synthetic `evals/placement/` workbench in read-only mode. Both received the same open discovery request; neither received or read the maintainer rubric, prior reports, credentials, or API results. Both proposed four bounded opportunities with insertion points, invocation conditions, alternatives, retained deterministic code, and falsifiable offline checks. The common leading set was a semantic rule type, post-diff notification relevance, source-bound date selection, and selective no-hit/conflict label advice. Both kept exact version ordering and authorization in code, and treated value as unmeasured.

The Claude Code report additionally identified `dispatch_request` as a bounded Choice/Noul argument decision while keeping `route_ticket` invocation in code; `due_soon` as semantic date selection with arithmetic in code; adversarial comment text as untrusted data; operation-based escalation criteria; and churn scores only as additional features. The Codex report discussed these as next-tier opportunities and explicitly warned against granting visibility or replacing the churn model. Codex's four chosen candidates met the requested depth, though its next-tier dispatch/due-date treatment was less specific. Neither result establishes an adoption recommendation for a real repository or a live API improvement. No further Skill change was justified by this check.

This is a behavioral sample from the installed hosts, not a statistically representative cross-model benchmark. No files were changed by either probe and no API call was made. The private raw transcripts are intentionally excluded from the distribution.
