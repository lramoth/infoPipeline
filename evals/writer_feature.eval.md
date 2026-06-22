# Eval: Writer

Purpose
Validate the observable behavior described in `specs/writer_feature.md`.

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

## Scenario 1: Local Model Failures
Given the Writer runs,
When the local model response is empty or fails,
Then:
- The run fails and reports a readable error

## Scenario 2: Missing Input
Given the Writer runs,
When the curated item list is empty or the configured prompt file is missing or empty,
Then:
- The stage is considered failed

## Scenario 3: Output Errors
Given the Writer runs,
When a generated output is not a string,
Then:
- The stage is considered failed

## Scenario 4: Generated String Errors
Given the Writer runs,
When the output is missing a title or url defined by an item in the Curated item list or is missing a summary text,
Then:
- The stage is considered failed

## Scenario 5: Ordering Error
Given the Writer runs,
When items in the generated output do not appear in the same ascending rank order as items in the Curated items,
Then:
- The stage is considered failed

## Scenario 6: Successful message structure
Given the Writer runs with valid curated items and a valid prompt,
When a non-empty Telegram message is generated,
Then:
- the stage is considered successful
- each curated item is represented by its title and URL
- each item has summary text
- items appear in the same ascending rank order provided by the Curator

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
