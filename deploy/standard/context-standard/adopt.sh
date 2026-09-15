#!/usr/bin/env bash
# adopt.sh — seed or resync the context standard into a product repo.
#
#   ./adopt.sh <target-repo>                    seed (day 1): managed + missing seeded files
#   ./adopt.sh --update <target-repo>           resync (day 2): overwrite managed files,
#                                               rewrite the CLAUDE.md sentinel header
#                                               (team front-matter values preserved;
#                                               writes team-context: unset + warns when
#                                               the key is absent), never touch seeded files
#   ./adopt.sh --set-team <org/repo> <target>   wire the team layer: write/update the
#                                               team-context: key + the team @import line
#                                               inside the sentinel, update the lock.
#                                               Pass "none" to opt out. Idempotent.
#   ./adopt.sh --migrate-rule-file <target>     rename a pre-v0.4 AGENTS.md → CLAUDE.md:
#                                               AGENTS.md carries a sentinel and CLAUDE.md
#                                               is absent → git mv + rewrite sentinel + lock.
#                                               Both present → keep CLAUDE.md canonical, warn.
#   ./adopt.sh --check  <target-repo>           verify: lock shas, sentinel, version (CI parity)
#   ./adopt.sh --force  <target-repo>           overwrite EVERYTHING, seeded included (destructive)
#   Add --dry-run to any mode to see what would happen without writing.
#
# File classes come from template/MANIFEST (managed / seeded) — see
# governance/distribution.md. {{PLACEHOLDERS}} in seeded files are intentional;
# fill them per repo after adoption.
set -euo pipefail

STD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$STD_DIR/template"
MANIFEST="$TEMPLATE/MANIFEST"
RULE_FILE="CLAUDE.md"
VERSION="$(grep -Eo 'context-standard: v[0-9]+\.[0-9]+' "$TEMPLATE/$RULE_FILE" | head -1 | awk '{print $2}')"
LOCK=".context-standard.lock"

sha() { if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | cut -d' ' -f1; else sha256sum "$1" | cut -d' ' -f1; fi; }
files_of() { awk -v c="$1" '$1==c {print $2}' "$MANIFEST"; }

valid_team() { # <org>/<repo> — reject empty or dot-only ("." / "..") segments,
  # which would make the derived /workspaces/<repo> import escape /workspaces/.
  printf '%s' "$1" | grep -Eq '^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$' || return 1
  printf '%s' "$1" | grep -Eq '(^|/)\.{1,2}(/|$)' && return 1
  return 0
}

require_end_sentinel() { # <file> — begin without end would make the sentinel
  # rewrite swallow everything after begin, destroying the team-owned body.
  grep -q '<!-- context-standard:end' "$1" && return 0
  echo "  FAIL: $1 has '<!-- context-standard:begin -->' but no '<!-- context-standard:end' marker." >&2
  echo "        Refusing to rewrite — the sentinel rewrite would delete everything after begin." >&2
  echo "        Restore the end-marker line, then re-run." >&2
  exit 1
}

mode=seed; dryrun=0; target=""; team_arg=""
args=()
for arg in "$@"; do args+=("$arg"); done
i=0; n=${#args[@]}
while [ "$i" -lt "$n" ]; do
  arg="${args[$i]}"
  case "$arg" in
    --update)  mode=update ;;
    --check)   mode=check ;;
    --force)   mode=force ;;
    --migrate-rule-file) mode=migrate ;;
    --set-team)
      mode=setteam
      i=$((i + 1))
      [ "$i" -lt "$n" ] || { echo "--set-team needs an argument: <org/repo> or none" >&2; exit 2; }
      team_arg="${args[$i]}"
      ;;
    --dry-run) dryrun=1 ;;
    -*) echo "unknown flag: $arg" >&2; exit 2 ;;
    *)  target="$arg" ;;
  esac
  i=$((i + 1))
done
[ -n "$target" ] || { echo "usage: adopt.sh [--update|--check|--force|--migrate-rule-file|--set-team <org/repo>] [--dry-run] <target-repo>" >&2; exit 2; }
[ -d "$target" ] || { echo "target not a directory: $target" >&2; exit 2; }

