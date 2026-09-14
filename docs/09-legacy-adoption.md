# 09. Legacy adoption: bootstrapping the loop onto a core with no net

The rest of this design assumes a repository that can already tell you whether a change is
safe. Most valuable code cannot. This chapter is the method for the other case: an old,
large, business-critical core that has tests but no measurement, conventions but no
enforcement, and no agent ever ran against it.

It was derived from one adoption, a 75-module Gradle Java core owned by a group of
companies, run between 2026-09-04 and 2026-09-07. Every number below carries the date it
was observed. The sequence generalises; the numbers are that core's.

## (a) A software factory over an un-netted core is a crash factory

The loop in [02-loop](02-loop.md) moves review load off people and onto gates. That trade
only works if the gates can actually fail. Over a core with no coverage measurement, no
mutation testing and no structural ratchets, every gate is a green light with no bulb in
it, and an agent that generates code faster than anyone reads it will land regressions at
machine speed.

So the first turn on a legacy core is not a feature. It is the verification net, and it is
the only turn whose deliverable is measurement rather than behaviour.

One correction the adoption forced immediately: "un-netted" is a claim about tooling, not
about tests, and the two are easy to confuse. The core was inferred to be untested from a
test-file ratio of about 12 %. Once JaCoCo was wired and the aggregate report ran, it was
at 55.63 % line coverage `[measured 2026-09-04]`. It had coverage. Nobody could see it.

The generalisable rule: **measure before you characterise the repository.** An inference
from file counts is not a baseline, and a bootstrap plan built on a wrong inference spends
its first week netting code that was already netted.

## (b) Adopt the standard, do not build a harness

The first version of the adoption design (v0, 2026-09-04) built a standalone harness: its
own gate manifest, its own module map, its own spec template, its own memory topology, its
own turn runner in CI. It was rewritten the same day as v1, because the organisation
already shipped, as reviewed and published artifacts, almost everything that harness
reinvented.

What was rebuilt versus what already existed:

| Reinvented in v0 | Already shipped by the group standard |
|---|---|
| An agent behavioural contract and quality floor | The org agent contract, loaded in every adopting repo |
| A repo structure and conformance check | The context standard, with an `adopt.sh` and conformance levels |
| A team knowledge plane (specs, memory, rubric) | The team-context template and its memory store |
| A sandbox with egress control and credentials | The devcontainer template, Java variant, with an allowlist gateway |
| A cross-vendor review step | The consort plugin in the group's plugin marketplace |
| A spec bootstrap and spec write-back | The spec plugin (retro-generate, plus a sister spec PR per commit) |
| A review rubric | The rule-pack plugin |
| A gate manifest listing every check | The above, plus mechanical CI, with no duplication of the local review |

The whole v0 gate manifest collapsed into: the shipped review plugins, the shipped rule
packs, the org contract's quality floor, and a CI job that stays purely mechanical.

**The rule: on a legacy core, the only things you build are the ones the standard cannot
know.** In this adoption that was exactly four: the verification net, the structural
ratchet configuration, the money-criticality tiering, and a language-specific review rule
pack that did not exist upstream yet. Everything else was adoption work: run the adopt
script, copy the sandbox variant, seed the specs, wire the plugins, commit the memory
pointer.

Why it matters beyond tidiness: a bespoke harness is a second standard with one user. It
does not receive upstream fixes, it does not benefit from other teams' incidents, and the
next repository in the group starts from zero again. A reinvention that works is still a
liability.

## (c) The verification-net bootstrap, in order

Five steps, each with the lesson that cost something to learn.

### 1. Wire coverage as a ratchet, and gate on the aggregate

Coverage is wired as a **ratchet, not a floor**: the number may not fall. A floor on a
legacy core is either unreachable or set so low it never fires.

