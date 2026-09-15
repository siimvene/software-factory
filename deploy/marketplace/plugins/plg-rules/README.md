# plg-rules

## Overview
The **adopted** PLG rule packs, packaged for laptop-natural consumption by
pack-aware review (consort, solo-review) and generation-time loading.
Currently 4 rules — devops CI/CD, devops observability, multilingual API
convention, common-angular library rules — each mirroring a published PLG
source (GPM/GAT Confluence standards, the live common-angular library).

**The release filter is the `status:` field** in the standards repo: only
`status: adopted` rules ship here. The inherited draft corpus (~30 candidate
rules) stays in `plg-development-standards` until a named pack maintainer
validates it against PLG reality — a review citing "the standard" must never
be citing an unvalidated inheritance.

This is a distribution artifact: source of truth is `plg-development-standards`
(git, PR review). Never edit packs here; changes land upstream and ship as a
version bump. Payload grows as maintainers adopt draft packs.

## Usage
`/plugin install plg-rules@plg-skills` — then:
- **consort / solo-review** discover the packs automatically (plugin-cache
  glob), or set `CONSORT_RULE_PACKS`/`PLG_RULE_PACKS` explicitly.
- Repos vendoring packs at `.claude/rules/` take precedence (consort 0.3.1+
  default resolution, no variable needed).

## Maintainers
- Siim Vene. Version tracks plg-development-standards releases — bump both
  together. Adding a rule to the payload requires its `status: adopted` flip
  upstream first, with the adopting maintainer named in the PR.