if [ "$mode" = setteam ]; then
  if [ -z "$team_arg" ]; then
    echo "--set-team needs <org/repo> or none" >&2; exit 2
  elif [ "$team_arg" != none ] && ! valid_team "$team_arg"; then
    echo "--set-team value must look like <org>/<repo> (no '.' or '..' segments) or be 'none' (got: $team_arg)" >&2; exit 2
  fi
fi

echo "context-standard $VERSION → $target  (mode: $mode)"
[ "$dryrun" = 1 ] && echo "(dry run — no files will be written)"

put() { # put <rel> — copy template file to target
  [ "$dryrun" = 1 ] && return 0
  mkdir -p "$(dirname "$target/$1")"
  cp "$TEMPLATE/$1" "$target/$1"
}

# agents-core.md is fetched from Piletilevi/plg-development-standards (not shipped
# in the template). Version-floating: tracks the source default branch; the lock
# pins the fetched bytes by sha per adoption.
CORE_REL="docs/standard/agents-core.md"
CORE_SRC="Piletilevi/plg-development-standards"
fetch_core() { # fetch_core <outfile>
  if command -v gh >/dev/null 2>&1 && gh api "repos/$CORE_SRC/contents/agents-core.md"       -H "Accept: application/vnd.github.raw" > "$1" 2>/dev/null && [ -s "$1" ]; then return 0; fi
  curl -sf -H "Authorization: Bearer ${GITHUB_TOKEN:-}" -H "Accept: application/vnd.github.raw"     "https://api.github.com/repos/$CORE_SRC/contents/agents-core.md" > "$1" && [ -s "$1" ]
}

sync_managed() { # always safe: teams do not own these files
  local rel="$1" src
  if [ "$rel" = "$CORE_REL" ]; then
    src="$(mktemp)"
    if ! fetch_core "$src"; then
      if [ -f "$target/$CORE_REL" ] && [ -s "$target/$CORE_REL" ]; then
        # Offline: reuse the vendored copy (may trail; next online update reconciles).
        echo "  WARN: cannot fetch agents-core.md from $CORE_SRC (no gh auth/GITHUB_TOKEN) — keeping the existing vendored copy (may trail the managed source)"
        cp "$target/$CORE_REL" "$src"
      else
        echo "  FAIL: cannot fetch agents-core.md from $CORE_SRC (need gh auth or GITHUB_TOKEN) and no existing vendored copy to fall back to"; exit 1
      fi
    fi
  else
    src="$TEMPLATE/$rel"
  fi
  if cmp -s "$src" "$target/$rel" 2>/dev/null; then
    echo "  ok (current): $rel"
  else
    echo "  sync: $rel"
    [ "$dryrun" = 1 ] || { mkdir -p "$(dirname "$target/$rel")"; cp "$src" "$target/$rel"; }
  fi
  [ "$rel" = "$CORE_REL" ] && rm -f "$src" 2>/dev/null
  return 0
}

seed_seeded() { # copy once; existing files are the team's
  local rel="$1"
  if [ -e "$target/$rel" ]; then echo "  skip (team-owned): $rel"
  else echo "  copy: $rel"; put "$rel"; fi
}

# build_sentinel <conf> <kit> <team> — emit the sentinel block: template structure,
# substituted values; <org>/<repo> injects the team @import, none/unset inject nothing.
build_sentinel() {
  local conf="$1" kit="$2" team="$3" reponame=""
  case "$team" in
    */*) reponame="${team##*/}" ;;
  esac
  awk -v conf="$conf" -v kit="$kit" -v team="$team" -v reponame="$reponame" '
    /^conformance:/  { print "conformance: " conf; next }
    /^starter-kit:/  { print "starter-kit: " kit; next }
    /^team-context:/ { print "team-context: " team; next }
    /^@docs\/standard\/agents-core\.md/ {
      print
      if (reponame != "") {
        print "@/workspaces/" reponame "/CLAUDE.md"
        print "<!-- Non-Claude agents: read /workspaces/" reponame "/CLAUDE.md before working. -->"
      }
      next
    }
    { print }
  ' <(sed -n '/<!-- context-standard:begin -->/,/<!-- context-standard:end/p' "$TEMPLATE/$RULE_FILE")
}

