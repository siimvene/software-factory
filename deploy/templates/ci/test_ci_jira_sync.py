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
        ("feat/REFAPP-8-item-list-no-owner-names", ["REFAPP-8"]),
        ("fix(meters): ... (REFAPP-3)", ["REFAPP-3"]),
        ("REFAPP-10 then REFAPP-1 then REFAPP-10 again", ["REFAPP-10", "REFAPP-1"]),
        ("REFAPP-1 REFAPP-10 REFAPP-100", ["REFAPP-1", "REFAPP-10", "REFAPP-100"]),
        ("ci: runner wake, no ticket", []),
        ("", []),
        ("lowercase refapp-4 does not count", []),
        ("XREFAPP-4 is another project's suffix", []),
        ("feat(audit): access trail (REFAPP-5/6/7)", ["REFAPP-5", "REFAPP-6", "REFAPP-7"]),  # title shorthand
        ("(REFAPP-1/10) and (REFAPP-10/1)", ["REFAPP-1", "REFAPP-10"]),
        ("feat/REFAPP-8-item-list/4", ["REFAPP-8"]),  # a slash after a word, not after the number
        ("feat/REFAPP-8/4-hotfix", ["REFAPP-8"]),  # bare shorthand outside parentheses never expands
        ("fix: REFAPP-8/2026 allocation", ["REFAPP-8"]),
        ("(REFAPP-8/2026 allocation)", ["REFAPP-8"]),  # not closed right after the numbers
    ],
)
def test_extract_keys(text, expected):
    assert js.extract_keys(text) == expected


@pytest.mark.parametrize(
    "subjects,expected",
    [
        ("feat: a (REFAPP-1)\nfix: b (REFAPP-2)", ["REFAPP-1", "REFAPP-2"]),
        ('feat: a (REFAPP-1)\nRevert "feat: a (REFAPP-1)"', []),  # merged and reverted in one range
        ('Revert "feat: old (REFAPP-3)"\nfeat: new (REFAPP-4)', ["REFAPP-4"]),
        ("Merge pull request #36 from siimvene/feat/REFAPP-8-item-list", ["REFAPP-8"]),
        ("", []),
    ],
)
def test_deployed_keys_subtracts_reverts(subjects, expected):
    assert js.deployed_keys(subjects) == expected


def test_extract_keys_is_capped():
    hostile = "(REFAPP-" + "/".join(str(n) for n in range(1, 501)) + ")"
    assert len(js.extract_keys(hostile)) == js.MAX_KEYS
    assert js.extract_keys(" ".join(f"REFAPP-{n}" for n in range(1, 40)))[-1] == f"REFAPP-{js.MAX_KEYS}"


def test_extract_keys_other_project():
    assert js.extract_keys("EST-9 and REFAPP-2", project="EST") == ["EST-9"]


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
    args = js.build_parser("REFAPP").parse_args(list(argv))
    return args.fn(jira, args)


def test_pickup_from_backlog_assigns_and_walks_to_in_progress():
    j = FakeJira({"REFAPP-9": "Backlog"})
    assert run(j, "pickup", "--key", "REFAPP-9") == 0
    assert j.assigned == {"REFAPP-9": "acc-1"}
    assert j.statuses["REFAPP-9"] == "In Progress"


def test_pickup_past_in_progress_only_assigns():
    j = FakeJira({"REFAPP-8": "Ready for LIVE"})
    assert run(j, "pickup", "--key", "REFAPP-8") == 0
    assert j.assigned == {"REFAPP-8": "acc-1"}
    assert j.statuses["REFAPP-8"] == "Ready for LIVE"


def test_pr_opened_links_and_moves_to_in_test():
    j = FakeJira({"REFAPP-5": "In Progress", "REFAPP-6": "In Progress"})
    run(j, "pr-opened", "--keys", "REFAPP-5,REFAPP-6", "--pr-url", "https://gh/pr/40", "--pr-title", "feat (REFAPP-5)")
    assert j.statuses == {"REFAPP-5": "In Test", "REFAPP-6": "In Test"}
    assert j.links == [("REFAPP-5", "https://gh/pr/40", "feat (REFAPP-5)"), ("REFAPP-6", "https://gh/pr/40", "feat (REFAPP-5)")]


