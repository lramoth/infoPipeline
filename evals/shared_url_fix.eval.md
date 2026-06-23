# Eval: Shared Curator Source URLs

Purpose
Validate the observable behavior described in `specs/shared_url_fix.md`.

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
- Do not perform live Gemini, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not resolve redirects.
- Do not fetch canonical URLs.
- Do not modify external systems.
- Use mocks, fixtures, or controlled test inputs.

## Scenario 1: One Complete Curated Item
Given Curator output is a list containing one item,
When the item has non-empty title, url, summary, curation_reason, and rank, and the rank is 1,
Then:
- validation passes

## Scenario 2: Multiple Complete Items With Distinct URLs
Given Curator output is a list containing multiple items,
When every item has non-empty title, url, summary, curation_reason, and rank, at least one item has rank 1, and each URL is distinct,
Then:
- validation passes

## Scenario 3: Multiple Complete Items Sharing One URL
Given Curator output is a list containing multiple distinct items,
When every item has non-empty title, url, summary, curation_reason, and rank, at least one item has rank 1, and two or more items have the same URL value,
Then:
- validation passes
- validation does not fail solely because the URL is repeated
- all items remain present in the curated output
- each item's URL is preserved exactly as provided

## Scenario 4: Non-List Curator Output
Given Curator output is not a list,
When validation runs,
Then:
- validation fails

## Scenario 5: Empty Curated List
Given Curator output is an empty list,
When validation runs,
Then:
- validation fails

## Scenario 6: Missing Required Fields
Given Curator output is a list containing an item missing title, url, summary, curation_reason, or rank,
When validation runs,
Then:
- validation fails

## Scenario 7: Empty Required Fields
Given Curator output is a list containing an item with an empty title, url, summary, curation_reason, or rank,
When validation runs,
Then:
- validation fails

## Scenario 8: No Rank 1 Item
Given Curator output is a list containing one or more otherwise complete items,
When no item has rank 1,
Then:
- validation fails

## Scenario 9: No URL Rewriting Or Canonicalization
Given Curator output is a list containing otherwise complete items with URLs that differ by case, query string, fragment, redirect token, or other exact characters,
When validation runs,
Then:
- validation does not rewrite URLs
- validation does not canonicalize URLs
- validation does not perform network calls to resolve URLs
- validation treats repeated exact URLs as acceptable citations when other requirements are satisfied

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
