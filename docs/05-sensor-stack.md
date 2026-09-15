# Sensor stack

Four mechanical, model-free layers around every change, in the agent's own loop, before any
model reviews anything. Together they substitute for the human eyes a software factory removes.
Each is deterministic, near-zero cost per run, and produces structured output a person or a
dashboard can read.

| # | Layer | When | Catches | Tool used here |
|---|---|---|---|---|
| 1 | Orientation map | pre-write | the agent not knowing what it is touching: call graph, blast radius, existing exemplars | ripwire |
| 2 | YAGNI ladder | during write | over-building: code that should be a stdlib call, a platform feature, one line, or nothing | chisle |
| 3 | Quality ratchets | post-write, Stop hook | complexity growth, escapes, duplication, dead symbols, layering, changed-line coverage, public API loss | cleat |
| 4 | Architecture diff | post-write, Stop hook | layer violations, cycles, scope spillover, cross-repo seams: what THIS change did to structure | enola |
| 5 | Cross-vendor review | pre-push | intent, security, design, novel risk: the only inferential layer | consort, see [06](06-verify-gate.md) |

Ordering rationale: the reviewer is the most expensive resource, and a review of code that a
ratchet would have failed is waste. Adoption order when starting from nothing: ratchets first
(simplest integration, immediate value), architecture diff second, the two pre-write layers
last (they are builder ergonomics, not gates, and stay off the critical path).

Every tool here is third-party and open source. The decision is the composition and the
placement, not the tools. Swap any of them for an equivalent that has the same property:
deterministic, baselined, fails with file and line, refuses to explain how to loosen itself.

Where each layer fires inside a single agent turn:

```mermaid
flowchart TB
    START(["turn starts"])
    subgraph PRE["before a line is written"]
        M1["1 · orientation map<br/>ripwire"]
    end
    subgraph WRITE["while writing"]
        M2["2 · YAGNI ladder<br/>chisle"]
    end
    subgraph STOP["Stop hook: the agent cannot call it done"]
        direction TB
        M3["3 · quality ratchets<br/>cleat"]
        M4["4 · architecture diff<br/>enola"]
    end
    subgraph PUSH["before the push"]
        M5["5 · cross-vendor review<br/>consort"]
    end
    DONE(["PR opens"])

    START --> M1 --> M2 --> M3 --> M4 --> M5 --> DONE

    classDef mech fill:#e8f3ec,stroke:#2f6b3f,stroke-width:1.5px,color:#14181b;
    classDef inferential fill:#e9f2f3,stroke:#0d5f68,stroke-width:2px,color:#14181b;
    classDef ergo fill:#fdf1e3,stroke:#c2610c,stroke-width:1.5px,color:#14181b;
    classDef ends fill:#f2f4f4,stroke:#5d686d,stroke-width:1px,color:#14181b;
    classDef frame fill:#00000000,stroke:#aab6b8,stroke-width:1px,color:#5d686d;
    class M3,M4 mech;
    class M5 inferential;
    class M1,M2 ergo;
    class START,DONE ends;
    class PRE,WRITE,STOP,PUSH frame;
```

Layers 1 and 2 are amber because they are ergonomics: they change what the agent reads and
writes, they never refuse. Layers 3 and 4 are the mechanical gates. Layer 5 is the only
inferential one.

The chain is drawn straight, but layers 3 and 4 do not return to the caller on failure: a red
Stop-hook gate is not a report a person reads later, it is handed straight back to the agent as
the next thing to fix, and the turn does not end until it is green or a person has accepted the
site into a baseline. That hand-back is the whole reason a ratchet in the agent loop is worth
more than the same check in CI.

What is wired where, as of 2026-09-07:

