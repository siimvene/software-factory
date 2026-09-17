# Failure catalogue

Every trap that cost at least an hour during the reference work, generalised. Symptom, cause,
fix. All `[measured]` on the date given. The legacy-core case study carries its own 20-row
table; the entries here are the ones that apply to any adoption.

## Delegation and agents

| Symptom | Cause | Fix |
|---|---|---|
| child process produces no output and no diff; the head "waits" for hours (2026-09-05) | stdin inherited; child blocks on "reading additional input" | `< /dev/null` or a payload on stdin; wall-clock cap on every delegation; never end a turn on a bare wait; empty output + empty diff = hung |
| subagent returns "you should now verify X" | delegation brief without the proactivity phrases | the three phrases in every brief; two-phase pattern when verify is expensive |
| a hands round is spent on a redesign after the reviewer finds the shape wrong (2026-09-05, round 3 of 4) | the brief named the outcome and left the shape (streaming granularity) to the builder | the program design note names shape decisions before the first brief; the brief cites its sections |
| worktree Bash guard refuses ~6 commands per cycle (2026-09-07) | guard cannot prove computed paths, heredocs mentioning git, relative `cd` stay in the worktree | absolute paths, editor tools on worktree paths, plain commands |
| a plugin or MCP server works in one session type and not another | two config directories on one machine | register in both |
| a skill runs in the main checkout and is absent from every station worktree (2026-09-10) | the skill directory is gitignored with the rest of the agent state; a worktree checks out only tracked files | re-include the skill in `.gitignore` and commit it; a skill the loop depends on is code |
| the saved browser state restores a session that is not logged in (2026-09-10) | state saved while the SPA callback was still running; the CLI reports the URL when the navigation ends, before the client-side redirect | wait for the callback to leave the URL, do the association selection, then save state |
| the auto-named page tree after a navigation is a 0-byte file (2026-09-10, Playwright CLI 0.1.19) | tool defect on this app; an explicit output filename works | always pass `--filename`; treat an empty tree file as "not captured", never as an empty page |
| review agent posts "done" without posting the review (field) | a runtime update changed behaviour | a hook that verifies the effect, not the self-report |
| top-tier model spend is half the bill | simple work routed to the top tier | explicit model per subagent; audit a week of usage per project |
| a canvas station never starts; the card sits "queued" (2026-09-09) | the desktop canvas starts a node only while its project is on screen; nobody was looking | run stations in-process when nobody watches the canvas; close the queued node so two builders never share a worktree |
| a worktree appears in `git worktree list` under a path with a space in it, and a second one is missing (2026-09-09) | a shell loop that word-splits in one shell and not in another; a stray local branch named like the remote ref (`origin/main`) shadowed the real one, so "ahead by 12" meant nothing | provision worktrees one explicit command each, verify `git worktree list` and `rev-parse` before opening a station, `git show-ref` when a ref name warns "ambiguous" |
| a station's gate ran without the complexity analyzer although the venv had it (2026-09-09) | the station recreated its worktree and wiped the provisioned venv | the brief says "do not create worktrees"; the principal reruns the gate with the analyzer before trusting a station's gate log |
| both review vendors flag a field that does not exist on the API (2026-09-09) | the brief stated the field name from a frontend type that was itself wrong | briefs cite the backend schema, not a consumer's type; the panel catching a brief's error is the panel working |
| two sessions fix the same red required check within 10 minutes (2026-09-09) | shared-checkout discipline covers the tree and the branch pointer, not the claim on a fix | claim a red shared gate in the team memory store or the escalation channel before fixing; check for a claim first, so the claim record exists before the branch does |
| a throwaway `git commit -am` probe swallows the uncommitted real fix; `git reset --hard` drops it and the rehearsal runs the old script (twice, 2026-09-09) | staging everything swept unrelated work into the probe commit | commit the real change before any throwaway commit in the same tree; recover with `git checkout <probe-sha> -- <paths>` |
| a shared checkout sits 12 commits behind with a 4-hour-old `.git/index.lock`, then 5 behind while the handoff says current (2026-09-09) | nobody fast-forwarded the shared tree; a stale lock from a dead git process | verify-on-arrival fast-forwards the shared checkout and lists the worktrees; remove the lock only after `ps` shows no git process |
| about 11,000 "opus" subagent calls ran on the wrong tier since 2026-08-13 (2026-09-08) | two of three config directories lacked the `claude-opus-5 -> claude-opus-4-8` alias override | a model alias is a per-config-dir setting; the routing audit checks the served model, not the requested alias (10-measurement) |

## Tracker and ledger

