# Team Memory Plugin

Promote matured memspec claims from a personal or product-repo memory store up into a **team-context
repo's `memory/` store** through the one sanctioned write path: a PR-gated batch, reviewed by the team
lead or PM.

## Overview

A team-context repo (`*-team-context`, or the grandfathered `*-team-specs`) keeps a team memspec store
under `memory/`. Everyone reads it through memspec pointers; nobody writes it directly. Per the
team-context agreement (§3 row 4, §4), the only way a claim enters that store is a **batched promote
PR** that a human - team lead or PM - reviews and merges. Batched, because the review load has to stay
human-sized: one PR of N vetted claims is one standup-sized review, not N rubber-stamps.

This plugin's `promote` skill produces exactly that batch and that PR. It:

- **Locates the team-context repo** by walking `POINTERS.md`, then a repo `CLAUDE.md`'s
  `team-context:` key, then asking once - no guessing.
- **Gathers candidates** from the source store since the last promote, via the `memspec` CLI
  (`memspec export` / `memspec search`) and, when the CLI is absent, by reading the store's
  `memory/{facts,decisions,procedures}/ms_*.md` files directly.
- **Filters** to cross-repo, team-relevant facts/decisions/procedures - dropping session noise,
  secrets, personal data, repo-local claims, and anything already in the team store.
- **Drafts** one record per claim in the target store's existing format (it inspects a real record
  first, it does not assume the shape), plus a PR body from the template.
- **Shows the full batch and stops.** It creates a branch and opens the PR only after the user
  explicitly approves the shown batch, and never merges - the reviewer does.
- **Records the promote** (batch id, date, claim ids) in the source store so the next run's
  since-filter starts in the right place.

Where the plugin refuses: direct (non-PR) writes to a team store, per-claim PRs, promoting secrets or
personal data, and merging its own PR. Direct writes to a personal/repo store are ungated and out of
scope - just use `memspec_remember`. Regenerating `specs/` is the `spec-repos` plugin; graduating PM
workspace docs is `pm-workspace`'s graduate skill (shipping in pm-workspace 1.1.0).

## Usage

```
Promote my repo memspec facts into the team memory store
Batch-promote these decisions to the ticketing-system team-context repo
Run a team memory promote since the last batch
/team-memory:promote
```

The skill will resolve the target repo, show you the full batch (promoting / dropped / files / PR
plan), and wait. Nothing touches git until you approve the batch. The PR then goes to the team lead or
PM for review and merge.

The PR body template lives at [references/PROMOTE-PR-TEMPLATE.md](references/PROMOTE-PR-TEMPLATE.md):
a batch summary table plus the reviewer's four-point checklist (true? durable? no secrets/PII? belongs
at team level?).

## Maintainers

- PLG Platform team
