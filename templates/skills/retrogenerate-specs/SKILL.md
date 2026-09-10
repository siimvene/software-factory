---
name: retrogenerate-specs
description: Use this skill when the user wants to retro-generate feature specs from existing source code for a specs repo, e.g. "map these projects for spec generation", "suggest which specs are missing", "generate a spec for create-edit-and-remove-a-show", "write the tech-refs for this feature". Has three modes (prepare / suggest / generate) selected by the first argument.
version: 1.0.0
---
<!-- Ported from the group's spec-repos plugin, 2026-09-10, anonymised. Logic unchanged except where 17-onboarding.md section 5 is cited. -->

# Retrogenerate feature specs from source code

Three modes of operation, selected by the first argument. All three write specs that follow the convention in `../README-specs.md`: one specs repo, subdomain folders, paired `<slug>.md` (business-facing) plus `<slug>.tech-refs.md` (technical paths) files per feature.

---

## Mode 1: Prepare

```
/retrogenerate-specs prepare <project-dir> [<project-dir> ...]
```

Scan one or more source projects, build a feature map for each, and save everything to memory so future runs can use the knowledge without re-exploring the full codebase.

### Steps

1. **Spawn one Explore subagent per project** (all in parallel). Each agent must:
   - **Stay strictly within the given `<project-dir>`**: never read, glob, or search outside of it; do not traverse parent directories or follow symlinks that lead outside
   - Identify the project type (admin dashboard, point-of-sale frontend, backend service, marketplace, etc.)
   - Map all major feature areas from a product/user perspective by looking at routes, pages, API endpoints, controllers, and domain models
   - Note the tech stack (framework, main libraries)
   - Return a structured, concise feature map grouped by area

2. **Save a memory file** for each project using memory type `project`:
   - Path: `<memory-dir>/project_<slugified-project-name>.md`
   - Include: absolute project path, project type and stack, full feature area map, and any notable technical boundaries (e.g. "this project is read-only; writes go to the reservation-service")

3. **Update `MEMORY.md`** with a one-line entry pointing to each new memory file.

4. **Report** which projects were mapped and list the top-level feature areas found in each.

---

## Mode 2: Suggest

```
/retrogenerate-specs suggest [<subdomain>]
```

Use the memorized project knowledge to propose a comprehensive, exhaustive list of feature-slug candidates: everything that could realistically become a spec. Optionally filter by a business subdomain (e.g. `repertoire`, `offer`, `channels`).

### Steps

1. **Load all `project_*.md` memory files** to get the feature area maps.

2. **Derive candidate features aggressively**, be feral about this. Mine every route, every controller, every domain model, every message topic, every menu item. Do not group things too eagerly; when in doubt, split into separate slugs. Aim for 50+ candidates across an average codebase. Apply the following decomposition rules:

   - **Every CRUD entity gets its own slug**: don't merge "manage X" into a catch-all; write `create-edit-and-remove-a-show`, `create-edit-and-remove-a-price-category`, etc.
   - **Every distinct user role's view of the same feature gets its own slug**: e.g. `view-sales-reports-as-organizer` and `view-sales-reports-as-system-admin` are separate if the data scope differs.
   - **Every multi-step flow is a slug**: ticket sale at point of sale, marketplace checkout, voucher purchase, product sale, embedded reservation, all separate.
   - **Every configuration screen is a slug**: payment provider setup, notification settings, purchase profile, invoice provider, consent settings, etc.
   - **Every report or analytics view is a slug**: sales report, reservation report, place report, affiliate sales report, cash operations report, stats dashboard.
   - **Every integration or channel-specific capability is a slug**: embedded widget per type, affiliate API, payment link, ticket template per channel.
   - **Every lifecycle operation is a slug**: cancel reservation, adjust reservation, transform sale to compensation, expire voucher, invalidate tickets, resend confirmation email.
   - If a subdomain argument was given, still be exhaustive but limit output to that subdomain.

3. **Present the suggestions** as a table with columns:
   | Feature slug | Subdomain | Projects involved | One-line description |
   |---|---|---|---|

   Sort rows by subdomain, then alphabetically within each subdomain. Do not truncate the list.

