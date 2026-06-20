# Eval: Env Config

Purpose
Validate the observable behavior described in `specs/env_config_feature.md`.

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

## Scenario 1: .env file missing
Given .env is loaded,
When .env file does not exist,
Then:
- Return an error to the caller

## Scenario 2: .env file key is missing
Given .env is loaded,
When a required key is missing,
Then:
- Return an error to the caller

## Scenario 3: .env file key's value is missing
Given .env is loaded,
When a required key exists but its value is an empty string or nil,
Then:
- Return an error to the caller

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
