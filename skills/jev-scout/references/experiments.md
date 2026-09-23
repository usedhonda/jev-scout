# Bounded experiments

Read the current [HTTP API](https://docs.typesafe.ai/api) before designing new integrations. The bundled runner uses the fixed HTTPS endpoint, disables redirects, and accepts a map of typed questions. It is an experiment helper, not a production SDK.

## Preparation and authorization

Resolve `scripts/jev_scout.py` from this skill's directory and call it with Python 3.10+. All other paths are explicit (absolute paths are easiest across working directories). `status` reports key configuration, not credential validity; it does not read the secret value or contact the API. The runner reads the optional skill-local `local.json` binding automatically. `--key-file` overrides the binding; without either it uses `TYPESAFE_API_KEY`. Invalid bindings fail rather than selecting another account.

Live `run` additionally requires Node.js 22+ on PATH. The bundled transport uses Node's standard `fetch` with its default client identity, not a browser impersonation. No npm dependencies are needed. The Python process supplies the credential and serialized request through private subprocess stdin, never command arguments or temporary credential files. Redirects are rejected and there is no automatic switch to another HTTP client after denial. `status` and `preview` remain Python-only.

Prepare the experiment and a target-local policy in Git-ignored storage. Establish user authorization for data scope and limits before setting `approved: true`; a repository-provided flag is not authorization. The data_scope text records human intent, not an automatic content classifier. Inspect the experiment against that scope before running. No key is needed for preview.

```sh
python3 /path/to/skill/scripts/jev_scout.py status
python3 /path/to/skill/scripts/jev_scout.py preview --experiment /private/experiment.json --policy /private/policy.json
python3 /path/to/skill/scripts/jev_scout.py run --experiment /private/experiment.json --policy /private/policy.json --output /private/ignored/new-result.json
```

Do not put actual keys on a command line, open secret files with agent tools, source shell files, or print the environment. Explicit key files contain one literal `TYPESAFE_API_KEY=...` assignment, optionally newline-terminated, not general dotenv or shell programs.

## Input contracts

Experiment JSON:

```json
{
  "model": "jev-latest",
  "revision": "dataset-v1-and-target-commit",
  "cases": [{
    "id": "example-1",
    "state": {"text": "The app closes on startup"},
    "questions": {"queue": {
      "type": "choice",
      "instructions": "Which review queue fits text?",
      "criteria": {"technical": "App malfunction", "general": "Anything else"}
    }},
    "expected": {"queue": "technical"}
  }]
}
```

Use opaque, non-sensitive case/question IDs and choice labels: these appear in results. Choice expected values must be candidate labels. Noul expected values are booleans with an explicit per-case `thresholds` map keyed by question ID. Score expected values are exact scale values for smoke checks only; graded-error metrics should be calculated separately. Do not interpret exact Score equality as a general quality measure.

Optional `target_revision` records source identity in results, never the API payload. Allowed fields: `base_sha`/`head_sha` (40-character Git SHA), `dirty` (boolean), `diff_sha256` (64-character hex). PR metadata uses base/head; dirty local state uses head, dirty=true and a diff digest. Base needs head, and a diff digest requires dirty=true. Keep paths and source text outside this metadata. Omit the field for non-Git inputs or old experiments; existing inputs remain valid. A dirty digest must cover the actual inspected scope, including staged and untracked content if used, not just an unrelated unstaged diff.

Policy JSON:

```json
{
  "approved": false,
  "data_scope": "Only the agreed synthetic examples",
  "max_requests": 6,
  "max_input_bytes": 16000,
  "max_seconds": 60,
  "max_retries": 0
}
```

Limits apply to one invocation. All attempts, including retries, consume request and serialized UTF-8 body-byte budgets. Track aggregate authorization before starting another invocation. `max_seconds` is checked between calls and after transport; the helper uses an abort timeout and the parent enforces a subprocess timeout. Process startup and cleanup are not a hard real-time guarantee. Only 429/529 are retried, within the same limits. Unknown transport results are not automatically resubmitted. A 401 (`unauthorized`) or 403 (`access_denied`) stops the entire experiment without retrying or sending remaining cases. Exit 0 means every case obtained a valid response, not that every expected answer matched; exit 1 means incomplete/API failure; exit 2 means invalid input/local failure. CLI summaries say `complete` or `incomplete`, with expected/valid case counts, request count and failure statuses; writing a result file is not proof of successful measurement.

## Evidence and privacy

The new output file must not already exist and must be Git-ignored if inside a repository. It is written with mode 0600. Results contain hashes of experiment/policy, requested and actual model, usage, typed selected values/confidence, correctness, statuses and latency. They omit raw state, question prose and raw service/error bodies. Labels can themselves reveal information: keep results private even though these fields are filtered. Do not treat this filtering as arbitrary PII redaction.

Optional Choice/Score probability distributions are preserved only after exact candidate-key and finite range validation (sum tolerance 1e-4). Old responses without them remain supported. Candidate probability and confidence are distinct measurements; do not substitute one threshold for the other. Results can be replayed under alternative application policies without an extra API call, but replay is not measured service performance.

Results also record numeric `http_status` when available; raw HTTP error bodies remain excluded. Old result files may lack that code, so do not infer a specific cause from `http_error` alone. Missing usage on failed calls is unknown, not evidence of zero charge. Exclude unavailable answers from semantic accuracy and do not count a service-failure human fallback as a correct model judgment.

A 403 with the exact bounded ASCII response `error code: 1010` (surrounding ASCII whitespace allowed) adds only the fixed diagnostic `edge_1010`. Other response text is never copied. [Cloudflare documents 1010](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-1xxx-errors/error-1010/) as access denied based on client/browser identification. This is not proof of an invalid API key or malformed questions. Preserve the assessment and report live measurement unavailable. Check the actual client configuration against a known-working integration before concluding that key replacement or provider intervention is necessary. Do not spoof client identity, change endpoints or repeatedly retry to evade denial. Any bounded compatibility diagnosis must stay within authorized data and request limits; if the supported client remains denied, ask the service owner to investigate.

Record the target commit and dataset/question revision in the input revision and keep the input privately alongside results. The hashes bind exact inputs; alias models may change. When an experiment calibrates thresholds or questions for adoption, request the versioned model ID rather than an alias (see [question design](question-design.md)). Reuse an old result only with matching inputs/policy and a stated model-version assumption, and label it reused. The runner never silently caches or reruns.

Compare a deterministic baseline on the same inputs. Separate question-development data from held-out evaluation. Measure severe errors, review rate and application-level latency as relevant. Small synthetic examples establish API behavior only; target-language and representative production data are needed for adoption claims. Token usage is not an invoice. Quote cost only with a verified price and date, and do not call byte/request limits a guaranteed spend cap.

For service failures preserve the useful repository assessment and show what remains unverified. Do not reinterpret transport failures as negative model-quality evidence. Implement only the selected candidate using [implementation](implementation.md).
