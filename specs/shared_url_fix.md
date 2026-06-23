# Spec: Curator Allows Shared Source URLs

## Objective
The Curator should allow multiple distinct curated items to share the same URL when that URL acts as a source citation rather than a unique item identifier.

## Background
A real pipeline run showed multiple distinct curated items sharing the same source URL. Each item had a different title and summary, but all items cited the same source page.
The Curator failed validation because duplicate URLs were not allowed.
For now, URLs should be treated as citations. Shared URLs should not cause Curator validation failure when the curated items themselves are otherwise valid.
This decision may be revisited after observing report quality over time.

## Requirements

- Curator validation shall not fail solely because multiple curated items share the same URL.
- Curator validation shall continue to require every curated item to include a URL.
- Curator validation shall continue to require every curated item to include a title.
- Curator validation shall continue to require every curated item to include a summary.
- Curator validation shall continue to require every curated item to include a curation reason.
- Curator validation shall continue to require every curated item to include a rank.
- Curator validation shall continue to require at least one curated item.
- Curator validation shall continue to require at least one item with rank 1.
- Curator validation shall continue to reject missing required fields.
- Curator validation shall continue to reject empty required fields.
- Curator validation shall continue to reject invalid output shapes.
- The Curator shall preserve each item's URL as provided.
- The Curator shall not remove an item only because its URL appears on another item.

## Inputs
- Curator output containing curated items.
Each curated item contains:
- title
- url
- summary
- curation_reason
- rank

## Outputs
- Curator validation passes for otherwise valid curated items even when URLs repeat.
- Curator validation fails when required fields or rank requirements are not satisfied.

## Behavior

## Success Behavior
- A curated list with one complete item passes validation.
- A curated list with multiple complete items and distinct URLs passes validation.
- A curated list with multiple complete items sharing the same URL passes validation.
- Shared URLs are treated as repeated citations, not duplicate item evidence.

## Failure Behavior
- Curator output that is not a list fails validation.
- An empty curated list fails validation.
- Any item missing title, URL, summary, curation reason, or rank fails validation.
- Any item with an empty title, URL, summary, curation reason, or rank fails validation.
- A curated list with no rank 1 item fails validation.

## Validation Success
- Curator output contains at least one item.
- Every item contains title, URL, summary, curation reason, and rank.
- Every required field is non-empty.
- At least one item has rank 1.
- Repeated URLs do not cause validation failure.

## Validation Failure
- Curator output is not a list.
- Curator output contains no items.
- Any curated item is missing a required field.
- Any required field is empty.
- No item has rank 1.

## Constraints
- Must not change Researcher behavior.
- Must not change Writer behavior.
- Must not change Planner stage ordering.
- Must not remove or rewrite URLs.
- Must not perform URL canonicalization.
- Must not perform network calls to resolve URLs.
- Must not add duplicate-item detection beyond the requirements in this spec.
- Must not require live Gemini, Ollama, Telegram, or other external calls in tests.

## Out of Scope
- Item identity deduplication.
- Canonical URL resolution.
- Redirect following.
- Researcher prompt changes.
- Researcher validation changes.
- Writer formatting changes.
- Telegram delivery.
- Retry behavior.
- Long-term report-quality policy.

## Acceptance Criteria
- Given multiple complete curated items with distinct URLs, Curator validation passes.
- Given multiple complete curated items sharing the same URL, Curator validation passes.
- Given a curated item missing a URL, Curator validation fails.
- Given a curated item with an empty URL, Curator validation fails.
- Given a curated item missing title, summary, curation reason, or rank, Curator validation fails.
- Given an empty curated list, Curator validation fails.
- Given Curator output that is not a list, Curator validation fails.
- Given a curated list with no rank 1 item, Curator validation fails.
- Existing Curator behavior outside URL uniqueness validation remains unchanged.

## Completion

When implementation is complete, append a build log entry to `eval_log.md` following the format in `AGENTS.md`.