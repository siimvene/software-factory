# Workstation setup, macOS

One machine, set up so that a session started in any wired repository has the whole line
available: the agent runtime with its memory, the second and third vendor for the verify gate,
the four sensors, the scanners, the plugins, and the credentials each of them needs. Apple
silicon assumed; Intel differs only in the enola archive name.

Two profiles. The **engineer** profile is everything below. The **PM** profile is section 1,
section 2, the PM lines of section 6 and section 8, and nothing else: a PM's agent reads specs
and drafts tickets, it never runs a gate. The checker knows both: `bin/check-workstation.sh`
and `bin/check-workstation.sh --pm`. Run it first on a machine you think is done; the lines
it prints are the list of what is not.

Order matters in two places only: the memory engine before the agent hooks that call it, and
the second vendor's CLI before the consort plugin that wraps it. Everything else can be
installed in any order.

## 1. Base toolchain

```
xcode-select --install                     # once; git and the compilers
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git gh jq uv node pnpm tmux shellcheck actionlint ast-grep trivy sonar-scanner playwright-cli
brew install --cask claude-code codex gcloud-cli orbstack
```

Why these: `uv` runs every Python tool in its own environment (cleat's helper, the ledger
script); `node` carries memspec, the Gemini CLI and Pi; `pnpm` is the frontend package manager
the reference project uses; `ast-grep` feeds two optional cleat gates; `trivy` is the scanner
tier; `sonar-scanner` and `playwright-cli` serve the static-analysis and browser legs;
`orbstack` is the Docker daemon (Docker Desktop works identically). Python itself comes with uv;
do not manage a system Python.

Sign in to the two hosts now, because later steps assume it:

```
gh auth login                              # GitHub, the account that will own PRs and merges
gcloud auth login                          # only if the Gemini leg runs on Vertex (section 3)
```

## 2. Agent runtime and memory

```
claude                                     # first run logs you in; then exit
npm install -g memspec@0.11.0 --min-release-age=0
memspec init ~/.memspec                    # the personal scratch store; installs the two session hooks
claude mcp add --scope user memspec -e MEMSPEC_ROOT="$HOME/.memspec" -- memspec-mcp
```

`--min-release-age=0` is there for one reason: a workstation that already carries the
supply-chain setting `min-release-age=30` in `~/.npmrc` (the operator's machines have it; a
fresh Mac does not) refuses to install a version published less than 30 days ago, and a
pinned memspec release is exactly that for its first month (0.11.0 shipped 2026-09-16). The flag lifts the
gate for this single install and nothing else; the pin, not the age, is the trust decision
here (the package is ours). Leave it in place even on a machine without the setting, it is a
no-op there.

`memspec init` writes `memspec-session-start.js` and `memspec-consolidate.js` under
`~/.claude/hooks/` and wires them into `~/.claude/settings.json`; the MCP registration gives
every session the `memspec_*` tools. Verify with `claude mcp list` (memspec listed, connected)
and `memspec stores` from any directory (the global store, read-write).

The store is personal scratch. Durable team knowledge lives in the team-context repo and
reaches it through promote PRs; the scaffold runbook binds each code repo to that store
read-only. Nothing in this section is per project.

## 3. Second and third vendor: the verify gate's reviewers

The gate is a two-leg panel, both legs required, hard-fail if either is unreachable
([docs/06](../docs/06-verify-gate.md)). Leg one is Codex; leg two is Gemini through Pi on
Vertex. Install the runtimes, then the plugin that drives them.

```
codex login                                # ChatGPT subscription or API key; writes ~/.codex/auth.json
codex exec 'Reply with exactly: CODEX_ALIVE' < /dev/null     # reachability, not budget
npm install -g @google/gemini-cli@0.58.0 @earendil-works/pi-coding-agent@0.84.1
gcloud auth application-default login      # ADC for the Vertex leg; or a service-account key file
git clone https://github.com/siimvene/consort ~/git/consort && git -C ~/git/consort checkout 5f68ef6
claude plugin marketplace add openai/codex-plugin-cc && claude plugin install codex@openai-codex
claude plugin marketplace add siimvene/consort   && claude plugin install consort@consort
```

