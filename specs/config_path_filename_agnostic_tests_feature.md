# Spec: Config Path Filename-Agnostic Tests

## Objective
Active pipeline configuration tests should verify that configured prompt and template paths are honored regardless of the specific filenames used in `config/pipeline.yaml`.

## Background
The pipeline now treats prompt and template paths as configuration-owned values. Recent cleanup removed topic-specific assumptions from Researcher and Curator prompt path tests, but active tests still refer to current Writer prompt and template filenames. Writer prompt and template filenames may change over time. As long as valid paths are declared in configuration, pipeline assembly should work independently of those filenames.

## Requirements
- Pipeline configuration tests shall continue to prove that configured prompt and template paths are loaded correctly.
- Pipeline configuration tests shall use arbitrary valid fixture filenames for Researcher, Curator, and Writer prompt paths.
- Pipeline configuration tests shall use an arbitrary valid fixture filename for Writer template path.
- Pipeline configuration tests shall not require Writer prompt files to use the current default Writer prompt filename.
- Pipeline configuration tests shall not require Writer template files to use the current default Writer template filename.
- Default configuration tests shall verify that configured prompt and template paths reference existing files without requiring specific filenames.
- Existing missing prompt path, missing Writer template path, missing prompt file, and missing Writer template file failures shall remain covered.
- Runtime pipeline behavior shall remain unchanged.

## Behavior
- A valid pipeline configuration with arbitrary existing Researcher, Curator, and Writer prompt filenames loads successfully.
- A valid pipeline configuration with an arbitrary existing Writer template filename loads successfully.
- The assembled stages use the exact prompt and template paths declared in the configuration.
- The default pipeline configuration remains valid as long as all configured prompt and template paths point to existing files.

## Validation

### Success Conditions
- Pipeline configuration behavior passes with non-default Writer prompt and template fixture filenames.
- Pipeline configuration tests verify configured Writer prompt and template paths by comparing against the fixture configuration, not by requiring current default filenames.
- Default configuration checks confirm referenced prompt and template files exist without asserting exact filenames.
- Existing configured path validation behavior continues to pass.

### Failure Conditions
- A test requires the Writer prompt path to contain the current default Writer prompt filename.
- A test requires the Writer template path to contain the current default Writer template filename.
- A test fails solely because the default Writer prompt or template file is renamed while configuration is updated to point to a valid replacement.
- Existing configured path validation behavior regresses.

## Out of Scope
- Renaming prompt or template files.
- Changing prompt or template content.
- Changing `config/pipeline.yaml` solely to remove existing filenames.
- Rewriting historical specs, evals, or `eval_log.md`.
- Adding a topic-profile configuration schema.
- Changing runtime pipeline behavior.
- Running external Gemini, Ollama, or Telegram calls.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in AGENTS.md.
