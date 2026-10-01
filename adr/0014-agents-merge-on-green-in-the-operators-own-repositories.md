# 0014. Agents merge on green in the operator's own repositories

- **Status:** rejected (withdrawn 2026-10-01, the day after it was merged)
- **Date:** 2026-09-30
- **Withdrawn because:** merge on green is the operator's local working practice for the operator's own
  repositories, not a decision of the reference design. At the reference level the owner merges
  ([0006](0006-pr-gated-output-human-release.md) stands in full, and 0005's merge half with it).
  This record is kept, as every record is, so the reasoning stays readable; nothing below is in
  force in the design.
- **Deciders:** the operator
- **Qualifies:** 0005 (humans approve and merge), 0006 (merge is a human decision; the loop
  does not merge), 0011 (auto-merge for context repos)

## Context

0006 kept the merge with a person, and its 2026-09-09 incident added "the loop does not merge"
plus a weekly check that counts merges by the owner's identity from an agent session, target 0.
In the reference implementation that person is the operator, who holds every role. The merge
click was measured as a wait, not as a reading:

- cycle 2: the owner merge took about 2 minutes, after a 5 h 25 min idle wait for it
  `[measured 2026-09-07]`;
- cycle 4: about 2 h of the 4 h 57 min from pickup to live were three merge waits and one CI
  round `[measured 2026-09-09]`.

The evidence the owner was supposed to read before merging already exists before the PR does:
the consort panel runs before the push (0003), the required checks run on the PR, and the
ruleset refuses a merge while any of them is red. When the owner merges on green without
adding a reading, the merge is the same etiquette 0011 removed for the context layer.

## Decision

In the operator's own repositories (the reference implementation's code and context repos), an
agent that opens a PR arms the forge's auto-merge right after opening it
(`gh pr merge <n> --auto --merge`), where the repository has required checks. The forge merges
when every required check is green and holds on red. No PR waits for a person to say "merge".

Where the repository has no required checks, the agent does not arm: `--auto` on a PR that is
already mergeable merges it at once, before CI has started (the forge client's own help: auto-
merge is enabled only "if required checks have not yet passed"). There the watcher below is the
only merge path. Where a PR has no checks at all, nothing can be green, and merge on green does
not apply: the merge is the owner's.

Rules that do not change:

- The consort panel and the security side-pass run before any push of code (0003).
- Never bypass or override a red check, never use an admin merge, never merge a PR whose
  checks did not run, never merge a head the checks did not see.
- A handoff still never instructs a merge: the PR is armed when it is opened, so there is
  nothing left to instruct.
- Production release stays a human authority (0006). The named-human outcome sign-off on
  money, tenant, identity and migration changes moves from the merge to the release.

Scope: repositories the operator owns outright. An organisation's repositories keep 0006 and
the managed contract's "never merge your own proposal" until the organisation decides
otherwise for itself.

## Mechanism

- **The ruleset is the merge gate.** Required checks plus an empty bypass list make "never
  merge red" and "never admin-merge" mechanical: the forge refuses both for the owner and for
  the bot `[measured 2026-09-08]`.
- **Watcher fallback.** Armed auto-merge did not fire on kvart #333 and #356 with every check
  green and the merge state `CLEAN` `[measured 2026-09-30]`. Cause not investigated; the
  candidate is a status posted by the out-of-forge poller that does not re-trigger the forge's
  evaluation. So arming is paired with a capped watcher: it records the head commit, polls
  that head's checks, stops and reports on any red, and once nothing is pending and the PR is
  still open a couple of minutes later merges directly with
  `gh pr merge <n> --merge --match-head-commit <sha>`. A new push changes the head, the merge
  is refused, and the watcher starts over on the new head. Where a repository has no required
  checks, the watcher is the only path, and the head pin is what stops a push that landed after
  the green from merging unchecked.
- **The ledger.** The forge records the arming identity, which is the owner's login. In these
  repositories a merge by the owner's identity no longer claims that a person read the PR: the
  standing order is the human decision, and this record is where it is written down. 0006's
  weekly identity check is retired here; its replacement counts merges whose required checks
  were not all green at merge time, target 0.

## Consequences

- **Positive:** the merge wait leaves the critical path. Checkable: pickup to live on the next
  cycles against cycle 4's 4 h 57 min, with merge wait reported as its own row.
- **Cost:** a merge is only as good as the base its green ran on. Two green PRs turned kvart's
  main red within 20 minutes on 2026-09-29, one through a stale base and one through impact
  selection skipping a repo-wide fence `[measured 2026-09-29]`. With no person in front of
  the merge, nobody re-checks the base by hand. Closing that needs a strict ruleset or a merge
  serializer, which is a separate decision.
- **Cost:** the ledger loses the signal 0006 relied on to tell a human's merge from an agent's
  in these repositories. What replaces it is the provenance trailer on every commit and the
  arming step in the session that opened the PR.
- **Follow-ups:** the merged-on-red count in the weekly audit (operator); the base-freshness
  decision above (operator); the README, the loop and the roles describe both shapes, the
  operator's repositories and an organisation's.

## Alternatives rejected

- Keep the human merge in the operator's repositories: the click carries no reading the gates
  have not already done, and it cost hours per cycle.
- Let the agent merge directly with `gh pr merge` as soon as it sees green: re-checks nothing
  the forge would not, and invites an admin merge when something is pending.
- Delegated merge only under the bot identity's own name (0006's incident decision): the
  right shape for an organisation, where the bot and the owner are different people's
  authority. Here both are the operator.

## Evidence

- `docs/10-measurement.md` (cycle 1 and 2 stage times), `STATUS.md` (cycle 4, branch
  protection rows).
- `adr/0006-pr-gated-output-human-release.md`, the 2026-09-09 incident.