| # | Layer | Checks in use | kvart | The legacy core |
|---|---|---|---|---|
| 1 | ripwire | symbol and call-graph rank, project MCP server, skill exfiltration scan | wired, index unverified across worktrees | not wired |
| 2 | chisle | plugin at project scope, marketplace source pinned to tag v3.0.0; ladder, prose ruleset, tool-output elision | wired 2026-09-10 (replaced ponytail), no trial on a complex task yet | not wired |
| 3 | cleat | escapes, duplication, complexity, layering, changed-line coverage, conventions, test hygiene, doc size, public API loss | 6 gates on main, 4 sites accepted into the baselines | ratchets adopted, 0 layering violations, no exemptions |
| 4 | enola | layers, cycles and intent (provable); scope spillover and cross-repo seams (heuristic) | wired, 12 module-level crossings pinned; Stop check on the three provable explainers, blocks once | not wired |
| 5 | consort | Codex backend, Gemini backend, blind security side-pass, browser QA pass (CLI-driven, headless, per-persona sessions, see adr/0008), rule packs | 3 runs, 4 real defects; QA runtime shaken down 2026-09-10 | measured |
| 5a | e2e receipt gate | scoped browser QA, receipt per git tree, pre-push check | wired `[measured 2026-09-09]` | not wired |
| 5b | sonar receipt gate | local SonarQube scoped by changed sources, receipt per tree plus project set | built, not yet exercised end to end `[designed 2026-09-09]` | not wired |
| 3a | fail-on-base check | new or changed tests red on the merge base with the branch's tests applied, green on the branch, exemptions declared, failure kind recorded | not wired; the gate report's `red-before` row is a hand step `[proposed]` | not wired |

The provable and heuristic split in layer 4 matters for gating. Only `layers`, `cycles` and
`intent` report at confidence 1.00, so those three are the recommended starting gate; the rest
need a confidence floor before they can refuse anything.

## Layer 1: orientation map (pre-write)

A deterministic index of the codebase (symbols, call graph, co-change, ownership) that answers
"what am I touching, who calls it, what already does this" in a few hundred tokens instead of a
fan-out of whole-file reads. Less context is measurably more accurate, not just cheaper: code
repair accuracy fell from 29 % to 3 % as context grew from 32K to 256K tokens in one benchmark
`[field: LongCodeBench, as cited by the tool]`.

Reflexes it installs: rank before reading; expand one symbol rather than open its file; check
for an exemplar before writing a new helper; run a quality delta before calling work done.

Caveats before production adoption: keyword retrieval can miss domain vocabulary (verify on real
tasks with the project's identifiers); confirm the index behaves in a worktree-per-agent
layout, because that is exactly the 3 to 5 trees-per-operator pattern the factory runs
`[designed]`.

## Layer 2: YAGNI ladder (during write)

A 7-rung decision ladder the agent climbs before writing code: does this need to exist; is it
already in this codebase; does the stdlib do it; does the platform do it; does an installed
dependency do it; is it one line; only then, the minimum that works. Security, validation, error
handling and accessibility are never on the chopping block.

Tool: chisle, which replaced ponytail on the reference implementation on 2026-09-10. Same
ladder, two additions. It compresses the agent's prose with a ruleset injected at session start,
and it adds an input-side hook: after a tool call, oversized output (over 8,000 characters) has
its middle elided, keeping 60 head and 40 tail lines plus up to 12 error-like lines, and a
byte-identical repeat of an earlier output becomes a marker. Read and Edit results are never
touched, so exact bytes still feed later edits. The kill switch is an environment variable
(`CHISLE_COMPRESS=0`).

Why the swap: the ladder was the reason for adopting ponytail, and chisle carries the same
ladder with a smaller, rarer downside on the vendor's 20-task comparison (billed output tokens as
a share of the no-tool baseline): ponytail 68 % total, 8 of 20 tasks worse than no tool, 227 %
worst case; chisle 52 % total, 1 of 20 worse, 173 % worst case `[field: chisle docs/comparison.md]`.
One vendor benchmarking the other on generic prompts: read it as a smaller worst case, not a
promise. Under a subscription model less code compounds: less future agent work per feature.

Caveats: "made my agent lazy" stays a real risk on complex domain tasks, the ladder is unchanged;
the plugin ships three Node.js lifecycle hooks (session start, prompt submit, post tool use),
read in full before adoption: no child process spawn, one 1.5 s update check against the npm
registry at session start with an environment variable to disable it, state files only under the
Claude config directory; the marketplace format accepts a tag or branch, not a commit, so the pin
is the tag v3.0.0 (released 2026-07-28), and the cached plugin content was verified to match that
tag's commit rather than the branch head; a tag can move, so a fork or the organisation's vetted
catalog remains the real pin. Tool-output elision is a context-cost mechanism, not a sensor: it
changes what the model reads, and a compressed result that hid an error line the agent needed
would be a new failure class, not yet observed `[designed; trial on one complex multi-file task
before rollout]`.

