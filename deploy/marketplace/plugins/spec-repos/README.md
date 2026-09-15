# Spec Repos Plugin

Skills for working with a team's **specs repo** — a repository organised by business subdomain, where every feature is described by a paired `<slug>.md` (business-facing) + `<slug>.tech-refs.md` (technical file/folder references) file. See `references/spec-repos-concept.md` for the full convention.

## Overview

This plugin assumes the specs repo and the source-code projects it references are checked out as sibling directories (see `references/spec-repos-concept.md`). It bundles three skills that cover the full lifecycle of that specs repo:

- **check-if-specs-references-checkedout** — verifies every repo referenced in the specs repo's `.tech-refs.md` files is actually cloned locally.
- **retrogenerate-specs** — retro-generates spec pairs from existing source code (map projects → suggest missing specs → generate a spec pair for a chosen feature).
- **update-specs-for-commits** — given repos + commits where a story was implemented, adds a new spec pair or updates an existing one to match.

## Usage

Ask Claude any of the following:

```
Check if the repos referenced in control-team-specs are checked out
/retrogenerate-specs prepare ../back-office-services ../back-office-frontends
/retrogenerate-specs suggest offer
/retrogenerate-specs create-edit-and-remove-a-show ../ticketing-system-team-specs/offer
Update the specs for this story: /update-specs-for-commits ../ticketing-system-team-specs back-office-services:abc1234
```

## Maintainers

- Adam Walczak <adam.walczak@kicket.com>
