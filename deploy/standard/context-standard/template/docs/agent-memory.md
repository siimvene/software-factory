# Agent Memory — {{PRODUCT}}

Durable, human-readable notes for agents working in this repo: the sharp edges, the
"we tried X, it doesn't work because Y", the non-obvious local conventions. Prose form,
for things that don't fit a memspec claim or a formal ADR.

> This complements `.memspec/` (structured, queryable) — it does not replace it. If a
> note is a fact/decision/procedure, put it in memspec and anchor it. Put it here when
> it's guidance or context that reads better as a paragraph.

## Gotchas

- {{e.g. "The X client caches Y for 5 min; restart after config changes."}}

## Local conventions

- {{e.g. "Tests use Testcontainers; Docker must be running."}}

## Do-not

- {{e.g. "Never regenerate the OpenAPI client without re-vendoring the contract sha."}}

<!-- Seed at L0/L1, grow as agents learn. -->
