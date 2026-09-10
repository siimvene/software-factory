# Inventory: concept to shipped source

Every mechanism this design names, and what actually provides it today. The design is a
composition, not a tool, so the honest question an adopter asks first is "which of this can I
install, and which do I have to write". This document answers it row by row.

Three kinds of provider appear in the tables:

- **Third-party open source**, named with its public repository owner and licence where the
  licence file is readable. These are installable by anyone.
- **The group standard**, meaning an organisation's own templates, rule packs and plugin
  catalog. An adopter without one substitutes the fourth column.
- **Local**, meaning a piece written for the reference implementation and not packaged. An
  adopter writes an equivalent, usually 20 to 200 lines.

Classes are the ones in [WRITING.md](../WRITING.md): `measured`, `designed`, `proposed`,
`field`. They describe the mechanism as used here, not the maturity of the upstream project.
Inventory taken 2026-09-07.

## 1. Operating contract

| Mechanism | What provides it today | Without an organisational standard | Class |
|---|---|---|---|
| The behavioural contract every session loads (identity, write paths, verification, quality floor, loops, memory, escalation) | the group standard: one managed markdown file, vendored into every repo, sentinel-marked | write it once from [03-operating-contract](03-operating-contract.md); it is about 150 lines and it is the cheapest artifact in the design | measured |
| Distribution of that file to every repo, and drift detection when a repo edits it | the group standard's adopt script plus a fleet drift report | a vendored copy per repo and a CI check that the sentinel block matches upstream | measured (vendoring) / designed (fleet report) |
| Enforcement tier above local hooks | managed settings at the organisation level in the agent runtime | branch protection on the git host is the only tier a solo owner has | measured (where an org plan exists) |
| Path-scoped rule files that load when a matching file is read | the agent runtime's own rules mechanism plus a lean root instructions file | the same mechanism; the work is splitting the root file honestly | measured |
| An eval suite that runs when the contract changes | nothing | nothing exists to adopt; this is the design's named biggest gap | proposed |

## 2. Knowledge plane

| Mechanism | What provides it today | Without an organisational standard | Class |
|---|---|---|---|
| Repository context standard: four knowledge layers, required layout, conformance levels L0 to L2, an idempotent adopt script with dry-run and check modes, a version lock file | the group standard, in its own repository | copy the layout from [04-knowledge-plane](04-knowledge-plane.md) and [17-onboarding](17-onboarding.md); the adopt script is a convenience, the layout is the standard | measured (L0 adoption) / designed (L2 docs-lint) |
| Team-context repo scaffold: front door instructions with a filled example, CODEOWNERS routing specs and memory to different owners, numbered decision-record folder | the group standard's team-context template | this repository's [templates](../templates/) plus a CODEOWNERS file; four files total | measured |
| Current-state specs generated from code, and kept current per commit | a plugin in the group's plugin marketplace: three skills, retro-generate from a codebase, update-specs-for-commits, and a checker that the specs' cited paths resolve in the checked-out tree | the retro-generation prompt is the whole product here; an adopter writes three prompts and a path checker. The checker is the part that must be mechanical | measured |
| Memory engine: typed claims (fact, decision, procedure, observation) with TTLs, supersede chains, code anchors to file SHAs, drift reconcile, duplicate rejection, FTS5 keyword search, an MCP server with 11 tools | memspec, MIT, `siimvene/memspec`, installed from npm. Markdown files under a store directory are canonical; the index rebuilds from them | install the same tool; there is no organisational substitute needed | measured |
| Promoting local scratch memory into the team store as a reviewed batch | a plugin in the group's plugin marketplace: one skill, reading the memory engine's export and writing a PR against the team store | a skill that runs the export and opens a PR. The gate is the PR, not the tooling | designed (never exercised in the measured cycles) |
| PM workspace: intake inbox, discovery notes, features, ticket drafts, decisions, stakeholder notes, and skills that read specs before writing a ticket | a plugin in the group's plugin marketplace (three skills: workspace setup, ingest, graduate) plus a folder template in the group standard | the folder is a folder; the value is the ordering rule that a ticket is drafted against the specs, not against the code | measured (with a finding: the template's skills referenced files the copy did not have) |
| Decision records, repo level and team level | the context standard's ADR folder plus a numbered template | [templates/adr.md](../templates/adr.md) in this repository | measured |
| Rule packs (review rubric and house conventions) shipped to agents | the group standard holds the packs; a marketplace plugin distributes only those marked adopted | the cross-vendor review tool ships three vendor-neutral packs of its own (review blast surface, finding discipline, security review), which is a working starting set | measured |
| Design system as a knowledge-plane layer: tokens in two formats, pattern catalogue, component catalogue, demo stylesheet, canvas provenance, divergence log | local: a standalone repository built by reading the reference implementation's frontend, plus one build-time gate as a shell script in the product repo | build it the same way, by reading the shipped code. See [15-design-system](15-design-system.md) for the shape and the minimum useful version | measured |

