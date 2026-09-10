<!-- Ported from the group's spec-repos plugin, 2026-09-10, anonymised. Logic unchanged except where 17-onboarding.md section 5 is cited. -->

# Spec Repos

Skills for working with a team's **specs repo**: a repository organised by business subdomain, where every feature is described by a paired `<slug>.md` (business-facing) plus `<slug>.tech-refs.md` (technical file/folder references) file. The convention and the usage are both below.

## Overview

This bundle assumes the specs repo and the source-code projects it references are checked out as sibling directories. It ships four skills that cover the full lifecycle of that specs repo:

- **check-specs-references**: verifies every repo referenced in the specs repo's `.tech-refs.md` files is actually cloned locally.
- **retrogenerate-specs**: retro-generates spec pairs from existing source code (map projects, then suggest missing specs, then generate a spec pair for a chosen feature).
- **update-specs-for-commits**: given repos plus commits where a story was implemented, adds a new spec pair or updates an existing one to match.
- **check-specs**: validates a specs repository (both files present, every cited path exists, no code identifiers in the business spec) before the specs PR. This one is the checker the reference implementation lost (17-onboarding.md section 5).

---

## Repo organization scheme for spec-driven development

Say a team owns one repository for features, but the features can reference multiple technical projects. Example:

- `team-specs`: folders under this are business subdomains
  - `channels`
  - `organizer`
  - `repertoire`
  - `offer`
    - `configuring-basic-offer-with-unnumbered-places.md`: describes the feature in business terms understandable for non-technical users
    - `configuring-basic-offer-with-unnumbered-places.tech-refs.md`: describes in which systems and their submodules this is implemented, supplemented by either a developer or an agent
    - `setup-access-codes-to-protected-price-categories.md`
    - `setup-access-codes-to-protected-price-categories.tech-refs.md`

### Example `*.tech-refs.md`

`setup-access-codes-to-protected-price-categories.tech-refs.md`, with one heading per project and the cited paths relative to that project's checkout:

```
## backend-service
- offer-api
- offer-impl

## web-frontend
- libs/event-admin-offer
- libs/purchase-flow/src/.../step-1

## mobile-app
- libs/access-code-section
```

---

## Onboarding a team on this

The `retrogenerate-specs` skill automates all three steps of the workflow (its `prepare` / `suggest` / generate modes).

### Step 1, prepare: map source projects into memory

```
/retrogenerate-specs prepare <project-dir> [<project-dir> ...]
```

Run once per team setup (or when a new project is added). The agent scans each source project, builds a feature-area map from routes, pages, controllers, and domain models, and saves the result to persistent memory. Subsequent commands use this memory without re-scanning the full codebase.

### Step 2, suggest: discover what specs are missing

```
/retrogenerate-specs suggest [<subdomain>]
```

The agent cross-references the memorized feature maps and proposes a list of feature-slug candidates as a table: slug, subdomain, projects involved, and a one-line description. Optionally filter by subdomain (e.g. `repertoire`, `offer`). The PM picks which slugs to generate.

### Owner review (reference-implementation addition)

Between suggest and generate, the candidate table is reviewed for business truth by the person in the PM role: merge, split, rename, drop, and mark what is known to be unbuilt. Record the decisions on a shared review artifact. Without that reviewer the output is generated text, not knowledge (17-onboarding.md section 5).

### Step 3, generate: write the spec pair

```
/retrogenerate-specs <feature-slug> <target-spec-dir>
```

The agent explores the relevant projects for that specific feature, then writes two files:

- `<feature-slug>.md`: business-facing description, plain language, no technical jargon. Covers: what the feature is, who can use it, field-by-field walkthrough of each user action, customer-facing impact, and downstream effects.
- `<feature-slug>.tech-refs.md`: precise relative file/folder paths grouped by project and sub-area (routes, controllers, commands, domain, events). Only real paths, verified during exploration.

### Step 3: batch alternative

Prompt after checking the output of step 2 and optionally refining it:

> take the above and push it through mode 3 of /retrogenerate-specs, root target folder is ".../team-specs", create a subfolder per subdomain

### Check and findings file (reference-implementation additions)

After generation, run the `check-specs` skill over the generated spec folders before the specs PR (both files present, every cited path exists, no code identifiers in the business spec), and keep the checker in the team repo so it survives the session. Collect every inline note the writers left into one findings file in the team repo: defects, dead surface, design docs behind the code, governance facts pinned from code. That findings file becomes the ticket backlog for the first cycles (17-onboarding.md section 5).

---

## Making AI use those specs

In every code repo, the repo's `CLAUDE.md` should inform the agent that functional specs are stored in a sibling folder.

Both the PM and the developers check out all the folders they need and the agent needs.

Example:

- `team-specs`: holds the `*.tech-refs.md` files pointing to the folders below
- `backend-service`: backend, its `CLAUDE.md` instructs the agent to use `team-specs` as well
- `web-frontend`: frontend, `CLAUDE.md` with the same advice
- `mobile-app`: shared client, `CLAUDE.md` with the same advice

---

## Usage at a glance

Ask the agent any of the following:

```
Check if the repos referenced in team-specs are checked out
/retrogenerate-specs prepare ../backend-service ../web-frontend
/retrogenerate-specs suggest offer
/retrogenerate-specs create-edit-and-remove-a-show ../team-specs/offer
Update the specs for this story: /update-specs-for-commits ../team-specs backend-service:abc1234
Check the specs: python3 check-specs/scripts/check-specs.py ../team-specs --root ..
```
