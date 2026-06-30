# Eval: Configurable Researcher Discovery

## Purpose

Validate only the observable behavior described in
`specs/configurable_researcher_discovery_feature.md`.

Do not infer requirements that are not stated in the referenced specification.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- file names
- validation-result shapes
- internal data structures or algorithms
- HTTP client implementation choices
- provider client implementation choices

Grade only observable behavior from the perspective of a command-line caller,
configuration author, downstream pipeline stage, or controlled provider endpoint.

## Evaluation Environment

Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Bandcamp, Telegram, web search, or
  other external endpoint calls.
- Do not send Telegram messages or modify external systems.
- Use the real local project configuration together with controlled or
  temporary configuration inputs as needed for each scenario.
- Use mocks, fixtures, or controlled endpoints for provider responses,
  provider request inspection, credentials, delivery providers, ledgers, and
  runtime checks.

Controlled Bandcamp scenarios may observe the outbound Bandcamp Discover
request made by the application, but must not contact live Bandcamp.

## Scenario 1: Configured Bandcamp Discovery Loads And Runs

Given:
- A Researcher stage is configured with the Bandcamp provider.
- The stage declares valid Bandcamp discovery criteria using the fields and
  value types allowed by the specification.
- A controlled Bandcamp Discover response provides at least three complete
  candidate items.

When:
- The selected pipeline configuration is loaded and the Researcher stage is run
  against the controlled Bandcamp response.

Then:
- Configuration loading succeeds.
- The Researcher run succeeds.
- The Researcher output contains normalized items with title, URL, and summary.
- Existing Researcher validation accepts the output and allows the pipeline to
  continue to Curator.

## Scenario 2: Configured Criteria Are Sent To Bandcamp Discover

Given:
- A Bandcamp Researcher stage declares valid discovery criteria with distinct,
  observable values for category, tags, geography, slice, time facet, cursor,
  result size, and included result types.
- The Bandcamp Discover endpoint is replaced with a controlled endpoint that
  records the application request and returns a valid response.

When:
- The Researcher stage collects candidates.

Then:
- The observed Bandcamp Discover request contains the configured discovery
  criteria.
- The configured tag names and included result types are preserved as lists of
  strings.
- The configured integer and string values are preserved with their configured
  meaning.
- The request does not use the previous default criteria instead of the
  configured criteria.

## Scenario 3: Omitted Discovery Uses Previous Default Behavior

Given:
- A Bandcamp Researcher stage is configured without discovery criteria.
- The Bandcamp Discover endpoint is replaced with a controlled endpoint that
  records the application request and returns a valid response.

When:
- The Researcher stage collects candidates.

Then:
- Configuration loading succeeds.
- The observed Bandcamp Discover request uses the previous default discovery
  criteria.
- The run returns normalized items with title, URL, and summary.
- Existing default Bandcamp discovery behavior remains available without
  requiring configuration authors to declare discovery criteria.

## Scenario 4: Source Context Includes Bounded Discovery Criteria

Given:
- A Bandcamp Researcher stage runs with valid configured discovery criteria.
- A controlled Bandcamp response provides complete candidate items and available
  non-secret source context.

When:
- The successful Researcher output, ledger-visible stage result, or diagnostic
  context is inspected.

Then:
- Bounded, inspectable source context is available when the provider supplies
  it.
- The source context includes the Bandcamp discovery criteria sent to Bandcamp.
- The context is limited enough to remain readable and is not an unbounded dump
  of source payloads.
- The context does not expose API keys, authentication headers, tokens, chat
  IDs, or environment values.

## Scenario 5: Malformed Bandcamp Discovery Is Rejected Before Stages Run

Given:
- A Bandcamp Researcher stage declares discovery criteria with one or more
  invalid shapes, such as a non-integer integer field, an empty string for a
  required string field, an empty list for a required list field, or a list item
  that is not a non-empty string.
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

## Scenario 5A: Unsupported Bandcamp Discovery Keys Are Rejected Before Stages Run

Given:
- A Bandcamp Researcher stage declares discovery criteria that include every
  documented Bandcamp discovery field with valid values.
- The same discovery criteria also include an unsupported field that is not part
  of the documented Bandcamp discovery contract.
- Controlled stages and provider endpoints are observable.

When:
- The selected pipeline configuration is loaded or validated.

