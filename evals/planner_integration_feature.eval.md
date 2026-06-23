# Eval: Planner Integratoin

Purpose
Validate the observable behavior described in `specs/planner_integration_feature`.

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

## Scenario 1: Executing stages in order
Given the planner loads stages from the pipeline config,
When executing stages,
Then:
- Stages are executed in the order
- The first stage recieves no input
- Each stage after the first stage recieves its input from the previous stage's output
- Each stages output, validation reason, status, and timestamp are recorded in the ledger

## Scenario 2: Stage output valid
Given the planner runs a stage,
When a stage's output passes validation,
Then:
- The stages ouput is recoded in the ledger
- The next stage is run

## Scenario 3: Stage output invalid
Given the planner runs a stage,
When a stage's output is invalid,
Then:
- no more stages are run

## Scenario 4: Stage error
Given the planner runs a stage,
When a stage throws an error,
Then:
- no more stages are run
- a readable error is reported

## Scenario 5: Final stage
Given the planner runs the final stage,
When the stages ouput is valid,
Then:
- report output of final stage

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
