"""Unit tests for scripts/ci/jira_sync.py (Jira ledger sync from GitHub events).

Pure logic plus a fake Jira: no network, no git, so this runs on the plain unit
path without Docker. The module is loaded by file path like its sibling
select-tests tests.
"""

import importlib.util
import io
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "jira_sync.py"
_spec = importlib.util.spec_from_file_location("ci_jira_sync", _MODULE_PATH)
js = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(js)


# ── key extraction ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "text,expected",
    [
        ("feat/KVART-8-apartment-list-no-owner-names", ["KVART-8"]),
        ("fix(meters): ... (KVART-3)", ["KVART-3"]),
        ("KVART-10 then KVART-1 then KVART-10 again", ["KVART-10", "KVART-1"]),
        ("KVART-1 KVART-10 KVART-100", ["KVART-1", "KVART-10", "KVART-100"]),
        ("ci: runner wake, no ticket", []),
        ("", []),
        ("lowercase kvart-4 does not count", []),
        ("XKVART-4 is another project's suffix", []),
        ("feat(audit): access trail (KVART-5/6/7)", ["KVART-5", "KVART-6", "KVART-7"]),  # title shorthand
        ("(KVART-1/10) and (KVART-10/1)", ["KVART-1", "KVART-10"]),
        ("feat/KVART-8-apartment-list/4", ["KVART-8"]),  # a slash after a word, not after the number
        ("feat/KVART-8/4-hotfix", ["KVART-8"]),  # bare shorthand outside parentheses never expands
        ("fix: KVART-8/2026 allocation", ["KVART-8"]),
        ("(KVART-8/2026 allocation)", ["KVART-8"]),  # not closed right after the numbers
    ],
)
def test_extract_keys(text, expected):
    assert js.extract_keys(text) == expected


@pytest.mark.parametrize(
    "subjects,expected",
    [
        ("feat: a (KVART-1)\nfix: b (KVART-2)", ["KVART-1", "KVART-2"]),
        ('feat: a (KVART-1)\nRevert "feat: a (KVART-1)"', []),  # merged and reverted in one range
        ('Revert "feat: old (KVART-3)"\nfeat: new (KVART-4)', ["KVART-4"]),
        ("Merge pull request #36 from siimvene/feat/KVART-8-apartment-list", ["KVART-8"]),
        ("", []),
    ],
)
def test_deployed_keys_subtracts_reverts(subjects, expected):
    assert js.deployed_keys(subjects) == expected


def test_extract_keys_is_capped():
    hostile = "(KVART-" + "/".join(str(n) for n in range(1, 501)) + ")"
    assert len(js.extract_keys(hostile)) == js.MAX_KEYS
    assert js.extract_keys(" ".join(f"KVART-{n}" for n in range(1, 40)))[-1] == f"KVART-{js.MAX_KEYS}"


def test_extract_keys_other_project():
    assert js.extract_keys("EST-9 and KVART-2", project="EST") == ["EST-9"]


# ── transition planning (the part that makes replays harmless) ──────────────


@pytest.mark.parametrize(
    "current,expected",
    [
        ("Backlog", ["Ready", "In Progress"]),
        ("Ready", ["In Progress"]),
        ("In Progress", []),
        ("In Test", []),
        ("Done", []),
    ],
)
def test_plan_pickup(current, expected):
    assert js.plan_pickup(current) == expected


@pytest.mark.parametrize(
    "event,current,conclusion,expected",
    [
        ("pr-opened", "In Progress", None, ["In Test"]),
        ("pr-opened", "In Test", None, []),  # replay (reopened PR, edited title)
        ("pr-opened", "Ready", None, ["In Progress", "In Test"]),  # drive it up from wherever it sits
        ("pr-opened", "Backlog", None, ["Ready", "In Progress", "In Test"]),  # unpicked: still walked up
        ("checks", "In Test", "success", ["Ready for LIVE"]),
        ("checks", "In Progress", "success", ["In Test", "Ready for LIVE"]),  # green after a red run
        ("checks", "Ready", "success", ["In Progress", "In Test", "Ready for LIVE"]),  # drive up from earlier
        ("checks", "Ready for LIVE", "success", []),  # second green run
        ("checks", "In Test", "failure", ["In Progress"]),
        ("checks", "Ready for LIVE", "failure", ["In Progress"]),  # a later push went red
        ("checks", "In Progress", "failure", []),
        ("checks", "In Test", "cancelled", []),  # superseded push, not a verdict
        ("checks", "In Test", "skipped", []),
        ("checks", "In Test", "action_required", []),  # awaiting approval, not a verdict
        ("checks", "In Test", "timed_out", ["In Progress"]),
        ("checks", "Ready for LIVE", "startup_failure", ["In Progress"]),
        ("merged", "In Test", None, ["Ready for LIVE"]),  # merged before the checks event landed
        ("merged", "In Progress", None, ["In Test", "Ready for LIVE"]),
        ("merged", "Ready", None, ["In Progress", "In Test", "Ready for LIVE"]),
        ("merged", "Backlog", None, ["Ready", "In Progress", "In Test", "Ready for LIVE"]),  # merged, never picked up
        ("merged", "Ready for LIVE", None, []),
        ("merged", "Done", None, []),
        ("deployed", "Ready for LIVE", None, ["Done"]),
        ("deployed", "In Test", None, ["Ready for LIVE", "Done"]),
        ("deployed", "In Progress", None, ["In Test", "Ready for LIVE", "Done"]),
        ("deployed", "Done", None, []),
        ("deployed", "Ready", None, ["In Progress", "In Test", "Ready for LIVE", "Done"]),  # shipped closes it, picked up or not
        ("bogus", "In Test", None, []),
    ],
)
def test_plan_transition(event, current, conclusion, expected):
    assert js.plan_transition(event, current, conclusion) == expected


