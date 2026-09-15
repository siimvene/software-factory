---
pack: frontend-angular
description: Mandatory use of @piletilevi/common-angular and common-ui-assets — CQRS client, logging, profiles, layout components, design tokens
maintainer: TBD
status: adopted
source: github.com/Piletilevi/common-angular (standards-as-code, adopted as exemplar 2026-07-22)
---

# PLG Angular Platform Library

The org's Angular standards live as code in
[`Piletilevi/common-angular`](https://github.com/Piletilevi/common-angular)
(`@piletilevi/common-angular`, sub-packages `base` and `components`) and
[`common-ui-assets`](https://github.com/Piletilevi/common-ui-assets) (design
tokens: color primitives, typography, fonts, theme). The library IS the
standard — these rules exist so agents reach for it instead of hand-rolling.

## Rules

1. **HTTP/CQRS**: use the library's CQRS client (`base/src/lib/client` —
   `CqrsHttpClient`, provided retries, base-url resolver). Do not hand-roll
   `HttpClient` wrappers, retry logic, or command/query plumbing in an app.
2. **Logging**: use the library's `LoggerFactory` (`base/src/lib/logging`),
   never raw `console.*` in application code. Log content rules follow the
   `frontend-typescript` logging pack; transport/format per
   `rules/devops/observability.md`.
3. **Environments**: environment/profile resolution goes through the library's
   domain-profile mechanism (`base/src/lib/environments`) — no custom
   `environment.ts` switching schemes in new code.
4. **UI**: before building a component, check `components/` (and its
   Storybook) — back-office layout, app switcher, menus, breadcrumbs, avatar
   exist. Extending the shared component in the library beats forking it into
   an app.
5. **Styling**: use `common-ui-assets` tokens (color primitives, sizes,
   typography, theme). No hardcoded colors/fonts in app styles.
6. **Versioning**: consume via the published package at a pinned version;
   never vendor/copy library source into an app.

## Contributing back

A missing component or client capability is a PR to `common-angular` (CODEOWNERS
apply), not a local workaround — the workaround becomes the divergence the
library exists to prevent. Agents: propose the library PR; flag the temporary
local shim, if unavoidable, as debt in the task's PR description.

Deviation from any rule above is an architecture decision — surface it, don't
pick it silently.