Then:
- Configuration loading fails before any Researcher, Curator, Writer, or
  Delivery behavior starts.
- The failure reason is readable to a configuration author and identifies that
  unsupported Bandcamp discovery criteria are not accepted.
- No provider endpoint is contacted.
- No ledger is created, overwritten, or updated for a pipeline run.
- No delivery message is produced or sent.

## Scenario 6: Discovery On Model-Backed Researcher Is Rejected

Given:
- A model-backed Researcher provider is selected.
- The Researcher stage also declares source-backed discovery criteria.
- Controlled provider endpoints are observable.

When:
- The selected pipeline configuration is loaded or validated.

Then:
- Configuration loading fails before any pipeline stage starts.
- The failure reason clearly indicates that source-backed discovery criteria
  are not valid for the selected model-backed Researcher provider.
- No model provider endpoint is contacted.
- Prompt-based Researcher behavior is not replaced by source-backed discovery
  criteria.

## Scenario 7: Model-Backed Researcher Prompt Behavior Remains Unchanged

Given:
- A model-backed Researcher provider is selected without source-backed
  discovery criteria.
- The selected profile supplies the configured Researcher prompt behavior.
- A controlled model response provides valid Researcher items.

When:
- The Researcher stage runs.

Then:
- The Researcher uses the configured prompt behavior for discovery.
- The model request behavior remains governed by the existing configured model
  provider contract.
- The Researcher output contains normalized items with title, URL, and summary.
- No Bandcamp discovery criteria are required or sent.

## Scenario 8: Non-Researcher Behavior Remains Unchanged

Given:
- Two otherwise equivalent pipeline configurations differ only by valid
  Bandcamp Researcher discovery criteria.
- Controlled successful Researcher, Curator, Writer, and Delivery behavior is
  available.

When:
- Each pipeline is loaded and run through the controlled successful path.

Then:
- Configured discovery criteria affect only Bandcamp candidate collection.
- Curator behavior remains governed by its configured provider and prompt.
- Writer behavior remains governed by its configured provider, prompt, and
  template.
- Delivery behavior remains governed by the configured delivery providers.
- Profile selection, prompt path selection, template selection, model
  configuration, ledger behavior, and output validation rules remain unchanged
  except for the configured Bandcamp discovery request.

## Scenario 9: Checked-In Default Configuration Is Loadable

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
- The command exits with status code 0.
- No Researcher, Curator, Writer, Delivery, provider endpoint, ledger write, or
  delivery side effect occurs.

## Scenario 10: Bandcamp Source Failures Remain Readable And Halt The Pipeline

Given:
- A Bandcamp Researcher stage is configured with valid discovery criteria.
- The controlled Bandcamp endpoint fails, or returns a malformed response, or
  returns too few complete candidate items.
- Later stages and delivery are observable.

When:
- The pipeline attempts to run.

Then:
- The run fails at the Researcher stage with a readable reason.
- Curator does not run.
- Writer does not run.
- Delivery does not run.
- User-visible errors, ledger-visible results, and diagnostics do not expose
  API keys, authentication headers, tokens, chat IDs, or environment values.

## Scenario 11: Automated Tests Avoid Live External Calls

Given:
- Configurable source-backed Researcher discovery has been implemented.

When:
- The repository's automated implementation tests for this feature are run.

Then:
- Configured Bandcamp discovery request behavior is covered with controlled
  inputs.
- Default Bandcamp discovery behavior is covered with controlled inputs.
- Invalid Bandcamp discovery configuration is covered with controlled inputs.
- Discovery criteria on model-backed Researcher providers are covered with
  controlled inputs.
- Model-backed prompt behavior and downstream pipeline stability are covered.
- No live Gemini, OpenAI, Ollama, Bandcamp, Telegram, web search, or other
  external endpoint call is required.

## Grading instructions

For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append an evaluation entry to `eval_log.md` using the format in `AGENTS.md`:
- eval file used
- PASS/FAIL result for each scenario
- one-sentence product-behavior reason for each scenario result
- overall verdict

Reasons must be written as black-box observable behavior: describe what a
caller, configuration author, downstream stage, or controlled provider endpoint
observes, not internal identifiers, return values, exception names, helper
inputs, file paths, or algorithms.

Overall verdict is PASS only if every scenario passes.

Evaluation sessions must not write build-log entries.
