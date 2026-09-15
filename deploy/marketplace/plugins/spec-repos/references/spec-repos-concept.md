## Repo organization scheme for SDD

Lets say we have a team called "Ticketing System Team". They should have one repository for features, but features can reference multiple technical projects. Example:
- ticketing-system-team-specs - folders under this a business subdomains
  - channels
  - orginizer
  - repertiore
  - offer
    - configuring-basic-offer-with-unnumbered-places.md - describes the feature in bussines term understandable for non technical users
    - configuring-basic-offer-with-unnumbered-places.tech-refs.md - describes in which systems and their submodules is this implemented, this would be suplemented by either developer or AI
    - setup-access-codes-to-protected-price-categories.md
    - setup-access-codes-to-protected-price-categories.tech-refs.md

### Example *.tech-refs.md

setup-access-codes-to-protected-price-categories.tech-refs.md:

```
- back-office-services/offer-api
- back-office-services/offer-impl
- back-office-frontends/libs/event-admin-offer
- back-office-frontends/libs/pos-purchase-flow/src/.../step-1
- purchase-flow/libs/access-code-section
```

## Onboarding a team on this

The `gen-spec` skill (`.claude/commands/gen-spec.md` in this repo) automates all three steps of the workflow.

### Step 1 — Prepare: map source projects into memory

```
/gen-spec prepare <project-dir> [<project-dir> ...]
```

Run once per team setup (or when a new project is added). Claude scans each source project, builds a feature-area map from routes, pages, controllers, and domain models, and saves the result to persistent memory. Subsequent commands use this memory without re-scanning the full codebase.

### Step 2 — Suggest: discover what specs are missing

```
/gen-spec suggest [<subdomain>]
```

Claude cross-references the memorized feature maps and proposes a list of feature-slug candidates as a table — slug, subdomain, projects involved, and a one-line description. Optionally filter by subdomain (e.g. `repertoire`, `offer`). The PM picks which slugs to generate.

##



### Step 3 — Generate: write the spec pair

```
/gen-spec <feature-slug> <target-spec-dir>
```

Claude explores the relevant projects for that specific feature, then writes two files:

- `<feature-slug>.md` — business-facing description, plain language, no technical jargon. Covers: what the feature is, who can use it, field-by-field walkthrough of each user action, customer-facing impact, and downstream effects.
- `<feature-slug>.tech-refs.md` — precise relative file/folder paths grouped by project and sub-area (routes, controllers, commands, domain, events). Only real paths — Claude verifies them during exploration.

### Step 3 - batch alternative

Prompt after checking output of step 2 and potentialy refining it:

take the above and push it through mode 3 of /gen-spec, root target folder is "...\ticketing-system-team-specs", create subfolder for subdomains

---

## Making AI use those specs

In every repo in `CLAUDE.md` we should inform AI that functional specs are stored in a sibling folder.

We assume both PM and devs checkout all the folders they need and the AI needs.

Example:
- ticketing-system-team-specs - has those `*.tech-refs.md` poiting to the folders below
- back-office-services - backend, `CLAUDE.md` instructs AI to use `ticketing-system-team-specs` as well
- back-office-frontends - frontend, `CLAUDE.md` with same advice
- purchase-flow - shared UI lib, `CLAUDE.md` with same advice