Why both a plugin and a checkout of consort: the plugin provides the `/consort:*` commands and
the companion-runtime integration; the panel script and the merge tool are run from the
checkout (`~/git/consort/scripts/consort-panel.sh`, `merge-findings.mjs`), which is how the
reference machine runs the gate. `codex exec` always reads stdin: redirect it from `/dev/null`
or it waits forever, which is the 2h08m stall in the trial report.

The panel configuration lives in the `env` block of `~/.claude/settings.json` so every session
inherits it (section 7). A review of a multi-hundred-line diff that returns in seconds did not
run; the panel's `[label]` stderr lines and its `seconds` are the evidence that it did.

## 4. Sensors

The four mechanical layers of [docs/05](../docs/05-sensor-stack.md). Binaries per machine, in
the user's local bin; the project-side wiring is the scaffold runbook's job.

```
mkdir -p ~/.local/bin
# sensor 3: cleat is vendored into each project by its attach script; keep the fork checked out
git clone https://github.com/siimvene/cleat ~/git/cleat && git -C ~/git/cleat checkout c2947a5
uv tool install lizard==1.23.0             # the complexity analyzer cleat calls; pin = the baselines' version
# sensor 4: enola, pinned release, checksum-verified (the darwin-arm64 archive on Apple silicon)
V=0.4.19; A=darwin-arm64
curl -fsSLO "https://github.com/enola-labs/enola/releases/download/v$V/enola-$V-$A.tar.gz"
curl -fsSLO "https://github.com/enola-labs/enola/releases/download/v$V/enola-$V-$A.sha256"
shasum -a 256 -c "enola-$V-$A.sha256" && tar -xzf "enola-$V-$A.tar.gz" && install -m 0755 "enola-$V-$A" ~/.local/bin/enola
# sensor 1: ripwire, from its installer at the pinned commit the reference binary was built from (0.4.0).
# Read skills/install.sh before running it: it is a script from a third-party checkout, not a signed release.
# RIPWIRE_NO_ACTIVATE=1 keeps it from editing your agent config.
git clone https://github.com/redhat-et/ripwire /tmp/ripwire && git -C /tmp/ripwire checkout e663ca8f8
less /tmp/ripwire/skills/install.sh && RIPWIRE_NO_ACTIVATE=1 bash /tmp/ripwire/skills/install.sh
# sensor 2: chisle is a marketplace plugin registered PER PROJECT by the scaffold, pinned to tag v3.0.0; nothing to do here
```

Make sure `~/.local/bin` is on PATH in `~/.zshrc`. The reference machine keeps lizard in its own
virtualenv with a symlink; `uv tool install` is the same thing with less ceremony and is what
CI does. Why enola is pinned by checksum and not `brew`: the CI job installs the same release
the same way, so the local check and the required check agree.

`enola install` and `ripwire wrap claude` write instructions into agent files. Run them in the
project, from the scaffold runbook, not globally: the reference implementation tracks the
resulting rule files per repo and the check in [docs/05](../docs/05-sensor-stack.md) says why
`enola install --targets=agents` pushed a shared file over its size ceiling.

## 5. Scanners and the optional static-analysis leg

Trivy came with section 1 and needs no configuration; the scan script in consort finds it. The
static-analysis leg is optional and reported loudly when absent: every SKIPPED line the scanner
tier prints goes into the gate report unchanged. To have it:

