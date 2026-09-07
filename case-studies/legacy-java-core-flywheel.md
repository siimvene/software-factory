# Case study: bootstrapping the loop onto a legacy Java core

**Subject:** the legacy core, a 75-module Gradle/Java/Spring monolith owned by a group of
companies, in continuous production use.
**Window:** 2026-09-04 to 2026-09-07.
**Operator:** one person (Siim) plus agent fleets, working entirely on local branches.
**Method:** [09-legacy-adoption](../docs/09-legacy-adoption.md). This is what actually
happened, in order, with the numbers.

Nothing in this window was pushed to any group repository. Every remote write was blocked by
policy and by a hook, deliberately, for the whole four days.

---

## 2026-09-04, morning: decision and mandate

The group picked the legacy core, over the alternative candidate, as the platform to carry
forward. The mandate attached to that decision was not "modernise it": it was to build an
agentic feature-development loop on it, with the author's own product (kvart) as the measured
reference implementation of the same loop.

That framing set the constraint that shaped everything after it. The reference implementation
is greenfield, has more test code than source, and its money paths are covered. The legacy core
is none of those things, so the port is the same operating model minus the greenfield advantage,
plus a one-time verification-net bootstrap.

Two housekeeping facts from the first hour that mattered later: the existing local checkout of
the core was 62 commits stale, so all work started from a fresh worktree off the real default
branch `[measured 2026-09-04]`; and a first-pass harness was scaffolded (a module map generated
from the build settings, a gate manifest, a spec template, a CI turn runner).

## 2026-09-04, midday: design v0, then the re-base onto the group standard

The v0 design was written, reviewed against published material on agentic SDLC practice, and
then discarded in the same day.

The finding that killed it: the group had **already shipped** the Agentic SDLC as two products,
a development-standards repository (agent contract, context standard, devcontainer templates,
an adopt script) and a plugin marketplace (cross-vendor review, solo review, UX QA, spec
generation, rule packs). The v0 harness had reinvented the agent contract, the repo structure,
the team knowledge plane, the sandbox, the review step, the spec write-back and the rubric
`[measured 2026-09-04]`.

v1 replaced "build the flywheel runner" with "**adopt the standard, then run turns**", and cut
the genuinely local build down to four items:

1. the verification net,
2. the structural ratchet configuration,
3. money-criticality tiering,
4. a backend-language review rule pack, which did not exist upstream (the marketplace shipped
   only a common and a testing pack) `[measured 2026-09-04]`.

The gate manifest collapsed entirely into shipped plugins plus a mechanical CI job.

## 2026-09-04: turn 0, adopt the standard, locally

Turn 0 ran on a throwaway worktree, never the live tree.

- The context standard's adopt script seeded the repository and pointed it at a team-context
  repository; the conformance check passed `[measured 2026-09-04]`.
- A local team-context repository was created **with no remote at all**, so it is structurally
  unpushable. Creating the real remote is a remote write, and remote writes were blocked.
- The Java devcontainer variant was copied in.
- Spec retro-generation ran over the whole core and produced **98 features across 196 spec files
  in 19 subdomains**, plus lane maps covering 44 backend modules and 7 frontend apps, with every
  technical reference path verified on disk `[measured 2026-09-04]`.

Two things came out of turn 0 that were not planned.

**Spec generation doubled as an audit.** Writing specs from code surfaced about 12 real defects,
including a checkout confirm-and-pay path whose entry method had zero callers, an embed widget
pointing at a script that does not exist, two commands that never emit the events their
consumers wait for, a dead cascade with no handler, and a back-office shell whose gating is
client-side only behind an unguarded wildcard `[measured 2026-09-04]`. These became candidate
feature turns.

**A delegation trap, with a fix worth copying.** Spec-generation agents told to "explore in
parallel" spawned write-capable forks that raced on the same files. The prompt that fixed it:
*you are the sole writer; helpers are read-only; one writer per file* `[measured 2026-09-04]`.

### Enforcing "local only" as a gate, not a note

The local-only rule was written into the repository's agent rules, and then backed by a
`pre-push` hook that rejects every push, on both the primary checkout and every worktree sharing
its git directory. Verified by dry run `[measured 2026-09-04]`.

