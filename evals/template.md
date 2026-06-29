# Eval: Eval Name

## Purpose

Validate only the observable behavior described in `spec name`.

Do not infer requirements that are not stated in the referenced specification.

Do not grade or report implementation details in eval_log.md, including:
- class names
- method names
- dataclasses
- return-value shapes
- internal data structures.
- helper inputs
- algorithms

Write scenario results from the product or artifact reader's perspective.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live external API calls.
- Do not modify external systems.
- Do not send emails, messages, or notifications.
- Use mocks, fixtures, or controlled test inputs.

## Scenario 1: Successful Observable Behavior
Given:
- Add the starting conditions visible to a user, caller, operator, or artifact reader.

When:
- Add the action being evaluated.

Then:
- Add the observable successful outcome.
- Add any required absence of side effects.

## Scenario 2: Required Failure Or Rejection Behavior
Given:
- Add the invalid, missing, or failing condition described by the specification.

When:
- Add the action being evaluated.

Then:
- Add the readable failure, rejection, halted work, or preserved state that must be observed.
- Add any downstream action that must not occur.

Add more scenarios only when the specification states more distinct observable requirements.

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append an evaluation entry to `eval_log.md` using the format in `AGENTS.md`:
- eval file used
- PASS/FAIL result for each scenario
- one-sentence product-behavior reason for each scenario result
- overall verdict

Overall verdict is PASS only if every scenario passes.

Evaluation sessions must not write build-log entries.
