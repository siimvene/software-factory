---
name: qa
description: Behavioral UI QA over the pending diff. Fires on "QA this diff", "walk the UI", "run a UX pass", "check the frontend before I push", or any pre-PR request to verify a UI change works in a real browser. Maps changed files to the surfaces they affect, boots the app and logs in using the repo's own contract, drives each surface in a real browser (Playwright), and reports rendering / interaction / console findings ranked by severity. Do NOT use it for logic/correctness code review (that is the code-review consort's job) or for writing/authoring test specs (this walks the running app, it does not add tests). Use it only when the pending diff touches something a user can see or click.
version: 0.1.0
---

# qa — behavioral QA pass over the pending diff

You are the UX consort: a code-review consort reads the diff, you *run* it. Judge the
rendered product the way a careful human tester would. You report findings; you do not
fix them (fixes are a separate, explicitly-requested step).

This is the behavioral review tier that static code review doesn't cover. It runs pre-PR,
before the change leaves the working tree.

## Phase 0 — scope

Collect the pending diff (union of all four):

```bash
git diff --name-only origin/main...HEAD   # unpushed commits (adjust base branch if not main)
git diff --name-only                      # unstaged
git diff --name-only --staged             # staged
git ls-files --others --exclude-standard  # untracked new files (a brand-new page is still a pending change)
```

If nothing user-facing changed, say so and stop — there is nothing behavioral to test.
"User-facing" = any file whose change alters what renders or how the UI behaves:

- UI component / view / template / page files (`.vue`, `.tsx`, `.jsx`, `.svelte`,
  `.html`, framework page dirs), styles (`.css`, `.scss`, Tailwind config), client-side
  state/composables/hooks.
- Localization / i18n message files.
- Backend route / handler / serializer files that a UI surface consumes (a shape change
  there shows up in the browser).

A change confined to build tooling, pure backend batch jobs, docs, or tests with no
rendered surface is out of scope — say which files you're skipping and why.

## Phase 1 — map changed files to surfaces

Build a surface list: for each changed file, the route(s) it renders on, the role/persona
that can reach it, and what to exercise. Mapping rules:

- **A page/route file** → its route. If the router uses file-based routing, derive the
  path from the file path; otherwise grep the route table / router config for the
  component. A route with a dynamic segment (`[id]`, `:id`) needs a real id — create the
  entity first (via the app or an API call) or click through from its list page.
- **A shared component / composable / hook** → grep for its importers and walk up to the
  page(s) that render it. Test those pages, not the component in isolation.
- **An i18n / locale file** → diff it for the changed keys, grep which components use
  those keys, and test those surfaces **in every changed locale**, watching for overflow,
  clipping, and untranslated fallback strings.
- **A backend route / handler** → grep the frontend for the path it serves (the API
  client call, the data hook) and test the consuming pages.
- **A layout / middleware / global plugin change** → smoke the handful of top-level
  surfaces (one representative page each), since the change touches all of them.

For roles: if the app gates surfaces by role/permission, note which role each surface
needs and plan to log in as that role. Surfaces reachable only through auth you can't
drive headlessly (hardware key / WebAuthn, external SSO with MFA) are **untestable via
automation** — list them as untested with the reason, don't fake a pass.

## Phase 2 — resolve how to boot and log in (discovery, not hardcode)

You do not know this app's boot command, URL, port, or test credentials. Resolve them from
the repo's own contract, in this order, and stop at the first that answers:

1. **`CLAUDE.md` (or `AGENTS.md`) Commands section** — a documented run/dev command
   (look for a `Run:` line, a "Dev server" / "Run app" row, a Commands table). This is
   the canonical answer when present.
2. **A project run/dev script** — `package.json` `scripts` (`dev`, `start`, `serve`),
   a `Makefile` / `justfile` target, `bin/dev`, `docker-compose` service, etc.
3. **An e2e harness config** — `playwright.config.*` `webServer.command` + `baseURL`
   (Playwright starts the app itself and names the URL); Cypress `baseUrl`. This often
   also carries the login path.

For **login**, resolve a test session the same way: an e2e auth fixture / setup project
(`storageState`, a global-setup that logs in), a dev-login or seed script the repo ships,
or documented test credentials in `CLAUDE.md`. Use a dedicated test/dev login path when
one exists: never real user secrets, and never anything from outside the repo.

If none of the above yields a boot command **or** a login, **ask the user once**: the
command to start the app (and the URL/port it comes up on) plus one test login for the
role(s) the diff touches. Then suggest they commit the boot command and a **reference** to
the login mechanism (the dev-login script name, the seeded persona name, the env var that
carries the credential) to `CLAUDE.md` so the next run is zero-question - never literal
credentials, passwords, or tokens. If the login is a literal secret, it stays out of git.
Ask once, not per-surface; don't guess and don't loop.

## Phase 3 — stack up

