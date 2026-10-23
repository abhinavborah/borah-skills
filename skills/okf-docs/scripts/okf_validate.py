#!/usr/bin/env python3
"""Validate an OKF v0.2 bundle, plus the typed index/log convention used here.

Usage: okf_validate.py [--strict] <bundle_dir>
       okf_validate.py --self-test

ERROR   a MUST in the spec is broken: unparseable or missing frontmatter, missing type,
        missing generated.by, a log heading that is not YYYY-MM-DD
WARNING convention gap: missing fields, bad time format, broken link, missing index or log,
        unlinked concept, naming
NOTE    informational, never fails: legacy fields in use
--strict exits non-zero on warnings as well.

Frontmatter is parsed with a strict YAML subset: mappings, block lists, flow lists and maps,
quoted and plain scalars. Anchors, tags and block scalars are reported as unsupported and the
file falls back to a loose read.
"""
import json
import re
import sys
import tempfile
from pathlib import Path

RESERVED = {"index.md", "log.md"}
SNAKE = re.compile(r"[a-z0-9]+(_[a-z0-9]+)*")
ISO = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})")
DATE_H = re.compile(r"^## (.+)$", re.M)
LINK = re.compile(r"\]\((?!https?:|mailto:|#|data:)([^)\s]+)")
FENCE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
FM = re.compile(r"---\n(.*?)\n---\n?", re.S)
STATUS = {"draft", "stable", "deprecated"}
KEY = re.compile(r'([A-Za-z_][\w-]*|"[^"]+")\s*:(?:\s+(.*))?$')


class YamlError(Exception):
    pass


BROKEN = object()  # marker: frontmatter exists but cannot be parsed


class Unsupported(Exception):
    pass


def parse_flow(s, i):
    """Parse a flow list or map starting at s[i]. Returns (value, next_index)."""
    def skip(i):
        while i < len(s) and s[i] in " \t":
            i += 1
        return i

    def item(i, stops):
        i = skip(i)
        if i >= len(s):
            raise YamlError("unterminated flow collection")
        if s[i] in "[{":
            return parse_flow(s, i)
        if s[i] == '"':
            try:
                val, end = json.JSONDecoder().raw_decode(s[i:])
            except ValueError:
                raise YamlError("bad double-quoted string")
            return val, i + end
        if s[i] == "'":
            m = re.match(r"'((?:[^']|'')*)'", s[i:])
            if not m:
                raise YamlError("unterminated single-quoted string")
            return m.group(1).replace("''", "'"), i + m.end()
        j = i
        while j < len(s) and s[j] not in stops:
            j += 1
        return s[i:j].strip(), j

    i = skip(i)
    close = "]" if s[i] == "[" else "}"
    i += 1
    out = [] if close == "]" else {}
    while True:
        i = skip(i)
        if i >= len(s):
            raise YamlError("unterminated flow collection")
        if s[i] == close:
            return out, i + 1
        if close == "]":
            val, i = item(i, ",]")
            out.append(val)
        else:
            key, i = item(i, ":,}")
            i = skip(i)
            if i >= len(s) or s[i] != ":":
                raise YamlError("flow map entry is not 'key: value' (an unquoted comma in a value?)")
            val, i = item(i + 1, ",}")
            out[key] = val
        i = skip(i)
        if i < len(s) and s[i] == ",":
            i += 1
        elif i < len(s) and s[i] != close:
            raise YamlError(f"unexpected '{s[i]}' in flow collection")


def parse_scalar(s):
    if s[0] == '"':
        try:
            val, end = json.JSONDecoder().raw_decode(s)
        except ValueError:
            raise YamlError(f"bad double-quoted string: {s[:40]}")
        rest = s[end:].strip()
        if rest and not rest.startswith("#"):
            raise YamlError(f"text after closing quote: {s[:40]}")
        return val
    if s[0] == "'":
        m = re.match(r"'((?:[^']|'')*)'\s*(#.*)?$", s)
        if not m:
            raise YamlError(f"bad single-quoted string: {s[:40]}")
        return m.group(1).replace("''", "'")
    if s[0] in "[{":
        val, end = parse_flow(s, 0)
        rest = s[end:].strip()
        if rest and not rest.startswith("#"):
            raise YamlError(f"text after flow collection: {s[:40]}")
        return val
    if s[0] in "|>&*!":
        raise Unsupported(s[:20])
    s = re.sub(r"\s+#.*$", "", s)
    if ": " in s or s.endswith(":"):
        raise YamlError(f"unquoted ': ' inside a value, quote it: {s[:50]}")
    return s


