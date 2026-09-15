---
name: promote
description: Use this skill when the user wants to graduate matured memspec claims from the agent's local scratch store (or an explicitly named store) up into a team-context repo's team store (.memspec/) - e.g. "promote these facts to the team memory", "batch-promote my scratch memspec into the team store", "graduate this decision to the team-context repo", "run a team memory promote". It gathers candidate claims since the last promote, filters to cross-repo team-relevant facts/decisions/procedures, drafts one file per claim in the target store's format, shows the full batch for confirmation, and only then opens a PR on the team-context repo. Do NOT use it for direct writes to your local scratch store (those are ungated - just use memspec_remember), for regenerating specs/ (that is the spec-repos plugin), or for graduating PM workspace docs (that is pm-workspace's graduate skill).
version: 0.1.0
---

# Batch-promote memspec claims into a team-context repo

Graduate durable, team-relevant claims from the agent's local scratch memspec store into the team
`memory/` store. The team store is authored by exactly one path: a PR-gated batch, reviewed by the
team lead or PM. This skill produces that batch and that PR. It never writes to the team store any
other way.

Topology (context-standard §6): code repos carry **no** store of their own - only a committed
`.memspec.yaml` pointer binding them to the team store. An agent's working memory is disposable
**local scratch**. The team store is the only durable home, and this promote PR is the only write
path into it. So candidates come from local scratch (or a store the user names), never from a
"repo store" - there isn't one.

Why a batch and not per-claim: the review load has to stay human-sized. One PR carrying N vetted
claims is one standup-sized review. N PRs of one claim each is noise the reviewer will rubber-stamp,
which defeats the gate. Batch, always.

The gate is not a trust check, it is a contract. Direct writes to a team `memory/` store are refused
by agreement: local scratch is agent-operated and self-correcting; the team store is witnessed by a
human who would catch a wrong claim in standup. Respect that even when you are sure.

## What this skill will and will not do

- WILL: read source stores, filter candidates, draft records in a staging directory outside the
  target checkout, show them, and (after go-ahead) copy them in, push a branch and open a PR on the
  team-context repo.
- WILL NOT: merge the PR, push to the team store's default branch, write a single claim without the
  batch view, write anything into the target checkout before approval, or create the branch/PR
  before the user explicitly approves the shown batch.

## Step 1 - Locate the team-context repo

Do not assume a path. Resolve the target repo in this order, stopping at the first hit:

1. **Workspace `.memspec.yaml` pointer** - under the context standard a code repo carries a committed
   `.memspec.yaml` at its root binding it to the team store. Walk up from the current working
   directory for `.memspec.yaml`; read its `stores:` block and take the team layer's `path` (e.g.
   `/workspaces/<team>-team-context`). The engine resolves that path to the store at
`<team-context-repo>/.memspec/` (records under `.memspec/memory/`), and its parent
   directory is the team-context repo checkout. This is the authoritative binding - prefer it over
   every other signal.
2. **`POINTERS.md`** - the PM workspace's `POINTERS.md` names the team's context repo (agreement
   §2, PM read path). Walk up from the current working directory looking for `POINTERS.md`; if found,
   read the entry that names the team-context / team-specs repo.
3. **Repo `CLAUDE.md` `team-context:` key** - a repo's `CLAUDE.md` carries a `team-context:` key (or
   an `@import` of the team repo's `CLAUDE.md`) wired by the context-standard ask-once bootstrap.
   Read it from the nearest `CLAUDE.md` up the tree.
4. **Ask once** - if none resolve, ask the user for the team-context repo (a `git remote`/`gh`
   slug like `plg/ticketing-system-team-specs`, or a local clone path) with AskUserQuestion. Do not
   guess an org or repo name.

Repos are named `*-team-specs` today and `*-team-context` going forward (agreement naming note) -
match both suffixes. Confirm the resolved repo back to the user in one line before doing work against
it.

Get the store onto disk to inspect and write against it. The pointer usually resolves it to the
mounted checkout at `/workspaces/<team>-team-context` already; if you only have a slug, clone it to a
scratch path (or use an existing local checkout if the user names one). The team store lives at
`<team-context-repo>/.memspec/memory/`.

## Step 2 - Consolidate scratch, then gather candidates

**The reflection pass comes first, every time.** There is no scheduled dream cycle in this
topology — this step is where scratch gets groomed, so it is mandatory, not optional:

