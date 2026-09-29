# 0013. Merge serialization is the substrate for delegated merge

- Status: proposed
- Date: 2026-09-29
- Deciders: the operator

## Context

A green check result is valid only on the base it ran on. With a non-strict ruleset, a PR that
went green before another PR merged can still merge, and the combined tree is tested for the
first time on main. On 2026-09-29 that turned kvart's main red within 20 minutes of a
five-PR merge run, and a third PR's CI failed on breaks that were not its own `[measured
2026-09-29]` ([evidence](../evidence/kvart-stale-green-merges-2026-09-29.md)).

A strict ruleset (the PR must be up to date with main) closes that gap, at a cost: every merge
puts every other open PR behind, and someone has to update each branch and wait for its CI
again. A forge merge queue does that bookkeeping, but kvart's forge account has none. Without
one, strict means a person runs the queue by hand: update, wait about 20 to 25 minutes of CI,
merge, next.

Separately, ADR 0006 leaves a path to delegated merge for narrowly qualified classes of change,
under the bot identity's own name. That needs a component that decides when a PR merges.
The queue already is that component.

## Decision

We will build one merge serializer, in two layers, and turn the strict ruleset back on when
layer 1 runs.

- **Layer 1, serializer only.** A poller next to the existing tracker-sync poller picks the
  oldest open PR that has the forge's auto-merge enabled and is behind main, updates its
  branch, and waits for its checks. One PR at a time. It never merges: the forge's auto-merge
  does, credited to whoever enabled it. Enabling auto-merge is the human merge decision
  ADR 0006 requires, and the forge records it as such. The serializer only makes that
  decision cheap to act on under strict.
- **Layer 2, delegated merge.** The same poller, running as the bot identity, enables
  auto-merge itself for PRs in a qualified class (candidates: tests-only, locale-only, a
  loop-infrastructure PR after green, per ADR 0006). The class list, its expiry and its
  revocation live in the poller's configuration, reviewed like code. Each class carries its
  record: merges under it, reverts, escaped defects. Any escaped defect suspends the class.

Scope: one serializer per repository. Layer 2 does not start before layer 1 has run for the
promotion window in `docs/11-scaling.md`.

## Consequences

- Positive: no merge lands on a base its checks did not see. Checkable: the count of main
  going red after a merge of a green PR (target 0, from the merge log and main's full-suite
  results). Layer 2 then needs no new plumbing, only a class list.
- Cost: merges become serial. At about 20 to 25 minutes of PR CI each, throughput is about 3
  merges an hour per repository, before any CI speed-up. Every queued PR re-runs its CI on
  every base change, so CI minutes rise with queue depth. A PR that goes red after an update
  leaves the queue, and its author gets the failure on the new base.
- Follow-ups: the poller (operator); strict ruleset on (owner, after layer 1 is live); the
  fence list in PR CI (`docs/06-verify-gate.md`), which is independent of this decision and
  cheaper; the first qualified class for layer 2 (owner, after the window).

## Alternatives rejected

- Non-strict plus the post-merge full suite and automatic revert: finds the break after main
  is red for everyone who branched in between. Measured on 2026-09-29.
- Non-strict plus a re-check by the merger on a local merge with current main: works when done,
  and was done for the last three PRs that day; a hand step the merger can skip, which is how
  the first break landed.
- Strict with branches updated by hand: correct, and turns the owner into the queue.
- A forge merge queue: the right tool where available; not available on this forge account.
  The serializer is replaced by it where it exists; layer 2's class list moves to whatever
  enables auto-merge.
- Letting the serializer merge (layer 1 merging directly): removes the record that a human
  decided, the failure ADR 0006's incident names.

## Evidence

- `evidence/kvart-stale-green-merges-2026-09-29.md`.
- ADR 0006, delegated merge and the 2026-09-09 incident.
