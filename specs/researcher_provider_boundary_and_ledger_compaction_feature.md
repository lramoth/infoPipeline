# Spec: Researcher Provider Boundary and Ledger Compaction

## Objective
Researcher output should remain easy to inspect after Gemini grounded-search normalization, and provider-specific Researcher behavior should be isolated so Gemini-specific response handling does not make the shared Researcher stage harder to reason about.

## Background
Gemini raw search normalization made Researcher output more reliable by deriving item URLs from grounded provider source data instead of model-generated URL strings. A live run produced usable links and completed delivery, but the Researcher ledger entry became overly verbose because source context appeared in more than one place.

The current behavior also concentrates provider-specific concerns in the shared Researcher path. Gemini grounded search normalization, Gemini raw-response context, OpenAI search handling, shared stage validation, and provider selection are separate concerns. This feature should preserve the successful behavior while making the ledger easier to read and making provider-specific behavior easier to maintain.

## Requirements
- Successful Researcher output shall continue to include the normalized `items` list as the authoritative downstream contract.
- Successful Researcher output shall avoid duplicating equivalent provider search/source context in multiple top-level locations.
- Successful Gemini-backed Researcher output shall still include bounded non-secret provider context sufficient to debug grounded search behavior.
- Gemini-backed Researcher output shall not include a separate top-level grounding/source metadata field when the same information is already present in the raw provider context.
- The ledger shall remain readable enough for a human to quickly identify:
  - the normalized Researcher items
  - whether URLs came from provider-grounded source data
  - the provider and model used
  - bounded raw or source context for debugging when available
- Curator, Writer, and Delivery shall continue to receive and operate on normalized research items, not provider-specific raw response data.
- Provider-specific Researcher behavior shall be bounded by provider.
- Gemini-specific raw response handling and grounded item normalization shall not change OpenAI Researcher behavior.
- OpenAI-specific web-search request and response behavior shall not change Gemini Researcher behavior.
- Shared Researcher validation shall remain provider-neutral and shall continue to validate the normalized output contract.
- Existing provider selection behavior shall remain unchanged.

## Ledger Behavior
- A successful Gemini-backed Researcher ledger entry shall contain normalized items and one non-duplicative provider context area.
- The provider context area shall identify the provider and configured model when available.
- The provider context area shall contain bounded non-secret raw provider response context or bounded source/search context when available.
- Equivalent search queries, grounding chunks, grounding supports, source titles, and source URLs shall not be repeated in multiple top-level Researcher output fields.
- The ledger shall make URL provenance visible without requiring a human to compare multiple duplicate metadata sections.
- Existing failed-stage diagnostic behavior shall remain unchanged except that duplicated provider context should not be introduced into the ledger.

## Provider Boundary Behavior
- A Gemini-backed Researcher run shall continue to:
  - request Gemini search grounding
  - normalize grounded search output into items with title, URL, and summary
  - use provider-grounded source data for URLs when available
  - preserve bounded Gemini provider context for debugging
- An OpenAI-backed Researcher run shall continue to:
  - use the existing OpenAI web-search behavior
  - return the existing normalized Researcher output contract
  - preserve existing available provider metadata or source context
  - fail with existing readable OpenAI-specific failure reasons
- Shared Researcher behavior shall continue to:
  - select the configured provider
  - expose the same stage interface to Planner
  - validate normalized items consistently across providers
  - report unsupported providers with a readable error

## Error Behavior
- If Gemini provider context cannot be compacted without preserving useful debugging information, the pipeline shall fail safely or preserve the original readable Researcher failure rather than silently dropping required debugging context.
- If a provider-specific Researcher path fails, the failure reason shall still identify the relevant provider when provider context is available.
- If diagnostic preservation fails, the original provider-specific Researcher failure shall still be reported normally.
- Refactoring provider-specific behavior shall not introduce stale ledger records, skipped-stage records, or downstream execution after invalid Researcher output.

