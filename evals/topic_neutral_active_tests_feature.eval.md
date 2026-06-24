# Eval: Topic-Neutral Active Tests

Purpose
Validate the observable behavior described in `specs/topic_neutral_active_tests_feature.md`.

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
- Do not perform live Gemini, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for runtime checks.

## Scenario 1: Pipeline Config Tests Use Topic-Neutral Fixture Prompt Names
Given active pipeline configuration tests are inspected,
When they create controlled prompt files or controlled pipeline configuration,
Then:
- controlled Researcher prompt filenames do not require the current topic name
- controlled Curator prompt filenames do not require the current topic name
- the tests still verify that configured prompt and template paths are loaded correctly
- topic-specific prompt filenames remain acceptable in real configuration values

## Scenario 2: Default Config Checks Do Not Require Topic-Specific Prompt Names
Given the default pipeline configuration is inspected through active tests,
When default configured prompt and template paths are checked,
Then:
- the default configuration's referenced prompt files are verified to exist
- the default configuration's referenced Writer template file is verified to exist
- the check does not fail solely because a valid default Researcher prompt file has a different name
- the check does not fail solely because a valid default Curator prompt file has a different name

## Scenario 3: Writer Test Fixtures Use Topic-Neutral Briefing Labels
Given active Writer tests are inspected,
When they build synthetic outbound messages unrelated to topic selection,
Then:
- synthetic briefing labels are topic-neutral
- Writer validation behavior remains unchanged
- Writer tests do not imply that a specific topic is required for outbound message validation

## Scenario 4: Prompt Files And Pipeline Configuration Are Not Renamed For This Cleanup
Given current prompt files and pipeline configuration are inspected,
When topic-neutral active test cleanup is evaluated,
Then:
- existing prompt filenames may remain topic-specific
- existing prompt content remains unchanged
- `config/pipeline.yaml` may continue pointing to topic-specific prompt filenames
- topic-specific configured prompt filenames are not treated as failures

## Scenario 5: Historical Artifacts Are Not Rewritten
Given historical specs, evals, and build/evaluation logs are inspected,
When older topic-specific wording is found,
Then:
- historical topic-specific wording is not treated as a failure
- append-only build and evaluation logs remain historical records
- current active test behavior is evaluated separately from historical artifacts

## Scenario 6: Repository Tests Still Pass Without Live External Calls
Given topic-neutral active tests have been implemented,
When the repository's automated tests are run without live external service calls,
Then:
- configured prompt-path behavior passes
- Writer template-path behavior passes
- Writer validation behavior passes with topic-neutral synthetic briefing labels
- no live Gemini, Ollama, or Telegram call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
