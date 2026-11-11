# chisle, copied into the software-factory marketplace

- Upstream: https://github.com/JayPokale/Chisle, MIT (see `LICENSE`).
- Pinned commit: `a5486fa112c961f9b25349a29ede38cc9f2a1a5c` (tag v3.0.0).
- Copied: `.claude-plugin/plugin.json`, `hooks/`, `skills/`, `LICENSE`. Left out: the installers,
  benchmarks, site, docs, and the rule files and command files for other agents, which Claude Code
  does not load.
- Version: `3.0.0+sf.2` in `plugin.json` and the marketplace entry. Upstream is `3.0.0`; the
  suffix counts the changes made here. Claude Code caches an install under its version, so a
  change to this copy without a new version never reaches a machine that already installed it.
- Two changes, both in `hooks/chisle-activate.js` (SessionStart):
  - the update check (step 4) is off unless `CHISLE_UPDATE_CHECK=1`. Upstream it is on, calls
    the npm registry at every session start and tells the session to update from upstream,
    which would route around this pin;
  - the status-line nudge (step 3) is off unless `CHISLE_STATUSLINE_NUDGE=1`. Upstream, when
    `settings.json` has no `statusLine`, it tells the model to proactively offer to edit the
    user's settings.

To move the pin: copy the same paths from a newer upstream commit, review the diff, re-apply the
changes above, and update the pin here and in `deploy/README.md` in the same pull request.
