# Eval: Gemini Raw Search Normalization

Purpose
Validate the observable behavior described in `specs/gemini_raw_search_normalization_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- HTTP client implementation choices
- parsing algorithms
- validation-result shapes
- internal data structures
- ledger storage algorithms

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for provider responses and runtime checks.

## Scenario 1: Gemini Success Produces Normalized Items
Given Researcher is configured with Gemini and receives a controlled successful grounded search response with usable source context,
When the pipeline processes that response,
Then:
- Researcher succeeds
- the Researcher output contains normalized research items
- at least 3 normalized items are present
- each normalized item contains a non-empty title, URL, and summary
- Researcher validation accepts the output
- the pipeline may continue to Curator

## Scenario 2: Gemini URLs Come From Grounded Source Data
Given Gemini returns item text and provider-grounded source URLs in the same controlled response,
When Researcher produces normalized items,
Then:
- normalized item URLs come from the provider-grounded source data
- Gemini-typed or guessed URL strings are not required for successful normalization when grounded source URLs are available
- the Researcher output makes clear that item URLs were derived from grounded provider data

## Scenario 3: Raw Gemini Search Context Is Inspectable
Given Gemini returns provider search context such as search queries, grounding chunks, grounding supports, source titles, and source URLs,
When Researcher succeeds and the ledger records the Researcher output,
Then:
- the Researcher ledger entry includes normalized items
- the Researcher ledger entry includes bounded non-secret raw provider search context
- the raw provider context includes available search/source information useful for human debugging
- the normalized items remain the authoritative output for validation and downstream stages

## Scenario 4: Curator Receives Normalized Items
Given a Gemini-backed Researcher run succeeds with normalized items and raw provider context,
When Curator runs after Researcher,
Then:
- Curator receives the normalized item list as its research input
- Curator does not need to parse raw Gemini provider response data
- Curator behavior remains consistent with the existing curation contract

## Scenario 5: Malformed Gemini Provider Response Fails At Researcher
Given Gemini returns a successful HTTP response that lacks usable provider response content or has an improper response shape,
When the pipeline processes that response,
Then:
- the run fails at Researcher
- the failure reason is readable
- Curator does not run
- Writer does not run
- delivery does not run
- a diagnostic record is written when diagnostic preservation succeeds
- available provider response context is bounded and non-secret

## Scenario 6: Missing Gemini Source Context Fails At Researcher
Given Gemini returns generated item text but no usable search or source context,
When the pipeline processes that response,
Then:
- the run fails at Researcher
- the failure reason clearly indicates that usable source context is missing
- no normalized item output is allowed to advance to Curator
- a diagnostic record is written when diagnostic preservation succeeds
- bounded provider context is preserved when available

## Scenario 7: Item Normalization Failure Fails At Researcher
Given Gemini returns source context but normalized research items cannot be created from the provider response,
When the pipeline processes that response,
Then:
- the run fails at Researcher
- the failure reason is readable
- the failure context is sufficient for a human to understand whether the issue involved missing titles, missing summaries, malformed generated content, missing source URLs, or insufficient usable items
- Curator and later stages do not run

## Scenario 8: Insufficient Normalized Item Count Fails At Researcher
Given Gemini returns fewer than 3 usable normalized items with title, URL, and summary,
When the pipeline validates Researcher output,
Then:
- Researcher output is rejected
- the rejection reason is readable
- Curator and later stages do not run
- the ledger records the Researcher failure for the current run

## Scenario 9: Required Item Fields Are Still Enforced
Given Researcher output contains items missing a title, URL, or summary,
When Researcher validation evaluates the output,
Then:
- the output is rejected
- the rejection reason is readable
- invalid Researcher output is not allowed to advance to Curator

## Scenario 10: Non-Gemini Researcher Behavior Is Unchanged
Given Researcher is configured with a non-Gemini provider,
When the provider returns controlled valid or invalid responses governed by existing provider behavior,
Then:
- the new Gemini raw-search normalization behavior does not change non-Gemini response parsing
- the new Gemini raw-search normalization behavior does not require non-Gemini providers to record raw provider responses
- existing non-Gemini diagnostics, validation, and ledger behavior remain intact

## Scenario 11: Existing Curator, Writer, And Delivery Behavior Remain
Given the pipeline receives valid normalized Researcher items,
When Curator, Writer, and Delivery run with controlled successful inputs,
Then:
- Curator still ranks and filters according to the existing Curator contract
- Writer still formats from curated items according to the existing Writer contract
- Delivery still sends only after all configured stages succeed
- the new Gemini raw provider context does not alter downstream output contracts

## Scenario 12: Secrets And Payload Bounds
Given Gemini Researcher runs while provider credentials and environment values are configured,
When user-visible errors, ledger entries, and diagnostics are inspected,
Then:
- API keys are not exposed
- authentication headers are not exposed
- tokens are not exposed
- chat IDs are not exposed
- `.env` values are not exposed
- endpoint URLs do not contain secrets
- raw provider response records and previews are bounded rather than unbounded payload dumps

## Scenario 13: Diagnostic Preservation Failure Does Not Obscure Original Failure
Given Gemini Researcher encounters a malformed response, missing source context, or item normalization failure,
When diagnostic preservation fails,
Then:
- the original Researcher failure is still reported normally
- the failed stage is still recorded as failed
- the original failure reason remains visible
- the diagnostic-preservation failure does not replace or obscure the original failure

## Scenario 14: Automated Tests Avoid Live External Calls
Given the feature has been implemented,
When the repository's automated implementation tests are run,
Then:
- Gemini success with grounded source context is covered with controlled provider responses
- missing source context is covered with controlled provider responses
- malformed response or item-normalization failure behavior is covered with controlled provider responses
- existing validation and downstream contract behavior remain covered
- non-Gemini provider behavior remains covered
- no live Gemini, OpenAI, Ollama, Telegram, web search, or other external endpoint call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
