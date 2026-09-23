# Synthetic support router

The existing router uses English keywords; a human reviews `general`. Queues are billing, technical, general. Routing does not approve refunds or change accounts. No production volume or measured triage time is known. Users may write English or Japanese.

`app.py` adds an optional semantic provider to the existing route, with failures/uncertainty returning to the original behavior. This is a demonstration integration, not a deployed support system.
