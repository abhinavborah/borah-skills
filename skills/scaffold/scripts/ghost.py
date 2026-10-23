#!/usr/bin/env python3
"""Ghost mode: keep agent traces out of a project's tracked history.

Usage: ghost.py apply --root DIR --levels all|none|a,b,c
       ghost.py check [--root DIR]
       ghost.py check-msg FILE        (used by the commit-msg hook)
       ghost.py --self-test

Levels (independent):
  attribution   blank commit and PR attribution in .claude/settings.json
  untracked     CLAUDE.md and AGENTS.md excluded through .git/info/exclude
  neutral-code  tracked files outside docs/ and commit messages carry no agent markers
  neutral-docs  docs/ prose carries none either (handoff folders are exempt)
  checker       a commit-msg hook blocks agent trailers (and wording, with neutral-code)

Markers come in two groups. Trailers (bot co-author lines, "generated with ..." lines) are
enforced by checker, attribution and neutral-code. Wording (tool names, robot emoji, "AI-generated")
is enforced only by neutral-code and neutral-docs.

.claude/ is always excluded through .git/info/exclude and never named in .gitignore.
--levels none excludes only .claude/. The script and ghost.json live in
<git-common-dir>/ghost/, shared by every linked worktree and never tracked. Applies per clone.

ghost.json keys: levels, agent_dirs, extra_markers (regex list), ignore_markers (regex list; a
matching line is skipped), ignore_paths (globs), baseline (commit; older history is not scanned).
"""
import fnmatch
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
TRAILERS = [
    r"co-authored-by:.*noreply@anthropic\.com",
    r"co-authored-by:\s*(claude|copilot|chatgpt|gemini|codex|cursor)\b[^<\n]*<[^>\n]*(noreply|bot|\.ai|anthropic|openai)[^>\n]*>",
    r"generated (with|by) \[?(claude|chatgpt|copilot|gemini|codex|cursor)",
]
WORDING = [
    r"generated (with|by) .{0,30}\bai\b",
    r"\bclaude code\b",
    "\U0001F916",
    r"written (with|by) (the help of )?(an? )?(ai|claude|chatgpt)",
    r"as an ai (language )?model",
    r"\bai[- ]generated\b",
]
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
    base = {"levels": LEVELS, "agent_dirs": AGENT_DIRS, "extra_markers": [], "ignore_markers": [], "ignore_paths": [], "baseline": None}
    return {**base, **cfg}


def pattern(parts, extra):
    return re.compile("|".join(f"(?:{m})" for m in [*parts, *extra]), re.I)


def hook_path(root):
    return Path(git(root, "rev-parse", "--path-format=absolute", "--git-path", "hooks/commit-msg")[1].strip())


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
    cfg = load(root)
    cfg["levels"] = levels
    if not cfg["baseline"]:
        rc, head = git(root, "rev-parse", "--verify", "-q", "HEAD")
        cfg["baseline"] = head.strip() if rc == 0 else None  # earlier history is not held against the project
    (cd / "ghost.json").write_text(json.dumps(cfg, indent=2) + "\n")
    lines = [".claude/"] + (["CLAUDE.md", "AGENTS.md"] if "untracked" in levels else [])
    exclude = Path(git(root, "rev-parse", "--path-format=absolute", "--git-path", "info/exclude")[1].strip())
    exclude.parent.mkdir(parents=True, exist_ok=True)
    have = exclude.read_text().splitlines() if exclude.exists() else []
    exclude.write_text("\n".join(have + [l for l in lines if l not in have]) + "\n")
    if "attribution" in levels:
        sp = root / ".claude" / "settings.json"
        sp.parent.mkdir(exist_ok=True)
        settings = json.loads(sp.read_text()) if sp.exists() else {}
        settings["attribution"] = {"commit": "", "pr": "", "sessionUrl": False}
        sp.write_text(json.dumps(settings, indent=2) + "\n")
    if "checker" in levels:
        me = Path(__file__).resolve()
        dest = cd / "ghost.py"
        if me != dest.resolve():
            shutil.copy(me, dest)
        hook = hook_path(root)
        hp = git(root, "config", "core.hooksPath")[1].strip()
        if hook.exists() and "ghost.py" not in hook.read_text():
            print(f"WARNING an existing commit-msg hook is in use: {hook}")
            print(f'  call the checker from it (or from your hook manager): python3 "{dest}" check-msg "$1"')
            print("  until then agent trailers are not blocked")
        else:
            hook.parent.mkdir(parents=True, exist_ok=True)
            hook.write_text(HOOK)
            hook.chmod(hook.stat().st_mode | stat.S_IXUSR)
            if hp:
                print(f"note: core.hooksPath is {hp}; the hook was installed there. Run apply again if you change it.")
    tracked = [f for f in git(root, "ls-files", ".claude", "CLAUDE.md", "AGENTS.md")[1].splitlines() if f]
    print(f"ghost levels: {','.join(levels) or 'none'}")
    if tracked:
        print(f"already tracked, run git rm --cached on: {' '.join(tracked)}")


