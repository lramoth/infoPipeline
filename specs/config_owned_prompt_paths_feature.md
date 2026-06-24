# Spec: Config-Owned Prompt Paths

## Objective
Prompt paths for prompt-driven stages are owned by `config/pipeline.yaml`, not by Python source defaults, so the pipeline can be retargeted to other topics by changing configuration and prompt files rather than code.

## Background
The pipeline configuration already defines explicit prompt paths for Researcher, Curator, and Writer stages. Earlier Python defaults for Researcher and Curator were established before `config/pipeline.yaml` existed. Those defaults now duplicate configuration responsibility and keep topic-specific prompt filenames visible in source code.

## Requirements
- Researcher prompt path selection shall come from pipeline configuration when the default pipeline is assembled.
- Curator prompt path selection shall come from pipeline configuration when the default pipeline is assembled.
- Researcher shall not define a Python-level default prompt path.
- Curator shall not define a Python-level default prompt path.
- Researcher documentation shall describe the stage as collecting and validating configured-topic research from Gemini.
- Existing behavior for configured prompt loading shall remain unchanged when `config/pipeline.yaml` provides valid prompt paths.

## Behavior
- When the default pipeline is loaded, each prompt-driven stage receives the prompt path declared for that stage in `config/pipeline.yaml`.
- A valid configured prompt path allows the corresponding stage to load and use that prompt at runtime.
- A missing configured prompt path for a prompt-driven stage remains a configuration error.
- A configured prompt path that does not exist remains a configuration error.

## Validation

### Success Conditions
- The default pipeline loads Researcher and Curator with prompt paths supplied by `config/pipeline.yaml`.
- Researcher source text contains no `DEFAULT_PROMPT_PATH` definition.
- Curator source text contains no `DEFAULT_PROMPT_PATH` definition.
- Researcher stage documentation uses topic-neutral language.
- Existing configured prompt-path behavior continues to pass.

### Failure Conditions
- A prompt-driven stage missing `prompt_path` in `config/pipeline.yaml` fails configuration loading.
- A prompt-driven stage with a nonexistent configured prompt file fails configuration loading.
- Researcher or Curator still provide a source-level prompt path fallback.

## Out of Scope
- Renaming existing prompt files.
- Changing prompt content.
- Adding a new topic-profile configuration schema.
- Changing Writer behavior.
- Running external Gemini, Ollama, or Telegram calls.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in AGENTS.md.
