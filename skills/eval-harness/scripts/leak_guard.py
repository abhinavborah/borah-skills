#!/usr/bin/env python3
"""Fail when production code mentions a forbidden string, such as a gold or sample-answer path.

Usage: leak_guard.py --code DIR --forbid TEXT [--forbid TEXT ...] [--skip NAME ...]
       leak_guard.py --self-test

Scans text files under DIR. Folders named tests, evaluation and .git are skipped, plus any --skip
names. Prints file:line for each hit and exits 1. It matches plain substrings, so a string built
at run time can slip past: keep paths as literals.
"""
import argparse
import sys
import tempfile
from pathlib import Path

SKIP = {"tests", "evaluation", ".git", "__pycache__", "node_modules", ".venv"}


def scan(code, forbid, skip=()):
    skip = SKIP | set(skip)
    hits = []
    for f in sorted(Path(code).rglob("*")):
        if not f.is_file() or skip & set(f.relative_to(code).parts[:-1]):
            continue
        try:
            lines = f.read_text().splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            for s in forbid:
                if s in line:
                    hits.append(f"{f}:{n}: mentions {s}")
    return hits


def self_test():
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        (r / "app").mkdir()
        (r / "tests").mkdir()
        (r / "app" / "a.py").write_text("x = 1\nopen('data/sample_output.csv')\n")
        (r / "tests" / "t.py").write_text("open('data/sample_output.csv')\n")
        hits = scan(r, ["sample_output.csv"])
        assert len(hits) == 1 and hits[0].endswith("a.py:2: mentions sample_output.csv"), hits
        assert scan(r, ["sample_output.csv"], skip=["app"]) == []
        assert scan(r, ["other"]) == []
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--code", required=True)
    p.add_argument("--forbid", action="append", required=True)
    p.add_argument("--skip", action="append", default=[])
    a = p.parse_args()
    found = scan(a.code, a.forbid, a.skip)
    print("\n".join(found) or "no leaks")
    sys.exit(1 if found else 0)