def test_pr_opened_replay_is_a_noop_but_keeps_the_link():
    j = FakeJira({"REFAPP-8": "Ready for LIVE"})
    run(j, "pr-opened", "--keys", "REFAPP-8", "--pr-url", "https://gh/pr/36", "--pr-title", "t")
    assert j.statuses["REFAPP-8"] == "Ready for LIVE"
    assert len(j.links) == 1


def test_checks_success_then_failure_round_trip():
    j = FakeJira({"REFAPP-8": "In Test"})
    run(j, "checks", "--keys", "REFAPP-8", "--conclusion", "success", "--run-url", "https://gh/run/1")
    assert j.statuses["REFAPP-8"] == "Ready for LIVE"
    assert j.comments == []
    run(j, "checks", "--keys", "REFAPP-8", "--conclusion", "failure", "--run-url", "https://gh/run/2", "--sha", "abc")
    assert j.statuses["REFAPP-8"] == "In Progress"
    assert j.comments == [("REFAPP-8", "CI failed on abc: https://gh/run/2. Back to In Progress.")]


def test_checks_cancelled_touches_nothing():
    j = FakeJira({"REFAPP-8": "In Test"})
    run(j, "checks", "--keys", "REFAPP-8", "--conclusion", "cancelled", "--run-url", "u")
    assert j.statuses["REFAPP-8"] == "In Test"
    assert j.comments == []


def test_merged_records_sha_and_walks_a_raced_ticket_forward():
    j = FakeJira({"REFAPP-8": "Ready for LIVE", "REFAPP-5": "In Test"})
    run(j, "merged", "--keys", "REFAPP-8,REFAPP-5", "--pr-url", "https://gh/pr/36", "--sha", "1ba9542f")
    assert j.statuses == {"REFAPP-8": "Ready for LIVE", "REFAPP-5": "Ready for LIVE"}
    assert [c[0] for c in j.comments] == ["REFAPP-8", "REFAPP-5"]
    assert "1ba9542f" in j.comments[0][1]
    run(j, "merged", "--keys", "REFAPP-8,REFAPP-5", "--pr-url", "https://gh/pr/36", "--sha", "1ba9542f")  # replay
    assert len(j.comments) == 2


def test_move_replans_once_when_a_transition_is_refused():
    class RacyJira(FakeJira):
        refused = 0

        def request(self, method, path, body=None):
            if path.endswith("/transitions") and method == "POST" and self.refused == 0:
                self.refused += 1
                self.statuses["REFAPP-8"] = "In Test"  # another job moved it meanwhile
                raise SystemExit("jira_sync: POST -> HTTP 400: transition not valid")
            return super().request(method, path, body)

    j = RacyJira({"REFAPP-8": "In Progress"})
    run(j, "checks", "--keys", "REFAPP-8", "--conclusion", "success", "--run-url", "u")
    assert j.statuses["REFAPP-8"] == "Ready for LIVE"
    assert j.refused == 1


def test_epics_are_linked_but_never_moved_or_commented():
    j = FakeJira({"REFAPP-4": "In Progress", "REFAPP-5": "In Progress"}, epics={"REFAPP-4"})
    run(j, "pr-opened", "--keys=REFAPP-4,REFAPP-5", "--pr-url=https://gh/pr/37", "--pr-title=t (REFAPP-5)")
    run(j, "checks", "--keys=REFAPP-4,REFAPP-5", "--conclusion=success", "--run-url=u")
    run(j, "merged", "--keys=REFAPP-4,REFAPP-5", "--pr-url=https://gh/pr/37", "--sha=9c21c1af")
    run(j, "deployed", "--keys=REFAPP-4,REFAPP-5", "--sha=9c21c1af")
    assert j.statuses == {"REFAPP-4": "In Progress", "REFAPP-5": "Done"}
    assert [k for k, *_ in j.links] == ["REFAPP-4", "REFAPP-5"]
    assert [k for k, _ in j.comments] == ["REFAPP-5", "REFAPP-5"]


def test_is_epic_is_read_once_per_key():
    j = js.Jira("https://x.atlassian.net", "e", "t")
    reads = []
    j.request = lambda method, path, body=None: (reads.append(path), {"fields": {"issuetype": {"hierarchyLevel": 1}}})[1]
    assert j.is_epic("REFAPP-4") is True
    assert j.is_epic("REFAPP-4") is True
    assert len(reads) == 1


