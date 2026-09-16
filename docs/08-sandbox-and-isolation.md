# Sandbox and isolation

Where an agent runs, what it can reach, who it is, and which git state it may mutate. Two
levels: the operator's machine (worktrees, shared-checkout discipline) and the sandbox
(devcontainer with an enforced egress gateway and a scoped identity). Autonomy is only
available in the second.

## Isolation on the operator's machine

**The checkout is shared mutable state.** File-ownership rules between parallel agents do not
cover the branch pointer and HEAD. Another session can switch branches between any two of
your tool calls. Origin incident: a `commit --amend` in a shared tree rewrote a fresh commit
another session had just made on a branch it had silently switched to; recovered byte-identical
from the reflog `[measured 2026-08-28]`.

Rules, enforced by behaviour and by the worktree tooling:

- Sessions that will commit, branch, merge or rebase enter their own worktree first. Read-only
  sessions may share.
- Banned in a shared checkout, no exceptions: branch switching, `commit --amend`, `rebase`,
  `reset --hard`, any history rewriting.
- If committing in a shared tree at all (docs-only, no other session active): verify
  `git branch --show-current && git log -1 --oneline` in the same tool call as the commit; a
  surprise is a full stop.
- Bootstrap is cheap when caches are shared: dependency install in a fresh worktree took 6 s
  (frontend) and 1 s (backend) `[measured 2026-09-07]`.

