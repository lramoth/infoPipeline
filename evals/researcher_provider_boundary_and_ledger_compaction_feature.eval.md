# Eval: Researcher Provider Boundary and Ledger Compaction

Purpose
Validate the observable behavior described in `specs/researcher_provider_boundary_and_ledger_compaction_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- file names
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

## Scenario 1: Gemini Success Uses Compact Ledger Output
Given Researcher is configured with Gemini and receives a controlled successful grounded search response with usable source context,
When the pipeline records the successful Researcher result,
Then:
- the Researcher ledger entry contains normalized items
- the Researcher ledger entry contains one bounded provider context area
- equivalent grounding or source context is not duplicated in multiple top-level Researcher output fields
- the Researcher ledger entry remains readable enough to identify the normalized items, provider, model, URL provenance, and available bounded debug context

## Scenario 2: Gemini Context Remains Useful After Compaction
Given Gemini returns search queries, grounding chunks, grounding supports, source titles, and source URLs,
When the successful Researcher output is inspected,
Then:
- bounded non-secret provider context is still available for debugging
- the available context is sufficient for a human to understand how grounded URLs were derived
- compaction does not remove the only visible source/search context needed to debug Gemini grounded search behavior

## Scenario 3: Gemini Normalized URLs Remain Grounded
Given Gemini returns item text and provider-grounded source data in a controlled response,
When Researcher produces normalized items,
Then:
- normalized item URLs come from provider-grounded source data when available
- normalized items contain title, URL, and summary
- Researcher validation accepts at least 3 complete normalized items
- the pipeline may continue to Curator

## Scenario 4: Gemini Does Not Expose Duplicate Top-Level Grounding Metadata
Given Gemini Researcher succeeds and provider context is already available in the compact provider context area,
When the Researcher output is inspected,
Then:
- equivalent Gemini grounding or source metadata is not repeated in a separate top-level field
- URL provenance remains visible without comparing duplicate metadata sections
- downstream stages still receive normalized items

## Scenario 5: OpenAI Behavior Remains Unchanged
Given Researcher is configured with OpenAI and receives controlled valid or invalid web-search responses,
When the pipeline processes those responses,
Then:
- OpenAI request behavior remains governed by the existing OpenAI Researcher contract
- OpenAI response parsing remains governed by the existing OpenAI Researcher contract
- OpenAI diagnostics and readable failure reasons remain governed by the existing OpenAI Researcher contract
- OpenAI ledger behavior remains unchanged except where existing OpenAI specs already require behavior
- Gemini-specific raw response handling and ledger compaction do not change OpenAI behavior

## Scenario 6: Provider-Specific Behavior Is Isolated
Given Researcher is configured with Gemini or OpenAI,
When provider-specific success and failure responses are processed,
Then:
- Gemini-specific grounded-search normalization does not change OpenAI behavior
- OpenAI-specific web-search handling does not change Gemini behavior
- each provider failure remains readable and provider-aware when provider context is available
- unsupported providers still produce a readable unsupported-provider error

## Scenario 7: Shared Researcher Validation Remains Provider-Neutral
Given Researcher output from any supported provider contains fewer than 3 complete items or items missing title, URL, or summary,
When Researcher validation evaluates the output,
Then:
- the output is rejected
- the rejection reason is readable
- invalid Researcher output is not allowed to advance to Curator

## Scenario 8: Downstream Contract Remains Stable
Given Researcher succeeds with normalized items from a supported provider,
When Curator, Writer, and Delivery run with controlled successful inputs,
Then:
- Curator receives normalized Researcher items
- Curator does not need to parse provider-specific raw response data
- Writer receives Curator output through the existing Writer contract
- Delivery runs only after all configured stages succeed
- downstream output contracts are unchanged

## Scenario 9: Researcher Failure Halts Later Stages
Given a provider-specific Researcher path fails because of a provider call, malformed provider response, missing source context, item normalization failure, or invalid normalized output,
When the pipeline processes that failure,
Then:
- the run fails at Researcher
- the failure reason is readable and provider-aware when provider context is available
- Curator does not run
- Writer does not run
- delivery does not run
- the current ledger records the Researcher failure without stale later-stage records

## Scenario 10: Diagnostics Remain Best-Effort
Given a provider-specific Researcher path fails and diagnostic preservation succeeds,
When the diagnostic is inspected,
Then:
- the diagnostic contains the failed stage
- the diagnostic contains readable provider context when available
- the diagnostic contains bounded non-secret response or search context when available

Given diagnostic preservation fails,
When the pipeline records the failed Researcher run,
Then:
- the original Researcher failure is still reported normally
- the failed stage remains recorded as failed
- the original failure reason remains visible
- diagnostic-preservation failure does not replace or obscure the original failure

## Scenario 11: Secrets And Bounds
Given Researcher runs while provider credentials and environment values are configured,
When user-visible errors, ledger entries, and diagnostics are inspected,
Then:
- API keys are not exposed
- authentication headers are not exposed
- tokens are not exposed
- chat IDs are not exposed
- `.env` values are not exposed
- endpoint URLs do not contain secrets
- raw provider response records and previews remain bounded rather than unbounded payload dumps

## Scenario 12: Automated Tests Avoid Live External Calls
Given the feature has been implemented,
When the repository's automated implementation tests are run,
Then:
- Gemini successful compact ledger behavior is covered with controlled provider responses
- Gemini grounded URL behavior remains covered with controlled provider responses
- OpenAI behavior remains covered with controlled provider responses
- provider-neutral Researcher validation remains covered
- downstream contract behavior remains covered
- Researcher failure and diagnostic behavior remain covered
- no live Gemini, OpenAI, Ollama, Telegram, web search, or other external endpoint call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