## Layer 3: quality ratchets (post-write)

The load-bearing layer. Nineteen checks, each a ratchet: the baseline records the debt present
on adoption day, and new debt fails. Wired as a Stop hook (the gate runs when the agent stops,
and a failure is handed back as the next thing to fix) and a PreToolUse guard (the agent cannot
edit the policy, the baselines or the hooks).

Gates used on kvart and the legacy core: doc-size (a document an agent reads growing past its
ceiling), test-hygiene, escapes (`# type: ignore`, `any`, `|| true`, `.skip`, keyed by site),
conventions (your own regex rules, your message at the site), duplication (a copied block in
changed lines), complexity (cyclomatic over 8 or 60 lines), layering, changed-coverage (changed
lines the tests did not run, minimum 0.8), public-api.

Rules that are not obvious until you have been bitten:

- **The failure names the fix, never the whitelist.** "Accepting a site into the baseline is a
  policy decision for a person." The agent block in the instructions forbids editing the policy
  to satisfy the gate, and the guard enforces it.
- **Baselines are tied to a tree state.** Adopting the gate onto a newer main legitimately
  requires re-cutting the baseline once, as a deliberate act by a person, recording main's real
  day-one debt. kvart's re-cut named 4 accepted sites in the commit message
  `[measured 2026-09-07]`.
- **`base_ref` must be the real default branch.** Pointed at a branch 81 commits behind, the
  duplication gate judged 19,431 lines as changed and reported 557 clone pairs; pointed at the
  right one, 6, all real `[measured 2026-09-04]`.
- **A repo-supplied `base_ref` can blank every ratchet.** A base_ref set to HEAD makes the diff
  against itself empty, so under strict CI every ratchet passes on nothing. Rule: in CI under
  `--strict`, ignore a repo-set base_ref and resolve the merge base against the default branch
  yourself. Check: the diff the ratchet measures is non-empty when the change is non-empty. Found
  by the blind security side-pass, open upstream `[measured 2026-09-09]`.
- **Exclude vendored static assets and, on an un-netted core, test trees.** 267 of 407 raw
  complexity findings were vendored JavaScript; a gate that fails new tests fights the turn whose
  purpose is to grow tests `[measured 2026-09-05]`.
- **Walkers must honour the ignore file, or nested worktrees poison the tree.** The agent runtime
  nests other branches' worktrees under the repo; the walkers pruned by directory name and read
  every nested tree, sending 3 of 6 gates red in the primary checkout. Config-only fix, proven
  with planted files `[measured 2026-09-07]`.
- **The guard is a speed bump, not a wall.** `python3 -c` walks past a PreToolUse guard. The
  control is branch protection; the guard exists to make the honest path the easy path.
- **Line-based clone detection flags import blocks.** A token-based finder was measured and made
  it worse (5 pairs vs 1), and no token threshold separates import blocks from real clones
  (overlapping distributions, p50 62 vs 69). The real fix is upstream: skip import lines. Do not
  raise `min_lines` `[measured 2026-09-05]`.
- **The right tool must answer to the right name.** A package manager installed a compressor
  under the complexity analyzer's binary name; the gate would have read nonsense instead of
  erroring. Verify with `--help`; pin the analyzer in a venv `[measured 2026-09-05]`.
