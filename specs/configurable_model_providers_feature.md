# Spec: Configurable Model Providers

## Objective
Model-backed pipeline stages use the model provider and model name selected in
the pipeline configuration, so supported providers can be switched without
changing Python source code.

## Background
The pipeline configuration already contains a model object for each configured
stage. The model object includes a provider and a name, and local providers may
also include an endpoint.

Researcher and Curator currently use Gemini. Writer currently uses local
Ollama. This feature keeps those existing provider paths available while adding
OpenAI support for Researcher and Curator and explicit provider handling for
Writer.

## Requirements
- The configured model provider and model name are used when a model-backed
  stage runs.
- Researcher supports the Gemini and OpenAI providers.
- Curator supports the Gemini and OpenAI providers.
- Writer has provider selection behavior and supports only the Ollama provider
  for this feature.
- Gemini remains a supported provider for Researcher and Curator.
- Ollama remains the supported provider for Writer.
- OpenAI can be selected for Researcher and Curator by configuring provider
  `openai` and a model name.
- Researcher uses provider search capability when the selected provider
  supports search.
- Curator applies the configured curation prompt to the Researcher output using
  the selected provider.
- Unsupported provider and stage combinations fail with a readable error.
- Missing credentials required by the selected provider fail with a readable
  error before a successful provider response is expected.
- Provider credentials are loaded from the project environment configuration.
- OpenAI calls use `OPENAI_API_KEY` from the project environment configuration.
- Existing Gemini calls continue to use `GEMINI_API_KEY` from the project
  environment configuration.
- Writer's Ollama provider does not require an API key.
- Diagnostics and error reporting identify the selected provider and configured
  model when provider context is available.
- Diagnostics and error reporting must not expose API keys, tokens,
  authentication headers, or environment values.
- Automated implementation tests must not call live Gemini, OpenAI, Ollama, or
  Telegram endpoints.

## Output Contracts
- Researcher output remains valid when it contains an item list with at least
  three items, and every item has a title, URL, and summary.
- Researcher returns provider grounding or source metadata when the selected
  provider makes it available.
- Curator output remains valid when it contains at least one curated item, each
  curated item has the required curated fields, and at least one item has rank
  1.
- Writer output remains the assembled outbound message using the configured
  Writer prompt, configured Writer template, curated item titles, curated item
  URLs, and model-generated item prose.

## Example Configuration

Gemini Researcher and Curator with Ollama Writer:

```yaml
stages:
  - name: researcher
    model:
      provider: gemini
      name: gemini-2.5-flash
  - name: curator
    model:
      provider: gemini
      name: gemini-2.5-flash
  - name: writer
    model:
      provider: ollama
      name: gemma4:e4b
      endpoint: http://localhost:11434/api/generate
```

OpenAI Researcher and Curator with Ollama Writer:

```yaml
stages:
  - name: researcher
    model:
      provider: openai
      name: gpt-4.1-mini
  - name: curator
    model:
      provider: openai
      name: gpt-4.1-mini
  - name: writer
    model:
      provider: ollama
      name: gemma4:e4b
      endpoint: http://localhost:11434/api/generate
```

## Validation

### Success Conditions
- A valid configuration using Gemini for Researcher and Curator still loads and
  runs with the existing observable stage output contracts.
- A valid configuration using OpenAI for Researcher and Curator loads and runs
  with the existing observable stage output contracts.
- A valid configuration using Ollama for Writer loads and runs with the
  existing observable Writer output contract.
- Switching Researcher or Curator between Gemini and OpenAI requires only
  configuration and environment changes, not source-code changes.
- Provider failures are reported with readable messages that identify the
  selected provider when provider context is available.
- Missing selected-provider credentials are reported with readable messages.
- Automated tests verify provider behavior without live external service calls.

### Failure Conditions
- A Researcher configured with an unsupported provider fails with a readable
  error.
- A Curator configured with an unsupported provider fails with a readable error.
- A Writer configured with a provider other than Ollama fails with a readable
  error.
- A stage configured with a supported provider but missing required credentials
  fails with a readable error.
- Provider errors do not expose secrets in diagnostics, logs, or user-visible
  error context.

## Out of Scope
- Adding OpenAI support to Writer.
- Removing Gemini support.
- Removing Ollama support.
- Adding delivery providers.
- Changing Researcher, Curator, or Writer validation rules beyond provider
  selection behavior.
- Changing prompt or template content.
- Requiring live external API calls during implementation tests.

## Completion
When implementation is complete, append a build log entry to eval_log.md
following the format in AGENTS.md.