```
docker run -d --name sonarqube -p 9000:9000 --restart unless-stopped sonarqube:community
# browse http://localhost:9000, set the admin password, create a user token, then:
mkdir -p ~/.config/sonar && printf 'export SONAR_HOST_URL=http://localhost:9000\nexport SONAR_TOKEN=<token>\n' > ~/.config/sonar/env
chmod 600 ~/.config/sonar/env
grep -q 'config/sonar/env' ~/.zshenv || printf '[ -r "$HOME/.config/sonar/env" ] && . "$HOME/.config/sonar/env"\n' >> ~/.zshenv
```

`~/.zshenv` rather than `~/.zshrc` because hooks and non-interactive shells read the former. The
scan reads `sonar-project.properties` from the project; without that file the leg is SKIPPED by
design, and a worktree without the file degrades the scan to dependency scanning only, which the
report must say.

## 6. Plugins and the marketplace

User scope, once per machine:

```
claude plugin marketplace add jarrodwatts/claude-hud && claude plugin install claude-hud@claude-hud
claude plugin marketplace add "$HOME/git/software-factory/deploy/marketplace"      # this repository, cloned
```

The `software-factory` marketplace is a directory source, so it points at your clone of this
repository; `git pull` is the update. It holds the eight plugins the loop uses from the group's
catalog at pinned versions ([README.md](README.md) has the pins). Install per role:

| Role | Install | Why |
|---|---|---|
| PM | `claude plugin install pm-workspace@software-factory` | the workspace setup, ingest, ticket, readiness, improver, splitter, graduate skills |
| PM | `claude plugin install secret-guard@software-factory` | a pre-tool hook that refuses reads of credential files; a deterrent, not a boundary (it fails open without `jq`, and a renamed file passes) |
| Engineer | `secret-guard`, `spec-repos`, `team-memory`, `plg-rules`, `dev-hygiene` from the same marketplace | the spec chain, the promote PR, the rule packs the reviewer loads, the pre-completion pass |
| Engineer, optional | `solo-review`, `ux-qa` | the single-model fallback (never the gate) and the browser QA prompt |

Project scope, written by the scaffold into the repo's tracked settings: `chisle` pinned to tag
v3.0.0. Do not install it at user scope; the pin is the point and the pin lives in the repo.

The `claude plugin marketplace add` commands above track each source's default branch, and a
plugin runs code. Where the source has tags, pin it the way the scaffold pins chisle: an
`extraKnownMarketplaces` entry in `~/.claude/settings.json` with a `ref` (consort tags its
releases; check the other two before pinning). An unpinned marketplace is a named shortcut.

Known trap: two config directories. A canvas or terminal-multiplexer runtime may start Claude
Code with its own `CLAUDE_CONFIG_DIR`; a marketplace, plugin or MCP server registered in one
directory is absent in the other, silently. Register in both, or run the checker under each.

## 7. Settings that every session inherits

Merge this into `~/.claude/settings.json` (the memspec hooks are already there after section 2).
Values in angle brackets are yours; nothing here is a secret.

```json
{
  "env": {
    "CONSORT_REVIEWERS": "codex,pi:google-vertex",
    "CONSORT_GCP_PROJECT": "<gcp project the Vertex calls bill to>",
    "CONSORT_GEMINI_LOCATION": "global",
    "CONSORT_GCP_CREDENTIALS": "<path to a service-account key, only if ADC is not used>"
  },
  "modelOverrides": { "claude-opus-5": "claude-opus-4-8" },
  "statusLine": { "type": "command", "command": "<what claude-hud:setup wrote>" }
}
```

Why each line: `CONSORT_REVIEWERS` makes the gate a two-leg panel instead of whichever backend
is reachable; the model override is the worker-tier decision in
[docs/03](../docs/03-operating-contract.md) (build stations on the mid tier, the top tier for
debugging and verification, and the alias that resolves to the unstable tier remapped); the
status line shows the served model, context and cost. Run `/claude-hud:setup` once and let it
write the status line entry. The reference machine also sets
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; it is not required by anything in this directory.

## 8. Credentials and identities

None of these go into a repo, a settings file or a memory record.

