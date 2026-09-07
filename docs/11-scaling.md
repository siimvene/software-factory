# Scaling

What changes when the factory runs many streams instead of one operator's tree: the rungs a
change must climb, why the shape is a DAG and not a swarm, and how parallelism width is earned.
Most of this document is `[proposed]`; the rungs that exist are marked.

## What compounds

Not the agents. Model capability is exogenous and arrives for free. The compounding asset is
the verification net, the team knowledge plane and the gates: every turn that makes the net
tighter makes the next feature cheaper and safer. Existence proof: one operator on kvart at
roughly the monthly output of a 15 to 25 person organisation `[measured 2026-09-07]`. Counter-
evidence in the same data: the cost curve has not yet bent even for the expert operator
(non-review fixes rising, cost per commit flat). The flywheel is real; its payoff on cost is
not yet measured.

## Where the bottleneck moves when code is nearly free

1. **Deciding what to build.** Spec quality and acceptance identity. Specs already contradict
   each other in a generated corpus; no enforced approver, content hash or invalidation existed
   `[measured 2026-09-05]`.
2. **Verification trust.** Reviewer F1, revert rate, defect escape: none baselined yet.
3. **Release blast radius.** PR-gated output is the safe shape; production release stays human.
4. **Human review capacity.** At 70 %+ agent PR share reviewers drown unless review is also
   agentic and humans read evidence, not code.

## The blast-radius ladder

Each rung is mechanical. Nothing skips a rung. Rungs are agents or harness except L5 (a PM) and
the L6 release owner.

