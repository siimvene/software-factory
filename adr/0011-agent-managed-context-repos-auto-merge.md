# 0011. Agent-managed context repos auto-merge; agents refresh shared context continuously

- Status: accepted
- Date: 2026-09-16
- Deciders: the operator (chief architect), extending 0005/0006/0007
- Qualifies: 0005 (humans approve, never author), 0006 (PR-gated output), 0007 (specs derived)

## Context

0006 fixed the merge decision to a human because a merge under the owner's identity from an
agent session launders a machine decision as a human one (the kvart #44 incident). That reasoning
holds wherever a human is *expected* to review. It does not hold for the context/spec layer:
those repos are agent-managed, derived from code, and effectively unread by a human before merge.
There, the human merge is not a decision - it is the etiquette the standard's own line ("gates are
mechanics, not etiquette") rejects. A PR that waits for a click nobody makes is latency, not a gate.

Separately: agents read the shared context (memory store, team-context) at session start, but a
run outlives that snapshot. Concurrent agents and stakeholders commit while a session works, and
a session that only pulled once operates on stale context - the measured stale-main class.

## Decision

1. **Context repos auto-merge, unconditionally.** A pull request into an agent-managed
   context/spec repository (`*-team-specs`, `*-team-context`, `*-context-repo`) is merged
   automatically on open. No human merge, no wait. This is not the 0006 laundering case: no human
   review is claimed for this layer, so no human decision is misrepresented.
2. **Human merge is unchanged for code repositories** and any human-read layer. 0005/0006 stand
   there in full; agents still never merge their own code proposals.
3. **Agents sync shared memory on a start/finish contract.** A session fast-forwards the local
   memory store from origin at start (before it reads any memory) and pushes its writes back at
   finish (after end-of-session memory management). This is mechanical - a SessionStart pull/ff hook
   and a Stop push hook (`~/.memspec/bin/sync-pull.sh`, `sync-push.sh`), not agent behaviour - so
   freshness never depends on the agent remembering. Pull is fast-forward-only (a diverged local
   no-ops and the finish-push reconciles); push is a bounded pull-rebase-retry for concurrent
   sessions on one store; both are non-blocking, so a network failure never stalls a session. A
   team-context read through the GitHub connector is already live; a locally-checked-out context
   repo follows the same start-sync.

## Mechanism

- **Branch protection must not require review on a context repo.** Auto-merge is a runtime
  contract; a repo whose branch protection sets `require_code_owner_reviews` physically blocks it.
  The scaffold (`deploy/02-scaffold-a-project.md` D0.2) drops the required review on the
  team-context repo under this ADR - the merge gate for that layer is removed on purpose, not left
  half-configured. Code repos keep their protection.
- **The start/finish sync applies to what is writable.** The pull/push in decision 3 is the
  operator's memory store and any writable clone. A team-context mounted read-only and cloned at
  boot (`deploy/standard/context-standard/STANDARD.md`) re-syncs at boot, not by a mid-run pull;
  its live-read path is the GitHub connector. Making a read-only mount refresh mid-session is a
  re-clone, a mechanism follow-up, not a guarantee this ADR delivers today.

## Consequences

- Positive: the context layer keeps pace with the code and the fleet without a human bottleneck no
  reader was using; sessions work from fresh shared context.
- Accepted tradeoff, second axis: with no human at the merge, the bytes that land get no
  diff-level human review - the human approved the package shown in chat, and the agent merges what
  it committed. For a code repo that would be unacceptable (a tampered or hallucinated payload
  merging unseen); for an agent-managed context repo the blast radius is a markdown spec that is
  treated as derived and rewritten from code, and the operator accepts it. This is why the carve-out
  is context repos only and code merges stay human.
- Accepted tradeoff, named: auto-merge removes the guard that 14-pm-surface calls "the only thing
  standing between the current-state specs and a swamp of proposals". A graduated *proposal* can now
  land in a context repo with no human between it and merge. The operator accepts this: the layer is
  agent-managed and treated as derived, not as a hand-curated human source of truth. The state-check
  (14-pm-surface defence #3) becomes the place to catch a proposal mislabelled as current state, if
  it is built; it is not a merge gate.
- Cost: a continuous pull adds git traffic and can surface a conflict a once-per-session run never
  saw; pulls are fast-forward-only and non-blocking so a diverged local never stalls the run.

## Alternatives rejected

- Auto-merge only on a green mechanical gate: safer, but the operator judged the gate not worth
  building for a layer nobody reads; revisit if a context repo ever gains human readers.
- Keep human merge everywhere: the status quo; leaves unread PRs waiting on a click that is pure
  latency.

## Evidence

- `docs/07-roles-and-authority.md`, `docs/03-operating-contract.md` (sections 2 and 9),
  `docs/14-pm-surface.md`, `docs/04-knowledge-plane.md`; `adr/0006`.
