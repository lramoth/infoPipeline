# Spec: Provider-Owned Stage Configuration

## Objective

Pipeline stage configuration selects a provider directly, while each provider
owns the provider-specific configuration requirements it needs to run. This
allows model-backed stages to continue requiring model details and allows
source-backed stages, such as Bandcamp Researcher, to run without fake model
names or caller-supplied endpoint details.

## Background

The current stage configuration treats every configured stage provider as a
model-backed provider by requiring a model object with provider, name, and
endpoint. That shape works for Gemini, OpenAI, and Ollama, but it is awkward for
source-backed providers that do not use a model.

The Researcher stage should be able to collect normalized research items from a
source-specific provider while preserving the same Researcher output contract
used by model-backed providers.

## Requirements

### Stage Provider Selection

- Every configured Researcher, Curator, and Writer stage shall declare a
  top-level provider.
- Provider is the mandatory selector for stage behavior.
- Model name and endpoint are mandatory only for providers that require model
  calls.
- Model-backed Researcher providers Gemini and OpenAI shall continue to require
  a configured model name and endpoint.
- Model-backed Curator providers Gemini and OpenAI shall continue to require a
  configured model name and endpoint.
- Writer provider Ollama shall continue to require a configured model name and
  endpoint.
- Source-backed Researcher providers may omit model name and endpoint when the
  selected provider does not require them.
- Unsupported provider and stage combinations shall fail with a readable
  configuration error.
- Supported provider and stage combinations that omit provider-required fields
  shall fail with a readable configuration error.
- Existing profile-owned prompt and template path behavior shall continue for
  providers that use prompts or templates.
- Providers that do not use prompts shall not require caller-supplied prompt
  content to run.
- Profile prompt paths that are present for a provider that does not use prompts
  shall be ignored for that provider.

### Existing Provider Behavior

- Existing Gemini, OpenAI, and Ollama stage capabilities shall remain available
  through the new provider-at-stage configuration shape.
- Existing Researcher, Curator, and Writer output validation rules shall remain
  unchanged.

### Bandcamp Researcher Provider

- Researcher shall support a Bandcamp provider that requires only provider
  selection from pipeline configuration.
- The Bandcamp provider shall not require a configured model name.
- The Bandcamp provider shall not require a configured endpoint.
- The Bandcamp provider shall not require API credentials.
- The Bandcamp provider shall collect items from Bandcamp Discover new releases
  for hypnotic techno and techno.
- The Bandcamp provider shall treat Bandcamp's selected Discover time facet as
  authoritative and shall not apply additional release-date filtering.
- The Bandcamp provider shall normalize Bandcamp results into the existing
  Researcher item contract: title, URL, and summary.
- The Bandcamp provider shall remove Bandcamp discovery tracking query
  parameters from item URLs before returning items.
- The Bandcamp provider shall skip source results that cannot produce a title,
  URL, and summary.
- If fewer than three normalized items remain, the existing Researcher
  validation behavior shall fail the stage.
- The Bandcamp provider shall preserve bounded, non-secret source context when
  useful for diagnostics.

### Bandcamp Source Contract

The Bandcamp provider uses the following Bandcamp Discover request as its
provider-owned source contract:

```text
POST https://bandcamp.com/api/discover/1/discover_web
```

Default request body:

```json
{
  "category_id": 0,
  "tag_norm_names": ["hypnotic-techno", "techno"],
  "geoname_id": 0,
  "slice": "new",
  "time_facet_id": 0,
  "cursor": "*",
  "size": 24,
  "include_result_types": ["a", "s"]
}
```

- `slice: "new"` selects release-oriented Bandcamp Discover results.
- `time_facet_id: 0` represents Bandcamp's today window.
- The request body is owned by the Bandcamp provider, not by pipeline
  configuration.
- Changing the Bandcamp request body is a provider behavior change and should be
  covered by a future spec or explicit spec revision.

## Example Configuration

Model-backed Researcher, Curator, and Writer:

```yaml
stages:
  - name: researcher
    provider: openai
    model:
      name: gpt-4.1-mini
      endpoint: https://api.openai.com/v1/responses
  - name: curator
    provider: openai
    model:
      name: gpt-4.1-mini
      endpoint: https://api.openai.com/v1/responses
  - name: writer
    provider: ollama
    model:
      name: gemma4:e4b
      endpoint: http://localhost:11434/api/generate
```

Source-backed Bandcamp Researcher with model-backed Curator and Writer:

```yaml
stages:
  - name: researcher
    provider: bandcamp
  - name: curator
    provider: openai
    model:
      name: gpt-4.1-mini
      endpoint: https://api.openai.com/v1/responses
  - name: writer
    provider: ollama
    model:
      name: gemma4:e4b
      endpoint: http://localhost:11434/api/generate
```

## Output Contracts

- Researcher output remains valid only when it contains an item list with at
  least three items and every item has a title, URL, and summary.
- Curator output remains valid only when it satisfies the existing Curator
  validation rules.
- Writer output remains valid only when it satisfies the existing Writer
  validation rules.

## Failure Handling

- A stage without a top-level provider fails configuration loading with a
  readable error.
- A model-backed stage missing model name or endpoint fails configuration
  loading with a readable error.
- A Bandcamp Researcher configuration with no model name and no endpoint loads
  successfully.
- Bandcamp network failures fail the Researcher stage with a readable error.
- Malformed Bandcamp responses fail the Researcher stage with a readable error.
- Empty Bandcamp result sets fail the Researcher stage with a readable error or
  existing Researcher validation failure.
- Provider errors and diagnostics must not expose API keys, authentication
  headers, tokens, or environment values.

## Validation

### Success Conditions

- Existing Gemini Researcher and Curator configurations still load and run with
  their existing observable behavior.
- Existing OpenAI Researcher and Curator configurations still load and run with
  their existing observable behavior.
- Existing Ollama Writer configuration still loads and runs with its existing
  observable behavior.
- A Bandcamp Researcher stage configured with only `provider: bandcamp` loads.
- A Bandcamp Researcher stage loads even when the selected profile does not
  declare a Researcher prompt path.
- A Bandcamp Researcher stage loads when unused Researcher prompt paths are
  present in the selected profile.
- A Bandcamp Researcher run with a controlled successful Bandcamp response
  produces normalized Researcher items with title, URL, and summary.
- A Bandcamp Researcher run cleans discovery tracking query parameters from
  returned item URLs.
- Automated implementation tests do not call live Gemini, OpenAI, Ollama,
  Bandcamp, or Telegram endpoints.

### Failure Conditions

- An unsupported provider for Researcher, Curator, or Writer fails with a
  readable error.
- A Gemini, OpenAI, or Ollama stage missing required model configuration fails
  with a readable error.
- A prompt-using provider missing a required prompt or template path fails with
  a readable error.
- A malformed Bandcamp response fails with a readable Researcher error.
- A Bandcamp response with fewer than three normalizable items fails the
  Researcher stage.
- Provider failures do not expose secrets in diagnostics, logs, or user-visible
  error context.

## Out of Scope

- Adding Bandcamp support to Curator or Writer.
- Adding user-configurable Bandcamp tags, slice, time facet, cursor, result
  types, size, or endpoint.
- Adding a Bandcamp weekly provider.
- Adding fallback from Bandcamp to Gemini or OpenAI.
- Changing Researcher, Curator, or Writer validation rules.
- Changing prompt or template content.
- Requiring live external API calls during implementation tests.

## Completion

When implementation is complete, append a build log entry to eval_log.md
following the format in AGENTS.md.
