# Eval: Config Path Filename-Agnostic Tests

Purpose
Validate the observable behavior described in `specs/config_path_filename_agnostic_tests_feature.md`.

Do not grade implementation details such as:
- helper modules
- validation-result shapes
- internal data structures
- test helper names
- exact fixture construction mechanics

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live Gemini, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for runtime checks.

## Scenario 1: Config Tests Use Arbitrary Valid Filenames For All Stage Paths
Given active pipeline configuration tests are inspected,
When controlled prompt and template files are created for configuration loading,
Then:
- controlled Researcher prompt filenames do not need to match the default Researcher prompt filename
- controlled Curator prompt filenames do not need to match the default Curator prompt filename
- controlled Writer prompt filenames do not need to match the default Writer prompt filename
- controlled Writer template filenames do not need to match the default Writer template filename

## Scenario 2: Configured Paths Are Honored Exactly
Given a valid controlled pipeline configuration declares arbitrary existing prompt and template paths,
When the pipeline configuration is loaded,
Then:
- the assembled Researcher uses the prompt path declared in the controlled configuration
- the assembled Curator uses the prompt path declared in the controlled configuration
- the assembled Writer uses the prompt path declared in the controlled configuration
- the assembled Writer uses the template path declared in the controlled configuration
- stage order remains the order declared in configuration

## Scenario 3: Default Config Checks Are Filename-Agnostic
Given the default pipeline configuration is loaded,
When default configured prompt and template paths are checked,
Then:
- each configured prompt path points to an existing file
- the configured Writer template path points to an existing file
- the check does not require the default Writer prompt path to contain any specific filename
- the check does not require the default Writer template path to contain any specific filename

## Scenario 4: Missing Path Failures Remain Covered
Given invalid controlled pipeline configurations are loaded,
When a prompt-driven stage omits `prompt_path` or Writer omits `template_path`,
Then:
- loading fails
- a readable configuration error is reported
- no implicit source-level path fallback is used

## Scenario 5: Missing File Failures Remain Covered
Given invalid controlled pipeline configurations are loaded,
When a configured prompt path or configured Writer template path points to a nonexistent file,
Then:
- loading fails
- a readable configuration error is reported
- no implicit source-level path fallback is used

## Scenario 6: Runtime Behavior Is Unchanged
Given filename-agnostic configuration tests have been implemented,
When the repository's runtime-facing behavior is considered,
Then:
- prompt files are not renamed by this cleanup
- template files are not renamed by this cleanup
- prompt and template content remains unchanged
- `config/pipeline.yaml` remains the source of configured paths
- no Gemini, Ollama, Telegram, or delivery behavior is changed

## Scenario 7: Repository Tests Still Pass Without Live External Calls
Given filename-agnostic configuration tests have been implemented,
When the repository's automated tests are run without live external service calls,
Then:
- configured prompt-path behavior passes
- configured Writer template-path behavior passes
- missing path and missing file failures remain covered
- no live Gemini, Ollama, or Telegram call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
