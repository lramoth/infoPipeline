# Eval: Configured Model Endpoints

Purpose
Validate the observable behavior described in `specs/configured_model_endpoints_feature.md`.

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

Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for provider responses and runtime checks.

## Scenario 1: Default Pipeline Declares Model Endpoints

Given the default pipeline configuration is present,
When the default pipeline configuration is inspected and loaded,
Then:
- Researcher has a configured model endpoint
- Curator has a configured model endpoint
- Writer has a configured model endpoint
- all configured model endpoints are non-empty text values
- loading succeeds without requiring source-level endpoint defaults

## Scenario 2: Gemini Endpoints Are Configuration-Owned

Given Researcher and Curator are configured for Gemini,
When the configured stages are assembled and run with controlled provider responses,
Then:
- Researcher attempts to contact the Gemini endpoint declared in configuration
- Curator attempts to contact the Gemini endpoint declared in configuration
- both stages preserve their existing observable output contracts
- changing the Gemini endpoint requires only changing configuration for the next assembled run

## Scenario 3: OpenAI Endpoints Are Configuration-Owned

Given Researcher and Curator are configured for OpenAI,
When the configured stages are assembled and run with controlled provider responses,
Then:
- Researcher attempts to contact the OpenAI endpoint declared in configuration
- Curator attempts to contact the OpenAI endpoint declared in configuration
- both stages preserve their existing observable output contracts
- changing the OpenAI endpoint requires only changing configuration for the next assembled run

## Scenario 4: Writer Endpoint Remains Configuration-Owned

Given Writer is configured for Ollama,
When the configured Writer runs with valid curated items and controlled model-generated prose,
Then:
- Writer attempts to contact the Ollama endpoint declared in configuration
- Writer preserves its existing observable outbound-message contract
- changing the Ollama endpoint requires only changing configuration for the next assembled run

## Scenario 5: Missing Endpoint Fails Configuration Loading

Given a configured model-backed stage model object does not include an endpoint,
When the pipeline configuration is loaded,
Then:
- loading fails
- a readable configuration error is reported
- the stage is not assembled with an implicit source-level endpoint fallback
- no provider call is attempted

Evaluate this behavior for Researcher, Curator, and Writer.

## Scenario 6: Invalid Endpoint Fails Configuration Loading

Given a configured model-backed stage model object includes an empty or non-text
endpoint,
When the pipeline configuration is loaded,
Then:
- loading fails
- a readable configuration error is reported
- the stage is not assembled with an implicit source-level endpoint fallback
- no provider call is attempted

Evaluate this behavior for at least one model-backed stage, and include both an
empty endpoint and a non-text endpoint.

## Scenario 7: Source-Level Endpoint Fallbacks Are Removed

Given the current Researcher and Curator stage behavior is reviewed,
When endpoint selection behavior is evaluated,
Then:
- Researcher requires an endpoint to be supplied by configuration or explicit construction
- Curator requires an endpoint to be supplied by configuration or explicit construction
- Researcher does not fall back to an embedded Gemini or OpenAI service endpoint
- Curator does not fall back to an embedded Gemini or OpenAI service endpoint

## Scenario 8: Provider Failure Diagnostics Use Configured Endpoint Safely

Given a configured provider call fails,
When diagnostic or error context is produced for the failed stage,
Then:
- the reported endpoint matches the configured endpoint used for the attempted call
- the selected provider remains identifiable when provider context is available
- the configured model remains identifiable when model context is available
- API keys, tokens, authentication headers, and environment values are not exposed

## Scenario 9: Existing Provider Support Remains Unchanged

Given configured endpoints have been implemented,
When Gemini, OpenAI, and Ollama behavior is exercised with controlled provider responses,
Then:
- Researcher still supports Gemini and OpenAI
- Curator still supports Gemini and OpenAI
- Writer still supports Ollama only
- unsupported provider combinations still fail with readable errors
- existing stage output contracts remain unchanged

## Scenario 10: Automated Tests Avoid Live External Calls

Given configured model endpoints have been implemented,
When the repository's automated implementation tests are run,
Then:
- configured endpoint behavior is covered with controlled inputs or mocked provider responses
- missing and invalid endpoint failures are covered
- no live Gemini, OpenAI, Ollama, Telegram, or other external endpoint call is required

## Grading instructions

For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
