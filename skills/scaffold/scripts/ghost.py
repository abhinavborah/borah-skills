#!/usr/bin/env python3
"""Ghost mode: keep agent traces out of a project's tracked history.

Usage: ghost.py apply --root DIR --levels all|a,b,c
       ghost.py check [--root DIR]
       ghost.py check-msg FILE        (used by the commit-msg hook)
       ghost.py --self-test

Levels (independent):
  attribution   blank commit and PR attribution in .claude/settings.json
  untracked     CLAUDE.md and AGENTS.md excluded through .git/info/exclude
  neutral-code  tracked files outside docs/ and commit messages carry no agent markers
  neutral-docs  docs/ prose carries none either (handoff folders are exempt)
  checker       a commit-msg hook runs this script

.claude/ is always excluded through .git/info/exclude and never named in .gitignore.
--levels none excludes only .claude/. The script, hook config and chosen levels live in
<git-common-dir>/ghost/, shared by every linked worktree and never tracked. Applies per clone.
"""
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

LEVELS = ["attribution", "untracked", "neutral-code", "neutral-docs", "checker"]
AGENT_DIRS = ["docs/handoffs", "docs/subagent-handoffs"]
MARKERS = [
    r"co-authored-by:.*(claude|anthropic|copilot|chatgpt|gpt|gemini|codex|cursor)",
    r"generated (with|by) .{0,30}(claude|\bai\b|chatgpt|gpt|copilot|gemini|codex|cursor)",
    r"\bclaude code\b",
    "\U0001F916",
    r"written (with|by) (the help of )?(an? )?(ai|claude|chatgpt)",
    r"as an ai (language )?model",
    r"\bai[- ]generated\b",
]
MARK = re.compile("|".join(f"(?:{m})" for m in MARKERS), re.I)
HOOK = '#!/bin/sh\nexec python3 "$(git rev-parse --path-format=absolute --git-common-dir)/ghost/ghost.py" check-msg "$1"\n'