- Dedupe scratch: same claim written twice → supersede into one survivor.
- Cluster: several observations circling one durable fact → write the fact (to scratch,
  `--store global`), supersede the observations into it.
- Drop the ephemeral: session noise and expired observations are not candidates; leave
  them to decay.

Only what survives consolidation becomes a candidate. This converts "someone remembers
that something matured" into "every promote sweeps for what matured" — recognition is
the failure mode; the sweep is the fix.

Candidates are claims in the **source store** - the agent's local scratch store (the global ~/.memspec layer; note that in pointer-only repos writes reach it via `--store global`), i.e. the writable
working-memory layer memspec resolves for this session (a local scratch `.memspec/` the agent kept,
or the global `~/.memspec`), or a store the user names explicitly. Code repos carry no store of their
own under the topology, so there is no product-repo `.memspec/` to pull from, and the pointer's team
layer is a read source, never a promote source. Keep claims created or last verified after the
previous promote to this team repo. The since-marker comes from Step 7's promote log; on a first run,
treat every active claim as a candidate and lean harder on Step 3's filter.

**Primary path - memspec CLI** (preferred when `memspec` is on PATH):

```bash
# Full active graph as JSONL, restricted to the three promotable types.
memspec export --format jsonl --types fact,decision,procedure --cwd <source-store-root>
```

Export emits a graph, so the JSONL mixes two line kinds - filter to `"kind":"node"` first:

- **Node lines** (`"kind":"node"`). Memory nodes (`"node_type":"memory"`) carry only `id`, `kind`,
  `node_type`, `source_kind`, `stale`, `state`, `title`, `type`, `verified_with`. File nodes
  (`"node_type":"file"`, anchored source files) carry `id`, `kind`, `node_type`, `path`.
- **Edge lines** (`"kind":"edge"`) with `from`, `to`, `type` - relations between nodes, skip them.

Node lines carry **no dates, source, or tags** - those live only in the record files and in
`memspec search --json` output. To date-filter the export list, take each memory node's `id` and read
the record file's frontmatter (`created`, `last_verified`) at
`<source-store-root>/memory/{facts,decisions,procedures}/<id>.md`, or resolve the same fields via
`memspec search --json` (see below).

For a topic-scoped pull instead of the whole graph, use search:

```bash
memspec search "<topic terms>" --json --type fact --cwd <source-store-root>
```

`search --json` records DO carry `created`, `last_verified`, `source`, and `tags` alongside `id`,
`type`, `title`, `state`. There is no since-filter flag: apply the last-promote cutoff locally, on
`created`/`last_verified` from the JSON. (`--as-of` is a point-in-time world-state validity filter,
unrelated to "changed since" - do not use it for the promote window.)

`export` gives you the full id list to date-filter locally; `search` gives you a relevance-ranked
slice when the user names a topic. Prefer `export` for a time-window sweep, `search` for "promote the
X stuff."

**Fallback path - read the store files directly** (when the `memspec` CLI is absent):

The store is plain files. Read them:

```bash
# Records live under <source-store-root>/memory/{facts,decisions,procedures}/ms_*.md
ls <source-store-root>/memory/facts <source-store-root>/memory/decisions <source-store-root>/memory/procedures
```

Each `ms_*.md` is YAML frontmatter (`id`, `type`, `state`, `created`, `last_verified`, `source`,
`source_kind`, `tags`, `check_by`) followed by a markdown body whose first `#` heading is the claim
title. Read the frontmatter to get `created`/`state`, keep only `state: active` records at or after
the since-marker. On macOS the default `/bin/bash` is 3.2 - do not run `${var//pattern/}` over whole
file contents; parse frontmatter with `grep`/`sed`/`awk` line by line instead.

Skip anything under `operator/` and any `observations/` - those are personal/point-in-time and never
promote (see Step 3).

## Step 3 - Filter to what belongs at the team level, and groom the target store

A claim promotes only if it clears every one of these. When in doubt, leave it out - the reviewer's
time is the scarce resource.

**Target-store hygiene rides this same pass** (and this same PR): while deduping against the
team store, also collect (a) team claims flagged `stale` (past their check_by), (b) team claims
the incoming batch contradicts, (c) duplicates among existing team claims you noticed while
grepping. Propose each as a supersede/retire row in the PR template's "Store hygiene proposals"
section — proposals for the reviewer, never silent edits. An empty table is a result to state,
not a step to skip.

