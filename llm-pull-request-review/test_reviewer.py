"""Offline tests: no model and no GitHub needed. Run make_repo.py first."""
import json
import threading
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

import reviewer
from reviewer import (HunkReview, filter_comments, local_diff, parse_hunks,
                      post_review, review_payload)

REPO = "orderdesk-lite"


def test_hunk_maps_added_lines_to_new_line_numbers():
    [hunk] = parse_hunks(local_diff(REPO, "main", "pr-2-orders-by-status"))

    assert hunk.path == "orderdesk/repository.py"
    assert hunk.added_lines == {18, 19, 20, 21}
    assert "  20 +         query = f\"SELECT" in hunk.text


def test_removed_lines_have_no_new_line_number():
    [hunk] = parse_hunks(local_diff(REPO, "main", "pr-8-refactor-client"))

    assert hunk.added_lines == {4, 8, 12}
    assert "     -         timeout=10," in hunk.text


def test_lock_files_are_skipped():
    diff = ("diff --git a/uv.lock b/uv.lock\n--- a/uv.lock\n+++ b/uv.lock\n"
            "@@ -1 +1 @@\n-a\n+b\n")
    assert parse_hunks(diff) == []


def test_filter_drops_wrong_lines_low_confidence_and_duplicates():
    [hunk] = parse_hunks(local_diff(REPO, "main", "pr-2-orders-by-status"))
    review = HunkReview.model_validate({"comments": [
        {"line": 20, "severity": "high", "category": "sql-injection", "confidence": 0.9, "body": "a"},
        {"line": 20, "severity": "high", "category": "sql-injection", "confidence": 0.8, "body": "b"},
        {"line": 15, "severity": "low", "category": "other", "confidence": 0.9, "body": "c"},
        {"line": 21, "severity": "low", "category": "other", "confidence": 0.4, "body": "d"},
        {"line": 21, "severity": "high", "category": "sql-injection", "confidence": 0.9, "body": "a"},
    ]})
    dropped = Counter()

    kept = filter_comments(hunk, review, 0.7, dropped)

    assert [(f.line, f.body) for f in kept] == [(20, "a")]
    assert dropped == {"duplicate": 2, "line is not an added line": 1, "below threshold": 1}


def test_review_is_posted_as_one_comment_review(monkeypatch):
    received = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            received["path"] = self.path
            received["auth"] = self.headers["Authorization"]
            received["json"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"id": 42}')

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.handle_request, daemon=True).start()
    monkeypatch.setattr(reviewer, "GITHUB_API", f"http://127.0.0.1:{server.server_port}")
    finding = reviewer.Finding("orderdesk/repository.py", 20, "high", "sql-injection", 0.9,
                               "Use a ? placeholder.")

    review_id = post_review("acme/orderdesk-lite", 7, review_payload("abc123", [finding]), "t0ken")

    assert review_id == 42
    assert received["path"] == "/repos/acme/orderdesk-lite/pulls/7/reviews"
    assert received["auth"] == "Bearer t0ken"
    assert received["json"]["event"] == "COMMENT"
    assert received["json"]["commit_id"] == "abc123"
    assert received["json"]["comments"] == [{
        "path": "orderdesk/repository.py", "line": 20, "side": "RIGHT",
        "body": "**high** (sql-injection): Use a ? placeholder."}]


def test_failed_hunks_are_reported_in_the_review_body():
    payload = review_payload("abc123", [], failed_hunks=1)

    assert payload["comments"] == []
    assert "1 hunk(s) could NOT be reviewed" in payload["body"]


def test_confidence_outside_zero_to_one_is_rejected():
    with pytest.raises(ValueError):
        HunkReview.model_validate({"comments": [
            {"line": 1, "severity": "low", "category": "other", "confidence": 7, "body": "x"}]})


def test_review_and_post_commands_end_to_end(tmp_path):
    """Runs both CLI commands with stub servers in place of Ollama and GitHub."""
    import os
    import subprocess
    import sys

    answer = {"comments": [{"line": 20, "severity": "high", "category": "sql-injection",
                            "confidence": 0.95, "body": "Use a ? placeholder."}]}
    posted = []

    class Stub(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if self.path == "/api/chat":
                reply = {"model": body["model"], "created_at": "2026-10-31T00:00:00Z",
                         "message": {"role": "assistant", "content": json.dumps(answer)},
                         "done": True}
            else:
                posted.append((self.path, body))
                reply = {"id": 7}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(reply).encode())

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Stub)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}"

    def sha(ref):
        return subprocess.run(["git", "-C", REPO, "rev-parse", ref], capture_output=True,
                              text=True, check=True).stdout.strip()

    event = tmp_path / "event.json"
    event.write_text(json.dumps({"pull_request": {
        "number": 7, "base": {"sha": sha("main")}, "head": {"sha": sha("pr-2-orders-by-status")}}}))
    out = tmp_path / "review.json"
    env = os.environ | {"OLLAMA_HOST": url, "GITHUB_API_URL": url, "NO_PROXY": "127.0.0.1",
                        "GITHUB_REPOSITORY": "acme/orderdesk-lite", "GITHUB_TOKEN": "t0ken"}

    subprocess.run([sys.executable, "reviewer.py", "review", "--repo", REPO, "--event", str(event),
                    "--out", str(out)], env=env, check=True)
    result = subprocess.run([sys.executable, "reviewer.py", "post", "--review", str(out)],
                            env=env, check=True, capture_output=True, text=True)
    server.shutdown()

    assert result.stdout.strip() == "posted review 7 with 1 comment(s)"
    [(path, payload)] = posted
    assert path == "/repos/acme/orderdesk-lite/pulls/7/reviews"
    assert payload["commit_id"] == sha("pr-2-orders-by-status")
    assert payload["comments"][0]["line"] == 20
