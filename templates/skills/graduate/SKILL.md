---
name: graduate
description: Promote a features/ file into a team-context repo, run the readiness gate, prepare the PR package. The human opens the PR.
---
<!-- Ported from the reference implementation's PM workspace, 2026-09-10. Generic names per docs/14-pm-surface.md; rename freely, but keep the description's firing conditions, because the description is what decides whether the skill fires. -->

# /graduate: the gate out of the swamp

Operate under the contract in `CLAUDE.md`, read it first if it isn't
already in context.

Input: a file in `features/` (or `discovery/`, in which case first check it
even qualifies for `features/`).

This is the ONLY path from this workspace into a team-context repo, and it
ends with a package for me to submit, never with you pushing anything
(CLAUDE.md R2).

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
3. Output the handoff: target repo, target path, suggested branch name, PR
   title + description, plus BOTH submission routes, my pick:
   - **git route:** the exact commands to branch, add, commit, push, open
     the PR.
   - **no-CLI route:** what to paste where in the hosting web UI
     (new branch → new file at target path → paste `.graduated.md` content
     → open PR), or "send the package to {{TEAM_LEAD}} to submit".

   Either way: I review, I submit. You never push.

## On fail

A short gap list: which gate, what's missing, what would close it. No
partial packages.