def test_pick_transition_by_destination_name():
    transitions = [
        {"id": "31", "name": "Test failed", "to": {"name": "In Progress"}},
        {"id": "41", "name": "Ready for LIVE", "to": {"name": "Ready for LIVE"}},
    ]
    assert js.pick_transition(transitions, "In Progress") == "31"
    assert js.pick_transition(transitions, "Ready for LIVE") == "41"
    assert js.pick_transition(transitions, "Done") is None
    assert js.pick_transition([], "Done") is None


# ── commands against a fake Jira ────────────────────────────────────────────


WORKFLOW = {
    "Backlog": {"Ready": "11"},
    "Ready": {"In Progress": "21", "Backlog": "91"},
    "In Progress": {"In Test": "31"},
    "In Test": {"Ready for LIVE": "41", "In Progress": "71"},
    "Ready for LIVE": {"Done": "51", "In Progress": "81"},
    "Done": {},
}


class FakeJira(js.Jira):
    def __init__(self, statuses, epics=()):
        super().__init__("https://x.invalid", "e", "t")
        self.statuses = dict(statuses)
        self.epics = set(epics)
        self.assigned = {}
        self.comments = []
        self.links = []

    def myself(self):
        return {"accountId": "acc-1", "displayName": "Operator"}

    def has_comment_mentioning(self, key, needle):
        return any(k == key and needle in text for k, text in self.comments)

    def status(self, key):
        return self.statuses[key]

    def is_epic(self, key):
        self.epic_reads = getattr(self, "epic_reads", 0) + 1
        return key in self.epics

    def transitions(self, key):
        return [{"id": tid, "to": {"name": to}} for to, tid in WORKFLOW[self.statuses[key]].items()]

    def request(self, method, path, body=None):  # every write funnels through here
        key = path.split("/")[5]  # /rest/api/3/issue/<key>/...
        if path.endswith("/transitions") and method == "POST":
            tid = body["transition"]["id"]
            to = next(t for t, i in WORKFLOW[self.statuses[key]].items() if i == tid)
            self.statuses[key] = to
            return None
        if path.endswith("/assignee"):
            self.assigned[key] = body["accountId"]
            return None
        if path.endswith("/comment"):
            self.comments.append((key, body["body"]["content"][0]["content"][0]["text"]))
            return None
        if path.endswith("/remotelink"):
            self.links.append((key, body["globalId"], body["object"]["title"]))
            return None
        raise AssertionError(f"unexpected {method} {path}")


def run(jira, *argv):
    args = js.build_parser("KVART").parse_args(list(argv))
    return args.fn(jira, args)


def test_pickup_from_backlog_assigns_and_walks_to_in_progress():
    j = FakeJira({"KVART-9": "Backlog"})
    assert run(j, "pickup", "--key", "KVART-9") == 0
    assert j.assigned == {"KVART-9": "acc-1"}
    assert j.statuses["KVART-9"] == "In Progress"


def test_pickup_past_in_progress_only_assigns():
    j = FakeJira({"KVART-8": "Ready for LIVE"})
    assert run(j, "pickup", "--key", "KVART-8") == 0
    assert j.assigned == {"KVART-8": "acc-1"}
    assert j.statuses["KVART-8"] == "Ready for LIVE"