| What | Where it lives | Set with |
|---|---|---|
| GitHub, your own account | `gh` keyring | `gh auth login` (section 1) |
| Codex | `~/.codex/auth.json` | `codex login` |
| Google ADC, or a key file | `~/.config/gcloud/` | `gcloud auth application-default login`, or `CONSORT_GCP_CREDENTIALS` |
| Jira API token (engineer and PM) | login keychain, service `factory-jira-api-token` | `security add-generic-password -s factory-jira-api-token -a <email> -w '<token>'` |
| Jira site, email, project key, code repo | `~/.config/factory/jira.env` | four lines, see `templates/bin/jira` header |
| Sonar token | `~/.config/sonar/env`, mode 600 | section 5 |
| The bot identity's private key (GitHub App) | `~/.config/github-apps/`, mode 600 | created in the scaffold runbook, leg G6; only the engineer who administers the repo holds it |

The ledger wrapper reads the keychain so the token is never typed into a shell history:

```
install -m 0755 "$HOME/git/software-factory/deploy/templates/bin/jira" ~/.local/bin/jira
jira whoami                                # prints your display name and account id
```

## 9. The PM profile, in one block

A PM's machine gets sections 1 (without the scanners and casks other than `claude-code`), 2, the
PM rows of 6, and the Jira rows of 8. Concretely:

```
brew install git gh jq node && brew install --cask claude-code
claude; gh auth login
npm install -g memspec@0.11.0 --min-release-age=0 && memspec init ~/.memspec
claude mcp add --scope user memspec -e MEMSPEC_ROOT="$HOME/.memspec" -- memspec-mcp
claude plugin marketplace add "$HOME/git/software-factory/deploy/marketplace"
claude plugin install pm-workspace@software-factory && claude plugin install secret-guard@software-factory
bash "$HOME/git/software-factory/deploy/bin/check-workstation.sh" --pm
```

The PM never runs git themselves ([docs/14](../docs/14-pm-surface.md) says why); the engineer
who sets the machine up also clones the specs repo and the code repos read-only next to the
workspace and fills `POINTERS.md`, which is leg M0 of the scaffold runbook. Since 2026-09-15 the
PM reads repositories through those local clones, not through a hosted connector.

## 10. Check, and what the checker cannot see

```
bash ~/git/software-factory/deploy/bin/check-workstation.sh          # engineer
bash ~/git/software-factory/deploy/bin/check-workstation.sh --pm     # PM
```

It proves presence and login state. Three things it cannot prove and you should, once:

- **Budget, not reachability.** `CODEX_ALIVE` proves the CLI answers. The first real panel run
  on a real diff, with its wall-clock in the report, proves the account can pay for one.
- **The Vertex leg bills to the project you named.** The first run of the panel logs to that
  project; look once.
- **The two config directories** (section 6). Run the checker under the second directory if a
  canvas runtime is in use.

## Known traps, from the reference machine

- `npm install -g memspec@<pin>` fails with `No matching version found` although the version
  is on npm: `~/.npmrc` has `min-release-age=30` and the pin is younger than that. Add
  `--min-release-age=0` to that one install (already in sections 2 and 9); the checker prints
  an OPTIONAL line when the setting is present.
- No `timeout` on macOS without coreutils. A delegation's wall-clock cap is
  `perl -e 'alarm N; exec @ARGV' <cmd...>`; a bare `timeout` exits 127 before the child starts
  and reads as an instant success.
- `codex exec` without `< /dev/null` hangs on stdin.
- macOS `ls` has no `--time-style`; `stat -f` instead.
- The Stop hooks run in every wired repo. A session in a repo with a red ratchet is handed the
  failure once; a gate you cannot fix is not a reason to edit the baseline (the guard refuses it
  anyway).
- The frontend test runner and the PDF library on the reference stack need Homebrew's
  libraries on the loader path (`DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`); the repo's
  hooks set it, a bare shell does not.
