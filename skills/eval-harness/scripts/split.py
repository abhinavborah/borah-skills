#!/usr/bin/env python3
"""Deterministic dev and holdout split of a labeled CSV, kept whole by group.

Usage: split.py LABELED.csv --group COLUMN [--holdout 0.3] [--seed 1] --out DIR
       split.py --self-test

Each group value goes to holdout when sha256(seed:group) falls under the fraction, so the split
is stable across runs and machines and a group never straddles both files. Writes DIR/dev.csv
and DIR/holdout.csv and prints the counts.
"""
import argparse
import csv
import hashlib
import sys
import tempfile
from pathlib import Path


def side(group, seed, frac):
    h = int(hashlib.sha256(f"{seed}:{group}".encode()).hexdigest()[:8], 16) / 0x100000000
    return "holdout" if h < frac else "dev"


def split(rows, group, seed, frac):
    out = {"dev": [], "holdout": []}
    for r in rows:
        out[side(r[group], seed, frac)].append(r)
    return out


def self_test():
    rows = [{"g": str(i % 20), "v": str(i)} for i in range(200)]
    a, b = split(rows, "g", 1, 0.3), split(rows, "g", 1, 0.3)
    assert a == b
    assert len(a["dev"]) + len(a["holdout"]) == 200
    assert {r["g"] for r in a["dev"]}.isdisjoint({r["g"] for r in a["holdout"]})
    assert a["holdout"] and a["dev"]
    with tempfile.TemporaryDirectory() as t:
        src = Path(t) / "l.csv"
        with src.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["g", "v"])
            w.writeheader()
            w.writerows(rows)
        run(src, "g", 0.3, 1, Path(t) / "o")
        assert (Path(t) / "o" / "dev.csv").exists() and (Path(t) / "o" / "holdout.csv").exists()
    print("self-test ok")


def run(src, group, frac, seed, out):
    with open(src, newline="") as f:
        rd = csv.DictReader(f)
        names, rows = rd.fieldnames, list(rd)
    if group not in names:
        sys.exit(f"no column {group}")
    parts = split(rows, group, seed, frac)
    Path(out).mkdir(parents=True, exist_ok=True)
    for k, v in parts.items():
        with open(Path(out) / f"{k}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=names)
            w.writeheader()
            w.writerows(v)
    print({k: len(v) for k, v in parts.items()})


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("labeled")
    p.add_argument("--group", required=True)
    p.add_argument("--holdout", type=float, default=0.3)
    p.add_argument("--seed", default="1")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    run(a.labeled, a.group, a.holdout, a.seed, a.out)
