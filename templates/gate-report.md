<!--
  GATE REPORT. One per pull request, written by the agent that ran the gates and attached
  to the PR. It is what the merging human reads instead of the diff: every row is a check
  that was run, with the command that reruns it and the log that holds the output.
  A row with no command is not a gate, it is an opinion. A gate that could not run is
  recorded as SKIPPED with the reason, never quietly dropped.
-->

# Gate report: <repo>#<n> (`<short sha>`)

- Branch: `<branch>`, base `<base ref>`
- Diff size: <n> files, <n> insertions, <n> deletions
- Money path touched: <yes|no>

## Per-gate results

| Gate | Command | Result | Notes / log |
|---|---|---|---|
| lint | `<lint command on changed files>` | <PASS/FAIL/SKIPPED> | |
| format | `<format check command>` | | |
| types | `<type checker on changed files>` | | |
| unit tests | `<test command>` | <PASS n/n> | `<log path>` |
| integration tests | `<test command>` | <PASS n/n> | `<log path>` |
| fail-on-base (red-before) | `<check command>`: new or changed tests at the merge base with the branch's tests applied | <n/n RED on base, n/n GREEN on branch> | failure kind per test; declared exemptions <n>; `<receipt or log path>` |
| changed-line coverage | `<coverage gate command>` | <PASS, >= threshold> | threshold <n> |
| ratchet: escapes | `<gate command>` | | baselined debt only |
| ratchet: conventions | `<gate command>` | | |
| ratchet: duplication | `<gate command>` | | |
| ratchet: complexity | `<gate command>` | | |
| ratchet: doc-size | `<gate command>` | | |
| ratchet: test-hygiene | `<gate command>` | | |
| architecture diff | `<snapshot and diff against the pinned baseline>` | | new findings, coupling added |
| secret scan | `<scanner command>` | | |
| dependency scan | `<scanner command>` | | pre-existing <n>, new from this diff <n> |
| static analysis | `<scanner command>` | | new-code issues <n> |
| cross-vendor review | `<review command>` | <n findings> | wall-clock <mm:ss>, reachability probe <result>, `<log path>` |
| blind security side-pass | `<side-agent invocation>` | <n findings> | non-inheriting context, `<log path>` |
| browser QA | `<qa command>` | <n surfaces, n findings> | `<screenshot directory>` |

<!-- Two entries on the cross-vendor row are load-bearing. The reachability probe proves a
     reviewer was actually reached, because an unreachable reviewer and a clean review look
     identical in the output. The wall-clock proves it read something: a multi-hundred-line
     diff reviewed in seconds did not happen. A clean verdict without both is not evidence.
     If no cross-vendor reviewer is reachable, the gate FAILS; it never degrades to a
     same-vendor reviewer, and the blind security side-pass never substitutes for it. -->

## Findings and disposition

| # | Source | Severity | Finding | Verified against code | Disposition | Where |
|---|---|---|---|---|---|---|
| 1 | <gate> | <CRITICAL/SERIOUS/MINOR> | <one line> | <yes/no> | <ACCEPT-FIX/ACCEPT-DEFER/ACKNOWLEDGE/DISMISS> | <commit or backlog id> |

<!-- Severity is about the defect; disposition is about what happens next. Every finding
     gets both, and one of the four dispositions, so nothing sits in the report undecided.
     Reviewer output is a hypothesis set, not a work queue: spot-verify every CRITICAL and
     SERIOUS claim against the code before acting on it, and record the verification
     column honestly. Volume is not confidence. A dismissed finding needs its reason in
     the finding column. -->

## Bootstrap versus feature failures

<!-- Kept separate on purpose. A gate failing on pre-existing debt that the diff did not
     touch is a bootstrap failure: it belongs to whoever adopted the gate, and it must not
     be used to argue the feature is unsafe. A gate failing on lines this diff changed is a
     feature failure and blocks. Mixing the two is how teams learn to ignore a red gate. -->

**Bootstrap (pre-existing, not this diff):**
- <gate>: <what>, <owner role>, <tracked where>

**Feature (this diff):**
- <gate>: <what>, <fixed in commit <sha> | blocking>

## Verdict

<Clear to merge, or blocked and by what. Name the role that merges; the agent does not.>
