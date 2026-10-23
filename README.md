# borah-skills

A plugin marketplace with one plugin, `hack-kit`: skills for setting up and running a hackathon project.

## Install

```shell
claude plugin marketplace add abhinavborah/borah-skills
claude plugin install hack-kit@borah-skills
```

Restart Claude Code after installing. Skills appear as `/hack-kit:<skill>`.

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
