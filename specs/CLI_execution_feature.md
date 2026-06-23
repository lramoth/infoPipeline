# Spec: CLI Execution

## Objective
A user can run the daily infoPipeline from the command line with:

```bash
python3 planner.py
```

# Requirements
- The command starts one pipeline run using the default configured pipeline.

## Success Handling
- the final pipeline output is printed
- the command exits with status code 0

## Failure Handling
- a readable error is printed
- the command exits with a nonzero status code

## Out of Scope
- Scheduling
- Telegram delivery
- Command-line flags or arguments
- Changing pipeline stage behavior
- Changing validation rules

## Completion
When implementation is complete, append a build log entry to eval_log.md following the format in AGENTS.md