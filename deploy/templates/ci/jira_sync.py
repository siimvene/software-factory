#!/usr/bin/env python3
"""jira_sync — keep the KVART Jira ledger in step with what GitHub observed.

The flywheel's ticket states used to be set by hand by whoever ran the loop,
at whatever moment they remembered. This module makes the transitions follow
observed events instead, and stamps the person who picked a ticket up:

  pickup    --key KVART-N                 assign the ticket to the token's own
                                          account and walk it Backlog -> Ready
                                          -> In Progress (the human/operator
                                          side; run locally, see bin wrapper)
  pr-opened --keys K1,K2 --pr-url U --pr-title T [--sha S]
                                          In Progress -> In Test; remote link
                                          to the PR (idempotent on the URL)
  checks    --keys ... --conclusion success|failure --run-url U [--sha S]
                                          success: In Test -> Ready for LIVE
                                          failure: back to In Progress
                                          (anything else: no-op)
  merged    --keys ... --pr-url U --sha S walk to Ready for LIVE (a merge past
                                          the ruleset implies green checks) and
                                          record the sha; Done follows the deploy
  deployed  --keys ... --sha S            walk to Done, with the sha
  link      --keys ... --url U --title T  remote link only
  keys      --text "..."|- [--subjects]   print the ticket keys found in text
                                          (`-` reads stdin; --subjects treats it
                                          as commit subjects and subtracts the
                                          keys that `Revert "..."` lines name)

Every transition is planned from the ticket's CURRENT status (plan_transition),
so replays and out-of-order events are no-ops with a notice, never an error,
and a ticket sent back by a red run is walked forward again by the next green,
the merge or the deploy. A ticket the text does not name is simply not touched.

Auth is HTTP basic from the environment: JIRA_BASE_URL, JIRA_USER_EMAIL,
JIRA_API_TOKEN (in Actions: a repository variable plus two secrets; locally:
the ~/.memspec/bin/jira wrapper fills them from the keychain). The token is
never printed. JIRA_PROJECT_KEY (default KVART) scopes the key regex.

Stdlib only, on purpose: it runs on a bare ubuntu-latest python3 and inside
deploy.sh on the operator's machine without a venv.
"""

from __future__ import annotations

import argparse
import base64
import http.client
import json
import os
import re
import sys
import urllib.parse
from collections.abc import Callable
from typing import Any

# workflow_run conclusions that are a verdict against the code. `cancelled`
# (a superseded push) and `action_required` (awaiting approval) are not.
FAILED_CONCLUSIONS = frozenset({"failure", "timed_out", "startup_failure"})
# The Basic credential goes to whatever JIRA_BASE_URL names, so the name is
# pinned to Atlassian Cloud: a mis-set variable cannot leak the token elsewhere.
ALLOWED_HOST_SUFFIX = ".atlassian.net"
# No PR or deploy range delivers more tickets than this; anything longer is a
# hostile title enumerating keys, and each key costs Jira reads and writes.
MAX_KEYS = 10

BACKLOG = "Backlog"
READY = "Ready"
IN_PROGRESS = "In Progress"
IN_TEST = "In Test"
READY_FOR_LIVE = "Ready for LIVE"
DONE = "Done"

# The board's status workflow, in order. Every forward transition walks a
# contiguous slice of this chain; plan_pickup and plan_transition both index
# into it. A status not on the chain (an unknown column) is off-limits: no
# move is planned to or from it.
CHAIN = [BACKLOG, READY, IN_PROGRESS, IN_TEST, READY_FOR_LIVE, DONE]


# ── pure helpers (unit-tested, no I/O) ──────────────────────────────────────


def extract_keys(text: str, project: str = "KVART") -> list[str]:
    """Ticket keys in `text`, first occurrence order, de-duplicated.

    Word-bounded so `KVART-1` does not match inside `KVART-10`; the branch
    name `feat/KVART-8-apartment-list` and the PR title `(KVART-8)` both count.
    The shorthand `(KVART-5/6/7)` names all three ONLY in that parenthesised
    title form: a bare `KVART-8/4-hotfix` in a branch name or `KVART-8/2026`
    in a subject is KVART-8 alone, so a slash used for something else can
    never reach another ticket.
    """
    seen: list[str] = []
    pattern = rf"(\()?\b{re.escape(project)}-(\d+)((?:/\d+)*)\b(\))?"
    for m in re.finditer(pattern, text or ""):
        numbers = [m.group(2)]
        if m.group(1) and m.group(4):
            numbers += m.group(3).split("/")[1:]
        for number in numbers:
            key = f"{project}-{number}"
            if key not in seen:
                seen.append(key)
    return seen[:MAX_KEYS]


