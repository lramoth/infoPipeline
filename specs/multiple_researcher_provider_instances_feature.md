# Spec: Multiple Researcher Provider Instances

## Objective

The configured pipeline can run more than one flat `researcher` stage before
Curator, combine their normalized candidate items, remove duplicates, and pass
one ordered candidate pool to Curator.

## Background

The pipeline currently treats Researcher as the configured candidate collection
stage. Researcher providers normalize provider-specific collection output into
items with title, URL, and summary before downstream stages run. This feature
extends configured stage behavior so multiple independently configured
Researcher entries can contribute candidates to the same Curator run without
introducing nested configuration.

## Requirements

- Pipeline configuration shall continue to declare Researcher stages as flat
  `name: researcher` entries in the existing top-level `stages` list.
- The system shall support more than one configured Researcher stage before
  Curator.
- Each configured Researcher stage shall run independently using its own
  provider configuration.
- Each Researcher provider shall remain responsible for its own collection
  behavior, normalization, diagnostics, and error handling.
- The normalized items from all successful Researcher stages before Curator
  shall be combined into one candidate pool before Curator runs.
- The combined candidate pool shall be deduplicated before Curator receives it.
- Deduplication shall preserve the first occurrence according to configured
  Researcher stage order and item order within each Researcher result.
- When only one Researcher stage is configured, existing single-Researcher
  behavior shall remain unchanged.
- A Researcher stage failure shall halt the pipeline before later Researcher
  stages, Curator, Writer, and Delivery run.
- If the deduplicated candidate pool fails the existing Researcher output
  validation requirements, Curator shall not run.
- Repeated Researcher stages and their outcomes shall remain readable in
  command-line failures, ledgers, and diagnostics.
- The default checked-in configuration shall use two Bandcamp Researcher stages,
  each with its own valid stage-level Bandcamp `discovery` object.
- The public configuration shall not introduce nested Researcher structures
  such as `researcher.instances`, `researcher.providers`, or
  `discovery_sources`.
- Existing Curator, Writer, Delivery, profile selection, prompt path selection,
  template selection, model configuration, validation command, and version
  command behavior shall remain unchanged except for receiving the deduplicated
  Researcher candidate pool.
- Provider failures and diagnostics shall not expose API keys, authentication
  headers, tokens, chat IDs, or environment values.

## Inputs

Multiple Researcher stages are configured by repeating flat entries in the
top-level `stages` list before Curator:

```yaml
stages:
  - name: researcher
    provider: bandcamp
    discovery:
      category_id: 0
      tag_norm_names:
        - hypnotic-techno
      geoname_id: 0
      slice: new
      time_facet_id: 0
      cursor: "*"
      size: 24
      include_result_types:
        - a
        - s
  - name: researcher
    provider: bandcamp
    discovery:
      category_id: 0
      tag_norm_names:
        - dub-techno
      geoname_id: 0
      slice: new
      time_facet_id: 0
      cursor: "*"
      size: 24
      include_result_types:
        - a
        - s
  - name: curator
    provider: openai
    model:
      name: gpt-4.1-mini
      endpoint: https://api.openai.com/v1/responses
```

Each repeated Researcher entry uses the existing provider-specific
configuration contract for its selected provider.

## Outputs

- A successful multi-Researcher run passes one provider-neutral Researcher
  output to Curator.
- The Researcher output visible to Curator contains the deduplicated normalized
  candidate items.
- Ledger and diagnostic records remain readable for repeated Researcher stages,
  including which Researcher stage failed when a failure occurs.
- Command-line success and failure results keep their existing parseable JSON
  format.
- `--validate-config` reports success for valid repeated flat Researcher
  entries and reports readable failures for invalid stage configuration.

## Behavior

### Normal Flow

1. The configured pipeline is loaded from the flat `stages` list.
2. Each consecutive Researcher stage before Curator runs independently in
   configured order.
3. Each successful Researcher stage produces normalized items using the existing
   Researcher item contract.
