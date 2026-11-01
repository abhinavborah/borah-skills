#!/usr/bin/env python3
"""Install the hack-kit subagents into Codex as custom agents.

Codex plugins cannot ship subagents. This script turns agents/*.md (the
Claude Code definitions, the single source) into Codex TOML files named
hack_kit_<name>.toml, so the two hosts never drift.

Usage: install_codex_agents.py [--dest DIR]            install (default ~/.codex/agents)
       install_codex_agents.py --uninstall [--dest DIR]
       install_codex_agents.py --self-test

Codex custom agents inherit the parent's model, permissions and MCP servers,
so Claude-only keys (model, tools, disallowedTools, maxTurns, isolation) are
dropped. Their intent is kept as text in developer_instructions.
"""
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
    m = re.match(r"---\n(.*?)\n---\n?(.*)", md, re.S)
    if not m:
        raise ValueError("missing frontmatter")
    fm = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    return {k.strip(): v.strip() for k, v in fm.items()}, m.group(2).strip()


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
    desc = fm["description"].replace("\\", "\\\\").replace('"', '\\"')
    return name, f'name = "{name}"\ndescription = "{desc}"\ndeveloper_instructions = \'\'\'\n{instructions}\n\'\'\'\n'


def install(dest, source=ROOT / "agents"):
    dest.mkdir(parents=True, exist_ok=True)
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
    import tomllib
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
    print("self-test ok")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-test" in args:
        self_test()
        sys.exit(0)
    dest = Path(args[args.index("--dest") + 1]) if "--dest" in args else Path.home() / ".codex" / "agents"
    done = uninstall(dest) if "--uninstall" in args else install(dest)
    print("\n".join(str(p) for p in done) or "nothing to do")