4. Ask the user which slug(s) they want to generate specs for.

---

## Owner review

Between Mode 2 and Mode 3, the candidate table is reviewed for business truth by the person in the PM role: merge, split, rename, drop, and mark what is known to be unbuilt. The table is generated text until a person who can judge business truth signs off on it; without that reviewer the output is not knowledge. Record the decisions on a shared review artifact so the approved slug list is auditable. This owner-review step is an addition from the reference implementation (17-onboarding.md section 5, the retro-generate step).

---

## Mode 3: Generate

```
/retrogenerate-specs <feature-slug> <target-spec-dir>
```

Generate the two spec files for a named feature using memorized project knowledge plus targeted code exploration.

- `feature-slug`: kebab-case feature name, also becomes the filename (e.g. `create-edit-and-remove-a-show`)
- `target-spec-dir`: absolute path to the folder where the two files should be written; per `../README-specs.md` this should be the subdomain folder inside the team's specs repo (e.g. `.../team-specs/offer`)

Output files:
- `<target-spec-dir>/<feature-slug>.md`: business-facing description, readable by non-technical stakeholders
- `<target-spec-dir>/<feature-slug>.tech-refs.md`: precise file/folder paths across all relevant projects

### Steps

1. **Load project memory**: read all `project_*.md` files to get the known projects and their feature areas.

2. **Select relevant projects**: reason from the feature slug and the memory maps to decide which projects are likely to contain code for this feature. Exclude projects whose feature map has no overlap with the topic.

3. **Explore each selected project in parallel** using Explore subagents. Each agent must:
   - **Stay strictly within that project's directory**: never read, glob, or search outside of it; do not traverse parent directories or follow symlinks that lead outside
   - Find routes, page components, or controllers that handle this feature
   - Find services, commands, handlers, or DAOs that implement the business logic
   - Find domain models or entities involved
   - Find message-bus or domain events published or consumed
   - Find shared libraries or reusable components
   - **Return precise relative paths from the project root only**: no invented or guessed paths

4. **Write `<feature-slug>.md`** with these sections:
   - **Overview**: what the feature is, why it exists, key concepts (no technical jargon)
   - **Who can do this**: roles/permissions as a markdown table
   - One H2 per major user action (e.g. Create / Edit / Remove) describing: input fields and their constraints, validation rules in plain language, what happens on save
   - **Customer-facing impact**: what changes for end users
   - **Notifications and downstream effects**: events, cascades, or integrations triggered

5. **Write `<feature-slug>.tech-refs.md`** with one H2 section per project. Within each section group paths under labelled sub-headings (e.g. **Routes**, **Controllers**, **CQRS commands**, **Domain & persistence**, **Message-bus events**) and list as bullets:
   ```
   - `relative/path/to/file-or-folder`: one-line description of its role in this feature
   ```
   Omit projects that have no relevant code.

6. **Report** the two absolute file paths that were written.

### Quality rules

- The `.md` spec must be understandable without any knowledge of the codebase: no class names, file paths, or framework jargon.
- Every path in `.tech-refs.md` must actually exist in the explored project; verify, do not guess.
- Keep both files focused on the named feature only; do not include loosely related features.

---

## Check

After Mode 3, run the spec checker over every generated spec folder: both files present, every cited path exists, and no code identifiers in the business spec. Run it before the specs PR, and keep the checker in the team repo so it survives the session that wrote it. In the reference implementation the checker lived in a scratch directory that was gone by the next cycle, and the three checks had to be done by hand. This check step is an addition from the reference implementation (17-onboarding.md section 5, the check step). See the `check-specs` skill.

---

## Findings file

Collect every inline note the writers left during Mode 3 into one findings file in the team repo: defects, dead or unreachable surface, design docs that sit behind the code, governance facts pinned from code. This is the audit the retro-generation produces for free, and in the reference implementation it became the entire ticket backlog for the first cycles. Cross out rows as cycles resolve them, recording the PR that did. This findings-file step is an addition from the reference implementation (17-onboarding.md section 5, the findings-file step).
