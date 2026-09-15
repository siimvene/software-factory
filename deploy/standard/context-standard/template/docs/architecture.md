# Architecture — {{PRODUCT}} (current state)

> Describes what is true **now**. Not a history, not a plan. When the code changes, this
> changes in the same PR. History lives in `adr/`; deltas live in Jira.

## Purpose

{{ONE_PARAGRAPH: what this service does and for whom.}}

## Context

How this service sits in the wider estate — upstreams, downstreams, shared contracts.

```
{{ASCII or mermaid context diagram: callers → this service → dependencies}}
```

## Components

| Component | Responsibility | Key tech |
|---|---|---|
| {{component}} | {{what it owns}} | {{stack}} |

## Data

- Stores: {{db/engine, ownership, migration tool}}
- Shared contracts consumed/produced: {{openapi / kafka topics / events}}
- Money is decimal end-to-end where applicable (never binary float).

## Runtime & deploy

- Runtime: {{jvm/node/…}}, packaging, entrypoint.
- Deploy: {{GKE / FluxCD / Helm per-country / …}}.
- Migrations run out-of-band (never at app startup).

## Cross-cutting

- AuthN/AuthZ: {{JWT/JWKS, scopes}}.
- Errors: {{RFC 7807 problem+json / …}}.
- Observability: {{metrics/logs/traces}}.

## Known constraints & risks

Link the relevant ADRs and any `Project Iris`-style risk items that touch this service.

<!-- TODO(review): fill from the repo. Keep it current-state only. -->
