# Eval: Curator

Purpose
Validate the observable behavior described in `specs/curator_feature.md`.

Do not grade implementation details such as: 
- class names
- method names 
- dataclasses
- validation-result shapes
- internal data structures.

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live external API calls.
- Do not modify external systems.
- Do not send emails, messages, or notifications.
- Use mocks, fixtures, or controlled test inputs.

## Scenario 1: Valid curated items
Given items have been curated,
When at least one item exists, no URLs are duplicated, each item contains title, url, summary, curation_reason, and rank, and rank 1 exists,
Then:
- validation passes

## Scenario 2: Empty item list
Given items have been curated,
When 0 items exist,
Then:
- validation fails

## Scenario 3: Duplicate urls
Given items have been curated,
When multiple items contain identical url,
Then:
- validation fails

## Scenario 4: Incomplete item data
Given items have been curated,
When an item is missing a title, url, summary, curation_reason, or rank
Then:
- validation fails

## Scenario 5: Gemini API error
Given the Curator sends researcher items to Gemini,
When the Gemini API returns an error,
Then:
- the run fails
- an error is reported

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
