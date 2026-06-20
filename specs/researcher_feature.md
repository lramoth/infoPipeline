# Spec: Researcher

Reference `architecture.md` for system context. This spec covers only the
Researcher — the raw data collector. The Researcher spec does not implement Planner, Curator, or Writer 

## What to build
- The Researcher uses the Gemini API search-related endpoint to gather raw data from a websearch. 
- The Researcher is coordinated by the Planner and is the first step in the pipeline. 
- The Researcher recieves no input from the Planner. 
- When the Researcher is runs by the Planner it prompts the Gemini API search and returns a list of items and the associated grounding metadata associated with those items (from Gemini API search)
- Grounding metadata returned by Gemini is preserved and returned with the research items when available.
- The Researcher searches for items published within the previous 7 days.

## Item Definition
- A research item contains a title, url, and summary.

## Output Validation Failures
- Less than 3 items exist.
- If any of the items is missing a title, url, or summary.
- Errors from the Gemini API search.

## Output Validation Success
The output is considered valid when:
- At least 3 items exist.
- Every item contains a title, url, and summary.

## Prompt for Gemini API search
```
You are a research assistant finding current techno production news.

Search for recent news (last 7 days) about:
- Techno record labels and new releases (Polegroup-adjacent labels especially: Polegroup and similar minimal/hypnotic/raw aesthetic)
- New hardware releases like synths, drum machines, sequencers. (Companies like Roland, Elektron, Korg, Moog and Eurorack manufacturers are good candidates)
- Notable techno artist news (new EPs,  label signings — not festival lineups or general EDM news)

Respond with ONLY a JSON array, no other text, no markdown formatting, no 
code fences. Each item must have exactly these fields:

[
  {"title": "short headline", "url": "https://...", "summary": "one sentence"}
]

If you find fewer than 3 genuinely relevant items, return only the ones that 
are real and relevant — do not invent items to reach a count.
```

## Out of Scope
- This spec is only for the Researcher stage and does not include behaviors for the Planner, Curator, or Writer stages.