The trap is granularity. A multi-module build attributes coverage only to the module that
owns the class, so a cross-module integration suite is credited with almost nothing. In this
core the integration module wrote 1.2 MB of execution data touching about 2,070 classes
across other modules, and its own report scored 12 of 12 lines, its single main class,
100 % `[measured 2026-09-04]`.

Summing per-module reports gave 36.77 % against a true aggregate of 55.63 %, a 19-point
undercount `[measured 2026-09-04]`. Worse than the error is what a per-module ratchet would
have permitted: **deleting the entire integration suite at zero coverage cost.**

So the gate reads a single merged report, produced by a root task that merges every module's
execution data against every module's classes. Never the per-module sum.

Two toolchain facts that stop the wiring dead on a modern JDK: the coverage agent must be
new enough to read the bytecode version (0.8.12 failed with `Unsupported class file major
version 69`, 0.8.14 worked) `[measured 2026-09-04]`, and the mutation engine hits the same
wall below version 1.20 `[measured 2026-09-04]`.

One measurement hazard to write down before anyone runs a filtered test: a filtered run with
a rerun flag **overwrites the module's execution data with only the matched class**, silently
corrupting the aggregate. Re-run the full module task before trusting any aggregate number
after a filtered run `[measured 2026-09-04]`.

### 2. Characterization tests on the money lane, with mutation score as the gate

Generated tests lock current behaviour, bugs included. Say so in every generated test
header: this is a refactor net, not a correctness proof.

**Coverage alone is gameable, and machine-generated tests game it by default.** A test that
calls the method and asserts that something came back scores full line coverage and zero
mutation score. So the acceptance gate on generated characterization tests is the **mutation
score**, not coverage: coverage says a line ran, mutation says a test would notice it
changing.

First-target selection matters more than volume. The class chosen was a price recalculation
service whose verification logic compares 20 money extractors across two states as chained
inequality tests. That shape is what mutation testing punishes hardest, so it is the honest
proving ground rather than the flattering one. Result: 51 test cases in one 912-line file
with mocked collaborators and no database, class line coverage 1/238 to 238/238, and
**68 of 68 mutants killed, up from 0** `[measured 2026-09-04]`. Aggregate coverage moved
55.63 % to 56.05 %.

Two derived rules:

- **One mismatch per field, table driven.** That is what kills mutants on comparison-heavy
  money code, and it is a reusable recipe for the next class.
- **Lock real bugs as-is, deliberately.** The suite found a field populated from the wrong
  source and asserted the wrong behaviour with a comment explaining it. A characterization
  net that silently fixes what it finds is no longer a net; it is an unreviewed behaviour
  change hiding inside a test commit. The fix is a separate, specified turn.

Keep the mutation scope narrow while the net is small. Mutation testing runs the suite once
per mutant, so widening the target list costs real wall-clock.

### 3. Self-provisioning test infrastructure

"You must have a database running" is a genuine blocker for a lights-out loop, because an
agent in a fresh sandbox has no hand-provisioned anything.

The shape that worked, with zero edits to any existing test or base class: a
**launcher-session listener** in the shared test-support module, registered through the
service-loader manifest, which runs once per test JVM before any test class loads, starts
the container, and publishes the connection details. It is opt-in behind a build flag; with
the flag absent, behaviour is exactly as before, including the schema-reaping task that a
container environment must skip.

Three rules fell out of it:

- **The contract with tests is system properties, never a class.** The listener implements a
  launcher type that is not on any consumer module's test compile classpath, so nothing
  downstream can import it, and nothing downstream needs to. The integration is entirely
  two properties that the shared test configuration already assembles the connection URL
  from.
- **Do not pin a BOM-managed dependency.** Let the framework BOM manage the container
  library. It renamed its module artifacts across a major version while leaving the old
  coordinates published, so asking for the old names with an old pin produced a
  **split-brain classpath**: the BOM forced the core to the new major, the modules stayed on
  the old one, and the code compiled against one and ran against the other. It worked for
  the database module, which is exactly why it was dangerous `[measured 2026-09-04]`.