| Rung | What | State |
|---|---|---|
| L0 | sandbox with egress allowlist and scoped identity | measured (booted; identity blocked) |
| L1 | verification net: ratchets, characterization, mutation kill on money classes, async paths, YAGNI ladder | measured on kvart; partial on the legacy core |
| L2 | parity replay against an oracle (the mature system): same input, diff the outputs, money cent-exact | proposed |
| L3 | adversarial review loop, cross-vendor, bounded to 3 to 4 cycles | measured |
| L4 | contract tests at module boundaries plus the architecture gate: a boundary violation fails the build | designed (the architecture diff's provable explainers plus scope spillover = 0 are the gate; no agent needed) |
| L5 | acceptance on evidence with acceptance identity (approver, content hash, invalidation) | proposed |
| L6 | staged release: flag → shadow → canary → prod, automated revert on SLO breach | proposed; kvart runs flag → deploy → probe |

The architecture gate at L4 is the delegation of the single architect: at more than about 10
streams one head cannot hold coherence, and an ADR-backed mechanical boundary check is what
holds it instead.

## Oracles, not just specs

Mature systems (in a group: the acquired platforms being consolidated; in a product: the
incumbent being replaced) are executable specifications. Harvest three things per flow family:

1. behaviour specs into the team-context repo (the pattern already used);
2. recorded fixtures: real request/response, event and database-state samples, anonymised;
3. differential parity: replay the same input against the mature system and the new
   implementation, compare. kvart's billing engine is held to cent-for-cent parity with the
   incumbent it replaces; that is the template.

Parity replay catches "works but wrong", which unit tests and review cannot. Build the rig once
per harvested system per flow family; then every port is judged mechanically. Pin oracle
versions and snapshot fixtures, or the oracle drifts under you. Never raw production data in
agent context: anonymise at harvest.

## DAG, not swarm

Compute is not the binding constraint past a few hundred thousand list-price dollars per
month; coordination physics is.

- **Mutating parallelism is bounded by conflict surface.** Concurrent streams touching shared
  files conflict roughly quadratically. A monolith with a couple of hundred endpoints has perhaps
  10 to 30 real modules: 20 to 60 sustainable concurrent mutating streams, not 1,000, until
  module ownership boundaries exist.
- **The roadmap has a critical path.** ~74 roadmap items decompose to ~700 to 2,000 slices with
  a dependency chain (data model → services → endpoints → UI) 10 to 20 levels deep. Amdahl: the
  serial fraction (critical path, integration, acceptance) caps speed-up regardless of agent
  count.
- **Non-mutating and speculative parallelism is effectively unbounded.** That is where
  thousands of agents pay: best-of-N candidate PRs per slice judged by the net and the reviewer
  (humans see one), test and spec and benchmark generation, exploration.
- **Monoculture.** A thousand copies of one model make the same wrong assumption at once; a
  spec error propagates everywhere. Cross-vendor at the builder tier too, plus human acceptance,
  are the only decorrelators.
- **Budget is a fuse length.** A top-tier agent working continuously ≈ $20 to 60/h list; an
  orchestrator tree ≈ $30/h median. 50 trees ≈ $1.5k/h. Size the fuse to the quarter, not the
  weekend.

Realistic autonomous shape: 20 to 60 mutating streams × best-of-3-to-5 speculation each,
DAG-scheduled off the roadmap, humans on merge. That alone is a 100 to 300 agent factory.

## Width is earned, not set

Promotion criteria between phases, each with its instrument
([10-measurement](10-measurement.md)):

- revert rate ≤ the human baseline;
- reviewer F1 ≥ target on the known-bug PR set;
- merge-conflict rate per stream below threshold (dry-run merges);
- parity replay pass rate per flow;
- defect escape flat.

Width: 5 to 10 trees → 20 to 60 → delegated merge for qualified feature classes only when the
criteria hold for N weeks.

## Phases

| Phase | Shape | Exit |
|---|---|---|
| 0 | build the rungs: harvest specs and fixtures, first parity rig (money first), lift the net, F1 benchmark set, module map and architecture gate, revert and escape baselines, provenance and branch protection | a no-op change walks the ladder end to end; first money flow replays cent-exact |
| 1 | bounded factory: 5 to 10 orchestrator trees, best-of-N, humans on merge, measure everything | promotion criteria hold |
| 2 | widen to DAG width as criteria hold | delegated merge qualified for one recurring pattern |
| 3 | delegated merge for qualified classes; production release still human | ongoing |

Phase 0 sequencing when one person runs it: platform access and baselines first (calendar
latency, zero work); the first oracle as the week's proof; provenance plus branch protection
before anyone else touches the repos; release ladder, F1 set and module map slide to week 2.

## People at scale

Engineers are not feature writers; agents are. Engineers are the operators of the factory and
the owners of the rungs: each owns one module boundary plus its oracle and parity rig and runs 3
to 5 orchestrator trees inside it. Ten such operators is exactly the DAG width above. PMs feed
the DAG (decomposition is agent work; PMs approve slices and accept behaviour). The architect
owns boundaries via the ADR gate, the readiness gate per engineer, and the metrics.

Training is a Phase 0 deliverable: each engineer ships one feature through the full ladder by
operating agents end to end before running trees. Onboarding material is the per-stage cycle
reports, not a course.

Risks specific to the people: skill transition is the readiness gate in practice (an engineer
who hand-writes competes with agents and loses; one who cannot read parity evidence blocks
merges); morale while "building the machine"; the operators are also the calibration
population for per-team thresholds. Keep a hygiene rule on how the programme is described.

## What breaks at scale

1. Quality debt compounding invisibly (characterization nets preserve bugs, contradictory
   specs get built, no revert baseline).
2. Spend runaway: spend flattens only after per-outcome metrics and governance
   `[field: Uber Engineering]`. Cost per merged feature from day 1, daily thresholds. Use-it-or-
   lose-it budgets produce token-burning theatre: every funded job yields a merged test, spec or
   benchmark row or it is noise.
3. Bus factor: it works where architect, operator, reviewer and PM are one head. Transfer to
   teams that lack that is the unproven step; the readiness gate is the honest instrument.
4. Vendor concentration: no cross-vendor fallback in lights-out mode stops the whole factory
   `[field: Pipedrive]`. Two backends at the review tier exist; extend to the builder tier.
5. Externals set the calendar floor: certifications, third-party integrations, compliance.
   Agents do not accelerate those.

## Time and cost compression, as a model

For a group roadmap previously estimated as a 20-engineer, 3-year programme: with cheap
engineering, 3 evidence-reading PMs and one architect, the model compresses it to roughly 6 to
9 months at low-single-digit millions of compute, i.e. 4 to 6× faster and ~3× cheaper, with a
calendar floor of ~6 months set by externals `[proposed]`. The lever is not per-developer
speed-up; it is that consolidation of platforms becomes feasible when feature-parity ports are
cheap. Retired platforms are where the savings live. The second-order consequence: if it is
this cheap for you, it is this cheap for a competitor; the moat is distribution, the customer
base and a 12-month flywheel maturity lead, not the code.