def scan_text(label, text, pat, ignore, out):
    for n, line in enumerate(text.splitlines(), 1):
        if pat.search(line) and not any(re.search(i, line, re.I) for i in ignore):
            out.append(f"{label}:{n}: agent marker: {line.strip()[:80]}")


def check(root):
    root = Path(root).resolve()
    cfg = load(root)
    levels, agent_dirs, ignore = cfg["levels"], cfg["agent_dirs"], cfg["ignore_markers"]
    trailers, full = pattern(TRAILERS, cfg["extra_markers"]), pattern(TRAILERS + WORDING, cfg["extra_markers"])
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
        hook = hook_path(root)
        if not hook.exists() or "ghost.py" not in hook.read_text():
            hp = git(root, "config", "core.hooksPath")[1].strip()
            out.append(f"commit-msg hook missing or shadowed (core.hooksPath={hp or 'unset'}); run apply again")
    for f in files:
        if Path(f).name in ("CLAUDE.md", "AGENTS.md") or f.startswith(".claude/"):
            continue
        if any(fnmatch.fnmatch(f, g) for g in cfg["ignore_paths"]):
            continue
        in_docs = f.startswith("docs/")
        exempt = any(f.startswith(d + "/") for d in agent_dirs)
        if (in_docs and ("neutral-docs" not in levels or exempt)) or (not in_docs and "neutral-code" not in levels):
            continue
        try:
            scan_text(f, (root / f).read_text(), full, ignore, out)
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            pass
    if {"neutral-code", "attribution", "checker"} & set(levels):
        base = cfg["baseline"]
        span = [f"{base}..HEAD"] if base and git(root, "cat-file", "-e", f"{base}^{{commit}}")[0] == 0 else []
        rc, log = git(root, "log", "--format=%h%x01%B%x02", *span)
        for entry in log.split("\x02"):
            sha, _, body = entry.strip().partition("\x01")
            if sha:
                scan_text(f"commit {sha}", body, full if "neutral-code" in levels else trailers, ignore, out)
    return out


def check_msg(path):
    cfg = load(Path.cwd())
    levels = cfg["levels"]
    if not {"neutral-code", "attribution", "checker"} & set(levels):
        return []
    pat = pattern(TRAILERS + (WORDING if "neutral-code" in levels else []), cfg["extra_markers"])
    text = "\n".join(l for l in Path(path).read_text().splitlines() if not l.startswith("#"))
    out = []
    scan_text("commit message", text, pat, cfg["ignore_markers"], out)
    return out