def deployed_keys(subjects: str, project: str = "KVART") -> list[str]:
    """Keys of the changes a range of commit SUBJECTS actually delivers.

    A `Revert "..."` subject names the ticket whose change is being removed;
    its keys are taken OUT even when the reverted commit sits in the same
    range, so a feature merged and reverted between two deploys never closes.
    """
    kept: list[str] = []
    reverted: set[str] = set()
    for line in subjects.splitlines():
        if line.startswith("Revert "):
            reverted.update(extract_keys(line, project))
        else:
            kept.extend(k for k in extract_keys(line, project) if k not in kept)
    return [k for k in kept if k not in reverted]


def _walk(current: str, target: str) -> list[str]:
    """The statuses to step through to drive `current` FORWARD to `target`.

    Empty when the ticket is already at or past `target`, or sits on no known
    column: a forward-only slice of CHAIN, so a replayed or late event and a
    ticket a person moved ahead are both no-ops, and nothing is ever walked
    backward here.
    """
    if current not in CHAIN:
        return []
    i, j = CHAIN.index(current), CHAIN.index(target)
    return CHAIN[i + 1 : j + 1] if i < j else []


def plan_pickup(current: str) -> list[str]:
    """Statuses to walk through, in order, to reach In Progress from `current`."""
    return _walk(current, IN_PROGRESS)


def plan_transition(event: str, current: str, conclusion: str | None = None) -> list[str]:
    """The statuses to walk through, in order, for `event` given the current status.

    The ledger follows the code mechanically: an event drives its ticket
    FORWARD to the status the event implies, from wherever the ticket sits on
    the chain. A PR opened on a Backlog ticket walks it up to In Test; a merge
    lands it at Ready for LIVE, and a deploy at Done, from any earlier column —
    a ticket nobody explicitly picked up is no longer stranded (the guard used
    to require it already be In Progress/In Test). Empty means "leave it": the
    ticket is already at or past that status (a replay, or a person moved it
    ahead) or off the chain. The one backward move is a red run, which returns
    an in-flight ticket to In Progress. Assignment is never touched here — who
    owns a ticket is the operator's explicit `jira pickup`, not a move a merge
    fakes.
    """
    if event == "pr-opened":
        return _walk(current, IN_TEST)
    if event == "checks":
        if conclusion == "success":
            return _walk(current, READY_FOR_LIVE)
        if conclusion in FAILED_CONCLUSIONS:
            return [IN_PROGRESS] if current in (IN_TEST, READY_FOR_LIVE) else []
        return []
    if event == "merged":
        return _walk(current, READY_FOR_LIVE)
    if event == "deployed":
        return _walk(current, DONE)
    return []


def pick_transition(transitions: list[dict[str, Any]], target: str) -> str | None:
    """The id of the transition whose destination status is `target`."""
    for t in transitions:
        if (t.get("to") or {}).get("name") == target:
            return str(t["id"])
    return None


# ── Jira REST (thin) ────────────────────────────────────────────────────────


