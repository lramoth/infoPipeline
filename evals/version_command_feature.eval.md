# Eval: Version Command

Purpose
Validate the observable behavior described in `specs/version_command_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- version storage location
- command-line parser implementation choices
- internal data structures

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Bandcamp, Telegram, or other
  external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for pipeline stages, delivery
  providers, configuration, credentials, command execution, ledger artifacts,
  and runtime checks.

## Scenario 1: Version Output
Given the command-line application is available,
When it is invoked with `--version`,
Then:
- standard output contains exactly one line
- the line is exactly `infoPipeline 0.1.0`
- no additional human-oriented or machine-oriented output appears on standard
  output
- the command exits with status code 0

## Scenario 2: Version Does Not Run Pipeline
Given the command-line application is invoked with `--version`,
And controlled configuration, credentials, stages, delivery providers, and
ledger locations are present,
When the command finishes,
Then:
- no Researcher, Curator, Writer, or Delivery behavior is started
- no configured provider endpoint is contacted
- no Telegram message or other external delivery is attempted
- no pipeline ledger is created, overwritten, or updated
- the command exits after reporting the version

## Scenario 3: Version Takes Precedence With Supported Options
Given another supported command-line option is provided together with
`--version`,
When the command-line application is invoked,
Then:
- standard output contains exactly `infoPipeline 0.1.0` as a single line
- the command exits with status code 0
- no pipeline run is started
- no configured provider endpoint is contacted
- no ledger or delivery side effect occurs

## Scenario 4: Normal Pipeline Invocation Is Unchanged
Given the command-line application is invoked without `--version`,
And controlled pipeline behavior is provided,
When the command completes,
Then:
- normal pipeline command output remains governed by the existing command-line
  result behavior
- profile selection behavior for pipeline runs is unchanged
- pipeline stage validation behavior is unchanged
- delivery behavior for completed pipeline runs is unchanged
- no version report is printed unless `--version` is provided

## Scenario 5: Repository Checks Cover Version Behavior Without Live Calls
Given the version command feature has been implemented,
When the repository's automated checks for this feature are run,
Then:
- version output is covered
- successful version exit status is covered
- absence of pipeline execution side effects is covered
- precedence with other supported options is covered
- no live Gemini, OpenAI, Ollama, Bandcamp, Telegram, or other external endpoint
  call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
