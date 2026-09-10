---
name: task-improver
description: Conversational refinement loop that takes a weak ticket and improves it to a readiness score of 85+ through targeted one-at-a-time questions. Use when the user wants to improve, refine, or work on a ticket. Triggered by phrases like "improve this ticket", "refine this story", "make this ticket better", "help me write a better ticket", "work on this task with me", or when the user pastes a ticket and asks for help.
---
<!-- Ported from the reference implementation's PM workspace, 2026-09-10. Generic names per docs/14-pm-surface.md; rename freely, but keep the description's firing conditions, because the description is what decides whether the skill fires. -->

# Task Improver Skill

A conversational refinement loop that takes a weak task, evaluates it using the readiness-evaluator skill,
and asks as many targeted questions as needed, one at a time, until the task reaches a Readiness Score of 85+.
At the end it validates the final output against the original to catch context drift.

---

## How to invoke

The user provides a ticket (XML export, plain text, or ticket ID).

**Ticket sourcing, local content takes priority:**
- If text or XML is already in the conversation: use it directly. Do **not** call the tracker MCP.
- If only a ticket key is given (e.g. `EX-123`) with no text: fetch via the tracker MCP. Fetch once and reuse.

**Context lookup, check local files before asking:**
When a gap could be answered from existing documentation, look it up first rather than asking the user. Two sources to check:

1. **Domain spec folders** (`context/{domain}/{feature}.md`): 22 domains covering the full platform. Match the ticket topic to a domain (e.g. event tickets → `context/repertoire/`, discounts → `context/discounts/`). Read the relevant `.md` file to find actor names, pre-conditions, scope boundaries, and acceptance criteria patterns already written for that feature area.

2. **The workspace** (`context/pm-workspace/`): search `features/`, `reference/`, and `<tickets>/` recursively for files matching the ticket topic.

If you find a relevant file, use it to inform assumptions (`[ASSUMED: per context/repertoire/…]`) and sharpen questions. Only ask the user about things genuinely not covered by the context files.

**Reference tickets, allowed during refinement:**
When a gap is hard to close because the user is unsure what "good" looks like for a specific criterion, you may use the tracker MCP to search for a similar well-defined ticket as a concrete example. Show the example briefly (key + the relevant section) and use it to ground the next question. Do this sparingly, only when it would materially help the user answer the gap question.

---

## Step 0: Start session timer

Before doing anything else, run this bash command to start a live timer in the terminal title bar:

```bash
date +%s > /tmp/task_improver_start_time; START=$(cat /tmp/task_improver_start_time); (while true; do ELAPSED=$(( $(date +%s) - START )); printf "\033]0;⏱ %02d:%02d (Task Improver)\007" $((ELAPSED/60)) $((ELAPSED%60)); sleep 1; done) & echo $! > /tmp/task_improver_timer_pid
```

This runs silently in the background. Do not mention it to the user.

---

## Step 1: Initial evaluation

On receiving the task, silently score it against all 7 criteria in the readiness-evaluator skill.
Do not show the scoring working. Show:

```
## Readiness Score: [X]/100, [Bad / Decent / Good]

| Criterion                   | Score | Max |
|-----------------------------|-------|-----|
| Objective / Problem         |       | 20  |
| Acceptance criteria         |       | 25  |
| Scope boundary              |       | 15  |
| Actor clarity               |       | 10  |
| Pre-conditions              |       | 10  |
| Specificity / Examples      |       | 15  |
| Title clarity               |       | 5   |

**What I understood from the ticket:**
[2–3 sentence plain-English summary of what the task appears to be about.
Call out anything that is ambiguous or assumed.]

💾 *You can save your progress at any time, type `checkpoint save` to resume this session later, or `checkpoint help` for options.*
```

Then immediately go to Step 2.

---

## Step 2: Pick the highest-impact gap and ask ONE question

Continue asking questions until the score reaches 85. There is no question limit.
Every time a gap is closed, the next question targets the next-largest remaining gap.

**Question priority** (work top-to-bottom; pick the first criterion whose score is below its midpoint):

| Priority | Criterion              | Midpoint |
|----------|------------------------|----------|
| 1        | Acceptance criteria    | 13       |
| 2        | Objective / Problem    | 10       |
| 3        | Scope boundary         | 8        |
| 4        | Specificity / Examples | 8        |
| 5        | Actor clarity          | 6        |
| 6        | Pre-conditions         | 5        |
| 7        | Title clarity          | 3        |

**Rules for asking the question:**