The reasoning is the whole design philosophy in miniature: a rule in a document is a suggestion,
a gate is enforcement. An accidental push or PR from an agent loop into a production core owned
by someone else is precisely the failure this setup must not have. Lifting the rule requires the
owner to say so in words, per action.

The hook's known limit was recorded at the same time: **git hooks do not travel with a clone**,
so every new clone starts unguarded and must have the guard re-installed.

## 2026-09-04: turn 1, the verification net

Wired in this order, each step verified on the machine rather than assumed for CI.

**Coverage tooling.** Coverage was applied across all subprojects. The first committed wiring was
broken and had been described as CI-validated: the coverage agent at 0.8.12 cannot read Java 25
bytecode (`Unsupported class file major version 69`). Fixed by moving to 0.8.14, after which a
single module's report emitted real counters `[measured 2026-09-04]`.

**The aggregate report, which is the actual gate input.** Summing per-module reports gave 36.77 %
line coverage. The merged aggregate gave **33,117 / 59,534 = 55.63 %** (branch 45.30 %, class
73.67 %, method 57.31 %), a 19-point undercount, because coverage is attributed only to the
module owning the class and the cross-module integration suite is credited with 12 of 12 lines
of its own single main class `[measured 2026-09-04]`. A per-module ratchet would have let the
entire integration suite be deleted for free. The full suite took 9 min 09 s across 75 projects
with 8 workers.

This also corrected the premise of the whole exercise: **the core was not un-netted, it was
un-measured.** The "no net" read came from a 12 % test-file ratio. The real number was 55.63 %.

**Mutation testing.** The mutation engine was wired, scoped narrowly to the aggregator module
while the net was small. Two traps: the Gradle plugin at 1.15.0 recurses to a `StackOverflowError`
auto-injecting the JUnit platform launcher (fixed by adding the launcher by hand and disabling
the auto-injection), and versions below 1.20 hit the same Java 25 bytecode wall as the coverage
agent. Pinned to 1.30.0 with the JUnit 5 plugin at 1.2.3. Worth noting: **the package registry's
search API was stale**, reporting 1.19.1 as latest while the repository metadata XML said 1.30.0
`[measured 2026-09-04]`.

**The first characterization net.** Target: the price recalculation service, chosen because its
verification logic compares 20 money extractors across two states as chained inequality tests,
which is the shape mutation testing punishes hardest. 51 test cases in one 912-line file, mocked
collaborators, no database. Class line coverage 1/238 to **238/238**; mutation **68 of 68 mutants
killed, up from 0**; aggregate coverage 55.63 % to 56.05 % `[measured 2026-09-04]`. Production
source and build files untouched.

The suite **locked a real bug rather than fixing it**: a compound field populated from the wrong
source, asserted as-is with an explanatory comment. That is what a characterization net is for.

Two targeting claims from earlier the same day had to be retracted. The main service module's
0 of 1,312 lines looked like the biggest money hole; 1,031 of those lines are demo-data seeding
active only in local profiles, and the rest is shutdown plumbing and actuator endpoints, so 0 %
is roughly correct behaviour there `[measured 2026-09-04]`. The earlier report had counted lines
without reading what they were.

**Self-provisioning test infrastructure.** A launcher-session listener in the shared test-support
module, registered through the service-loader manifest, starts a database container once per test
JVM before any test class loads. Zero existing tests or base classes changed. Verified in both
directions with the external database stopped: passes with the flag, fails without it
`[measured 2026-09-04]`. The default no-flag path is untouched.

The message-broker container is **blocked**: the library injects its starter script after
container creation, the file never arrives, and the container sits in its wait loop with empty
logs until the readiness probe times out. Ruled out by measurement: image (started by hand it
reaches the awaited log line in about 20 s), wait string, timeout, reuse, entrypoint, and two
broker major versions. Database containers work on the same host `[measured 2026-09-04]`. Failure
is deliberately non-fatal and the broker smoke test skips itself.

A second, independent blocker sits behind it: every test profile group in the shared test
configuration pulls in an exclusion that removes the messaging auto-configuration, so **no test
context in the repository talks to a broker at all**, and the asynchronous choreography is
untested by construction `[measured 2026-09-04]`.