def git(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.returncode, r.stdout


def cfgdir(root):
    """Config lives in the git common dir so every linked worktree shares it."""
    return Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")[1].strip()) / "ghost"


def load(root):
    p = cfgdir(root) / "ghost.json"
    cfg = json.loads(p.read_text()) if p.exists() else {}
    return cfg.get("levels", LEVELS), cfg.get("agent_dirs", AGENT_DIRS), cfg.get("extra_markers", [])


def apply(root, levels):
    root = Path(root).resolve()
    if git(root, "rev-parse", "--git-dir")[0]:
        sys.exit(f"{root} is not a git repository")
    levels = {"all": LEVELS, "none": []}.get(",".join(levels), levels)
    bad = [l for l in levels if l not in LEVELS]
    if bad:
        sys.exit(f"unknown levels: {bad}")
    cd = cfgdir(root)
    cd.mkdir(parents=True, exist_ok=True)
    (cd / "ghost.json").write_text(json.dumps({"levels": levels, "agent_dirs": AGENT_DIRS}, indent=2) + "\n")
    lines = [".claude/"] + (["CLAUDE.md", "AGENTS.md"] if "untracked" in levels else [])
    exclude = Path(git(root, "rev-parse", "--path-format=absolute", "--git-path", "info/exclude")[1].strip())
    exclude.parent.mkdir(parents=True, exist_ok=True)
    have = exclude.read_text().splitlines() if exclude.exists() else []
    exclude.write_text("\n".join(have + [l for l in lines if l not in have]) + "\n")
    if "attribution" in levels:
        sp = root / ".claude" / "settings.json"
        sp.parent.mkdir(exist_ok=True)
        cfg = json.loads(sp.read_text()) if sp.exists() else {}
        cfg["attribution"] = {"commit": "", "pr": "", "sessionUrl": False}
        sp.write_text(json.dumps(cfg, indent=2) + "\n")
    if "checker" in levels:
        me = Path(__file__).resolve()
        dest = cd / "ghost.py"
        if me != dest.resolve():
            shutil.copy(me, dest)
        hook = Path(git(root, "rev-parse", "--path-format=absolute", "--git-path", "hooks/commit-msg")[1].strip())
        if hook.exists() and "ghost.py" not in hook.read_text():
            print(f"kept existing {hook}; add a call to .claude/ghost.py check-msg manually")
        else:
            hook.parent.mkdir(parents=True, exist_ok=True)
            hook.write_text(HOOK)
            hook.chmod(hook.stat().st_mode | stat.S_IXUSR)
    tracked = [f for f in git(root, "ls-files", ".claude", "CLAUDE.md", "AGENTS.md")[1].splitlines() if f]
    print(f"ghost levels: {','.join(levels) or 'none'}")
    if tracked:
        print(f"already tracked, run git rm --cached on: {' '.join(tracked)}")


def scan_text(label, text, pattern, out):
    for n, line in enumerate(text.splitlines(), 1):
        if pattern.search(line):
            out.append(f"{label}:{n}: agent marker: {line.strip()[:80]}")


def check(root):
    root = Path(root).resolve()
    levels, agent_dirs, extra = load(root)
    pat = re.compile(MARK.pattern + "".join(f"|(?:{m})" for m in extra), re.I)
    out = []
    files = [f for f in git(root, "ls-files")[1].splitlines() if f]
    for f in files:
        if f.startswith(".claude/"):
            out.append(f"{f}: tracked, must be untracked")
    if "untracked" in levels:
        for f in files:
            if Path(f).name in ("CLAUDE.md", "AGENTS.md"):
                out.append(f"{f}: tracked, must be untracked")
    gi = root / ".gitignore"
    if gi.exists():
        for n, line in enumerate(gi.read_text().splitlines(), 1):
            if re.search(r"\.claude|CLAUDE\.md|AGENTS\.md", line):
                out.append(f".gitignore:{n}: names an agent path; use .git/info/exclude")
    if "attribution" in levels:
        # a linked worktree has no .claude/, so fall back to the main checkout's
        sps = [root / ".claude" / "settings.json", cfgdir(root).parent.parent / ".claude" / "settings.json"]
        sp = next((s for s in sps if s.exists()), sps[0])
        a = json.loads(sp.read_text()).get("attribution", {}) if sp.exists() else {}
        if a.get("commit") != "" or a.get("pr") != "" or a.get("sessionUrl") is not False:
            out.append(".claude/settings.json: attribution is not blank")
    if "checker" in levels:
        rc, p = git(root, "rev-parse", "--path-format=absolute", "--git-path", "hooks/commit-msg")
        hook = Path(p.strip())
        if not hook.exists() or "ghost.py" not in hook.read_text():
            out.append("commit-msg hook missing")
    for f in files:
        if Path(f).name in ("CLAUDE.md", "AGENTS.md") or f.startswith(".claude/"):
            continue
        in_docs = f.startswith("docs/")
        exempt = any(f.startswith(d + "/") for d in agent_dirs)
        if (in_docs and ("neutral-docs" not in levels or exempt)) or (not in_docs and "neutral-code" not in levels):
            continue
        try:
            scan_text(f, (root / f).read_text(), pat, out)
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            pass
    if "neutral-code" in levels or "attribution" in levels:
        rc, log = git(root, "log", "--format=%h%x01%B%x02")
        for entry in log.split("\x02"):
            sha, _, body = entry.strip().partition("\x01")
            if sha:
                scan_text(f"commit {sha}", body, pat, out)
    return out


def check_msg(path):
    levels, _, extra = load(Path.cwd())
    if "neutral-code" not in levels and "attribution" not in levels:
        return []
    pat = re.compile(MARK.pattern + "".join(f"|(?:{m})" for m in extra), re.I)
    text = "\n".join(l for l in Path(path).read_text().splitlines() if not l.startswith("#"))
    out = []
    scan_text("commit message", text, pat, out)
    return out


def self_test():
    me = Path(__file__).resolve()
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    def run(*a, cwd):
        return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, env=env)

    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        run("git", "init", "-q", cwd=r)
        (r / "app.py").write_text("print('hi')\n")
        (r / "CLAUDE.md").write_text("rules\n")
        run("git", "add", "app.py", cwd=r)
        run("python3", str(me), "apply", "--root", str(r), "--levels", "all", cwd=r)
        for p in (".git/ghost/ghost.json", ".claude/settings.json", ".git/ghost/ghost.py", ".git/hooks/commit-msg"):
            assert (r / p).exists(), p
        ex = (r / ".git/info/exclude").read_text()
        assert ".claude/" in ex and "CLAUDE.md" in ex
        assert not (r / ".gitignore").exists()
        assert run("git", "commit", "-q", "-m", "add app", cwd=r).returncode == 0
        assert check(r) == [], check(r)
        bad = run("git", "commit", "-q", "--allow-empty", "-m", "x\n\nCo-Authored-By: Claude <noreply@anthropic.com>", cwd=r)
        assert bad.returncode != 0, "hook should block a marked message"
        (r / "notes.md").write_text("Generated with Claude Code\n")
        (r / ".gitignore").write_text(".claude/\n")
        run("git", "add", "notes.md", ".gitignore", cwd=r)
        run("git", "commit", "-q", "--no-verify", "-m", "more", cwd=r)
        out = "\n".join(check(r))
        assert "agent marker" in out and ".gitignore:1" in out, out

    # linked worktrees (where orchestrate dispatches writers) share hook and config
    with tempfile.TemporaryDirectory() as t:
        r, wt = Path(t) / "main", Path(t) / "wt"
        r.mkdir()
        run("git", "init", "-q", "-b", "main", cwd=r)
        (r / "app.py").write_text("print('hi')\n")
        run("git", "add", "app.py", cwd=r)
        run("python3", str(me), "apply", "--root", str(r), "--levels", "all", cwd=r)
        assert run("git", "commit", "-q", "-m", "add app", cwd=r).returncode == 0
        run("git", "worktree", "add", "-q", "-b", "side", str(wt), cwd=r)
        assert run("git", "commit", "-q", "--allow-empty", "-m", "fine", cwd=wt).returncode == 0
        bad = run("git", "commit", "-q", "--allow-empty", "-m", "x\n\nGenerated with Claude Code", cwd=wt)
        assert bad.returncode != 0, "hook must also block inside a worktree"
        assert check(wt) == [], check(wt)

    # ghost off: only .claude/ is excluded and nothing is checked
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        run("git", "init", "-q", cwd=r)
        run("python3", str(me), "apply", "--root", str(r), "--levels", "none", cwd=r)
        lines = [l for l in (r / ".git/info/exclude").read_text().splitlines() if l and not l.startswith("#")]
        assert lines == [".claude/"], lines
        (r / "n.md").write_text("Generated with Claude Code\n")
        run("git", "add", "n.md", cwd=r)
        run("git", "commit", "-q", "-m", "n", cwd=r)
        assert check(r) == [], check(r)
    print("self-test ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-test" in a:
        self_test()
    elif a[:1] == ["apply"]:
        opt = dict(zip(a[1::2], a[2::2]))
        apply(opt.get("--root", "."), opt.get("--levels", "all").split(","))
    elif a[:1] == ["check"]:
        opt = dict(zip(a[1::2], a[2::2]))
        res = check(opt.get("--root", "."))
        print("\n".join(res) or "ghost check ok")
        sys.exit(1 if res else 0)
    elif a[:1] == ["check-msg"] and len(a) == 2:
        res = check_msg(a[1])
        if res:
            res.append("commit blocked: remove the agent marker lines from the message and commit again")
        print("\n".join(res), file=sys.stderr)
        sys.exit(1 if res else 0)
    else:
        sys.exit(__doc__)