# replace_block <tgt> <blockfile> — swap the sentinel block in <tgt> for <blockfile>
# (which itself contains begin…end). Everything outside the block is preserved.
replace_block() {
  local tgt="$1" blockfile="$2"
  require_end_sentinel "$tgt"
  awk -v hdrfile="$blockfile" '
    /<!-- context-standard:begin -->/ {while ((getline l < hdrfile) > 0) print l; inblk=1; next}
    /<!-- context-standard:end/       {inblk=0; next}
    !inblk {print}' "$tgt" > "$tgt.tmp" && mv "$tgt.tmp" "$tgt"
}

read_fm() { # read_fm <file> <key> — first front-matter value for key
  sed -n "s/^$2: *//p" "$1" | head -1
}

update_sentinel() { # rewrite only the managed header block; body untouched;
  local tgt="$target/$RULE_FILE"  # team's conformance/starter-kit/team-context preserved
  [ -f "$tgt" ] || { echo "  $RULE_FILE missing — seeding fresh copy"; put "$RULE_FILE"; return; }
  grep -q '<!-- context-standard:begin -->' "$tgt" || {
    echo "  WARN: $RULE_FILE has no sentinel block — prepending one; review the file manually."
    [ "$dryrun" = 1 ] && return 0
    { build_sentinel "L0" "none" "unset"; echo; cat "$tgt"; } > "$tgt.tmp" && mv "$tgt.tmp" "$tgt"
    return
  }
  require_end_sentinel "$tgt"
  local conf kit team
  conf="$(read_fm "$tgt" conformance)"; [ -n "$conf" ] || conf="L0"
  kit="$(read_fm "$tgt" starter-kit)";  [ -n "$kit" ]  || kit="none"
  team="$(read_fm "$tgt" team-context)"
  if [ -z "$team" ]; then
    team="unset"
    echo "  WARN: $RULE_FILE has no team-context key — writing 'unset'. Answer it with:"
    echo "        adopt.sh --set-team <org>/<team>-team-context $target"
  fi
  local blk; blk="$(mktemp)"
  build_sentinel "$conf" "$kit" "$team" > "$blk"
  if cmp -s "$blk" <(sed -n '/<!-- context-standard:begin -->/,/<!-- context-standard:end/p' "$tgt"); then
    echo "  ok (current): $RULE_FILE sentinel header"; rm -f "$blk"; return
  fi
  echo "  sync: $RULE_FILE sentinel header (conformance=$conf starter-kit=$kit team-context=$team preserved)"
  [ "$dryrun" = 1 ] && { rm -f "$blk"; return 0; }
  replace_block "$tgt" "$blk"
  rm -f "$blk"
}

set_team() { # --set-team: write team-context key + import line, update lock
  local tgt="$target/$RULE_FILE"
  [ -f "$tgt" ] || { echo "  FAIL: $RULE_FILE not found in $target — adopt the repo first"; exit 1; }
  grep -q '<!-- context-standard:begin -->' "$tgt" || { echo "  FAIL: $RULE_FILE has no sentinel block — run adopt.sh --update first"; exit 1; }
  require_end_sentinel "$tgt"
  local conf kit
  conf="$(read_fm "$tgt" conformance)"; [ -n "$conf" ] || conf="L0"
  kit="$(read_fm "$tgt" starter-kit)";  [ -n "$kit" ]  || kit="none"
  echo "  set team-context: $team_arg"
  [ "$dryrun" = 1 ] && { echo "  (dry run) would rewrite sentinel + lock"; return 0; }
  local blk; blk="$(mktemp)"
  build_sentinel "$conf" "$kit" "$team_arg" > "$blk"
  replace_block "$tgt" "$blk"
  rm -f "$blk"
  write_lock
  case "$team_arg" in
    none) echo "  team layer opted out (team-context: none) — no import, tripwire suppressed." ;;
    *)    echo "  team import wired → /workspaces/${team_arg##*/}/CLAUDE.md" ;;
  esac
}

