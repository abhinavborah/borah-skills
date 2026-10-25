#!/usr/bin/env python3
"""Scan a folder or zip for secret-shaped strings and junk entries. Prints names only.

Usage: scan_bundle.py PATH [PATH ...]
       scan_bundle.py --self-test

PATH is a directory or a .zip file. Flags entries named __MACOSX, .DS_Store, .env, __pycache__,
node_modules, .venv or memory, and files that contain a secret-shaped string (sk- keys, AKIA ids,
ghp_ tokens, xoxb or xoxp tokens, private key headers). The matched text is never printed.
Exit 1 on any finding.
"""
import re
import sys
import tempfile
import zipfile
from pathlib import Path

JUNK = {"__MACOSX", ".DS_Store", ".env", "__pycache__", "node_modules", ".venv", "memory"}
SECRET = re.compile(rb"sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|xox[bp]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")


def entries(path):
    p = Path(path)
    if p.is_file() and zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as z:
            for n in z.namelist():
                yield n, (lambda n=n: z.read(n)) if not n.endswith("/") else None
    else:
        for f in sorted(p.rglob("*")):
            yield str(f.relative_to(p)), (lambda f=f: f.read_bytes()) if f.is_file() else None


def scan(path):
    out = []
    for name, read in entries(path):
        if JUNK & set(Path(name).parts):
            out.append(f"{path}: junk entry {name}")
        if read and SECRET.search(read()):
            out.append(f"{path}: secret-shaped string in {name}")
    return out


def self_test():
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        (r / "d").mkdir()
        (r / "d" / "ok.txt").write_text("nothing here\n")
        assert scan(r / "d") == []
        (r / "d" / "bad.txt").write_text("key = " + "AK" + "IA" + "A" * 16 + "\n")
        (r / "d" / ".DS_Store").write_text("x")
        out = scan(r / "d")
        assert len(out) == 2 and all("AKIA" not in x for x in out), out
        z = r / "a.zip"
        with zipfile.ZipFile(z, "w") as zf:
            zf.writestr("__MACOSX/x", "y")
            zf.writestr("ok.txt", "fine")
        out = scan(z)
        assert len(out) == 1 and "junk entry __MACOSX/x" in out[0], out
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    found = [x for p in sys.argv[1:] for x in scan(p)]
    print("\n".join(found) or "bundle clean")
    sys.exit(1 if found else 0)