- Ask exactly ONE question per turn. No sub-questions, no option lists.
- **Be concrete and brief.** One sentence is ideal; two is the maximum. Cut all preamble.
  Bad: "Could you help me understand what the acceptance criteria might look like for this feature?"
  Bad: "What are the acceptance criteria?"
  Good: "What's the one thing a TC admin should be able to do after this ships that they can't do now?"
- **Infer before asking.** If you can make a reasonable assumption from the ticket or prior answers,
  state it as `[ASSUMED: …]` in the draft and move to the next gap. Ask only when the information
  is genuinely unavailable from context.
- **Reference prior context sparingly**, only when it makes the question meaningfully sharper.
  Don't recap just to seem attentive; it pads the question without helping the user answer it.
- If the user says "I don't know" or "not decided yet", record it as an explicit open assumption,
  update the draft accordingly, and move to the next gap on the next turn. Do not stay stuck.
- Never re-ask a question whose gap has already been addressed, even partially.
- A single good answer can close multiple criteria at once, re-score all 7 after every answer.

**Show each question like this:**

```
---
**Question [N]** *(unlocks up to [X] points, [criterion name])*

[The question, one or two sentences, specific, grounded in accumulated context.]
```

After displaying the question, speak it aloud by running:

```bash
bash .claude/scripts/speak.sh "[the question text, markdown stripped]"
```

Strip markdown before passing to speak.sh: remove `**`, `*`, backticks, and leading `#` characters. Pass plain prose only.

---

## Step 3: Incorporate the answer and re-evaluate

After each user response:

1. **Update the working draft**: integrate the new information into the structured template in Step 4.
   Track it across all turns; it is your source of truth for the final output.

2. **Re-score**: recalculate all 7 criteria based on the full accumulated context
   (original ticket + every answer so far).

3. **Acknowledge and show the updated score:**

For any criterion whose score is strictly higher than its score in the previous round, show the score as `[score] (+[delta])`. Criteria at their original score show just the score number.

After each answer, open the acknowledgement with a brief, genuine encouragement line. Make it personal,
reference what the user actually said or what specific gap their answer closed. Never use a canned phrase twice.

Guidelines by progress level:
- **Small gain (< 5 pts):** Acknowledge the specific detail they gave. e.g. "That bit about the fallback
  behaviour is exactly the kind of nuance that makes a ticket airtight."
- **Good gain (5–9 pts):** Be warm and specific. e.g. "The way you described the actor flow just made
  three criteria much clearer, you clearly know this feature inside out."
- **Big gain (10+ pts):** Show genuine excitement about what they contributed. e.g. "Okay, that answer
  was gold, you just gave us the acceptance criteria and the scope boundary in one go."
- **Score just crossed into Decent (55+):** Mark the milestone personally. e.g. "We've turned the corner,
  this is starting to look like a ticket a developer could actually pick up and run with."
- **Score just crossed into Good (85+):** Celebrate with warmth. e.g. "That's it, seriously, this ticket
  went from rough notes to something genuinely great. You did the hard part. 🎉"

The tone should feel like a thoughtful colleague who is genuinely impressed, not a chatbot dispensing
gold stars. Reference the actual content of the answer whenever possible.

```
[Encouragement line]. [One sentence: what the answer clarified and which gap it closed or narrowed.]

## Readiness Score: [X]/100, [Bad / Decent / Good]

| Criterion                   | Score    | Max |
|-----------------------------|----------|-----|
| Objective / Problem         | 15 (+5)  | 20  |   ← example: improved since previous round
| Acceptance criteria         | 10       | 25  |   ← example: not yet improved
| Scope boundary              |          | 15  |
| Actor clarity               |          | 10  |
| Pre-conditions              |          | 10  |
| Specificity / Examples      |          | 15  |
| Title clarity               |          | 5   |
```

(Remove the `← example` annotations from actual output; they are shown here for illustration only.)

After showing the updated score table, speak two things back-to-back:

First, speak the encouragement line (the same one shown in text, keep it natural and varied, occasionally throw in something like "Wow, you are doing so good!" or "That was a great answer!" for milestone moments):

```bash
bash .claude/scripts/speak.sh "[encouragement line]"
```

Then speak the score change:

```bash
bash .claude/scripts/speak.sh "Score improved by [delta] points to [new total] out of 100."
```

If the score did not change, say: `"Score unchanged at [total] out of 100."`

