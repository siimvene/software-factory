# How this repository is written

This repository is the reference design for a dark factory: an agentic software delivery
line where humans specify outcomes and inspect evidence, and machines build, verify and
ship. It is written to be adapted by any company. Every rule below exists so that the text
can be published without a scrub pass.

## Anonymization (non-negotiable)

- The only named product is **kvart**, the reference implementation. It is the author's own
  product and its numbers are the author's own data.
- The employer and its systems are never named. Say **"the group"** for the organisation,
  **"the legacy core"** for its ticketing monolith (a Java/Gradle system of 75 modules), and
  **"the group standard"** for its published agent standards. No repo names, no wiki page
  identifiers, no cloud project names, no cost mandates, no ownership or exit information.
- No person names other than **Siim** (the operator). Colleagues appear as roles: "the CIO",
  "a PM", "the code owner", "a staff engineer at a large marketplace".
- Third-party tools and public sources may be named: cleat, consort, memspec, enola, ripwire,
  ponytail, the context standard, Claude Code, Codex, Gemini, Uber Engineering, Pipedrive.
- No credentials, tokens, hostnames, ports of private machines, or private URLs.

## Evidence classes

Every claim carries its class, because the difference is the whole point of the design:

| Class | Meaning | Marker |
|---|---|---|
| **measured** | a number or behaviour observed by running something, with the date | `[measured 2026-09-07]` |
| **designed** | built and wired, not yet exercised end to end | `[designed]` |
| **proposed** | argued, reviewed, not adopted | `[proposed]` |
| **field** | from a public external source | `[field: source]` |

`STATUS.md` is the ledger of which parts of the design sit in which class.

## Prose

- Plain technical prose. One idea per sentence. Short paragraphs.
- No em dashes. Commas, colons, parentheses, full stops.
- Numbers as digits, with units, with the date they were measured.
- A rule and its mechanism go together: a rule without an enforcing check is written as a
  rule *and* its check, or it is labelled advisory.
- Commands, file names and error text go in code spans or fenced blocks, never in running
  prose beyond one identifier per sentence.
- Every "why" is stated. A design choice without its rejected alternative is incomplete.

## Files

- `docs/` is the design, numbered in reading order.
- `case-studies/` is what happened, with dates and numbers.
- `evidence/` holds source reports copied close to verbatim (anonymised), so the case studies
  can be checked against them.
- `templates/` are the artifacts a team copies on day one.
- `adr/` records the decisions of this design itself, in the same format the design asks
  adopters to use.