def test_pickup_still_walks_an_epic_a_person_chose():
    j = FakeJira({"REFAPP-4": "Backlog"}, epics={"REFAPP-4"})
    assert run(j, "pickup", "--key", "REFAPP-4") == 0
    assert j.statuses["REFAPP-4"] == "In Progress"


def test_green_after_red_walks_two_steps():
    j = FakeJira({"REFAPP-8": "In Progress"})
    run(j, "checks", "--keys", "REFAPP-8", "--conclusion", "success", "--run-url", "u")
    assert j.statuses["REFAPP-8"] == "Ready for LIVE"


def test_hyphen_leading_values_parse_with_equals_form():
    j = FakeJira({"REFAPP-8": "In Progress"})
    run(j, "pr-opened", "--keys=REFAPP-8", "--pr-url=https://gh/pr/36", "--pr-title=- odd title (REFAPP-8)")
    assert j.statuses["REFAPP-8"] == "In Test"
    assert j.links[0][2] == "- odd title (REFAPP-8)"


def test_deployed_closes_everything_shipped_from_any_column_but_not_done():
    # A ticket already Done stays put with no duplicate comment; every other
    # shipped ticket is driven to Done from wherever it sits — including
    # REFAPP-11 (Ready), which nobody explicitly picked up. Shipped code closes
    # the ticket; pickup state is irrelevant.
    j = FakeJira({"REFAPP-8": "Ready for LIVE", "REFAPP-3": "Done", "REFAPP-9": "In Test", "REFAPP-11": "Ready"})
    run(j, "deployed", "--keys", "REFAPP-8 REFAPP-3 REFAPP-9 REFAPP-11", "--sha", "deadbeef")
    assert j.statuses == {"REFAPP-8": "Done", "REFAPP-3": "Done", "REFAPP-9": "Done", "REFAPP-11": "Done"}
    assert j.comments == [
        ("REFAPP-8", "Deployed to production at deadbeef."),
        ("REFAPP-9", "Deployed to production at deadbeef."),
        ("REFAPP-11", "Deployed to production at deadbeef."),
    ]


def test_merged_drives_a_backlog_ticket_to_ready_for_live():
    # The bug REFAPP-40 fixes: a ticket nobody `jira pickup`'d merged and stayed
    # in Backlog. The merge now walks it all the way to Ready for LIVE.
    j = FakeJira({"REFAPP-40": "Backlog"})
    run(j, "merged", "--keys", "REFAPP-40", "--pr-url", "https://gh/pr/99", "--sha", "cafef00d")
    assert j.statuses["REFAPP-40"] == "Ready for LIVE"
    assert j.comments[0][0] == "REFAPP-40"
    assert "cafef00d" in j.comments[0][1]


def test_pr_opened_walks_a_backlog_ticket_up_to_in_test():
    j = FakeJira({"REFAPP-40": "Backlog"})
    run(j, "pr-opened", "--keys", "REFAPP-40", "--pr-url", "https://gh/pr/99", "--pr-title", "chore (REFAPP-40)")
    assert j.statuses["REFAPP-40"] == "In Test"
    assert j.links[0][0] == "REFAPP-40"


def test_keys_argument_rejects_text_without_keys():
    parser = js.build_parser("REFAPP")
    argv = ["merged", "--keys", "no-ticket-here", "--pr-url", "u", "--sha", "s"]
    with pytest.raises(SystemExit):
        parser.parse_args(argv)


def test_keys_command_is_offline():
    args = js.build_parser("REFAPP").parse_args(["keys", "--text", "feat/REFAPP-12-x (REFAPP-12) REFAPP-4"])
    assert args.offline is True
    assert js.extract_keys(args.text, args.project) == ["REFAPP-12", "REFAPP-4"]


def test_keys_command_reads_stdin_for_dash(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("feat: x (REFAPP-7)\n\nRefs REFAPP-4\n"))
    assert run(None, "keys", "--text", "-") == 0
    assert capsys.readouterr().out.split() == ["REFAPP-7", "REFAPP-4"]


def test_main_treats_empty_project_key_as_default(monkeypatch, capsys):
    """An exported-but-empty JIRA_PROJECT_KEY (unset repository variable) must not
    yield the empty project, which makes `REFAPP-12` extract as `-12`."""
    monkeypatch.setenv("JIRA_PROJECT_KEY", "")
    assert js.main(["keys", "--text=feat/REFAPP-12-x"]) == 0
    assert capsys.readouterr().out.split() == ["REFAPP-12"]


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
