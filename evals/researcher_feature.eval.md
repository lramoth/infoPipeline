# Eval: Researcher Feature

These scenarios validate the observable behavior described in `specs/researcher_feature.md`.

Do not grade implementation details such as class names, method names, dataclasses, validation-result shapes, or internal data structures.

## Scenario 1: Successful run
Given a Gemini API search result contains at least 3 valid research items,
When the Researcher runs,
Then:
- it returns the items
- each item contains a title, url, and summary
- it preserves available grounding metadata
- the run is considered valid


## Scenario 2: Too Few Items
Given a Gemini API search result with fewer than 3 items,
When the Researcher runs,
Then:
- the run is considered invalid

## Scenario 3: Incomplete Items
Given a Gemini API search result with at least 3 items with any items missing a title, url or summary,
When the Researcher runs,
Then:
- the run is considered invalid


## Scenario 4: Gemini Errors
Given a Gemini API call which reports an error,
When the Researcher runs,
Then:
- the run is considered invalid
- an error is reported


## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.