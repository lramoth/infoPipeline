# Spec: OpenClaw Cron Result Output

## Objective

A scheduled OpenClaw run receives a clear machine-readable result from the
command-line pipeline run, including whether the run succeeded or failed and
enough failure detail to explain the result to a user.

## Background

The pipeline is intended to run from cron under OpenClaw. The existing command
line behavior reports success or failure through process exit status and
human-readable terminal output. That is not sufficient for OpenClaw to reliably
forward the outcome and failure reason to a user after a scheduled run.

This spec extends the observable command-line result contract for:

```bash
python3 planner.py
```

and profile-specific runs such as:

```bash
python3 planner.py --profile techno
```

Related spec: `specs/CLI_execution_feature.md`.

## Requirements

### Functional Requirements

- The command shall print exactly one final JSON object to standard output for
  each pipeline run.
- The final JSON object shall contain a top-level `status` field with the value
  `SUCCESS` when the run completes successfully.
- The final JSON object shall contain a top-level `status` field with the value
  `FAILURE` when the run does not complete successfully.
- The final JSON object shall contain a readable `summary` field suitable for
  forwarding to a user.
- The final JSON object shall contain the selected profile name when a profile
  is known.
- On success, the final JSON object shall contain the final pipeline output.
- On failure, the final JSON object shall contain the readable failure reason.
- On stage failure, the final JSON object shall identify the failed stage.
- On delivery failure, the final JSON object shall identify the failed delivery
  provider and preserve the final pipeline output that was produced before
  delivery failed.
- When a diagnostic artifact is available for a failure, the final JSON object
  shall include its path.
- When a ledger artifact path is known, the final JSON object shall include its
  path.
- The command shall exit with status code 0 when the final JSON object reports
  `SUCCESS`.
- The command shall exit with a nonzero status code when the final JSON object
  reports `FAILURE`.

### Non-Functional Requirements

- The output shall be valid JSON.
- The result format shall be stable enough for a scheduler to parse without
  reading human-oriented prose from standard error.
- The result shall not expose configured API keys, access tokens, or Telegram
  credentials.
- Failure output shall prefer concise user-facing explanations over raw provider
  responses.

## Inputs

- A command-line invocation of the configured pipeline.
- Optional profile selection through the existing profile command-line argument.
- Existing pipeline configuration, prompts, credentials, and delivery settings.

## Outputs

The command prints one final JSON object to standard output.

### Success Output

For a successful run, the JSON object shall include:

- `status`: `SUCCESS`
- `summary`: a readable success summary
- `output`: the final pipeline output
- `profile`: the selected profile name when known
- `ledger_path`: the ledger path when known

### Failure Output

For an unsuccessful run, the JSON object shall include:

- `status`: `FAILURE`
- `summary`: a readable failure summary
- `reason`: the readable failure reason
- `profile`: the selected profile name when known
- `failed_stage`: the failed stage when a pipeline stage failed
- `failed_delivery`: the failed delivery provider when delivery failed
- `output`: the final pipeline output when output was produced before the
  failure
- `diagnostic_path`: the diagnostic artifact path when available
- `ledger_path`: the ledger path when known

## Behavior

### Normal Flow

1. A user or scheduler starts the configured pipeline from the command line.
2. The pipeline runs once.
3. The command prints one final JSON object describing the run result.
4. The command exits with a status code matching the JSON `status`.

### Stage Failure Flow

1. A pipeline stage fails validation or cannot complete.
2. Remaining stages and delivery do not run.
3. The command prints a `FAILURE` JSON object that names the failed stage and
   provides a readable reason.
4. If a diagnostic artifact was produced, the JSON object includes its path.
5. The command exits with a nonzero status code.

### Delivery Failure Flow

1. Pipeline stages complete and produce final output.
2. Delivery fails.
3. The command prints a `FAILURE` JSON object that names the failed delivery
   provider, includes the final pipeline output, and provides a readable reason.
4. The command exits with a nonzero status code.

### Startup Failure Flow

1. The command cannot start the configured pipeline.
2. The command prints a `FAILURE` JSON object with a readable reason.
3. The command exits with a nonzero status code.

## Persistence

This feature does not require new persistent data. Existing ledger and
diagnostic artifacts may continue to be written according to their current
contracts and may be referenced by the final JSON output.

## Failure Handling

- If a pipeline stage fails, the result reports `FAILURE`, the failed stage, a
  readable reason, and any available diagnostic path.
- If delivery fails after final pipeline output is produced, the result reports
  `FAILURE`, the failed delivery provider, the readable delivery failure reason,
  and the final pipeline output.
- If the command fails before a pipeline run can start, the result reports
  `FAILURE` with a readable reason.
- Failure output must not require OpenClaw to inspect standard error in order to
  determine success, failure, or the user-facing reason.

## Acceptance Criteria

- [ ] A successful command prints valid JSON with `status` set to `SUCCESS`,
      includes final output, and exits with status code 0.
- [ ] A stage failure prints valid JSON with `status` set to `FAILURE`, includes
      the failed stage and readable reason, and exits with a nonzero status code.
- [ ] A delivery failure prints valid JSON with `status` set to `FAILURE`,
      includes the failed delivery provider, final pipeline output, and readable
      reason, and exits with a nonzero status code.
- [ ] A startup failure prints valid JSON with `status` set to `FAILURE`,
      includes a readable reason, and exits with a nonzero status code.
- [ ] OpenClaw can determine success or failure and a user-facing explanation
      from standard output alone.
- [ ] The JSON output does not expose configured secrets.

## Validation

### Success Conditions

- Successful runs produce a parseable result object that reports `SUCCESS`.
- Unsuccessful runs produce a parseable result object that reports `FAILURE`.
- The process exit code agrees with the reported result status.
- User-facing failure details are available without relying on standard error.

### Failure Conditions

- The command reports success in JSON but exits with a nonzero status code.
- The command reports failure in JSON but exits with status code 0.
- The command prints non-JSON output instead of the final result object.
- A failure result omits the readable reason.
- A stage or delivery failure omits the relevant failed component identity.
- The output exposes configured secrets.

## Constraints

- This feature must not change pipeline stage behavior.
- This feature must not change validation rules.
- This feature must not require live external calls during implementation tests.
- This feature must preserve command-line profile selection.

## Out of Scope

- Scheduling configuration.
- Changing OpenClaw itself.
- Changing Telegram delivery behavior.
- Adding command-line flags or arguments.
- Changing researcher, curator, writer, or delivery provider behavior.

## Completion

When implementation is complete, append a build log entry to `eval_log.md`
following the format in `AGENTS.md`.
