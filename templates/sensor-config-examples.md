<!--
  SENSOR CONFIG EXAMPLES. Read by whoever wires the mechanical layers into a repository
  on day one, and by anyone later asking why a gate is shaped the way it is.
  These are annotated shapes, not a config you can paste unchanged: the module names,
  ceilings and thresholds are placeholders for your repository's facts. Everything
  project-specific lives in these files and nowhere else, so a new language or a new rule
  is a config entry rather than a patch to a check.
-->

# Sensor config examples

## 1. Quality ratchets (`quality.json`)

The ratchet layer holds a change to what the repository already achieves. Existing debt is
baselined once, and the baseline is only ever allowed to tighten: a new violation fails,
and a baselined function that gets worse fails too. The baselines record debt a person
accepted, so only a person loosens them, in a reviewed commit.

```json
{
  "project": "<project name>",

  "doc_size": [
    { "file": "<agent instructions file>", "ceiling": 2800 },
    { "file": "README.md", "ceiling": 2300 }
  ],
```

Documents an agent reads every session have a token ceiling. Without one they grow until
the instructions crowd out the task. The ceiling is a number a person chose, not a default.

```json
  "escapes": {
    "roots": ["."],
    "languages": ["<language>", "<language>"],
    "skip_dirs": ["quality"],
    "baseline": "quality/escapes-baseline.json"
  },
```

Escapes are the ways a check gets switched off in place: a suppression comment, an untyped
cast, a skipped test, a command that always exits zero. They are keyed by site, so moving
one does not silently forgive it. The gate directory skips itself.

```json
  "duplication": {
    "roots": ["."],
    "languages": ["<language>"],
    "min_lines": 6,
    "baseline": "quality/duplication-baseline.json",
    "base_ref": "origin/main"
  },
```

`base_ref` is what "changed" means for this repository. The duplication gate only judges
blocks inside the lines the diff touched, plus the overall duplicated share, so an agent
copying a block instead of extracting it fails while the pre-existing clones stay in the
baseline.

```json
  "changed_coverage": {
    "report": "coverage.xml",
    "minimum": 0.8,
    "min_lines": 20,
    "base_ref": "origin/main"
  },
```

Coverage on changed lines only. Whole-repository coverage moves too slowly to gate a
single change, and a per-module average hides exactly the file the diff touched. The report
path is whatever the test run already writes; `min_lines` stops a two-line change from
being judged on a ratio.

```json
  "conventions": {
    "rules": [
      {
        "name": "<layer>-must-stay-pure",
        "pattern": "^[ \\t]*(?:from|import)\\s+(?:<forbidden module>)\\b",
        "roots": ["src/<domain layer>"],
        "extensions": [".<ext>"],
        "message": "<why this rule exists, what to do instead, and how many sites existed when it was adopted>"
      }
    ],
    "baseline": "quality/conventions-baseline.json"
  },
```

A convention is a rule the team wrote about its own code, enforced at the site that breaks
it, with the team's own message attached. Two details are worth copying: the pattern allows
leading whitespace, because anchoring at column zero leaves a one-keystroke bypass through
an import inside a function; and the message says why, so the agent that trips it can fix
the design rather than the regex.

```json
  "complexity": {
    "tool": "<complexity analyzer>",
    "languages": ["<language>"],
    "exclude": ["*/node_modules/*", "*/migrations/*", "*/tests/*", "*/vendor/*"],
    "ceilings": { "cc": 8, "lines": 60 },
    "baseline": "quality/complexity-baseline.json",
    "_note": "Excludes are deliberate, not tuning to pass. Generated migrations are linear by nature and every new one would trip the line ceiling. Test trees are excluded because this repository mandates a test per endpoint, and a gate that fights test-writing gets switched off. Escapes, conventions and duplication still cover tests."
  }
}
```

Every exclusion carries its justification in the file. An exclusion without a stated reason
is indistinguishable from tuning the gate until it passes, which is the failure mode this
whole layer exists to prevent.

## 2. Architecture layers (`enola-intent.yaml`)

The ratchets judge files. The architecture layer judges the shape between them: a reference
from a lower layer to a higher one, a cycle spanning four files, coupling nobody asked for.
None of that lives in any single file, so no file-by-file linter can see it.

