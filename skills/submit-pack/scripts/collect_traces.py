#!/usr/bin/env python3
"""Copy Claude Code transcripts for a repo and its worktrees into one folder.

Usage: collect_traces.py --repo PATH --out DIR [--projects DIR]
       collect_traces.py --self-test

Claude Code names a project folder after the working directory, with / and . replaced by -.
Worktrees such as <repo>.build get their own folder. This copies every folder whose name equals
the repo's, or starts with it followed by -, into DIR/<folder name>/. Only *.jsonl files are
copied, with the session and subagents layout kept. memory/ and tool-results/ are skipped.
It prints the matched folders: a sibling repo with a longer name can match, so check the list.
"""
import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path


def slug(path):
    return re.sub(r"[/.]", "-", str(Path(path).resolve()))


def collect(repo, out, projects):
    s, matched, n = slug(repo), [], 0
    for d in sorted(Path(projects).iterdir()):
        if not d.is_dir() or not (d.name == s or d.name.startswith(s + "-")):
            continue
        matched.append(d.name)
        for f in d.rglob("*.jsonl"):
            rel = f.relative_to(d)
            if {"memory", "tool-results"} & set(rel.parts):
                continue
            dest = Path(out) / d.name / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            n += 1
    return matched, n


def self_test():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        repo = t / "work" / "my.repo"
        repo.mkdir(parents=True)
        proj = t / "projects"
        s = slug(repo)
        for name in (s, s + "-build", s + "x", "-other"):
            (proj / name / "sess" / "subagents").mkdir(parents=True)
            (proj / name / "sess.jsonl").write_text("{}\n")
            (proj / name / "sess" / "subagents" / "a.jsonl").write_text("{}\n")
        (proj / s / "memory").mkdir()
        (proj / s / "memory" / "m.jsonl").write_text("{}\n")
        (proj / s / "sess" / "tool-results").mkdir()
        (proj / s / "sess" / "tool-results" / "r.jsonl").write_text("{}\n")
        matched, n = collect(repo, t / "out", proj)
        assert matched == [s, s + "-build"], matched
        assert n == 4, n
        assert (t / "out" / s / "sess" / "subagents" / "a.jsonl").exists()
        assert not (t / "out" / s / "memory").exists()
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--repo", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--projects", default=str(Path.home() / ".claude" / "projects"))
    a = p.parse_args()
    matched, n = collect(a.repo, a.out, a.projects)
    print("matched folders:", *matched, sep="\n  ")
    print(f"copied {n} jsonl files")
    sys.exit(0 if n else 1)
