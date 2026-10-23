#!/usr/bin/env python3
"""Project journal: one append-only file per entry under docs/journal/.

Usage: journal.py new --root DIR --kind KIND --title TITLE [--status draft|stable]
                      [--confidence low|medium|high] [--evidence STRENGTH] [--by ACTOR] [--neutral]
       journal.py supersede --root DIR --old FILE --new FILE
       journal.py digest --root DIR [--limit N]
       journal.py --self-test

KIND is decision, finding, change, rejection or question. `new` writes the entry with
FILL: placeholders and syncs docs/journal/index.md and log.md. `supersede` is the only
allowed edit to an accepted entry. `digest` prints the active view: current decisions,
open questions, recent entries, and entries with unfilled placeholders.
--neutral writes `timestamp` instead of `generated` (ghost level neutral-docs).
"""
import argparse
import importlib.util
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SECTIONS = {
    "decision": ["What was decided", "Why", "Alternatives considered", "Consequences", "Links"],
    "finding": ["What was found", "Evidence and scope", "Links"],
    "change": ["What changed", "Why", "Links"],
    "rejection": ["What was rejected", "Why", "Links"],
    "question": ["The question", "What would answer it", "Links"],
}
FM = re.compile(r"---\n(.*?)\n---\n", re.S)


def journal_dir(root):
    d = Path(root) / "docs" / "journal"
    if not (d / "index.md").exists():
        sys.exit(f"{d} is missing index.md; run scaffold, or create the folder as the okf-docs skill describes")
    return d


def frontmatter(text):
    m = FM.match(text)
    return dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l and not l.startswith(" ")) if m else {}


def unquote(value):
    value = value.strip()
    return json.loads(value) if value.startswith('"') else value


def set_key(text, key, value):
    m = FM.match(text)
    body = m.group(1)
    line = f"{key}: {value}"
    if re.search(rf"^{key}:.*$", body, re.M):
        body = re.sub(rf"^{key}:.*$", line, body, flags=re.M)
    else:
        body += "\n" + line
    return f"---\n{body}\n---\n" + text[m.end():]


def sync_index(d, title, fname, kind):
    p = d / "index.md"
    lines = p.read_text().split("\n")
    entry = f"* [{title}]({fname}) - {kind}: {title}"
    at = next((i for i, l in enumerate(lines) if l.startswith("* [")), None)
    if at is None:
        lines = [l for l in lines if l != ""] + ["", entry, ""]
    else:
        lines.insert(at, entry)
    p.write_text("\n".join(lines))


def sync_log(d, day, entry):
    p = d / "log.md"
    text = p.read_text()
    m = re.search(r"^## (\S+)$", text, re.M)
    if m and m.group(1) == day:
        text = text[: m.end()] + "\n" + entry + text[m.end():]
    elif m:
        text = text[: m.start()] + f"## {day}\n{entry}\n\n" + text[m.start():]
    else:
        text = text.rstrip("\n") + f"\n\n## {day}\n{entry}\n"
    p.write_text(text)


def new(root, kind, title, status=None, confidence=None, evidence=None, by="agent/unknown", neutral=False):
    d = journal_dir(root)
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:40] or "entry"
    fname = f"{now.strftime('%Y_%m_%d_%H%M%S')}_{slug}.md"
    path = d / fname
    if path.exists():
        sys.exit(f"{path} exists")
    status = status or ("stable" if kind == "decision" else None)
    fm = ["type: Journal Entry", f"title: {json.dumps(title)}", f"description: {json.dumps(f'{kind}: {title}')}", f"tags: [{kind}]", f"kind: {kind}"]
    fm += [f"{k}: {v}" for k, v in (("status", status), ("confidence", confidence), ("evidence", evidence)) if v]
    fm.append(f"timestamp: {stamp}" if neutral else f"generated: {{ by: {json.dumps(by)}, at: {stamp} }}")
    body = "\n\n".join(f"## {s}\nFILL: " for s in SECTIONS[kind])
    path.write_text("---\n" + "\n".join(fm) + f"\n---\n\n# {title}\n\n{body}\n")
    sync_index(d, title, fname, kind)
    sync_log(d, stamp[:10], f"* **Creation**: Added [{title}]({fname}).")
    return path


def supersede(root, old, new_):
    d = journal_dir(root)
    po, pn = d / Path(old).name, d / Path(new_).name
    to, tn = po.read_text(), pn.read_text()
    if frontmatter(to).get("kind", "").strip() not in ("decision", "question"):
        sys.exit("only a decision or a question can be superseded")
    po.write_text(set_key(set_key(to, "status", "deprecated"), "superseded_by", pn.name))
    pn.write_text(set_key(tn, "supersedes", po.name))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sync_log(d, stamp, f"* **Update**: [{po.stem}]({po.name}) superseded by [{pn.stem}]({pn.name}).")


