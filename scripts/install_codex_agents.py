#!/usr/bin/env python3
"""Install the hack-kit subagents into Codex as custom agents.

Codex plugins cannot ship subagents. This script turns agents/*.md (the
Claude Code definitions, the single source) into Codex TOML files named
hack_kit_<name>.toml, so the two hosts never drift.

Usage: install_codex_agents.py [--dest DIR]            install (default $CODEX_HOME/agents, else ~/.codex/agents)
       install_codex_agents.py --uninstall [--dest DIR]
       install_codex_agents.py --self-test

Codex custom agents inherit the parent's model, permissions and MCP servers,
so Claude-only keys (model, tools, disallowedTools, maxTurns, isolation) are
dropped. Their intent is kept as text in developer_instructions.
"""
import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "hack_kit_"
WORKTREE_NOTE = (
    "Codex note: Codex has no worktree isolation for subagents. The orchestrator "
    "creates your worktree and gives its absolute path in the brief. Run every "
    "command and edit inside that directory only."
)


def parse(md):
    md = md.replace("\r\n", "\n")
    m = re.match(r"---\n(.*?)\n---\n?(.*)", md, re.S)
    if not m:
        raise ValueError("missing frontmatter")
    fm = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fm[k.strip()] = v.strip().strip("\"'")
    for key in ("name", "description"):
        if fm.get(key, "") in ("", ">", "|", ">-", "|-"):
            raise ValueError(f"frontmatter {key} must be a single-line value")
    return fm, m.group(2).strip()


def to_toml(fm, body):
    if "'''" in body:
        raise ValueError("body contains ''' and cannot be a TOML literal string")
    extra = []
    if fm.get("isolation") == "worktree":
        extra.append(WORKTREE_NOTE)
    if "Edit" in fm.get("disallowedTools", "") or "Write" in fm.get("tools", ""):
        extra.append("Codex note: you are read-only except for the one report file named in your prompt.")
    instructions = "\n\n".join([body, *extra])
    name = PREFIX + fm["name"].replace("-", "_")
    if not re.fullmatch(r"[a-z0-9_]+", name):
        raise ValueError(f"agent name {name!r} is not [a-z0-9_]")
    if instructions.endswith("'"):
        instructions += " "
    return name, f"name = {json.dumps(name)}\ndescription = {json.dumps(fm['description'])}\ndeveloper_instructions = \'\'\'\n{instructions}\n\'\'\'\n"


def install(dest, source=ROOT / "agents"):
    dest.mkdir(parents=True, exist_ok=True)
    uninstall(dest)  # drop agents whose .md was renamed or deleted
    out = []
    for md in sorted(source.glob("*.md")):
        name, toml = to_toml(*parse(md.read_text()))
        (dest / f"{name}.toml").write_text(toml)
        out.append(dest / f"{name}.toml")
    return out


def uninstall(dest):
    gone = sorted(dest.glob(PREFIX + "*.toml"))
    for f in gone:
        f.unlink()
    return gone


def self_test():
    try:
        import tomllib
    except ModuleNotFoundError:
        print("self-test needs Python 3.11+ (tomllib)")
        sys.exit(1)
    with tempfile.TemporaryDirectory() as t:
        dest = Path(t) / "agents"
        files = install(dest)
        assert len(files) == len(list((ROOT / "agents").glob("*.md"))) > 0, files
        for f in files:
            d = tomllib.loads(f.read_text())
            assert set(d) == {"name", "description", "developer_instructions"}, d.keys()
            assert d["name"] == f.stem and d["name"].startswith(PREFIX), d["name"]
        worker = tomllib.loads((dest / f"{PREFIX}packet_worker.toml").read_text())
        assert "no worktree isolation" in worker["developer_instructions"]
        (dest / "other.toml").write_text("x")
        assert len(uninstall(dest)) == len(files) and [p.name for p in dest.iterdir()] == ["other.toml"]
        try:
            to_toml({"name": "x", "description": "d"}, "has ''' inside")
            raise AssertionError("triple quote not rejected")
        except ValueError:
            pass
        name, toml = to_toml({"name": "q", "description": 'say "hi" \\ there'}, "ends with '")
        assert tomllib.loads(toml)["description"] == 'say "hi" \\ there'
        assert parse("---\r\nname: x\r\ndescription: d\r\n---\r\nbody")[0]["name"] == "x"
        try:
            parse("---\nname: x\ndescription: >\n  folded\n---\nb")
            raise AssertionError("folded description not rejected")
        except ValueError:
            pass
    print("self-test ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dest", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "agents")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        sys.exit(0)
    done = uninstall(a.dest) if a.uninstall else install(a.dest)
    print("\n".join(str(p) for p in done) or "nothing to do")
