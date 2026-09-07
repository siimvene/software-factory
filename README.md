# Dark factory

A reference design for lights-out software delivery: humans specify outcomes and inspect
evidence, machines build, verify and ship, and every human touchpoint is a decision on
evidence rather than an inspection of code.

The design was derived from running the loop on a real product (kvart, an apartment
association management SaaS with money paths and a 4-locale UI) and from bootstrapping the same
loop onto a legacy Java core of 75 modules inside a group of companies. Every mechanism here
was either measured in one of those two places or is labelled as designed or proposed.
`STATUS.md` is the ledger.

## The claim in one paragraph

An agent generates code faster than people can read it. So the review load has to move off
people and onto gates, and gates have to be mechanical wherever they can be (ratchets that
only tighten, architecture diffs, coverage of changed lines, egress allowlists) and
inferential only where they must be (a cross-vendor reviewer that never saw the author's
context). What compounds is not the model, it is the verification net, the team knowledge
plane and the gates: every feature that lands makes the next one cheaper and safer. That is
the flywheel. The humans that remain do three things: approve intent, accept behaviour on
evidence, and press release.

## Measured, in brief

| What | Number | Where |
|---|---|---|
| Dev hat on to code PR open, one-line fix with full gate | 12 min 11 s | [cycle 1](case-studies/kvart-reference-implementation.md) |
| Dev hat on to live in prod, same fix, including human merge | ~28 min | cycle 1 |
| Dev hat on to code PR open, 1,383-line retirement of a money path | 18 min 58 s | [cycle 2](case-studies/kvart-reference-implementation.md) |
| Share of that time spent in the cross-vendor review | 52 to 58 % | cycles 1 and 2 |
| Real defects the cross-vendor reviewer found that tests and lint passed | 1 SERIOUS perf regression (trial), 1 HIGH money-path regression (cycle 2) | [trial](case-studies/kvart-head-hands-trial.md), cycle 2 |
| All-in cost per shipped feature on kvart, Aug 8 to Sep 7 2026 | ≈ $96 list price | [measurement](docs/10-measurement.md) |
| Coverage the legacy core actually had once measured on the aggregate, not per module | 55.6 % (per-module sum said 36.8 %) | [legacy adoption](docs/09-legacy-adoption.md) |
| Money-path lines the module-level tiering could not see | ~16,700 of 22,143 | legacy adoption |

## Read in this order

1. [Glossary](docs/00-glossary.md)
2. [Principles](docs/01-principles.md): gates not instructions, verification discipline, humans inspect output
3. [The loop](docs/02-loop.md): SPEC, BUILD, VERIFY, SHIP, LEARN and the two write-backs
4. [Operating contract](docs/03-operating-contract.md): the behavioural rules every agent session loads
5. [Knowledge plane](docs/04-knowledge-plane.md): specs, decision records, memory, and how they stay true
6. [Sensor stack](docs/05-sensor-stack.md): the four mechanical layers that run before any model reviews
7. [Verify gate](docs/06-verify-gate.md): the cross-vendor review, its three axes, and how to prove it ran
8. [Roles and authority](docs/07-roles-and-authority.md): who decides what, and what agents may never do
9. [Sandbox and isolation](docs/08-sandbox-and-isolation.md): worktrees, egress, identity
10. [Legacy adoption](docs/09-legacy-adoption.md): the verification-net bootstrap for a core with no net
11. [Measurement](docs/10-measurement.md): what to baseline before agents dominate, and the bar for "it paid off"
12. [Scaling](docs/11-scaling.md): the blast-radius ladder, DAG not swarm, width that is earned
13. [Adoption playbook](docs/12-adoption-playbook.md): turn 0 to turn N for a healthy repo, a legacy core, a solo owner, an organisation
14. [Failure catalogue](docs/13-failure-catalogue.md): every trap that cost an hour, with its fix

Then the [case studies](case-studies/), the [evidence](evidence/), the [templates](templates/)
and this design's own [decision records](adr/).

## What this is not

- Not a tool. It composes tools that exist (cleat, consort, memspec, enola, ripwire, a context
  standard, a devcontainer template) and says where each sits and why.
- Not a claim that review can be removed. It is a claim that review can be moved: from reading
  diffs to reading evidence, and from every change to the changes that carry risk.
- Not finished. `STATUS.md` says which rungs are measured and which are still a drawing.

## Provenance

Derived 2026-09-07 from the kvart dogfood (Day 1 bootstrap, cycles 1 and 2, the sensor-stack
wiring), the 2026-09-05 head-and-hands harness trial, and the 2026-09-04 to 09-07 legacy-core
flywheel work. See [WRITING.md](WRITING.md) for the anonymisation and evidence rules this text
follows.
