#!/usr/bin/env python3
"""Rebuild the link list in every index.md of an OKF bundle from concept frontmatter.

Usage: build_index.py [--check] [--root <bundle_dir>] <dir>
       build_index.py --self-test

Each entry is `* [title](file.md) - description`, taken from the linked file, so the
index cannot drift from the concepts. Subfolders are listed from their own index.md.
Only the block between the okf-index markers is managed; other text in index.md stays.
A missing index.md is created with Bundle Index frontmatter (the root one with
okf_version and the docs-versus-code precedence line).
--check writes nothing and exits 1 when any index is out of date.
--root names the bundle root when <dir> is a subfolder: only <dir>, its subfolders and its
parent indexes are rebuilt, and root-only lines go to the real root. Without --root, a
<dir> whose parent holds an index.md is refused, so a subfolder is never treated as the root.
"""
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python3 -I drops the script dir
from okf_validate import BROKEN, RESERVED, concept_dirs, read  # noqa: E402

START, END = "<!-- okf-index:start -->", "<!-- okf-index:end -->"
BULLET = re.compile(r"^\* \[[^\]]*\]\(([^)#\s]+)\)")
PRECEDENCE = "If this bundle and the code disagree, follow the code and report the mismatch."


def meta(path):
    fm = read(path.read_text().replace("\r\n", "\n"), str(path), [], [])
    fm = fm if isinstance(fm, dict) and fm is not BROKEN else {}
    return str(fm.get("title") or path.stem), " ".join(str(fm.get("description") or "").split())


def entries(d):
    out = []
    for f in sorted(p for p in d.iterdir() if p.suffix == ".md" and p.name not in RESERVED):
        out.append((f.name, *meta(f)))
    for sub in sorted(p for p in d.iterdir() if p.is_dir() and not p.name.startswith(".") and any(p.glob("*.md"))):
        title, desc = meta(sub / "index.md") if (sub / "index.md").exists() else (sub.name, "")
        out.append((f"{sub.name}/index.md", title if title != "index" else sub.name, desc))
    return out


def render(d, root):
    lines = [f"* [{t}]({link})" + (f" - {desc}" if desc else "") for link, t, desc in entries(d)]
    return "\n".join([START, *lines, END])


def new_index(d, root):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    top = d == root
    fm = ["---", "type: Bundle Index", f"title: {d.name}", f"description: Index of {d.name}.",
          "tags: [index]", f"timestamp: {now}", *(['okf_version: "0.2"'] if top else []), "---", ""]
    return "\n".join(fm + ([PRECEDENCE, ""] if top else []))


def rebuild(text, block, managed):
    if START in text and END in text:
        pre, rest = text.split(START, 1)
        return pre + block + rest.split(END, 1)[1]
    # first run: drop hand-written bullets for managed targets, keep everything else
    kept = [ln for ln in text.splitlines() if not (BULLET.match(ln) and BULLET.match(ln).group(1) in managed)]
    return "\n".join(kept).rstrip("\n") + "\n\n" + block + "\n"


def guard(target, root, explicit_root):
    """Return an error message when target cannot be built as asked, else None."""
    if target != root and root not in target.parents:
        return f"{target} is not inside --root {root}"
    if not explicit_root and (target.parent / "index.md").exists():
        return f"{target} looks like a subfolder ({target.parent / 'index.md'} exists); run on the bundle root or pass --root <bundle root>"
    return None


def build(root, check=False, target=None):
    target = target or root
    stale = []
    # deepest first, so a parent lists the index its child just got
    dirs = [d for d in concept_dirs(root) if d == target or target in d.parents or d in target.parents]
    for d in sorted(dirs, key=lambda p: -len(p.parts)):
        idx = d / "index.md"
        text = idx.read_text() if idx.exists() else new_index(d, root)
        managed = {link for link, _, _ in entries(d)}
        out = rebuild(text, render(d, root), managed)
        if out != text or not idx.exists():
            stale.append(idx)
            if not check:
                idx.write_text(out)
    return stale


def self_test():
    note = "---\ntype: Note\ntitle: Alpha\ndescription: First note.\n---\nbody\n"
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        (r / "alpha.md").write_text(note)
        (r / "sub").mkdir()
        (r / "sub" / "beta.md").write_text(note.replace("Alpha", "Beta"))
        assert len(build(r, check=True)) == 2 and not (r / "index.md").exists(), "check must not write"
        build(r)
        root_idx = (r / "index.md").read_text()
        assert "* [Alpha](alpha.md) - First note." in root_idx and "](sub/index.md)" in root_idx, root_idx
        assert 'okf_version: "0.2"' in root_idx and PRECEDENCE in root_idx, root_idx
        assert "* [Beta](beta.md)" in (r / "sub" / "index.md").read_text()
        assert build(r, check=True) == [], "second run must be a no-op"
        (r / "alpha.md").write_text(note.replace("First note.", "Changed."))
        assert build(r, check=True) == [r / "index.md"]
        build(r)
        assert "Changed." in (r / "index.md").read_text()
        # hand-written bullets are replaced, other prose and unmanaged links stay
        (r / "index.md").write_text("---\ntype: Bundle Index\n---\n\nIntro.\n\n* [Old](alpha.md) - stale\n* [PDF](report.pdf) - keep\n")
        build(r)
        out = (r / "index.md").read_text()
        assert "Intro." in out and "[PDF](report.pdf)" in out and "[Old]" not in out and out.count("alpha.md") == 1, out

    # a subfolder run is refused without --root; with it, root-only lines stay at the real root
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        (r / "alpha.md").write_text(note)
        build(r)
        sub = r / "handoffs"
        sub.mkdir()
        (sub / "h.md").write_text(note.replace("Alpha", "Gamma"))
        assert "looks like a subfolder" in (guard(sub, sub, False) or "")
        assert guard(sub, r, True) is None and "not inside" in (guard(r, sub, True) or "")
        build(r, target=sub)
        sub_idx = (sub / "index.md").read_text()
        assert "okf_version" not in sub_idx and PRECEDENCE not in sub_idx and "[Gamma](h.md)" in sub_idx, sub_idx
        assert "](handoffs/index.md)" in (r / "index.md").read_text()
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    argv = sys.argv[1:]
    root = None
    if "--root" in argv:
        i = argv.index("--root")
        if i + 1 >= len(argv):
            sys.exit(__doc__)
        root = Path(argv.pop(i + 1)).resolve()
        argv.pop(i)
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    target = Path(args[0]).resolve()
    err = guard(target, root or target, root is not None)
    if err:
        sys.exit("build_index.py: " + err)
    check = "--check" in argv
    stale = build(root or target, check, target)
    for p in stale:
        print(("out of date: " if check else "updated: ") + str(p))
    sys.exit(1 if check and stale else 0)
