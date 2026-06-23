# Spec: Planner Integration

## Objective
The Planner executes the configured pipeline from `config/pipeline.yaml`, passing each stage's successful output into the next stage, validating outputs between stages, halting on failure, and recording stage results in the ledger.


## Background
- Researcher, Curator, and Writer exist as independent stages.
- The pipeline configuration defines stage order, prompt paths, and optional model configuration.
- The pipeline configuration defines what stage instances the planner will create and in what order they will be executed.

## Requirements
- The planner loads stages via the pipeline config.
- The planner executes stages in the order returned by the pipeline config.
- The first stage receives no input provided by the caller.
- Each subsequent stage receives the previous successful stage output as its input.
- Each stage output is validated before the next stage runs.
- If validation passes, the planner records the stage result in the ledger and continues.
- If validation fails, the planner records the failure in the ledger and stops.
- If a stage raises an error while running or validating, the planner records that stage as failed and stops.
- The planner returns the final successful stage output when all configured stages complete.
- The default configured pipeline runs:
  - Researcher
  - Curator
  - Writer

## Inputs
- The planner receives its list of stages to execute from the pipeline config.

## Outputs
- The planner writes each stages output to the ledger.
- Returns any error recieved from a current stage
- When all stages are complete returns the output of the final stage

## Behavior
- The planner receives its list of stages from the pipeline config
- Each stage is executed in the order it was returned by the pipeline config
- If any stage's execution returns an error its output is recorded in the ledger for that stage.
- When any stage's validation returns false it is recorded in the ledger and execution the planner is halted.
- When any stage's validation returns true it is recorded in the ledger along with the stages output.
- The ledger is written after every stage result.
- The output/ledger.json is a record of each stage's status, output and validation

```json
{
  "date": "2026-06-20",
  "stages": {
    "<stage_name>": {
      "status": "done" | "failed",
      "output": "<whatever the stage returned>",
      "validation_reason": "<why it passed or failed>",
      "timestamp": "<ISO 8601>"
    }
  }
}
```

## Validation

### Success Conditions
- A valid default pipeline runs Researcher, Curator, and Writer in order.
- A valid run of the planner is when all stages are run in order, pass validation, and return output.
- Ledger entries exist for all completed stages.
- Stage outputs are passed forward in sequence.

### Failure Conditions
- If a stage produces an error, the remaining stages do not run.
- If a stage's output fails validation, the remaining stages do not run.

## Persistence
- The planner stores the history of running all stages in the ledger

## Out of Scope
- Sending the ouput of the final stage to Telegram

## Completion
When implementation is complete, append a build log entry to eval_log.md following the format in AGENTS.md
