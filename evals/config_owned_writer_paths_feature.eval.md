# Eval: Config-Owned Writer Paths

Purpose
Validate the observable behavior described in `specs/config_owned_writer_paths_feature.md`.

Do not grade implementation details such as:
- helper modules
- validation-result shapes
- internal data structures
- HTTP client implementation choices
- model provider client implementation choices
- parsing or assembly algorithms

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live Gemini, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for runtime checks.

## Scenario 1: Default Pipeline Uses Configured Writer Paths
Given the default pipeline configuration is present,
When the default pipeline is loaded,
Then:
- Writer receives the prompt path declared for Writer in `config/pipeline.yaml`
- Writer receives the template path declared for Writer in `config/pipeline.yaml`
- the loaded Writer prompt path points to an existing prompt file
- the loaded Writer template path points to an existing template file
- Researcher and Curator configured prompt-path behavior remains unchanged

## Scenario 2: Default Writer Configuration Includes Template Path
Given the default pipeline configuration is inspected,
When the Writer stage entry is reviewed,
Then:
- the Writer stage entry includes `prompt_path`
- the Writer stage entry includes `template_path`
- both configured Writer paths are non-empty

## Scenario 3: Source-Level Writer Path Fallbacks Are Removed
Given the current Writer source is inspected,
When path selection behavior is reviewed,
Then:
- Writer does not define `DEFAULT_PROMPT_PATH`
- Writer does not define `DEFAULT_TEMPLATE_PATH`
- Writer does not provide a source-level prompt path fallback
- Writer does not provide a source-level template path fallback

## Scenario 4: Configured Writer Prompt And Template Loading Still Works
Given controlled Writer prompt and template files are supplied through configuration or explicit test setup,
When Writer runs with controlled curated items and controlled local-model output,
Then:
- Writer loads the supplied prompt at runtime
- Writer sends the supplied prompt content to the configured local model endpoint
- Writer loads the supplied template at runtime
- Writer uses the supplied template to assemble the outbound message
- valid configured prompt and template paths allow Writer to complete existing outbound-message behavior without requiring source-level defaults

## Scenario 5: Missing Writer Prompt Path Remains A Configuration Error
Given the Writer stage is missing `prompt_path` in `config/pipeline.yaml`,
When the pipeline configuration is loaded,
Then:
- loading fails
- a readable configuration error is reported
- the pipeline is not assembled with an implicit source-level prompt path fallback

## Scenario 6: Missing Writer Template Path Is A Configuration Error
Given the Writer stage is missing `template_path` in `config/pipeline.yaml`,
When the pipeline configuration is loaded,
Then:
- loading fails
- a readable configuration error is reported
- the pipeline is not assembled with an implicit source-level template path fallback

## Scenario 7: Missing Configured Writer Prompt File Remains A Configuration Error
Given the Writer stage points to a prompt file that does not exist,
When the pipeline configuration is loaded,
Then:
- loading fails
- a readable configuration error is reported
- the pipeline is not assembled with an implicit source-level prompt path fallback

## Scenario 8: Missing Configured Writer Template File Is A Configuration Error
Given the Writer stage points to a template file that does not exist,
When the pipeline configuration is loaded,
Then:
- loading fails
- a readable configuration error is reported
- the pipeline is not assembled with an implicit source-level template path fallback

## Scenario 9: Existing Stage Boundaries Remain Unchanged
Given config-owned Writer paths have been implemented,
When Writer behavior is exercised with controlled local-model output,
Then:
- Writer still uses local Ollama behavior for item prose generation
- Writer still preserves curated titles and source URLs in the outbound message
- no Gemini API call is required for Writer message generation
- no delivery behavior is invoked or changed by Writer message generation

## Scenario 10: Repository Tests Still Pass Without Live External Calls
Given config-owned Writer paths have been implemented,
When the repository's automated tests are run without live external service calls,
Then:
- existing Writer prompt loading and template assembly behavior passes
- configured Writer path behavior passes
- missing Writer path and missing Writer file failures remain covered
- existing Researcher and Curator configured prompt-path behavior passes
- no live Gemini, Ollama, or Telegram call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
