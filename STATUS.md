# Status ledger

Which parts of the design sit in which evidence class, as of 2026-09-07. See
[WRITING.md](WRITING.md) for the classes.

| Mechanism | Class | Where | Note |
|---|---|---|---|
| The loop end to end on a real product | measured | kvart cycles 1, 2 | 12 to 19 min to PR, <30 min to live excluding human waits |
| Operating contract loaded in every session | measured | kvart, legacy core | eval suite on contract changes: proposed |
| Context standard L0 + team-context repo | measured | kvart | L1 ADRs bootstrapped; L2 docs-lint disabled on the plan |
| Spec retro-generation and findings file | measured | kvart | skills run by hand; sister spec PRs hand-edited |
| Day 1 onboarding runbook (team repo, standard adoption, memory move, specs, ADRs, PM workspace) | measured | kvart | one session for ~250 features; see 17-onboarding |
| ADR candidate table and rejected list | measured | kvart | 30 candidates, 13 + 8 written, 1 unconfirmed |
| PM workspace and skill catalogue | measured (workspace) / designed (most skills) | kvart | only the ticket and readiness skills exercised in the cycles; see 14-pm-surface |
| Design system as a knowledge-plane layer | designed | kvart | repo built on Day 1; not yet read by a BUILD or QA pass in a measured cycle; see 15-design-system |
| Concept-to-tool inventory | reference | | see 16-inventory |
| Memory store bound read-only; promote PR | measured / designed | kvart | store moved; promote PR never exercised in the cycles |
| Cross-vendor review, three axes | measured | kvart, legacy core | two backends; hard-fail proven |
| Blind security side-pass | measured | kvart | |
| Scanner tier | measured | kvart | static analysis scope excludes the gate code itself |
| Browser QA pass | measured | kvart | headless fallback, not the browser extension |
| Quality ratchets (cleat) in the agent loop | measured | kvart, legacy core | guard held against its operator; 11 upstream defects deferred |
| Architecture diff (enola) with layer declaration | designed | kvart | wired; not yet the cause of a caught regression |
| Orientation map (ripwire) | designed | kvart | worktree-index behaviour unverified |
| YAGNI ladder (ponytail) | designed | kvart | no real pin possible via marketplace; trial on a complex task pending |
| Head-and-hands delegation | measured | kvart trial | works when the head verifies; fails when it waits |
| Worktree isolation and shared-checkout discipline | measured | kvart | incident-derived |
| Sandbox: egress, toolchain | measured | legacy core | |
| Sandbox: scoped bot identity | blocked | legacy core | no autonomy in the box until it exists |
| Verification net: aggregate coverage ratchet, characterization + mutation, database self-provisioning | measured | legacy core | message broker container blocked |
| Money tiering per class with self-testing predicate | measured | legacy core | |
| Layering as lint over declared dependencies | measured | legacy core | 0 violations, no exemptions |
| Local-only phase enforced by pre-push hook | measured | legacy core | |
| Provenance trailer | measured (trailer) / proposed (rejection check) | kvart | |
| Branch protection as the merge gate | measured where the plan allows; habit where it refuses | kvart (habit), legacy core (org plan) | |
| Per-stage wall-clock and tokens | measured | kvart | principal session tokens not instrumented |
| Cost per feature, per commit, per tree-hour | measured | kvart | list-price equivalents |
| Revert rate, defect escape, lead time baselines | proposed | | must precede agent dominance |
| Reviewer F1 benchmark set | proposed | | |
| Recommendation acceptance rate | field | Pipedrive | |
| PM acceptance with acceptance identity | proposed, critic-reviewed | | manual trial first |
| Parity replay against an oracle | proposed | | kvart's billing parity with the incumbent is the template |
| Blast-radius ladder L0 to L6 | mixed | see 11-scaling | L0, L1, L3 measured; L4 designed; L2, L5, L6 proposed |
| DAG scheduling, best-of-N, width promotion criteria | proposed | | |
| Evals on the agent-config surface | proposed | | the named biggest gap |
| Backend rule pack for the legacy stack | proposed | | seeded by the first turns |
