# Eval: Provider-Specific Researcher Prompt Paths

Purpose
Validate the observable behavior described in `specs/provider_specific_researcher_prompts_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- file names
- validation-result shapes
- internal data structures
- HTTP client implementation choices
- model provider client implementation choices

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for configuration and runtime checks.

## Scenario 1: Gemini Provider Selects Gemini Researcher Prompt
Given a profile defines provider-specific Researcher prompt paths for Gemini and OpenAI,
And the configured Researcher provider is Gemini,
When the default pipeline is assembled,
Then:
- Researcher receives the Gemini-specific Researcher prompt path
- the selected prompt path points to an existing prompt file
- the fallback Researcher prompt path is not selected instead of the Gemini-specific path

## Scenario 2: OpenAI Provider Selects OpenAI Researcher Prompt
Given a profile defines provider-specific Researcher prompt paths for Gemini and OpenAI,
And the configured Researcher provider is OpenAI,
When the default pipeline is assembled,
Then:
- Researcher receives the OpenAI-specific Researcher prompt path
- the selected prompt path points to an existing prompt file
- the fallback Researcher prompt path is not selected instead of the OpenAI-specific path

## Scenario 3: Missing Provider-Specific Prompt Falls Back
Given a profile defines the existing Researcher prompt path,
And the profile does not define a provider-specific prompt path for the configured Researcher provider,
When the default pipeline is assembled,
Then:
- Researcher receives the existing Researcher prompt path
- pipeline assembly succeeds when the fallback prompt file exists
- a missing provider-specific prompt path for that provider does not prevent fallback

## Scenario 4: Existing Profiles Continue To Load
Given a profile defines only the existing Researcher prompt path and no provider-specific Researcher prompt paths,
When the default pipeline is assembled,
Then:
- pipeline assembly succeeds when the existing prompt file exists
- Researcher receives the existing Researcher prompt path
- no provider-specific prompt configuration is required for existing profiles

## Scenario 5: Missing Selected Provider Prompt Is A Configuration Error
Given a profile defines a provider-specific Researcher prompt path for the configured Researcher provider,
And the selected provider-specific prompt file does not exist,
When the default pipeline is assembled,
Then:
- configuration loading fails
- the failure reason is readable
- no pipeline stages are executed
- the missing selected prompt does not silently fall back to another prompt

## Scenario 6: Unconfigured Provider Prompt Is Ignored
Given a profile defines a provider-specific Researcher prompt path for a provider that is not configured for the Researcher stage,
And the profile also defines the existing Researcher prompt path,
When the default pipeline is assembled,
Then:
- the unconfigured provider's prompt path does not affect the selected run
- the configured provider selects its own provider-specific prompt when available
- otherwise the configured provider falls back to the existing Researcher prompt path

## Scenario 7: Other Stage Paths Remain Unchanged
Given a profile defines provider-specific Researcher prompt paths,
When the default pipeline is assembled,
Then:
- Curator receives its configured Curator prompt path
- Writer receives its configured Writer prompt path
- Writer receives its configured template path
- stage order remains unchanged
- model provider selection remains unchanged
- delivery configuration remains unchanged

## Scenario 8: Provider Prompt Selection Does Not Change Provider Behavior
Given the configured Researcher provider is changed between Gemini and OpenAI,
When the default pipeline is assembled,
Then:
- the configured Researcher provider is still passed to Researcher
- the configured model name is still passed to Researcher
- the configured endpoint is still passed to Researcher
- only the Researcher prompt path changes according to provider-specific prompt selection

## Scenario 9: Automated Tests Avoid Live External Calls
Given provider-specific Researcher prompt selection has been implemented,
When the repository's automated implementation tests are run,
Then:
- Gemini provider-specific prompt selection is covered with controlled configuration
- OpenAI provider-specific prompt selection is covered with controlled configuration
- fallback prompt selection is covered with controlled configuration
- missing selected prompt failures are covered with controlled configuration
- Curator, Writer, stage order, model provider selection, and delivery configuration stability are covered
- no live Gemini, OpenAI, Ollama, Telegram, web search, or other external endpoint call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
