# The loop

SPEC → BUILD → VERIFY → SHIP → LEARN. One turn per ticket. The loop is the standard shape of
an agentic SDLC; what this design adds is where the gates sit, who decides what, and the two
write-backs that make it a flywheel.

```
   ┌──────────────────────────────────────────────────────────────────────────┐
   │                                                                          │
   ▼                                                                          │
 SPEC ──► BUILD ──► VERIFY ──► SHIP ──► LEARN ─────────────────────────────────┘
 ticket   sandbox   sensors    PR      specs regenerated (sister PR)
 examples worktree  consort    owner   memory promoted (promote PR)
 approve  agents    security   merge   report: wall-clock, tokens, shortcuts
          plan      scanners   release
          first     QA
```

## SPEC

**Input:** a finding, a request, a backlog row.
**Output:** a ticket with numbered observable examples, approved by a person.

- The ticket is the delta, nothing else. Current state lives in the specs; the ticket says
  what changes. See [templates/ticket.md](../templates/ticket.md).
- Numbered examples (starting state, action, expected observable outcome) are the acceptance
  contract. They are written before any code and referenced by number from the plan, the
  tests and the evidence. See [07-roles-and-authority](07-roles-and-authority.md) for why
  builder-authored criteria are not acceptance.
- Readiness is scored against a rubric before the ticket moves to Ready. The kvart cycles
  self-scored 94 and 93 of 100 `[measured 2026-09-07]`; a team uses an evaluator agent and the
  PM's approval.
- Security is considered here, not only pre-merge: a short design-vs-checklist pass on the
  ticket (data touched, actors, trust boundaries). Advisory until a checker exists.
- Unresolved business rules get a named owner in the ticket. A ticket with an open decision
  is not Ready.

Where the PM investigation corrected the premise: cycle 2 started as "fix a misleading label"
and became "retire a payment path" after 20 minutes of reading code, the production database
and the audit trail `[measured 2026-09-07]`. The SPEC stage is where that reading belongs.

## BUILD

**Input:** a Ready ticket.
**Output:** a branch with the change, its tests and a plan that maps to the examples.

- Isolation first: a worktree (or a real clone where a sandbox requires it) per turn. No git
  mutation in a shared checkout. See [08-sandbox-and-isolation](08-sandbox-and-isolation.md).
- Orientation before writing: the codebase map (sensor layer 1), the specs, the decision
  records, the memory store. Do not open files you have not located.
- Plan mode first for anything non-trivial: a 2 to 6 step plan with a model tier per step and
  a verify step per step. Adversarial questions before implementing: what fails, which edge
  case breaks it, can state be left inconsistent, which assumption might be wrong.
- Tests first, red on the unfixed code. Cycle 1: the unit case failed on the unfixed
  middleware with the exact wrong redirect, then passed after a one-line fix; the browser
  spec was proven to fail with the fix reverted `[measured 2026-09-07]`.
- Parallel lanes on disjoint file ownership. Cycle 2 ran the backend lane in the principal
  session and the frontend lane in a subagent on disjoint files; the subagent returned 20
  green unit tests in 118 s `[measured 2026-09-07]`.
- Every subagent gets a five-part brief and a wall-clock cap. See
  [templates/delegation-brief.md](../templates/delegation-brief.md).

## VERIFY

**Input:** the branch.
**Output:** a gate report with every gate's result and every finding's disposition.

Order matters and is the subject of two documents:

1. Mechanical sensors, in the agent's own loop: quality ratchets, architecture diff, changed-line
   coverage, format, lint, types, unit and integration tests. See
   [05-sensor-stack](05-sensor-stack.md).
2. Inferential review, before any push: the cross-vendor reviewer on the cumulative diff, the
   blind security side-pass, the scanner tier (secrets, dependency CVEs, static analysis), the
   browser QA pass on every UI surface the diff touches. See
   [06-verify-gate](06-verify-gate.md).

Findings are classified (CRITICAL, SERIOUS, MINOR), spot-verified against code, and given a
disposition (ACCEPT-FIX, ACCEPT-DEFER, ACKNOWLEDGE, DISMISS). CRITICAL and SERIOUS are fixed
before push. Bootstrap failures (a ratchet red on pre-existing code) are reported separately
from feature failures and never "fixed" by editing a baseline.

## SHIP

**Input:** a gate-clean branch.
**Output:** a merged PR and a release.

- The PR arrives already reviewed. CI is mechanical (lint, tests, version, docs-lint) and does
  not duplicate the consort review.
- The owner merges. Agents propose; humans merge. Never push to a default branch, never
  merge your own proposal, never approve a PR.
- Provenance: every commit carries an agent attribution trailer and a session link. See
  [07-roles-and-authority](07-roles-and-authority.md).
- Money, tenant, identity and migration changes require named-human outcome sign-off, always.
  Low-risk surfaces may auto-accept on green once the promotion criteria in
  [11-scaling](11-scaling.md) hold.
- Release is a separate authority from merge. Pre-deploy gate (smoke plus the changed-surface
  spec) on merged main, then deploy, then a probe of the changed behaviour in production.
  Cycle 1: 16 s pre-deploy gate, 39 s deploy, anonymous probe of the changed route
  `[measured 2026-09-07]`.

## LEARN

**Input:** a merged change.
**Output:** the two write-backs and the dogfood report.

1. **Specs.** A behaviour-changing PR is incomplete until its sister spec delta is staged in
   the team-context repo. Specs are derived from merged code, never hand-edited. Pure
   refactors need none, and say so.
2. **Memory.** Facts, decisions and procedures discovered during the turn are written at the
   moment of discovery into local scratch, and promoted to the team store by a batched,
   human-reviewed PR. Anchored claims the diff invalidated are superseded in the same turn.
3. **Report.** Wall-clock per stage, tokens per agent, what the gate caught, every skipped or
   shortcut step and why. See [templates/dogfood-cycle-report.md](../templates/dogfood-cycle-report.md).

The write-backs are what make turn N+1 cheaper: the next ticket is written against current
specs, the next agent starts from current memory, and the next proposal to the organisation
is written from measured shortcuts rather than from opinion.

## Supervision levels

The loop runs at one of three levels per turn, chosen at SPEC:

| Level | Where the agent runs | Human touchpoints |
|---|---|---|
| Autonomous (default) | sandbox, scoped identity | ticket approval, merge, release |
| Interactive | operator's machine, worktree | plus checkpoint before implementation |
| Hands-on | operator drives step by step | every step |

Autonomy is only available inside the sandbox. A turn that needs a change outside its brief
stops; it does not improvise.

## What one turn costs

| Turn | Diff | Dev hat on to PR open | Of which cross-vendor review | To live in prod |
|---|---|---|---|---|
| cycle 1, public-route fix | +47 / −1 | 12 min 11 s | 7 min 06 s | ~28 min incl. human merge |
| cycle 2, retire a payment path | +121 / −679 | 18 min 58 s | 9 min 48 s | ~27 min excl. a 5 h owner wait |
| trial, stream an export | +112 / −11 | (3 h run, 24 min real work) | 2 review rounds | not merged by design |

All `[measured 2026-09-05..07]`. Details in the [case studies](../case-studies/).