4. **Stagnation check**: only active when the current score is below 85. Do not apply this check at all when the score is 85 or above.

   While score < 85:
   - If the score increased by **5 or more points**: reset the stagnation counter to 0.
   - Otherwise (score unchanged or gained fewer than 5 points): increment the stagnation counter.
   - If the stagnation counter reaches 2 (two consecutive rounds with less than +5 gain):
     1. Automatically save a checkpoint using the format in the session-checkpoint skill.
        Do not ask for confirmation, save silently, then announce it.
     2. Show:
        ```
        ---
        💾 **Progress saved automatically.**

        We've worked through [N] questions and the score hasn't moved meaningfully in the last two rounds (currently [X]/100).
        This usually means the remaining gaps need information that isn't available right now:
        a stakeholder conversation, a decision still pending, or just some time to think it over.

        Your session is saved as: `~/.claude/checkpoints/<filename>`
        Resume any time with: `checkpoint resume <filename>`

        Take a break and come back when you're ready. There's no rush. 🙂
        ```
     3. Stop the timer and restore the terminal title:
        ```bash
        kill $(cat /tmp/task_improver_timer_pid) 2>/dev/null; rm -f /tmp/task_improver_timer_pid; printf "\033]0;\007"
        ```
     4. Stop the loop. Do not ask the next question.

   If score < 85 and stagnation counter < 2: go to Step 2 for the next question.
   If score ≥ 85: go to Step 5.

---

## Step 4: Working draft (maintained across all turns, shown only at Step 5)

Keep this template updated mentally after every answer. Do not show it mid-loop unless the user
explicitly asks to see the current draft (`show draft`).

```
## [Title]

**Objective**
[One sentence: what is built + for whom]

**Context**
[Why this is needed: current pain, workaround, or missing capability, named concretely]

**Scope**
- [what is explicitly included]

**Out of scope**
- [what is explicitly excluded]

**Pre-conditions**
- [required privilege, system state, or dependent work]

**Acceptance criteria**
- [Actor] can [action] → [observable outcome]
- [Edge case or regression check]
- [...]

**Open assumptions**
- [Anything treated as decided that was not in the original ticket]
- [UNKNOWN]: [anything the user said is not yet decided]
```

---

## Step 5: Final polished output (score ≥ 85)

Show the complete working draft using the template above. Then show the final score table.

Then immediately run the **drift check** (Step 6) before offering write-back.

---

## Step 6: Drift check

Compare the final polished task against the original ticket content.
Check for three types of drift:

| Drift type | What to look for |
|------------|-----------------|
| **Scope creep** | Does the final task include features or behaviour not implied by the original? |
| **Intent shift** | Does the final task describe a meaningfully different goal than the original summary/title suggested? |
| **Actor substitution** | Did the actor change (e.g., original said "admin user", final says "end buyer")? |

Show the drift check result:

```
## Drift Check

**Original intent:** [One sentence restating what the original ticket was about, verbatim concepts only]
**Final intent:** [One sentence restating what the polished task is about]

| Drift type       | Status | Notes |
|------------------|--------|-------|
| Scope creep      | ✅ None / ⚠️ Minor / ❌ Major | [if flagged: what was added and where] |
| Intent shift     | ✅ None / ⚠️ Minor / ❌ Major | [if flagged: how the goal changed] |
| Actor substitution | ✅ None / ⚠️ Minor / ❌ Major | [if flagged: original vs final actor] |
```

**If any drift is Major:**
Flag it explicitly and ask the user to confirm before writing back to the tracker:

```
⚠️ The refined task diverged significantly from the original on [drift type].
Original: [quote]
Final: [quote]

Is this intentional, or should we adjust?
```

**If all drift is None or Minor:** proceed directly to the write-back offer.

---

## Step 7: Write-back offer

```
---
**Ready to write back to the tracker?**
Type `yes` to update the ticket description via the tracker MCP, or `edit [section]` to revise a specific section first.
```

If the user types `edit [section]`:
- Show just that section, accept the edit, update the draft, re-run the drift check, then offer write-back again.

If the user types `yes`, follow the Preview → Confirm → Execute → Log pattern:

**Step 7a: Preview (show before any write):**
```
📋 ACTION PLAN
══════════════════════════════
Action:   Update Issue Description
Issue:    [KEY], [Summary]
Fields:   description (full replacement with polished draft)
══════════════════════════════
Confirm? (yes / no)
```

**Step 7b: Wait for explicit confirmation.** Never infer confirmation from context.

**Step 7c: Execute:** call the tracker MCP `edit-issue` operation with the polished description using `contentFormat: "markdown"`.

**Step 7d: Log** (append to `~/tracker-actions.log`):
```
────────────────────────────────────────
[ISO-8601 timestamp]
ACTION:   Update Issue Description (task-improver write-back)
ISSUE:    [KEY], [Summary]
SCORE:    [X]/100, Good
RESULT:   ✅ Success
────────────────────────────────────────
```

