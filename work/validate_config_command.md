# Validate Config Command

## Goal

Add a `--validate-config` command-line option that checks whether the configured pipeline can be loaded and reports success or failure without running the pipeline, calling providers, writing a ledger, or attempting delivery.

Before beginning, read:

- `development_workflow.md`
- `governance.md`
- `architecture.md`

Use those documents to guide all workflow decisions while executing this Work File.

---

## Initial Architectural Review

- The application already exposes a command-line entry point through `planner.py`.
  The architecture defines standard output as the machine-readable command result
  surface and treats configuration loading as a step that happens before any
  pipeline stage runs, calls providers, writes a ledger, or attempts delivery.
- Configuration loading and assembly are already separated from execution. The
  configuration loading path validates the profile selection, assembles each
  configured stage, confirms required model settings, and confirms that
  configured prompt and template files exist. A readable error is raised when the
  configuration cannot be loaded or assembled. The requested `--validate-config`
  option should exercise this existing load-and-assemble path and report its
  result, without advancing into a pipeline run.
- Like the existing `--version` option, `--validate-config` is a command-line
  concern. It should resolve before Planner runs stages, so it must not call
  Researcher, Curator, Writer, or Delivery providers, must not write a ledger,
  and must not attempt delivery. Validating configuration loadability does not
  require live provider credentials or network access.
- Profile selection already exists through `--profile`. Validation should respect
  a selected profile so an operator can confirm a specific profile loads,
  defaulting to the configured default profile when none is selected, consistent
  with normal run behavior.
- The result must be observable to a command-line caller: a readable success or
  failure report and an exit status that agrees with the reported outcome,
  consistent with the architecture's command-line result contract.
- This feature does not require changes to Researcher, Curator, Writer, Delivery,
  configured prompts, provider behavior, or the configuration file format. It is
  a read-only inspection of configuration loadability.

---

## Tasks

- Task 1: Add configuration validation command-line behavior.
  - Status: Pending
  - Scope: Define and implement observable `--validate-config` behavior for the
    command-line entry point — load and assemble the configured pipeline for the
    selected (or default) profile, report success or failure to the caller with
    an agreeing exit status, and do so without running the pipeline, calling
    providers, writing a ledger, or attempting delivery. Then evaluate it
    independently from live provider calls.

---

## Recommended Future Work Files

---

## Governance

---

## Final Summary
