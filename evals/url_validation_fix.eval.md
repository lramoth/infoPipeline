# Eval: Exact URL Uniqueness Validation

Purpose
Validate the observable behavior described in `specs/url_validation_fix.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- validation-result shapes
- internal data structures.

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment

Unless explicitly required by the spec:
- Do not perform live Gemini, Telegram, Ollama, or other external API calls.
- Do not perform web searches.
- Do not resolve redirects.
- Do not fetch canonical URLs.
- Do not modify external systems.
- Use mocks, fixtures, or controlled test inputs.

## Scenario 1: Distinct Complete URLs
Given curated items contain all required fields and include rank 1,
When every curated item has a distinct complete URL value,
Then:
- validation passes

## Scenario 2: Same Domain, Different URLs
Given curated items contain all required fields and include rank 1,
When multiple curated item URLs share the same domain but have different complete URL values,
Then:
- validation passes
- validation does not fail because of the shared domain

## Scenario 3: Same Path Prefix, Different URLs
Given curated items contain all required fields and include rank 1,
When multiple curated item URLs share the same path prefix but have different complete URL values,
Then:
- validation passes
- validation does not fail because of the shared path prefix

## Scenario 4: Distinct Gemini Grounding Redirect URLs
Given curated items contain all required fields and include rank 1,
When multiple curated item URLs are Gemini grounding redirect URLs with the same redirect prefix but different complete URL values,
Then:
- validation passes
- validation does not fail because the URLs are visually similar Gemini grounding redirect URLs

## Scenario 5: Distinct Long Redirect Tokens
Given curated items contain all required fields and include rank 1,
When multiple curated item URLs differ only by long redirect tokens in the complete URL value,
Then:
- validation passes
- validation compares the complete URL value rather than truncated URL previews

## Scenario 6: Exact Duplicate URLs
Given curated items contain all required fields and include rank 1,
When two or more curated items contain the same complete URL value,
Then:
- validation fails
- the failure reason identifies the duplicate URL
- the failure reason identifies the affected item ranks or titles

## Scenario 7: Existing Required Fields Validation
Given curated items are missing title, url, summary, curation_reason, or rank,
When validation runs,
Then:
- validation fails according to the existing required-fields behavior

## Scenario 8: Existing Rank Validation
Given curated items contain all required fields and no duplicate complete URL values,
When no curated item has rank 1,
Then:
- validation fails according to the existing rank requirement

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