## 3. Sensors

Every tool in this tier is third-party and open source. The design decision is the placement,
not the tool. See [05-sensor-stack](05-sensor-stack.md).

| Mechanism | What provides it today | Without an organisational standard | Class |
|---|---|---|---|
| Sensor 1, orientation map: symbol and call-graph rank, blast radius, exemplar lookup, co-change, an MCP server, a skill-file exfiltration scanner | ripwire, a single binary on PATH plus an MCP server. Not a local checkout here, so its licence was not read for this inventory | same tool, or any deterministic index that answers "who calls this, what already does this" in a few hundred tokens | designed |
| Sensor 2, YAGNI ladder: seven rungs before code is written, plus a prose ruleset and elision of oversized tool output | chisle, MIT, `JayPokale/Chisle`, installed as a marketplace plugin pinned to tag v3.0.0 (replaced ponytail, same ladder, 2026-09-10) | same tool. It installs three lifecycle hooks, and the marketplace format pins a tag, not a commit, so inspect the hooks and consider a fork | designed |
| Sensor 3, quality ratchets: 19 gates, baselines that only tighten, a Stop hook that hands the failure back to the agent, a pre-tool guard refusing policy edits | cleat, MIT, `svetdev/cleat`. Attach copies the gate directory into the project and writes the baselines. Escape patterns and conformance fixtures for 9 languages | same tool. Some gates need helpers on PATH: a complexity analyzer, an AST matcher, a coverage report in LCOV or Cobertura | measured |
| Sensor 4, architecture diff: snapshot before, diff after, 19 explainers, three of them provable at confidence 1.00, a scope-spillover check, cross-repo seam declarations, a doctor command that proves the hooks fired | enola, Apache 2.0, `enola-labs/enola`, one binary plus an MCP server and hook installation | same tool. Nothing else in the stack crosses repository boundaries, so an adopter with more than one repo needs this or an equivalent | designed |
| Changed-line coverage as a gate | a ratchet gate, fed by a converter from the project's coverage report format | the converter is local work on any stack whose coverage output is not LCOV or Cobertura | measured |
| Mutation score on the money surface | the language ecosystem's own mutation tool, wired per project | local wiring; the design's contribution is using mutation, not coverage, as the exit gate for a verification-net bootstrap | measured |

## 4. Verify gate

