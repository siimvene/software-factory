# Wiring files, from the reference implementation

Copied from kvart at `e6b90e18` (2026-09-16) with placeholders where a value is the project's
own. Each file says at its top what it does and why; this index says where it goes and what to
edit. The scaffold runbook ([../02-scaffold-a-project.md](../02-scaffold-a-project.md)) copies
them in order.

| File | Goes to | Edit | Why it exists |
|---|---|---|---|
| `claude/settings.json` | `.claude/settings.json`, tracked | nothing for a first run; add project hooks below the sensor ones | the sensor hooks (cleat guard and Stop, enola Stop and SessionStart) and the chisle plugin pinned to a tag; PATH-guarded no-ops without the binaries |
| `claude/mcp.json` | `.mcp.json` | nothing | the ripwire and enola MCP servers, found on `~/.local/bin` |
| `claude/rules/ripwire.md` | `.claude/rules/ripwire.md` | nothing | the orientation-map verbs and the three "do not" defaults |
| `claude/rules/enola.md` | written by `enola install --targets=claude`; this copy is the reference | nothing | the architecture-map verbs; `enola install` overwrites it |
| `claude-hooks/enola-stop.sh` | `scripts/claude-hooks/` | nothing | `enola hook stop` cannot fail; this runs `enola check` and blocks once on a violation |
| `git-hooks/pre-push` | `scripts/git-hooks/` | the receipt section names the reference project's surfaces; drop or port it | the ratchets before code leaves the machine; coverage gate only with a fresh report |
| `git-hooks/commit-msg` | `scripts/git-hooks/` | nothing | `Provenance: human` or `Provenance: agent:<name>` on every commit; merges exempt |
| `git-hooks/post-commit` | `scripts/git-hooks/` | the team store path | memory records touched by the commit, surfaced at the moment they may have gone stale |
| `git-hooks/pre-commit.example` | port per stack | everything below the header | the reference stack's staged-file tripwires (lint, single migration head, staged tests) |
| `git-hooks/README.md` | `scripts/git-hooks/` | nothing | the one-line install: `git config core.hooksPath scripts/git-hooks` |
| `github/workflows/gates.yml` | `.github/workflows/` | the coverage artifact step if the test job does not upload one | cleat, enola, trivy as required checks with stable job names |
| `github/workflows/jira-sync.yml` | `.github/workflows/` | nothing; needs the `ci` workflow name and the vars/secrets | the ledger follows PR events and CI verdicts; always runs main's script |
| `github/workflows/pr-ticket-key.yml` | `.github/workflows/` | nothing | a PR names its ticket or carries `no-ticket` |
| `github/ruleset.json` | `gh api repos/<org>/<repo>/rulesets --input` | `required_status_checks` to the job names that exist | PR required, five green checks, no force-push, no deletion, empty bypass list |
| `ci/jira_sync.py` | `scripts/ci/` | nothing; `JIRA_PROJECT_KEY` from the environment | the ledger transitions, planned from the current status; stdlib only |
| `ci/test_ci_jira_sync.py` | `tests/unit/` | the module path at the top if `scripts/ci` moves | the tests for the above; run with pytest from the repo root |
| `bin/jira` | `~/.local/bin/jira` | nothing; configured by `~/.config/factory/jira.env` | pickup, link, deploy write-back from the operator's machine, token from the keychain |
| `memspec/config.yaml` | `.memspec/config.yaml`, the only tracked file under `.memspec/` | the team store path | the engine binding: team store read-only, scratch read-write |
| `memspec/memspec.yaml` | `.memspec.yaml` | the team repo name | the standard's pointer; the engine does not read it yet, the standard's check does |
| `jira/workflow_payload.json` | Jira REST `POST /rest/api/3/workflows/create` | every `statusReference` (site-issued UUIDs) and the status `id`s | the six-status chain with three loopbacks, as the reference project created it |

Not templated on purpose: `quality.json` and the baselines (attach writes them, a person
re-cuts them), `enola-intent.yaml` (the shape is in
[../../templates/sensor-config-examples.md](../../templates/sensor-config-examples.md), the
layers are the project's), the receipt-checked browser and static-analysis gates (their scope
maps are the project's route and module tables), and the project's own `ci.yml`.
