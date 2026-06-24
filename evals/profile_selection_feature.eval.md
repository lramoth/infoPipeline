# Eval: Profile Selection

Purpose
Validate the observable behavior described in `specs/profile_selection_feature.md`.

Do not grade implementation details such as:
- helper modules
- validation-result shapes
- internal data structures
- command-line parser implementation choices
- ledger storage algorithms
- exact fixture construction mechanics

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live Gemini, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for runtime checks.

## Scenario 1: Explicit Valid Profile Selects Profile Paths
Given a valid controlled pipeline configuration declares a named profile,
When the pipeline is invoked with that profile name,
Then:
- the run uses that profile's Researcher prompt path
- the run uses that profile's Curator prompt path
- the run uses that profile's Writer prompt path
- the run uses that profile's Writer template path
- stage order and model settings remain the configured values

## Scenario 2: Default Profile Is Used When No Profile Is Provided
Given a valid controlled pipeline configuration declares a default profile,
When the pipeline is invoked without a profile name,
Then:
- the run uses the configured default profile
- the default profile's prompt and template paths are used
- the run does not require callers to edit source code or swap configuration files

## Scenario 3: Different Profiles Can Be Selected Without Source Changes
Given a controlled pipeline configuration declares at least two valid profiles,
When each profile is selected in separate invocations,
Then:
- each invocation uses the prompt and template paths for the selected profile
- the same configured pipeline stage order is used for both profiles
- no Python source changes are required between profile selections

## Scenario 4: Unknown Profile Fails Before Stages Run
Given a controlled pipeline configuration declares one or more valid profiles,
When the pipeline is invoked with an unknown profile name,
Then:
- loading fails with a readable error
- no Researcher, Curator, Writer, or delivery stage runs
- no implicit fallback profile is used for the unknown profile name

## Scenario 5: Missing Default Profile Fails Before Stages Run
Given a controlled pipeline configuration does not declare a usable default profile,
When the pipeline is invoked without a profile name,
Then:
- loading fails with a readable error
- no Researcher, Curator, Writer, or delivery stage runs
- no implicit source-level default profile is used

## Scenario 6: Incomplete Profile Path Configuration Fails Before Stages Run
Given a controlled pipeline configuration declares a selected profile that is missing a required prompt or template path,
When that profile is loaded,
Then:
- loading fails with a readable error
- the missing path is identified in a way a caller can correct
- no Researcher, Curator, Writer, or delivery stage runs
- no implicit source-level prompt or template path fallback is used

## Scenario 7: Nonexistent Profile Path Fails Before Stages Run
Given a controlled pipeline configuration declares a selected profile with a prompt or template path that does not exist,
When that profile is loaded,
Then:
- loading fails with a readable error
- the nonexistent configured path is identified in a way a caller can correct
- no Researcher, Curator, Writer, or delivery stage runs
- no implicit source-level prompt or template path fallback is used

## Scenario 8: Profile Runs Use Separate Ledger Locations
Given two different valid profiles are run for the same day with controlled stage and delivery results,
When each run records its results,
Then:
- each profile writes to a profile-specific ledger or output location
- one profile's same-day run does not overwrite the other profile's same-day run
- each recorded run remains available after both profiles have run

## Scenario 9: Ledger Records Selected Profile
Given a valid profile run completes with controlled stage and delivery results,
When the ledger or output record is inspected,
Then:
- the selected profile name is recorded
- the recorded profile matches the profile used for the run
- default-profile runs record the resolved default profile name

## Scenario 10: Existing Pipeline Behavior Remains Unchanged
Given profile selection has chosen valid configured paths,
When existing stage validation, Writer message assembly, and delivery behavior are exercised with controlled inputs,
Then:
- configured validation behavior remains unchanged
- Writer message assembly behavior remains unchanged
- enabled delivery behavior remains unchanged
- profile selection does not require live Gemini, Ollama, or Telegram calls during automated checks

## Scenario 11: Repository Tests Still Pass Without Live External Calls
Given profile selection has been implemented,
When the repository's automated tests are run without live external service calls,
Then:
- explicit profile selection behavior passes
- default profile behavior passes
- missing and invalid profile failures remain covered
- profile-specific ledger behavior passes
- existing configuration, stage, Writer, and delivery behavior continues to pass
- no live Gemini, Ollama, or Telegram call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
