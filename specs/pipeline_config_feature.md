# Spec: Pipeline Config

## Objective
Pipeline stage order and stage prompt paths are defined in a YAML configuration file so the pipeline can be assembled without changing Python source code.

## Background
The Planner runs stages in order.
Researcher, Curator, and Writer already exist as independent stages.
Researcher, Curator, and Writer prompt content is loaded from markdown files.
This feature introduces a pipeline configuration file that describes which stages are included, the order in which they are executed, and which prompt file each prompt-driven stage uses.

## Requirements
- The pipeline configuration is stored at config/pipeline.yaml
- The configuration defines an ordered list of stages
- Each stage entry contains a name
- Stages that use a prompt contain a prompt_path
- Stage order in the YAML file is preserved when the pipeline is assembled
- The default pipeline config includes:
    - Researcher using prompts/researchers/techno_news.md
    - Curator using prompts/curators/polegroup_techno.md
    - Writer using prompts/writers/telegram_brief.md
- Stage entries may contain a model object
- A model object contains provider and name
- Local model providers may contain endpoint


## Example Configuration
```yaml
stages:
  - name: researcher
    prompt_path: prompts/researchers/techno_news.md
    model: 
        provider: gemini
        name: gemini-2.5-flash
  - name: curator
    prompt_path: prompts/curators/polegroup_techno.md
    model: 
        provider: gemini
        name: gemini-2.5-flash
  - name: writer
    prompt_path: prompts/writers/telegram_brief.md
    model: 
        provider: ollama
        name: gemma4:e4b
        endpoint: http://localhost:11434/api/generate
```
## Behavior
- The pipeline config is loaded at runtime
- Loaded stage definitions preserve the order from config/pipeline.yaml
- The loaded configuration assembles stage instances but does not execute them.
- The prompt path from the config is loaded into its cooresponding stage
- Unknown stage names produce an error
- Missing required stage fields produce an error
- Missing prompt files produce an error

## Validation

### Success Conditions
- A valid pipeline config loads successfully
- Loaded stages preserves YAML order
- Each prompt-driven stage's configured prompt path exists
- The default config/pipeline.yaml defines Researcher, Curator, and Writer in that order

### Failure Conditions
- The config file is missing
- The YAML is malformed
- The config does not contain a stages list
- A stage entry is missing a name
- A prompt-driven stage is missing prompt_path
- A stage name is unknown
- A prompt-driven stage configured prompt file does not exist

## Out of Scope
- Running the full pipeline end to end
- Telegram delivery
- Supporting multiple pipeline config files
- Changing stage behavior beyond using configured prompt paths

## Completion
When implementation is complete, append a build log entry to eval_log.md following the format in AGENTS.md
