#!/usr/bin/env python3
"""Create the docs/ OKF bundle for a project. Existing files are never overwritten.

Usage: scaffold_docs.py --root DIR --project NAME [--by ACTOR] [--neutral]
       scaffold_docs.py --self-test

--neutral writes `timestamp` instead of `generated` (ghost level neutral-docs).
--by is the actor for `generated.by`, e.g. human:handle. Defaults to human:unknown.
"""
import importlib.util
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DIRS = {
    "research": "Dated, sourced research notes.",
    "handoffs": "Timestamped session handoffs. The newest file is read first.",
    "subagent-handoffs": "Briefs and reports for dispatched subagents.",
}


def page(kind, title, desc, tags, stamp, body, extra=""):
    return f"---\ntype: {kind}\ntitle: {title}\ndescription: {desc}\ntags: [{tags}]\n{stamp}\n{extra}---\n\n{body}\n"


def build(root, project, by, neutral):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    day = now[:10]
    stamp = f"timestamp: {now}" if neutral else f"generated: {{ by: {by}, at: {now} }}"
    docs = Path(root) / "docs"
    made = []

    def write(path, text):
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            made.append(str(path))

    root_links = "\n".join(f"* [{n}]({n}/) - {d}" for n, d in DIRS.items())
    write(docs / "index.md", page("Bundle Index", project, f"Docs for {project}.", "index", stamp,
                                   f"# {project}\n\n{root_links}", 'okf_version: "0.2"\n'))
    write(docs / "log.md", page("Change Log", f"{project} log", "History of changes to the docs.", "log", stamp,
                                 f"## {day}\n* **Creation**: Initialized the docs bundle."))
    for name, desc in DIRS.items():
        write(docs / name / "index.md", page("Bundle Index", name, desc, "index", stamp, f"# {name}\n\n{desc}"))
        write(docs / name / "log.md", page("Change Log", f"{name} log", f"History of changes in {name}.", "log", stamp,
                                            f"## {day}\n* **Creation**: Created the folder."))
    return made


def self_test():
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("okf", here.parent.parent / "okf-docs" / "scripts" / "okf_validate.py")
    okf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(okf)
    for neutral in (False, True):
        with tempfile.TemporaryDirectory() as t:
            made = build(t, "demo", "human:tester", neutral)
            assert len(made) == 8, made
            assert build(t, "demo", "human:tester", neutral) == [], "must not overwrite"
            errs, warns = okf.validate(Path(t) / "docs")
            assert (errs, warns) == ([], []), (errs, warns)
            body = (Path(t) / "docs" / "index.md").read_text()
            assert ("timestamp:" in body) == neutral and ("generated:" in body) != neutral
    print("self-test ok")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root")
    p.add_argument("--project")
    p.add_argument("--by", default="human:unknown")
    p.add_argument("--neutral", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
    elif args.root and args.project:
        made = build(args.root, args.project, args.by, args.neutral)
        print("\n".join(made) or "nothing to create")
    else:
        p.error("--root and --project are required")
