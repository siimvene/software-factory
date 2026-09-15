---
name: readiness-evaluator
description: Evaluate a ticket against a 7-criterion readiness rubric and output a score (0-100) with per-criterion feedback. Use whenever the user asks to score, evaluate, assess, or review a ticket's quality or readiness. Triggered by phrases like "evaluate this ticket", "score this ticket", "is this ticket ready", "how good is this ticket", "check ticket quality".
---
<!-- Ported from the reference implementation's PM workspace, 2026-09-10. Generic names per docs/14-pm-surface.md; rename freely, but keep the description's firing conditions, because the description is what decides whether the skill fires. -->

# Task Readiness Evaluator

Evaluate any ticket (provided as XML, plain text, or key+description) against the rubric below.
Output a **Readiness Score** (0–100) and per-criterion feedback.

---

## Scoring rubric (100 points total)

### 1. Objective / Problem statement (20 pts)

Does the ticket explain **what** is being built **and why** it is needed?

| Score | Signal |
|-------|--------|
| 17–20 | Clear one-sentence objective + context that names the current pain or gap ("today X is broken/missing/manual") |
| 10–16 | Objective exists but no context; or context exists but objective is implicit |
| 4–9   | Description is present but reads as implementation instructions with no stated problem |
| 0–3   | No description beyond the title, or description is a single vague sentence |

**From examples:**
- Good: "Enable POS operators to offer remote electronic payment for reservations. Today the only remote payment option is bank transfer: manual, slow, error-prone."
- Bad: "Need to allow creating any (non-bo3) event from scratch."

---

### 2. Acceptance / Success criteria (25 pts)

Are there explicitly stated, **testable**, outcome-focused conditions for "done"?

| Score | Signal |
|-------|--------|
| 21–25 | Multiple criteria, each describing an observable outcome (actor + action + expected result). Edge cases and regressions covered. |
| 13–20 | AC section exists; some criteria are testable but others describe implementation steps rather than outcomes |
| 5–12  | Vague completion signals ("feature must work", "fields must be saved") or only happy-path listed |
| 0–4   | No acceptance criteria at all |

**Key distinction:** "A cashier can create a reservation and the buyer receives an email with a working payment link" = good (observable). "Need to enter the name" = bad (not a criterion, not testable).

---

### 3. Scope boundary (15 pts)

Is scope bounded, ideally with an explicit **Out of scope** section?

| Score | Signal |
|-------|--------|
| 13–15 | Explicit "Scope" list + explicit "Out of scope" list |
| 8–12  | Scope is defined (bulleted list of what is included) but out-of-scope is absent or only implied |
| 3–7   | Scope is partially inferable from AC but no dedicated section |
| 0–2   | No scope definition at all |

**Why it matters:** Without out-of-scope, engineers must guess whether adjacent features are included. Leads to gold-plating or missed expectations.

---

### 4. Actor clarity (10 pts)

Is it clear **who** performs the action and **who** benefits? Named roles, not generic "user".

| Score | Signal |
|-------|--------|
| 9–10 | All actors named and qualified ("back-office user with the commission-fee manage privilege", "English-language buyer in a specific market instance") |
| 6–8  | Some actors named but one or more uses generic "user" or "admin" without qualification |
| 3–5  | One actor referenced but inconsistently or vaguely |
| 0–2  | Only "user" or no actor mentioned |

---

### 5. Pre-conditions / Dependencies (10 pts)

Are prerequisite states, permissions, or dependent tickets listed?

| Score | Signal |
|-------|--------|
| 9–10 | Explicit pre-conditions section: user privileges, system state, dependent tickets |
| 5–8  | Some dependencies mentioned inline but not as a dedicated section |
| 2–4  | Only implicit ("assumes the feature X exists") |
| 0–1  | No pre-conditions or dependencies stated |

---

### 6. Specificity / Concrete examples (15 pts)

Are requirements specific enough to build from without a follow-up conversation?
Does at least one concrete scenario (with input + expected output) exist?

| Score | Signal |
|-------|--------|
| 13–15 | Field-level specs, validation rules, or concrete user scenarios with named inputs and outputs |
| 8–12  | Requirements are specific but rely on implicit domain knowledge; no worked example |
| 3–7   | High-level descriptions that require substantial interpretation |
| 0–2   | Ticket could describe dozens of different implementations |

