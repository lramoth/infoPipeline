# Eval: Diagnostics

Purpose
Validate the observable behavior described in `specs/diagnostics_feature.md`.

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

## Scenario 1: Model output cannot be parsed
Given a pipeline stage receives malformed model output,
When the pipeline run fails because the model output cannot be parsed,
Then:
- Local diagnostic information is preserved
- The diagnostic identifies what stage failed
- The diagnostic includes when the failure happened
- The diagnostic explains that parsing failed
- The diagnostic includes a readable parse error
- The diagnostic includes only a bounded preview of the raw model output
- The run result and ledger still report the stage failure

## Scenario 2: External service failure
Given a pipeline stage receives a failed response from an external service,
When the pipeline run fails because of that service response,
Then:
- Local diagnostic information is preserved
- The diagnostic identifies what stage failed
- The diagnostic includes when the failure happened
- The diagnostic includes the provider name when known
- The diagnostic includes the model name when known
- The diagnostic includes the service endpoint without secrets
- The diagnostic includes the HTTP method
- The diagnostic includes the response status when available
- The diagnostic includes only a bounded preview of the response body when available
- The diagnostic does not expose API keys, tokens, chat IDs, `.env` values, or authentication headers

## Scenario 3: Local model runtime failure
Given the Writer depends on the local model runtime,
When the pipeline run fails because that local runtime is unavailable or returns an error,
Then:
- Local diagnostic information is preserved
- The diagnostic identifies what stage failed
- The diagnostic includes when the failure happened
- The diagnostic includes the local provider name when known
- The diagnostic includes the model name when known
- The diagnostic includes the local endpoint
- The diagnostic includes a human-readable error message
- The run result and ledger still report the stage failure

## Scenario 4: Validation failure
Given a pipeline stage produces output that does not pass validation,
When the pipeline run stops at that failed validation,
Then:
- Local diagnostic information is preserved
- The diagnostic identifies what stage failed
- The diagnostic includes when the failure happened
- The diagnostic explains that validation failed
- The diagnostic includes the validation reason
- The diagnostic includes only a bounded preview of the invalid output
- No later pipeline stages are run

## Scenario 5: Successful stage
Given a pipeline stage completes successfully and passes validation,
When the pipeline continues past that stage,
Then:
- No diagnostic information is created for that successful stage
- The successful stage is recorded as successful
- The successful stage record does not point to diagnostic information

## Scenario 6: Diagnostic preservation fails
Given the application attempts to preserve diagnostic information,
When preserving that diagnostic information fails,
Then:
- The original pipeline failure is still reported normally
- The failed stage is still recorded as failed
- The original failure reason is still visible
- The diagnostic-preservation failure does not replace or obscure the original failure

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.