**Two environment traps**, each costing a failed full-suite run: a stock `max_connections` of 100
is below what 8 parallel workers need, and a native frontend dependency with no binary for the
developer architecture compiled from source, needing an older interpreter twice over. That npm
failure silently took down two test modules including the 19-file cross-module money-lane suite,
and the continue-on-failure flag reported it only as an unrelated package error
`[measured 2026-09-04]`.

**One hazard to a neighbouring system.** The build defaults its test datasource and a schema-reaping
task to the standard database port on localhost, which on this machine belonged to kvart's
database. Two bare runs wrote schemas into it, and the reaping task drops every test-looking
schema older than 24 hours in whatever database it reaches. Both schemas were dropped, the
neighbour verified back to stock, and a dedicated container on a non-default port plus a
mandatory port flag became a hard rule `[measured 2026-09-04]`.

## 2026-09-04: the money-surface retier

The module-level money tiering was wrong at its granularity. The aggregator module carried the
bulk of the money logic and was not flagged at all, and the proof was measurable: fully netting
the price recalculation service moved the module-level money metric by 0.17 points, because the
metric could not see it `[measured 2026-09-04]`.

Replaced by a per-class and per-package tier spec with two tiers: **transaction** (wrong code
moves wrong money, named-human outcome sign-off) and **reporting** (wrong numbers get shown or
paid on, lighter gate).

| Surface | Lines | Coverage |
|---|---|---|
| Old, module-level | 5,398 | 48.0 % |
| New, transaction tier | 22,143 | 61.87 % |
| New, reporting tier | 8,224 | 42.98 % |

The module view could not see roughly **16,700 lines of money code** `[measured 2026-09-04]`.

The resolver **self-tests its own tier predicate on 15 cases, true and false, and withholds every
number if any case misclassifies**. It exposed two traps while doing so: whole-moduling the main
service module put demo fixtures at the top of the money gap list, and the tier globs match the
**bytecode package, not the directory**, where exactly one file in 4,317 disagrees
`[measured 2026-09-04]`.

## 2026-09-04 to 09-05: the structural ratchets

Nineteen checks, each a ratchet over a baseline taken on adoption day, attached in a **throwaway
detached worktree, never a live tree**, because the attach step writes an agent settings file
containing hooks, which is a supply-chain tripwire. The resulting diff was inspected: exactly two
hooks, both invoking the gate, nothing else `[measured 2026-09-04]`.

- **It caught real debt on its first honest run.** The default base reference was `origin/main`,
  81 commits behind the real default branch, so the duplication gate judged 19,431 lines as
  changed and reported **557 clone pairs**. Pointed at the real base: **6**, all genuine
  copy-paste in the characterization test written earlier the same day `[measured 2026-09-04]`.
  A 100 % mutation score had said nothing about copy-paste. Five were extracted into helpers, and
  51 tests plus 68/68 mutants were re-verified afterwards by the orchestrator rather than taken
  from the subagent.
- **Changed-line coverage needed a converter.** The ratchet reads LCOV or Cobertura; the build's
  coverage plugin emits neither. A converter over the aggregate report, cross-checked against the
  coverage tool's own totals (33,371 / 59,534 = 56.05 %, zero unresolved), wired it. The 0.8
  threshold applies to changed executable lines, not to a repo floor `[measured 2026-09-04]`.
- **Baselines preserved next to the configuration**: 245 escape sites, a 14.74 % duplicated share.
  Without them, re-attaching regenerates the baseline from whatever the tree looks like that day
  and the ratchet silently resets looser.
- **Run the post-flight form.** The bare gate invocation runs preflight checks only, so
  changed-coverage and its derived metric are silently absent. 4 gates versus 5
  `[measured 2026-09-04]`. This was briefly mistaken for a broken configuration.

## 2026-09-04: the layering gate

The generic layering checker did not fit, because it models layers as directories under a root,
not as 75 build modules. The authoritative layering fact here is the **declared build dependency**,
so the rules were written as convention regexes over every module's build file.

