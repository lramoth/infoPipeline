# Spec: Latest Run Ledger and OpenAI Researcher Debuggability

## Objective
Each pipeline invocation should leave a ledger that represents only the latest run, and OpenAI-backed research should be easier to debug when the provider returns no usable research items.

## Background
A configured OpenAI run produced confusing evidence because the ledger still contained results from an earlier run. This made it appear that Researcher had produced valid items for the failed run even though OpenAI's run log showed an empty model response array.

The OpenAI Researcher path also depends on provider web search. If web search is optional or source context is not requested using the current provider contract, a successful-looking provider call can produce weak or empty output that is hard to diagnose.

## Requirements
- At the start of each pipeline invocation, the ledger for the selected output location shall be cleared for the new run.
- The latest ledger shall contain only stage and delivery records produced by the latest invocation.
- Previous stage records, previous delivery records, and previous diagnostic pointers shall not remain in the latest ledger after a new run starts.
- The ledger shall still be written after each stage result, so a partially failed latest run remains inspectable.
- Profile-specific ledger isolation shall remain unchanged: separate profiles shall continue to write to separate profile-specific output locations.
- The ledger shall continue to record the selected profile when a profile is used.
- Existing diagnostic files do not need to be deleted when a new run starts, but the latest ledger shall not point to diagnostics from earlier runs.

## OpenAI Researcher Search Behavior
- When Researcher is configured to use OpenAI, the request shall require OpenAI web search rather than leaving web search optional.
- When the OpenAI API offers documented source or search context for web search responses, the Researcher request shall ask for that context.
- OpenAI Researcher diagnostics and ledger-visible failure reasons shall identify OpenAI and the configured model when that context is available.
- OpenAI Researcher behavior shall not expose API keys, authentication headers, tokens, chat IDs, or environment values in diagnostics, logs, or user-visible errors.
- Automated tests for OpenAI Researcher behavior shall use controlled responses and shall not call live OpenAI endpoints.

## Empty Research Output Behavior
- If Researcher receives a model response that contains no research items, the pipeline shall fail at Researcher.
- A zero-item Researcher result shall not be allowed to advance to Curator.
- The failure reason shall be readable and shall make clear that no research items were produced.
- Local diagnostic information for a zero-item Researcher result shall preserve enough bounded provider-output context for a human to see that the model produced no usable items.
- When raw model text is available for a zero-item Researcher result, diagnostics shall include a bounded preview of that raw text.
- When provider search metadata or source context is available for a zero-item Researcher result, diagnostics shall include bounded non-secret search/source context.
- Existing Researcher validation for item count and required fields shall not be weakened.

## Behavior

### Latest Run Ledger
1. A caller starts a pipeline invocation.
2. Any existing ledger at that run's ledger location is replaced with a new latest-run ledger.
3. As stages complete or fail, the ledger records only results from that invocation.
4. If the run fails before later stages or delivery execute, the ledger contains no stale records for those skipped stages or delivery providers.

### OpenAI Researcher With Usable Items
1. Researcher is configured with OpenAI.
2. Researcher makes an OpenAI request that requires web search.
3. OpenAI returns usable research items.
4. Researcher returns the existing Researcher output contract, including items and available provider metadata.
5. The pipeline continues only if the existing Researcher validation rules pass.

### OpenAI Researcher With Zero Items
1. Researcher is configured with OpenAI.
2. OpenAI returns a response that contains an empty research item list.
3. The pipeline records a Researcher failure in the latest ledger.
4. Curator and later stages do not run.
5. A diagnostic record is written on a best-effort basis with bounded non-secret context about the empty provider output.

## Validation

### Success Conditions
- Running the pipeline twice on the same day leaves the ledger containing only records from the second run.
- If the second run fails before Writer or delivery, the latest ledger contains no stale Writer or delivery records from the first run.
- Separate profile runs continue to use separate ledger/output locations.
- OpenAI Researcher requests require provider web search.
- OpenAI Researcher requests ask for documented web-search source context when available.
- A valid OpenAI Researcher response with enough complete items still passes the existing Researcher output contract.
- An OpenAI Researcher response with zero items fails at Researcher with a readable reason.
- Curator does not run after a zero-item Researcher result.
- Diagnostics for a zero-item Researcher result include bounded non-secret provider-output context when available.
- Automated tests cover the behavior without live Gemini, OpenAI, Ollama, or Telegram calls.

### Failure Conditions
- The latest ledger retains stale stage or delivery records from an earlier invocation.
- A zero-item Researcher result advances to Curator.
- OpenAI Researcher can complete a provider request without requiring web search.
- Diagnostics or user-visible errors expose API keys, authentication headers, tokens, chat IDs, or environment values.

## Out of Scope
- Changing Researcher topic prompts.
- Changing Curator ranking behavior.
- Retrying failed Researcher, Curator, Writer, or delivery stages.
- Deleting historical diagnostic files.
- Sending diagnostics to Telegram or any external system.
- Running live OpenAI, Gemini, Ollama, or Telegram calls in automated tests.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in `AGENTS.md`.
