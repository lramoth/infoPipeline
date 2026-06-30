# Spec: Configurable Researcher Discovery

## Objective

Source-backed Researcher providers can take their candidate discovery criteria
from pipeline configuration while preserving existing behavior for
configurations that do not declare discovery criteria.

## Background

Model-backed Researcher providers already obtain topic behavior from configured
prompts. Source-backed Researcher providers interact with a specific source and
previously owned both source interaction and the default discovery criteria.
This feature makes source-backed discovery criteria configurable without moving
source interaction, normalization, diagnostics, or error handling out of the
provider.

## Requirements

- A source-backed Researcher provider shall be able to receive configured
  discovery criteria from the stage configuration.
- If no discovery criteria are configured for a source-backed Researcher
  provider, the existing default discovery behavior shall remain unchanged.
- Configured discovery criteria shall affect candidate collection only for the
  source-backed Researcher provider that supports them.
- Model-backed Researcher providers shall continue to use configured prompts
  for discovery behavior.
- Configured discovery criteria shall not change Curator, Writer, Delivery,
  profile selection, prompt path selection, template selection, model
  configuration, ledger behavior, or output validation rules.
- Configuration validation shall reject malformed discovery criteria with a
  readable error before a pipeline run starts.
- Source-backed Researcher providers shall continue to return the existing
  Researcher output contract: an item list whose items can be validated for
  title, URL, and summary.
- Source-backed Researcher providers shall continue to preserve bounded,
  non-secret source context when available.
- Provider failures and diagnostics shall not expose API keys, authentication
  headers, tokens, chat IDs, or environment values.

## Inputs

For the Bandcamp Researcher provider, the optional stage-level `discovery`
configuration may provide the following Bandcamp Discover criteria:

```yaml
stages:
  - name: researcher
    provider: bandcamp
    discovery:
      category_id: 0
      tag_norm_names:
        - hypnotic-techno
        - techno
      geoname_id: 0
      slice: new
      time_facet_id: 0
      cursor: "*"
      size: 24
      include_result_types:
        - a
        - s
```

When present:

- `category_id`, `geoname_id`, `time_facet_id`, and `size` must be integers.
- `slice` and `cursor` must be non-empty strings.
- `tag_norm_names` and `include_result_types` must be non-empty lists of
  non-empty strings.

## Outputs

- A successful source-backed Researcher run returns normalized Researcher items
  using the existing Researcher output contract.
- Bandcamp-backed output preserves inspectable, bounded source context that
  includes the discovery criteria sent to Bandcamp.
- Configuration validation failures are readable and occur before any stage
  runs.

## Behavior

### Normal Flow

1. A Bandcamp Researcher stage with valid discovery criteria loads
   successfully.
2. The Bandcamp Researcher uses the configured discovery criteria when
   collecting candidates from Bandcamp Discover.
3. Bandcamp results are normalized into Researcher items with title, URL, and
   summary.
4. Existing Researcher validation determines whether enough complete items were
   produced.

### Default Flow

1. A Bandcamp Researcher stage with no discovery criteria loads successfully.
2. The Bandcamp Researcher uses the existing default Bandcamp Discover
   criteria.
3. The externally visible request and Researcher output behavior match the
   previous default behavior.

## Failure Handling

- Missing or malformed discovery criteria fields fail configuration loading
  with a readable error before any provider is called.
- Discovery criteria on a model-backed Researcher provider fail configuration
  loading with a readable error.
- Bandcamp network failures and malformed Bandcamp responses continue to fail
  the Researcher stage with readable errors.
- If configured discovery criteria produce fewer than three complete items, the
  existing Researcher validation behavior rejects the stage.

## Acceptance Criteria

- [ ] Bandcamp Researcher loads and runs with configured discovery criteria.
- [ ] Bandcamp Researcher uses the configured discovery criteria in the
      Bandcamp Discover request.
- [ ] Bandcamp Researcher preserves the previous default request behavior when
      discovery criteria are omitted.
- [ ] Invalid discovery criteria are rejected during configuration loading.
- [ ] Model-backed Researcher providers continue to use prompts and reject
      source discovery criteria.
- [ ] Existing Researcher, Curator, Writer, Delivery, profile, prompt,
      template, model, ledger, and validation behavior remains unchanged except
      for the configured source-backed discovery criteria.

## Validation

### Success Conditions

- A controlled Bandcamp run with configured discovery criteria sends those
  criteria to Bandcamp Discover and returns normalized complete items.
- A controlled Bandcamp run without configured discovery criteria sends the
  previous default Bandcamp Discover criteria and returns normalized complete
  items.
- The checked-in default pipeline configuration is loadable.

### Failure Conditions

- Discovery criteria with wrong field types or missing required fields are
  rejected before stages execute.
- Discovery criteria declared for a model-backed Researcher provider are
  rejected before stages execute.

## Constraints

- Do not add dependencies unless required for the feature.
- Do not perform live Gemini, OpenAI, Ollama, Bandcamp, Telegram, or other
  external calls during implementation tests.
- Preserve existing observable behavior unless this spec explicitly changes it.

## Out of Scope

- Adding new Researcher providers.
- Changing Curator, Writer, or Delivery behavior.
- Changing model-backed prompt behavior.
- Adding command-line discovery overrides.
- Performing live provider evaluation.

## Completion

For this build session, append a `## Build log — 2026-06-30` entry to
`eval_log.md` with the spec used, summary of observable work completed,
assumptions made, and gaps or suspected bugs. Do not write an Evaluation entry.
