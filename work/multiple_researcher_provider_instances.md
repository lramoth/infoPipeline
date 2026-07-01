# Multiple Researcher Provider Instances

## Goal

Allow the configured pipeline to execute more than one Researcher stage before
Curator.

Each configured Researcher stage should run independently using its own
provider configuration.

The normalized candidate output from all configured Researcher stages should be
combined into one candidate pool before Curator runs.

The combined candidate pool should be deduplicated before Curator receives it.

Deduplication should preserve the first occurrence according to configured
Researcher stage order and item order within each Researcher result.

When only one Researcher stage is configured, existing single-Researcher
behavior should remain unchanged.

Each Researcher provider should remain responsible for its own collection
behavior, normalization, diagnostics, and error handling.

## Director Intent

The public configuration should remain repeated flat `researcher` stage entries
in the existing `stages` list.

Do not introduce nested configuration structures such as `researcher.instances`,
`researcher.providers`, or `discovery_sources`.

The initial implementation should use two Bandcamp Researcher stages, each with
its own stage-level Bandcamp `discovery` object.

---

## Initial Architectural Review

The configured pipeline already loads stage entries from the flat `stages`
list in YAML order, and Researcher providers already own provider-specific
collection, normalization, diagnostics, and error handling. The current runtime
passes each successful stage output directly to the next stage, which supports
the single-Researcher pipeline but does not yet expose the requested behavior
when multiple flat `researcher` entries appear before Curator.

This feature should preserve the existing provider boundary: each configured
Researcher entry runs as an independent Researcher using its own provider
configuration, while the runtime exposes a provider-neutral candidate pool to
Curator. The externally important behavior is ordered aggregation and
deduplication of normalized candidate items before Curator runs. The exact
internal representation of repeated stages, aggregation, and ledger storage is
left to implementation as long as command-line behavior, validation, diagnostics,
and durable records remain readable to operators.

Because the requested initial configuration changes the default configured
pipeline and public configuration behavior, durable product documentation must
be updated with the repeated flat Researcher-stage contract.

## Implementation

- Scope: Define a behavioral specification, implement multiple independent
  Researcher stage execution from repeated flat `researcher` entries, combine
  and deduplicate normalized candidates in configured order before Curator,
  preserve single-Researcher behavior, and update applicable documentation and
  default configuration.
- Spec: `specs/multiple_researcher_provider_instances_feature.md`
- Implementation Summary: Repeated flat Researcher stages now run
  independently before Curator. Successful Researcher outputs are combined in
  configured order, deduplicated by normalized URL with first occurrence
  preserved, and passed to Curator as one candidate pool. Single-Researcher
  behavior remains on its existing path. Researcher failures and
  too-few-unique-candidate pools halt before Curator, Writer, and Delivery.
  Repeated Researcher outcomes are readable in the ledger, and the default
  configuration now declares two Bandcamp Researcher stages with separate valid
  discovery objects. Durable documentation was updated.
- Implementation Observations:
    - Repeated Researcher aggregation applies to consecutive flat `researcher`
      stages before Curator.
    - Duplicate candidates are identified by the normalized `url` field already
      required by the Researcher output contract.
    - The combined candidate pool is validated with the existing Researcher
      output requirements before Curator runs.
    - No new dependencies were added.
- Tests Run:
    - `python3 -m unittest tests.test_planner tests.test_pipeline_config` —
      PASS.
    - `python3 planner.py --validate-config` — PASS.
    - `python3 -m unittest discover -s tests -t .` — PASS.
- Assumptions:
    - Repeated Researcher aggregation applies to consecutive flat `researcher`
      stages before Curator.
    - Duplicate detection uses the normalized `url` field.
    - Combined candidate validation uses the existing Researcher output
      contract.
- Limitations:
    - Live Gemini, OpenAI, Ollama, Bandcamp, Telegram, web search, and other
      external calls were not run during implementation.
    - The implementation does not add nested Researcher configuration or
      command-line overrides for Researcher instances.
- Future Work:
    - Run live provider confirmation only if a future evaluation plan
      explicitly requires external calls.
- Eval: `evals/multiple_researcher_provider_instances_feature.eval.md`
- Result: PASS
- Evaluation Summary: All 10 evaluation scenarios passed. The evaluation
  confirmed repeated flat Researcher configuration, independent ordered
  collection, one deduplicated candidate pool for Curator, first-occurrence
  duplicate preservation, single-Researcher compatibility, Researcher failure
  handling, too-few-unique-candidate rejection, default configuration
  validation, readable operator records, and controlled automated coverage
  without live external calls.
