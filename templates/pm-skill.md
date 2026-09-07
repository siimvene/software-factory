<!--
  PM SKILL SKELETON. Copy this file to `.claude/skills/<name>/SKILL.md` in the PM
  workspace and fill every section. The shape is taken from the best-structured skill in
  the reference workspace (the readiness evaluator): frontmatter that decides when the
  skill fires, inputs in an explicit read order, numbered procedure, one named output
  path, a self-check, and a refusal list.
  Delete nothing. A section with no content is a finding, so write "none" rather than
  removing the heading. See docs/14-pm-surface.md for what each skill in the catalogue
  does and where it sits in the loop.
-->

---
name: <lowercase-hyphenated, matches the directory name>
description: <One sentence naming the job, then the firing conditions, spelled out.
  Name the artifacts and the verbs that should trigger it, and the phrases a person
  actually types. This field is the only thing the model reads when deciding whether to
  invoke the skill, so a vague description is a skill that never fires or fires always.
  Example shape: "Score a draft ticket against the readiness rubric and return a score
  out of 100 with per-criterion gaps. Use whenever the user asks to score, evaluate,
  assess or review a ticket's quality or readiness, or pastes a ticket and asks whether
  it is ready. Triggered by phrases like 'evaluate this ticket', 'is this ready',
  'check ticket quality'.">
allowed-tools: <Read, Grep, Glob, Write, Edit, Bash, WebFetch, and any MCP tools by
  exact name. List the minimum. A skill that only reads and reports never gets Write;
  a skill that never leaves the machine never gets WebFetch.>
---

# <Skill name>

<Two or three sentences. What the skill is for, and the one failure it exists to
prevent. State the standard it is held to, in the user's terms: for an analysis skill,
"the user should not have to ask what you missed"; for a drafting skill, "no half-baked
draft leaves this skill".>

Operate under the workspace contract in the workspace instruction file. Read it first if
it is not already in context.

**Input:** <what the skill accepts: a file path, a glob resolved against a named folder,
an identifier, free text from the conversation, or several of these. If the input is
ambiguous, say which single question to ask and with which tool. Never guess.>

## Inputs, in read order

Read in this order and stop at the first source that answers. Every claim in the output
cites the source it came from.

1. **The input itself.** <The pasted text, the named file. If content is already in the
   conversation, use it. Never re-fetch what you already have.>
2. **Current-state specs.** <Where they live, taken from the workspace pointer file.
   Specs are the source of truth for what the system does today.>
3. **Code.** <Which repositories, from the same pointer file, and what to look for:
   entry points, input types, configuration, validators, user-visible messages, state
   machines, permissions, feature flags. Use code when the spec is unclear or silent,
   not instead of the spec.>
4. **Workspace context.** <Discovery notes, reference material, decisions, prior
   tickets. Deeper background and things already decided.>
5. **The human.** <Only when the answer is genuinely not determinable from the sources
   above, for example when it depends on a decision nobody has made. State what you
   already checked before asking.>

All sources above are **read-only**. This skill never writes outside the workspace.

## Procedure

1. <Resolve and classify the input. Say what makes it valid, and what makes it a
   refusal. Refuse with the alternative path rather than proceeding degraded.>
2. <Run the read order above. Report what was found and what was not, by path, before
   producing anything. "Not found" is an output, never a silent omission.>
3. <The skill's actual work, one numbered step per decision. Each step names the rule it
   applies rather than leaving it to judgement.>
4. <Gap handling. For each gap, name where the answer comes from: in the source, in the
   code, needs a human decision, or belongs to a later stage and is out of scope here.
   A human-decision gap blocks; a later-stage gap is marked and does not block.>
5. <Assemble the output in the exact format below.>
6. <Pause. Show the output and wait for approval before any write.>

### Refusals

<The conditions under which this skill produces nothing: an input from the wrong stage,
an unresolved decision, a missing prerequisite file, an ambiguity that a guess would
paper over. For each one, say what to offer instead. A skill that degrades quietly is
worse than one that stops.>

## Output artifact

**Format:**

```
<The exact output shape, with headings, tables and placeholders. Being exact here is
what makes two runs comparable, and what lets a later skill parse the result.>
```

**Where it is saved:** `<folder>/<naming convention>`

- Save only after explicit approval. <Name the approval phrases if the workspace uses
  them.>
- Follow the naming convention already used in the target folder; when the folder is
  empty or the convention is unclear, ask rather than inventing one.
- Confirm the saved path in the reply, then stop.

## Self-check before returning

Answer each of these to yourself, and fix rather than caveat. If a check cannot be
answered yes, say so explicitly in the output rather than staying silent.

- [ ] Every factual claim about current behaviour cites a spec path or a code path.
- [ ] Anything I could not verify is listed as unverified, with what would verify it.
- [ ] I read the specs before the code, and the code before asking the human.
- [ ] No dimension was silently skipped. Where one does not apply, the output says so.
- [ ] The output matches the format above exactly, including headings.
- [ ] Nothing in the output exceeds the workspace sensitivity tier for its destination.
- [ ] Nothing was written outside this workspace, and nothing was written at all without
      approval.
- [ ] <One check specific to this skill, stated as an observable condition.>

## What this skill must never do

- **No git.** No commit, no push, no branch, no pull request, in any repository,
  including this workspace. Preparing a package a human submits is allowed; submitting
  it is not.
- **No writes outside this workspace.** The specs repositories and the code repositories
  are read-only. The only path out is the promotion skill, and it ends with a package,
  not a push.
- **No external writes without approval.** No tracker mutation, no message, no post, no
  upload. Where a write is in scope, it follows preview, confirm, execute: show the
  action plan, wait for an explicit yes, and never infer confirmation from context.
- **No personal data in committed artifacts.** Names, contact details, salary or HR
  content, and privileged passages stay out of anything that outlives the conversation.
  Where the source carries them, omit with a note pointing at the source. Raw
  transcripts stay in the git-ignored folder.
- **No company-specific data in an external query** beyond what the workspace
  sensitivity tier allows. Check the tier before any web search or fetch.
- **No inventing.** No API, config option, field or behaviour that was not read in a
  spec or in code. No deadlines or owners that nobody stated. No confident single
  estimate: base plus contingency plus a one-line justification, or no estimate.
- **No scope expansion.** Do only what was asked. Renaming, restructuring or creating
  adjacent artifacts is a separate request, even when it is obviously an improvement.
