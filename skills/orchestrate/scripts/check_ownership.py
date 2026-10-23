#!/usr/bin/env python3
"""Merge gate for parallel packets: no edits outside ownership, no file touched twice.

Usage: check_ownership.py --plan PLAN.md --base REF --packet NAME=REF [--packet ...] [--repo DIR]
       check_ownership.py --self-test

PLAN.md holds one fenced block that starts with ```json ownership:
  {"packets": {"auth": {"may_write": ["src/auth/**", "tests/auth/**"]}}}
Each --packet maps a packet name to the branch or commit that holds its work.
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
    r = subprocess.run(["git", "-C", repo, "diff", "--name-only", f"{base}...{ref}"], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"git diff failed for {ref}: {r.stderr.strip()}")
    return set(r.stdout.split())


def gate(plan, repo, base, refs):
    packets, out, seen = load_plan(plan), [], {}
    for name, ref in refs.items():
        if name not in packets:
            out.append(f"{name}: not in plan")
            continue
        allowed = [g2re(g) for g in packets[name]["may_write"]]
        for f in sorted(changed(repo, base, ref)):
            seen.setdefault(f, []).append(name)
            if not any(a.match(f) for a in allowed):
                out.append(f"{name}: wrote {f} outside its ownership")
    out += [f"{f}: touched by {', '.join(n)}" for f, n in sorted(seen.items()) if len(n) > 1]
    return out


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
    print("self-test ok")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--plan")
    p.add_argument("--base")
    p.add_argument("--packet", action="append", default=[])
    p.add_argument("--repo", default=".")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
    elif a.plan and a.base and a.packet:
        found = gate(a.plan, a.repo, a.base, dict(x.split("=", 1) for x in a.packet))
        print("\n".join(found) or "ownership ok")
        sys.exit(1 if found else 0)
    else:
        p.error("--plan, --base and at least one --packet are required")