migrate_rule_file() { # --migrate-rule-file: AGENTS.md → CLAUDE.md
  local old="$target/AGENTS.md" new="$target/$RULE_FILE"
  if [ -f "$new" ] && [ -f "$old" ]; then
    echo "  WARN: both AGENTS.md and $RULE_FILE exist — keeping $RULE_FILE canonical."
    echo "        Reconcile any divergence by hand, then reduce AGENTS.md to a one-line"
    echo "        pointer ('read CLAUDE.md') or delete it. Leaving AGENTS.md untouched."
    return 0
  fi
  if [ ! -f "$old" ]; then
    echo "  nothing to migrate: no AGENTS.md in $target"
    [ -f "$new" ] && echo "  ($RULE_FILE already present)"
    return 0
  fi
  grep -q '<!-- context-standard:begin -->' "$old" || {
    echo "  WARN: AGENTS.md has no context-standard sentinel — not a managed rule file."
    echo "        Not migrating automatically; rename by hand if intended."
    return 0
  }
  echo "  migrate: AGENTS.md → $RULE_FILE (rename + rewrite sentinel to $VERSION)"
  [ "$dryrun" = 1 ] && { echo "  (dry run) would git mv + rewrite sentinel + lock"; return 0; }
  if git -C "$target" ls-files --error-unmatch AGENTS.md >/dev/null 2>&1; then
    git -C "$target" mv AGENTS.md "$RULE_FILE"
  else
    mv "$old" "$new"
  fi
  local conf kit team
  conf="$(read_fm "$new" conformance)"; [ -n "$conf" ] || conf="L0"
  kit="$(read_fm "$new" starter-kit)";  [ -n "$kit" ]  || kit="none"
  team="$(read_fm "$new" team-context)"
  if [ -z "$team" ]; then
    team="unset"
    echo "  team-context absent in migrated file — writing 'unset' (tripwire stays live)."
    echo "  answer it: adopt.sh --set-team <org>/<team>-team-context $target"
  fi
  local blk; blk="$(mktemp)"
  build_sentinel "$conf" "$kit" "$team" > "$blk"
  replace_block "$new" "$blk"
  rm -f "$blk"
  write_lock
  echo "  done. commit the rename (git mv preserves history)."
}

write_lock() { # lock = version + sha256 per managed file, from target bytes
  echo "  write: $LOCK"
  [ "$dryrun" = 1 ] && return 0
  { echo "# Managed by adopt.sh — do not edit. Divergence policy: governance/distribution.md §8."
    echo "context-standard: $VERSION"
    echo "managed:"
    files_of managed | while read -r rel; do
      printf '  %s: "sha256:%s"\n' "$rel" "$(sha "$target/$rel")"
    done
  } > "$target/$LOCK"
}

write_gitattributes() { # sha-covered bytes must survive autocrlf checkouts
  local line added=0
  for line in "docs/standard/* text eol=lf" "$LOCK text eol=lf"; do
    grep -qxF "$line" "$target/.gitattributes" 2>/dev/null && continue
    echo "  append: .gitattributes ($line)"
    [ "$dryrun" = 1 ] || echo "$line" >> "$target/.gitattributes"
    added=1
  done
  # plain if: a bare `[ ... ] &&` returns 1 when lines were appended → set -e kills the run
  if [ "$added" = 0 ]; then echo "  ok (current): .gitattributes"; fi
}

