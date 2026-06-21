# Eval: Prompt Loading

Purpose
Validate the observable behavior described in `specs/prompt_loading_feature.md`.

Do not grade implementation details such as: 
- class names
- method names 
- dataclasses
- validation-result shapes
- internal data structures.

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live external API calls.
- Do not modify external systems.
- Do not send emails, messages, or notifications.
- Use mocks, fixtures, or controlled test inputs.

## Scenario 1: Missing prompt file
Given a stage is configured with a markdown prompt file that does not exist,
When the stage runs,
Then:
- the run fails
- an error is reported

## Scenario 2: Alternate prompt file
Given a stage is configured with a valid markdown prompt file,
When the stage runs,
Then:
- the contents of that markdown file are used as the stage prompt

## Scenario 3: Default prompt files exist
Given the prompt loading feature has been implemented,
When the repository is inspected,
Then:
- `prompts/researchers/techno_news.md` exists
- `prompts/curators/polegroup_techno.md` exists
- `prompts/writers/telegram_brief.md` exists

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