def parse_block(items, i, indent):
    def is_dash(t):
        return t == "-" or t.startswith("- ")

    if items[i][1][:1] == "-" and is_dash(items[i][1]):
        out = []
        while i < len(items) and items[i][0] == indent and is_dash(items[i][1]):
            rest = items[i][1][2:].strip()
            if not rest:
                if i + 1 < len(items) and items[i + 1][0] > indent:
                    val, i = parse_block(items, i + 1, items[i + 1][0])
                else:
                    val, i = None, i + 1
            elif KEY.match(rest) and rest[0] not in "\"'[{":
                items[i] = (indent + 2, rest)
                val, i = parse_block(items, i, indent + 2)
            else:
                val, i = parse_scalar(rest), i + 1
            out.append(val)
        return out, i
    out = {}
    while i < len(items) and items[i][0] == indent:
        m = KEY.match(items[i][1])
        if not m:
            raise YamlError(f"line is not 'key: value': {items[i][1][:50]}")
        key, rest = m.group(1).strip('"'), (m.group(2) or "").strip()
        if key in out:
            raise YamlError(f"duplicate key '{key}'")
        if not rest:
            nxt = items[i + 1] if i + 1 < len(items) else None
            if nxt and (nxt[0] > indent or (nxt[0] == indent and is_dash(nxt[1]))):
                val, i = parse_block(items, i + 1, nxt[0])
            else:
                val, i = None, i + 1
        else:
            val, i = parse_scalar(rest), i + 1
        out[key] = val
    if i < len(items) and items[i][0] > indent:
        raise YamlError(f"unexpected indentation near: {items[i][1][:40]}")
    return out, i


def parse_yaml(block):
    items = []
    for raw in block.splitlines():
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise YamlError("tab used for indentation")
        if raw.strip() and not raw.strip().startswith("#"):
            items.append((len(raw) - len(raw.lstrip(" ")), raw.strip()))
    if not items:
        return {}
    val, i = parse_block(items, 0, items[0][0])
    if i < len(items) or not isinstance(val, dict):
        raise YamlError("frontmatter must be a mapping")
    return val


def loose(block):
    """Fallback reader for files the strict parser reports as unsupported."""
    return {m.group(1): m.group(2) for l in block.splitlines() if (m := re.match(r"([A-Za-z_][\w-]*):\s*(.*)$", l))}


def read(text, where, errs, warns):
    m = FM.match(text)
    if not m:
        return None
    try:
        return parse_yaml(m.group(1))
    except Unsupported as e:
        warns.append(f"{where}: unsupported YAML construct ({e}), checked loosely")
        return loose(m.group(1))
    except YamlError as e:
        errs.append(f"{where}: unparseable frontmatter: {e}")
        return BROKEN


def times(fm):
    """Yield (label, value) for every time-valued key the spec defines."""
    for k in ("timestamp", "stale_after"):
        if k in fm:
            yield k, fm[k]
    g = fm.get("generated")
    if isinstance(g, dict) and "at" in g:
        yield "generated.at", g["at"]
    v = fm.get("verified")
    for e in [v] if isinstance(v, dict) else (v if isinstance(v, list) else []):
        if isinstance(e, dict) and "at" in e:
            yield "verified.at", e["at"]
    for s in fm.get("sources") if isinstance(fm.get("sources"), list) else []:
        if isinstance(s, dict) and "last_modified" in s:
            yield "sources.last_modified", s["last_modified"]


def concept_dirs(root):
    for d in [root, *sorted(p for p in root.rglob("*") if p.is_dir())]:
        rel = d.relative_to(root).parts
        if any(p.startswith(".") or p == "references" for p in rel):
            continue
        if any(f.suffix == ".md" for f in d.iterdir()):
            yield d


