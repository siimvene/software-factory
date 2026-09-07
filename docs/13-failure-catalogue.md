# Failure catalogue

Every trap that cost at least an hour during the reference work, generalised. Symptom, cause,
fix. All `[measured]` on the date given. The legacy-core case study carries its own 20-row
table; the entries here are the ones that apply to any adoption.

## Delegation and agents

| Symptom | Cause | Fix |
|---|---|---|
| child process produces no output and no diff; the head "waits" for hours (2026-09-05) | stdin inherited; child blocks on "reading additional input" | `< /dev/null` or a payload on stdin; wall-clock cap on every delegation; never end a turn on a bare wait; empty output + empty diff = hung |
| subagent returns "you should now verify X" | delegation brief without the proactivity phrases | the three phrases in every brief; two-phase pattern when verify is expensive |
| worktree Bash guard refuses ~6 commands per cycle (2026-09-07) | guard cannot prove computed paths, heredocs mentioning git, relative `cd` stay in the worktree | absolute paths, editor tools on worktree paths, plain commands |
| a plugin or MCP server works in one session type and not another | two config directories on one machine | register in both |
| review agent posts "done" without posting the review (field) | a runtime update changed behaviour | a hook that verifies the effect, not the self-report |
| top-tier model spend is half the bill | simple work routed to the top tier | explicit model per subagent; audit a week of usage per project |

## Gates and ratchets

| Symptom | Cause | Fix |
|---|---|---|
| duplication gate reports 557 clone pairs (2026-09-04) | `base_ref` pointed at a branch 81 commits behind the real default | set `base_ref` to the real default branch (6 pairs, all real) |
| 407 complexity findings, most in files nobody wrote (2026-09-05) | vendored static JavaScript counted | exclude vendored assets; on an un-netted core exclude test trees too, with the reason |
| complexity gate reads nonsense | a package manager installed a compressor under the analyzer's binary name | verify with `--help`; pin the analyzer in a venv |
| 3 of 6 gates red in the primary checkout after a clean merge (2026-09-07) | walkers ignore the ignore file and read nested worktrees; a glob with a leading `*/` never matched relative paths | teach walkers the runtime directories; test with planted files |
| duplication gate red on an import block; a token-based finder makes it worse (2026-09-05) | line-based clone finder; import blocks and real clones have overlapping token distributions | upstream fix (skip import lines); never raise `min_lines`; note the condition clears on merge |
| a scratch copy of a test reads as a clone | the scanner walks scratch directories | keep scratch code off scannable extensions, or fix the walkers |
| "bootstrap issue, not a defect" on a red ratchet (2026-09-06) | misreading; the baselined function had doubled on main | a ratchet fails on baselined debt that got worse; that is it working |
| the gate's own code has an argv injection (2026-09-07) | a changed path beginning with `-` parsed as a flag | gates get the same cross-vendor review as product code |
| a regex conventions rule baselined an empty site | `^\s*` under MULTILINE | validate rules on true and false cases before wiring |
| 7 layering violations on day one, all legitimate (2026-09-04) | pattern matched test-scope dependencies | anchor the pattern on production scopes only; 10-case validation |
| a hook configured is a hook that never fired | config is not execution | a doctor command that verifies the hook ran; `source` tags on entries it must recognise |
| the guard refuses a PR body | the body quoted the baseline flag | write long texts with the editor tool and reference them by path; the refusal is the guard working |

## Review gate

| Symptom | Cause | Fix |
|---|---|---|
| zero findings in seconds on a large diff (2026-09-04) | the reviewer never ran; the wrapper reported the failure as a clean pass | reachability probe first; wall-clock sanity; the wrapper fixed to distinguish the two |
| a CRITICAL that is false in one line (2026-09-04) | diff-only transport, no repo access; a framework claim | verify against code; use a repo-reading transport when the finding class needs a sweep |
| the author's scoping accepted by the author's model | same-vendor, inheriting review | cross-vendor, non-inheriting; the cycle-2 HIGH is the proof |
| a probe succeeds, the real call trips a spend cap | reachability is not budget | a second backend; hard-fail, never degrade |

## Testing and coverage

