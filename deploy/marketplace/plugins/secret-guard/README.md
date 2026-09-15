# secret-guard

## Overview
A deterministic PreToolUse hook that blocks Read/Bash tool calls targeting
secret-bearing files: `.env*` (templates `.env.example/.tpl/.template/.sample`
allowed), private keys, keystores, kubeconfigs, `.aws/credentials`, `.npmrc`,
`auth.json`, `.netrc`. Exit-2 block with an explanation the model can act on
(fetch secrets at runtime via op run / ADC instead).

## Usage
`/plugin install secret-guard@plg-skills` — active immediately, no
configuration. False positive? Rename the file to a template suffix or read it
yourself. This guard is client-side defense in depth: the real controls are
vault ACLs and scoped identities. Intended to be **mandated via server-managed
settings** once the policy rail is live; marketplace install is the
distribution mechanism.

## Maintainers
- Siim Vene. Ported from a legacy secret-read guard hook (Cursor
  format) to Claude Code PreToolUse; pattern list extended (cloud creds,
  kubeconfig, keystores) and template allowlist added.
