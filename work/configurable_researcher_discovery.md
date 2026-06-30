# Configurable Researcher Discovery

## Goal

Allow source-backed Researcher providers to obtain their discovery behavior from configuration rather than embedding it in provider code.

Discovery configuration should define the observable candidate collection behavior while preserving the provider's responsibility for interacting with its underlying source.

The feature should improve configurability without changing the responsibilities of the Researcher, Curator, Writer, or Delivery stages.

When no discovery configuration is supplied, the existing discovery behavior should remain available as the default.

Before beginning, read:
- `development_workflow.md`
- `governance.md`
- `architecture.md`

Use those documents to guide all workflow decisions while executing this Work File.

---

## Initial Architectural Review

The current architecture already separates Researcher provider selection from
Curator, Writer, and Delivery responsibilities. Model-backed Researcher
providers obtain prompt-driven discovery behavior from configuration, while the
Bandcamp source-backed provider currently owns both source interaction and the
hardcoded discovery criteria it sends to Bandcamp Discover.

This feature should preserve the Researcher boundary: configuration may define
the observable collection criteria for a source-backed provider, but the
provider should continue to own source-specific request execution,
normalization, diagnostics, and error handling. Configuration validation should
remain the point where invalid configured runtime behavior is rejected before a
pipeline run.

The existing default Bandcamp discovery behavior must remain available when no
discovery configuration is supplied, so current invocations continue to work.
Because the feature changes configuration contracts and documented runtime
behavior, durable documentation updates are current-scope work under
`governance.md`.

---

## Tasks

- Task 1: Add configurable source-backed Researcher discovery
    - Scope: Define a behavioral specification, implement configuration-owned
      discovery behavior for source-backed Researcher providers, preserve the
      existing default behavior when no discovery configuration is supplied,
      keep provider/source responsibilities separated, update applicable
      documentation, and append the required build log entry.
    - Spec: `specs/configurable_researcher_discovery_feature.md`
    - Implementation Summary: Source-backed Bandcamp Researcher discovery can
      now be supplied through optional stage-level configuration and is
      validated before pipeline runs. When no discovery configuration is
      supplied, the prior default Bandcamp discovery behavior remains
      available. Model-backed Researcher providers continue to use prompts, and
      documentation now describes the completed configuration behavior.
    - Implementation Observations:
        - Bandcamp is currently the only source-backed Researcher provider, so
          the implemented discovery contract is scoped to Bandcamp.
        - Discovery configuration is rejected for model-backed Researcher
          providers, which continue to use prompts.
    - Planner Agent Decisions:
        - Author and run an evaluation for
          `specs/configurable_researcher_discovery_feature.md` as the normal
          next workflow step.
        - Record generalized source-backed discovery contracts for future
          consideration if additional source-backed Researcher providers are
          added.
        - Record optional live-provider confirmation for configured Bandcamp
          discovery as future work rather than current scope because the spec
          explicitly excludes live provider evaluation.
    - Tests Run:
        - `python3 -m unittest tests.test_researcher tests.test_pipeline_config`
          — PASS, 61 tests.
        - `python3 -m unittest discover -s tests -t .` — PASS, 160 tests.
        - `python3 planner.py --validate-config` — PASS for
          `techno-releases`.
    - Implementation Commit: `430030e16162cd9997090f77e24687cad5b96725`
    - Eval: `evals/configurable_researcher_discovery_feature.eval.md`
    - Evaluation Authoring Commit: `19145628886f308287c6dd3d14c76b2933896d6c`
    - Result: PASS
    - Evaluation Summary: All 11 evaluation scenarios passed using controlled
      local tests and configuration validation. The evaluation made no live
      Gemini, OpenAI, Ollama, Bandcamp, Telegram, web search, or other external
      calls.
    - Evaluation Commit: `7ceec18e2e1869b09af7c5a81e58a17bd5187e80`
    - Status: Complete.

- Task 2: Reject unsupported Bandcamp discovery keys
    - Origin: Governance Review warning.
    - Scope: Ensure Bandcamp discovery configuration accepts only the
      documented discovery contract, rejects unknown keys before a pipeline run,
      updates the behavioral specification and evaluation coverage as needed,
      and appends the required build log entry.
    - Spec: `specs/configurable_researcher_discovery_feature.md`
    - Implementation Summary: Bandcamp discovery configuration now accepts only
      the documented discovery criteria fields and rejects unsupported fields
      during configuration loading before a pipeline run starts. Valid
      documented discovery configuration and omitted-discovery default behavior
      remain unchanged.
    - Implementation Observations:
        - The rejection is scoped to Bandcamp discovery keys only.
        - No additional current-scope implementation tasks were recommended.
    - Tests Run:
        - `python3 -m unittest tests.test_pipeline_config tests.test_researcher`
          — PASS, 62 tests.
        - `python3 -m unittest discover -s tests -t .` — PASS, 161 tests.
        - `python3 planner.py --validate-config` — PASS for
          `techno-releases`.
    - Implementation Commit: `773d82c28aa42e5e00f677b5ea746c302bf2c0d8`
    - Eval: `evals/configurable_researcher_discovery_feature.eval.md`
    - Status: Implemented; awaiting evaluation execution.

---

## Recommended Future Work Files

- Generalized source-backed Researcher discovery contracts for future
  source-backed providers.
- Optional live-provider confirmation for configured Bandcamp discovery.

---

## Governance

- Result: PASS WITH WARNINGS
- Findings:
    - The feature fits the project architecture: configuration owns discovery
      criteria, Bandcamp owns source interaction and normalization,
      model-backed Researcher providers continue to use prompts, and Curator,
      Writer, and Delivery responsibilities are unchanged.
    - Durable docs, build logs, and evaluation logs are present.
    - Warning: Bandcamp discovery validation checks required documented fields
      but does not reject undocumented extra keys, leaving an undocumented
      configuration surface outside the described contract.
- Planner Agent Decision: Create Task 2 to reject unsupported Bandcamp
  discovery keys and keep the configuration contract narrow and durable.

---

## Final Summary
