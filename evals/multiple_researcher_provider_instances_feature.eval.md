# Eval: Multiple Researcher Provider Instances

## Purpose

Validate only the observable behavior described in
`specs/multiple_researcher_provider_instances_feature.md`.

Do not infer requirements that are not stated in the referenced specification.

Do not grade or report implementation details, including:
- class names
- method names
- helper modules
- file names
- return-value shapes
- internal data structures
- helper inputs
- algorithms

Write scenario results from the perspective of a command-line caller,
configuration author, downstream pipeline stage, operator reading artifacts, or
controlled provider endpoint.

## Evaluation Environment

Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Bandcamp, Telegram, web search, or
  other external endpoint calls.
- Do not send Telegram messages or modify external systems.
- Use the real local project configuration together with controlled or
  temporary configuration inputs as needed for each scenario.
- Use mocks, fixtures, or controlled endpoints for provider responses, provider
  request inspection, credentials, delivery providers, ledgers, and runtime
  checks.

## Scenario 1: Repeated Flat Researcher Entries Validate

Given:
- A pipeline configuration declares two flat top-level `researcher` entries
  before Curator.
- Each Researcher entry has a supported provider and valid provider-specific
  configuration.

When:
- The selected configuration is loaded or validated without running provider
  calls.

Then:
- Configuration loading succeeds.
- The Researcher entries are accepted as repeated flat stages.
- No nested Researcher configuration structure is required or used.
- No provider endpoint, ledger, or delivery side effect occurs during
  validation.

## Scenario 2: Independent Researchers Feed One Curator Pool

Given:
- Two configured Researcher stages before Curator each produce complete
  normalized candidate items.
- Curator is observable through controlled local behavior.

When:
- The pipeline runs through the controlled successful path.

Then:
- Each Researcher stage runs independently in configured order.
- Curator runs once after the Researcher stages succeed.
- Curator receives one combined provider-neutral candidate pool containing
  items from both Researcher stages.
- Writer and Delivery behavior remains governed by the existing downstream
  contracts after Curator succeeds.

## Scenario 3: Deduplication Preserves First Occurrence

Given:
- Multiple Researcher stages produce complete normalized candidate items.
- At least one later item has the same normalized URL as an earlier item.
- Additional non-duplicate items appear before and after the duplicate.

When:
- The pipeline combines Researcher results before Curator.

Then:
- Curator receives only one candidate for the duplicated URL.
- The kept candidate is the earliest occurrence by configured Researcher stage
  order and item order.
- Non-duplicate candidates preserve their relative order.

## Scenario 4: Single Researcher Behavior Remains Unchanged

Given:
- A pipeline configuration declares exactly one Researcher stage before Curator.
- Controlled successful Researcher, Curator, Writer, and Delivery behavior is
  available.

When:
- The pipeline runs through the controlled successful path.

Then:
- Curator receives the same observable Researcher output it would receive from
  a single-Researcher pipeline.
- Existing command-line result, ledger, validation, and downstream behavior
  remain unchanged.

## Scenario 5: Researcher Failure Halts Before Later Work

Given:
- Multiple Researcher stages are configured before Curator.
- One Researcher stage fails or returns invalid output.
- Later Researcher stages, Curator, Writer, and Delivery are observable.

When:
- The pipeline runs.

Then:
- The run fails at the failing Researcher stage with a readable reason.
- Later Researcher stages do not run.
- Curator does not run.
- Writer does not run.
- Delivery does not run.
- User-visible errors, ledger-visible results, and diagnostics do not expose
  API keys, authentication headers, tokens, chat IDs, or environment values.

## Scenario 6: Too Few Unique Candidates Halt Before Curator

Given:
- Multiple Researcher stages return enough raw complete items before
  deduplication.
- Deduplication leaves fewer than three complete unique candidate items.
- Curator, Writer, and Delivery are observable.

When:
- The pipeline combines and validates the Researcher candidate pool.

Then:
- The run fails before Curator with a readable validation reason.
- Curator does not run.
- Writer does not run.
- Delivery does not run.

## Scenario 7: Default Configuration Uses Two Bandcamp Researchers

Given:
- The checked-in default pipeline configuration is present.
- The prompt and template files referenced by the selected default profile are
  present.

When:
- The command-line application is invoked with `--validate-config` and no
  profile is selected.

Then:
- Standard output contains a readable machine-parseable result indicating that
  configuration validation succeeded.
- The validated profile is identified.
- The configuration includes two flat Bandcamp Researcher stages with separate
  valid stage-level discovery objects before Curator.
- The command exits with status code 0.
- No Researcher, Curator, Writer, Delivery, provider endpoint, ledger write, or
  delivery side effect occurs.

## Scenario 8: Invalid Repeated Researcher Configuration Is Rejected

Given:
- A pipeline configuration declares repeated Researcher stages.
- At least one repeated Researcher stage has invalid provider-specific
  configuration.
- Controlled stages and provider endpoints are observable.

When:
- The selected pipeline configuration is loaded or validated.

Then:
- Configuration loading fails before any Researcher, Curator, Writer, or
  Delivery behavior starts.
- The failure reason is readable to a configuration author.
- No provider endpoint is contacted.
- No ledger is created, overwritten, or updated for a pipeline run.
- No delivery message is produced or sent.

## Scenario 9: Operator Records Remain Readable For Repeated Researchers

Given:
- Multiple Researcher stages are configured before Curator.
- Controlled execution produces either a successful multi-Researcher candidate
  pool or a Researcher-stage failure.

When:
- The command-line result, ledger, and any diagnostic artifact are inspected.

Then:
- Repeated Researcher stage outcomes are readable to an operator.
- A Researcher-stage failure identifies which configured Researcher stage
  failed clearly enough for an operator to locate the failing stage.
- The records do not hide successful earlier Researcher outcomes behind a later
  repeated stage with the same public stage name.
- The records do not expose API keys, authentication headers, tokens, chat IDs,
  or environment values.

## Scenario 10: Automated Tests Avoid Live External Calls

Given:
- Multiple Researcher provider instances have been implemented.

When:
- The repository's automated implementation tests for this feature are run.

Then:
- Multi-Researcher aggregation is covered with controlled inputs.
- Deduplication order is covered with controlled inputs.
- Single-Researcher compatibility is covered with controlled inputs.
- Researcher failure and too-few-unique-candidates behavior are covered with
  controlled inputs.
- Default configuration validation is covered.
- No live Gemini, OpenAI, Ollama, Bandcamp, Telegram, web search, or other
  external endpoint call is required.

## Grading instructions

For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Report evaluation results to the Planner Agent for recording in the Work File.
The report must include:

- eval file used
- PASS/FAIL result for each scenario
- one-sentence product-behavior reason for each scenario result
- overall verdict

Reasons must be written as black-box observable behavior: describe what a
caller, configuration author, downstream stage, operator, or controlled provider
endpoint observes, not internal identifiers, return values, exception names,
helper inputs, file paths, or algorithms.

Overall verdict is PASS only if every scenario passes.

Evaluation sessions must not modify implementation.
