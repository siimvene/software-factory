<!--
  CYCLE REPORT. Written at the end of every dogfood cycle by whoever ran it, while the
  timestamps are still recoverable. It is the measurement instrument for the loop itself:
  the product outcome is in the PR, this file is about how the line behaved.
  One file per cycle, named with the cycle number and the date.
-->

# Cycle <n> report, <YYYY-MM-DD>

- Ticket: `<path or id of the approved ticket>`
- Code PR: `<repo>#<n>` (`<short sha>`, branch `<branch>`)
- Sister spec PR: `<context repo>#<n>` (branch `<branch>`)
- Merge authority: <role>. Agents open PRs; they never merge their own.

## Wall-clock per stage

<!-- Fill start and end from real timestamps, not from memory. Elapsed is computed, not
     estimated. The two bold totals are the numbers that get compared across cycles;
     everything above them explains where the time went. Idle waiting on a human is
     recorded on its own row and excluded from the totals, so process time and queue time
     never get confused. -->

| Stage | Start | End | Elapsed | Notes |
|---|---|---|---|---|
| SPEC: investigate the candidate against code and production | | | | |
| SPEC: draft the ticket, self-score readiness | | | | <n>/100 |
| BUILD: worktree and dependency install | | | | |
| BUILD: failing test written first, confirmed red | | | | |
| BUILD: implementation, unit tests green, lint | | | | |
| BUILD: end-to-end fence, stack boot, pass | | | | |
| BUILD: negative run (fix reverted, the fence must fail) | | | | |
| VERIFY: scanner tier (secrets, dependencies, static analysis) | | | | |
| VERIFY: cross-vendor review | | | | <k> findings, reachability probe first |
| VERIFY: blind security side-pass | | | | |
| VERIFY: browser QA | | | | |
| VERIFY: fix pass for review findings | | | | |
| Commit, push, code PR open | | | | |
| Sister spec PR open | | | | |
| **Dev hat on to code PR open** | | | **<mm:ss>** | review is <n>% of it |
| (idle: waiting on the owner) | | | | not counted in the totals |
| SHIP: owner merges, worktree cleanup | | | | |
| SHIP: pre-deploy gate on merged main | | | | |
| SHIP: deploy | | | | |
| SHIP: production probe | | | | |
| **Dev hat on to live, excluding idle** | | | **<mm:ss>** | |

## Tokens per agent

| Agent | Role | Tokens | Tool calls |
|---|---|---|---|
| principal session | build and orchestration | <n, or "not instrumented"> | |
| <lane agent> | <lane> | | |
| security side-agent | blind security pass | | |
| cross-vendor reviewer | independent review | <n, or "not reported by the vendor"> | |

<!-- Record "not instrumented" rather than guessing. A missing counter is a finding about
     the harness, and it is the cheapest one to fix. -->

## What the gate caught

<!-- The point of the exercise. For each finding: which gate found it, whether tests and
     lint had already passed, whether it was verified against the code, and what was done.
     A cycle where the gates caught nothing is worth recording too: it is evidence about
     the risk of the change, not proof that the gates work. -->

- <gate>: <finding>, <CRITICAL|SERIOUS|MINOR>, verified <yes|no>, <fixed in commit <sha> |
  deferred with owner <role>>.

## Skipped or shortcut steps

<!-- Each entry is a finding about the process, not about the product. Write them even
     when they are embarrassing, especially then: the list is the backlog for the next
     turn of the loop. Name the cost the shortcut carried. -->

1. <what was skipped> Cost: <what it bought and what it risked>.
2. <...>

## Candidate next ticket

<One paragraph: the next thing this cycle surfaced, what still has to be decided before it
becomes a ticket, and which role owns that decision.>