- **A dead optional container must not fail the JVM.** The message-broker container never
  started on the development host: the library injects a starter script after container
  creation, the file never arrived, and the container came up with completely empty logs
  until the readiness probe timed out. This was diagnosed, not solved. Image, wait string,
  timeout, reuse and entrypoint were each ruled out by measurement, the image reaches the
  awaited log line in about 20 s when started by hand, and database containers work on the
  same host `[measured 2026-09-04]`, so it is a container-runtime interaction and it stays
  open. The design absorbed it by making broker failure non-fatal and having the broker
  smoke test skip itself when the property is absent.

A second, independent finding in the same area generalises further: **verify that a test
profile actually enables the subsystem you think you are testing.** Every test profile group
in this core excluded the messaging auto-configuration outright, so no test context talked to
a broker at all and the asynchronous choreography was untested by construction
`[measured 2026-09-04]`. Nothing about the container work would have revealed that.

### 4. Baseline the environment traps, once, in writing

Two host traps each cost a failed full-suite run, and both reappear on every new machine:

- **Connection limits.** A stock database `max_connections` of 100 is below what a parallel
  build needs; one module died with "too many clients". The dedicated test container runs
  with a raised limit `[measured 2026-09-04]`.
- **A native frontend dependency with no binary for the developer architecture,** which
  compiled from source and needed an older interpreter twice over. The failure surfaced as an
  unrelated package-manager error while silently taking down two test modules, including the
  19-file cross-module money-lane suite, because they depended on the frontend bundle task
  `[measured 2026-09-04]`.

The general rule: **when a build runs with a continue-on-failure flag, an early failure in an
unrelated-looking task can remove whole test modules from the run.** Compare the count of
executed test tasks against the module list before trusting a coverage number. For reference,
the full suite here ran in 9 min 09 s across 75 projects with 8 workers `[measured 2026-09-04]`.

### 5. Protect neighbouring systems from the build

The core's build defaulted its test datasource, and a schema-reaping task, to the standard
database port on localhost. On the development machine that port belonged to a different
project's database (kvart's). Two bare test runs wrote schemas into it, and the reaping task
had a licence to **drop every test-looking schema older than 24 hours in whatever database it
reached** `[measured 2026-09-04]`.

Mitigation is mechanical: a dedicated container on a non-default port, that port passed on
every invocation, and a post-run assertion that the neighbouring database is still clean.
Written into the repo's agent rules as a hard rule, not remembered.

## (d) Money-criticality is tiered per class, not per module

Risk tiering decides which changes need a named human to sign off on the outcome. On a legacy
core, **module granularity is almost always wrong**, because the module boundaries were drawn
for deployment, not for risk.

Here, a large aggregator module carried the bulk of the money logic and was not on the
money-critical module list at all. The proof was measurable: fully netting one money class
moved the module-level money metric by 0.17 points, because the metric could not see it
`[measured 2026-09-04]`.

The retier used two tiers over class and package globs:

- **transaction**: wrong code moves wrong money. Named-human outcome sign-off, always.
- **reporting**: wrong numbers get shown or paid on. Lighter gate.

The size of the correction is the argument. The module-level surface was **5,398 lines at
48.0 %**; the real surface was **22,143 transaction lines at 61.87 %** plus 8,224 reporting
lines at 42.98 %, so the module view could not see roughly **16,700 lines of money code**
`[measured 2026-09-04]`.

Three rules from the resolver that produced those numbers:

- **The predicate self-tests before it prints anything.** 15 cases, true and false both
  exercised, and the tool exits non-zero and withholds all numbers if any case misclassifies
  `[measured 2026-09-04]`. A scan over a large space that cannot fail is not evidence; it is a
  confident wrong answer. This is [06-verify-gate](06-verify-gate.md)'s "prove the reviewer
  ran" applied to a script.