def test_pr_opened_links_and_moves_to_in_test():
    j = FakeJira({"KVART-5": "In Progress", "KVART-6": "In Progress"})
    run(j, "pr-opened", "--keys", "KVART-5,KVART-6", "--pr-url", "https://gh/pr/40", "--pr-title", "feat (KVART-5)")
    assert j.statuses == {"KVART-5": "In Test", "KVART-6": "In Test"}
    assert j.links == [("KVART-5", "https://gh/pr/40", "feat (KVART-5)"), ("KVART-6", "https://gh/pr/40", "feat (KVART-5)")]


def test_pr_opened_replay_is_a_noop_but_keeps_the_link():
    j = FakeJira({"KVART-8": "Ready for LIVE"})
    run(j, "pr-opened", "--keys", "KVART-8", "--pr-url", "https://gh/pr/36", "--pr-title", "t")
    assert j.statuses["KVART-8"] == "Ready for LIVE"
    assert len(j.links) == 1


def test_checks_success_then_failure_round_trip():
    j = FakeJira({"KVART-8": "In Test"})
    run(j, "checks", "--keys", "KVART-8", "--conclusion", "success", "--run-url", "https://gh/run/1")
    assert j.statuses["KVART-8"] == "Ready for LIVE"
    assert j.comments == []
    run(j, "checks", "--keys", "KVART-8", "--conclusion", "failure", "--run-url", "https://gh/run/2", "--sha", "abc")
    assert j.statuses["KVART-8"] == "In Progress"
    assert j.comments == [("KVART-8", "CI failed on abc: https://gh/run/2. Back to In Progress.")]


def test_checks_cancelled_touches_nothing():
    j = FakeJira({"KVART-8": "In Test"})
    run(j, "checks", "--keys", "KVART-8", "--conclusion", "cancelled", "--run-url", "u")
    assert j.statuses["KVART-8"] == "In Test"
    assert j.comments == []


def test_merged_records_sha_and_walks_a_raced_ticket_forward():
    j = FakeJira({"KVART-8": "Ready for LIVE", "KVART-5": "In Test"})
    run(j, "merged", "--keys", "KVART-8,KVART-5", "--pr-url", "https://gh/pr/36", "--sha", "1ba9542f")
    assert j.statuses == {"KVART-8": "Ready for LIVE", "KVART-5": "Ready for LIVE"}
    assert [c[0] for c in j.comments] == ["KVART-8", "KVART-5"]
    assert "1ba9542f" in j.comments[0][1]
    run(j, "merged", "--keys", "KVART-8,KVART-5", "--pr-url", "https://gh/pr/36", "--sha", "1ba9542f")  # replay
    assert len(j.comments) == 2


def test_move_replans_once_when_a_transition_is_refused():
    class RacyJira(FakeJira):
        refused = 0

        def request(self, method, path, body=None):
            if path.endswith("/transitions") and method == "POST" and self.refused == 0:
                self.refused += 1
                self.statuses["KVART-8"] = "In Test"  # another job moved it meanwhile
                raise SystemExit("jira_sync: POST -> HTTP 400: transition not valid")
            return super().request(method, path, body)

    j = RacyJira({"KVART-8": "In Progress"})
    run(j, "checks", "--keys", "KVART-8", "--conclusion", "success", "--run-url", "u")
    assert j.statuses["KVART-8"] == "Ready for LIVE"
    assert j.refused == 1


def test_epics_are_linked_but_never_moved_or_commented():
    j = FakeJira({"KVART-4": "In Progress", "KVART-5": "In Progress"}, epics={"KVART-4"})
    run(j, "pr-opened", "--keys=KVART-4,KVART-5", "--pr-url=https://gh/pr/37", "--pr-title=t (KVART-5)")
    run(j, "checks", "--keys=KVART-4,KVART-5", "--conclusion=success", "--run-url=u")
    run(j, "merged", "--keys=KVART-4,KVART-5", "--pr-url=https://gh/pr/37", "--sha=9c21c1af")
    run(j, "deployed", "--keys=KVART-4,KVART-5", "--sha=9c21c1af")
    assert j.statuses == {"KVART-4": "In Progress", "KVART-5": "Done"}
    assert [k for k, *_ in j.links] == ["KVART-4", "KVART-5"]
    assert [k for k, _ in j.comments] == ["KVART-5", "KVART-5"]


def test_is_epic_is_read_once_per_key():
    j = js.Jira("https://x.atlassian.net", "e", "t")
    reads = []
    j.request = lambda method, path, body=None: (reads.append(path), {"fields": {"issuetype": {"hierarchyLevel": 1}}})[1]
    assert j.is_epic("KVART-4") is True
    assert j.is_epic("KVART-4") is True
    assert len(reads) == 1