| Rule | Roots | Violations |
|---|---|---|
| an `-api` must not depend on any `-impl` | 33 | 0 |
| an `-impl` must not depend on a sibling `-impl` | 27 | 0 |
| nothing may depend on a `*-service` | 72 | 0 |

Zero production violations and zero production cycles, so the gate ships with no exemptions and
no baseline file `[measured 2026-09-04]`. Every future site is a decision, not inherited debt.

**The near-miss.** The first measurement reported 7 violations of rule 2. Every one was a
test-scope dependency, which is legitimate, and a regex conflating the scopes would have fired on
seven innocent lines on day one. The patterns were re-anchored so test scopes cannot match, then
**validated on 10 cases (4 must match, 6 must not)** before being wired `[measured 2026-09-04]`.

Proven by injection in a throwaway worktree: each rule fires naming file, line, rule, offending
text and reason; a test-scope dependency stays green as a negative control; revert leaves no
residue. The failure message **refuses to tell the agent how to whitelist the site**, saying that
accepting one into the baseline is a policy decision for a person `[measured 2026-09-04]`.

Graph facts worth keeping from the same measurement, production configurations only: the
aggregator module depends on 54 projects including 21 implementation modules, and 10 modules
depend on it, so it is the god/aggregator node. Highest fan-in is a shared commons module at 69.
Module kinds: 33 api, 27 impl, 4 service, 8 other `[measured 2026-09-04]`.

## 2026-09-05: the complexity ratchet

The last structural gate. Baseline: **94 functions over the ceiling out of 10,679 judged, 31 of
them on the money transaction tier and 27 on reporting** `[measured 2026-09-05]`.

The raw number was 407. 267 were vendored static JavaScript (a jQuery bundle at 71 findings, a
typeahead bundle at 21, a highlighter at 21, plus others), excluded because it is third party,
never refactored, and bumping a vendored library would fail the gate. That was 66 % of the raw
findings. Test trees were excluded too, because the verification-net turn exists to grow the test
layer and a gate that fails new tests fights its own purpose. Cross-check: the backend-only subset
came to exactly 128, matching a figure measured before the analyzer was installed.

**The tooling trap.** The package manager's `lizard` formula is a compression library. The
analyzer is a different project that installs a binary with the same name, so the wrong tool
answers to the right name and the gate reads nonsense instead of erroring. The gate invokes a bare
`lizard` with no configurable path. Also, the distribution's analyzer build was 17 days old,
inside the 30-day release-age rule, so it went in as a pinned virtual environment on the previous
version instead `[measured 2026-09-05]`.

Proven by injection: a complexity-11 method added to the payments implementation module fails by
name and line, and the gate refuses to accept it as anything but a person's decision.

## 2026-09-05: the duplication false positive, measured and left red

One gate stays red on purpose. A six-line block of identical static test imports appears in two
test files. Imports cannot be extracted, and the tool has no accept path for clones in changed
lines.

The proposed fix, feeding it a token-based duplication report instead of the built-in line-based
finder, was installed (pinned, isolated, with install scripts disabled) and measured. **It makes
it worse: 5 clone pairs against the built-in finder's 1**, all import blocks either way. And no
token threshold separates the classes, which is measured rather than assumed: across 3,468 clones,
import blocks (1,749; min 50, median 62, max 308) and real code clones (1,719; min 50, median 69,
max 10,199) overlap, so at 150 tokens you still catch 17 import blocks while discarding 90 % of
the real clones `[measured 2026-09-05]`. Configuration reverted to the built-in finder.

The gate is left failing rather than loosened. The honest fixes are upstream, or waiting: those
lines stop being changed lines the moment the branch merges, so the gate self-clears, which only
matters because this loop gates feature branches **before** merge.

## 2026-09-04: the sandbox boot

The devcontainer sandbox booted and its boundary was proven rather than assumed.

- **Egress is genuinely enforced.** Allowlisted host returns 200; a non-allowlisted host fails at
  the gateway (curl 56); stripping the proxy environment to go direct fails with no DNS and no
  route (curl 6), because the workload sits on an internal network with no network-admin
  capability `[measured 2026-09-04]`.
- **The build works through the gateway**: both JDKs installed and registered, Gradle downloads
  its own distribution and configures all 75 projects.
