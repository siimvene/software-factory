# 0018. Graduation into a context repo is PR-only by default; a repo opts into auto-merge

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** the operator (chief architect)
- **Supersedes:** 0011 decision 1, for graduation pull requests only

## Context

0011 made every pull request into an agent-managed context repo merge on open, on the premise that
the layer is derived from code and unread. Its own rejected alternative named the condition for
revisiting it: a context repo that gains human readers.

That condition now holds. Context repos are moving from one per team to one per product
(`<product>-context`), and a product context carries the normative contract that every
implementation of the product builds against: invariants, test oracles, behavioural specs. A PM's
graduation is the one write into that contract that is a *decision*, not a derivation, and with
several PMs on one product it is the only guard 14-pm-surface names between the current-state specs
and a swamp of proposals. Merging it on open means the PM approves a package their own agent
rewrote, the bytes land unseen by anyone else, and the mechanical checks report on a change that is
already on the default branch.

There is no evidence yet about where auto-merge would be safe. Before this record it was used
rarely, so changing the default breaks almost nobody.

## Decision

We will open graduation pull requests and stop. A graduation into a context repo waits for that
repo's code owners to review and merge, unless the repo declares otherwise.

- **The policy lives in the target repo**, in `.graduation.yml` at its root: `merge: pr-only`
  (the default, also when the file is absent or unreadable) or `merge: auto` with
  `auto_merge_paths`. Under `auto`, a graduation merges only when every path it changes matches
  one of those patterns and every check on the verified head has passed. Turning auto-merge on for
  a path is a one-line PR in that repo, not a plugin release.
- **A graduation may carry the spec plus append-only rows in the repo's declared oracle table**
  (`oracle_table`), so the decision and its observable outcomes land together.
- **Every graduation PR is labelled `graduation`.** How each one ended (merged as is, merged after
  edits, closed) is the evidence for which paths earn auto-merge.
- **The default branch requires the repo's check status.** A graduation from a client that still
  merges on open is then refused and waits like any other PR.
- **0011 stands for the rest of the layer.** Memory promote PRs and derived spec regeneration are
  still agent-managed and unread, and keep merging on open.

## Consequences

- **Positive:** a decision that changes the product contract gets a second reader before it is
  binding; the mechanical checks run before merge, not after; auto-merge is enabled per path on
  measured outcomes instead of assumed.
- **Cost:** a code owner's click per graduation, and the latency of waiting for it. With a handful
  of graduations a week this is small; the label makes it visible if it grows.
- **Follow-ups:** the PM workspace plugin reads `.graduation.yml` and never merges by default
  (plugin owner); each product context declares its policy and requires its check (repo owners);
  review the `graduation` label outcomes after the first month and open per-path auto-merge where
  merges came through unchanged (operator).

## Alternatives considered

- **Keep 0011 unconditional auto-merge:** fine for an unread derived layer; wrong for the layer
  implementations build against, where a wrong decision becomes tickets and code before anyone else
  reads it.
- **Required code-owner review on the whole context repo:** blocks memory promotes and spec
  regeneration that 0011 rightly keeps hands-off, and blocks a sole owner from merging their own
  agent's PR.
- **Auto-merge on a green check only:** closes the after-merge gap but still puts no second reader
  on a decision. Kept as the opt-in mode for paths that earn it.

## Evidence

- `adr/0011`, its "Alternatives rejected" revisit condition; `docs/14-pm-surface.md` defence #5.
