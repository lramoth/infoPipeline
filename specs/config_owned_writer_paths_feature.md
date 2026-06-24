# Spec: Config-Owned Writer Paths

## Objective
Writer prompt and template paths are owned by `config/pipeline.yaml`, not by Python source defaults, so Writer presentation and prompt behavior can be changed through configuration rather than code.

## Background
The pipeline configuration already defines explicit prompt paths for prompt-driven stages. Researcher and Curator prompt paths are being moved away from Python source defaults so configuration owns prompt selection. Writer still defines Python-level defaults for both its prompt path and template path, and `config/pipeline.yaml` does not yet declare the Writer template path.

This feature extends config-owned path selection to Writer by requiring both Writer `prompt_path` and Writer `template_path` in pipeline configuration.

## Requirements
- Writer prompt path selection shall come from pipeline configuration when the default pipeline is assembled.
- Writer template path selection shall come from pipeline configuration when the default pipeline is assembled.
- Writer shall not define a Python-level default prompt path.
- Writer shall not define a Python-level default template path.
- The default `config/pipeline.yaml` Writer stage entry shall include `template_path`.
- Existing Writer behavior shall remain unchanged when `config/pipeline.yaml` provides valid prompt and template paths.
- Existing Researcher and Curator configured prompt-path behavior shall remain unchanged.

## Behavior
- When the default pipeline is loaded, Writer receives the prompt path declared for Writer in `config/pipeline.yaml`.
- When the default pipeline is loaded, Writer receives the template path declared for Writer in `config/pipeline.yaml`.
- A valid configured Writer prompt path allows Writer to load and use that prompt at runtime.
- A valid configured Writer template path allows Writer to assemble the outbound message at runtime.
- A missing configured Writer prompt path remains a configuration error.
- A missing configured Writer template path is a configuration error.
- A configured Writer prompt path that does not exist remains a configuration error.
- A configured Writer template path that does not exist is a configuration error.

## Validation

### Success Conditions
- The default pipeline loads Writer with prompt and template paths supplied by `config/pipeline.yaml`.
- Writer source text contains no `DEFAULT_PROMPT_PATH` definition.
- Writer source text contains no `DEFAULT_TEMPLATE_PATH` definition.
- The default Writer configuration includes both `prompt_path` and `template_path`.
- Existing Writer prompt loading and template assembly behavior continues to pass with valid configured paths.
- Existing Researcher and Curator configured prompt-path behavior continues to pass.

### Failure Conditions
- A Writer stage missing `prompt_path` in `config/pipeline.yaml` fails configuration loading.
- A Writer stage missing `template_path` in `config/pipeline.yaml` fails configuration loading.
- A Writer stage with a nonexistent configured prompt file fails configuration loading.
- A Writer stage with a nonexistent configured template file fails configuration loading.
- Writer still provides a source-level prompt path fallback.
- Writer still provides a source-level template path fallback.

## Out of Scope
- Renaming existing prompt or template files.
- Changing Writer prompt content.
- Changing Writer template content.
- Adding a new topic-profile configuration schema.
- Changing Researcher, Curator, Delivery, Gemini, Ollama, or Telegram behavior.
- Running external Gemini, Ollama, or Telegram calls.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in AGENTS.md.
