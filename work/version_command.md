# Version Command

## Goal

Add a `--version` command-line option that reports the application version and exits successfully without running the pipeline.

Before beginning, read:
- `development_workflow.md`
- `governance.md`
- `architecture.md`
Use those documents to guide all workflow decisions while executing this Work File.

---

## Initial Architectural Review

- The application already exposes a command-line entry point through `planner.py`,
  and the architecture defines standard output as the machine-readable command
  result surface for normal pipeline runs.
- The requested `--version` option is a command-line concern and should exit
  before Planner assembles or runs pipeline stages, calls providers, writes a
  ledger, or attempts delivery.
- The version value should be easy for command-line callers to read without
  requiring model, provider, or delivery configuration.
- This feature does not require changes to Researcher, Curator, Writer,
  Delivery, configured prompts, or provider behavior.

---

## Tasks

- Task 1: Add version reporting command-line behavior.
  - Status: Implementation complete; evaluation pending
  - Scope: Define and implement observable `--version` behavior for the
    command-line entry point, then evaluate it independently from live provider
    calls.
  - Iteration 1
    - Spec: `specs/version_command_feature.md`
    - Implementation commit: `678f97c293cb1240e0d8459adef16c415ea1caba`
    - Summary: `python3 planner.py --version` reports `infoPipeline 0.1.0`
      as a single standard-output line, exits successfully, and does not start
      a pipeline run. When provided alongside another supported option, the
      version report is returned without running the pipeline.
    - Implementation observations:
      - The repository did not previously expose a version source.
        - Planner Agent Decision: Accept the implementation assumption that
          the initial application version is `0.1.0` for this feature.
      - Version output is plain text while normal pipeline run output remains
        JSON.
        - Planner Agent Decision: Accept; the requested behavior is a command
          metadata response, not a pipeline result.
      - Centralized version metadata may be useful if packaging or release
        automation is added later.
        - Planner Agent Decision: Recommend Future Work File.

---

## Recommended Future Work Files

- Centralize application version metadata for packaging and release automation
  if the project later adds distribution tooling.

---

## Governance

---

## Final Summary
