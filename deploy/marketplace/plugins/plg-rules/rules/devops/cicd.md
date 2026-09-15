---
pack: devops
description: PLG CI/CD rules for application container images and Helm charts — branching, tagging, pipeline steps, production promotion
maintainer: TBD
status: adopted
source: Confluence GPM "CI/CD process for applications" (page 2625863700, adopted 2026-07-22)
---

# CI/CD Rules — Application Images and Charts

Source of truth for the full process: Confluence → GPM → *CI/CD process for
applications*. These are the rules an agent must follow when touching CI
workflows, Dockerfiles, or deployment configs. Post-registry behavior (Flux
reconciliation, per-country rollout) is out of scope here.

## Structure

- One application per repository; one container image per build.
- CI platform is **GitHub Actions**; registry is **Google Artifact Registry**
  (both images and Helm charts, OCI).
- Feature flags control per-country behavior. Never create per-country builds.

## Branching and tagging

| Branch | Image tag | Example |
|---|---|---|
| `main` | `YYYYMMDDHHMMSS` (UTC at build start) | `portal-ui:20260225124348` |
| feature branch | `{sanitized-branch}-{short-sha}` | `portal-ui:feature-new-checkout-a1b2c3d` |

- Sanitize branch names for OCI (`/` → `-`).
- Timestamp tags are numerically Flux-sortable — do NOT switch a repo to semver
  tags ad hoc; that is an org-level migration, not a repo tweak.
- Feature-branch images are for ephemeral/staging testing only. Never promote
  one to production.

## Pipeline steps (every push to main and feature branches)

1. Checkout and setup
2. **Test — the suite runs and failure fails the pipeline.** Never skip, mute,
   or conditionally bypass the test step to get an image out.
3. Build from the repo's Dockerfile
4. Tag per branch type (above)
5. Push to Artifact Registry

- Registry auth uses **Workload Identity Federation** between GitHub Actions
  and GCP. Never introduce service-account key files into a workflow.
- Feature-branch images accumulate: repos need an Artifact Registry cleanup
  policy pruning old images.

## Production promotion

Trunk images do not automatically reach production. Two approved gates:

- **Option A — prefix promotion:** a separate, explicitly triggered workflow
  re-tags a verified image with `prod-`; Flux `filterTags` matches only the
  prefix. Same digest, new tag.
- **Option B — manual GitOps bump:** no image automation in production; every
  deployment is a reviewed PR against the GitOps repo.

An agent must not convert a repo from one option to the other, weaken a
promotion gate, or add production `ImageUpdateAutomation` — those are
architecture changes requiring human decision, not task work.
