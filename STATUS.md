# Status ledger

Which parts of the design sit in which evidence class, as of 2026-09-09. See
[WRITING.md](WRITING.md) for the classes.

| Mechanism | Class | Where | Note |
|---|---|---|---|
| The loop end to end on a real product | measured | kvart cycles 1, 2, 3 | 12 to 19 min to PR; <30 min to live without required CI (cycles 1, 2), 41 min with the ruleset's five required checks on hosted runners (cycle 3, 2026-09-09) |
| Operating contract loaded in every session | measured | kvart, legacy core | eval suite on contract changes: proposed |
| Context standard L0 + team-context repo | measured | kvart | L1 ADRs bootstrapped; L2 docs-lint disabled on the plan |
| Spec retro-generation and findings file | measured | kvart | skills run by hand; sister spec PRs hand-edited |
| Day 1 onboarding runbook (team repo, standard adoption, memory move, specs, ADRs, PM workspace) | measured | kvart | one session for ~250 features; see 17-onboarding |
| ADR candidate table and rejected list | measured | kvart | 30 candidates, 13 + 8 written, 1 unconfirmed |
| PM workspace and skill catalogue | measured (workspace) / designed (most skills) | kvart | only the ticket and readiness skills exercised in the cycles; see 14-pm-surface |
| Design system as a knowledge-plane layer | designed | kvart | repo built on Day 1; not yet read by a BUILD or QA pass in a measured cycle; prototype-on-the-ticket decided 2026-09-09, first UI cycle will measure it; see 15-design-system |
| Concept-to-tool inventory | reference | | see 16-inventory |
| Memory store bound read-only; promote PR | measured | kvart | store moved; first promote PR opened by the bot identity in cycle 3 (2026-09-09), code owner reviews |
| Cross-vendor review, three axes | measured | kvart, legacy core | two backends; hard-fail proven |
| Blind security side-pass | measured | kvart | |
| Scanner tier | measured | kvart | static analysis scope excludes the gate code itself |
| Browser QA pass | measured | kvart | headless fallback, not the browser extension |
| Quality ratchets (cleat) in the agent loop | measured | kvart, legacy core | guard held against its operator; 11 upstream defects deferred; Stop-hook re-send and formatter-pass false positives fixed in the operator's fork and vendored back (kvart #23); upstream `svetdev/cleat#6` carries the first batch, the second has no PR yet |
| Architecture diff (enola) with layer declaration | measured (gate) / designed (catch) | kvart | the shipped Stop hook could not fail; replaced by a check on the three provable explainers that blocks once, 7 planted cases (kvart #24); not yet the cause of a caught regression |
| Orientation map (ripwire) | designed | kvart | worktree-index behaviour unverified |
| YAGNI ladder (ponytail) | designed | kvart | no real pin possible via marketplace; trial on a complex task pending |
| Head-and-hands delegation | measured | kvart trial | works when the head verifies; fails when it waits |
| Worktree isolation and shared-checkout discipline | measured | kvart | incident-derived; 55 worktrees and 103 merged or superseded branches (72 local, 31 remote) piled up because no step owned the delete, now the orchestrator's after merge |
| Sandbox: egress, toolchain | measured | legacy core | |
| Sandbox: scoped bot identity | measured (kvart) / blocked (legacy core) | kvart, legacy core | kvart: a GitHub App with contents + pull-requests write and no admin; cannot merge past the ruleset, cannot edit workflows; authored a real PR that was merged and deployed in cycle 3 |
| Verification net: aggregate coverage ratchet, characterization + mutation, database self-provisioning | measured | legacy core | message broker container blocked |
| Money tiering per class with self-testing predicate | measured | legacy core | |
| Layering as lint over declared dependencies | measured | legacy core | 0 violations, no exemptions |
| Local-only phase enforced by pre-push hook | measured | legacy core, kvart | kvart's hook ignores the ref list and gates a pure branch delete; open |
| Provenance trailer | measured (trailer) / proposed (rejection check) | kvart | |
| Branch protection as the merge gate | measured | kvart (ruleset, 2026-09-08), legacy core (org plan) | kvart moved to a paid plan; ruleset = PR + five required checks, empty bypass list, refused a direct push from owner and bot |
| Per-stage wall-clock and tokens | measured | kvart | principal session tokens not instrumented |
| CI as a required check on a real product | measured | kvart | first full run 40 min backend (serial suite); tiered: 19 min impact-selected backend on the PR (hosted 2-core), 6 min full suite on the on-demand 8-core runner after merge; the checks gated a real merge in cycle 3. 2026-09-09: PR-path backend moved to the same on-demand runner (kvart #31, #32): full suite 23m23s hosted -> 11m15s, runner woken by a pull_request_target run of main's code so the WIF ref pin holds; three reviewers converged on the residual (unreviewed PR code on a stateful VM), accepted, stateless per-wake VM queued as phase 2. Same day, #34: the first-ever impact-selected run (#33) failed on the whole-suite coverage floor (tiering had shipped without that branch executing), a deleted test module now forces FULL, and a late nightly displaced a merge's pending run in the shared concurrency group (per-run groups now) |
| Escalation channel (agent asks, named human decides in-thread, decision written back) | measured (round trip) / designed (Jira write-back) | kvart | 49 s decision latency on the synthetic test; responder allowlist and timeout-as-state proven |
| Cost per feature, per commit, per tree-hour | measured | kvart | list-price equivalents |
| Revert rate, defect escape, lead time baselines | measured (kvart, Jun to Sep 2026) | kvart | 0 reverts in 920 commits, 84.7 % direct-to-main, PR lead time median 6 min on 22 PRs, 46.5 % of fixes review-attributed; deploy tags missing, so escape stays a proxy |
| Reviewer F1 benchmark set | proposed | | |
| Recommendation acceptance rate | field | Pipedrive | |
| PM acceptance with acceptance identity | proposed, critic-reviewed | | manual trial first |
| Parity replay against an oracle | proposed | | kvart's billing parity with the incumbent is the template |
| Blast-radius ladder L0 to L6 | mixed | see 11-scaling | L0, L1, L3 measured; L4 designed; L2, L5, L6 proposed |
| DAG scheduling, best-of-N, width promotion criteria | proposed | | |
| Evals on the agent-config surface | proposed | | the named biggest gap |
| Backend rule pack for the legacy stack | proposed | | seeded by the first turns |