- **Globs match the bytecode package, not the directory.** Exactly one file in 4,317 declared
  a package that disagreed with its directory `[measured 2026-09-04]`. One is enough: the
  coverage report keys on the declared package, so a directory-keyed index silently dropped
  that file. Key on what the report says, then assert that nothing is unresolved.
- **Beware fixtures.** Whole-moduling the main service module put demo-data seeding at the top
  of the money gap list, because 1,031 of its 1,312 lines were a seeding configuration active
  only in local profiles `[measured 2026-09-04]`. That is how the error announced itself. A
  module showing 0 % coverage is a hypothesis about risk, not a finding: read what the lines
  are before netting them.

## (e) Structural ratchets on a legacy core

The ratchet layer (cleat here) sits below review and fires inside the agent loop: complexity
ceiling, escape sites, duplication, doc size, test hygiene, changed-line coverage,
conventions. Each check is a ratchet: **a baseline records the debt present on adoption day,
and only new debt fails.** On a low-rot core this is rot prevention, not cleanup.

Six things a legacy adoption must get right.

1. **The baseline is the debt on adoption day, and it is a person's artifact.** Keep the
   baseline files next to the configuration and restore them when re-attaching, or the attach
   step regenerates them from whatever the tree looks like that day and the ratchet silently
   resets looser. Baselined here: 245 escape sites and a 14.74 % duplicated share
   `[measured 2026-09-04]`.
2. **`base_ref` must be the real default branch.** The attach default was `origin/main`; this
   core's default branch was `develop`, and `origin/main` was 81 commits behind it. The
   duplication gate therefore judged 19,431 lines as changed and reported **557 clone pairs**.
   Pointed at the real base it reported **6** `[measured 2026-09-04]`. All 6 were genuine
   copy-paste, in the characterization test written earlier the same day, which a 100 %
   mutation score had said nothing about. That is the argument for running a behavioural gate
   and a structural gate together.
3. **Changed-line coverage usually needs a report converter.** The ratchet wanted LCOV or
   Cobertura; the build's coverage plugin emitted neither. A small converter over the
   aggregate report closed it, cross-checked against the coverage tool's own totals
   (33,371 / 59,534 = 56.05 %, zero unresolved) `[measured 2026-09-04]`. The threshold applies
   to **changed** executable lines, not to a repo-wide floor, which is what makes the
   verification net pay off inside the agent loop rather than only in CI.
4. **Exclude vendored static assets and test trees, with the reasoning written down.** The raw
   complexity finding count was 407. 267 of those were vendored static JavaScript (a jQuery
   bundle at 71 findings, a typeahead bundle at 21, a highlighter at 21, plus others): third
   party, never refactored, and bumping a vendored library would fail the gate. That exclusion
   was worth 66 % of the raw findings. Test trees are excluded too, and on a legacy core the
   reasoning is stronger than usual: **the verification-net turn exists to grow the test layer,
   and a gate that fails new tests fights its own purpose.** Escapes, conventions and
   duplication still cover tests. Final baseline: **94 functions over the ceiling out of 10,679
   judged, 31 of them on the money transaction tier** `[measured 2026-09-05]`. Cross-check
   kept: the backend-language-only subset came to exactly 128, matching a figure measured
   before the analyzer was installed.
5. **The wrong tool can answer to the right name.** The package manager's `lizard` formula is a
   compression library; the complexity analyzer is a different project that installs a binary
   with the same name. The gate invokes a bare `lizard` with no configurable path, so the wrong
   tool would have been read as nonsense rather than erroring `[measured 2026-09-05]`. Verify
   that the tool identifies itself correctly (`lizard --help` must name the analyzer) before
   trusting a single number it prints.
