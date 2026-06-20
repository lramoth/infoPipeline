# Eval: Planner Feature

These scenarios validate the observable behavior described in `specs/planner_feature.md`.

Do not grade implementation details such as class names, method names, dataclasses, validation-result shapes, or internal data structures.

## Scenario 1: Successful run

Given multiple test stages that produce output and pass validation,

When the Planner runs,

Then:

- all stages are executed
- each stage is recorded in the ledger as `done`
- the caller is told the run succeeded

## Scenario 2: Validation failure

Given a test stage that fails validation,

When the Planner runs,

Then:

- the failed stage is recorded as `failed`
- the failure reason is recorded in the ledger
- no remaining stages are executed
- the caller is told which stage failed and why

## Scenario 3: Stage execution error

Given a test stage that raises an exception while running,

When the Planner runs,

Then:

- the stage is recorded as `failed`
- the error reason is recorded in the ledger
- no remaining stages are executed
- the caller is told which stage failed and why

## Scenario 4: Ledger lifecycle

Given a ledger from a previous day,

When the Planner runs,

Then:

- a fresh ledger is started for today

Given a ledger from today,

When the Planner reruns a stage with the same name,

Then:

- the existing stage entry is overwritten with the latest result

## Grading instructions

For each scenario:

- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append results to `eval_log.md` and provide an overall verdict.

Overall verdict is PASS only if every scenario passes.