Keep:

- **Cross-repo, team-relevant** facts, decisions, or procedures - knowledge more than one repo or
  more than one teammate needs (a shared convention, a team-wide decision, a deploy/runbook procedure
  that spans services).

Drop:

- **Repo-local / session-local** knowledge that only makes sense inside one codebase or one session
  - it stays in the disposable local scratch and is never promoted (the topology keeps no durable
  repo store; code that needs a code-anchored claim belongs in team-context if it's team-relevant,
  otherwise it stays scratch).
- **Session noise** - anything that reads like a transcript, a one-off debugging note, or an
  observation with a short `check_by`.
- **Secrets** - tokens, keys, passwords, internal hostnames/IPs, connection strings. Never. Grep the
  candidate bodies for obvious secret shapes before drafting and hard-drop any hit.
- **Personal data** - anything `source_kind: operator` or tagged to a person's identity, home
  infra, or private life. The team store forbids personal data by contract (agreement §1, §4).
- **Already-in-team-store** - grep the target `memory/` first and drop duplicates:

  ```bash
  # Match by source id, then by title, against the target store.
  grep -rl "<source-claim-id>" <team-context-repo>/.memspec/memory/ 2>/dev/null
  grep -ril "<distinctive title phrase>" <team-context-repo>/.memspec/memory/ 2>/dev/null
  ```

  If the team store already carries the claim (same source id, or same assertion under a different
  id), skip it and note it in the batch view as a duplicate, do not re-add it.

## Step 4 - Draft the batch in the target store's format

Inspect before you write. Read one existing record from the target store to learn its exact frontmatter
shape and body convention - do not assume it matches the source store field-for-field:

```bash
find <team-context-repo>/.memspec/memory -name 'ms_*.md' | head -1   # then Read it
```

For each surviving candidate, draft one file in a **staging directory outside the target checkout**
(a scratch path, e.g. `<scratch>/team-promote-<date>-<shortid>/`), mirroring the target's
`.memspec/memory/` layout (`facts/`, `decisions/`, or `procedures/` - use a subdir only if the
target already uses that shape). Nothing is written into the target clone in this step: the drafts
live in staging until the user approves the batch in Step 5, and only Step 6 copies them into the
target. Follow the target's frontmatter exactly. At minimum carry:

- a fresh `id` if the target mints its own, or preserve the source `id` if the target keys on it -
  match the target's existing convention;
- `type` (fact | decision | procedure);
- `source` recording the origin store and original id (provenance - so a later reader can trace the
  claim home), e.g. `promoted-from: <source-store>#<source-id>`;
- `state: active`;
- the claim title as the first `#` heading and the claim body verbatim, minus anything the Step 3
  filter would strip mid-claim.

Do not invent fields the target store does not use - with one exception: `promoted-from` is this
workflow's one required addition. Add it even when no existing target record carries it; the PR
template promises reviewers that every promoted record's frontmatter names its origin store and id.
Do not reformat unrelated files. Every staged file traces to exactly one promoted claim.

Then draft the PR body from `${CLAUDE_PLUGIN_ROOT}/references/PROMOTE-PR-TEMPLATE.md`: fill the
summary table (one row per claim) and the reviewer checklist. Save it to a scratch file for the PR
create step.

## Step 5 - Show the full batch, then STOP

Show the user the complete batch before anything touches git or the target checkout:

```
## Team memory promote: <team-context-repo>

**Source store:** <source-store-root>
**Since:** <last-promote-iso or "first run">
**Candidates scanned:** N   **Promoting:** M   **Dropped:** N-M

### Batch (M claims)
| # | Claim (title) | Type | Source id | Why team-relevant |
|---|---|---|---|---|
| 1 | ... | fact | ms_... | shared across back-office + purchase-flow |

### Dropped
| Claim | Reason |
|---|---|
| ... | repo-local |
| ... | already in team store (ms_...) |
| ... | personal (source_kind: operator) |

### Files to be added (full drafted contents, from the staging directory)
#### .memspec/memory/facts/ms_...md
<complete drafted file: frontmatter + body>
#### .memspec/memory/decisions/ms_...md
<complete drafted file: frontmatter + body>

### PR
- Target repo: <slug>
- Branch: team-memory/promote-<date>-<shortid>
- Base: <default branch>
- Reviewer: team lead or PM (per the agreement gate)
```