| Symptom | Cause | Fix |
|---|---|---|
| coverage reads 36.8 % when the truth is 55.6 % (2026-09-04) | per-module sum; the integration suite's coverage attributed to one class | gate on the aggregate report only |
| a money metric moves 0.17 points when a 238-line money class goes from 1 to 238 lines covered | tiering per module; the bulk of money logic in a module never flagged | tier per class; a self-testing predicate |
| demo fixtures top the money gap list | a whole module tiered as money; 1,031 of 1,312 lines were seeding behind a flag | tier the endpoints, not the module |
| one file in 4,317 disagrees with its directory | globs matched directories; the bytecode package differed | match the declared package |
| a filtered test run silently corrupts the aggregate | `--rerun-tasks` with a filter overwrites the module's exec data | re-run the full module task before trusting the aggregate |
| a 100 % mutation score next to 6 real clones | mutation says the tests notice changes; it says nothing about copy-paste | keep both gates |
| a test that passes alone and fails in the suite reported as a regression | test pollution | run in isolation first; check the history of the asserted contract |
| "verified in CI" for a change never run locally | the coverage library could not read the JVM's bytecode version | run it; intent is not completion |

## Environment

| Symptom | Cause | Fix |
|---|---|---|
| a test suite writes into another project's database and may drop its schemas (2026-09-04) | both defaulted to the same port; a cleanup task drops matching schemas older than 24 h | dedicated container on a distinct port; mandatory port flag; post-run isolation check |
| `FATAL: too many clients` | stock `max_connections` under 8 parallel build workers with connection pools | raise it in the test container |
| a native module fails to compile on the operator's architecture | no prebuilt binary for the platform; the build needs an older interpreter | pin the interpreter on PATH for the install; replace the dependency later |
| the sandbox dies with exit 128 at post-create | a worktree's `.git` points at a host path outside the mount | real clone for sandboxed repos; reinstall hooks in each clone |
| test containers do not start in the sandbox | no Docker socket, by design | database sidecar in the compose file |
| the build cannot resolve private packages in the sandbox | no scoped credential | scoped bot identity; never a personal token in a shared volume |
| the message-broker container waits forever with empty logs | a starter script the container library injects never arrives on this Docker provider | open item; non-fatal skip so database tests still run |
| `timeout` missing on macOS; `git stash` refuses intent-to-add files (2026-09-07) | platform gaps | tool's own cap or coreutils; copy the file for a negative run |
| browser tests from a worktree cannot reach the database | compose project name differs; runtime key not copied | pin the project name; copy the key; document it |
| a health check compares against the wrong body | `{"status":"UP"}` vs "ok" | read the real response before asserting on it |
| the primary checkout is suddenly bare (2026-09-07) | a gate branch's pre-commit fixture run set `core.bare=true` | reset; fixtures must not touch the parent repo's config |

## Knowledge and memory

| Symptom | Cause | Fix |
|---|---|---|
| a rule file loaded into every session describes a token model retired months ago (2026-09-07) | doc-vs-code drift in the repo layer | the spec bootstrap's drift findings are priority tickets; fix the rule file before any work in its area |
| a backlog whose "open" medium items are mostly shipped (2026-09-05) | stale toward done | verify against code and active branches before picking anything |
| a duplicate memory written on retry | the duplicate warning is a warning, the write lands | merge with a supersede; read the tool's return |
| a generated spec contradicts itself on a business rule (2026-09-05) | regeneration documents implementation, not intent | resolve the business decision before using the spec as an acceptance reference |
| a PM skill silently drafts from the wrong source | the template references a file the copy lacks | run the skill once against the copy; each broken lookup is a finding |
| the team import is a silent no-op on one platform | the standard's mount path does not exist there | the memory binding carries the team layer; say so in the ADR |
| a personal name in a PR body | pre-claim search skipped on outbound text | search before writing any PR artifact; history rewrite is the cost otherwise |

## Measurement

| Symptom | Cause | Fix |
|---|---|---|
| a per-slice cost 2 to 5× too high | costed per bare agent | cost per orchestrator tree from session data |
| fix:feat looks alarming in a review-gated repo | half of fixes are the gate succeeding | non-review fix:feat; in a hardening phase, the fix count trend |
| per-account spend not recoverable | session files mirrored across config directories | dedupe by message id; use ratios only |
| a dependency count marked as a total | scanners report floors | treat zero as "none found", never "none exists" |