def test_pickup_still_walks_an_epic_a_person_chose():
    j = FakeJira({"KVART-4": "Backlog"}, epics={"KVART-4"})
    assert run(j, "pickup", "--key", "KVART-4") == 0
    assert j.statuses["KVART-4"] == "In Progress"


def test_green_after_red_walks_two_steps():
    j = FakeJira({"KVART-8": "In Progress"})
    run(j, "checks", "--keys", "KVART-8", "--conclusion", "success", "--run-url", "u")
    assert j.statuses["KVART-8"] == "Ready for LIVE"


def test_hyphen_leading_values_parse_with_equals_form():
    j = FakeJira({"KVART-8": "In Progress"})
    run(j, "pr-opened", "--keys=KVART-8", "--pr-url=https://gh/pr/36", "--pr-title=- odd title (KVART-8)")
    assert j.statuses["KVART-8"] == "In Test"
    assert j.links[0][2] == "- odd title (KVART-8)"


def test_deployed_closes_everything_shipped_from_any_column_but_not_done():
    # A ticket already Done stays put with no duplicate comment; every other
    # shipped ticket is driven to Done from wherever it sits — including
    # KVART-11 (Ready), which nobody explicitly picked up. Shipped code closes
    # the ticket; pickup state is irrelevant.
    j = FakeJira({"KVART-8": "Ready for LIVE", "KVART-3": "Done", "KVART-9": "In Test", "KVART-11": "Ready"})
    run(j, "deployed", "--keys", "KVART-8 KVART-3 KVART-9 KVART-11", "--sha", "deadbeef")
    assert j.statuses == {"KVART-8": "Done", "KVART-3": "Done", "KVART-9": "Done", "KVART-11": "Done"}
    assert j.comments == [
        ("KVART-8", "Deployed to production at deadbeef."),
        ("KVART-9", "Deployed to production at deadbeef."),
        ("KVART-11", "Deployed to production at deadbeef."),
    ]


def test_merged_drives_a_backlog_ticket_to_ready_for_live():
    # The bug KVART-40 fixes: a ticket nobody `jira pickup`'d merged and stayed
    # in Backlog. The merge now walks it all the way to Ready for LIVE.
    j = FakeJira({"KVART-40": "Backlog"})
    run(j, "merged", "--keys", "KVART-40", "--pr-url", "https://gh/pr/99", "--sha", "cafef00d")
    assert j.statuses["KVART-40"] == "Ready for LIVE"
    assert j.comments[0][0] == "KVART-40"
    assert "cafef00d" in j.comments[0][1]


def test_pr_opened_walks_a_backlog_ticket_up_to_in_test():
    j = FakeJira({"KVART-40": "Backlog"})
    run(j, "pr-opened", "--keys", "KVART-40", "--pr-url", "https://gh/pr/99", "--pr-title", "chore (KVART-40)")
    assert j.statuses["KVART-40"] == "In Test"
    assert j.links[0][0] == "KVART-40"


def test_keys_argument_rejects_text_without_keys():
    parser = js.build_parser("KVART")
    argv = ["merged", "--keys", "no-ticket-here", "--pr-url", "u", "--sha", "s"]
    with pytest.raises(SystemExit):
        parser.parse_args(argv)


def test_keys_command_is_offline():
    args = js.build_parser("KVART").parse_args(["keys", "--text", "feat/KVART-12-x (KVART-12) KVART-4"])
    assert args.offline is True
    assert js.extract_keys(args.text, args.project) == ["KVART-12", "KVART-4"]


def test_keys_command_reads_stdin_for_dash(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("feat: x (KVART-7)\n\nRefs KVART-4\n"))
    assert run(None, "keys", "--text", "-") == 0
    assert capsys.readouterr().out.split() == ["KVART-7", "KVART-4"]


@pytest.mark.parametrize("base", ["http://example.atlassian.net", "https://jira.invalid", "https://example.atlassian.net.evil.example"])
def test_request_refuses_wrong_scheme_or_host(base):
    j = js.Jira(base, "e", "t")
    with pytest.raises(SystemExit) as e:
        j.request("GET", "/rest/api/3/myself")
    assert ".atlassian.net" in str(e.value)


def test_from_env_names_what_is_missing(monkeypatch):
    for k in ("JIRA_BASE_URL", "JIRA_USER_EMAIL", "JIRA_API_TOKEN"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("JIRA_BASE_URL", "https://x.invalid")
    with pytest.raises(SystemExit) as e:
        js.Jira.from_env()
    assert "JIRA_USER_EMAIL, JIRA_API_TOKEN" in str(e.value)
