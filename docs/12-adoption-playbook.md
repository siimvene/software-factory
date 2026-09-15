# Adoption playbook

Turn 0 to turn N, in four variants: a healthy repo, a legacy core, a solo owner, an
organisation. Each step names its mechanical check. Skip nothing that has a check; label what
you skip.

## Before turn 0: decide three things

1. **What is the standard you adopt?** If the organisation ships an agent contract, a context
   standard, a sandbox template and a plugin catalog, adopt them; build only what is specific to
   your system ([adr/0001](../adr/0001-adopt-a-standard-not-build-a-harness.md)). If it ships
   nothing, this repository's [templates](../templates/) and the third-party tools named in
   [05](05-sensor-stack.md) and [06](06-verify-gate.md) are the minimum. Where the organisation
   ships a starter kit per stack (a working reference service with the contract handling, CI
   gates, test layout and agent rules already encoded), the kit is the architecture layer a
   program design note builds on: a note for a service on the kit names only the deltas, and
   the kit is where a gate script such as the fail-on-base check ships once for every fork
   ([02-loop](02-loop.md)).
2. **What is your money surface?** The code where a wrong change moves wrong money or shows
   wrong numbers people pay on. Tier it per class. It sets human sign-off and mutation targets.
3. **Which baselines do you take now?** Revert rate, defect escape, lead time on human-written
   code, dated, in memory. The comparison point is gone once agents dominate.

## Turn 0: adopt (one day for a healthy repo)

The full runbook, with the kvart numbers, is [17-onboarding](17-onboarding.md). The table
below is the short checklist; the tickable one, leg by leg with evidence columns and the gate
and sandbox wiring included, is [18-flightlist](18-flightlist.md).

| Step | Check |
|---|---|
| Operating contract vendored into the repo; lean root instructions; path-scoped rule files with honest paths | the sentinel is present; every rule file's globs match at least one file |
| Team-context repo created: front door, CODEOWNERS, ADR 0001 naming every shortcut, memory store bound read-only | `memspec stores` lists the team store read-only |
| Current-state specs bootstrapped by retro-generation; owner reviews the candidate table in the PM role | every spec folder passes the checker; the findings file exists |
| Repo and team ADRs for every live decision, candidates mined from docs and confirmed against code | every evidence path resolves |
| Consort gate reachable: cross-vendor backend probe returns the token; a second backend configured | probe passes; a deliberately failed backend makes the gate FAIL, not degrade |
| Sensor stack attached in a throwaway worktree, settings diff read, baselines re-cut on main by a person | gate green; the guard refuses a baseline edit |
| Branch protection (or the pre-push hook where the plan refuses it); provenance trailer | a push without the trailer is rejected; a dry-run push against the guard is blocked |
| Sandbox booted; egress proven closed both ways; scoped identity in place | allowlisted 200, non-allowlisted refused, direct route absent; the build resolves private packages |
| PM workspace from the template, pointers filled | the ticket skill runs against the specs |

Day 1 grows by the bootstrap. Record its wall-clock; it is the honest cost of the standard.

## Turn 1 on a legacy core: the verification net

Before any feature. See [09-legacy-adoption](09-legacy-adoption.md) for the method and the
measured lessons.

| Step | Check |
|---|---|
| Coverage tooling across the module tree, measured on the aggregate report | aggregate number exists; per-module sum shown next to it so nobody gates on the wrong one |
| Characterization tests on the money lane, current behaviour locked bugs included, header says so | mutation score on the first target, not coverage |
| Self-provisioning test infrastructure (database first; message broker as an open item) | the suite passes with the external database stopped and the flag on |
| Money surface tiered per class, predicate self-tests on true and false cases | the resolver refuses to print if a case misclassifies |
| Ratchets: base_ref is the real default branch, vendored assets and test trees excluded with reasons, changed-line coverage wired via a report converter | a planted violation of each gate fails by name and line |
| Layering as lint over the declared dependency graph, rules measured before written, validated on 10 cases | injection of each rule fires; a test-scope dependency stays green |

Gate for leaving turn 1: mutation score on the money modules, not a coverage percentage.

## Turn 2+: features, one ticket per turn

Run [02-loop](02-loop.md). After each turn:

- the sister spec PR is open before the code PR is called done;
- the cycle report has the four numbers ([10-measurement](10-measurement.md));
- every shortcut is in the report, and a repeated shortcut becomes a ticket against the
  process;
- every new or changed test was red on the merge base, or is declared a characterization or
  refactor test with its reason (the fail-on-base check, [05](05-sensor-stack.md));
- a sized ticket had its program design note before the first brief, and the note's module
  list is the scope the spillover check ran with ([02](02-loop.md)).

First turns are deliberately small and risky in the right way: a one-line fix through the
whole loop (proves the loop), then a money-path change with an owner decision inside it
(proves the gate). kvart did exactly these two.

## Variant: solo owner

Wear all three hats and record it. The named shortcuts kvart took, each now a measured cost:

| Shortcut | Consequence | What a team keeps |
|---|---|---|
| self-review as code owner (plan refuses branch protection) | merge gate is a habit | branch protection |
| PM and dev hat in one session | dev inherits the PM's framing | separate sessions or a non-inheriting reviewer, which is what caught the cycle-2 HIGH |
| no ticket tracker; tickets are files with a stage line | fine for one person | the ledger |
| spec update and spec checker not installed | sister spec hand-edited (forbidden by the contract) | the skills installed |
| no promote PR | knowledge stays in local scratch | the batched promote PR |
| headless QA fallback | less faithful than a real browser session | the browser extension |

## Variant: organisation

Add to the above, in this order:

1. Managed settings and the scoped bot identity as the enforcement tier above local hooks.
2. The vetted plugin catalog: nothing installed from an author's marketplace on a company
   machine; 30-day release age; pins that are real (fork or catalog).
3. A rule pack per stack (the backend pack that did not exist yet for the legacy core is the
   first thing the first turns seed).
4. Evals on the agent-config surface: changes to the contract, rule packs, instructions and
   skills gated behind a suite that replays past incidents. The biggest missing piece in every
   stack looked at; a runtime update once made a review agent post "done" without posting the
   review `[field: Pipedrive]`.
5. Per-outcome cost dashboard with daily thresholds from day 1.
6. The readiness gate per engineer: one feature through the full ladder by operating agents.
7. A hygiene rule on how the programme is described internally.

## Decisions an adopter must make explicitly

- Which mature system and which flow is the first oracle (the smallest thing that proves
  parity replay).
- Module ownership map: who owns which boundary.
- Whether hand-written-code overrides need a named approver or just the incident log.
- The retry and fallback policy when a model vendor is down in lights-out mode.
- The first delegated-merge pattern, if any, and its expiry.

## Anti-patterns, each observed once

- Building a harness the standard already ships.
- Gating on a per-module coverage sum.
- Raising a ratchet threshold to make it pass.
- Reading a zero-finding review as a pass without the reachability probe and the wall-clock.
- Ending a turn waiting on a child process.
- Attaching a gate into a live shared tree.
- A rule file that describes a model the code stopped using months ago.
- A cost estimate per bare agent instead of per orchestrator tree.
- A brief that names the outcome and leaves the shape to the builder.
- A test that passes on the merge base counted as a test of the change.