```yaml
# Layer declaration, outermost first. A reference from a lower layer to a higher one is a
# violation. Derived from the repository's own structure document, so the declaration and
# the prose cannot drift apart silently.
layers:
  - {name: entry,      paths: ["src/<pkg>/api/**", "src/<pkg>/tasks/**", "src/<pkg>/main.<ext>"]}
  - {name: service,    paths: ["src/<pkg>/service/**"]}
  - {name: domain,     paths: ["src/<pkg>/<domain engine>/**", "src/<pkg>/integrations/**"]}
  - {name: models,     paths: ["src/<pkg>/models/**"]}
  - {name: foundation, paths: ["src/<pkg>/core/**", "src/<pkg>/config/**", "src/<pkg>/security/**"]}
```

Order is the whole content of the declaration: `entry` may reach `service`, `service` may
reach `domain`, and nothing may reach back up. Five layers is usually enough; more layers
than the team can name from memory means the declaration will be edited to fit the code
rather than the other way round.

```yaml
# A declared crossing: the one edge that is allowed, stated with its reason.
rules:
  - id: domain-depends-on-ports-only
    allow: domain
    only: [ports]
    via: depends_on
    because: "The domain names the interfaces it needs and nothing that implements them. An adapter can be replaced without the domain noticing, and the domain can be exercised with no adapter present."

  - id: domain-names-no-adapter
    forbid: domain
    to: adapters
    via: calls
    because: "A domain that calls an adapter directly has a hidden dependency on one implementation, and every test of the domain has to bring that adapter with it."
```

A crossing is declared, not discovered. `because:` is not documentation: it is what the
gate prints at the violation, which is the difference between an agent fixing the design
and an agent adding a suppression.

## 3. Agent hook wiring (`.claude/settings.json` and `.mcp.json`)

Hooks are where the gates stop being something an agent is asked to run and become
something the harness runs regardless. Three moments are worth wiring.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "PATH=\"$HOME/.local/bin:$PATH\"; command -v <arch tool> >/dev/null 2>&1 && <arch tool> hook session-start || :",
            "timeout": 60
          }
        ]
      }
    ],
```

SessionStart pins the architecture baseline before the first edit, so the change can be
graded afterwards against what the repository looked like when the session began. Without a
baseline taken up front, nothing can tell a regression this session introduced from the
hundreds already present.

```json
    "PreToolUse": [
      {
        "matcher": "Bash|Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "PATH=\"$HOME/.local/bin:$PATH\"; if [ -f quality/bin/gate.py ]; then python3 quality/bin/gate.py --guard; fi"
          }
        ]
      }
    ],
```

The PreToolUse guard runs before the edit, not after, and its job is narrow: refuse edits
to the gates themselves, to the config, and to the baselines. It is what makes "the agent
cannot loosen the policy" a mechanism rather than an instruction. The guard exits non-zero
on refusal so the harness actually blocks the call.

```json
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "PATH=\"$HOME/.local/bin:$PATH\"; if [ -f quality/bin/gate.py ]; then python3 quality/bin/gate.py --hook --changed; fi"
          }
        ]
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "PATH=\"$HOME/.local/bin:$PATH\"; command -v <arch tool> >/dev/null 2>&1 && <arch tool> hook stop || :",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

Stop runs the gates on the changed files and hands a failure back to the agent as the next
thing to fix, and takes the after-snapshot for the architecture diff. This is the moment
that turns a gate from a report someone reads into a loop the agent has to close.

Both commands use the same defensive shape, and it matters:

```sh
PATH="$HOME/.local/bin:$PATH"; command -v <tool> >/dev/null 2>&1 && <tool> hook stop || :
```

The `PATH=` prefix exists because a hook runs in a non-interactive shell that never sourced
the profile, so a tool installed in a user directory is simply absent. The `command -v`
test plus the trailing `|| :` make the hook a no-op in a checkout where the tool is not
installed, instead of failing every session with a confusing error. A hook that breaks
clean checkouts gets deleted by the next person, which is worse than a hook that quietly
does nothing there.

```json
{
  "mcpServers": {
    "<map tool>": {
      "command": "sh",
      "args": ["-c", "PATH=\"$HOME/.local/bin:$PATH\"; exec <map tool> --mcp"]
    },
    "<arch tool>": {
      "command": "sh",
      "args": ["-c", "PATH=\"$HOME/.local/bin:$PATH\"; exec <arch tool>"]
    }
  }
}
```

The same PATH problem applies to server launchers, which is why they go through `sh -c`
with an explicit `exec`. These two servers give the agent deterministic answers about the
codebase (what calls this, what does this change touch) so that orientation is a query
rather than a fan-out of whole-file reads.