---

### 7. Title clarity (5 pts)

Is the title a clear, actionable one-liner that stands alone?

| Score | Signal |
|-------|--------|
| 5     | Reads as a user value statement or clear feature name ("Payment Link", "Localized e-mails based on reservation session language") |
| 3–4   | Functional but includes noise (ticket reference prefix, internal jargon) |
| 1–2   | Vague or requires reading the description to understand |
| 0     | Missing or meaningless (e.g. "Improvements") |

---

## Score interpretation

| Range  | Label   | Meaning |
|--------|---------|---------|
| 85–100 | **Good**   | Ready for sprint planning. Minor clarifications may be needed. |
| 55–84  | **Decent** | Core intent is clear; significant gaps remain. One refinement round likely needed. |
| 0–54   | **Bad**    | Not ready. Major structural elements are missing. Requires a full refinement conversation. |

---

## Scoring principles

- **Document-only scoring.** Every score is derived solely from the text present in the ticket. Do not penalise for information that would require external domain knowledge, adjacent-system context, or assumptions about what *should* be there.
- **No scope widening.** Do not introduce topics, actors, edge cases, or systems that are not already mentioned in the ticket. If a criterion gap would require knowing something outside the ticket, note only what the ticket itself is silent on, not what you think should exist.
- **Scope-widening rejections are score-neutral.** If you ask whether a topic or scenario should be included and the author confirms it is intentionally out of scope or not applicable, do not adjust the score for that criterion. The score reflects the document as submitted.

---

## Bigger tickets: one extra question

Some tickets are more than a quick fix. Once they are Ready, the build side writes its own short
design from the ticket before any code (docs/02-loop). It can only write what the ticket gives it.
A ticket can score 85 and still leave that design with nothing to work from, and then the build
bounces the ticket back to the author after pickup. Asking here is the same question, an hour
earlier, before anyone has started building.

**When this applies.** Only if the ticket's own text says one of these:

- money is moved, charged, refunded, or shown as an amount people pay on
- login, identity, permissions, or keeping one customer's data away from another's
- something new gets stored
- someone else consumes it: a mobile app, another system, an external API
- an existing feature or path is removed
- more than one existing feature spec is touched

Nothing about the score changes. This only decides which question you ask first and what you
point out as misplaced.

**The one question, in this order.** Ask for the first thing on the list that the ticket does not
already have. One question, then stop.

1. **What must never break, and how would we know?** Also: is there a speed or volume limit
   (a number, or "none"), and what happens on the bad case (wrong person, duplicate, expired,
   malformed input) including what must stay unchanged.
2. **What exactly does the user see or type?** Exact names, amounts, dates, messages, field
   labels. For anything with a screen: is the agreed clickable prototype attached to the
   ticket? Without it the build cannot know the fields and states, whatever the score.
3. **What has to exist or ship before this?** Including which other ticket this depends on.
4. **Who does this, and where?** Which role, on which page, button, endpoint, job, or message,
   for each example.

Put it at the top of the gaps list, in plain words, like this:

```
This one is bigger than a quick fix. Before the build can plan it, I need:
[the one thing, as a question the author can answer in a sentence or two]
```

Ask it at Good scores too. A high score means the ticket is well written, not that the build has
what it needs.

**Never ask for, and point out if you find:** file or module names, database tables, function
names, the order engineering will build things in, or technical choices such as streaming versus
buffering, batch sizes, retry rules. Those are decided downstream. If the ticket contains them,
add one gap line, no score change:

```
This belongs to the build's design, not the ticket; you can drop it: [what was found]
```

and say why in one sentence: once implementation detail is in the acceptance criteria, the
criteria are no longer the requester's (docs/07-roles-and-authority).

**The lines only the author can write.** Whether money, identity, or customer isolation is
involved; whether something new is stored; whether another system consumes it; whether a path is
being removed. The build cannot find these out from code it has not written yet. If the text
shows one of them but the ticket never states it as a constraint, ask for that line first,
before anything else in the order above.

---

## Context lookup

Before scoring, attempt to find relevant context. Finding context does **not** change the ticket's score (the score still reflects only what is written in the ticket) but it makes gap feedback actionable by pointing to the exact file where the missing context already exists.

**Two lookup sources (check both, domain specs first):**