- Status: Complete.

## Planner Agent Decisions

- Treat the configured `stages` order as the public ordering contract for
  multiple Researcher stages.
- Require deduplication before Curator receives candidates, preserving the
  first occurrence by Researcher stage order and item order within each
  Researcher output.
- Require readable ledger/CLI/diagnostic behavior for repeated Researcher
  stages without prescribing a storage shape.
- Keep live Gemini, OpenAI, Ollama, Bandcamp, Telegram, web search, and other
  external calls out of implementation and evaluation unless a future Director
  request explicitly requires them.

## Assumptions

- Candidate duplicates can be identified by an observable source identity,
  primarily the normalized item URL, because every valid Researcher item already
  requires a URL.
- The default configured implementation can demonstrate the feature with two
  Bandcamp Researcher entries using distinct valid stage-level `discovery`
  objects.

## Risks

- Repeated stage names currently need readable operator-facing records that do
  not hide earlier Researcher runs.
- Deduplication must not strip provider-owned diagnostics or make it difficult
  to identify which Researcher stage failed.
- Configurations with fewer than three complete unique candidates after
  deduplication must halt before Curator using the existing Researcher
  validation expectation.

## Specification

- `specs/multiple_researcher_provider_instances_feature.md`

## Evaluation

- `evals/multiple_researcher_provider_instances_feature.eval.md`

## Evaluation Results

- Eval file used: `evals/multiple_researcher_provider_instances_feature.eval.md`
- Scenario 1, Repeated Flat Researcher Entries Validate: PASS — a valid
  configuration with two flat Researcher entries is accepted during validation
  without requiring nested configuration or causing runtime side effects.
- Scenario 2, Independent Researchers Feed One Curator Pool: PASS — two
  configured Researchers contribute independently ordered candidates, and
  Curator receives one combined candidate pool before downstream work
  continues.
- Scenario 3, Deduplication Preserves First Occurrence: PASS — duplicate
  candidate URLs are reduced to the earliest candidate while preserving the
  order of the remaining unique candidates.
- Scenario 4, Single Researcher Behavior Remains Unchanged: PASS — a
  one-Researcher pipeline still presents the same candidate output to Curator
  and keeps the existing run behavior.
- Scenario 5, Researcher Failure Halts Before Later Work: PASS — a failing
  Researcher stops the run before later collection, curation, writing, or
  delivery, with readable failure reporting and no observed secret exposure.
- Scenario 6, Too Few Unique Candidates Halt Before Curator: PASS — when unique
  complete candidates fall below the minimum after combining, the run stops
  before Curator with a readable validation reason.
- Scenario 7, Default Configuration Uses Two Bandcamp Researchers: PASS —
  default configuration validation succeeds, identifies the selected profile,
  includes two flat Bandcamp Researcher stages with separate discovery settings,
  and exits successfully without running the pipeline.
- Scenario 8, Invalid Repeated Researcher Configuration Is Rejected: PASS —
  invalid repeated Researcher configuration is rejected before any pipeline
  stage or delivery behavior begins.
- Scenario 9, Operator Records Remain Readable For Repeated Researchers: PASS
  — operator records remain readable for repeated Researchers, preserve earlier
  successful outcomes, and clearly indicate the failing repeated Researcher
  without observed secret exposure.
- Scenario 10, Automated Tests Avoid Live External Calls: PASS — automated
  checks cover multi-Researcher aggregation, duplicate ordering,
  single-Researcher compatibility, failure paths, too-few-candidate rejection,
  and default validation without requiring live external calls.
- Overall verdict: PASS.

## Final Summary

- Outcome: Complete pending Director acceptance.
- Completed Behavior: The configured pipeline can now use repeated flat
  `researcher` entries before Curator. Each Researcher runs independently with
  its own provider configuration, successful normalized items are combined in
  configured order, duplicates by normalized URL are removed with the first
  occurrence preserved, and Curator receives one deduplicated candidate pool.
  Single-Researcher behavior remains unchanged. Researcher failures and
  too-few-unique-candidate pools halt before Curator, Writer, and Delivery with
  readable reporting. The checked-in default configuration uses two Bandcamp
  Researcher stages with separate discovery settings.
- Evidence: Implementation checks passed, `python3 planner.py
  --validate-config` passed for the checked-in default configuration, the full
  automated suite passed, and independent evaluation passed all 10 scenarios
  without live external calls.
- Director Action: Review the completed Work File and branch, then accept,
  reject, or request additional work.
