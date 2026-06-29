# Spec: Version Command

## Objective

A user can ask the command-line application for its version without starting a
pipeline run.

## Requirements

- Running the command-line application with `--version` reports the application
  name and version to standard output.
- The version report is a single line in this format:

```text
infoPipeline 0.1.0
```

- The command exits with status code 0 after reporting the version.
- The command does not run the pipeline, call configured providers, write a
  ledger, or attempt delivery.
- When `--version` is provided with other supported options, the command still
  reports the version and exits without running the pipeline.

## Out of Scope

- Changing normal pipeline run output.
- Changing profile selection behavior for pipeline runs.
- Live Gemini, OpenAI, Ollama, Bandcamp, or Telegram calls.
- Packaging metadata or release automation.

## Completion

When implementation is complete, append a build log entry to `eval_log.md`
following the format in `AGENTS.md`.
