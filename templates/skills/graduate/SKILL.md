---
name: graduate
description: Promote a features/ file into a team-context repo, run the readiness gate, open the PR into it and merge it - context repos auto-merge (adr 0011); the go-ahead to graduate is the human decision.
---
<!-- Ported from the reference implementation's PM workspace, 2026-09-10. Generic names per docs/14-pm-surface.md; rename freely, but keep the description's firing conditions, because the description is what decides whether the skill fires. -->

# /graduate: the gate out of the swamp

Operate under the contract in `CLAUDE.md`, read it first if it isn't
already in context.

Input: a file in `features/` (or `discovery/`, in which case first check it
even qualifies for `features/`).

This is the ONLY path from this workspace into a team-context repo. After
the go-ahead to graduate you open the PR into it AND merge it, because a
context repo is agent-managed and unread and its PRs auto-merge (adr 0011).
The human decision is the go-ahead, not the merge (CLAUDE.md R2). Code repos
are never a graduation target and keep human-owned merge.

## Gate checks: all must pass

1. **Code-grounded (R1)**: every claim about current system behavior cites
   repo + path from `POINTERS.md`. Unverified claims are marked as such and
   listed; any unmarked unverified claim fails the gate.
2. **Decisions closed**: no open decisions or blockers in the file. Open
   items go back to `discovery/` with a list of what needs closing.
3. **Scope traced (R4)**: if the feature is part of a larger scope
   (migration, program), the parent scope file maps this item; no ⚠️/❓ flags
   on it.
4. **Estimate rule (R3)**: if the file carries an estimate, base +
   contingency + justification present.
5. **Ticket hygiene (R6)**: describes what, not how; acceptance criteria
   are observable outcomes.
6. **Sensitivity (R5)**: nothing in the file exceeds what the target
   team-context repo may contain (it's team-visible; this workspace is not).

## On pass

1. Rewrite the file into the target team-context repo's spec format (read
   its `specs/` conventions via `POINTERS.md`).
2. Write the result to `features/{name}.graduated.md` in THIS repo.
3. Show the full package and destination and stop for an explicit go-ahead
   to graduate (that approval also merges - say so).
4. On the go-ahead, open the PR through the team's git host as the owner's
   identity (branch, one commit of the graduated file, PR to the default
   branch), then merge it - the target context repo auto-merges (adr 0011).
   Guard: confirm the target is the context repo from `POINTERS.md` (never a
   code repo) and pin the merge to the verified head SHA. If a write or the
   merge is denied, stop and report the gap - never paste by hand.

## On fail

A short gap list: which gate, what's missing, what would close it. No
partial packages.
