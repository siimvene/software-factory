# claude-md — PLG rule-file templates

CLAUDE.md is the PLG standard rule file (decided 2026-08-06): it's what Claude
Code, the org's standard agent runtime, loads natively. Using another tool? Copy
CLAUDE.md and rename it to whatever that tool expects (e.g. AGENTS.md for
standalone Codex).

| Template | Use for |
|---|---|
| [`project/CLAUDE.md`](project/CLAUDE.md) | One per repository, version-controlled. Repo conventions, canonical build/test/run commands, protected areas, review expectations. |
| [`multi-repo-folder/CLAUDE.md`](multi-repo-folder/CLAUDE.md) | A workspace folder holding several related checkouts. Routes the agent to each project's own CLAUDE.md. |

Keep CLAUDE.md concise — long files get skimmed. When a prompt goes off the
rails, capture the lesson in CLAUDE.md so the whole team avoids the same trap.

Source: graduated from the GAT "Preparations before you start working on first
task" page (a group engineer); this repo is the canonical copy.