6. **The 30-day release-age rule applies to gate tooling too.** The distribution's analyzer
   build was 17 days old, so it was installed instead as a pinned virtual environment on the
   previous version `[measured 2026-09-05]`. The same rule sent a duplication tool, whose
   latest release was 1 day old, to a pinned older version in an isolated install
   `[measured 2026-09-05]`. Gate tooling runs with repo access on every agent turn; it is part
   of the supply chain, not adjacent to it.

**Do not edit the policy to pass the gate.** One known failure was left red on purpose: a
six-line block of identical static test imports flagged as a clone across two files. Imports
cannot be extracted, and the tool has no accept path for clones in changed lines. The proposed
fix, feeding it a token-based duplication report instead of the line-based built-in finder,
was installed, measured and reverted, because it made the result worse: **5 clone pairs against
the built-in finder's 1**, all import blocks either way `[measured 2026-09-05]`. Nor can a
token threshold separate them, and that is measured rather than assumed: across 3,468 clones,
import blocks (1,749; min 50, median 62, max 308 tokens) and real code clones (1,719; min 50,
median 69, max 10,199) have **overlapping distributions**, so at a threshold of 150 tokens you
still catch 17 import blocks while discarding 90 % of the real clones `[measured 2026-09-05]`.
Raising the minimum would have been pure gaming with a cost. The honest paths are an upstream
fix, or waiting for the branch to merge, at which point those lines stop being changed lines
and the gate self-clears.

## (f) Layering as lint over the declared dependency graph

Layering is the one gate that catches architectural drift no test would, and it is the
highest-value thing a legacy core can add, because module seams are where an agent fleet does
its damage.

The generic layering checker did not fit. It models layers as top-level directories under a
root, which does not map onto 75 build modules. **The authoritative layering fact in a
multi-module build is the declared dependency**, so the rules were written as convention
regexes over every module's build file instead.

Three rules, each **measured against the real graph before being written**:

| Rule | Roots | Violations on adoption day |
|---|---|---|
| an `-api` module must not depend on any `-impl` | 33 | 0 |
| an `-impl` module must not depend on a sibling `-impl` | 27 | 0 |
| nothing may depend on a `*-service` module | 72 | 0 |

Zero production violations and zero production cycles `[measured 2026-09-04]`, so the gate
ships with **no exemptions and no baseline file**, which is the ideal ratchet: every future
site is a decision rather than inherited debt.

The near-miss is the transferable part. The first measurement said rule 2 had **7 violations**.
Every one was a test-scope dependency, which is entirely legitimate, and a regex conflating the
two scopes would have fired on seven innocent lines on day one. The patterns therefore anchor
on the production configuration names only, so a test scope cannot match, and they were
**validated on 10 cases (4 that must match, 6 that must not) before being wired**
`[measured 2026-09-04]`.

Then prove the gate by injection, in a throwaway worktree: inject a violating dependency and
watch each rule fire naming file, line, rule, offending text and reason; inject a test-scope
dependency as a negative control and watch it stay green; revert and confirm no residue
`[measured 2026-09-04]`.

One property worth copying verbatim: the failure message **refuses to tell the agent how to
whitelist the violation**. It says that accepting a site into the baseline is a policy decision
for a person. A gate that explains its own bypass is a suggestion.

## (g) The ratchet is working, even when the number is inconvenient

The failure mode after a baseline is taken is to explain away every red result as a bootstrap
artifact. One such dismissal was checked and turned out wrong in a way worth generalising. A
function that was **in** the baseline at complexity 10 across 48 lines had grown to complexity
15 across 100 lines on the default branch. It had been recorded as "a bootstrap issue, not a
defect". It was a real regression, a 2x growth of a baselined function, and the gate was doing
exactly its job `[measured 2026-09-06]`.

Two rules:

- **Being in the baseline means "this much debt was accepted", not "this file is exempt".**
  Growth of baselined debt is new debt.
- **Accepting a worse number is a person's reviewed commit,** never an agent's edit to the
  policy file and never a baseline rewrite in the middle of a task. The gates only ever
  tighten; that is the entire mechanism.

