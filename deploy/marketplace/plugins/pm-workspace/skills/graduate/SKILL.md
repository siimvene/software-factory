---
name: graduate
description: Use this skill when the user wants to promote a matured feature out of their PM workspace into a team repository - e.g. "graduate this feature", "prepare the PR for the payments team", "this spec is ready, package it for team-context", "promote Features/Localized Emails.md". Runs the readiness gate, checks the sensitivity gate in both directions, resolves the target repository via POINTERS.md, and prepares the pull request package. It never pushes or opens a PR without an explicit go-ahead, and after that go-ahead it opens the PR through the GitHub MCP server as the owner's own identity and merges it (context/spec repos auto-merge; adr 0011), with no local git or copy-paste. Do not use it to write or mature a feature - that is done in Discovery/ and Features/ by hand or with the `ingest` skill.
version: 1.1.0
---

# Graduate a feature into a team repository

Graduation is the single gate out of the workspace. A matured `Features/` document leaves the
personal PM workspace only as a **pull request into a team-context repository** (`*-team-specs` /
`*-team-context`, `*-context-repo`), and the go-ahead to graduate is the human decision: the agent
opens the PR only after an explicit go-ahead, and then merges it automatically, because a context
repo is agent-managed and unread and its PRs auto-merge (software-factory adr 0011). This skill runs
the readiness gate, prepares the package, and stops there unless the owner explicitly says to
graduate.

Reads out; the writes are the ones that open a pull request and, into a context repo, merge it. You
read the target repository to learn its spec format. After the owner's go-ahead you open a PR - three
writes onto a side branch (create the branch, commit the graduated file, open the PR) - and then
merge it, because the target is an agent-managed context/spec repo whose PRs auto-merge (adr 0011).
The owner reviews the package and gives the go-ahead to graduate; the merge follows automatically,
so the human decision is at graduation, not at the merge click. Human-owned merge stays the rule for
code repositories, which graduation never targets.

## Workspace layout and rules

Do not assume a layout. Locate the workspace root by walking up from the current working directory
until a `CONVENTIONS.md` containing a `Convention version:` line is found, then read that file. Section
15 (Graduation) and section 13 (POINTERS.md) of the conventions define the contract this skill
enforces; read the workspace copy, not the plugin's copy.

Read the workspace `CLAUDE.md` first - it is the canonical rule file. If the workspace still carries an
`AGENTS.md`, read it too as a legacy fallback, but scope what it wins: it takes precedence only for
personal preferences (language, tone, product context). In a workspace upgraded from v1, `AGENTS.md`
may be old plugin boilerplate describing the v1 layout; layout and routing always follow the
workspace `CONVENTIONS.md`, never a legacy `AGENTS.md`.

All paths handled here are relative to the workspace root, so the same instructions work on Windows,
macOS and Linux.

## Input

A file in `Features/`. If the user points at a `Discovery/` document, first check whether it even
qualifies for `Features/` (Scope and Requirements complete, `Status: Spec ready`); if it does not, say
what is missing and stop - it is not ready to graduate.

## Step 1 - Run the readiness gate

Every check must pass. A single failure stops graduation; report the gap and what would close it.

1. **Code-grounded (R1).** Every claim about current system behaviour cites a repo + path from
   `POINTERS.md`. Any claim that cannot be grounded is marked **unverified** and listed. An unmarked
   unverified claim fails the gate.
2. **Decisions closed.** No open decisions or blockers remain in the file. Open items send it back to
   `Discovery/` with a short list of what needs closing.
3. **Scope traced.** If the feature is part of a larger scope (a migration or a program), the parent
   scope maps this item, with no uncovered or undecided flags on it.
4. **Sensitivity, both directions (SENSITIVITY.md, section 14).** Nothing in the package exceeds what
   the target team-context repository may hold - it becomes team-visible, and the workspace is not.
   This runs outbound (what leaves the workspace) and inbound (no verbatim sensitive passages carried
   along); check `SENSITIVITY.md` and its per-folder overrides before packaging.

Tickets and specs describe **what**, not **how**: acceptance criteria state observable outcomes, and
there are no proposed-technical-approach sections. The developers own the implementation.

Reported with the gate result, never a gate failure: when the feature's own text shows any of the
ticket skill's bigger-ticket triggers (money moved, charged, refunded or shown as an amount people pay
on; login, identity, permissions or customer isolation; something new stored; another consumer such
as a mobile app, another system or an external API; an existing feature or path removed; more than
one existing feature spec touched), the build side will write a short design
from this file before any code, and it needs four things the file may not carry: what must never
break and how we would know (plus any speed or volume limit and the bad-input case); the exact names,
amounts, messages and fields the user sees, with the agreed prototype for anything with a screen;
what must exist or ship first; who does each thing, on which screen or through which user action
(never which endpoint or service). List whichever of the four the file
does not answer as "the build will ask for: ...". The owner decides whether to close them now or let
the ticket skill ask at drafting time.