def entries(d):
    out = []
    for f in sorted(d.glob("*.md"), reverse=True):
        if f.name in ("index.md", "log.md"):
            continue
        text = f.read_text()
        fm = {k.strip(): unquote(v) for k, v in frontmatter(text).items()}
        out.append((f, fm, "FILL:" in text))
    return out


def digest(root, limit=10):
    items = entries(journal_dir(root))
    when = lambda f: f"{f.name[:10].replace('_', '-')} {f.name[11:13]}:{f.name[13:15]}"
    live = lambda fm: fm.get("status") != "deprecated"
    out = [f"ACTIVE DECISIONS ({sum(1 for _, fm, _ in items if fm.get('kind') == 'decision' and live(fm))})"]
    for f, fm, _ in items:
        if fm.get("kind") == "decision" and live(fm):
            tag = " (proposed)" if fm.get("status") == "draft" else ""
            out.append(f"  {when(f)}  {fm.get('title') or f.stem}{tag}  [{fm.get('confidence', '-')}]  {f.name}")
    out.append("OPEN QUESTIONS")
    out += [f"  {when(f)}  {fm.get('title') or f.stem}  {f.name}" for f, fm, _ in items if fm.get("kind") == "question" and live(fm)]
    out.append(f"RECENT ({limit})")
    out += [f"  {when(f)}  {fm.get('kind') or '-':9} {fm.get('title') or f.stem}" for f, fm, _ in items[:limit]]
    out.append(f"SUPERSEDED OR CLOSED, hidden: {sum(1 for _, fm, _ in items if not live(fm))}")
    todo = [f.name for f, _, fill in items if fill]
    if todo:
        out.append("INCOMPLETE (FILL: left): " + ", ".join(todo))
    return "\n".join(out)


def self_test():
    here = Path(__file__).resolve().parent
    def load(rel, name):
        spec = importlib.util.spec_from_file_location(name, here / rel)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    scaffold = load("../../scaffold/scripts/scaffold_docs.py", "sd")
    okf = load("../../okf-docs/scripts/okf_validate.py", "okf")
    for neutral in (False, True):
        with tempfile.TemporaryDirectory() as t:
            scaffold.build(t, "demo", "human:t", neutral)
            a = new(t, "decision", "Use Postgres", confidence="high", neutral=neutral)
            new(t, "finding", "Pooling helps", evidence="primary", neutral=neutral)
            new(t, "question", "Who owns auth?", neutral=neutral)
            b = new(t, "decision", "Use SQLite instead", neutral=neutral)
            supersede(t, a.name, b.name)
            assert "status: deprecated" in a.read_text() and f"superseded_by: {b.name}" in a.read_text()
            assert f"supersedes: {a.name}" in b.read_text()
            out = digest(t)
            assert "Use SQLite instead" in out.split("OPEN QUESTIONS")[0], out
            assert "Use Postgres" not in out.split("RECENT")[0], out
            assert "hidden: 1" in out and "INCOMPLETE" in out and "Who owns auth?" in out, out
            assert ("timestamp:" in a.read_text()) == neutral
            c = new(t, "change", "Odd by", by="human:a, b", neutral=neutral)
            assert c.name.startswith(datetime.now(timezone.utc).strftime("%Y_%m_%d")), c.name
            errs, warns = okf.validate(Path(t) / "docs")
            assert (errs, warns) == ([], []), (errs, warns)
            (Path(t) / "docs" / "journal" / "zz_note.md").write_text("---\ntype: Note\n---\nhand written\n")
            assert "zz_note" in digest(t), "digest must survive entries without kind"
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("--root", required=True)
    n.add_argument("--kind", required=True, choices=sorted(SECTIONS))
    n.add_argument("--title", required=True)
    n.add_argument("--status", choices=["draft", "stable"])
    n.add_argument("--confidence", choices=["low", "medium", "high"])
    n.add_argument("--evidence")
    n.add_argument("--by", default="agent/unknown")
    n.add_argument("--neutral", action="store_true")
    s = sub.add_parser("supersede")
    s.add_argument("--root", required=True)
    s.add_argument("--old", required=True)
    s.add_argument("--new", required=True)
    g = sub.add_parser("digest")
    g.add_argument("--root", required=True)
    g.add_argument("--limit", type=int, default=10)
    a = p.parse_args()
    if a.cmd == "new":
        print(new(a.root, a.kind, a.title, a.status, a.confidence, a.evidence, a.by, a.neutral))
    elif a.cmd == "supersede":
        supersede(a.root, a.old, a.new)
        print("superseded")
    else:
        print(digest(a.root, a.limit))