## Security
- Ledger entries and diagnostics shall not expose API keys, authentication headers, Telegram tokens, chat IDs, `.env` values, or other secrets.
- Raw provider response records and previews shall remain bounded.
- Endpoint URLs in ledger entries and diagnostics shall not include secrets.
- Compacting the ledger shall not move secrets from diagnostics or provider responses into user-visible output.

## Behavior

### Gemini Success With Compact Ledger
1. Researcher is configured with Gemini.
2. Gemini returns a successful grounded search response with usable source context.
3. Researcher produces normalized items with title, URL, and summary.
4. The Researcher ledger entry records normalized items.
5. The Researcher ledger entry records one bounded provider context area.
6. Equivalent grounding/source context is not duplicated in multiple top-level Researcher output fields.
7. Curator receives normalized items and the pipeline continues normally.

### OpenAI Behavior Remains Provider-Specific
1. Researcher is configured with OpenAI.
2. OpenAI returns a controlled valid or invalid web-search response.
3. Researcher behavior remains governed by the existing OpenAI Researcher contract.
4. Gemini-specific raw response normalization and ledger compaction do not change OpenAI request behavior, response parsing, diagnostics, validation, or ledger behavior.

### Downstream Contract Remains Stable
1. Researcher succeeds with normalized items from any supported provider.
2. Curator receives the normalized Researcher item list.
3. Writer receives Curator output.
4. Delivery runs only after all configured stages succeed.
5. No downstream stage needs to parse provider-specific raw response data.

### Researcher Failure
1. A provider-specific Researcher path fails because of a provider call, malformed provider response, missing source context, item normalization failure, or invalid normalized output.
2. The pipeline fails at Researcher with a readable provider-aware reason when provider context is available.
3. Curator and later stages do not run.
4. A diagnostic record is written when diagnostic preservation succeeds.
5. The ledger remains readable and does not duplicate equivalent provider context.

## Validation

### Success Conditions
- A successful Gemini-backed Researcher run records normalized items and one non-duplicative provider context area in the ledger.
- A successful Gemini-backed Researcher run still makes bounded raw or source context available for debugging.
- Gemini-backed normalized item URLs still come from provider-grounded source data when provider-grounded source data is available.
- A successful Researcher output no longer repeats equivalent Gemini grounding/source context in both top-level grounding metadata and raw provider context.
- Curator receives normalized Researcher items and does not need to parse provider-specific raw response data.
- OpenAI Researcher request behavior, response behavior, diagnostics, validation, and ledger behavior remain unchanged except for behavior explicitly governed by existing OpenAI specs.
- Shared Researcher validation still rejects outputs with fewer than 3 complete items or missing required item fields.
- Automated tests cover the behavior without live Gemini, OpenAI, Ollama, Telegram, or other external calls.

### Failure Conditions
- A successful Gemini-backed Researcher ledger entry contains duplicate equivalent provider source context in multiple top-level fields.
- Ledger compaction removes the only provider context needed to debug Gemini grounded search behavior.
- Gemini-specific response handling changes OpenAI Researcher behavior.
- OpenAI-specific response handling changes Gemini Researcher behavior.
- Curator, Writer, or Delivery must parse provider-specific raw response data to operate normally.
- Invalid Researcher output advances to Curator.
- User-visible errors, ledger entries, or diagnostics expose API keys, authentication headers, tokens, chat IDs, `.env` values, or unbounded provider payloads.

## Out of Scope
- Changing Researcher topic prompts.
- Changing Curator ranking or filtering behavior.
- Changing Writer formatting behavior.
- Changing Delivery behavior.
- Changing provider selection or profile selection behavior.
- Retrying failed provider calls.
- Live URL fetching or independent source validation.
- Scoring multiple source candidates for the same item.
- Changing external provider APIs.
- Running live Gemini, OpenAI, Ollama, Telegram, or other external calls in automated tests.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in `AGENTS.md`.
