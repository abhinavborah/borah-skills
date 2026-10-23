---
name: ste
description: Write or edit technical text in plain, precise English: short sentences, active voice, one idea per sentence, consistent terms. Use for READMEs, setup steps, error messages, specs and any instructions others must follow or translate. Not a compliance check for ASD-STE100, and not for pitch or marketing copy.
---

# Simple technical English

The goal is text that one reader, in a hurry or reading in a second language, cannot misread. This is a practical subset of the ideas behind controlled technical English. It does not claim compliance with ASD-STE100, which has its own rules and a controlled dictionary. For compliance, use the standard itself.

## Rules

**Sentences**
- Instructions: 20 words or fewer. Descriptions: 25 words or fewer.
- One instruction per sentence. One idea per sentence.
- Paragraphs: 6 sentences or fewer. Start with the point.
- Use a period or a comma. Do not use semicolons, em dashes or double hyphens.

**Verbs**
- Steps are commands: "Run the build." Not "You should run the build."
- Prefer the active voice: "The server rejects the request." Not "The request is rejected."
- Use simple tenses. Avoid "has been removed" and "is checking". Write "was removed" or "checks".
- Use the same verb for the same action every time.

**Words**
- Pick one name for each thing and keep it. Do not switch between "repo", "project" and "codebase".
- Use short common words. "Use", not "utilize". "Start", not "initiate".
- Avoid idioms, phrasal verbs with several meanings, and figures of speech.
- Spell out abbreviations on first use unless every reader knows them.
- Do not stack more than three nouns. "Request validation error message" becomes "the error message for request validation".
- Keep articles ("the", "a"). Dropping them makes the reader guess.

**Structure**
- Number steps. Put one action in each.
- Put the condition first: "If the build fails, check the log."
- Put warnings before the step they protect.
- Show the expected result after a step when it is not obvious.
- Use a list or table for three or more parallel items.

## Procedure

1. Read the text and find the reader and the task they must complete.
2. Rewrite sentence by sentence against the rules. Keep the meaning and every fact.
3. Check for lost facts: numbers, names, conditions, units.
4. List the changes you made only if the user asks.

## Example

Before: "The configuration file should be updated by the user before the application is started, otherwise errors might be encountered."

After: "Edit the configuration file. Then start the application. If you skip this step, the application shows errors."
