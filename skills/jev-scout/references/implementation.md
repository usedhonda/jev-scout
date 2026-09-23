# Implement a selected candidate

Confirm selection from the user's request or existing task scope; do not solicit approval again for the same authorized work. Read the target's build/test/architecture instructions and current API/SDK reference before integration. Keep the experiment runner separate from production dependencies unless the target explicitly needs a CLI experiment tool.

1. Specify the current contract to preserve and the behavior to change. Establish baseline examples and the smallest meaningful acceptance check.
2. Follow the existing stack. Obtain candidate data in code, ask narrow semantic questions, validate typed results, and apply decisions through existing application logic. Keys stay in a private runtime, never frontend bundles.
3. Define uncertainty and service-failure behavior for this actual consumer. A human-review queue may be appropriate; an automatic LLM fallback is not mandatory. Check input freshness before side effects. Keep authorization and exact calculations independent of model output.
4. Make the smallest integration. Prefer an existing feature toggle or injected provider where available; do not invent a framework for one call. Preserve a working non-Jev path when the product requires it.
5. Test behavior with representative examples and service failures. Live API evidence and mocks prove different things. Report whether the real application execution path was exercised.
6. Complete project-required build/restart/commit steps within scope. Separate local integration, live service proof and deployment. Do not silently publish or deploy from a discovery request.

For selective placement, preserve deterministic successes and explicit user labels; measure the final workload rather than only the easy routed subset. For evidence-bound decisions, test source mismatch, missing candidates, incompatible evidence and service failures separately. Keep proposed and corrected outcomes for audit; automatic correction is allowed only for an explicit invariant. Use [integration patterns](integration-patterns.md) to select an appropriate rollout instead of imposing a universal sequence.

For unknown production requirements, deliver a concrete integration proposal and identify the specific missing decision rather than pretending a fixture is production-ready.