**Parallel agents on one tree:** explicit file ownership per agent (OWN / APPEND ONLY / MUST
NOT TOUCH); re-read shared files (schema index, locale files, migration directory) before
editing; leave broken-looking code you did not write alone (another agent's in-progress work);
run only the tests and lint for files you changed; stage by explicit path; never push, merge
to main or deploy from a worktree agent. The orchestrator merges sequentially and runs the full
suite before pushing. Migration numbers: check the latest before creating one; renumber on
collision.

**Worktree Bash guard.** Worktree-isolated sessions get a guard that refuses anything it cannot
prove stays in the worktree: computed paths, `time (…)`, heredocs mentioning git, relative
`cd`, edits to the shared checkout. Cost: about 6 refused commands per cycle
`[measured 2026-09-07]`. Use absolute paths, the editor tools on worktree paths, plain commands.

**Nested worktrees poison naive walkers.** The agent runtime nests other branches' worktrees
under the repo (`.claude/worktrees/`). Any scanner that prunes by directory name and ignores
the ignore file reads every nested tree: the ratchet gate went 3 of 6 red in the primary
checkout (6,222 escapes, 286 functions) until its walkers were taught to skip them; the
complexity analyzer sees paths without a leading slash, so the glob `*/.claude/*` never
matched `[measured 2026-09-07]`.

**Gates must be worktree-safe; three of them were not.** Measured on the reference
implementation `[measured 2026-09-16]`, each a gate that ran and reported without judging the
change:

- *Hook roots.* After a mid-session worktree switch the agent runtime's hooks run with the
  working directory in the worktree but `CLAUDE_PROJECT_DIR` still naming the main checkout.
  A Stop hook rooted on that variable graded main while the agent edited the worktree, and
  reported clean 344 times. Rule: a hook takes its root from the hook input's `cwd`, then the
  repository top-level; never from the launch-directory variable.
- *Per-checkout gate state.* Baselines, coverage reports and gate receipts are gitignored, so
  a fresh worktree has none. A gate that needs them either fails to run on every stop (the
  architecture gate exited 2 and blocked once per turn under a worktree launch) or cannot be
  satisfied from the checkout that pushes (a receipt earned in the station worktree was not
  found by the pre-push hook in the main checkout after the merge). Rule: state the gate
  reads is shared across worktrees, keyed by content (receipts keyed by tree id live under the
  main checkout root, found via `git rev-parse --git-common-dir`), or seeded from the main
  checkout when missing (the architecture check grades against main's pinned baseline). A
  gate that cannot find its state still blocks; it never passes.
- *Git hook path.* `core.hooksPath` set to an absolute path runs the main checkout's copy of
  the pre-commit and pre-push hooks in every worktree, so a branch that changes a hook cannot
  exercise it until merged. Rule: the path is relative (`scripts/git-hooks`); the project
  checker should verify that, not just that it is set.

**Worktrees are never collected.** The runtime creates its worktrees locked and removes only
the untouched ones; stations placed by hand are forgotten once their PR merges; worktrees
created inside a session's temporary directory die with the session and leave dangling
metadata. 18 were hanging across the operator's repositories, 9 of them removable
`[measured 2026-09-16]`. Rule: stations live beside the checkout (`<repo>.worktrees/<name>`),
never inside a temporary directory, and a scheduled collector removes every worktree whose
head is an ancestor of the default branch or whose branch has a merged PR, provided its tree
is clean; everything else it lists with the reason it stays. Ghost entries are pruned.

**Two config directories.** A plain-terminal agent and a canvas-runtime agent on the same
machine use different config directories; a plugin, an MCP server or a marketplace registered
in one is absent in the other. Register in both or expect a silent no-op.

## The sandbox

A devcontainer template from the group standard: host-enforced egress gateway, scoped
credential delivery, team-context mount, memory engine wiring, one-word launcher. Booted and
measured on the legacy core `[measured 2026-09-04]`.

**Egress is real, not advisory.** An allowlisted host returned 200; a non-allowlisted host
failed with curl 56 (the gateway refused); stripping the proxy environment to go direct failed
with curl 6 (no DNS, no route) because the workload sits on an internal network with no
NET_ADMIN. Bypass and allowlist are both closed. A new domain or a second model vendor is a
reviewable config diff.

**Toolchain through the gateway.** Two JDKs, toolchain paths written by a setup script, JVM
proxy settings supplied through `JAVA_TOOL_OPTIONS` (the `*_PROXY` variables do not reach the
JVM). The build tool downloaded its own distribution and configured all 75 projects.

**Three constraints found in the boot:**

1. **The sandbox cannot run in a git worktree.** A worktree's `.git` is a file pointing at an
   absolute host path outside the mount; every git command fails and post-create dies with exit
   128. Sandboxed repos must be real clones. This collides with worktree-per-turn isolation, so
   it is one or the other per turn. A local clone with hardlinked objects took 0.7 s for a 135 MB
   `.git`. Git hooks do not travel with a clone; reinstall the pre-push guard in every new one.
2. **No Docker socket inside the box, by design.** Self-provisioning test containers cannot
   work there. Two provisioning paths exist: an ephemeral container flag on the host, a compose
   database sidecar in the sandbox (internal-only, no egress, no socket exposed to an agent). The
   sidecar is the better shape anyway.
3. **The scoped bot identity is a hard blocker, not a nice-to-have.** Resolving the group's
   private packages failed with "Username must not be null!": auth, not allowlist. The sandbox
   has no credential. Never paste a personal token: the build cache is a machine-wide shared
   volume. Until a scoped token (contents plus package read) exists, the box cannot build, so
   there is no autonomy in it.

Smaller boot findings, all fixed or recorded: the launcher reuses running containers, so an
override edit is silently ignored until a force-recreate; the template sidecar shipped an older
database major than CI and stock `max_connections`, both corrected in the override slot; a
feature in the lock file was unpinned; the environment check reported the memory engine
missing and called it expected while the post-create step never installed it (memory reconcile
and session injection silently skipped).

## Identity

- Attended work runs as the person driving it.
- Unattended runs use a scoped service identity: contents plus PR write, nothing more. Boot
  checks refuse a personal token.
- No service-account key files; federated identity only.
- Managed settings at the organisation level are the enforcement tier above local hooks: the
  local pre-push guard is the solo stand-in until the scoped bot identity lands.

## Local-only as an explicit phase

While a loop is being proven against a production core, everything stays local: no push to
any remote, no PR, no comment, no CI trigger. Pulls are fine; data flows in, never out. The rule
is written in the project's agent instructions and enforced by a pre-push hook that rejects
every push on both the main clone and its worktrees (which share hooks). The lift is an
explicit, per-action statement from the owner; "the loop looks ready" is not a lift.

Verify the guard is present and firing before trusting it: a dry-run push must be blocked.

## Test data isolation

A shared database port is a hazard when two projects' test suites default to it. The legacy
core's build defaulted its test datasource and its schema-cleanup task to the same port the
reference product's database listens on, and the cleanup task drops every schema matching a
pattern older than 24 h in whatever database it reaches. A dedicated container on a distinct
port, a mandatory port flag, and a post-run isolation check (no foreign test schemas in the
shared database) `[measured 2026-09-04]`.

For browser tests from a worktree against a shared local stack: pin the compose project name
to reuse the primary database and copy the runtime encryption key from the primary; neither
was documented `[measured 2026-09-07]`.
