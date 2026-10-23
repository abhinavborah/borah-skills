# Research tools

Match by capability. Names below are examples and vary per install.

## Routing

| Question | Try in this order |
|---|---|
| Library or framework docs, API syntax | context7, then the official docs site via firecrawl or curl |
| Latest stable version of a package | the registry (commands below), then the release page |
| General web, comparisons, how-tos | firecrawl search, exa, web search |
| Academic papers, methods | alphaxiv, then firecrawl search with the research category |
| What people say recently (Reddit, X, YouTube, HN) | the `last30days` skill |
| Gov, legal, regulatory | firecrawl search with the gov category |
| A specific known URL | firecrawl scrape (markdown format), or curl |

## Probes

One cheap call each. Examples:

- firecrawl: search with `limit: 1`
- exa: search with `numResults: 1`
- alphaxiv: discover with one keyword
- context7: resolve a library id for a well-known library
- web search: any simple query
- last30days: confirm the skill is listed, then run its own doctor or health check if it has one

A probe passes when it returns a result. It fails on an error, a timeout, a missing tool, or a credit or auth message. Quote the shortest line that says why.

## Version checks

```shell
v=$(npm view <pkg> dist-tags.latest)      # the stable tag, not canary or next
npm view <pkg> time.$v                     # its release date
curl -s https://pypi.org/pypi/<pkg>/json   # info.version, releases
gh api repos/<owner>/<repo>/releases/latest --jq '.tag_name,.published_at'
```

Report the version, its release date, and whether the project is still maintained (recent commits and releases). Do not suggest a legacy or end-of-life version unless the user asks for it.

## Cost notes

Search and scrape tools may spend credits. Probe with one result. Do not fetch many pages to answer something a highlight already answers.