check() {
  local fail=0 rel want got team
  [ -f "$target/$LOCK" ] || { echo "  FAIL: $LOCK missing — not adopted?"; exit 1; }
  got="$(sed -n 's/^context-standard: //p' "$target/$LOCK" | head -1)"
  echo "  lock version: $got (template: $VERSION)"
  [ "${got%%.*}" = "${VERSION%%.*}" ] || { echo "  FAIL: major version behind — run adopt.sh --update"; fail=1; }
  while read -r rel; do
    want="$(sed -n "s|^  $rel: \"sha256:\(.*\)\"|\1|p" "$target/$LOCK")"
    if [ -z "$want" ]; then echo "  FAIL: $rel not in lock"; fail=1; continue; fi
    if [ ! -f "$target/$rel" ]; then echo "  FAIL: $rel missing"; fail=1; continue; fi
    if [ "$(sha "$target/$rel")" = "$want" ]; then echo "  ok: $rel"
    else echo "  FAIL: $rel — sha mismatch (managed file edited locally; see distribution.md §8)"; fail=1; fi
  done < <(files_of managed)
  if grep -q '<!-- context-standard:begin -->' "$target/$RULE_FILE" 2>/dev/null \
    && grep -q '@docs/standard/agents-core.md' "$target/$RULE_FILE"; then
    echo "  ok: $RULE_FILE sentinel + agents-core pointer"
  else
    echo "  FAIL: $RULE_FILE sentinel header or agents-core pointer missing"; fail=1
  fi
  # L0: team-context key must be present and resolved (org/repo or none; unset fails).
  team="$( [ -f "$target/$RULE_FILE" ] && read_fm "$target/$RULE_FILE" team-context || true )"
  if [ "$team" = none ] || valid_team "$team"; then
    echo "  ok: team-context resolved ($team)"
  elif [ -z "$team" ] || [ "$team" = unset ]; then
    echo "  FAIL: team-context is '${team:-absent}' — resolve it (adopt.sh --set-team <org/repo>|none)"; fail=1
  else
    echo "  FAIL: team-context value malformed ($team) — expected <org>/<repo> or none"; fail=1
  fi
  [ -f "$target/.memspec.yaml" ] && echo "  ok: .memspec.yaml" || { echo "  FAIL: .memspec.yaml pointer missing"; fail=1; }
  [ "$fail" = 0 ] && echo "check: PASS" || { echo "check: FAIL"; exit 1; }
}

case "$mode" in
  seed)
    files_of managed | while read -r rel; do sync_managed "$rel"; done
    files_of seeded  | while read -r rel; do seed_seeded "$rel"; done
    write_lock; write_gitattributes
    echo "done. next:"
    echo "  1. fill {{PLACEHOLDERS}} in $RULE_FILE and docs/ (seeded files are yours)"
    echo "  2. wire the team layer:  adopt.sh --set-team <org>/<team>-team-context $target  (or 'none')"
    echo "  3. fill {{TEAM_CONTEXT}} in .memspec.yaml (the pointer binding this repo to the team memspec store; no local store is created)"
    echo "  4. add the GitHub topic:  gh repo edit --add-topic context-standard"
    echo "  5. commit everything, including $LOCK"
    ;;
  update)
    files_of managed | while read -r rel; do sync_managed "$rel"; done
    files_of seeded  | while read -r rel; do
      [ "$rel" = "$RULE_FILE" ] && continue
      if [ ! -e "$target/$rel" ]; then echo "  copy (new in template): $rel"; put "$rel"
      elif ! cmp -s "$TEMPLATE/$rel" "$target/$rel"; then
        echo "  fyi (team-owned, differs from template — cherry-pick if useful): $rel"
      fi
    done
    update_sentinel
    write_lock; write_gitattributes
    echo "done. review the diff, then commit (branch chore/context-standard-$VERSION suggested)."
    ;;
  setteam) set_team ;;
  migrate) migrate_rule_file ;;
  check) check ;;
  force)
    if [ "$dryrun" != 1 ]; then
      printf "This OVERWRITES team-owned seeded files in %s. Type 'yes' to continue: " "$target"
      read -r ans; [ "$ans" = "yes" ] || { echo "aborted."; exit 1; }
    fi
    files_of managed | while read -r rel; do sync_managed "$rel"; done
    files_of seeded  | while read -r rel; do echo "  OVERWRITE: $rel"; put "$rel"; done
    write_lock; write_gitattributes
    echo "done (forced)."
    ;;
esac
