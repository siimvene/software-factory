# Team memory promote: <batch-date>

Batch promote of matured memspec claims into this team-context repo's team store (`.memspec/`).
Source store: `<source-store-root>`. Batch id: `<shortid>`.

This is the only sanctioned write path into the team store (team-context agreement §3 row 4,
§4). Merging accepts these claims as team-level knowledge everyone reads through the memspec pointers.

## Batch summary

| # | Claim | Type | Source store | Why team-relevant |
|---|---|---|---|---|
| 1 | <title> | fact / decision / procedure | `<source-store>#<ms_id>` | <one line: which repos/teammates need it> |
| 2 | ... | ... | ... | ... |

Files added: `.memspec/memory/**` (one file per row above). Files changed: only records listed
under Store hygiene below. No other files touched.

## Reviewer checklist (team lead or PM)

Merge only when every claim clears all four. Reject or ask changes on the batch if any claim fails -
do not merge a partial and hand-drop after.

- [ ] **True** - each claim is actually correct (the "would I catch this wrong in standup?" test).
- [ ] **Durable** - current-state knowledge, not a session note, transient state, or a soon-stale
      observation.
- [ ] **No secrets / no PII** - no tokens, keys, credentials, internal hosts/IPs, and no personal or
      colleague-identifying data. (Team store forbids both by contract.)
- [ ] **Belongs at team level** - cross-repo / cross-teammate knowledge, not repo-local detail that
      belongs in that repo's `CLAUDE.md`/`docs/` (code repos carry no store).

## Store hygiene proposals

Hygiene is event-attached: every promote also grooms the store it writes to (there is no
scheduled cleanup by design — this PR is the dream cycle). Proposed on this pass:

| Existing claim | Proposal | Reason |
|---|---|---|
| <ms_id — title> | supersede-by-#N / retire | stale past check_by / contradicted by incoming #N / duplicate of #N |

If the table is empty, state "none this batch" — that is a checked result, not a skipped step.

## Notes for the reviewer

- Provenance for each claim is in its record frontmatter (`promoted-from: <source-store>#<id>`) - trace
  a doubtful claim back to its origin store.
- Dropped candidates (duplicates, repo-local, personal) are listed in the promote run output, not here -
  ask the author if you want the drop rationale.
- This PR does not modify `specs/` (derived, regen pipeline only) or `CLAUDE.md`/`rules/`.
