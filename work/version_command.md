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
  - Status: Planned
  - Scope: Define and implement observable `--version` behavior for the
    command-line entry point, then evaluate it independently from live provider
    calls.

---

## Recommended Future Work Files

---

## Governance

---

## Final Summary