## (h) Sandbox constraints a legacy build imposes

The sandbox design is in [08-sandbox-and-isolation](08-sandbox-and-isolation.md). Four
constraints only appear when the workload is a large legacy build.

- **A sandboxed repo must be a real clone, not a worktree.** A worktree's `.git` is a file
  pointing at an absolute host path outside the container mount, so every git command fails
  with `not a git repository` and the post-create step dies at its first `git config`
  `[measured 2026-09-04]`. This collides with the loop's own worktree-per-turn isolation, so it
  is one or the other per turn. A local clone is cheap: hardlinked object cloning took 0.7 s
  for a 135 MB git directory `[measured 2026-09-04]`.
- **Git hooks do not travel with a clone.** Any local enforcement (here, a pre-push guard
  implementing a local-only rule) must be re-installed in every new clone, and its absence is
  silent. Anything that must hold everywhere belongs in managed settings or CI, not in a hook.
- **Container-based test infrastructure cannot work inside the sandbox**, because there is no
  Docker socket and no Docker CLI in the workload, by design. So the two environments get two
  provisioning paths: an ephemeral container on the host, a compose **sidecar database** in the
  sandbox, selected by build flags. The sidecar is arguably the better shape anyway:
  internal-only, no egress, and no Docker socket handed to an agent `[measured 2026-09-04]`.
- **Egress control works, and is worth verifying rather than assuming.** An allowlisted host
  returned 200; a non-allowlisted host failed at the gateway; stripping the proxy environment
  to go direct failed with no DNS and no route, because the workload sits on an internal network
  with no network-admin capability. Bypass and allowlist are both closed `[measured 2026-09-04]`.

**The hard blocker is identity, not tooling.** The build could not resolve its private Maven
packages inside the sandbox, failing with `Username must not be null!`, which is authentication
rather than the allowlist, since the host was reachable `[measured 2026-09-04]`. Pasting the
operator's personal token into a machine-wide shared cache volume is the wrong answer, so the
sandbox cannot build the repository at all until a **scoped bot identity** exists (read access
to contents and packages, nothing more). Until then there is no autonomy in the box, which
makes scoped identity the first thing to request, not the last.

Smaller boot findings that generalise: the sandbox CLI **reuses running containers**, so an
override edit is silently ignored until a forced recreate; the template's example sidecar image
version drifted from the CI image version, and its stock connection limit was below what a
parallel build needs; the lock file had no entry for one feature, so it resolved unpinned on
every boot; and the environment check script reported a missing memory CLI as "expected,
installed at post-create" when nothing installed it, so memory reconcile and session injection
were silently skipped `[measured 2026-09-04]`. Check that a boot check's excuse for a missing
component is actually true.

## (i) What remains open

At the end of this bootstrap, with the net green and the ratchets live:

- **A scoped bot identity.** Without it the sandbox cannot build, so BUILD is theoretical and
  there is no autonomy. It is a decision for the owner, not an agent action.
- **Lifting local-only.** Everything above ran with all remote writes blocked. Lifting it is
  what unblocks SHIP and LEARN, meaning both write-backs, meaning the flywheel edge.
- **CI and merge authority** on the core, which belongs to the owning team.
- **The message-broker container**, diagnosed to a container-runtime interaction and parked,
  plus the separate finding that no test profile enables messaging at all.
- **A language-specific review rule pack**, which did not exist upstream and has to be authored
  from the conventions the first feature turns surface.
- **Evals on the agent-configuration surface.** Every gate here points at the code; none points
  at the machine. Changes to the agent contract, rule packs, repo agent files and skills should
  themselves be gated by an eval suite, with each incident becoming a permanent eval. It is the
  largest missing piece in this design, and it is `[proposed]`, not built.
- **One known-failing structural gate**, left red on purpose (see (e)), because the honest fix
  is upstream and the dishonest fix is a policy edit.
