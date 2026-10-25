#!/usr/bin/env python3
"""Validate a contract table written from the contract-check template.

Usage: contract_lint.py CONTRACT.md [--final]
       contract_lint.py --self-test

Checks every table row whose first cell is an id like C-001:
  unique ids, level MUST or SHOULD, a source, a rule, a valid status,
  a proof for `met` and `waived` rows.
--final also fails on rows still `open` or `conflict`. Exit 1 on any finding.
"""
import re
import sys
import tempfile
from pathlib import Path

STATUSES = {"open", "met", "waived", "conflict"}
ROW = re.compile(r"^\|\s*(C-\d+)\s*\|(.*)\|\s*$")


def check(text, final=False):
    out, seen = [], set()
    for line in text.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        cid, cells = m.group(1), [c.strip() for c in m.group(2).split("|")]
        if len(cells) != 5:
            out.append(f"{cid}: expected 6 columns, got {len(cells) + 1}")
            continue
        level, source, rule, status, proof = cells
        if cid in seen:
            out.append(f"{cid}: duplicate id")
        seen.add(cid)
        if level not in ("MUST", "SHOULD"):
            out.append(f"{cid}: level must be MUST or SHOULD")
        if not source:
            out.append(f"{cid}: no source")
        if not rule:
            out.append(f"{cid}: no rule text")
        if status not in STATUSES:
            out.append(f"{cid}: status must be one of {sorted(STATUSES)}")
        if status in ("met", "waived") and not proof:
            out.append(f"{cid}: {status} row has no proof")
        if final and status in ("open", "conflict"):
            out.append(f"{cid}: still {status}")
    if not seen:
        out.append("no contract rows found")
    return out


def self_test():
    good = "| id | l | s | r | st | p |\n|---|---|---|---|---|---|\n| C-001 | MUST | a.md | do x | met | ran it |\n| C-002 | SHOULD | b.md | do y | open | |\n"
    assert check(good) == []
    assert check(good, final=True) == ["C-002: still open"]
    bad = "| C-001 | MUST | a.md | x | met | |\n| C-001 | MAYBE | | | done | |\n"
    out = "\n".join(check(bad))
    for needle in ("duplicate id", "level must be", "no source", "no rule text", "status must be", "no proof"):
        assert needle in out, (needle, out)
    assert check("nothing here\n") == ["no contract rows found"]
    with tempfile.TemporaryDirectory() as t:
        f = Path(t) / "c.md"
        f.write_text(good)
        assert check(f.read_text()) == []
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    problems = check(Path(sys.argv[1]).read_text(), "--final" in sys.argv)
    print("\n".join(problems) or "contract ok")
    sys.exit(1 if problems else 0)
