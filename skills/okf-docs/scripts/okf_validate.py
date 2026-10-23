#!/usr/bin/env python3
"""Validate an OKF v0.2 bundle, plus the typed index/log convention used here.

Usage: okf_validate.py [--strict] <bundle_dir>
       okf_validate.py --self-test

ERROR   conformance break: missing frontmatter or type, bad log date, broken link
WARNING convention gap: missing fields, index or log, unlinked concept, naming
--strict exits non-zero on warnings as well.
"""
import re
import sys
import tempfile
from pathlib import Path

RESERVED = {"index.md", "log.md"}
SNAKE = re.compile(r"[a-z0-9]+(_[a-z0-9]+)*")
ISO = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})")
DATE_H = re.compile(r"^## (.+)$", re.M)
LINK = re.compile(r"\]\((?!https?:|mailto:|#|data:)([^)\s]+)")
FENCE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
STATUS = {"draft", "stable", "deprecated"}


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return None
    fm, key = {}, None
    for line in m.group(1).splitlines():
        top = re.match(r"([A-Za-z_][\w-]*):\s*(.*)$", line)
        if top and not line.startswith((" ", "\t")):
            key = top.group(1)
            fm[key] = top.group(2)
        elif key:
            fm[key] += " " + line.strip()
    return fm


def concept_dirs(root):
    for d in [root, *sorted(p for p in root.rglob("*") if p.is_dir())]:
        rel = d.relative_to(root).parts
        if any(p.startswith(".") or p == "references" for p in rel):
            continue
        if any(f.suffix == ".md" for f in d.iterdir()):
            yield d


def validate(root):
    errs, warns = [], []
    for d in concept_dirs(root):
        files = sorted(f for f in d.iterdir() if f.suffix == ".md")
        for need in RESERVED:
            if not (d / need).exists():
                warns.append(f"{d}: missing {need}")
        index_text = (d / "index.md").read_text() if (d / "index.md").exists() else ""
        for f in files:
            text = f.read_text()
            fm = frontmatter(text)
            where = str(f)
            if f.name not in RESERVED:
                if not SNAKE.fullmatch(f.stem):
                    warns.append(f"{where}: filename not snake_case")
                if fm is None:
                    errs.append(f"{where}: missing frontmatter")
                    continue
                if not fm.get("type", "").strip():
                    errs.append(f"{where}: missing type")
                for k in ("title", "description", "tags"):
                    if k not in fm:
                        warns.append(f"{where}: missing {k}")
                if "timestamp" not in fm and not re.search(r"\bat:\s*\S", fm.get("generated", "")):
                    warns.append(f"{where}: missing timestamp or generated.at")
                for k in ("timestamp",):
                    if k in fm and not ISO.fullmatch(fm[k].strip().strip("\"'")):
                        warns.append(f"{where}: {k} is not ISO 8601 with offset")
                if fm.get("status") and fm["status"].strip() not in STATUS:
                    warns.append(f"{where}: status must be draft, stable or deprecated")
                if f.name not in index_text:
                    warns.append(f"{where}: not linked from {d / 'index.md'}")
            else:
                if fm is None or not fm.get("type", "").strip():
                    warns.append(f"{where}: reserved file should carry a type")
            if f.name == "index.md" and d == root and (fm is None or "okf_version" not in fm):
                warns.append(f"{where}: root index missing okf_version")
            if f.name == "log.md":
                dates = DATE_H.findall(text)
                bad = [h for h in dates if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", h)]
                for h in bad:
                    errs.append(f"{where}: log heading '{h}' is not YYYY-MM-DD")
                good = [h for h in dates if h not in bad]
                if good != sorted(good, reverse=True):
                    warns.append(f"{where}: log entries not newest first")
            for ref in LINK.findall(FENCE.sub("", text)):
                path = ref.split("#")[0]
                if not path:
                    continue
                target = root / path.lstrip("/") if path.startswith("/") else d / path
                if not target.exists():
                    errs.append(f"{where}: broken link {ref}")
    return errs, warns


def self_test():
    ok = "---\ntype: Note\ntitle: A\ndescription: d\ntags: [a]\ntimestamp: 2026-10-24T10:00:00Z\n---\nbody\n"
    idx = '---\ntype: Bundle Index\ntitle: i\ndescription: d\ntags: [i]\ntimestamp: 2026-10-24T10:00:00Z\nokf_version: "0.2"\n---\n* [A](a_note.md) - d\n'
    log = "---\ntype: Change Log\ntitle: l\ndescription: d\ntags: [l]\ntimestamp: 2026-10-24T10:00:00Z\n---\n## 2026-10-24\n* **Creation**: made.\n"
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        (r / "a_note.md").write_text(ok)
        (r / "index.md").write_text(idx)
        (r / "log.md").write_text(log)
        e, w = validate(r)
        assert (e, w) == ([], []), (e, w)
        (r / "Bad-Name.md").write_text("no frontmatter [x](gone.md)\n")
        (r / "no_type.md").write_text("---\ntitle: x\n---\n")
        (r / "log.md").write_text(log + "## yesterday\n")
        e, w = validate(r)
        out = "\n".join(e + w)
        for needle in ("missing frontmatter", "missing type", "not YYYY-MM-DD", "not snake_case", "not linked"):
            assert needle in out, (needle, out)
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    errs, warns = validate(Path(args[0]).resolve())
    for line in errs:
        print("ERROR  ", line)
    for line in warns:
        print("WARNING", line)
    print(f"{len(errs)} errors, {len(warns)} warnings")
    sys.exit(1 if errs or ("--strict" in sys.argv and warns) else 0)
