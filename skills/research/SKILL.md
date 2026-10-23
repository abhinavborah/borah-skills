---
name: research
description: Dated, sourced research using the best available tools (firecrawl, exa, alphaxiv, last30days, context7, web search). Tests which tools work first, tells the user, falls back when one fails, and saves a note to docs/research/. Use for library or stack choices, best-practice checks, prior art and anything that needs current facts. Not for reading the local codebase.
---

# Research

Facts go stale. Every note records when it was checked and where each claim came from.

## 1. Preflight

Before the first real query:

1. Find what exists. Tool names differ per setup, so match by capability, not by name. Deferred tools load through ToolSearch. `last30days` is a skill, so look for it in the skill list instead.
2. Probe each tool once with the cheapest real call (one result, a harmless query). Record ok or failed with the shortest decisive error.
3. Tell the user in a short table: tool, status, what it will be used for. Do this before continuing, and ask only if no general search tool works at all.

Tool details and the order to try them: [references/tools.md](references/tools.md).

## 2. Search

- Route by question type using the table in [references/tools.md](references/tools.md).
- Search first and read result highlights. Fetch a page only when a highlight is not enough.
- For a long docs page, fetch the raw `.md` or text with `curl` into a temp file and filter it with `grep`. Do not load whole pages into context.
- Avoid firecrawl scrape with the `query` format. It failed on 5 of 5 pages in testing (2026-10) and still charged credits. Use markdown format or curl instead, and re-test before trusting it.
- Check versions at the source of truth (registry or release page), not in blog posts.

## 3. When a tool fails

Say which tool failed and why, in one line. Try the next tool in the order. Record the failure in the note's tool log. Do not retry the same call more than once.

## 4. Judge the sources

- Prefer primary sources: official docs, specs, papers, repositories.
- Mark each claim by strength: primary source, multiple independent sources, single source, vendor or promotional, opinion.
- Paraphrase. Do not copy tables or text from third-party sources, and note any license limits.
- Record the retrieval date, and the publish date when known. If a source is older than a year and the topic moves fast, say so.

## 5. Save and report

1. Write the note with the template in [references/note.md](references/note.md) to `docs/research/<topic>.md`, using the `okf-docs` skill for frontmatter, index, log and validation.
2. If the project has `docs/journal/`, record the conclusion that drives a choice with the `project-log` skill, linking the note.
3. Report the findings to the user in plain language, with links. When the research feeds a choice (library, algorithm, stack), present the options and a recommendation, and wait for the user's decision before acting on it.
