# Jev Scout contributor notes

## Architecture

- `skills/jev-scout/SKILL.md` is the distributable agent-skill entrypoint.
- `skills/jev-scout/scripts/` contains the dependency-light Python and Node CLI helpers.
- `evals/` contains example workflows and evaluation material; `tests/` contains the Python unit tests.
- Discovery and preview are keyless. Only an explicitly approved `run` experiment may use the optional TypeSafe API key.

## Development checks

Use Python 3.10 or newer. Node.js 22 or newer is required only for live API runs.

```sh
python3 -m unittest discover -s tests -v
python3 skills/jev-scout/scripts/jev_scout.py status
python3 skills/jev-scout/scripts/jev_scout.py preview --experiment evals/support/experiment.json --policy evals/support/policy.example.json
```

Do not commit local key bindings, credentials, experiment outputs, or other `.local/` data.
