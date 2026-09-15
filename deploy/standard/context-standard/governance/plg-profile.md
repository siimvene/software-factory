# PLG adoption profile

The estate-specific overlay on the neutral `STANDARD.md`. This is where PLG facts live,
so the core standard stays employer-agnostic and reusable.

## Required no-touch zones (PLG estate)

Every PLG repo's `CLAUDE.md` No-touch section MUST cover, where present:

- Schema migrations — Flyway/Liquibase applied migrations are immutable.
- Generated code — jOOQ output, OpenAPI clients/models (regenerate + `git diff --exit-code`).
- **Payment / basket paths** — highest blast radius in the estate. No agent change
  without human review; contract tests against legacy *and* the consolidated platform.
- Global Accounts / OAuth / OIDC config (`accounts.plgmoments.com` integration).
- FluxCD/Helm per-country deploy values, `.github/workflows/**` release gates.

## Starter-kit lineage

`CLAUDE.md` front-matter `starter-kit:` SHOULD name the bookstore-family kit the repo's
stack derives from (e.g. `boot-backend`, `nuxt-ui`, `micronaut-backend`), so contract
and CI conventions are inherited, not reinvented. Backends consuming a shared contract
vendor a byte-identical copy and verify the pinned sha in CI.

## Conformance expectations

- New repos: L0 at creation, L1 within the first delivery cycle.
- Consolidated-platform services: L2 (CI-enforced) — these carry exit-critical weight.
- Legacy (phasing out through 2027): L0 is enough; don't over-invest in docs for code
  being decommissioned. Prioritize the four Project Iris gap areas.

## Retrieval

memspec hybrid retrieval needs a reachable embeddings endpoint. If PLG stands up an
org embeddings proxy, set it in each repo's `.memspec/config.yaml`; until then repos
run `engine: fts` (keyword-only), which needs no service.

<!-- TODO(review with Martin): confirm the payment/basket path globs, the kit lineage
     names actually in use, and whether an org embeddings endpoint exists. -->
