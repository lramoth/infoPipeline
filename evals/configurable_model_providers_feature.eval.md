# Eval: Configurable Model Providers

Purpose
Validate the observable behavior described in `specs/configurable_model_providers_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- HTTP client implementation choices
- parsing algorithms
- validation-result shapes
- internal data structures.

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment

Unless a scenario explicitly requires live-provider confirmation:
- Do not perform live Gemini, OpenAI, Ollama, Telegram, or other external API calls.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for provider responses and runtime checks.

Live-provider confirmation, when run as a separate evaluation session, may call
the real configured model provider endpoints only for the scenarios that require
genuine provider behavior. Do not call Telegram for this feature evaluation
unless a separate delivery evaluation requires it.

## Scenario 1: Configured Provider Selection

Given pipeline configuration selects Gemini for Researcher, Gemini for Curator,
and Ollama for Writer,
When the pipeline configuration is loaded,
Then:
- loading succeeds
- the configured model names are preserved
- Researcher and Curator remain configured for Gemini
- Writer remains configured for Ollama
- no stage runs during configuration loading

## Scenario 2: OpenAI Researcher And Curator Selection

Given pipeline configuration selects OpenAI for Researcher and Curator and
Ollama for Writer,
When the pipeline configuration is loaded,
Then:
- loading succeeds
- Researcher is configured to use OpenAI with the configured model name
- Curator is configured to use OpenAI with the configured model name
- Writer remains configured to use Ollama
- switching Researcher and Curator from Gemini to OpenAI requires only
  configuration and environment changes

## Scenario 3: Unsupported Provider Combinations

Given a model-backed stage is configured with a provider not supported by that
stage,
When the pipeline configuration is loaded or the stage is run,
Then:
- the operation fails
- a readable error identifies that the configured provider is unsupported
- no successful provider response is reported

Evaluate at least these unsupported combinations:
- Researcher with a provider other than Gemini or OpenAI
- Curator with a provider other than Gemini or OpenAI
- Writer with a provider other than Ollama

## Scenario 4: Gemini Researcher Behavior Remains Available

Given Researcher is configured for Gemini and receives a controlled successful
Gemini provider response containing valid research items,
When Researcher runs,
Then:
- Researcher succeeds
- the returned output contains the research items
- available Gemini grounding metadata is preserved
- existing Researcher validation still passes

## Scenario 5: OpenAI Researcher Behavior

Given Researcher is configured for OpenAI and receives a controlled successful
OpenAI provider response containing valid research items,
When Researcher runs,
Then:
- Researcher succeeds
- the returned output contains the research items
- available OpenAI source or search metadata is preserved when exposed by the
  provider response
- existing Researcher validation still passes
- the behavior does not require source-code changes after configuration and
  environment values are changed

## Scenario 6: Gemini Curator Behavior Remains Available

Given Curator is configured for Gemini and receives a controlled successful
Gemini provider response containing valid curated items,
When Curator runs with Researcher output,
Then:
- Curator succeeds
- the returned output contains the curated items
- existing Curator validation still passes

## Scenario 7: OpenAI Curator Behavior

Given Curator is configured for OpenAI and receives a controlled successful
OpenAI provider response containing valid curated items,
When Curator runs with Researcher output,
Then:
- Curator succeeds
- the returned output contains the curated items
- existing Curator validation still passes
- the behavior does not require source-code changes after configuration and
  environment values are changed

## Scenario 8: Writer Ollama Boundary

Given Writer is configured for Ollama and receives controlled model-generated
item prose,
When Writer runs with valid curated items,
Then:
- Writer succeeds
- the outbound message is assembled from the configured Writer prompt,
  configured Writer template, curated item titles, curated item URLs, and
  model-generated item prose
- existing Writer validation still passes

Given Writer is configured for a provider other than Ollama,
When Writer runs,
Then:
- Writer fails
- a readable error identifies that the configured Writer provider is unsupported

## Scenario 9: Missing Selected-Provider Credentials

Given Researcher or Curator is configured for a provider that requires a
credential,
When the required credential is missing from the project environment
configuration,
Then:
- the stage fails before a successful provider response is expected
- a readable error identifies the missing required credential
- no unrelated provider credential is required for that selected provider

Evaluate at least:
- Gemini-selected Researcher or Curator missing the Gemini credential
- OpenAI-selected Researcher or Curator missing the OpenAI credential
- Writer configured for Ollama without an API key

## Scenario 10: Provider Failures And Diagnostics

Given a configured provider returns a failed response or unavailable-service
condition,
When the affected stage fails,
Then:
- the failure is reported with a readable message
- provider context identifies the selected provider when available
- model context identifies the configured model when available
- diagnostics, logs, and user-visible error context do not expose API keys,
  tokens, authentication headers, or environment values

## Scenario 11: Automated Tests Avoid Live External Calls

Given configurable model providers have been implemented,
When the repository's automated implementation tests are run,
Then:
- provider switching behavior is covered with controlled inputs or mocked
  provider responses
- no live Gemini, OpenAI, Ollama, Telegram, or other external endpoint call is
  required
- the existing stage output contracts remain covered

## Scenario 12: Live Provider Smoke Check

Given a separate evaluation session has real credentials for the configured
model providers,
When Researcher and Curator are each run with the selected live provider
configuration under evaluation,
Then:
- the selected live provider accepts the configured model name
- Researcher can produce valid research output for that provider
- Curator can produce valid curated output for that provider
- the Writer provider boundary remains unchanged
- no Telegram message is sent as part of this provider evaluation

This scenario may be skipped only when live-provider credentials are not
available; if skipped, record that the live-provider confirmation was not run
and do not treat the skip as proof of live-provider behavior.

## Grading instructions

For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
- SKIP only for Scenario 12 when live-provider credentials are unavailable.

Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every non-skipped scenario passes and any skip
is explicitly justified.
