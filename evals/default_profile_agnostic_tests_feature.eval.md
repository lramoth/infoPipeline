# Eval: Default Profile-Agnostic Tests

Purpose
Validate the observable behavior described in `specs/default_profile_agnostic_tests_feature.md`.

Do not grade implementation details such as:
- helper modules
- validation-result shapes
- internal data structures
- test helper names
- exact fixture construction mechanics

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live Gemini, OpenAI, Ollama, Telegram, Bandcamp, OpenClaw, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for runtime checks.

## Scenario 1: Explicit Profile Selection Is Independent Of Checked-In Defaults
Given active profile selection tests are inspected,
When they verify behavior for an explicitly requested profile,
Then:
- the selected profile name comes from a controlled fixture or from the configuration under test
- the test does not require the checked-in default profile to have any specific name
- the test does not require the checked-in configuration to declare a default profile
- explicit profile selection behavior remains covered

## Scenario 2: Default-Profile Resolution Uses A Controlled Default
Given active default-profile resolution tests are inspected,
When they verify behavior for an invocation with no requested profile,
Then:
- the default profile comes from a controlled configuration fixture that intentionally declares one
- the declared default profile resolves successfully
- the run uses that resolved profile
- the test does not assume the checked-in default profile is named `techno`, `techno-releases`, or any other specific value

## Scenario 3: Missing-Default Failure Uses A Controlled Missing Default
Given active missing-default tests are inspected,
When they verify behavior for an invocation with no requested profile and no usable default profile,
Then:
- the missing or invalid default profile condition comes from a controlled configuration fixture
- loading fails with a readable reason before any stage or delivery provider runs
- the test does not depend on removing or altering the checked-in configuration
- missing-default failure behavior remains covered

## Scenario 4: Checked-In Configuration Checks Internal Consistency Only
Given the repository's checked-in pipeline configuration is inspected through active tests,
When profile declarations are checked,
Then:
- configured profiles are present and internally usable for the checked behavior
- if a default profile is declared, it points to a configured profile
- if no default profile is declared, that absence is not treated as a failure except in a scenario that intentionally invokes the checked-in configuration without a profile
- no test requires the checked-in default profile to have a topic-specific or historical name

## Scenario 5: Checked-In Default Profile May Be Renamed Or Removed
Given active tests have been made default-profile agnostic,
When the checked-in default profile is renamed, replaced, or removed while the checked-in configuration remains valid for the exercised scenario,
Then:
- tests do not fail solely because the old default profile name is absent
- tests do not fail solely because a new default profile name is used
- tests do not fail solely because no default profile is declared
- profile path and profile ledger behavior remain covered through controlled profiles or derived expectations

## Scenario 6: Historical Artifacts Are Not Rewritten
Given historical specs, evals, build logs, evaluation logs, README examples, or older comments are inspected,
When older profile names or topic-specific examples are found,
Then:
- historical wording is not treated as an active-test failure
- append-only logs remain historical records
- current active behavior is evaluated separately from historical artifacts

## Scenario 7: Runtime Behavior Is Unchanged
Given default-profile agnostic tests have been implemented,
When runtime-facing profile behavior is considered,
Then:
- explicit profile selection behavior remains unchanged
- default-profile behavior remains unchanged when configuration declares a default profile
- missing-default failure behavior remains unchanged when no usable default profile is available
- no prompt files, template files, profile content, delivery behavior, or model-provider behavior is changed for this cleanup

## Scenario 8: Repository Tests Still Pass Without Live External Calls
Given default-profile agnostic tests have been implemented,
When the repository's automated tests are run without live external service calls,
Then:
- explicit profile selection behavior passes
- default-profile resolution behavior passes through controlled configuration
- missing-default failure behavior passes through controlled configuration
- checked-in configuration consistency passes without requiring a specific default profile name
- existing configuration, stage, Writer, delivery, and ledger behavior continues to pass
- no live Gemini, OpenAI, Ollama, Telegram, Bandcamp, OpenClaw, or other external call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
