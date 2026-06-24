# Eval: Outbound Message Terminology Cleanup

Purpose
Validate the observable behavior described in `specs/outbound_message_terminology_cleanup.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- validation-result shapes
- internal data structures.

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live Gemini, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for runtime checks.

## Scenario 1: Writer Responsibility Uses Outbound Message Terminology
Given the Writer contract and related repository documentation are inspected,
When they describe the Writer's generated content,
Then:
- the generated content is described as an outbound message
- the generated content is not described as a Telegram message
- the generated content is not described as a Telegram-ready message
- the Writer is not described as responsible for Telegram delivery behavior

## Scenario 2: Writer Prompt Is Destination-Agnostic
Given the default Writer prompt is inspected,
When it describes the Writer task,
Then:
- it describes the task as writing an outbound briefing
- it does not describe the task as writing a Telegram briefing
- the generated message format remains suitable for the current daily briefing pipeline

## Scenario 3: Writer Prompt Path Is Destination-Agnostic
Given the repository's default Writer prompt files and configured prompt paths are inspected,
When the Writer's default prompt path is identified,
Then:
- the default Writer prompt uses a destination-agnostic file name
- configured Writer prompt paths point to the destination-agnostic prompt file
- default Writer prompt references do not point to `prompts/writers/telegram_brief.md`

## Scenario 4: Writer Validation Language Uses Outbound Message Terminology
Given Writer validation is exercised with controlled valid and invalid outbound messages,
When validation reports success or failure reasons,
Then:
- missing item title reasons refer to an outbound message
- missing item URL reasons refer to an outbound message
- missing item summary reasons refer to an outbound message
- success reasons refer to an outbound message
- validation reasons do not describe the Writer output as a Telegram message

## Scenario 5: Writer Tests Describe Destination-Agnostic Behavior
Given Writer-related tests are inspected,
When they describe generated Writer output, test prompt content, helper behavior, or assertions,
Then:
- they use destination-agnostic terminology for Writer output
- they do not describe Writer output as a Telegram message
- they do not describe Writer output as a Telegram-ready message
- Telegram terminology appears only in tests that are explicitly about Telegram delivery

## Scenario 6: Telegram References Remain Only For Concrete Delivery Concerns
Given current Writer-related code, prompts, tests, configuration, AGENTS instructions, and architecture documentation are inspected,
When Telegram references are reviewed,
Then:
- Telegram references remain when they describe credentials, bot token, chat ID, actual delivery behavior, or the current concrete delivery destination
- Telegram references do not remain when describing generic Writer output
- historical append-only logs or prior eval artifacts are not treated as failures solely because they preserve old wording

## Scenario 7: Runtime Message Generation Behavior Is Preserved
Given a controlled local-model response contains a non-empty final briefing message,
When the Writer formats curated items with a valid prompt,
Then:
- the Writer returns the final message string
- the message content structure is not changed by the terminology cleanup
- no Telegram API call is required to generate the message
- no new Delivery stage or delivery module is required to generate the message

## Scenario 8: Repository Tests Still Pass
Given the terminology cleanup has been implemented,
When the repository's existing test suite is run without live external service calls,
Then:
- the existing tests pass after the expected terminology and prompt-path updates

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