4. The successful Researcher outputs are combined in configured order.
5. Duplicate items are removed while preserving the earliest occurrence.
6. The deduplicated candidate pool is validated with the existing Researcher
   validation requirements.
7. Curator runs once with the deduplicated candidate pool.
8. Writer and Delivery continue through the existing configured behavior after
   Curator succeeds.

### Single-Researcher Flow

1. A pipeline with one configured Researcher stage runs as it did before this
   feature.
2. Curator receives the same observable Researcher output it would have
   received before this feature.
3. Existing ledger, CLI, validation, and downstream behavior remain unchanged.

### Duplicate Handling

- When two or more Researcher outputs contain items with the same normalized
  URL, the first occurrence is kept.
- Later duplicate occurrences are omitted from the candidate pool given to
  Curator.
- Non-duplicate items preserve their relative order from the configured
  Researcher stage order and item order within each stage.

## Failure Handling

- Invalid repeated Researcher configuration fails configuration loading with a
  readable error before stages run.
- If any Researcher stage raises a provider error or returns invalid output,
  the pipeline fails at that Researcher stage and does not run later Researcher
  stages, Curator, Writer, or Delivery.
- If deduplication leaves fewer than three complete candidate items, the
  pipeline fails before Curator with a readable validation reason.
- Multi-Researcher failures shall not expose API keys, authentication headers,
  tokens, chat IDs, or environment values.

## Acceptance Criteria

- [ ] Configuration supports repeated flat `researcher` entries before Curator.
- [ ] Each configured Researcher stage runs independently with its own provider
      configuration.
- [ ] Curator receives one combined candidate pool from all successful
      Researcher stages.
- [ ] Duplicate candidate items are removed before Curator receives the pool.
- [ ] Deduplication preserves first occurrence by Researcher stage order and
      item order.
- [ ] Existing single-Researcher behavior remains unchanged.
- [ ] Researcher-stage failures halt before Curator, Writer, and Delivery.
- [ ] Too few complete unique candidates after deduplication halt before
      Curator with a readable reason.
- [ ] Repeated Researcher stage records remain readable in ledgers, CLI
      failures, and diagnostics.
- [ ] The checked-in default configuration uses two Bandcamp Researcher stages
      with separate valid `discovery` objects.
- [ ] Documentation describes the repeated flat Researcher-stage configuration
      contract.

## Validation

### Success Conditions

- A controlled multi-Researcher run demonstrates that two configured
  Researchers run before Curator and that Curator receives one deduplicated
  candidate pool.
- A controlled duplicate scenario demonstrates that the first occurrence is
  preserved by configured Researcher stage order and item order.
- A controlled single-Researcher run demonstrates unchanged observable behavior.
- `python3 planner.py --validate-config` succeeds for the checked-in default
  configuration.

### Failure Conditions

- A failing Researcher stage halts before later Researcher stages, Curator,
  Writer, and Delivery.
- A deduplicated candidate pool with fewer than three complete unique items is
  rejected before Curator.
- Invalid provider-specific configuration for any repeated Researcher stage is
  rejected before stages run.

## Constraints

- Do not add dependencies unless required for the feature.
- Do not perform live Gemini, OpenAI, Ollama, Bandcamp, Telegram, web search,
  or other external calls during implementation tests.
- Preserve existing observable behavior unless this spec explicitly changes it.
- Do not introduce nested Researcher configuration structures.

## Out of Scope

- Adding new Researcher providers.
- Changing provider-specific collection, normalization, diagnostics, or error
  handling except as needed to preserve existing contracts under repeated
  Researcher execution.
- Changing Curator ranking behavior.
- Changing Writer formatting behavior.
- Changing Delivery transport behavior.
- Adding command-line overrides for Researcher instances.
- Performing live provider evaluation.

## Completion

For implementation sessions, report results to the Planner Agent for recording
in the Work File.

The implementation report must include:

- spec used
- summary of observable work completed
- tests or checks run
- assumptions made
- limitations or gaps
- future work recommendations, when applicable

Implementation sessions must not evaluate correctness against the specification.