class Jira:
    def __init__(self, base_url: str, email: str, token: str) -> None:
        self.base = base_url.rstrip("/")
        self._auth = base64.b64encode(f"{email}:{token}".encode()).decode()
        self._epic: dict[str, bool] = {}

    @classmethod
    def from_env(cls) -> Jira:
        missing = [k for k in ("JIRA_BASE_URL", "JIRA_USER_EMAIL", "JIRA_API_TOKEN") if not os.environ.get(k)]
        if missing:
            raise SystemExit(f"jira_sync: missing {', '.join(missing)} in the environment")
        return cls(os.environ["JIRA_BASE_URL"], os.environ["JIRA_USER_EMAIL"], os.environ["JIRA_API_TOKEN"])

    def request(self, method: str, path: str, body: Any | None = None) -> Any:
        # http.client on a host parsed once from JIRA_BASE_URL: https only, no
        # scheme or host ever comes from an argument.
        url = urllib.parse.urlsplit(self.base)
        if url.scheme != "https" or not url.hostname or not url.hostname.endswith(ALLOWED_HOST_SUFFIX):
            raise SystemExit(f"jira_sync: JIRA_BASE_URL must be https://<site>{ALLOWED_HOST_SUFFIX}, got {self.base!r}")
        data = json.dumps(body).encode() if body is not None else None
        headers = {
            "Authorization": "Basic " + self._auth,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        conn = http.client.HTTPSConnection(url.hostname, url.port, timeout=30)
        try:
            conn.request(method, url.path.rstrip("/") + path, body=data, headers=headers)
            resp = conn.getresponse()
            raw = resp.read()
        finally:
            conn.close()
        if resp.status >= 400:
            detail = raw.decode(errors="replace")[:500]
            raise SystemExit(f"jira_sync: {method} {path} -> HTTP {resp.status}: {detail}")
        return json.loads(raw) if raw else None

    # reads
    def myself(self) -> dict[str, Any]:
        return dict(self.request("GET", "/rest/api/3/myself"))

    def status(self, key: str) -> str:
        d = self.request("GET", f"/rest/api/3/issue/{key}?fields=status")
        return str(d["fields"]["status"]["name"])

    def is_epic(self, key: str) -> bool:
        """Anything above story level (Epic, hierarchyLevel >= 1) is a container, not a deliverable."""
        if key not in self._epic:
            d = self.request("GET", f"/rest/api/3/issue/{key}?fields=issuetype")
            self._epic[key] = int(d["fields"]["issuetype"].get("hierarchyLevel") or 0) >= 1
        return self._epic[key]

    def transitions(self, key: str) -> list[dict[str, Any]]:
        return list(self.request("GET", f"/rest/api/3/issue/{key}/transitions")["transitions"])

    # writes
    def transition_to(self, key: str, target: str) -> bool:
        tid = pick_transition(self.transitions(key), target)
        if tid is None:
            notice(f"{key}: no transition to '{target}' from '{self.status(key)}'; left as is")
            return False
        try:
            self.request("POST", f"/rest/api/3/issue/{key}/transitions", {"transition": {"id": tid}})
        except SystemExit as e:
            # A concurrent job may have moved the ticket between the read and
            # the POST (Jira answers 400 for a transition that no longer
            # applies). Report and let the caller re-plan from a fresh read.
            notice(f"{key}: transition to '{target}' refused ({e}); re-reading")
            return False
        return True

    def assign(self, key: str, account_id: str) -> None:
        self.request("PUT", f"/rest/api/3/issue/{key}/assignee", {"accountId": account_id})

    def comment(self, key: str, text: str) -> None:
        body = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
            }
        }
        self.request("POST", f"/rest/api/3/issue/{key}/comment", body)

    def has_comment_mentioning(self, key: str, needle: str) -> bool:
        d = self.request("GET", f"/rest/api/3/issue/{key}/comment?maxResults=100&orderBy=-created")
        return any(needle in json.dumps(c.get("body", {})) for c in d.get("comments", []))

    def remote_link(self, key: str, url: str, title: str) -> None:
        # globalId makes this an upsert: the same PR linked twice stays one link.
        body = {"globalId": url, "object": {"url": url, "title": title}}
        self.request("POST", f"/rest/api/3/issue/{key}/remotelink", body)


def notice(msg: str) -> None:
    # `::notice::` renders in the Actions summary; plain text elsewhere.
    prefix = "::notice::" if os.environ.get("GITHUB_ACTIONS") else ""
    print(prefix + msg)


# ── commands ────────────────────────────────────────────────────────────────


def _move(jira: Jira, key: str, event: str, conclusion: str | None = None) -> str | None:
    """Walk the ticket along the planned path; the status reached, or None if it did not move.

    Epics are never moved by an event: a branch named after the epic
    (`feat/KVART-4-access-trail`) delivers stories, and the epic closes when
    a person says the whole thing is done.
    """
    if jira.is_epic(key):
        notice(f"{key}: epic, left to a person ({event})")
        return None
    current = jira.status(key)
    path = plan_transition(event, current, conclusion)
    if not path:
        notice(f"{key}: '{current}', nothing to do for {event}{' ' + conclusion if conclusion else ''}")
        return None
    reached = None
    replanned = False
    while path:
        step = path[0]
        if jira.transition_to(key, step):
            print(f"{key}: {current} -> {step}")
            current = reached = step
            path = path[1:]
            continue
        if replanned:
            break
        # Re-plan once from what Jira says now (another job may have moved it).
        replanned = True
        current = jira.status(key)
        path = plan_transition(event, current, conclusion)
    return reached


def cmd_pickup(jira: Jira, args: argparse.Namespace) -> int:
    me = jira.myself()
    key = args.key
    jira.assign(key, me["accountId"])
    print(f"{key}: assigned to {me.get('displayName', me['accountId'])}")
    current = jira.status(key)
    for step in plan_pickup(current):
        if not jira.transition_to(key, step):
            return 1
        print(f"{key}: {current} -> {step}")
        current = step
    if not plan_pickup(jira.status(key)) and current != IN_PROGRESS:
        notice(f"{key}: already past In Progress ('{current}'); assignee set, status untouched")
    return 0


