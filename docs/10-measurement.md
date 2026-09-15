# Measurement

What to measure, what to baseline before agents dominate, what the reference implementation
measured, and the bar for "it paid off". A software factory without these numbers is a story.

## The four numbers per turn

Every cycle report carries them. See [templates/dogfood-cycle-report.md](../templates/dogfood-cycle-report.md).

1. **Wall-clock per stage.** Start, end, elapsed for every stage from "pick ticket" to "live
   in prod", idle waits on humans separated out.
2. **Tokens per agent.** Subagents report their own; the principal session is not
   instrumented by default. A Stop-hook counter is the mechanical upgrade if the number matters.
3. **What the gate caught.** Every finding with class, whether it was verified real, and what
   it changed in the diff.
4. **Skipped or shortcut steps.** Each one is a finding about the process, not the product.

Measured on kvart, cycles 1 and 2 `[measured 2026-09-07]`:

| Stage | Cycle 1 (route fix, +47/−1) | Cycle 2 (retire a payment path, +121/−679) |
|---|---|---|
| PM: investigate, decide, draft, score | ~11 min | ~29 min (premise corrected; owner decision inside) |
| Dev: worktree + deps | ~1 min | ~2 min |
| Dev: tests first, red, fix, green | ~1 min | ~3 min (two lanes in parallel) |
| Dev: browser spec, negative run | ~4 min | 19 s |
| Gate: scanners | <1 min | ~1 min |
| Gate: cross-vendor review | 7 min 06 s (0 findings) | 9 min 48 s (1 HIGH, 1 MEDIUM, 1 LOW) |
| Gate: blind security side-pass | 2 min 53 s (0) | 3 min 25 s (2 LOW, 1 INFO) |
| QA: browser pass | ~4 min, 10 surfaces | ~3 min, 7 surfaces |
| Fix passes from findings | none | ~7 min, 2 commits |
| **Dev hat on → code PR open** | **12 min 11 s** | **18 min 58 s** |
| Sister spec PR | 1 min 33 s | <1 min |
| Owner merge + cleanup | ~4 min | ~2 min (after a 5 h 25 min idle wait) |
| Pre-deploy gate | 16 s | 17 s |
| Deploy | 39 s | 52 s |
| Prod probe | <1 min | ~4 min |
| **Dev hat on → live, excluding idle** | **~28 min** | **~27 min** |

Tokens: security side-agent 113,435 and 110,339; frontend lane agent 89,774. Hands tokens in
the trial ≈ 314k across 5 calls `[measured 2026-09-05]`.

Reading: the cross-vendor review is the largest block (52 to 58 %); review-driven fix passes
were 37 % of cycle 2. Humans are the long pole only when they are away (the 5 h wait), not when
they are reading evidence (2 to 4 minutes to merge).

## Cost per feature

Outcome-denominated cost (per merged PR, per feature, per review) replaces per-token spend as
the primary metric once agents author most PRs `[field: Uber Engineering]`. Under a
subscription model, cost per feature = subscription ÷ features delivered.

Measured on kvart, 2026-08-08 to 09-07, list-price equivalents `[measured 2026-09-07]`:

| Unit | Number |
|---|---|
| kvart sessions in the window | 217, $9,414 |
| session cost | median $18.7, p75 $41, p90 $117, max $416 |
| orchestrator-tree burn (sessions ≥ 30 min) | median $14/h, p75 $30/h, p90 $57/h |
| feature groups (feat commits sharing scope and day) | 98 |
| **all-in cost per feature** (fixes, docs, review loops, tests included) | **≈ $96** |
| the feature session itself | ≈ $20 to 40 |
| cost per commit | ≈ $10 |
| share of added lines that are tests | 37 % |
| cache reads as share of tokens | 96 % (the standing context is the cost driver) |

Operator-level, same window, ~30 repos: ~3,500 commits, ~+820k/−150k lines, ~$19.4k list price.
Roughly the monthly output of a 15 to 25 person engineering organisation, at a cost per unit of
shipped code on the order of 50 to 100× below hiring. Caveats that keep it from being a vanity
number: test share; the gate catching about half of fixes before they escape; cadence is bursty;
the top model tier is half the spend and it is unproven that all of it was hard-tier work.

An earlier estimate of $200 to 500 per slice was 2 to 5× too high; the corrected unit is an
orchestrator tree, not a bare agent.

## The headline ratio

```
accepted outputs
----------------
human review minutes
```

This ratio captures what the factory is supposed to do: convert model capability into useful,
reviewable work without consuming equal human attention on the way out. It is the single number
to report upward: it compresses cost (denominator) and quality (numerator) into one signal
`[field: Ichigo, "Harness Engineering", 2026-08-29]`.

Numerator: merged PRs where a human said yes (not reverted, not bounced from gate). Denominator:
wall-clock minutes a person spent reading, deciding, and merging, idle wait excluded. A factory
that produces 20 PRs in an afternoon of human attention and a factory that produces 5 PRs after a
week of back-and-forth have the same accepted-output count; the ratio tells them apart.

Track it alongside the four per-turn numbers. The per-turn numbers diagnose; the ratio is the
mandate signal.

## Baselines that must exist before agents dominate

