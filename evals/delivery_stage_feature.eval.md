# Eval: Delivery Stage

Purpose
Validate the observable behavior described in `specs/delivery_stage_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- validation-result shapes
- internal data structures
- HTTP client implementation choices

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live Gemini, Ollama, Telegram, or other external API calls during unit-style checks.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems during unit-style checks.
- Use mocks, fixtures, or controlled test inputs for delivery behavior checks.

If a separate end-to-end evaluation session is performed with real project credentials, live Telegram delivery may be checked only as a delivery confirmation after successful message generation. Unit-style delivery checks must still pass without live Telegram calls.

## Scenario 1: Delivery Configuration Is Separate From Stages
Given the pipeline configuration is inspected,
When delivery is configured,
Then:
- delivery providers are defined in a top-level delivery section
- Telegram can be configured as a delivery provider
- delivery configuration is not represented as a normal content-producing stage
- configured content stages remain in their existing order

## Scenario 2: Enabled Delivery Runs After Successful Writer Output
Given all configured pipeline stages complete successfully,
When the Writer produces a valid outbound message,
Then:
- enabled delivery providers run only after the Writer output is available
- delivery receives the Writer outbound message
- delivery does not run before message generation completes
- the final run output remains the Writer outbound message

## Scenario 3: Delivery Does Not Modify The Outbound Message
Given the Writer produces a controlled outbound message,
When delivery is performed,
Then:
- the exact Writer message is provided for transport
- delivery does not edit, rank, filter, summarize, or reformat the message
- the message available as the successful run output matches the Writer message

## Scenario 4: Stage Failure Prevents Delivery
Given one configured pipeline stage fails validation or raises an error,
When the pipeline run stops at that stage,
Then:
- no delivery provider is invoked
- the failed stage is reported as the cause of the run failure
- delivery is not recorded as a successful or failed normal stage
- command-line stdout remains empty
- command-line stderr reports the stage failure reason

## Scenario 5: Disabled Delivery Providers Do Not Run
Given a delivery provider is configured with `enabled: false`,
When the pipeline stages complete successfully,
Then:
- the disabled provider is not invoked
- the final run output remains the Writer outbound message
- the disabled provider does not create a delivery result for the run

## Scenario 6: Delivery Results Are Recorded Separately
Given delivery runs after successful message generation,
When the ledger is inspected,
Then:
- stage results remain under the stages section
- delivery results are recorded outside the stages section
- delivery is not represented as a normal pipeline stage
- the Writer stage output remains recorded as the Writer outbound message
- a successful delivery record identifies the provider and reports success

## Scenario 7: Delivery Failure Is Observable And Attributed
Given the Writer produces a valid outbound message,
When an enabled delivery provider fails to transport the message,
Then:
- the delivery failure is reported clearly
- the failure identifies the provider that failed
- the Writer stage remains recorded as successful
- the Writer outbound message remains available as the run output
- the failure report does not imply that Writer generation failed

## Scenario 8: Command-Line Output Preserves Message Semantics
Given the command-line entry point is executed,
When the pipeline stages and delivery succeed,
Then:
- stdout contains the final Writer outbound message
- delivery status does not replace the outbound message on stdout
- the command exits successfully

Given the Writer succeeds but delivery fails,
When the command-line entry point reports the result,
Then:
- the generated outbound message remains visible as the final generated output
- the delivery failure is reported separately on stderr
- the failure report identifies delivery rather than stage generation

## Scenario 9: Telegram Uses Configured Destination
Given Telegram delivery is enabled and exercised with controlled HTTP behavior,
When an outbound message is delivered,
Then:
- the message is sent to the configured Telegram destination
- existing project Telegram configuration values are used
- Telegram delivery reports success when Telegram accepts the message
- Telegram delivery reports failure when Telegram transport fails or Telegram rejects the message
- Telegram delivery does not perform Writer formatting or Curator filtering

## Scenario 10: Repository Tests Do Not Require Live Telegram
Given the delivery feature has been implemented,
When the repository's automated tests are run without live external service calls,
Then:
- tests covering delivery behavior pass without sending a real Telegram message
- existing content stage behavior remains unchanged

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
