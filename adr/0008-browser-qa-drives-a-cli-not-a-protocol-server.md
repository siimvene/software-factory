# 0008. The browser QA pass drives a CLI, not a protocol server or a browser extension

- **Status:** accepted
- **Date:** 2026-09-10
- **Deciders:** the operator (Siim), the principal session that proposed it

## Context

Step 4 of the verify gate ([06-verify-gate](../docs/06-verify-gate.md)) is a behavioural pass:
an agent walks every UI surface the diff touches, as the right persona, in a real browser, and
reports findings with evidence. On kvart this pass had two runtimes. The primary was a browser
extension that exposes a headed Chrome to the agent through a protocol server; it needs a
display, a running desktop browser and a human's session. The fallback was a Playwright script
the agent wrote by hand for each pass, under a gitignored runtime directory, judged from
screenshots. Every measured pass used the fallback `[measured 2026-09-09]`. Two consequences:

- Each pass began by writing harness code. Tokens went into plumbing, and a defect in the
  throwaway script read as a defect in the product, or hid one.
- Neither runtime works from an unattended station worktree: the extension needs a desktop
  session, and the skill that describes the pass was itself gitignored, so no worktree had it
  `[measured 2026-09-10]`.

Two further constraints shaped the choice. The design already rejects pushing a page's full
accessibility tree into the agent's context on every step, which is what a protocol-server
runtime does by default. And the PM surface will attach a prototype to a UI ticket
([15-design-system](../docs/15-design-system.md)), so the verify pass needs a structural view of
the rendered page to check against, not only pixels.

The alternative that appeared on 2026-09-01: a command-line front end to Playwright, published
by the Playwright maintainers, headless by default, one shell command per browser action, with
the page tree, console log, network log, screenshot and trace written to files in the working
directory instead of returned to the caller.

## Decision

We will drive the browser QA pass through the Playwright command-line tool. One named session per
persona; login once, save the storage state, restore it instead of logging in again. Every
surface leaves a snapshot, a console extract, a network extract and a screenshot on disk; every
exercised interaction is wrapped in a recording and a trace, and the recorded code is attached to
the codify candidate it supports. The skill ships in the repository so a station worktree has it.
The browser extension remains available as an optional headed mode when a person wants to watch;
a hand-written script is no longer an accepted fallback: a missing runtime stops the pass.

Scope limit: this is the agent's exploratory runtime. The deterministic browser gate (the
receipt-checked spec run of [06-verify-gate](../docs/06-verify-gate.md)) is unchanged and stays
on the test runner.

## Consequences

- **Positive:** the pass runs unattended and headless from any worktree; the agent's context
  carries a few lines per action while the evidence sits on disk (a 419 KB page tree cost 8 lines
  of context `[measured 2026-09-10]`); the recorded code closes the gap between "this flow
  deserves a spec" and a spec draft; the page tree gives the design-system check something
  structural to compare against.
- **Cost:** a second Playwright engine on the machine (the CLI pins a pre-release ahead of the
  test runner's version), so a rendering finding must be checked against the runner's browser
  before it is called a regression; one more tool to install per machine; the CLI is young, and
  its first version in use already has one defect the skill routes around (the auto-named page
  tree after a navigation on the app is written empty; an explicit filename works).
- **Follow-ups:** the design-system VERIFY row (patterns checked from the page tree) becomes
  buildable and is owned by the verify gate; the CLI enters the repository's dependency
  manifest only after the supply-chain age window, owned by the code owner; the first measured UI
  cycle on this runtime updates [STATUS.md](../STATUS.md).

## Alternatives considered

- **Protocol server (the Playwright MCP server):** same engine, but it returns the accessibility
  tree to the agent on every step, which is the context cost the design rejects; and it is one
  more long-running process per station to supervise.
- **Browser extension (headed Chrome through a protocol server):** needs a display and a
  person's browser session; cannot run from an unattended station; kept as the optional headed
  mode.
- **Hand-written Playwright script per pass:** the measured status quo; harness code written
  under time pressure on every pass, invisible to review, and a source of false findings.
- **Only the deterministic spec suite, no exploratory pass:** rejected earlier
  ([06-verify-gate](../docs/06-verify-gate.md)); the specs cover the routes they were written for
  and nothing the diff newly touches.

## Evidence

- Shakedown of the CLI against the running kvart stack `[measured 2026-09-10]`: dev-login
  redirect chain lands the persona; storage state saved after the callback restores a logged-in
  session in a fresh browser without a second login (saved during the callback it carried the
  refresh cookie alone); console and network extracts as text; recording prints Playwright code
  for the walked actions; trace written per surface; teardown leaves no process.
- The e2e gate analysis of 2026-09-06 (five gaps in the browser pass) and the receipt gate of
  2026-09-09, both in [06-verify-gate](../docs/06-verify-gate.md).
