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
  - Status: Implementation complete; evaluation pending
  - Scope: Define and implement observable `--validate-config` behavior for the
    command-line entry point — load and assemble the configured pipeline for the
    selected (or default) profile, report success or failure to the caller with
    an agreeing exit status, and do so without running the pipeline, calling
    providers, writing a ledger, or attempting delivery. Then evaluate it
    independently from live provider calls.
  - Iteration 1
    - Spec: `specs/validate_config_command_feature.md`
    - Implementation commit: `663f57c2ca48ddc791c7a9fe969f5a42319c8434`
    - Summary: `--validate-config` loads and assembles the configured pipeline
      for the resolved profile and reports the result to standard output without
      running the pipeline, calling any provider, writing a ledger, or attempting
      delivery. With no profile selected it validates the configured default
      profile; with `--profile` it validates that profile. Success prints a
      readable result identifying the validated profile and exits 0; failure
      prints a readable result with a reason (and the selected profile when
      known) and exits non-zero. Reported outcome and exit status always agree.
      Incidental load-path output is routed to standard error so standard output
      remains the machine-readable result surface. Existing `--version`, profile
      selection, and normal-run behavior are unchanged.
    - Implementation observations:
      - Success/failure results reuse the established JSON command-result shape
        (`status`/`summary`/`reason`/`profile`); the spec requires readable,
        parseable reporting and does not prescribe field names.
        - Planner Agent Decision: Accept; reusing the existing result surface is
          consistent with the architecture's command-line result contract and
          keeps the command-line surface uniform.
      - Validation also exercises delivery configuration, so an
        enabled-but-misconfigured delivery provider is reported as a
        configuration failure — a slightly broader notion of "configured
        pipeline" than stages alone.
        - Planner Agent Decision: Accept; delivery is part of the assembled
          pipeline per the architecture, so validating its configuration is in
          scope and desirable. Recorded for the evaluator's awareness.
      - Configuration loadability does not verify provider credentials or network
        reachability, so a valid result does not guarantee runtime provider
        success.
        - Planner Agent Decision: Accept; this is consistent with the stated
          no-live-calls scope. An optional deeper credential/reachability
          preflight would contradict the current no-live-calls requirement and
          is left to Director discretion rather than recorded as required work.

---

## Recommended Future Work Files

---

## Governance

---

## Final Summary