### 1. Domain spec folders
**Root:** `context/` (22 domain folders: accounts, affiliate, billing, cash, channels, discounts, embeds, logistics, marketing, marketplace, offer, payments, repertoire, reporting, reservations, reviews, sales, shop, tickets, venues)

Each folder contains `{feature}.md` (functional spec) and `{feature}.tech-refs.md` (technical reference) files.

Match the ticket topic to a domain and feature file. Examples:
- Ticket about events → `context/repertoire/create-edit-and-remove-an-event.md`
- Ticket about discounts → `context/discounts/`
- Ticket about ticket types → `context/tickets/`

### 2. The workspace
**Root:** `context/pm-workspace/` (the workspace tree)

Search recursively across `features/`, `reference/`, and `<tickets>/` for filenames matching the ticket topic. Covers deeper PM notes, competitor research, legacy system docs, and polished ticket examples.

**Lookup steps:**
1. Extract a feature name or topic keyword from the ticket title and description.
2. Check domain spec folders first: find the matching domain and read the relevant `{feature}.md`.
3. Then search the workspace recursively across `features/` and `reference/` for any additional matches.
4. If a match is found in either source, read it before applying the rubric.
5. For each gap found during scoring, check whether the matched file contains an answer. If yes, cite the path in feedback (e.g., `[available in context/repertoire/create-edit-and-remove-an-event.md]` or `[available in features/Payment Link.md § 4.2]`).
6. If no match is found in either source, proceed as normal.

**What the context is used for:**
- Making gap feedback specific: "missing actor qualification, the spec names POS Operator as the actor (context/repertoire/…)"
- Identifying quick wins: gaps where the answer is already written and just needs to be copied into the ticket
- The found context is **not** used to infer what the ticket intends, fill in unstated scope, or raise the score

---

## How to use this evaluator

0. **Ticket sourcing: local content takes priority.**
   - If the user provides ticket text, XML, or a pasted description: use that directly. Do **not** call the tracker MCP.
   - If the user provides only a ticket key (e.g. `EX-433`) with no accompanying text: fetch the ticket via the tracker MCP. Fetch once and reuse, do not re-fetch mid-session.
   - Never call the tracker MCP when local content is already present in the conversation.

0b. **Clarify first if needed.** Before scoring, check whether the ticket's overall topic and domain are clear enough to apply the rubric. If the ticket is so sparse or ambiguous that the subject matter itself is unclear, ask the author one concise clarifying question about the high-level goal before proceeding. Do not infer or assume the domain from external knowledge.

0c. **Workspace lookup.** Run the workspace context lookup described above (recursive search across features/ and reference/ including all subfolders). Report the result (file found / not found) before presenting scores.

1. Read the ticket content (description + summary + any AC fields).
2. Score each criterion independently using the rubric above, based only on what is written in the ticket.
3. Sum the scores. State the total and label (Good / Decent / Bad).
4. For each criterion scored below its midpoint, output one specific, actionable gap statement referencing only content (or its absence) within the ticket. Where the workspace lookup found relevant spec content, append a `[available in features/X.md § N]` citation.
5. If the ticket is Decent or Bad, identify the **single highest-impact question** to ask the author that would unlock the most score improvement, scoped to what the ticket already covers, not to topics outside it. For a bigger ticket (see "Bigger tickets" above) the question follows that section's order and is asked at Good scores too, as the first line under gaps.
5b. **Auto-transition to improver.** If the total score is below 85, immediately invoke the `task-improver` skill without waiting for the user to ask. Pass the ticket content and the full evaluation output (score, gaps, top clarifying question) as context so the improver starts from the first gap question rather than re-evaluating from scratch.
5c. **Good score: offer three paths.** If the total score is 85 or above, always present all three options before taking any action:

```
Score is [X]/100, Good. What would you like to do?

  [1] Post this evaluation as a comment on [KEY] and mark it ready.
  [2] Keep improving, push the score higher toward 100.
  [3] Split into sub-tasks: this ticket may be larger than 2 man-days.
```

