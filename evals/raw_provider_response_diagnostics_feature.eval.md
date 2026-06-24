# Eval: Raw Provider Response Diagnostics

Purpose
Validate the observable behavior described in `specs/raw_provider_response_diagnostics_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- HTTP client implementation choices
- parsing algorithms
- validation-result shapes
- internal data structures

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for provider responses and runtime checks.

## Scenario 1: Gemini Researcher Missing Model Text
Given Gemini Researcher receives a controlled successful provider response that lacks extractable model text,
When the pipeline processes that response,
Then:
- the run fails at Researcher
- the failure reason is readable
- a local diagnostic record is written when diagnostic preservation succeeds
- the diagnostic identifies Researcher as the failed stage
- the diagnostic includes the provider name when available
- the diagnostic includes the configured model when available
- the diagnostic includes the service endpoint without secrets
- the diagnostic includes a readable parse error
- the diagnostic includes bounded non-secret provider response context when available

## Scenario 2: Curator Missing Model Text
Given a model-backed Curator receives a controlled successful provider response that lacks extractable model text,
When the pipeline processes that response,
Then:
- the run fails at Curator
- the failure reason is readable
- a local diagnostic record is written when diagnostic preservation succeeds
- the diagnostic identifies Curator as the failed stage
- the diagnostic includes provider and model context when available
- the diagnostic includes a readable parse error
- the diagnostic includes bounded non-secret provider response context when available

## Scenario 3: Provider Response Context Is Useful
Given a missing-text provider response contains visible response context such as finish reasons, safety indicators, candidate metadata, grounding metadata, or other provider-returned fields,
When diagnostic preservation succeeds,
Then:
- the diagnostic includes enough bounded provider response context for a human to understand why model text could not be extracted
- the provider response context is not empty when provider response context is available
- the provider response context is bounded rather than a full unbounded response dump

## Scenario 4: Existing Raw Model Text Parse Diagnostics Remain
Given a model provider returns extractable model text that cannot be parsed into the expected structured output,
When the pipeline records the failure,
Then:
- the diagnostic continues to include a bounded raw model text preview
- the diagnostic continues to include a readable parse error
- the run result and ledger still report the stage failure
- adding provider response preview behavior does not remove existing raw-model-text diagnostic behavior

## Scenario 5: Validation Diagnostics Remain
Given a stage produces output that fails existing validation,
When the pipeline records the validation failure,
Then:
- the diagnostic continues to include the validation reason
- the diagnostic continues to include a bounded preview of the invalid output
- later pipeline stages do not run
- adding provider response preview behavior does not change validation failure diagnostics

## Scenario 6: HTTP Failure Diagnostics Remain
Given a model-backed external provider call fails at the HTTP or transport layer,
When the pipeline records the failure,
Then:
- the diagnostic continues to identify the provider when available
- the diagnostic continues to identify the configured model when available
- the diagnostic continues to include the endpoint without secrets
- the diagnostic continues to include the HTTP method
- the diagnostic continues to include response status and bounded response body preview when available

## Scenario 7: Successful Stages Do Not Write Diagnostics
Given a model-backed stage completes successfully and passes validation,
When the pipeline continues past that stage,
Then:
- no diagnostic record is created for that successful stage
- the successful stage is recorded as successful
- the successful stage record does not point to diagnostic information

## Scenario 8: Diagnostic Preservation Failure Does Not Obscure Original Failure
Given the application attempts to preserve diagnostic information for a missing-text provider response,
When diagnostic preservation fails,
Then:
- the original pipeline failure is still reported normally
- the failed stage is still recorded as failed
- the original failure reason is still visible
- the diagnostic-preservation failure does not replace or obscure the original failure

## Scenario 9: Secrets Are Not Exposed
Given a missing-text provider response failure occurs while provider credentials or environment values are configured,
When user-visible errors, ledger entries, and diagnostics are inspected,
Then:
- API keys are not exposed
- authentication headers are not exposed
- tokens are not exposed
- chat IDs are not exposed
- `.env` values are not exposed
- endpoint URLs do not contain secrets
- provider response previews are bounded and sanitized

## Scenario 10: Automated Tests Avoid Live External Calls
Given the feature has been implemented,
When the repository's automated implementation tests are run,
Then:
- missing-text provider response diagnostics are covered with controlled provider responses
- existing raw model text parse diagnostics remain covered
- existing validation and HTTP failure diagnostics remain covered
- diagnostic safety behavior is covered without exposing secrets
- no live Gemini, OpenAI, Ollama, Telegram, or other external endpoint call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