| Symptom | Cause | Fix |
|---|---|---|
| every Done ticket shows Resolution "Unresolved"; `resolvedDate` empty; resolved-vs-created reports flat (2026-09-09) | the workflow was created over the API with statuses and transitions only; in Jira a status is not a resolution, and Resolution was on no screen | an update-field post-function on the terminal transition (Resolution = Done) and a clearing one on each reopen transition; backfill the already-Done tickets through a temporarily added screen field; the list view with the Resolution column is the check |
| a workflow probe ticket cannot be removed afterwards (2026-09-09) | the automation token has no Delete issues permission | prove a transition on a ticket the token may delete, or label the probe for a human; never leave it unlabelled in the ledger |

## Gates and ratchets

| Symptom | Cause | Fix |
|---|---|---|
| duplication gate reports 557 clone pairs (2026-09-04) | `base_ref` pointed at a branch 81 commits behind the real default | set `base_ref` to the real default branch (6 pairs, all real) |
| 407 complexity findings, most in files nobody wrote (2026-09-05) | vendored static JavaScript counted | exclude vendored assets; on an un-netted core exclude test trees too, with the reason |
| complexity gate reads nonsense | a package manager installed a compressor under the analyzer's binary name | verify with `--help`; pin the analyzer in a venv |
| the architecture Stop gate reports clean on every stop while the change is in a worktree; under a worktree launch it blocks every stop with "no baseline" (2026-09-16) | the hook rooted on `CLAUDE_PROJECT_DIR`, which stays at the launch directory after a mid-session worktree switch; the worktree has no gitignored baseline | root the hook on the hook input's `cwd` then the repo top-level; grade against the main checkout's baseline when the worktree has none; no baseline anywhere still blocks |
| pre-push refuses "no passing receipt" after the gate passed in the station worktree (2026-09-16) | receipts stored per checkout although keyed by tree id | one receipt store under the main checkout root (`--git-common-dir`), atomic writes |
| a branch that changes a git hook is judged by the old hook (2026-09-16) | `core.hooksPath` absolute: every worktree runs the main checkout's copy | keep it relative; the project checker verifies |
| worktrees pile up (18 hanging, 9 removable) (2026-09-16) | the runtime never removes a worktree that has commits; hand-placed stations are forgotten after merge; worktrees in a session temp dir leave ghost metadata | stations beside the checkout, never in a temp dir; a daily collector removes merged + clean worktrees and prunes ghosts |
| a failed `git push` with a wrong token erases the operator's stored GitHub credential (2026-09-16) | the OS keychain credential helper erases on 401; a one-off token passed as a header failed first | push bot commits through a scoped credential helper for that one command; route git auth through the `gh` helper so a bad attempt cannot erase it |
| 3 of 6 gates red in the primary checkout after a clean merge (2026-09-07) | walkers ignore the ignore file and read nested worktrees; a glob with a leading `*/` never matched relative paths | teach walkers the runtime directories; test with planted files |
| duplication gate red on an import block; a token-based finder makes it worse (2026-09-05) | line-based clone finder; import blocks and real clones have overlapping token distributions | upstream fix (skip import lines); never raise `min_lines`; note the condition clears on merge |
| a scratch copy of a test reads as a clone | the scanner walks scratch directories | keep scratch code off scannable extensions, or fix the walkers |
| "bootstrap issue, not a defect" on a red ratchet (2026-09-06) | misreading; the baselined function had doubled on main | a ratchet fails on baselined debt that got worse; that is it working |
| the gate's own code has an argv injection (2026-09-07) | a changed path beginning with `-` parsed as a flag | gates get the same cross-vendor review as product code |
| a regex conventions rule baselined an empty site | `^\s*` under MULTILINE | validate rules on true and false cases before wiring |
| 7 layering violations on day one, all legitimate (2026-09-04) | pattern matched test-scope dependencies | anchor the pattern on production scopes only; 10-case validation |
| a hook configured is a hook that never fired | config is not execution | a doctor command that verifies the hook ran; `source` tags on entries it must recognise |
| the guard refuses a PR body | the body quoted the baseline flag | write long texts with the editor tool and reference them by path; the refusal is the guard working |
| strict ratchet red on every PR that improves the number (2026-09-09) | `--strict` demands the baseline be tightened in the same PR; the agent guard refuses the write; the ruleset has no bypass | decided 2026-09-09 evening (ADR 0004, option b): the guard permits a write that only lowers a number; five of the day's seven collisions were the merge-base diff bug (#41), two the real deadlock, the last on #43 Closed 2026-09-09: cleat gained `--tighten`, the same rewrite refused whenever it would accept anything new or worse (or a target it did not write, or drift, or a scoped run); the guard lets it through, the agent answers the NOTE itself |
| impact-selected PR run fails on a repo-wide coverage floor (2026-09-09) | pytest inherits `fail_under` from the project config; a two-target slice reaches 28 % | no coverage floor on the slice; the floor applies to the full run and to the post-merge full suite |
| two PRs both tighten the same baseline file | each improving branch records its own number | tighten after rebase, one PR at a time; merge order is the fix, not a merge tool |
| the introducing PR cannot exercise itself; three instances in one day (2026-09-09) | the workflow runs the default branch's copy of the script (`pull_request_target`, the sync legs, the wake-runner call), never the PR's own change | prove a CI-plumbing PR with the NEXT PR and name it in the handoff, or ship the change behind a flag the PR flips after merge |
| a merge commit lands red on cleat with the regenerated baseline missing (2026-09-09, #40) | `git checkout --theirs` plus regenerate plus `git add` plus `commit --no-edit` left the baseline staged but out of the merge commit | `git status --short` after every merge commit |
| a scoped gate cannot fail and the FULL run aborts in 0 s (2026-09-09) | macOS bash 3.2 has no `mapfile`, so scope came back empty; `"${arr[@]}"` on an empty array under `set -u` aborted | rehearse the blocked direction, not only the pass; a gate that cannot fail is not a passing gate |
| a repo-set `base_ref` of HEAD blanks every ratchet under strict CI (2026-09-09) | the diff against itself is empty | under `--strict`, ignore a repo-set `base_ref` and resolve the merge base with the default branch yourself |

## Review gate

| Symptom | Cause | Fix |
|---|---|---|
| zero findings in seconds on a large diff (2026-09-04) | the reviewer never ran; the wrapper reported the failure as a clean pass | reachability probe first; wall-clock sanity; the wrapper fixed to distinguish the two |
| a CRITICAL that is false in one line (2026-09-04) | diff-only transport, no repo access; a framework claim | verify against code; use a repo-reading transport when the finding class needs a sweep |
| "the existing unit suite is red" (2026-09-09) | the reviewer read the test file on the base, not the branch, where the station had updated it | run the named test file before believing a suite claim; one command, thirty seconds |
| a review finding contradicts the spec's role table (2026-09-09) | the reviewer widened scope from the code's shape, not the product's | dismiss with the spec cited, and escalate the dismissal (§11) so a PM can overrule |
| the author's scoping accepted by the author's model | same-vendor, inheriting review | cross-vendor, non-inheriting; the cycle-2 HIGH is the proof |
| a probe succeeds, the real call trips a spend cap | reachability is not budget | a second backend; hard-fail, never degrade |
| seven PRs green on every gate; the owner opens the native app to the old screen under a new card, a misused monogram, a scrolling help footer (2026-09-17) | every gate read a diff, none rendered a screen; the surface QA step had no native runtime and was skipped silently; the story's criterion "opens the announcement list" named no prototype view, so the old screen satisfied it | native harness shoots the named routes, screenshots travel with the PR, a verifier above the builder's tier compares each to its named prototype view; a touched platform with no runtime is a FAILED gate line; a UI ticket names `<prototype>#<view>` per screen (06-verify-gate "Native client QA", 14-pm-surface) |

## Testing and coverage

| Symptom | Cause | Fix |
|---|---|---|
| coverage reads 36.8 % when the truth is 55.6 % (2026-09-04) | per-module sum; the integration suite's coverage attributed to one class | gate on the aggregate report only |
| a money metric moves 0.17 points when a 238-line money class goes from 1 to 238 lines covered | tiering per module; the bulk of money logic in a module never flagged | tier per class; a self-testing predicate |
| demo fixtures top the money gap list | a whole module tiered as money; 1,031 of 1,312 lines were seeding behind a flag | tier the endpoints, not the module |
| one file in 4,317 disagrees with its directory | globs matched directories; the bytecode package differed | match the declared package |
| a filtered test run silently corrupts the aggregate | `--rerun-tasks` with a filter overwrites the module's exec data | re-run the full module task before trusting the aggregate |
| a 100 % mutation score next to 6 real clones | mutation says the tests notice changes; it says nothing about copy-paste | keep both gates |
| changed-line coverage green on every PR, whole-module kill rate 30 to 40 %, 11.2 % on the largest billing module (2026-09-15) | coverage says a line ran; a test that asserts only that something came back covers everything | mutation kill rate as a ratchet on the touched modules, killed over total |
| a module reads 100 % mutation score with 3.6 % of its mutants exercised (2026-09-15) | killed over (killed plus survived) drops the not-exercised column | report killed over total, always |
| parallel mutant runs against one shared test database score garbage (2026-09-15) | workers collide on the same rows | a migrated template database, cloned per run, behind a flag |
| a new test passes on the merge base as well as on the branch (the trial's behavioural test proved only that a function was unused; a `list(...)` would have passed, 2026-09-05) | it asserts something that was already true | the fail-on-base check: red on the base, green on the branch, exemptions declared, failure kind recorded |
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
| a worktree starts a second database container (2026-09-09) | the compose project name defaulted to the worktree directory | pin the compose project name; rehearse the blocked direction so the collision shows |
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
