# solo-review

## Overview
Single-model, pack-aware review for environments without a second vendor —
no Codex CLI or no OpenAI egress (e.g. base-profile sandboxes). Loads
`PLG_RULE_PACKS`/`CONSORT_RULE_PACKS` and reports severity-rated findings.
**This is the fallback: `/consort:review` is the PLG standard** — one model
reviewing alone shares its own blind spots, and this skill says so in its
output.

## Usage
`/plugin install solo-review@plg-skills`, then ask for a review with packs set:
`PLG_RULE_PACKS="path/to/rules/common:path/to/rules/security"`. Never applies
its own findings; fixing is a separate, explicitly requested pass.

## Maintainers
- Siim Vene. Severity taxonomy salvaged from a legacy review skill; the
  self-applying workflow was deliberately not ported.
