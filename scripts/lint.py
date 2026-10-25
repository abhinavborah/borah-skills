#!/usr/bin/env python3
"""Lint skills/*/SKILL.md and repo prose.

Usage: lint.py [repo_root]    lint every skill (default: parent of scripts/)
       lint.py --self-test    check the linter against built-in fixtures

Rules (limits come from the Claude Code skills docs and the authoring guide):
  name        matches directory, [a-z0-9-]{1,64}, no "claude" or "anthropic"
  description present, single line; description + when_to_use <= 1536 chars
  body        <= 500 lines
  links       relative links resolve; reference files do not link onward
  prose       no em dash and no spaced double hyphen in .md, .json, .py or .yml files
"""
import re
import sys
import tempfile
from pathlib import Path

DESC_CAP = 1536
BODY_CAP = 500
EM_DASH = chr(0x2014)
SPACED_DOUBLE = " " + "-" * 2 + " "
LINK = re.compile(r"\]\((?!https?:|mailto:|#)([^)#\s]+)")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fm[k.strip()] = v.strip().strip("\"'")
    return fm, m.group(2)


def lint_skill(skill_dir):
    errs = []
    path = skill_dir / "SKILL.md"
    fm, body = frontmatter(path.read_text())
    if fm is None:
        return [f"{path}: missing frontmatter"]
    name = fm.get("name", "")
    if name != skill_dir.name:
        errs.append(f"{path}: name '{name}' must equal directory '{skill_dir.name}'")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name) or re.search(r"claude|anthropic", name):
        errs.append(f"{path}: invalid name '{name}'")
    desc = fm.get("description", "")
    if not desc or desc in (">", "|", ">-", "|-"):
        errs.append(f"{path}: description must be a single line")
    if len(desc) + len(fm.get("when_to_use", "")) > DESC_CAP:
        errs.append(f"{path}: description + when_to_use exceed {DESC_CAP} chars")
    if len(body.splitlines()) > BODY_CAP:
        errs.append(f"{path}: body over {BODY_CAP} lines")
    for md in skill_dir.rglob("*.md"):
        for ref in LINK.findall(CODE.sub("", md.read_text())):
            target = (md.parent / ref).resolve()
            if not target.exists():
                errs.append(f"{md}: broken link {ref}")
            elif md.name != "SKILL.md" and target.suffix == ".md" and skill_dir in target.parents and target.name != "SKILL.md":
                errs.append(f"{md}: reference links onward to {ref} (keep references one level deep)")
    return errs


def lint_prose(root):
    errs = []
    for f in [*root.rglob("*.md"), *root.rglob("*.json"), *root.rglob("*.py"), *root.rglob("*.yml")]:
        if ".git" in f.parts:
            continue
        t = f.read_text()
        if EM_DASH in t or SPACED_DOUBLE in t:
            errs.append(f"{f}: em dash or spaced double hyphen")
    return errs


def lint_readme(root):
    readme = root / "README.md"
    if not readme.exists() or not (root / "skills").is_dir():
        return []
    listed = set(re.findall(r"^\| `([a-z0-9-]+)` \|", readme.read_text(), re.M))
    actual = {d.name for d in (root / "skills").iterdir() if d.is_dir()}
    return [f"{readme}: skill table lists {sorted(listed - actual)} not in skills/" for _ in [0] if listed - actual] + [f"{readme}: skills/ has {sorted(actual - listed)} missing from the skill table" for _ in [0] if actual - listed]


def lint(root):
    errs = lint_prose(root) + lint_readme(root)
    for d in sorted((root / "skills").glob("*/")):
        if (d / "SKILL.md").exists():
            errs += lint_skill(d)
        else:
            errs.append(f"{d}: missing SKILL.md")
    return errs


def self_test():
    def make(base, name, fm_extra="", body="ok\n", fname="SKILL.md"):
        d = base / "skills" / name
        d.mkdir(parents=True)
        (d / fname).write_text(f"---\nname: {name}\ndescription: does a thing\n{fm_extra}---\n{body}")
        return d

    with tempfile.TemporaryDirectory() as t:
        good = Path(t) / "good"
        make(good, "alpha")
        assert lint(good) == [], lint(good)

    with tempfile.TemporaryDirectory() as t:
        bad = Path(t) / "bad"
        d = make(bad, "claude-x", body="\n" * 600)
        (d / "ref.md").write_text("see [other](other.md)\n")
        (d / "other.md").write_text("x\n")
        d2 = make(bad, "beta", body="[gone](nope.md) and a " + EM_DASH + " dash\n")
        (d2 / "SKILL.md").write_text((d2 / "SKILL.md").read_text().replace("name: beta", "name: wrong"))
        (bad / "README.md").write_text("| `ghost` | x |\n| `beta` | x |\n")
        out = "\n".join(lint(bad))
        assert "not in skills/" in out and "missing from the skill table" in out, out
        for needle in ("invalid name", "body over", "broken link", "must equal directory", "em dash"):
            assert needle in out, (needle, out)
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    problems = lint(root.resolve())
    print("\n".join(problems) or "lint ok")
    sys.exit(1 if problems else 0)