| Mechanism | What provides it today | Without an organisational standard | Class |
|---|---|---|---|
| Cross-vendor adversarial review of the pending diff, two backends either of which satisfies the vendor axis, hard-fail when both are unreachable, blind panels, schema-forced results, resumable state on disk | consort, MIT, `siimvene/consort`, also packaged in the group's plugin marketplace | install the public plugin. This is the single most load-bearing third-party piece in the design and it is freely available | measured |
| The second vendor's runtime that the review calls | the other vendor's CLI plus its official agent-runtime plugin, from that vendor's public repository. A second backend calls a third vendor's cloud model API | either backend works standalone. Two backends exist so the gate can hard-fail instead of degrading when one is down | measured |
| Single-model fallback review when the cross-vendor path is unavailable | a plugin in the group's plugin marketplace: one skill, review only, never edits | a prompt. It explicitly does not satisfy the cross-vendor axis and is a stopgap, not a gate | measured |
| Blind security side-pass on the same diff | a security-only reviewer agent shipped inside the cross-vendor review tool, spawned in parallel with no session context | comes with the tool. It is same-vendor and additive; it never satisfies the vendor axis on its own | measured |
| Scanner tier: dependency CVEs, leaked secrets, infrastructure misconfiguration, static analysis | Trivy, invoked by a scan script in the cross-vendor review tool, plus an optional static-analysis server leg that joins when one is reachable and a project properties file exists. Skipped scanners are reported loudly rather than silently dropped | Trivy alone covers the first three. The loud-skip behaviour is the part worth copying: a silent skip and a clean pass look identical | measured |
| Browser QA pass over every UI surface a diff touches, as the right persona, with screenshots | a plugin in the group's plugin marketplace: one skill, driving Playwright | Playwright plus a prompt that names the personas, the locales and what counts as a finding. The design system of tier 2 is what gives it something to check against | measured (headless fallback, not the browser extension) |
| Review rule packs the reviewer loads | the review tool's own three vendor-neutral packs, always injected, plus any packs named by an environment variable or found in the repo's rules directory | the three shipped packs are a working start. A stack-specific pack is the adopter's own work | measured (the shipped packs) / proposed (a backend pack for a legacy stack) |
| Spec conformance in the review: the feature spec, numbered examples and decisions injected to every leg, a scope-drift finding class, a REFINE-SPEC disposition, a delta receipt before push | none yet. The review tool's pack injection can carry the text today; the finding class, the disposition and the receipt are to write | the injection is an environment variable, the class is a paragraph in the reviewer instruction, the receipt reuses the browser-gate pattern | proposed (adr/0009) |
| Provenance trailer on every agent-authored commit | a local commit hook | 5 lines of hook. The matching rejection check, refusing a push whose trailer is missing, is not built | measured (trailer) / proposed (rejection check) |
| The merge gate itself | branch protection on the git host, requiring code-owner review | where the plan refuses protection, the gate is a habit and must be recorded as a named shortcut in a decision record. A pre-push hook is the solo stand-in | measured where the plan allows it |

## 5. Sandbox

| Mechanism | What provides it today | Without an organisational standard | Class |
|---|---|---|---|
| Devcontainer for agent sessions: no direct internet route from the workload container, a language variant system, a boot check that names the identity the agent reads company data as | MIT, `siimvene/devcontainers`, vendored into the group standard as a template with the organisation's defaults and a version file | install the public template directly; the group's copy adds organisational wiring, not the isolation | measured |
| Host-enforced egress allowlist | a proxy sidecar whose entrypoint renders the allowlist into a filter file; the workload sits on an internal network with no route and no capability to add one, so both bypass and allowlist edits are closed | comes with the template. Verify it both ways on first boot: an allowlisted host returns 200, a non-allowlisted one is refused, and stripping the proxy variables fails with no route rather than succeeding | measured |
| Credential delivery without plaintext in the box | an environment file on the host holding references into a secrets manager, resolved at launch. Several managers are supported | comes with the template | measured |
| Refusing to read secret files at all | a plugin in the group's plugin marketplace: one deterministic pre-tool hook blocking reads and shell access to environment files, private keys, keystores, cloud credential files and package-manager auth files, with template suffixes allowed | about 40 lines of hook configuration and a path pattern list | measured |
| One-word launcher and template refresh | launcher scripts in the template, plus a local override slot preserved across template updates | comes with the template. Known trap: the launcher reuses running containers, so an override edit is silently ignored until a forced recreate | measured |
| Team-context mount and memory engine wiring inside the box | setup scripts in the template | two scripts. Known trap: the environment check reported the memory engine missing and called it expected, while the install step had never run | measured (with the finding) |
| Scoped bot identity for unattended runs: contents plus package read, nothing more | nothing. This is a hard blocker, not a nice-to-have: without it the sandbox cannot resolve private packages, so it cannot build, so there is no autonomy in it | federated identity from the git host or cloud provider. Never a downloaded key file, never a personal token, because the build cache is a shared volume | blocked |
| Worktree isolation per session, and a guard refusing commands that cannot be proven to stay in the worktree | the agent runtime's worktree tooling plus a local Bash guard; cost about 6 refused commands per cycle | the discipline is the product: enter a worktree before any git mutation, never rewrite history in a shared checkout | measured |
| Local-only phase while a loop is being proven against a production core | a local pre-push hook rejecting every push, on the clone and its worktrees | 10 lines of hook, plus the rule written into the repo's agent instructions. Verify with a dry-run push before trusting it | measured |
| Test-data isolation between projects sharing a database port | a dedicated container on a distinct port, a mandatory port flag, and a post-run check for foreign test schemas | local work, and worth doing before the first destructive cleanup task runs against the wrong database | measured |

