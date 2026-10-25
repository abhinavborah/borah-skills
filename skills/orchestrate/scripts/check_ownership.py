#!/usr/bin/env python3
"""Merge gate for parallel packets: no edits outside ownership, no file touched twice.

Usage: check_ownership.py --plan PLAN.md --base REF --packet NAME=REF [--packet ...]
                          [--worktree NAME=DIR ...] [--repo DIR]
       check_ownership.py --plan PLAN.md --shared NAME [--repo DIR]
       check_ownership.py --self-test

PLAN.md holds one fenced block that starts with ```json ownership:
  {"packets": {"auth": {"may_write": ["src/auth/**", "tests/auth/**"]}}}
Each --packet maps a packet name to the branch or commit that holds its work. Pass only packets
that write files. --worktree names the directory a packet worked in, so uncommitted work is caught.
Renames count as a delete plus an add, so moving a file out of another packet's area is flagged.
A packet with no commits past the base is reported, since uncommitted work cannot be merged.
--shared NAME is for a single shared tree: it checks the uncommitted and untracked files in --repo
against packet NAME's may_write. Run it after each packet, before the lead commits that packet.
Globs: ** matches across directories, * within one. Exit 1 on any finding.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def g2re(glob):
    out, i = "", 0
    while i < len(glob):
        if glob[i : i + 2] == "**":
            out, i = out + ".*", i + 2
        elif glob[i] == "*":
            out, i = out + "[^/]*", i + 1
        else:
            out, i = out + re.escape(glob[i]), i + 1
    return re.compile(out + r"\Z")


def load_plan(path):
    m = re.search(r"```json ownership\n(.*?)\n```", Path(path).read_text(), re.S)
    if not m:
        sys.exit("plan has no ```json ownership block")
    return json.loads(m.group(1))["packets"]


def changed(repo, base, ref):
    r = subprocess.run(["git", "-C", repo, "diff", "--name-only", "--no-renames", f"{base}...{ref}"], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"git diff failed for {ref}: {r.stderr.strip()}")
    return set(r.stdout.splitlines())


def gate(plan, repo, base, refs, worktrees=None):
    packets, out, seen = load_plan(plan), [], {}
    for name, ref in refs.items():
        if name not in packets:
            out.append(f"{name}: not in plan")
            continue
        n = subprocess.run(["git", "-C", repo, "rev-list", "--count", f"{base}..{ref}"], capture_output=True, text=True)
        if n.returncode or int(n.stdout.strip() or 0) == 0:
            out.append(f"{name}: no commits past {base} on {ref}; the subagent must commit its work")
        wt = (worktrees or {}).get(name)
        if wt:
            dirty = subprocess.run(["git", "-C", wt, "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
            if dirty:
                out.append(f"{name}: uncommitted changes in {wt}")
        allowed = [g2re(g) for g in packets[name]["may_write"]]
        for f in sorted(changed(repo, base, ref)):
            seen.setdefault(f, []).append(name)
            if not any(a.match(f) for a in allowed):
                out.append(f"{name}: wrote {f} outside its ownership")
    out += [f"{f}: touched by {', '.join(n)}" for f, n in sorted(seen.items()) if len(n) > 1]
    return out


def gate_shared(plan, repo, name):
    packets = load_plan(plan)
    if name not in packets:
        return [f"{name}: not in plan"]
    r = subprocess.run(["git", "-C", repo, "status", "--porcelain", "--untracked-files=all", "-z"], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"git status failed: {r.stderr.strip()}")
    files, parts = set(), r.stdout.split("\0")
    i = 0
    while i < len(parts) and parts[i]:
        files.add(parts[i][3:])
        if parts[i][0] in "RC":  # a rename lists the old path next
            i += 1
            files.add(parts[i])
        i += 1
    allowed = [g2re(g) for g in packets[name]["may_write"]]
    out = [f"{name}: wrote {f} outside its ownership" for f in sorted(files) if not any(a.match(f) for a in allowed)]
    return out or ([] if files else [f"{name}: no changes in the working tree"])


def self_test():
    def run(*a, cwd):
        return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, check=True)

    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        env = ["-c", "user.name=t", "-c", "user.email=t@t"]
        run("git", "init", "-q", "-b", "main", cwd=r)
        (r / "README.md").write_text("x\n")
        run("git", "add", ".", cwd=r)
        run("git", *env, "commit", "-q", "-m", "base", cwd=r)
        for branch, files in (("a", ["src/auth/x.py"]), ("b", ["src/billing/y.py", "src/auth/z.py"])):
            run("git", "checkout", "-q", "-b", branch, "main", cwd=r)
            for f in files:
                (r / f).parent.mkdir(parents=True, exist_ok=True)
                (r / f).write_text("1\n")
            run("git", "add", ".", cwd=r)
            run("git", *env, "commit", "-q", "-m", branch, cwd=r)
        plan = r / "plan.md"
        plan.write_text('```json ownership\n{"packets": {"a": {"may_write": ["src/auth/**"]}, "b": {"may_write": ["src/billing/**"]}}}\n```\n')
        assert gate(plan, str(r), "main", {"a": "a"}) == []
        out = gate(plan, str(r), "main", {"a": "a", "b": "b"})
        assert out == ["b: wrote src/auth/z.py outside its ownership"], out

        # a rename out of another packet's area is a delete plus an add
        run("git", "checkout", "-q", "-b", "mv", "main", cwd=r)
        (r / "src/auth").mkdir(parents=True, exist_ok=True)
        (r / "src/auth/keep.py").write_text("1\n")
        run("git", "add", ".", cwd=r)
        run("git", *env, "commit", "-q", "-m", "seed", cwd=r)
        run("git", "branch", "seeded", cwd=r)
        (r / "src/billing").mkdir(parents=True, exist_ok=True)
        run("git", "mv", "src/auth/keep.py", "src/billing/keep.py", cwd=r)
        run("git", *env, "commit", "-q", "-m", "move", cwd=r)
        out = gate(plan, str(r), "seeded", {"b": "mv"})
        assert out == ["b: wrote src/auth/keep.py outside its ownership"], out

        # no commits, and uncommitted work in a worktree
        run("git", "branch", "empty", "seeded", cwd=r)
        assert any("no commits" in x for x in gate(plan, str(r), "seeded", {"a": "empty"}))
        wt = Path(t) / "wt"
        run("git", "worktree", "add", "-q", "-b", "wtb", str(wt), "seeded", cwd=r)
        (wt / "src/auth").mkdir(parents=True, exist_ok=True)
        (wt / "src/auth/new.py").write_text("1\n")
        out = gate(plan, str(r), "seeded", {"a": "wtb"}, {"a": str(wt)})
        assert any("uncommitted" in x for x in out) and any("no commits" in x for x in out), out

    with tempfile.TemporaryDirectory() as t:
        r = Path(t) / "repo"
        r.mkdir()
        env = ["-c", "user.name=t", "-c", "user.email=t@t"]
        run("git", "init", "-q", "-b", "main", cwd=r)
        (r / "README.md").write_text("x\n")
        run("git", "add", ".", cwd=r)
        run("git", *env, "commit", "-q", "-m", "base", cwd=r)
        plan = Path(t) / "plan.md"
        plan.write_text('```json ownership\n{"packets": {"a": {"may_write": ["src/auth/**"]}}}\n```\n')
        assert gate_shared(plan, str(r), "a") == ["a: no changes in the working tree"]
        (r / "src/auth").mkdir(parents=True)
        (r / "src/auth/x.py").write_text("1\n")
        assert gate_shared(plan, str(r), "a") == []
        (r / "src/other.py").write_text("1\n")
        assert gate_shared(plan, str(r), "a") == ["a: wrote src/other.py outside its ownership"]
    print("self-test ok")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--plan")
    p.add_argument("--base")
    p.add_argument("--packet", action="append", default=[])
    p.add_argument("--worktree", action="append", default=[])
    p.add_argument("--shared")
    p.add_argument("--repo", default=".")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
    elif a.plan and a.shared:
        found = gate_shared(a.plan, a.repo, a.shared)
        print("\n".join(found) or "ownership ok")
        sys.exit(1 if found else 0)
    elif a.plan and a.base and a.packet:
        found = gate(a.plan, a.repo, a.base, dict(x.split("=", 1) for x in a.packet), dict(x.split("=", 1) for x in a.worktree))
        print("\n".join(found) or "ownership ok")
        sys.exit(1 if found else 0)
    else:
        p.error("--plan with --shared, or --plan, --base and at least one --packet, are required")
