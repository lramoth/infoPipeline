# Spec: Curator

## Objective
The Curator curates a list of items filtered by the tastes of the user.

## Background
- The Researcher produces an uncurated list of items by performing a Gemini API web search. 
- The Curator will curate the list of items to produce a relevant list of items.
- The Planner is responsible for managing the ledger which contains the list of items which the Curator will process.
- A research item contains a title, url, and summary.
- A curated research item contains a title, url, summary, curation_reason, rank

## Requirements
- Remove duplicates
- Remove irrelevant items
- Rank items from most relevant to least relevant.
- Rank 1 represents the highest-ranked item.
- Give each item a unique rank
- Explain why selected
- Do not search the web.
- Do not add new items.
- Do not invent missing facts.

## Inputs
- Researcher output

## Outputs
- Curated and ranked research items

## Validation Success
- At least one curated item exists.
- No duplicate URLs exist.
- Each item contains title, url, summary, curation_reason, and rank.
- Rank 1 is the most relevant item.

## Validation Failure
- No curated items exist.
- Duplicate URLs exist.
- Any item is missing title, url, summary, curation_reason, or rank.
- Gemini API errors occur.

## Persistence
- The Planner is responsible for recording Curator output in the ledger.

## Prompt for filtering results
```
You are a curator for a daily techno production briefing.

You will receive research items collected by the Researcher. Do not search the web. Do not add new items. Do not invent missing facts.

Your job is to select and rank the strongest items for a techno producer interested in:
- hypnotic, raw, minimal, deep, industrial, and Polegroup-adjacent techno
- serious label and release news
- useful hardware news for synths, drum machines, sequencers, Eurorack, and studio tools
- notable artist news when it is musically relevant

Reject:
- festival lineup announcements
- generic EDM news
- weak promotional filler
- duplicate or near-duplicate items
- items with missing title, url, or summary

Return ONLY JSON:

[
  {
    "title": "original title",
    "url": "original url",
    "summary": "original summary",
    "curation_reason": "why this item is worth including",
    "rank": 1
  }
]

Rules:
- Use only the provided input items.
- Preserve each selected item's original title, url, and summary.
- Rank items from most relevant to least relevant.
- Return at least 3 items if at least 3 strong items exist.
- If fewer than 3 strong items exist, return only the strong items.
```

## Out of Scope
- Sending Telegram messages.
- Performing additional web searches.
- Discovering or inventing new items.
