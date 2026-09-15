# dev-hygiene

## Overview
Three finishing-pass skills for agent work: `verify` (no completion claims
without fresh evidence), `deslop` (behavior-preserving cleanup of recent
changes), `meta-reasoning` (decompose / confidence / refute for complex calls).
All propose-only: working-tree edits at most, never commit/push/merge.

## Usage
Install: `/plugin install dev-hygiene@plg-skills`. Skills fire on their
triggers (completion claims, "deslop"/"cleanup", "think carefully") or invoke
directly. Pairs with the org rule packs — deslop and verify respect loaded
pack conventions.

## Maintainers
- Siim Vene. Checklist content salvaged from an audited legacy standards corpus
  (2026-07-22); operating rules rewritten for the PLG contract
  (agents propose, humans merge).