Then **wait**. Write nothing to git and nothing into the target checkout - the drafts exist only in
the staging directory. Do not create the branch, do not open the PR. The batch view is the
deliverable of this step; the copy-in and push are Step 6, and only after an explicit go-ahead. A
rejected batch costs nothing to discard: delete the staging directory and the target clone is
untouched.

If the user edits the batch (drops a claim, fixes wording), apply the edit in the staging directory
and re-show the batch. Only a clear approval of the shown batch unlocks Step 6.

## Step 6 - After go-ahead: branch, commit, PR (never before)

Only once the user has explicitly approved the shown batch:

1. Verify the target checkout is safe to write to - on its default branch, with a clean tree:

   ```bash
   git -C <team-context-repo> rev-parse --abbrev-ref HEAD   # must print the default branch
   git -C <team-context-repo> status --porcelain            # must print nothing
   ```

   Wrong branch or any status output → **stop and report** exactly what you saw. Never commit over
   unrelated changes, and never stash/reset/clean someone else's work to make room.

2. Create the branch (never commit to the default branch):

   ```bash
   git -C <team-context-repo> checkout -b team-memory/promote-<date>-<shortid>
   ```

3. Copy the approved files from the Step 4 staging directory into the target clone at their
   `.memspec/memory/**` paths, then stage **only those files, by explicit path** - never
   `git add -A` or `git add .`:

   ```bash
   git -C <team-context-repo> add .memspec/memory/facts/ms_...md .memspec/memory/decisions/ms_...md
   ```

   Commit with a message naming the batch id and claim count. Keep the commit body free of PII and
   secrets (it is team-visible history).

4. Open the PR with the drafted body, base = the repo's default branch:

   ```bash
   git -C <team-context-repo> push -u origin team-memory/promote-<date>-<shortid>
   gh pr create --repo <slug> --base <default-branch> \
     --title "Team memory promote <date>: <M> claims" \
     --body-file <scratch-pr-body.md>
   ```

   Request review from the team lead or PM if the user names one. Do not merge - the reviewer merges.

5. Report the PR URL back in one line.

If `gh` is unauthenticated or the push is rejected, stop and surface the exact error - do not retry
blind and do not fall back to any non-PR write into the team store.

## Step 7 - Record the promote so the next run's since-filter works

Append a batch record to a promote log at the **source** store root so the next run knows where the
window starts:

```
<source-store-root>/local/team-promote-log.jsonl
```

One JSON line per batch:

```json
{"batch_id":"<shortid>","date":"<iso>","target_repo":"<slug>","pr":"<url>","claim_ids":["ms_...","ms_..."]}
```

The next run reads the latest line's `date` as its since-marker for this `target_repo`.

Know what this log is: operational telemetry, not memory — and note that memspec 0.9.0's
generated `.gitignore` does NOT cover `local/`, so in a git-tracked source store the log would
sync unless you ignore it: before writing it, ensure `local/` is listed in the store's
`.gitignore` (add the line if missing). Treat the log as **machine-local** either way — it is
lost if the store is re-cloned. Fallback that survives a re-clone: record the marker as a git-tracked
memspec fact in the source store, titled "last team promote to <team-slug>", carrying the same fields
(batch id, date, PR url, claim ids), and supersede it with each new batch so exactly one is active.
Either way, the since-marker is only an optimization of the candidate window - Step 3's dedupe grep
against the target `memory/` is the real duplicate guard, and it runs on every batch regardless.

Do not record the promote in the team repo - it belongs to the source's bookkeeping.

## What not to do

- Do not write to a team `memory/` store outside a PR. Ever. No "just this once" direct commit.
- Do not write drafted records into the target checkout before the user approves the shown batch -
  drafts live in the Step 4 staging directory until Step 6.
- Do not create the branch or PR before the user approves the shown batch.
- Do not branch or commit in a dirty target checkout, and do not stage with `-A`/`.` - explicit
  batch-file paths only.
- Do not promote secrets, personal data, or `source_kind: operator` records.
- Do not promote repo-local or session-local claims - they belong in disposable local scratch, not the team store.
- Do not merge the PR yourself - the team lead or PM reviews and merges (the human gate).
- Do not one-claim-per-PR. One batch, one PR, one human-sized review.
- Do not assume the target store's record format - inspect an existing record first.
