# Documentation Manifest — {{PRODUCT}}

The index of this repo's **current-state** docs. One row per module/area, pointing at
the doc that describes what is true *now*. Jira/PRs hold the delta; this holds the state.

Keep this table in sync with reality — a module with no row is invisible to agents and
new engineers.

| Module / area | State doc | Owner | Last reconciled |
|---|---|---|---|
| Overview | [architecture.md](architecture.md) | {{OWNER}} | {{DATE}} |
| {{MODULE}} | {{docs/modules/xxx.md}} | {{OWNER}} | {{DATE}} |

<!-- TODO(review): one row per real module. Delete this comment once populated. -->

## Conventions

- Module state docs live under `docs/` (e.g. `docs/modules/<name>.md`).
- "Last reconciled" = the date a human/agent last confirmed the doc matches the code.
- When a doc drifts from the code, fix the doc in the same PR as the code change.
