#!/usr/bin/env python3
"""PostToolUse hook: after a git commit, remind the agent to journal when no entry covers it.

Reads the hook event JSON on stdin. Prints a JSON reminder, or nothing. Silent when:
the command is not a commit, the event comes from a subagent, the project has no docs/journal/, the commit is a merge,
the commit itself touches docs/journal/, or an entry was written in the last 20 minutes.
Never fails the tool call: any error exits quietly.
"""
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RECENT_SECONDS = 20 * 60


def git(cwd, *args):
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def nudge(event):
    if event.get("agent_id"):
        return None  # subagents never write the journal; the orchestrator does
    if not re.search(r"\bgit\b[^|;&]*\bcommit\b", event.get("tool_input", {}).get("command", "")):
        return None
    top = git(event.get("cwd") or ".", "rev-parse", "--show-toplevel")
    journal = Path(top) / "docs" / "journal" if top else None
    if not journal or not journal.is_dir():
        return None
    if len(git(top, "rev-list", "--parents", "-n", "1", "HEAD").split()) > 2:
        return None
    if any(f.startswith("docs/journal/") for f in git(top, "show", "--name-only", "--format=", "HEAD").splitlines()):
        return None
    mtimes = [f.stat().st_mtime for f in journal.glob("*.md") if f.name not in ("index.md", "log.md")]
    if mtimes and time.time() - max(mtimes) < RECENT_SECONDS:
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"Commit {git(top, 'log', '-1', '--format=%h %s')} has no journal entry. "
                "If it carried a decision, a finding, a change of direction or a rejected approach, "
                "record it now with the hack-kit:project-log skill. If not, ignore this."
            ),
            "classifierContext": "Routine reminder to write a docs note. It asks for no other action.",
        }
    }


def self_test():
    def run(cwd, *a):
        return subprocess.run(a, cwd=cwd, capture_output=True, text=True)

    def commit(cwd, name):
        (Path(cwd) / name).write_text("x\n")
        run(cwd, "git", "add", name)
        run(cwd, "git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", f"add {name}")

    event = lambda cwd, cmd="git commit -m x": {"tool_input": {"command": cmd}, "cwd": str(cwd)}
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        run(r, "git", "init", "-q")
        commit(r, "a.txt")
        assert nudge(event(r)) is None, "no journal folder, must stay silent"
        (r / "docs" / "journal").mkdir(parents=True)
        (r / "docs" / "journal" / "index.md").write_text("x\n")
        commit(r, "b.txt")
        out = nudge(event(r))
        assert out and "hack-kit:project-log" in out["hookSpecificOutput"]["additionalContext"], out
        assert nudge(event(r, "git status")) is None, "not a commit"
        assert nudge(event(r, f"git -C {r} commit -m x")), "git -C commit must count"
        sub = event(r)
        sub["agent_id"] = "abc"
        assert nudge(sub) is None, "subagent events must stay silent"
        entry = r / "docs" / "journal" / "2026_10_24_100000_use_postgres.md"
        entry.write_text("x\n")
        run(r, "git", "add", "-A")
        run(r, "git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "log it")
        assert nudge(event(r)) is None, "commit touching the journal must stay silent"
        commit(r, "c.txt")
        assert nudge(event(r)) is None, "a recent entry must silence the reminder"
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    try:
        result = nudge(json.load(sys.stdin))
        if result:
            print(json.dumps(result))
    except Exception:
        pass
