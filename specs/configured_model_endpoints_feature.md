# Spec: Configured Model Endpoints

## Objective
Model provider endpoints are selected from pipeline configuration rather than
implicit source defaults, so provider endpoint changes can be made without
changing Python source code.

## Background
The pipeline configuration already contains a model object for each configured
model-backed stage. The model object includes a provider and a model name, and
some stage entries already include an endpoint.

Researcher and Curator support Gemini and OpenAI providers. Writer supports
Ollama for this feature set. Each provider has a service endpoint that should
be visible in configuration alongside the selected provider and model name.

## Requirements
- Each configured model-backed stage model object contains provider, name, and
  endpoint.
- The default pipeline configuration declares endpoints for Researcher,
  Curator, and Writer.
- Gemini Researcher and Curator configuration declares the Gemini model service
  endpoint.
- OpenAI Researcher and Curator configuration can declare the OpenAI model
  service endpoint.
- Ollama Writer configuration declares the local Ollama generation endpoint.
- A configured stage uses the endpoint declared in pipeline configuration when
  contacting its selected provider.
- Switching a provider endpoint requires only a configuration change, not a
  Python source-code change.
- A configured model-backed stage with a missing endpoint fails during
  configuration loading with a readable error.
- A configured model-backed stage with an empty or non-string endpoint fails
  during configuration loading with a readable error.
- Provider failures and diagnostics continue to report the endpoint used for
  the attempted provider call without exposing credentials.
- Existing provider support remains unchanged:
  - Researcher supports Gemini and OpenAI.
  - Curator supports Gemini and OpenAI.
  - Writer supports Ollama only.
- Automated implementation tests must not call live Gemini, OpenAI, Ollama, or
  Telegram endpoints.

## Example Configuration

Gemini Researcher and Curator with Ollama Writer:

```yaml
stages:
  - name: researcher
    model:
      provider: gemini
      name: gemini-2.5-flash
      endpoint: https://generativelanguage.googleapis.com/v1beta/models
  - name: curator
    model:
      provider: gemini
      name: gemini-2.5-flash
      endpoint: https://generativelanguage.googleapis.com/v1beta/models
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
      endpoint: https://api.openai.com/v1/responses
  - name: curator
    model:
      provider: openai
      name: gpt-4.1-mini
      endpoint: https://api.openai.com/v1/responses
  - name: writer
    model:
      provider: ollama
      name: gemma4:e4b
      endpoint: http://localhost:11434/api/generate
```

## Validation

### Success Conditions
- The default pipeline configuration loads successfully with endpoints declared
  for Researcher, Curator, and Writer.
- A valid configuration using Gemini endpoints for Researcher and Curator loads
  successfully.
- A valid configuration using OpenAI endpoints for Researcher and Curator loads
  successfully.
- A valid configuration using an Ollama endpoint for Writer loads successfully.
- Controlled provider-call checks show that each configured stage attempts to
  use the endpoint declared in configuration.
- Existing stage output contracts remain unchanged.
- Automated tests verify endpoint behavior without live external service calls.

### Failure Conditions
- A configured model-backed stage missing an endpoint fails during
  configuration loading with a readable error.
- A configured model-backed stage with an empty endpoint fails during
  configuration loading with a readable error.
- A configured model-backed stage with a non-string endpoint fails during
  configuration loading with a readable error.
- Provider failure diagnostics do not expose API keys, tokens, authentication
  headers, or environment values.

## Out of Scope
- Adding new model providers.
- Adding OpenAI support to Writer.
- Removing Gemini, OpenAI, or Ollama provider support.
- Changing provider credentials.
- Changing prompt or template content.
- Changing Researcher, Curator, or Writer validation rules beyond endpoint
  configuration behavior.
- Requiring live external API calls during implementation tests.

## Completion
When implementation is complete, append a build log entry to eval_log.md
following the format in AGENTS.md.