**Confirm to user:** `✅ [KEY] updated.` and the tracker link if returned by the API.

**Step 7e: Post evaluation comment.** Immediately after the description write-back succeeds, offer to post the readiness evaluation as a comment on the same ticket. Follow the same Preview → Confirm → Execute → Log pattern:

**Preview:**
```
📋 ACTION PLAN
══════════════════════════════
Action:   Add Comment (Readiness evaluation)
Issue:    [KEY], [Summary]
Comment:  Readiness Score: [X]/100, Good
          [score table]
          Refined from [start score] → [final score] in [N] questions.
          [open assumptions if any]
══════════════════════════════
Confirm? (yes / no)
```

**On confirmation:** call the tracker MCP `add-comment` operation with `contentFormat: "markdown"`. The comment body must include:
- `## Readiness Score: [X]/100, Good`
- The full 7-criterion score table
- One line: `Refined from [start]/100 → [final]/100 across [N] questions.`
- Any remaining minor gaps (criteria that scored below their max)
- Any `[UNKNOWN]` open assumptions

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

**Confirm to user:** `✅ Evaluation comment posted to [KEY].`

Then proceed to **Step 8**.

If no ticket key is known (ticket was pasted as plain text without a key), skip both the write-back offer and the comment offer, note that no tracker key is available, and proceed to **Step 8**.

---

## Step 8: Save session log

Run immediately after Step 7 completes (or after the drift check when no tracker key is available).
This step is always silent, do not mention it to the user unless the write fails.

**1. Compute session duration:**
```bash
ELAPSED=$(( $(date +%s) - $(cat /tmp/task_improver_start_time 2>/dev/null || date +%s) )); printf "%02d:%02d" $((ELAPSED/60)) $((ELAPSED%60))
```

**2. Determine the log filename:**
- If ticket key is known: `session-logs/YYYY-MM-DD_TICKETKEY.md`
- If no key: `session-logs/YYYY-MM-DD_no-key.md`
- If that file already exists, append `_2`, `_3`, etc. to avoid overwrite.

**3. Create the directory and write the log** using the Write tool:

```bash
mkdir -p session-logs
```

Write `session-logs/<filename>` with this exact structure:

```markdown
---
date: [ISO-8601 timestamp]
ticket_key: [KEY or none]
ticket_title: [title of ticket]
initial_score: [N]
final_score: [N]
questions_asked: [N]
drift_flags: [none / minor / major, worst single drift level from Step 6]
stagnated: [true / false]
---

## Session: [KEY, title, or "Untitled"]
**Date:** [YYYY-MM-DD]
**Duration:** [MM:SS]
**Score:** [initial] → [final]/100 across [N] questions
**Outcome:** [Success (85+) / Stagnated at N/100]

## Original Ticket

[verbatim original ticket text as provided by the user]

## Score Progression

| Turn | Criterion targeted        | Score |
|------|---------------------------|-------|
| 0    | (initial)                 | [N]   |
| 1    | [criterion name]          | [N]   |
| …    | …                         | …     |

## Q&A Transcript

### Q1: [criterion targeted]
**Question:** [exact question asked]
**Answer:** [user's answer, verbatim or close paraphrase]
**Score after:** [N]/100

[repeat block for each question]

## Final Polished Ticket

[full working draft from Step 4]

## Drift Check

**Original intent:** [one sentence from Step 6]
**Final intent:** [one sentence from Step 6]

| Drift type         | Status | Notes |
|--------------------|--------|-------|
| Scope creep        | [✅/⚠️/❌] | [notes] |
| Intent shift       | [✅/⚠️/❌] | [notes] |
| Actor substitution | [✅/⚠️/❌] | [notes] |

## Open Assumptions

[bullet list of all [ASSUMED] and [UNKNOWN] items from the final draft, or "None" if clean]
```

**4. Stop the timer and restore the terminal title:**
```bash
kill $(cat /tmp/task_improver_timer_pid) 2>/dev/null; rm -f /tmp/task_improver_timer_pid /tmp/task_improver_start_time; printf "\033]0;\007"
```

---

## What NOT to do

- Do not stop asking questions early because the task "seems good enough", continue until 85.
- Do not ask multiple questions in one message.
- Do not show the full working draft on every turn, only at Step 5 or when asked.
- Do not invent specifics (field limits, technical decisions). Mark them `[UNKNOWN]` and move on.
- Do not skip the drift check. Run it even if the score jumped cleanly from Bad to Good.
- Do not re-ask any question whose gap has already been addressed in any prior turn.
