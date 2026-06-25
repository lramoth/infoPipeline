# Spec: Gemini Raw Search Normalization

## Objective
Gemini-backed Researcher runs should preserve the provider's raw grounded search response for debugging while producing a normalized JSON research item list for the rest of the pipeline.

## Background
Gemini grounded search responses contain provider-owned metadata such as search queries, grounding chunks, grounding support spans, source titles, and source URLs. Previous approaches asked Gemini to emit final item URLs directly inside generated JSON, which can produce guessed or broken URLs. A later approach copied URLs from grounding metadata, but item-to-source matching remained fragile because it depended on generated JSON text and provider support spans lining up cleanly.

This feature separates two concerns:
- Preserve the provider response in an inspectable form so a human can see what Gemini returned.
- Convert Gemini's grounded response into the existing Researcher item contract before downstream stages run.

## Requirements
- The raw search normalization behavior in this spec shall apply only when Researcher is configured with the Gemini provider.
- When Researcher is configured with Gemini, the Researcher output recorded in the ledger shall include an inspectable representation of the raw Gemini search response.
- The raw Gemini search response recorded in the ledger shall preserve provider search context when available, including search queries, grounding chunks, grounding supports, source titles, and source URLs.
- The raw Gemini search response recorded in the ledger shall be bounded and sanitized so secrets and unbounded provider payloads are not exposed.
- Gemini-backed Researcher shall normalize the provider response into JSON research items before the Researcher stage is considered successful.
- Normalized research items shall preserve the existing downstream contract: each item has a title, URL, and summary.
- URLs in normalized Gemini research items shall come from provider-grounded source data when provider-grounded source data is available.
- Gemini-backed Researcher shall not require Gemini to directly generate final URL strings inside item JSON when grounded source URLs are available in provider metadata.
- Curator, Writer, and Delivery behavior shall remain unchanged: they continue to receive the normalized Researcher item list, not the raw provider response as their primary input.
- Existing provider selection behavior shall remain unchanged for non-Gemini providers.
- Non-Gemini Researcher providers shall continue to use their existing provider-specific response parsing, diagnostics, validation, and ledger behavior unless a separate provider-specific spec changes them.

## Ledger Behavior
- A successful Gemini-backed Researcher ledger entry shall make both the raw provider search response and the normalized item output inspectable.
- The normalized item output shall be the authoritative Researcher output for validation and downstream stages.
- The raw provider search response shall be diagnostic context, not a replacement for normalized items.
- The ledger shall make it clear when normalized item URLs were derived from provider-grounded source data.
- If the Gemini response contains provider source metadata but no usable normalized items can be produced, the failed Researcher ledger entry shall include a readable failure reason and a diagnostic path when diagnostic preservation succeeds.

## Error Behavior
- If the Gemini provider call fails, the pipeline shall fail at Researcher with a readable provider failure reason and shall not advance to Curator.
- If the Gemini response cannot be interpreted as a usable provider response, the pipeline shall fail at Researcher with a readable malformed-response reason and shall not advance to Curator.
- If Gemini returns no usable search/source context, the pipeline shall fail at Researcher with a readable reason and shall not advance to Curator.
- If normalized item creation fails, the pipeline shall fail at Researcher with a readable item-normalization reason and shall not advance to Curator.
- If normalized JSON item creation fails, the pipeline shall fail at Researcher with a readable structured-output reason and shall not advance to Curator.
- If fewer than 3 normalized items with title, URL, and summary can be produced, the pipeline shall fail at Researcher with a readable insufficient-items reason and shall not advance to Curator.
- If any normalized item lacks a title, URL, or summary, the Researcher output shall fail validation and the pipeline shall not advance to Curator.
- If diagnostic preservation fails, the original Researcher failure shall still be reported normally.

## Security
- Do not write API keys, authentication headers, Telegram tokens, chat IDs, `.env` values, or other secrets into the ledger or diagnostics.
- Do not write full unbounded request or response bodies into the ledger or diagnostics.
- Provider response previews or raw-response records shall be capped to a fixed size.
- Endpoint URLs in ledger entries and diagnostics shall not include secrets.

## Behavior

### Successful Gemini Researcher Run
1. Researcher is configured with Gemini.
2. Gemini returns a successful grounded search response with usable source context.
3. The Researcher ledger entry records bounded non-secret raw provider search context.
4. Researcher produces normalized JSON items with title, URL, and summary.
5. Each normalized item URL is grounded in provider source data when provider source data is available.
6. Researcher validation passes only if at least 3 complete normalized items exist.
7. Curator receives the normalized item list and the pipeline continues normally.

### Malformed Gemini Response
1. Researcher is configured with Gemini.
2. Gemini returns a successful HTTP response that does not contain the expected provider response content or source context.
3. The pipeline fails at Researcher.
4. The ledger records the Researcher failure with a readable reason.
5. A diagnostic record is written on a best-effort basis with bounded non-secret provider response context when available.
6. Curator and later stages do not run.

### Item Normalization Failure
1. Researcher is configured with Gemini.
2. Gemini returns provider search/source context, but normalized items cannot be created from it.
3. The pipeline fails at Researcher with a readable reason.
4. The ledger and diagnostic context preserve enough bounded non-secret information for a human to understand whether the failure was caused by missing titles, missing summaries, missing source URLs, malformed generated content, or insufficient usable items.
5. Curator and later stages do not run.

### Existing Non-Gemini Researcher Behavior
1. Researcher is configured with a non-Gemini provider.
2. The provider-specific Researcher behavior remains governed by the existing provider specs.
3. The new Gemini raw-response normalization behavior does not weaken existing validation or diagnostic safety requirements.
4. The new Gemini raw-response normalization behavior does not require non-Gemini providers to record raw provider responses or change their normalized item creation behavior.

## Validation

### Success Conditions
- A Gemini Researcher response with usable grounded source context produces at least 3 normalized items with title, URL, and summary.
- Normalized Gemini item URLs come from provider-grounded source data when provider-grounded source data is available.
- A successful Gemini Researcher ledger entry includes both normalized items and bounded non-secret raw provider search context.
- Curator receives normalized Researcher items and does not need to parse raw Gemini provider response data.
- Existing Researcher validation still rejects outputs with fewer than 3 complete items.
- Existing Curator, Writer, and Delivery behavior remains unchanged.
- Non-Gemini Researcher providers keep their existing provider-specific behavior.
- Automated tests cover the behavior without live Gemini, OpenAI, Ollama, Telegram, or other external calls.

### Failure Conditions
- Gemini-backed Researcher succeeds without producing normalized JSON items.
- Gemini-backed Researcher succeeds with item URLs that are not grounded in available provider source data.
- Gemini-backed Researcher advances to Curator after malformed provider response content, failed item normalization, failed JSON item creation, missing source context, insufficient item count, or missing required item fields.
- The ledger or diagnostics expose API keys, authentication headers, tokens, chat IDs, `.env` values, or unbounded provider payloads.
- Curator, Writer, or Delivery must parse raw Gemini provider response data to operate normally.
- A non-Gemini Researcher provider changes response parsing, diagnostics, validation, or ledger behavior because of this Gemini-specific feature.

## Out of Scope
- Changing Curator ranking or filtering behavior.
- Changing Writer formatting behavior.
- Changing Delivery behavior.
- Changing provider selection or profile selection behavior.
- Retrying failed provider calls.
- Live URL fetching or independent source validation.
- Scoring multiple source candidates for the same item.
- Running live Gemini, OpenAI, Ollama, Telegram, or other external calls in automated tests.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in `AGENTS.md`.