- **A Stop hook reports a failure set once.** The gate re-sent its whole report on every stop,
  so a failure the agent could not fix (a policy question for a person) cost the agent its
  context every turn. Fixed at source: the report that blocked is fingerprinted, an identical
  report on a later stop gets one line and exit 0, and a stop that is already a continuation
  reads the same way. Any change in any gate's output is a new report and blocks again
  `[measured 2026-09-07]` (fork `3dc0569`, vendored back in kvart #23).
- **A formatter pass is not a change.** Two commits of pure formatter output tripped the
  duplication gate with 25 clone pairs and the scoped complexity gate with 80 test functions,
  none of them new. The fix judges a clone under changed lines new only when the base lacks a
  copy (whitespace, brackets, commas and colons removed; occurrences counted per file), and a
  scoped run keeps its exclude globs. 25 pairs to 0 with the 25 real ones held; 80 functions to 0.
  `--ignore-all-space` was tried and dropped: it hid indentation-only edits, which are semantic
  in Python, and bought 8 % `[measured 2026-09-07]` (fork `6585f44`..`006043b`).
- **A gate that cannot fail is not a gate.** Running the whole local wheel on main found three:
  the architecture Stop hook carried no policy and exited 0 on a planted layering violation,
  the container scanner exited 0 by default, the static-analysis upload never waited for its
  quality gate. All three now fail; the wheel prints PASS, FAIL or SKIP with a reason for each
  of its 12 gates `[measured 2026-09-07]` (kvart #22).
- **A pre-push gate must read the ref list.** kvart's hook runs the full gate on a pure
  `--delete` push, so a branch cleanup was blocked by a complexity gate that had nothing to
  measure. Open `[measured 2026-09-07]`.

What it caught for real: 2 new escape comments and a function over 60 lines in a hands
implementer's first pass `[measured 2026-09-05]`; 6 genuine copy-paste blocks in a
characterization test that had a 100 % mutation score `[measured 2026-09-04]`; a baselined
function that had doubled on main `[measured 2026-09-06]`.

Consort review of the vendored ratchet source itself produced 17 findings in 20 min 19 s: 2
real in the adopter's config (an argv injection via a changed path beginning with `-`, a
`MULTILINE` anchor baselining an empty-text site), 11 product defects deferred upstream
`[measured 2026-09-07]`. A gate is code too and gets the same review.

The tool is a third party's MIT repository, so the fixes travel as fork and pull request, and
the project refreshes its vendored copy only from a fork branch. Same day: upstream
`svetdev/cleat#6` (the flag-shaped path refusal, the analyzer's working directory, attach's
hook detection); a second fork batch of 5 commits (the once-per-failure-set report, the
formatter-pass judgment, an option injection via a `-`-shaped base ref from the config,
found by the blind security pass) gated by both review legs plus a second Gemini leg, vendored
into kvart (#23), no upstream PR yet `[measured 2026-09-07]`.

### Receipt-checked pre-push gates

A general rule for a check too slow to sit on the Stop hook: run it once before the push, write a
receipt keyed by the git tree id, and have the pre-push hook check the receipt. The receipt records
that the gate ran green on this exact tree, and any later commit voids it. The receipt is never an
authorisation token: it cannot be hand-written to satisfy the hook, because it is bound to a tree the
gate actually produced. Check: the pre-push hook reads the receipt and the tree id it names before
letting the push proceed `[measured 2026-09-09]`. Two of these run on kvart, the browser QA gate and
the static-analysis gate, both detailed in [06-verify-gate](06-verify-gate.md). The fail-on-base check
below takes the same shape when its tests need the database.

### Mutation kill rate as a ratchet on the touched modules

Coverage is the ratchet layer's only test-strength signal, and it is gameable by construction: a
test that calls the function and asserts that something came back covers every line and notices
nothing. Machine-written tests do this by default (see [09-legacy-adoption](09-legacy-adoption.md)
§2, where mutation score, not coverage, was the exit gate for generated characterization tests).
On the reference implementation the same shape showed up in the human-era suite: the service
layer's whole-module kill rate was 30.3 % on the database-free modules and 39.9 % on the
database-coupled ones, with the largest billing module at 11.2 % and the platform billing module
at 31.3 % `[measured 2026-09-15]`, next to a changed-line coverage gate that had passed every PR.
Two failure modes, told apart by the module's own coverage: assertion theatre (coverage 64 to
100 %, kill rate 13 to 35 %: nine modules, one of them the passkey service, one the platform
billing service) and unit-coverage gaps (coverage 3 to 17 %, the module lives on integration
tests). Only the first condemns the tests.

Design, `[proposed]` on kvart with the baseline `[measured 2026-09-15]`:

- **Scope by the diff, like every other slow gate.** Mutation runs the suite once per mutant, so
  the whole repository is hours (47,124 mutants across 140 modules on the reference
  implementation). The gate mutates only the source modules the diff touched, with the tests the
  test-selection map names for them, and writes a receipt keyed by the tree id (see above).
- **A baseline per module, one writer, tightened only by the tool.** The campaign's CSV is the
  day-one baseline: killed, survived, not exercised, total, per module. The gate refuses a drop
  in killed over total on a touched module and accepts only a rise, the same `--tighten` shape as
  the other ratchets (adr 0004). A person re-cuts the baseline; the agent cannot edit it.
- **Killed over total, never killed over checked.** The not-exercised column stays in the
  denominator, or a module that no test reaches reports 100 %.
- **Money and identity modules get a target as well as a ratchet.** Tiering per class
  ([12-adoption-playbook](12-adoption-playbook.md)) already sets mutation targets for the money
  lane; a module at 11.2 % gets a named hardening ticket, and "did not get worse" is not a pass.
- **Generated tests must earn their kills.** A build station that adds or changes tests ships
  them with the kill rate on the touched module, and the station's exit check is that number, not
  coverage. This is principle 3 applied to the artefact the loop produces most of.
- **The database-coupled half needs isolation.** Mutant runs in parallel collide on one shared
  test database and the scores are garbage. The measured fix: migrate a template database once,
  clone it per run (`CREATE DATABASE ... TEMPLATE`), gated behind a flag so the ordinary suite is
  untouched `[measured 2026-09-15]`. A fresh worktree must be able to do this itself
  ([09-legacy-adoption](09-legacy-adoption.md) §3).

Known limits: a kill rate says nothing about copy-paste (the 100 % module with 6 clones in
[13-failure-catalogue](13-failure-catalogue.md)), equivalent mutants inflate the survivor count
and are accepted by name, and async or time-dependent paths produce flaky kills that must be
excluded explicitly rather than retried into green. The gate is trusted only after it has refused
one real PR for a real drop (rehearse the blocked direction, below).

### Fail-on-base: every new or changed test is red on the merge base

Coverage is the known-true case and mutation the known-false case for the code. The change has
a known-false case too: the code as it was before the change. A test that ships with a change
and also passes on the merge base proves something that was already true; it is not a test of
this change, whatever its name says. The loop has had the rule since cycle 1 ("tests first, red
on the unfixed code") and the gate report has had a `red-before` row, and both were done by
hand: a fix reverted, a test rerun, a line written `[measured 2026-09-07]`. Principle 1 says a
rule is written twice, so this is the check. The measured cost of not having it is the trial's
MINOR: a behavioural test that only proved a function was unused, where a `list(...)` would have
passed `[measured 2026-09-05]`.

Design, `[proposed]`:

- **Select by the diff.** The test functions added or changed against the merge base, by file
  and node id, read from the diff itself; never a hand-named set (cycle 4's rule for the related
  set applies here too).
- **Run them at the base with the branch's tests applied.** A temporary worktree at the merge
  base, the branch's test files copied over it, then only the selected node ids run with the test
  cache disabled. Expected: every selected test fails. Then the same ids on the branch: every one
  passes. Two results per test, both recorded.
- **Record why it failed.** An assertion failure on the base is the strong witness: the test
  reached the behaviour and found it absent. A collection or import error (the test cannot load
  without the new module) is a weak witness: it proves the test needs the change, not that it
  detects it. The receipt shows the kind; a weak witness on a money, tenant or identity path is a
  finding, not a pass.
- **Exemptions are declared, never inferred.** Three legitimate cases pass on the base: a
  characterization test that locks existing behaviour on purpose (the legacy-core bootstrap in
  [09-legacy-adoption](09-legacy-adoption.md)), a test moved or renamed by a refactor, and a test
  added for a defect fixed by an earlier commit on the same branch. Each is named with its reason
  in the program design note (section 6) or the plan, and the check reads that list. An undeclared
  pass on the base fails the check. A test the diff deletes is reported on its own line every
  time: the quality floor forbids deleting a test to make new work pass, and this is where that
  becomes visible.
- **Where it fires.** On the Stop hook when the selected tests need no database or browser
  (seconds: the tests are the diff's own). Otherwise as a receipt-checked pre-push gate in the
  shape the browser and static-analysis passes use, on the self-provisioning test database. The
  receipt names the merge base, the node ids, both results per id and the failure kind.
- **Rehearse both directions before trusting it.** Plant a test that passes on the base and
  confirm the refusal; run a real red-first test and confirm the pass; declare a characterization
  test and confirm it is allowed with its label in the receipt.

What it is not: mutation. Mutation asks whether the existing suite notices a planted change in
the code; fail-on-base asks whether the new tests notice the change they shipped with. A change
can pass both and still be wrong (the trial's export was byte-identical and its shape was the
defect); that is the reviewer's job. Cost: the selected tests run twice plus one worktree
checkout; a handful of unit tests is seconds, the database-coupled ones the testbench's usual
minute. The check is trusted only after it has refused one real test for passing on the base.

### Rehearse the blocked direction

Rehearse the BLOCKED path of a gate, not only the pass: a gate that cannot fail is not a gate. Check:
a deliberately failing case must actually block before the gate is trusted. Three defects surfaced
only this way `[measured 2026-09-09]`:

- macOS bash 3.2 has no `mapfile`, so the scope came back empty and the gate could not fail.
- an empty array expanded under `set -u` aborted the FULL run in 0 s.
- the Compose project name defaulted to the worktree directory, so a worktree tried to start a
  second database container.

## Layer 4: architecture diff (post-write)

A snapshot of the codebase's structure (modules, symbols, routes, storage, dependencies) pinned
as a baseline before editing and diffed after. It reports only what the change did: findings
introduced or resolved, coupling added, a cycle spanning four files, a layer crossed the wrong
way. Nothing without a baseline can tell a regression you just introduced from the hundreds
already there, which is why this is not a linter and does not replace one.

Configuration is a layer declaration (kvart: entry → service → domain → models → foundation)
plus the existing crossings pinned as accepted. kvart's declaration pinned 12 module-level
crossings; the real one is nine service modules lazy-importing an authorisation helper from the
entry layer `[measured 2026-09-07]`. Every future crossing is a decision, not inherited debt.

Three explainers are provable (confidence 1.00): `layers`, `cycles`, `intent`. Everything else
is heuristic and needs a confidence floor to gate on. Out of the box it fails nothing; the
recommended starting gate is the three provable ones. The scope-spillover check
(`--target=<declared scope> --max-spillover=0`) is the mechanical form of "the builder stayed in
its lane" and doubles as the architecture gate a scaling factory needs
([11-scaling](11-scaling.md)).

Cross-repo: an intent file can declare seams between repositories, so a builder importing
across a service boundary without declaring the dependency fails even though build and tests
pass. The other layers do not cross repo boundaries `[designed]`.

Hooks: session-start snapshot, Stop diff, a doctor command that verifies the hooks actually
fired. Config is not execution; the doctor closes that gap.

The shipped Stop hook carries no policy: it exited 0 on a planted layering violation. kvart
replaced it with a script that runs `check --fail-on=layers,cycles,intent` from the project
root (the invocation directory is wrong from a subdirectory, where the gate silently disabled
itself), blocks the stop with the report on stderr, releases on the retry with one line, and
treats a check that did not run (no baseline, tool exit 2) as a block, not a pass. Seven
planted cases, clean tree 11 s. The first cut was a one-liner; the cross-vendor panel found
three real problems in that one line (no continuation handling, so an infinite block; tool
exit codes swallowed; the directory bug) `[measured 2026-09-07]` (kvart #24).

## Wiring, as measured on kvart

- Hooks live in the tracked agent settings file: PreToolUse guard, Stop (ratchet gate on changed
  files, then the architecture check on layers, cycles and intent), SessionStart (architecture
  snapshot). Every entry is
  PATH-guarded so it is a no-op where the binary is absent; nothing here runs in production
  images.
- Binaries per machine, pinned, in the user's local bin; the analyzer in its own venv.
- The settings file is a supply-chain tripwire, so it is tracked and its diff reviewed. The
  attach step wrote exactly two hooks, both invoking the gate; verified by diff.
- Two agent config directories exist on one machine (plain terminal vs the canvas runtime);
  a plugin registered in one is absent in the other.
- Rule files for layers 1 and 4 sit next to the other path-scoped rules and say when to reach
  for each verb. See [templates/sensor-config-examples.md](../templates/sensor-config-examples.md).

## What this stack is not

Not a replacement for the cross-vendor review. It is a prerequisite filter that reduces that
review's surface to the non-trivial problems, and it cannot see intent, security semantics or
design.
