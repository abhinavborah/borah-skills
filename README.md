# borah-skills

A plugin marketplace with one plugin, `hack-kit`: skills for setting up and running a hackathon project.

## Docs location

Handoffs, journal entries, research notes and specs go to a docs home outside the repo by default (`../<repo-name>.docs/`). The plugin asks before it writes into a tracked tree. See the `okf-docs` skill.

## Install

```shell
claude plugin marketplace add abhinavborah/borah-skills
claude plugin install hack-kit@borah-skills
```

Restart Claude Code after installing. Skills appear as `/hack-kit:<skill>`.

### Codex

```shell
codex plugin marketplace add abhinavborah/borah-skills
codex plugin add hack-kit@borah-skills
python3 ~/.codex/plugins/cache/borah-skills/hack-kit/*/scripts/install_codex_agents.py
```

The last line installs the three orchestrate subagents as Codex custom agents (`~/.codex/agents/hack_kit_*.toml`), because Codex plugins cannot ship agents. Rerun it after an update. To remove everything:

```shell
python3 ~/.codex/plugins/cache/borah-skills/hack-kit/*/scripts/install_codex_agents.py --uninstall
codex plugin remove hack-kit@borah-skills
codex plugin marketplace remove borah-skills
```

Skills use `${CLAUDE_SKILL_DIR}` and AskUserQuestion; each skill tells Codex what to use instead. `orchestrate` has a Codex section for subagents and herdr sessions. Claude-only features (ghost mode's `.claude/settings.json` attribution, `submit-pack` trace collection from Claude Code) do nothing in Codex.

## Skills

| Skill | Use it to |
|---|---|
| `scaffold` | Set up a project: git, `docs/` bundle, rules file, researched stack, optional GitHub repo and ghost mode. Manual only, asks before creating anything. |
| `okf-docs` | Write and validate the `docs/` folder as an OKF v0.2 bundle. |
| `research` | Run dated, sourced research. Tests which tools work, falls back when one fails, saves a note. |
| `project-log` | Record decisions, findings, changes and rejected approaches in `docs/journal/`. |
| `session-handoff` | Write a timestamped handoff for the next session or for one subagent. |
| `orchestrate` | Split work into packets with disjoint file ownership, in a worktree per packet or one shared tree. Up to 5 subagents, reports in files, ownership gate. |
| `spec-interview` | Turn an idea into a testable spec, or stress-test a plan. |
| `contract-check` | Number the organizer's rules as MUST and SHOULD items, flag conflicts, recheck before submitting. |
| `eval-harness` | Seeded dev and holdout split, plus a guard against reading gold labels in production code. |
| `submit-pack` | Deadline readout, clean-clone check, archive, trace collection from every worktree folder, bundle scan. |
| `demo-pitch` | Prepare the demo, pitch and submission, including a UI polish pass for the demo path. |

### Ghost mode

`scaffold` can keep agent traces out of a project. The user picks all levels or a few: `attribution`, `untracked`, `neutral-code`, `neutral-docs`, `checker`. See [docs/design.md](docs/design.md).

## Layout

```
.claude-plugin/    Claude Code plugin and marketplace manifests
.codex-plugin/     Codex plugin manifest (kept in sync by lint)
.agents/plugins/   Codex marketplace manifest
skills/<name>/     one SKILL.md per skill, with optional references/ and scripts/
agents/            packet-worker, packet-worker-shared and reviewer, used by orchestrate
scripts/lint.py    skill, prose and manifest linter, run in CI on every push
scripts/install_codex_agents.py  turns agents/*.md into Codex custom agents
docs/design.md     how the skills are structured and why
```

## Develop

```shell
python3 scripts/lint.py                 # lint every skill and all prose
python3 scripts/lint.py --self-test     # test the linter
claude plugin validate .                # manifest, skills, agents
claude plugin validate .claude-plugin/marketplace.json
```

No version is pinned in `plugin.json`, so every commit reaches installers as a new version. See [docs/design.md](docs/design.md).

## License

MIT. See [LICENSE](LICENSE).