- If the user picks **[1]** (or says "post", "done", "write back", "looks good"): proceed to the tracker comment write-back below.
- If the user picks **[2]** (or says "improve", "keep going", "higher", "100"): invoke `task-improver` passing the ticket content and full evaluation output as context. The improver will continue from the remaining minor gaps rather than re-scoring from scratch.
- If the user picks **[3]** (or says "split", "too big", "break it up"): invoke the `task-splitter` skill, passing the full refined ticket content (the polished version at this point in the conversation) as context.
- Never skip this choice prompt and go straight to write-back, even if the score is very high.

5d. **Tracker comment write-back on Good score.** Triggered by user choosing option [1] above. Offer to post the evaluation summary as a comment on the tracker ticket. Follow the Preview → Confirm → Execute → Log pattern:

   **Preview (show before any write):**
   ```
   📋 ACTION PLAN
   ══════════════════════════════
   Action:   Add Comment
   Issue:    [KEY], [Summary]
   Comment:  Readiness Score: [X]/100, Good
             [paste the score table + any minor gap notes, formatted as markdown]
   ══════════════════════════════
   Confirm? (yes / no)
   ```

   **On confirmation:** call the tracker MCP `add-comment` operation with `contentFormat: "markdown"`.

   **Log entry** (append to `~/tracker-actions.log`):
   ```
   ────────────────────────────────────────
   [ISO-8601 timestamp]
   ACTION:   Add Comment (Readiness evaluation)
   ISSUE:    [KEY], [Summary]
   SCORE:    [X]/100, Good
   RESULT:   ✅ Success
   ────────────────────────────────────────
   ```

   **Confirm to user:** `✅ Evaluation posted to [KEY].`

   If no ticket key is known (ticket was pasted as plain text without a key), skip this offer and note that no tracker key is available to write back to.

6. **Context-drift check (last iteration only).** Once all refinement rounds are complete and the final version is ready, compare it against the original input. Flag any content introduced in the final version that was not present or clearly implied in the initial ticket: new topics, actors, systems, or scope additions. List each drift item explicitly. If none, state that. Drift is reported as a warning only; it does not affect the score.

---

## Output format

**First evaluation:**
```
## Readiness Score: [X]/100, [Good / Decent / Bad]

> Context: [features or reference path] matched, gaps annotated with workspace citations.
> (omit this line if no workspace file was found)
> Bigger ticket: [why, e.g. money is charged; something new is stored]. One extra question below.
> (omit this line otherwise)

| Criterion                   | Score | Max |
|-----------------------------|-------|-----|
| Objective / Problem         |       | 20  |
| Acceptance criteria         |       | 25  |
| Scope boundary              |       | 15  |
| Actor clarity               |       | 10  |
| Pre-conditions              |       | 10  |
| Specificity / Examples      |       | 15  |
| Title clarity               |       | 5   |

### Gaps
- [criterion]: [specific gap and what's missing] [available in features/X.md § N, if applicable]
- This one is bigger than a quick fix. Before the build can plan it, I need: [the one question] (bigger tickets only, no score effect)

### Top clarifying question
[Single most impactful question to ask the author]
```

**Re-evaluation after refinement**: show the score delta in the Score column as `new (+delta)` for improved criteria, `new (-delta)` for regressions, and `same` for unchanged. Total line shows the net change.
```
## Readiness Score: [X]/100 (+[N]), [Good / Decent / Bad]

| Criterion                   | Score      | Max |
|-----------------------------|------------|-----|
| Objective / Problem         | [n] (+[d]) | 20  |
| Acceptance criteria         | [n]        | 25  |
| Scope boundary              | [n] (+[d]) | 15  |
| Actor clarity               | [n]        | 10  |
| Pre-conditions              | [n]        | 10  |
| Specificity / Examples      | [n] (+[d]) | 15  |
| Title clarity               | [n]        | 5   |

### Changes from previous version
- [criterion]: [what was added/improved]

### Remaining gaps
- [criterion]: [specific gap still present]
```

---

## Calibration examples

| Ticket         | Expected score range | Key deficiencies |
|----------------|----------------------|------------------|
| EX-2 (bad)    | 5–15                 | No objective, no AC, no scope, no actor qualification, no pre-conditions |
| EX-497 (decent) | 55–70              | No objective section, no out-of-scope, AC partially implementation-focused |
| EX-324 (good) | 75–85                | No explicit out-of-scope, no pre-conditions section |
| EX-433 (good) | 85–95                | Near-complete; minor gap is no explicit assumptions section |
