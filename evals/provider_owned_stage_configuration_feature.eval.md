# Eval: Provider-Owned Stage Configuration

Purpose
Validate the observable behavior described in `specs/provider_owned_stage_configuration_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- file names
- validation-result shapes
- internal data structures
- HTTP client implementation choices
- parsing algorithms

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment

Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Bandcamp, Telegram, or other
  external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for configuration, provider
  responses, and runtime checks.

## Scenario 1: Stage Provider Is Declared At Stage Level

Given a pipeline configuration defines Researcher, Curator, and Writer stages,
And each stage declares its provider at the stage level,
When the pipeline configuration is loaded,
Then:
- loading succeeds when each selected provider is supported for its stage
- each stage is configured with the selected provider
- no stage runs during configuration loading

## Scenario 2: Missing Stage Provider Is A Configuration Error

Given a configured Researcher, Curator, or Writer stage does not declare a
stage-level provider,
When the pipeline configuration is loaded,
Then:
- configuration loading fails
- the failure reason is readable
- no stage runs

## Scenario 3: Model-Backed Provider Requirements

Given Researcher or Curator is configured for Gemini or OpenAI,
Or Writer is configured for Ollama,
When the pipeline configuration is loaded,
Then:
- loading succeeds when the selected provider has a configured model name and
  endpoint
- the configured model name and endpoint are preserved for that stage
- loading fails with a readable error when the selected provider is missing a
  required model name
- loading fails with a readable error when the selected provider is missing a
  required endpoint

## Scenario 4: Unsupported Provider Combinations

Given a stage is configured with a provider not supported by that stage,
When the pipeline configuration is loaded or the stage is run,
Then:
- the operation fails
- the failure reason is readable
- no successful provider response is reported

Evaluate at least:
- Researcher with a provider other than Gemini, OpenAI, or Bandcamp
- Curator with a provider other than Gemini or OpenAI
- Writer with a provider other than Ollama

## Scenario 5: Prompt And Template Requirements Are Provider-Owned

Given a prompt-using provider is selected for a stage,
When the selected profile omits the prompt path required by that provider,
Then:
- configuration loading fails
- the failure reason is readable
- no stage runs

Given Writer is configured for Ollama,
When the selected profile omits the Writer template path,
Then:
- configuration loading fails
- the failure reason is readable
- no stage runs

## Scenario 6: Existing Model-Backed Providers Remain Available

Given Researcher and Curator are configured for Gemini or OpenAI using the new
stage-level provider configuration,
And Writer is configured for Ollama using the new stage-level provider
configuration,
When the pipeline is assembled and controlled successful provider responses are
used,
Then:
- Gemini Researcher behavior remains available
- OpenAI Researcher behavior remains available
- Gemini Curator behavior remains available
- OpenAI Curator behavior remains available
- Ollama Writer behavior remains available
- existing Researcher, Curator, and Writer validation rules still apply

## Scenario 7: Bandcamp Researcher Loads With Provider Only

Given Researcher is configured with only `provider: bandcamp`,
And the selected profile does not declare a Researcher prompt path,
When the pipeline configuration is loaded,
Then:
- loading succeeds
- Researcher is configured for Bandcamp
- no model name is required
- no endpoint is required
- no API credential is required
- no Researcher prompt content is required

## Scenario 8: Bandcamp Ignores Unused Researcher Prompt Paths

Given Researcher is configured for Bandcamp,
And the selected profile declares Researcher prompt paths that Bandcamp does
not use,
When the pipeline configuration is loaded,
Then:
- loading succeeds
- the unused Researcher prompt paths do not affect the Bandcamp run
- missing unused Researcher prompt files do not prevent Bandcamp configuration
  from loading

## Scenario 9: Bandcamp Request Contract

Given Researcher is configured for Bandcamp,
And a controlled Bandcamp response is available,
When Researcher runs,
Then the outbound Bandcamp request uses:
- `POST https://bandcamp.com/api/discover/1/discover_web`
- `category_id` set to `0`
- `tag_norm_names` set to `["hypnotic-techno", "techno"]`
- `geoname_id` set to `0`
- `slice` set to `"new"`
- `time_facet_id` set to `0`
- `cursor` set to `"*"`
- `size` set to `24`
- `include_result_types` set to `["a", "s"]`

## Scenario 10: Bandcamp Normalizes Successful Results

Given Researcher is configured for Bandcamp,
And Bandcamp returns at least three controlled results that can produce a title,
URL, and summary,
When Researcher runs,
Then:
- Researcher succeeds
- Researcher output contains at least three items
- each returned item has a title, URL, and summary
- returned URLs do not contain Bandcamp discovery tracking query parameters
- existing Researcher validation accepts the output
- bounded non-secret source context is available when diagnostics or ledger
  inspection need provider context

## Scenario 11: Bandcamp Skips Incomplete Results

Given Researcher is configured for Bandcamp,
And Bandcamp returns a controlled response containing some results that cannot
produce a title, URL, or summary,
When Researcher runs,
Then:
- incomplete source results are not returned as Researcher items
- complete source results are still returned when present
- if fewer than three complete items remain, the Researcher stage fails through
  a readable Researcher error or existing Researcher validation failure

## Scenario 12: Bandcamp Failure Handling

Given Researcher is configured for Bandcamp,
When Bandcamp is unavailable, returns malformed data, or returns an empty result
set,
Then:
- the Researcher stage fails
- the failure reason is readable
- no Curator, Writer, or delivery success is reported from invalid Bandcamp
  output
- diagnostics, logs, and user-visible error context do not expose API keys,
  authentication headers, tokens, or environment values

## Scenario 13: No Extra Bandcamp Configuration Is Exposed

Given Researcher is configured for Bandcamp,
When the pipeline configuration is loaded,
Then:
- user-configurable Bandcamp tags are not required
- user-configurable Bandcamp slice is not required
- user-configurable Bandcamp time facet is not required
- user-configurable Bandcamp cursor is not required
- user-configurable Bandcamp result types are not required
- user-configurable Bandcamp size is not required
- user-configurable Bandcamp endpoint is not required

## Scenario 14: Automated Tests Avoid Live External Calls

Given provider-owned stage configuration has been implemented,
When the repository's automated implementation tests are run,
Then:
- stage-level provider selection is covered with controlled configuration
- provider-specific model requirements are covered with controlled
  configuration
- provider-specific prompt and template requirements are covered with
  controlled configuration
- Bandcamp successful responses are covered with controlled provider responses
- Bandcamp malformed, empty, or insufficient responses are covered with
  controlled provider responses
- no live Gemini, OpenAI, Ollama, Bandcamp, Telegram, web search, or other
  external endpoint call is required

## Grading instructions

For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
