# Eval: Validate Config Command

## Purpose

Validate only the observable behavior described in
`specs/validate_config_command_feature.md`.

Do not infer requirements that are not stated in the referenced specification.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- command-line parser implementation choices
- result field names or return-value shapes
- internal data structures or algorithms

Grade only observable behavior, written from the perspective of a command-line
caller, operator, or scheduling mechanism reading the command's standard output
and process exit status.

## Evaluation Environment

Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Bandcamp, Telegram, or other
  external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use the real local project configuration together with controlled or
  temporary configuration inputs as needed for the failing scenario.
- Use mocks, fixtures, or controlled test inputs for pipeline stages, delivery
  providers, credentials, ledger artifacts, and runtime checks.

Validating configuration loadability must not require live provider credentials
or network access.

## Scenario 1: Successful Validation Reports Success And Exits 0

Given:
- The command-line application is available.
- The project's pipeline configuration and the prompt and template files it
  references are present and loadable.

When:
- The application is invoked with `--validate-config` and no profile is
  selected.

Then:
- Standard output contains a readable result that clearly indicates the
  configuration validation succeeded.
- The success result identifies the profile that was validated.
- Standard output remains a single parseable machine-readable result object;
  any incidental human-oriented output appears only on standard error.
- The command exits with status code 0.

## Scenario 2: Successful Validation Has No Run, Provider, Ledger, Or Delivery Side Effects

Given:
- The command-line application is invoked with `--validate-config` against a
  loadable configuration.
- Controlled stages, delivery providers, credentials, and ledger locations are
  present and observable.

When:
- The command finishes.

Then:
- No Researcher, Curator, Writer, or Delivery behavior is started.
- No configured provider endpoint is contacted and no network call is made.
- No pipeline ledger is created, overwritten, or updated.
- No delivery message is produced and no Telegram or other external delivery is
  attempted.
- The command reports the validation result and stops without running the
  pipeline.

## Scenario 3: Unloadable Configuration Reports A Readable Failure And Exits Non-Zero

Given:
- The command-line application is available.
- A configuration that cannot be loaded or assembled is selected — for example
  an unknown selected profile.

When:
- The application is invoked with `--validate-config` selecting that
  configuration.

Then:
- Standard output contains a readable result that clearly indicates the
  configuration validation failed.
- The failure result includes a readable reason describing why the
  configuration could not be loaded or assembled.
- The failure result identifies the selected profile when one is known.
- Standard output remains a single parseable machine-readable result object;
  any incidental human-oriented output appears only on standard error.
- The command exits with a non-zero status code.
- On failure, the command still does not run the pipeline, contact any
  provider, write a ledger, or attempt delivery.

## Scenario 4: Reported Outcome And Exit Status Always Agree

Given:
- The command-line application is invoked with `--validate-config` in both a
  loadable-configuration case and an unloadable-configuration case.

When:
- Each invocation finishes and its standard-output result and process exit
  status are observed together.

Then:
- A result reporting success is always paired with a zero exit status.
- A result reporting failure is always paired with a non-zero exit status.
- A failure result paired with a zero exit status, or a success result paired
  with a non-zero exit status, is rejected.

## Scenario 5: Profile Selection Determines What Is Validated

Given:
- The command-line application is available with the existing
  profile-selection command-line option.
- The configured default profile and at least one other selectable, loadable
  profile are available in the configuration.

When:
- The application is invoked with `--validate-config` and no profile selected,
  and separately invoked with `--validate-config` and a named profile selected.

Then:
- With no profile selected, the result reports the configured default profile
  as the validated profile.
- With a named profile selected, the result reports that named profile as the
  validated profile.
- In each case the reported outcome and exit status agree as in Scenario 4.

## Scenario 6: Existing Command-Line Behavior Is Unchanged

Given:
- The command-line application is invoked without `--validate-config`.
- Controlled pipeline behavior, version reporting, and profile selection are
  available.

When:
- The command completes.

Then:
- Normal pipeline command output remains governed by the existing command-line
  result behavior.
- Version reporting behavior is unchanged.
- Profile selection behavior for normal runs is unchanged.
- No configuration-validation result is printed unless `--validate-config` is
  provided.

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
caller observes on standard output and from the exit status, not internal
identifiers, return values, exception names, file paths, or test mechanics.

Overall verdict is PASS only if every scenario passes.

Evaluation sessions must not write build-log entries.