Check whether the app is already running before booting a second copy: hit the URL from
Phase 2 (`curl -s -o /dev/null -w '%{http_code}' <url>`) and its backend/health endpoint
if it has one. Up and serving real content → reuse it.

**Gotcha:** a dev server started without the env/config the app needs to reach its backend
(API base URL, auth origin) renders logged-out or empty on every page. If a reused server
shows empty/anonymous surfaces, it was probably started wrong - but only kill a server
**this run started**. A pre-existing server the run doesn't own showing anonymous/empty
pages → report the mismatch and either boot your own copy on a fresh port or ask the user;
never kill a process the run doesn't own.

If down, start it in the background per the Phase 2 command and poll until healthy
(backend health endpoint returns 200, frontend URL returns HTML). Cold starts with
containers + migrations can take 60–90 s; wait, don't declare it broken early. But set a
ceiling: give up after 5 minutes (or a longer bound if the repo documents one). At the
ceiling, stop the run and report honestly — a SERIOUS finding naming the exact boot
command you ran, the URL(s) polled, and the last output/status you observed. An app that
won't come healthy per its own documented command is itself the finding; don't keep
waiting and don't retry the same boot in a loop.

## Phase 4 — walk each surface

Drive a real browser with **Playwright**. Two ways, in preference order:

1. **A browser-automation MCP**, if one is connected in this session (navigate,
   screenshot, read-console, click/type tools). Load the tools you need in one
   `ToolSearch` call.
2. **A headless script fallback** — a small Playwright script driving Chromium, saving a
   screenshot per surface to the report dir; judge the screenshots by reading them. Place
   the script where the repo's Playwright install resolves (e.g. under the e2e dir) and in
   an ignored/scratch path so you don't leave artifacts in the diff. If the repo has no
   Playwright installed, say so and fall back to whatever browser driver it does ship,
   rather than installing one.

**Log in** via the mechanism resolved in Phase 2. If switching role/persona mid-walk,
re-run the login for the next role. Watch for a post-login gate (org/tenant/workspace
picker, "select account" screen) that a raw login URL doesn't satisfy; click through it,
because until you do, every gated route bounces you back.

Per surface, in order:

1. **Load** the route. Fail conditions: blank page, error boundary, redirect loop, bounce
   to home/login.
2. **Console** — read console messages filtered to errors. Any uncaught error or failed
   request (4xx/5xx to the app's own API) is a finding. Hydration/dev warnings: MINOR.
3. **Render sanity** — screenshot and judge like a human: overlapping or clipped text,
   cut-off buttons, sections that should hold data but are empty, raw i18n keys on screen
   (`foo.bar.baz`), broken layout.
4. **Primary interaction** — exercise what the diff actually touched: open the modal,
   submit the form, drag the card, toggle the setting. Verify the effect is *real*: the row
   appears, survives a reload, the API returns it. A click that merely doesn't throw is not
   a pass.
5. **Locale check** — when locale files changed, switch to each changed locale and
   re-screenshot the affected surface. Otherwise spot-check the longest-string locale on
   one dense surface (most likely to clip).
6. **Screenshot** every finding at the moment it's visible.

**Data discipline:** creating entities is allowed only against a local/dev environment
this run booted, or one the repo explicitly documents as disposable. Against anything
shared or remote, do a **read-only walk** instead - report which interactions you could
not exercise and why, don't create data there. Where creation is allowed: treat any
seeded/baseline data as read-only scenery; other tests depend on it. Anything you create
must be uniquely named (prefix `QA <timestamp>`) so it's obviously test data and safe to
leave behind. Never mutate or delete baseline entities.

**Anti-loop:** if a surface won't load after 2 attempts, log it as a finding (SERIOUS:
surface unreachable) and move on. Never burn more than ~5 tool calls on one stuck
interaction.

## Phase 5 — report

Write a report to an untracked scratch dir (e.g. `tmp/qa/<YYYY-MM-DD-HHmm>/report.md`)
with screenshots alongside. Structure:

```markdown
# QA pass — <date>, diff <short-sha range or "working tree">
Surfaces walked: N (list). Untested: (list + why — e.g. admin needs hardware-key auth).

## Findings
### [CRITICAL|SERIOUS|MINOR] <one-line claim>
- Surface: <route> as <role>
- Repro: <steps>
- Observed vs expected: …
- Screenshot: <file>

## Codify candidates
Which findings/flows deserve a permanent automated spec (name the spec file and the
assertion), if the repo has an e2e suite to hold them.
```

Severity: **CRITICAL** = data loss, security, a core flow broken. **SERIOUS** = a feature
the diff touched doesn't work as intended. **MINOR** = cosmetic, copy, console noise.

Then report in chat: findings ranked most-severe first, each with the one-line claim +
surface, plus the report path. No findings → say exactly which surfaces you walked and
what you exercised on each, so "green" is auditable. Do NOT claim a surface passed if you
only loaded it without exercising the diff-touched interaction.