- **Hard constraint: the sandbox cannot run in a git worktree.** The worktree's `.git` is a file
  pointing at an absolute host path outside the mount, so every git command fails and the
  post-create step dies at exit 128 on its first `git config`. Sandboxed repos must be real
  clones, which collides with the loop's own worktree-per-turn isolation, so it is one or the
  other per turn. A local hardlinked clone took 0.7 s for a 135 MB git directory
  `[measured 2026-09-04]`. The pre-push guard was re-installed in the new clone and verified
  firing.
- **Container-based test infrastructure cannot work inside the sandbox**, by design, since there
  is no Docker socket and no Docker CLI. The sandbox path is a compose sidecar database instead,
  which is arguably better: internal-only, no egress, no socket handed to an agent.
- **Blocked on identity.** The build cannot resolve its private Maven packages inside the box:
  `Username must not be null!`, which is authentication, not the allowlist, since the host is
  reachable `[measured 2026-09-04]`. The shared cache volume is machine-wide, so a personal token
  is the wrong answer. A scoped bot identity, read access to contents and packages and nothing
  more, is the owner's decision, and without it **there is no autonomy in the box because the box
  cannot build the repository.**

Smaller boot findings, all recorded or fixed: the sandbox CLI reuses running containers so an
override edit is silently ignored until a forced recreate; the example sidecar image version
drifted from the CI image version and its stock connection limit was too low (both corrected in
the override slot); the lock file had no entry for one feature so it resolved unpinned every boot
(pinned); and the environment check script reported a missing memory CLI as "expected, installed
at post-create" when nothing installed it, so memory reconcile was silently skipped
`[measured 2026-09-04]`.

## State as of 2026-09-06 and 09-07

Everything local. Nothing pushed to any group repository. The pre-push guard is present on the
primary checkout and on the sandbox clone, both verified firing.

**Green:**

- Verification net complete: coverage ratchet, aggregate report, mutation gate, first
  characterization net, self-provisioning database. Aggregate coverage **56.05 %**.
- Structural ratchets configured with baselines, 7 gates.
- Layering gate: 3 rules, 0 violations, no exemptions.
- Complexity ratchet: 94 of 10,679 baselined.
- Money surface retiered per class: transaction **13,699 / 22,143 = 61.87 %**, reporting
  3,535 / 8,224 = 42.98 %, with a self-testing predicate.
- Sandbox booted, egress boundary proven.
- The same ratchet layer was adopted on the reference implementation as a cross-check: 7 gates,
  all green, about 3.1 s, 3 layering rules derived from its own structure rules, complexity 697
  of 5,771 baselined. Its cross-vendor review of that adoption ran about 9 minutes over a
  24,914-insertion diff and returned 14 findings, **13 of them in the vendored tool's own source**
  and 1 real in the configuration: a one-keystroke indented-import bypass, which was closed
  `[measured 2026-09-06]`.

**Known failing, deliberately:** the duplication gate, one clone pair, the six identical static
test imports. See above for why loosening it was refused.

**Blocked:** the message-broker container (plus the profile finding behind it), and the scoped bot
identity, which blocks autonomy in the sandbox.

**One correction issued on 2026-09-06** and worth restating, because it is the failure mode
every adoption will hit: a red complexity gate on the reference implementation had been written
off as "a bootstrap issue, not a feature defect". Verified: the function **is** in the baseline at
complexity 10 across 48 lines, and on the default branch it is complexity 15 across 100 lines. The
ratchet was flagging baselined debt that had doubled. It was a real regression, not an artifact of
when the baseline was taken `[measured 2026-09-06]`. Baseline membership means "this much was
accepted", never "this file is exempt".

---

## Traps that cost an hour

