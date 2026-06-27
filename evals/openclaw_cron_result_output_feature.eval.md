# Eval: OpenClaw Cron Result Output

Purpose
Validate the observable behavior described in `specs/openclaw_cron_result_output_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- file names
- validation-result shapes
- internal data structures
- JSON serialization implementation choices
- terminal redirection implementation choices

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment

Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Telegram, OpenClaw, or other
  external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for pipeline stages, delivery
  providers, configuration, credentials, command execution, ledger artifacts,
  diagnostic artifacts, and runtime checks.

## Scenario 1: Successful Command Result

Given the configured pipeline command is executed,
And the pipeline run completes successfully,
When the command finishes,
Then:
- standard output contains exactly one final JSON object
- the JSON object is valid and parseable
- the JSON object reports `status` as `SUCCESS`
- the JSON object includes a readable success summary
- the JSON object includes the final pipeline output
- the JSON object includes the selected profile name when the profile is known
- the JSON object includes the ledger path when the ledger path is known
- the command exits with status code 0

## Scenario 2: Stage Failure Result

Given the configured pipeline command is executed,
And a pipeline stage fails validation or cannot complete,
When the command finishes,
Then:
- standard output contains exactly one final JSON object
- the JSON object is valid and parseable
- the JSON object reports `status` as `FAILURE`
- the JSON object includes a readable failure summary
- the JSON object includes a readable failure reason
- the JSON object identifies the failed stage
- the JSON object includes the selected profile name when the profile is known
- the JSON object includes the ledger path when the ledger path is known
- the JSON object includes the diagnostic artifact path when a diagnostic
  artifact is available
- remaining stages and delivery are not reported as successful after the stage
  failure
- the command exits with a nonzero status code

## Scenario 3: Delivery Failure Result

Given the configured pipeline command is executed,
And all pipeline stages complete successfully,
And delivery fails,
When the command finishes,
Then:
- standard output contains exactly one final JSON object
- the JSON object is valid and parseable
- the JSON object reports `status` as `FAILURE`
- the JSON object includes a readable failure summary
- the JSON object includes a readable delivery failure reason
- the JSON object identifies the failed delivery provider
- the JSON object preserves the final pipeline output produced before delivery
  failed
- the JSON object includes the selected profile name when the profile is known
- the JSON object includes the ledger path when the ledger path is known
- the command exits with a nonzero status code

## Scenario 4: Startup Failure Result

Given the pipeline command is executed,
And the command cannot start the configured pipeline,
When the command finishes,
Then:
- standard output contains exactly one final JSON object
- the JSON object is valid and parseable
- the JSON object reports `status` as `FAILURE`
- the JSON object includes a readable failure summary
- the JSON object includes a readable failure reason
- the JSON object includes the selected profile name when the profile is known
- the command exits with a nonzero status code

## Scenario 5: Standard Output Is Sufficient For OpenClaw

Given any successful, stage-failed, delivery-failed, or startup-failed command
result,
When only standard output and the process exit status are inspected,
Then:
- success or failure can be determined from the JSON `status`
- the user-facing explanation can be determined from the JSON summary and, for
  failures, the JSON reason
- the process exit status agrees with the JSON `status`
- standard error is not required to determine whether the run succeeded or
  failed
- standard error is not required to determine the user-facing failure reason

## Scenario 6: Output Remains Single Parseable JSON

Given the configured pipeline command is executed,
And controlled stage or delivery behavior produces incidental human-oriented
terminal output during the run,
When the command finishes,
Then:
- standard output still contains exactly one final JSON object
- standard output can be parsed as JSON without removing any non-JSON text
- the JSON object still reports the final run status
- the JSON object still includes the required success or failure fields for
  that result

## Scenario 7: Secret And Raw Payload Safety

Given configured credentials, tokens, chat identifiers, or controlled provider
payloads are present during a command run,
When the command prints its final JSON result,
Then:
- the JSON result does not expose configured API keys
- the JSON result does not expose access tokens
- the JSON result does not expose Telegram credentials
- failure output uses concise user-facing explanations rather than unbounded
  raw provider responses
- diagnostic and ledger paths may be referenced without requiring raw provider
  payloads to be printed in the command result

## Scenario 8: Existing Pipeline Behavior Is Unchanged

Given OpenClaw cron result output has been implemented,
When the pipeline is exercised with controlled successful and failing stage
outputs,
Then:
- pipeline stage behavior is unchanged
- validation rules are unchanged
- profile command-line selection is preserved
- Telegram delivery behavior is unchanged
- no new command-line flag or argument is required
- no live external endpoint call is required for implementation tests

## Grading instructions

For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