def cmd_pr_opened(jira: Jira, args: argparse.Namespace) -> int:
    for key in args.keys:
        jira.remote_link(key, args.pr_url, args.pr_title)
        _move(jira, key, "pr-opened")
    return 0


def cmd_checks(jira: Jira, args: argparse.Namespace) -> int:
    for key in args.keys:
        moved = _move(jira, key, "checks", args.conclusion)
        if moved == IN_PROGRESS:
            jira.comment(key, f"CI failed on {args.sha or 'the PR head'}: {args.run_url}. Back to In Progress.")
    return 0


def cmd_merged(jira: Jira, args: argparse.Namespace) -> int:
    for key in args.keys:
        if jira.is_epic(key):
            notice(f"{key}: epic, left to a person (merged)")
            continue
        _move(jira, key, "merged")
        if jira.has_comment_mentioning(key, args.sha):
            notice(f"{key}: merge at {args.sha} already recorded")
            continue
        jira.comment(key, f"Merged to main at {args.sha} ({args.pr_url}). Done follows the production deploy.")
        print(f"{key}: merge recorded")
    return 0


def cmd_deployed(jira: Jira, args: argparse.Namespace) -> int:
    for key in args.keys:
        if _move(jira, key, "deployed") == DONE:
            jira.comment(key, f"Deployed to production at {args.sha}.")
    return 0


def cmd_link(jira: Jira, args: argparse.Namespace) -> int:
    for key in args.keys:
        jira.remote_link(key, args.url, args.title)
        print(f"{key}: linked {args.url}")
    return 0


def cmd_keys(_jira: Jira | None, args: argparse.Namespace) -> int:
    text = sys.stdin.read() if args.text == "-" else args.text
    keys = deployed_keys(text, args.project) if args.subjects else extract_keys(text, args.project)
    for key in keys:
        print(key)
    return 0


def _keys_type(project: str) -> Callable[[str], list[str]]:
    def parse(value: str) -> list[str]:
        keys = extract_keys(value.replace(",", " "), project)
        if not keys:
            raise argparse.ArgumentTypeError(f"no {project}-N keys in {value!r}")
        return keys

    return parse


def build_parser(project: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jira_sync", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    keys = _keys_type(project)

    s = sub.add_parser("pickup")
    s.add_argument("--key", required=True)
    s.set_defaults(fn=cmd_pickup)

    s = sub.add_parser("pr-opened")
    s.add_argument("--keys", required=True, type=keys)
    s.add_argument("--pr-url", required=True)
    s.add_argument("--pr-title", required=True)
    s.add_argument("--sha")
    s.set_defaults(fn=cmd_pr_opened)

    s = sub.add_parser("checks")
    s.add_argument("--keys", required=True, type=keys)
    s.add_argument("--conclusion", required=True)
    s.add_argument("--run-url", required=True)
    s.add_argument("--sha")
    s.set_defaults(fn=cmd_checks)

    s = sub.add_parser("merged")
    s.add_argument("--keys", required=True, type=keys)
    s.add_argument("--pr-url", required=True)
    s.add_argument("--sha", required=True)
    s.set_defaults(fn=cmd_merged)

    s = sub.add_parser("deployed")
    s.add_argument("--keys", required=True, type=keys)
    s.add_argument("--sha", required=True)
    s.set_defaults(fn=cmd_deployed)

    s = sub.add_parser("link")
    s.add_argument("--keys", required=True, type=keys)
    s.add_argument("--url", required=True)
    s.add_argument("--title", required=True)
    s.set_defaults(fn=cmd_link)

    s = sub.add_parser("keys")
    s.add_argument("--text", required=True)
    s.add_argument("--project", default=project)
    s.add_argument("--subjects", action="store_true", help="text is commit subjects, one per line; reverts subtract")
    s.set_defaults(fn=cmd_keys, offline=True)
    return p


def main(argv: list[str] | None = None) -> int:
    # `or`, not a get() default: the workflows always export the variable, and an unset
    # repository variable arrives as "" (which would turn KVART-12 into "-12").
    project = os.environ.get("JIRA_PROJECT_KEY") or "KVART"
    args = build_parser(project).parse_args(argv)
    jira = None if getattr(args, "offline", False) else Jira.from_env()
    return int(args.fn(jira, args))


if __name__ == "__main__":
    sys.exit(main())