## Step 2 - Resolve the target and rewrite into its format

- Resolve the target team-context repository from `POINTERS.md` (the `*-team-specs` / `*-team-context`
  entry). If more than one could fit, ask which team once; do not guess.
- Read the target repository's spec directory and conventions (typically `specs/`; confirm from the
  repo itself or the notes in `POINTERS.md`) through its `POINTERS.md` entry and rewrite the feature
  into the target repo's spec format. Read it live; do not copy stale content in.
- Write the rewritten result to `Features/<name>.graduated.md` in **this** workspace. That file is the
  package; it stays here even after the PR is opened.
- Read the target path on the repository's default branch to determine whether this graduation
  **creates** a new spec file or **updates** an existing one. Carry that answer into the confirmation
  so the owner sees which it is before approving.

## Step 3 - Show the full package and destination, then wait

The go-ahead you ask for authorizes opening the PR **and merging it** - the target is a context repo,
which auto-merges (adr 0011), so approval lands the change in the team layer. Say this in the ask.

Present, and stop for an explicit go-ahead:

```
## Graduation: <Feature Name>

**Gate:** all checks passed  (list any unverified-but-marked claims)
**Target repo:** <name>  (from POINTERS.md)
**Target path:** <spec dir>/<...>.md   (spec dir as resolved in step 2)
**Action:** create new spec  |  update existing spec at that path
**Branch:** <suggested branch name>
**PR title:** <title>
**PR description:** <summary>

### Package (Features/<name>.graduated.md)
<the full rewritten spec>
```

Write nothing to the target repository yet. This is the confirmation gate; the owner reviews the whole
package and its destination before anything moves.

## Step 4 - Open the PR via the GitHub MCP server, after the go-ahead

Once the owner explicitly confirms, open the pull request through the **GitHub MCP server**, acting as
the owner's own GitHub identity. This is the only route: no local git, no copy-paste, no web-UI
hand-off. It runs identically on every machine (Cowork, Windows, macOS), whether or not the repo is
cloned. Never open the PR before the go-ahead, and never touch a `POINTERS.md` repo outside this flow
(R2).

This skill depends on the GitHub MCP server connector being present and authenticated. Do the steps in
order; if any check or write fails, stop and follow "If a write fails" below.

1. **Confirm the connector.** Verify the GitHub MCP server is available and identify who it acts as
   (`get_me`). Missing or unauthenticated → stop; this is the same honest stop as a denied write, not
   a reason to fall back to anything.
2. **Don't duplicate an open PR.** Check for an already-open PR from this graduation's head branch into
   the target's default branch. If one exists, report its URL and stop - never open a second.
3. **Resolve the base branch.** Read the target repository's default branch (it may not be `main`); the
   feature branch and the PR both target it.
4. **Get a branch you can account for.** Prefer the branch name in the package, created off the default
   branch. If a branch by that name already exists, reuse it **only** when it is provably this same
   graduation and nothing else: exactly one commit ahead of the default branch, touching only the one
   target path. Anything else - extra commits, other files, unknown history - means create a new
   branch under a distinct name. Never build on top of a branch you cannot fully account for.
5. **Re-run the sensitivity gate on the real outbound bytes.** The step 1 check ran on the source
   feature; now re-check the material actually leaving the workspace - the rewritten
   `Features/<name>.graduated.md` content, the PR title, and the PR description - against
   `SENSITIVITY.md` and its overrides. If anything now exceeds what the target may hold, stop; nothing
   is written.
6. **Commit exactly one file.** Commit the graduated spec to the target path as a single commit that
   touches only that one path:
   - the path does not exist in the repo → create it;
   - it already exists → fetch its current blob SHA **on the feature branch** and update against that
     SHA; never blind-overwrite.
7. **Verify, then open the PR.** Immediately before opening, confirm the branch is still exactly one
   commit ahead of the default branch and touches only the target path. Then open the PR from the
   branch into the default branch with the package's title and description, and report the PR URL.

You open the PR and, into a context repo, merge it - the go-ahead to graduate was the human
decision, and the merge is a mechanical consequence for a layer no human reviews (adr 0011). Guard
before merging: confirm the target matches the `*-team-specs` / `*-team-context` / `*-context-repo`
shape (never auto-merge a code repo) and pin the merge to the head SHA you just verified. Human-owned
merge stays the rule for code repositories.

**If a write fails** - a denied push (no write access, or a read-only MCP grant), or a failure partway
through - stop and say plainly what happened: which operation failed, and exactly what already landed
(branch created? commit SHA? PR opened?). Do not auto-clean-up, do not fall back to copy-paste, do not
invent or guess a PR URL, and do not pretend a PR was opened. A permission gap is fixed at the
permission layer; a partial write is left as-is for a human to inspect.

## On gate failure

A short gap list: which check failed, what is missing, and what would close it. No partial packages,
and nothing written to any target repository.
