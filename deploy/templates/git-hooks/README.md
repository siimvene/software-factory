# Git hooks

Version-controlled git hooks for this repo. To enable, run **once per clone**:

```bash
git config core.hooksPath scripts/git-hooks
```

## post-commit

Memspec reconciliation. Fires after every code commit; greps memspec entries
(project-local `.memspec/` and global `~/.memspec/`) for files touched by the
commit and surfaces any matches.

**Purpose:** close the gap between "code changed" and "agent knows the relevant
memspec fact is now stale." Without this, memory drift accumulates silently
until time-based decay fires (90 days for facts) — by which point agents have
been operating on stale truth for months.

**Behavior:**
- Informational only — does not block the commit
- Only fires on commits that touch code files (skips pure-doc commits)
- Output goes to stderr so it surfaces in interactive shells without polluting
  scripts that read commit stdout

**When the hook surfaces entries:**
- Fact still true → leave alone (or `memspec_promote` if you re-verified)
- Your commit invalidated it → `memspec_correct` immediately, do not defer
- Can't verify quickly → flag for follow-up; don't pretend you didn't see it
