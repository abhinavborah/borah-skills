#!/usr/bin/env python3
"""Check that a repository is ready for parallel subagents in worktrees.

Usage: preflight.py [--root DIR] [--fix] [--home DIR]
       preflight.py --self-test

Checks:
  repo      a git repository with at least one commit
  clean     no uncommitted changes, so the plan and briefs are committed
  baseRef   worktree.baseRef is "head". By default a subagent worktree branches from the
            default branch on the remote, and would miss every unpushed commit.
--fix writes worktree.baseRef = "head" into <root>/.claude/settings.json (tool config, so ask first).
Exit 1 when any check fails.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def git(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def base_ref(root, home):
    """Effective worktree.baseRef: local settings, then project, then user."""
    for p in (root / ".claude" / "settings.local.json", root / ".claude" / "settings.json", home / ".claude" / "settings.json"):
        if p.exists():
            try:
                v = json.loads(p.read_text()).get("worktree", {}).get("baseRef")
            except (ValueError, AttributeError):
                v = None
            if v:
                return v
    return None


def check(root, home):
    out = []
    if git(root, "rev-parse", "--verify", "-q", "HEAD")[0]:
        return ["repo: not a git repository with a commit"]
    dirty = git(root, "status", "--porcelain", "--", ".", ":(exclude).claude")[1]
    if dirty:
        out.append("clean: uncommitted changes; commit the plan and briefs first so worktrees contain them:\n  " + dirty.replace("\n", "\n  "))
    has_remote = bool(git(root, "remote")[1])
    if base_ref(root, home) != "head" and has_remote:
        out.append('baseRef: worktree.baseRef is not "head"; subagent worktrees would branch from the remote default branch and miss unpushed work. Run with --fix.')
    return out


def fix(root):
    sp = root / ".claude" / "settings.json"
    sp.parent.mkdir(exist_ok=True)
    cfg = json.loads(sp.read_text()) if sp.exists() else {}
    cfg.setdefault("worktree", {})["baseRef"] = "head"
    sp.write_text(json.dumps(cfg, indent=2) + "\n")


def self_test():
    def run(*a, cwd):
        return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True)

    with tempfile.TemporaryDirectory() as t:
        r, home = Path(t) / "r", Path(t) / "home"
        r.mkdir()
        home.mkdir()
        run("git", "init", "-q", cwd=r)
        assert check(r, home)[0].startswith("repo"), "no commit must fail"
        run("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "i", cwd=r)
        assert check(r, home) == [], "no remote: local HEAD is used, so nothing to fix"
        run("git", "remote", "add", "origin", "https://example.invalid/x.git", cwd=r)
        assert "baseRef" in "".join(check(r, home)), check(r, home)
        fix(r)
        assert check(r, home) == [], check(r, home)
        (r / "plan.md").write_text("x\n")
        assert "clean" in "".join(check(r, home)), check(r, home)
        (home / ".claude").mkdir()
        (home / ".claude" / "settings.json").write_text('{"worktree":{"baseRef":"head"}}')
        (r / ".claude" / "settings.json").unlink()
        run("git", "add", "plan.md", cwd=r)
        run("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "p", cwd=r)
        assert check(r, home) == [], "user-level setting counts"
    print("self-test ok")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", default=".")
    p.add_argument("--home", default=str(Path.home()))
    p.add_argument("--fix", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
        sys.exit(0)
    root = Path(a.root).resolve()
    if a.fix:
        fix(root)
    res = check(root, Path(a.home))
    print("\n".join(res) or "orchestrate preflight ok")
    sys.exit(1 if res else 0)