def self_test():
    me = Path(__file__).resolve()
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    def run(*a, cwd):
        return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, env=env)

    def apply_to(r, levels):
        run("python3", str(me), "apply", "--root", str(r), "--levels", levels, cwd=r)

    BOT = "x\n\nCo-Authored-By: Claude <noreply@anthropic.com>"

    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        run("git", "init", "-q", cwd=r)
        (r / "app.py").write_text("print('hi')\n")
        (r / "CLAUDE.md").write_text("rules\n")
        run("git", "add", "app.py", cwd=r)
        apply_to(r, "all")
        for p in (".git/ghost/ghost.json", ".claude/settings.json", ".git/ghost/ghost.py", ".git/hooks/commit-msg"):
            assert (r / p).exists(), p
        ex = (r / ".git/info/exclude").read_text()
        assert ".claude/" in ex and "CLAUDE.md" in ex
        assert not (r / ".gitignore").exists()
        assert run("git", "commit", "-q", "-m", "add app", cwd=r).returncode == 0
        assert check(r) == [], check(r)
        assert run("git", "commit", "-q", "--allow-empty", "-m", BOT, cwd=r).returncode != 0, "hook should block a marked message"
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
        apply_to(r, "all")
        assert run("git", "commit", "-q", "-m", "add app", cwd=r).returncode == 0
        run("git", "worktree", "add", "-q", "-b", "side", str(wt), cwd=r)
        assert run("git", "commit", "-q", "--allow-empty", "-m", "fine", cwd=wt).returncode == 0
        assert run("git", "commit", "-q", "--allow-empty", "-m", "x\n\nGenerated with Claude Code", cwd=wt).returncode != 0
        assert check(wt) == [], check(wt)

    # ghost off: only .claude/ is excluded and nothing is checked
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        run("git", "init", "-q", cwd=r)
        apply_to(r, "none")
        lines = [l for l in (r / ".git/info/exclude").read_text().splitlines() if l and not l.startswith("#")]
        assert lines == [".claude/"], lines
        (r / "n.md").write_text("Generated with Claude Code\n")
        run("git", "add", "n.md", cwd=r)
        run("git", "commit", "-q", "-m", "n", cwd=r)
        assert check(r) == [], check(r)

    # checker works alone for trailers, but does not police wording
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        run("git", "init", "-q", cwd=r)
        apply_to(r, "checker")
        assert run("git", "commit", "-q", "--allow-empty", "-m", BOT, cwd=r).returncode != 0, "checker alone must block trailers"
        assert run("git", "commit", "-q", "--allow-empty", "-m", "uses the Claude Code CLI", cwd=r).returncode == 0

    # a human with the same first name is not a bot; the allowlist and path globs work
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        run("git", "init", "-q", cwd=r)
        apply_to(r, "neutral-code,checker")
        human = "x\n\nCo-authored-by: Claude Dubois <claude.dubois@example.fr>"
        assert run("git", "commit", "-q", "--allow-empty", "-m", human, cwd=r).returncode == 0, "human co-author must pass"
        (r / "bot.py").write_text("print('\U0001F916 ready')\n")
        (r / "README.md").write_text("Summaries are AI-generated by our model.\n")
        run("git", "add", "-A", cwd=r)
        run("git", "commit", "-q", "-m", "add files", cwd=r)
        assert len(check(r)) == 2, check(r)
        cfgp = r / ".git" / "ghost" / "ghost.json"
        cfg = json.loads(cfgp.read_text())
        cfg["ignore_paths"] = ["bot.py"]
        cfg["ignore_markers"] = [r"ai-generated by our model"]
        cfgp.write_text(json.dumps(cfg))
        assert check(r) == [], check(r)

    # history before apply is not held against the project
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        run("git", "init", "-q", cwd=r)
        run("git", "commit", "-q", "--allow-empty", "-m", BOT, cwd=r)
        apply_to(r, "attribution,checker")
        assert check(r) == [], check(r)
        run("git", "commit", "-q", "--allow-empty", "--no-verify", "-m", BOT, cwd=r)
        assert any("commit" in l for l in check(r)), check(r)

    # core.hooksPath: installed there, and a later change is reported as shadowing
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        run("git", "init", "-q", cwd=r)
        run("git", "config", "core.hooksPath", ".myhooks", cwd=r)
        apply_to(r, "checker")
        assert (r / ".myhooks" / "commit-msg").exists()
        assert run("git", "commit", "-q", "--allow-empty", "-m", BOT, cwd=r).returncode != 0
        run("git", "config", "core.hooksPath", ".other", cwd=r)
        assert any("shadowed" in l for l in check(r)), check(r)
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
