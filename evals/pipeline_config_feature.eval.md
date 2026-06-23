# Eval: Pipeline Config

Purpose
Validate the observable behavior described in `specs/pipeline_config_feature.md`.

Do not grade implementation details such as: 
- class names
- method names 
- dataclasses
- validation-result shapes
- internal data structures.

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live external API calls.
- Do not modify external systems.
- Do not send emails, messages, or notifications.
- Use mocks, fixtures, or controlled test inputs.

## Scenario 1: Config Exists
Given the pipeline config feature has been implemented,
When the repository is inspected,
Then:
- `config/pipeline.yaml` exists

## Scenario 2: Valid config
Given a valid pipeline configuration,
When the configuration is loaded,
Then:
- Valid YAML data is loaded 
- Loaded stages preserve YAML order
- Each prompt-driven stage contains a prompt_path
- Each stage contains a name
- Reseacher, Curator, and Writer stages are defined in that order

## Scenario 3: Missing or malformed config
Given the pipeline config is missing or contains malformed YAML,
When the config is loaded,
Then:
- loading fails
- a readable error is reported

## Scenario 4: Missing required stage fields
Given the pipeline config contains a stage missing `name` or a prompt-driven stage missing `prompt_path`,
When the config is loaded,
Then:
- loading fails
- a readable error is reported

## Scenario 5: Invalid stage or prompt path
Given the pipeline config contains an unknown stage name or a prompt path that does not exist,
When the config is loaded,
Then:
- loading fails
- a readable error is reported

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
