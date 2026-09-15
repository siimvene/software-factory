---
pack: common
description: PLG convention for multilingual fields in APIs and JSON — universal/default language semantics and per-language sections
maintainer: TBD
status: adopted
source: Confluence GAT "Multilingual fields in API / JSON" (page 3034873897, adopted 2026-07-22)
---

# Multilingual Fields in API / JSON

Source of truth: Confluence → GAT → *Multilingual fields in API / JSON*
(includes the Figma UX pattern and full model examples). Rules for any agent
designing or modifying API models with translatable fields:

1. **Model translatable fields with a "universal" default language**, not the
   local market language. Rationale (decided): organizers frequently enter one
   title without picking a language, and defaulting to the local language
   produces mislabeled data (English festival names tagged as Polish).
   The universal value is the fallback for every locale.
2. **Follow the group JSON convention** for per-language sections from the
   source page — do not invent an alternative shape for a new endpoint, even
   inside one service.
3. **`updatedAt` is stored redundantly per language section — deliberately.**
   A shared metadata section was considered and rejected because it couples the
   data model to UI field grouping; regrouping fields in UI must not imply an
   API change. Do not "optimize away" this redundancy.
4. UI for multilingual entry follows the Figma pattern linked from the source
   page (Directus-like language selector, universal as default).

When a task requires deviating from any of these, surface the deviation in the
PR description — the convention is group-wide and a local exception is an
architecture decision, not a task decision.