| Symptom | Cause | Fix |
|---|---|---|
| Coverage report fails with `Unsupported class file major version 69` | Coverage agent too old for the JDK's bytecode | Coverage agent 0.8.14 or newer; the mutation engine needs 1.20 or newer for the same reason |
| Repo coverage reads ~19 points low | Per-module reports credit only the owning module, so cross-module suites score nothing | Gate on the merged aggregate report, never on the per-module sum |
| Aggregate coverage silently wrong after a targeted run | A filtered test run with a rerun flag overwrites the module's execution data with only the matched class | Re-run the full module test task before trusting any aggregate number |
| Duplication gate reports 557 clone pairs on a clean tree | Base reference defaulted to a branch 81 commits behind the real default | Set the base reference to the actual default branch |
| Changed-line coverage gate silently absent | The bare gate invocation runs preflight checks only | Run the post-flight form |
| Changed-line coverage will not attach at all | The ratchet wants LCOV or Cobertura; the build's coverage plugin emits neither | A converter over the aggregate report, cross-checked against the tool's own totals |
| Complexity gate reads nonsense instead of erroring | The package manager installs a compression tool that owns the same binary name as the analyzer | Verify `lizard --help` names the analyzer; install the analyzer pinned, in an isolated environment |
| Layering rule reports 7 violations on a clean graph | The regex matched test-scope dependencies as well as production ones | Anchor on production configuration names only, and validate on true and false cases before wiring |
| A cross-module test suite vanishes from the run | A native frontend dependency failed to build and the continue-on-failure flag reported it as an unrelated package error | Compare executed test tasks against the module list before trusting coverage |
| One module dies with "too many clients" | Stock database connection limit below what parallel workers need | Raise it in the dedicated test container |
| Another project's test schemas disappear | The build defaults its datasource and its schema-reaping task to the standard port, and the reaper drops old test schemas in whatever database it reaches | Dedicated container on a non-default port, passed on every invocation, plus a post-run isolation check |
| Container library compiles against one major version and runs against another | An old pin on module coordinates the framework BOM already manages, across a major-version rename | Do not pin it; use the current module names with no version |
| Message-broker container up, logs empty, readiness times out | The library never delivers the starter script it injects after container creation | Unresolved; failure made non-fatal and the smoke test skips |
| Every git command in the sandbox fails with `not a git repository` | The workspace is a worktree whose `.git` points at an absolute host path outside the mount | Sandbox real clones only |
| A fresh clone can push despite the local-only rule | Git hooks do not travel with a clone | Re-install the guard in every clone; put anything that must hold everywhere in managed settings or CI |
| Sandbox override edits appear to do nothing | The sandbox CLI reuses running containers | Force-recreate the affected service |
| Memory reconcile never runs in the sandbox | The environment check reports the missing CLI as "expected, installed at post-create" when nothing installs it | Verify that a boot check's excuse for a missing component is true |
| Parallel doc-generation agents overwrite each other | Agents told to "explore in parallel" spawned write-capable forks racing on the same files | Prompt: sole writer, read-only helpers, one writer per file |
| A dependency looks a version behind | The package registry's search API was stale against its own repository metadata | Read the metadata, not the search endpoint |

## Decisions that were waiting on the owner

Stated generically, because these are the ones every legacy adoption ends up parked on. None of
them is an agent's to make.

1. **A scoped bot identity** (read access to contents and packages, nothing more). Without it the
   sandbox cannot resolve the private packages, so it cannot build the repository, so there is no
   autonomy in the box. This is the top blocker, and it arrived as a hard blocker rather than the
   nice-to-have the design had assumed.
2. **Lifting local-only.** Every remote write was blocked for the whole window. Lifting it is what
   creates the real team-context remote, allows a PR, and unblocks SHIP and LEARN, meaning both
   write-backs, meaning the flywheel edge itself.
3. **CI and merge authority** on the core: whether the operator holds it or it routes through the
   owning team. Gated behind local-only anyway, but it decides where the turn runner lives.
4. **The backend-language review rule pack**, which does not exist upstream and must be authored
   and adopted there rather than kept local. The first feature turns are what seed it.
5. **Evals on agent configuration.** Every gate built in this window points at the code; none
   points at the machine that writes the code. Gating changes to the agent contract, rule packs,
   repo agent files and skills behind an eval suite, with each incident becoming a permanent eval,
   is the named gap and the highest-leverage remaining item.

Smaller ones that were also a person's call, and are recorded because agents kept wanting to
decide them: installing each new gate tool (each one is a dependency decision under the 30-day
release-age rule), and whether to loosen the duplication policy to clear the one red gate. The
answer to the second was no.
