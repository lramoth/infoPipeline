# Eval: Config-Owned Prompt Paths

Purpose
Validate the observable behavior described in `specs/config_owned_prompt_paths_feature.md`.

Do not grade implementation details such as:
- helper modules
- validation-result shapes
- internal data structures
- HTTP client implementation choices
- model provider client implementation choices

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live Gemini, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for runtime checks.

## Scenario 1: Default Pipeline Uses Configured Prompt Paths
Given the default pipeline configuration is present,
When the default pipeline is loaded,
Then:
- Researcher receives the prompt path declared for Researcher in `config/pipeline.yaml`
- Curator receives the prompt path declared for Curator in `config/pipeline.yaml`
- Writer configured prompt-path behavior remains unchanged
- the loaded prompt paths point to existing prompt files

## Scenario 2: Source-Level Researcher Prompt Fallback Is Removed
Given the current Researcher source is inspected,
When prompt path selection behavior is reviewed,
Then:
- Researcher does not define `DEFAULT_PROMPT_PATH`
- Researcher does not provide a source-level prompt path fallback
- Researcher documentation describes the stage with topic-neutral configured-topic language

## Scenario 3: Source-Level Curator Prompt Fallback Is Removed
Given the current Curator source is inspected,
When prompt path selection behavior is reviewed,
Then:
- Curator does not define `DEFAULT_PROMPT_PATH`
- Curator does not provide a source-level prompt path fallback

## Scenario 4: Configured Prompt Loading Still Works
Given controlled Researcher and Curator prompts are supplied through configuration or explicit test setup,
When Researcher and Curator are run with controlled model responses,
Then:
- each stage loads the supplied prompt at runtime
- each stage sends the supplied prompt content to the configured model endpoint
- valid configured prompt paths allow the stages to complete their existing behavior without requiring source-level defaults

## Scenario 5: Missing Prompt Path Remains A Configuration Error
Given a prompt-driven stage is missing `prompt_path` in `config/pipeline.yaml`,
When the pipeline configuration is loaded,
Then:
- loading fails
- a readable configuration error is reported
- the pipeline is not assembled with an implicit source-level prompt fallback

## Scenario 6: Missing Configured Prompt File Remains A Configuration Error
Given a prompt-driven stage points to a prompt file that does not exist,
When the pipeline configuration is loaded,
Then:
- loading fails
- a readable configuration error is reported
- the pipeline is not assembled with an implicit source-level prompt fallback

## Scenario 7: Repository Tests Still Pass Without Live External Calls
Given config-owned prompt paths have been implemented,
When the repository's automated tests are run without live external service calls,
Then:
- existing configured prompt-path behavior passes
- missing prompt-path and missing prompt-file failures remain covered
- no live Gemini, Ollama, or Telegram call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
