# Spec: Topic-Neutral Active Tests

## Objective
Active tests should verify that topic and presentation choices come from configuration and fixtures without implying that the pipeline architecture requires a specific topic such as techno.

## Background
The pipeline is now configured through `config/pipeline.yaml`, and prompt/template paths are supplied by configuration rather than Python source defaults. Prompt filenames and configuration values may still describe the current topic or purpose, because those files are part of the configured profile. However, active tests should not hard-code the current topic name as though it were an architectural requirement.

Historical specs, evals, and build/evaluation logs may still preserve older topic-specific wording.

## Requirements
- Pipeline configuration tests shall continue to prove that configured prompt and template paths are loaded correctly.
- Pipeline configuration tests shall allow arbitrary valid configured prompt filenames, rather than depending on the current default prompt filenames.
- Pipeline configuration tests shall verify that the default configuration's referenced prompt and template files exist.
- Pipeline configuration tests shall not require the default Researcher or Curator prompt files to have topic-specific names.
- Writer tests shall use topic-neutral synthetic briefing text when the test is not specifically about the current configured topic.
- The current prompt filenames may remain topic-specific.
- `config/pipeline.yaml` may continue to point to topic-specific prompt filenames.
- Existing prompt content shall remain unchanged.

## Behavior
- A valid pipeline configuration with arbitrary existing prompt filenames loads successfully.
- The default pipeline configuration remains valid and all referenced prompt and template files exist.
- Writer validation behavior remains unchanged when synthetic test messages use topic-neutral briefing labels.
- Topic-specific prompt filenames remain acceptable configuration values.

## Validation

### Success Conditions
- Pipeline configuration behavior continues to pass with non-topic-specific fixture prompt filenames.
- The default configuration is checked for valid referenced prompt and template files without requiring specific topic words in those filenames.
- Writer tests no longer use topic-specific briefing labels in synthetic messages unrelated to topic selection.
- Existing configured prompt-path and Writer template-path behavior continues to pass.

### Failure Conditions
- A test requires Researcher or Curator prompt filenames to contain the current topic name.
- A test fails solely because the current default Researcher or Curator prompt file is renamed while the configuration is updated to point to a valid replacement.
- Writer tests continue to use topic-specific synthetic briefing labels where the topic is not under test.
- Existing configured path validation behavior regresses.

## Out of Scope
- Renaming prompt files.
- Changing prompt content.
- Changing `config/pipeline.yaml` solely to remove topic-specific prompt filenames.
- Rewriting historical specs, evals, or `eval_log.md`.
- Adding a topic-profile configuration schema.
- Changing runtime pipeline behavior.
- Running external Gemini, Ollama, or Telegram calls.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in AGENTS.md.
