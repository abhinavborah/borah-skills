# borah-skills

A plugin marketplace with one plugin, `hack-kit`: skills for setting up and running a hackathon project.

## Install

```shell
claude plugin marketplace add abhinavborah/borah-skills
claude plugin install hack-kit@borah-skills
```

Restart Claude Code after installing. Skills appear as `/hack-kit:<skill>`.

## Skills

| Skill | Use it to |
|---|---|
| `scaffold` | Set up a project: git, `docs/` bundle, rules file, researched stack, optional GitHub repo and ghost mode. Manual only, asks before creating anything. |
| `okf-docs` | Write and validate the `docs/` folder as an OKF v0.2 bundle. |
| `research` | Run dated, sourced research. Tests which tools work, falls back when one fails, saves a note. |
| `session-handoff` | Write a timestamped handoff for the next session or for one subagent. |
| `orchestrate` | Split work into packets with disjoint file ownership, dispatch up to 5 subagents, gate the merge. |
| `spec-interview` | Turn an idea into a testable spec, or stress-test a plan. |
| `spike` | Answer one design question with disposable code. |
| `test-first` | Build features test-first, or fix bugs by reproducing them first. |
| `ste` | Write plain, precise technical English. |
| `better-ui` | Audit and polish a web interface, details and motion included. |
| `demo-pitch` | Prepare the demo, pitch and submission. |

### Ghost mode

`scaffold` can keep agent traces out of a project. The user picks all levels or a few: `attribution`, `untracked`, `neutral-code`, `neutral-docs`, `checker`. See [docs/design.md](docs/design.md).

## Layout

```
.claude-plugin/    plugin and marketplace manifests
skills/<name>/     one SKILL.md per skill, with optional references/ and scripts/
scripts/lint.py    skill linter used before every commit
docs/design.md     how the skills are structured and why
```

## Develop

```shell
python3 scripts/lint.py                 # lint every skill
python3 scripts/lint.py --self-test     # test the linter
claude plugin validate --strict .claude-plugin/plugin.json
claude plugin validate --strict .claude-plugin/marketplace.json
```

## License

MIT. See [LICENSE](LICENSE).
