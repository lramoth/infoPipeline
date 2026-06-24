# Spec: Profile Selection

## Objective
The pipeline can be invoked for different configured profiles, so separate scheduled runs can produce different topic reports without changing source code or manually swapping configuration files.

## Background
The pipeline currently uses `config/pipeline.yaml` as the source of truth for stage order, prompt paths, Writer template path, model settings, and enabled delivery providers. This supports one configured topic at a time.

To run two scheduled jobs, such as one for techno news and one for financial news, the caller needs to select which configured profile supplies the prompt and template paths for that run. Each profile also needs an isolated ledger/output location so same-day runs for different profiles do not overwrite each other.

## Requirements
- The command-line entry point shall accept a profile selection option.
- A caller shall be able to run the same pipeline for different profiles without editing Python source code.
- Each profile shall provide the configured paths needed by Researcher, Curator, and Writer:
  - Researcher prompt path
  - Curator prompt path
  - Writer prompt path
  - Writer template path
- The selected profile's configured paths shall be used when assembling the default pipeline.
- When no profile is provided, the pipeline shall use a default profile declared in configuration.
- An unknown requested profile shall fail before any stage runs.
- A missing default profile shall fail before any stage runs.
- A profile missing a required prompt or template path shall fail before any stage runs.
- A profile path that points to a nonexistent file shall fail before any stage runs.
- Each profile run shall record its results in a profile-specific ledger/output location.
- Same-day runs for different profiles shall not overwrite each other's ledger entries.
- The ledger shall record which profile was used for the run.
- Existing stage validation, delivery behavior, and Writer message assembly behavior shall remain unchanged after profile selection chooses the configured paths.

## Behavior

### Normal Flow
1. A caller invokes the pipeline with a profile name, such as `--profile techno`.
2. The pipeline configuration is loaded.
3. The requested profile is found.
4. The selected profile's Researcher, Curator, Writer prompt, and Writer template paths are validated.
5. The default stage order and model/delivery settings are assembled using the selected profile's paths.
6. The pipeline runs once.
7. Stage and delivery results are recorded in a profile-specific ledger/output location.
8. The ledger records the selected profile name.

### Default Profile Flow
1. A caller invokes the pipeline without a profile name.
2. The pipeline uses the default profile declared in configuration.
3. The run behaves as a selected-profile run for that default profile.

### Multiple Scheduled Jobs
1. One scheduled job invokes the pipeline with one profile name.
2. Another scheduled job invokes the pipeline with a different profile name.
3. Each run uses the prompt and template paths for its selected profile.
4. Each run writes to its own profile-specific ledger/output location.

## Validation

### Success Conditions
- Running with an explicit valid profile loads that profile's configured prompt and template paths.
- Running without a profile uses the configured default profile.
- Two different valid profile names can be loaded without changing source code.
- Two same-day runs using different profiles record separate ledgers or output locations.
- The ledger for each run records the selected profile name.
- Existing configured stage order, model settings, validation behavior, Writer message assembly, and delivery behavior continue to pass.

### Failure Conditions
- Requesting an unknown profile fails with a readable error before any stage runs.
- Omitting a profile when no default profile is configured fails with a readable error before any stage runs.
- A profile missing a required prompt or template path fails with a readable error before any stage runs.
- A profile path pointing to a nonexistent file fails with a readable error before any stage runs.
- Two different profiles write to the same same-day ledger and overwrite each other.

## Out of Scope
- Adding new prompt files for additional topics.
- Changing prompt content.
- Changing Writer template content.
- Changing model provider behavior.
- Changing Telegram delivery behavior.
- Running external Gemini, Ollama, or Telegram calls during implementation tests.
- Building a UI for selecting profiles.
- Supporting multiple profiles in a single pipeline invocation.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in AGENTS.md.