Once agents author most PRs the comparison point is gone. Take these on human-written code
now `[field: Uber Engineering; designed]`:

- **Revert rate** per 100 merged PRs.
- **Defect escape rate** per merged PR (bugs reaching production).
- **Lead time** request → prod.
- **Reviewer F1**: a benchmark set of real PRs with known bugs; precision (flagged that are
  real), recall (real that were caught), cost per catch. Run whatever is Pareto-optimal on
  quality and cost; re-benchmark as models change. Model choice becomes a data problem.
- **Recommendation acceptance rate**: did the developer act on the review comment (commit) or
  dismiss it. A 200-engineer shop measures ~70 % and uses it as the benchmark for every model
  or harness change `[field: Pipedrive]`.

Quality debt compounds faster than it is visible: a characterization net preserves known bugs,
contradictory specs get implemented faithfully, and without a revert-rate baseline nobody sees
the regression until customers do.

## Rework after the first review

Whether design before the build pays is a measurable question. Two numbers per PR: review rounds,
and the post-review rework share, lines touched by fix passes after the first review divided by
lines in the merged diff. Cycle 2: one fix pass of 2 commits, 37 % of dev-hat wall-clock
`[measured 2026-09-07]`; the trial: 2 review rounds, 1 of 4 hands rounds spent on a redesign
`[measured 2026-09-05]`. The bar for the program design note ([02-loop](02-loop.md)): on sized
tickets the rework share falls and the review share of wall-clock with it. If neither moves over
the first five sized tickets, the note is overhead and the sizing rule is wrong `[proposed]`.
Idle waits and CI reruns are excluded, as everywhere.

## The honest fix:feat ratio

Raw fix:feat lies in a review-gated repo: about half of fix commits are the review apparatus
succeeding. Re-cut on non-review fixes (subject and body not matching review, audit, panel,
finding, scanner, QA keywords). kvart, four weeks `[measured 2026-09-07]`:

| Week of | commits | raw fix:feat | non-review fix:feat | $/commit |
|---|---|---|---|---|
| Aug 10 | 261 | 1.83 | 0.79 | 8.4 |
| Aug 17 | 71 | 0.69 | 0.31 | 17.5 |
| Aug 24 | 114 | 3.24 | 1.24 | 19.2 |
| Aug 31 | 209 | 5.69 | 2.50 | 11.2 |

Non-review fixes rose three weeks straight while features fell, and cost per commit stayed
flat. Two indistinguishable readings from commit labels alone: better detection surfacing old
debt (the ratio should crash once the backlog clears), or the toolset generating its own
rework. In a deliberate pre-launch hardening phase fix > feat is the intended shape, so the bar
there is the weekly non-review fix count peaking and turning down (a finite backlog being
drained). It was still rising (8 → 21 → 40).

## The factory-on-itself share

The share of merges that are the line fixing its own machinery, not shipping product:
loop-infrastructure merges divided by all merges, cut weekly. It is the number that says
whether the line has settled or is still being built.

kvart, 2026-09-09 `[measured 2026-09-09]`: 8 of 13 merges were loop infrastructure. Loop:
runner routing (#31, #32), coverage floor and concurrency (#34), Jira ledger (#39, #40), test
selection and merge base (#41), browser gate (#42, #44). Product: #30, #33, #36, #37, #38.

Proposed settle threshold: the share below one in five for two consecutive weeks `[proposed]`.
A line that spends most of its merges on itself is still under construction; when the machinery
holds, the merges go back to being product.

## The payoff bar

"Methods maturing" is a plan until a measurement lands. Agreed bar for the reference
implementation `[measured 2026-09-07, re-measure at check-by]`:

- a week with non-review fix:feat < 1 (after the hardening phase is declared over), and
- cost per commit < $8 list price.

Secondary check: audit top-tier model usage per project for a week; if half is mechanical, the
routing rule is not being obeyed (≈ $4k/month waste at list price). The audit reads the served
model, not the requested alias: an alias that resolves to the wrong tier in one config
directory routes silently, so a per-alias count would report clean while the served count shows
the leak (2026-09-08, about 11,000 calls on the wrong tier since 2026-08-13).

## Instruments, one per constraint

| Constraint | Instrument |
|---|---|
| wall-clock | `time`, the tool's timeout, the cycle report's stage table |
| spend | the usage CLI per config dir (dedupe by message id; per-account split is not recoverable when session files are mirrored), provider consoles, a daily threshold |
| surface | `git status`, `git diff --stat`, the scope-spillover check, read-only mounts |
| merge conflicts per stream | dry-run merges per stream |
| design quality | review rounds per PR; post-review rework share of the merged diff |
| net strength | mutation kill rate per module as killed over all mutants (killed over checked hides the unexercised ones), money-surface coverage |
| parity | replay pass rate per flow |
| review quality | F1 on the benchmark set |
| escape | revert rate and prod defect count vs baseline |

If a constraint has no instrument, it is not a constraint.

## What "took off" would look like

Agent PR share above 70 %, cost per merged feature falling, revert rate flat against the human
baseline, defect escape flat, lead time falling, and (for a group) platforms retired. Baselines
first or the comparison is lost forever.