def validate(root, notes=None):
    errs, warns = [], []
    legacy = 0
    for d in concept_dirs(root):
        files = sorted(f for f in d.iterdir() if f.suffix == ".md")
        for need in RESERVED:
            if not (d / need).exists():
                warns.append(f"{d}: missing {need}")
        index_text = (d / "index.md").read_text() if (d / "index.md").exists() else ""
        for f in files:
            text = f.read_text().replace("\r\n", "\n")
            fm = read(text, str(f), errs, warns)
            where = str(f)
            if fm is BROKEN:
                continue
            if f.name not in RESERVED:
                if not SNAKE.fullmatch(f.stem):
                    warns.append(f"{where}: filename not snake_case")
                if fm is None:
                    errs.append(f"{where}: missing frontmatter")
                    continue
                if not str(fm.get("type") or "").strip():
                    errs.append(f"{where}: missing type")
                for k in ("title", "description", "tags"):
                    if k not in fm:
                        warns.append(f"{where}: missing {k}")
                g = fm.get("generated")
                if "generated" in fm and not (isinstance(g, dict) and str(g.get("by") or "").strip()):
                    errs.append(f"{where}: generated needs a non-empty 'by' (spec 5.2)")
                if "timestamp" not in fm and not (isinstance(g, dict) and g.get("at")):
                    warns.append(f"{where}: missing generated.at or timestamp")
                if "timestamp" in fm and "generated" not in fm:
                    legacy += 1
                for label, val in times(fm):
                    if not ISO.fullmatch(str(val or "").strip()):
                        warns.append(f"{where}: {label} is not ISO 8601 with an offset")
                if fm.get("status") and str(fm["status"]).strip() not in STATUS:
                    warns.append(f"{where}: status must be draft, stable or deprecated")
                if f.name not in index_text:
                    warns.append(f"{where}: not linked from {d / 'index.md'}")
            else:
                if fm is None or not str(fm.get("type") or "").strip():
                    warns.append(f"{where}: reserved file should carry a type")
            if f.name == "index.md" and d == root and (not fm or "okf_version" not in fm):
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
                    warns.append(f"{where}: broken link {ref}")
    if legacy and notes is not None:
        notes.append(f"{legacy} concept(s) use the legacy `timestamp` field (OKF v0.1); v0.2 prefers generated.at")
    return errs, warns


def self_test():
    ok = "---\ntype: Note\ntitle: A\ndescription: d\ntags: [a]\ntimestamp: 2026-10-24T10:00:00Z\n---\nbody\n"
    idx = '---\ntype: Bundle Index\ntitle: i\ndescription: d\ntags: [i]\ntimestamp: 2026-10-24T10:00:00Z\nokf_version: "0.2"\n---\n* [A](a_note.md) - d\n'
    log = "---\ntype: Change Log\ntitle: l\ndescription: d\ntags: [l]\ntimestamp: 2026-10-24T10:00:00Z\n---\n## 2026-10-24\n* **Creation**: made.\n"

    def bundle(t, concept):
        r = Path(t)
        (r / "a_note.md").write_text(concept)
        (r / "index.md").write_text(idx)
        (r / "log.md").write_text(log)
        notes = []
        return (*validate(r, notes), notes)

    with tempfile.TemporaryDirectory() as t:
        e, w, n = bundle(t, ok)
        assert (e, w) == ([], []) and len(n) == 1, (e, w, n)
        r = Path(t)
        (r / "Bad-Name.md").write_text("no frontmatter [x](gone.md)\n")
        (r / "no_type.md").write_text("---\ntitle: x\n---\n")
        (r / "log.md").write_text(log + "## yesterday\n")
        e, w = validate(r)
        out = "\n".join(e + w)
        for needle in ("missing frontmatter", "missing type", "not YYYY-MM-DD", "not snake_case", "not linked"):
            assert needle in out, (needle, out)

    good = "---\ntype: Note\ntitle: A\ndescription: d\ntags: [a]\ngenerated: { by: human:me, at: 2026-10-24T10:00:00Z }\nsources:\n  - id: s\n    resource: https://x.example\n    last_modified: 2026-05-30T00:00:00Z\n---\n"
    with tempfile.TemporaryDirectory() as t:
        e, w, n = bundle(t, good)
        assert (e, w, n) == ([], [], []), (e, w, n)

    # each of these must be caught, none may pass silently
    bad = {
        'title: "unterminated': "unparseable",
        "tags: [a": "unparseable",
        "generated: { by: human:me, at: 2026-10-24T10:00:00Z": "unparseable",
        "description: decision: unquoted colon": "unparseable",
        "type: Other": "duplicate key",
        "generated: { at: 2026-10-24T10:00:00Z }": "needs a non-empty 'by'",
        "generated: { by: human:a, b, at: 2026-10-24T10:00:00Z }": "unparseable",
        "stale_after: soon": "stale_after is not ISO",
        "timestamp: yesterday": "timestamp is not ISO",
        "status: wip": "status must be",
    }
    for line, needle in bad.items():
        concept = f"---\ntype: Note\ntitle: A\ndescription: d\ntags: [a]\n{line}\n---\n"
        with tempfile.TemporaryDirectory() as t:
            e, w, _ = bundle(t, concept)
            assert needle in "\n".join(e + w), (line, e, w)
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    notes = []
    errs, warns = validate(Path(args[0]).resolve(), notes)
    for line in errs:
        print("ERROR  ", line)
    for line in warns:
        print("WARNING", line)
    for line in notes:
        print("NOTE   ", line)
    print(f"{len(errs)} errors, {len(warns)} warnings")
    sys.exit(1 if errs or ("--strict" in sys.argv and warns) else 0)
