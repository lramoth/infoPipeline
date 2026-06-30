# Spec: Validate Config Command

## Objective

An operator can ask the command-line application to confirm that the configured
pipeline can be loaded and assembled for a selected (or default) profile,
without starting a pipeline run. The command reports a readable success or
failure result and exits with a status that agrees with the reported outcome.

## Background

The command-line application already loads and assembles its configured pipeline
before any stage runs. Loading validates the profile selection, assembles each
configured stage, confirms required model settings, and confirms that configured
prompt and template files exist; a readable error is reported when the
configuration cannot be loaded or assembled.

Operators and scheduling mechanisms need a way to confirm that a profile's
configuration is loadable before relying on a scheduled run, and to do so safely
— without contacting providers, without writing run records, and without
delivering anything. This mirrors the existing `--version` command, which is a
command-line concern that resolves before the pipeline runs.

Related specs:

- `specs/version_command_feature.md`

## Requirements

- Running the command-line application with `--validate-config` checks whether
  the configured pipeline can be loaded and assembled for the selected profile,
  and reports the result to standard output.
- When no profile is selected, validation uses the configured default profile,
  consistent with normal run behavior.
- When a profile is selected with the existing profile-selection option,
  validation checks that selected profile.
- When the configured pipeline loads and assembles successfully, the command
  reports a readable success result to standard output and exits with status
  code 0. The success result identifies the profile that was validated.
- When the configured pipeline cannot be loaded or assembled, the command
  reports a readable failure result to standard output, including a readable
  reason describing why loading failed, and exits with a non-zero status code.
  The failure result identifies the selected profile when one is known.
- The reported success or failure outcome and the process exit status agree:
  a success result corresponds to a zero exit status, and a failure result
  corresponds to a non-zero exit status.
- The command does not run the pipeline, does not call Researcher, Curator,
  Writer, or Delivery providers, does not write a ledger, and does not attempt
  delivery, regardless of whether validation succeeds or fails.
- Validating configuration loadability does not require live provider
  credentials or network access.

## Inputs

- Command-line invocation of the application with the `--validate-config`
  option.
- Optionally, the existing profile-selection command-line option to choose which
  configured profile is validated. When omitted, the configured default profile
  is used.
- The project's pipeline configuration and the prompt and template files it
  references.

## Outputs

- A readable result printed to standard output describing whether configuration
  validation succeeded or failed.
  - A success result clearly indicates success and identifies the validated
    profile.
  - A failure result clearly indicates failure and includes a readable reason
    describing why the configuration could not be loaded or assembled, and
    identifies the selected profile when known.
- A process exit status that agrees with the reported outcome: zero on success,
  non-zero on failure.
- No ledger file is created or modified by this command.
- No delivery message is produced or sent by this command.

## Behavior

### Normal Flow

1. The caller invokes the command-line application with `--validate-config`,
   optionally selecting a profile.
2. The command resolves the profile to validate: the selected profile when one
   is provided, otherwise the configured default profile.
3. The command loads and assembles the configured pipeline for that profile
   without running any stage.
4. When loading and assembly succeed, the command prints a readable success
   result identifying the validated profile and exits with status code 0.

### Edge Cases

- No profile selected: the configured default profile is validated.
- Selected profile is unknown or its configuration is incomplete or invalid:
  loading fails and the command reports a readable failure result with a reason
  and a non-zero exit status (see Failure Handling).

## Failure Handling

- When the configured pipeline cannot be loaded or assembled — for example an
  unknown profile, missing required configuration, or a configured prompt or
  template file that does not exist — the command prints a readable failure
  result to standard output that clearly indicates failure and includes a
  readable reason, identifies the selected profile when known, and exits with a
  non-zero status code.
- On failure, the command still does not run the pipeline, call any provider,
  write a ledger, or attempt delivery.

## Acceptance Criteria

- [ ] `--validate-config` reports a readable success result and exits with
      status 0 when the configured pipeline loads and assembles for the resolved
      profile.
- [ ] `--validate-config` reports a readable failure result with a reason and a
      non-zero exit status when the configured pipeline cannot be loaded or
      assembled.
- [ ] The reported outcome and the exit status always agree.
- [ ] With no profile selected, the configured default profile is validated;
      with a profile selected, that profile is validated.
- [ ] No provider is called, no ledger is written, no delivery is attempted, and
      the pipeline is not run, on either success or failure.
- [ ] Existing behavior for normal pipeline runs, `--version`, and profile
      selection is unchanged.

## Validation

### Success Conditions

- Invoking the command with `--validate-config` against a loadable configuration
  prints a readable success result identifying the validated profile and exits
  with status 0.
- Invoking the command with `--validate-config` and a selected profile validates
  that profile; invoking it without a selected profile validates the configured
  default profile.
- During validation, no Researcher, Curator, Writer, or Delivery provider is
  contacted, no ledger file is created or modified, and no delivery is
  attempted.

### Failure Conditions

- Invoking the command with `--validate-config` against a configuration that
  cannot be loaded or assembled prints a readable failure result with a reason
  and exits with a non-zero status.
- A failure result paired with a zero exit status, or a success result paired
  with a non-zero exit status, must be rejected.
- Any provider call, ledger write, or delivery attempt during validation must be
  rejected.

## Constraints

- Must not modify runtime behavior outside this specification.
- Must preserve existing observable behavior for normal pipeline runs,
  `--version`, and profile selection.
- Must not perform live external calls.

## Out of Scope

- Changing normal pipeline run output or behavior.
- Changing `--version` behavior.
- Changing the pipeline configuration file format.
- Changing Researcher, Curator, Writer, Delivery, or provider behavior.
- Validating provider credentials, network reachability, or live provider
  responses.

## Completion

For build sessions, append a build log entry to `eval_log.md` following
`AGENTS.md`.

The build log must include:

- spec used
- summary of observable work completed
- assumptions made
- gaps or suspected bugs

Build sessions must not write evaluation entries.
