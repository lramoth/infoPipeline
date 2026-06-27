# Spec: Default Profile-Agnostic Tests

## Objective
Active tests should verify profile selection behavior without treating any particular checked-in default profile name as a permanent product requirement.

## Background
Profile selection allows the same pipeline to run with different configured profiles. Existing behavior includes a default-profile flow when configuration declares a default profile and the caller does not provide one.

The checked-in configuration may change over time. A current default profile may be renamed, replaced, or removed as the project evolves. Active tests should continue to prove profile selection behavior while avoiding brittle coupling to the current topic, profile name, or presence of a default profile in the repository configuration.

Historical specs, evals, and build/evaluation logs may still preserve older profile names or examples.

## Requirements
- Tests for explicit profile selection shall use controlled configuration fixtures or derive expectations from the configuration under test.
- Tests for default-profile resolution shall use controlled configuration fixtures that intentionally declare a default profile.
- Tests for missing-default behavior shall use controlled configuration fixtures that intentionally omit or invalidate the default profile.
- Tests shall not require the checked-in configuration to declare a default profile.
- Tests shall not require the checked-in default profile, when one exists, to have any specific name.
- Tests shall not fail solely because the checked-in default profile is renamed, replaced, or removed.
- Checks against the checked-in configuration shall validate internal consistency only:
  - if a default profile is declared, it refers to a configured profile;
  - if no default profile is declared, the configuration is still acceptable unless the scenario specifically tests no-profile invocation against that configuration.
- Existing behavior for explicit profile selection shall remain covered.
- Existing behavior for default-profile resolution shall remain covered through fixtures.
- Existing behavior for missing-default failure shall remain covered through fixtures.
- Runtime pipeline behavior shall remain unchanged.

## Behavior
- A pipeline configuration with an explicit requested profile loads that profile when the profile exists.
- A controlled configuration that declares a default profile resolves that profile when no profile is requested.
- A controlled configuration with no usable default profile reports a readable failure when no profile is requested.
- The repository's checked-in configuration remains valid when its declared profiles are internally consistent, whether or not a default profile is present.
- If the repository's checked-in configuration declares a default profile, no test assumes that the name is tied to a specific topic or historical profile identifier.

## Validation

### Success Conditions
- Explicit profile selection tests pass using fixture-owned profile names or expectations derived from the configuration under test.
- Default-profile resolution tests pass using a fixture that declares an arbitrary valid default profile.
- Missing-default tests pass using a fixture that intentionally has no usable default profile.
- Checked-in configuration tests pass when the repository configuration has internally consistent profiles and paths, regardless of the default profile name.
- Checked-in configuration tests pass when no default profile is present, except in scenarios that intentionally invoke the pipeline without a profile against that configuration.
- Existing profile-specific ledger behavior remains covered without requiring a specific checked-in profile name.

### Failure Conditions
- A test requires the checked-in default profile to be named `techno`, `techno-releases`, or any other specific value.
- A test fails solely because the checked-in default profile is renamed while the configuration remains internally consistent.
- A test fails solely because the checked-in configuration no longer declares a default profile.
- Explicit profile selection behavior is no longer covered.
- Default-profile resolution behavior is no longer covered by a controlled fixture.
- Missing-default failure behavior is no longer covered by a controlled fixture.

## Out of Scope
- Changing runtime profile-selection behavior.
- Removing the default-profile behavior from the product.
- Renaming, adding, or deleting checked-in profiles.
- Changing prompt files, template files, or profile content.
- Rewriting historical specs, evals, or `eval_log.md`.
- Running external Gemini, OpenAI, Ollama, Telegram, Bandcamp, or OpenClaw calls.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in AGENTS.md.