## 6. Harness ergonomics

Off the critical path by design. None of these refuses anything, and none is required for the
loop to work.

| Mechanism | What provides it today | Without an organisational standard | Class |
|---|---|---|---|
| Status line showing active model, context-window usage and session cost | claude-hud, MIT, `jarrodwatts/claude-hud`, vendored into the group's plugin marketplace | install it directly from its own repository | measured |
| Second-vendor CLI integration: a companion runtime with session reuse, a rescue subagent, a stop-time review gate | the other vendor's own agent-runtime plugin, from that vendor's public repository | install it directly. The cross-vendor review tool prefers this runtime and falls back to raw CLI invocation, losing session reuse | measured |
| Pre-completion hygiene skills: a fresh-evidence verification pass, a behaviour-preserving cleanup pass, and a decomposition aid for hard calls, all proposing rather than applying | a plugin in the group's plugin marketplace: three skills, no hooks, working-tree edits at most | three prompts. The propose-only constraint is the part that matters | measured |

## 7. Measurement

| Mechanism | What provides it today | Without an organisational standard | Class |
|---|---|---|---|
| Per-session and per-window spend and tokens | a usage CLI reading the agent runtime's local session logs, run per config directory and deduplicated by message id. Per-account split is not recoverable when session files are mirrored | the same CLI, plus the provider console as a cross-check and a daily threshold | measured |
| The four numbers per turn: wall-clock per stage, tokens per agent, what the gate caught, what was skipped | [templates/dogfood-cycle-report.md](../templates/dogfood-cycle-report.md), filled by hand at the end of each turn | the same template. A skipped step recorded is a finding about the process; an unrecorded one is nothing | measured |
| The gate's own report: one row per gate with command, result and log path, with the reachability probe and wall-clock of every model reviewer | [templates/gate-report.md](../templates/gate-report.md) | the same template. Recording the wall-clock is what distinguishes a clean verdict from a review that never ran | measured |
| Principal-session token accounting | not instrumented. A Stop-hook counter is the mechanical upgrade if the number matters | same gap | proposed |
| Cost per feature, per commit, per tree-hour | derived by hand from the usage CLI plus commit grouping | a script over the same two inputs | measured |

## What does not exist yet

Six named gaps. Each is a mechanism this design calls for and nothing currently provides, here
or upstream. They are the honest edge of the inventory.

1. **Evals on the agent configuration surface.** The contract, the rule files, the skills and
   the hooks are prompt-shaped code with no test suite. A change to any of them ships on
   judgement. This is the design's largest single gap: everything else in the tables is gated,
   and the thing that configures the gates is not `[proposed]`.
2. **Acceptance identity for the PM role.** Accepting behaviour on evidence requires knowing
   who accepted it, and no identity currently distinguishes the PM's acceptance from the code
   owner's merge. A manual trial precedes any tooling here `[proposed, critic-reviewed]`.
3. **A parity rig: replay against an oracle.** For a rewrite or a retirement, the only real
   verification is running the old and new implementations over the same inputs and diffing.
   The reference implementation's billing parity against an incumbent product is the template,
   and it is not built as reusable tooling `[proposed]`.
4. **A reviewer F1 benchmark set.** A corpus of real pull requests with known bugs, so that
   precision, recall and cost per catch are measurable per model and per harness change. Without
   it, model choice for the review gate is taste. With it, it is a data problem `[proposed]`.
5. **Revert rate, defect escape rate and lead time baselines on human-written code.** These must
   be taken before agents author most changes, because the comparison point disappears
   afterwards. Nothing in the inventory captures them today `[proposed]`.
6. **A backend rule pack for the legacy stack.** The review tool's shipped packs are
   vendor-neutral and the group standard's adopted packs cover common conventions, testing, CI
   and one frontend framework. The pack for a large legacy backend is seeded by the first turns
   against it and does not exist yet `[proposed]`.

Two more absences are recorded elsewhere rather than repeated here: the scoped bot identity in
tier 5, which is blocked rather than proposed, and the mechanical token diff between the design
system and the shipped stylesheet in [15-design-system](15-design-system.md).
