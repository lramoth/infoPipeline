# Eval: Latest Run Ledger and OpenAI Researcher Debuggability

Purpose
Validate the observable behavior described in `specs/openai_debugging_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- HTTP client implementation choices
- parsing algorithms
- validation-result shapes
- internal data structures
- ledger storage algorithms

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by a scenario:
- Do not perform live Gemini, OpenAI, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for provider responses and runtime checks.

## Scenario 1: Latest Run Ledger Replaces Earlier Run Records
Given a ledger already contains stage records from an earlier run,
When a later pipeline invocation records its stage results,
Then:
- the ledger represents the later invocation only
- earlier stage records are not retained in the latest ledger
- earlier diagnostic pointers are not retained in the latest ledger
- the latest ledger still records the current date

## Scenario 2: Latest Run Ledger Removes Earlier Delivery Records
Given a ledger already contains delivery records from an earlier run,
When a later pipeline invocation records its results without running delivery,
Then:
- the latest ledger does not contain stale delivery records from the earlier run
- skipped later stages and delivery providers are not represented as if they ran
- the latest failure or success remains inspectable from the latest ledger

## Scenario 3: Partial Failure Remains Inspectable
Given a pipeline invocation fails before all configured stages complete,
When the latest ledger is inspected,
Then:
- completed stages from that invocation are recorded
- the failed stage from that invocation is recorded
- stages that did not run in that invocation are absent
- the failure reason is readable
- a diagnostic path is present for the failed stage when diagnostic preservation succeeds

## Scenario 4: Profile Ledger Isolation Is Preserved
Given two different valid profiles are run with controlled stage or delivery results,
When each profile records its latest run,
Then:
- each profile writes to its own profile-specific ledger or output location
- one profile's latest run does not overwrite another profile's latest run
- each profile ledger records the profile used for that run

## Scenario 5: OpenAI Researcher Requires Web Search
Given Researcher is configured to use OpenAI,
When the OpenAI request is prepared for a controlled run,
Then:
- OpenAI web search is available to the request
- web search is required rather than optional
- the request asks for documented web-search source or search context when available
- the configured OpenAI model remains identifiable in provider context

## Scenario 6: OpenAI Researcher Valid Output Still Passes
Given Researcher is configured to use OpenAI and receives a controlled provider response with enough complete research items,
When the pipeline processes that response,
Then:
- Researcher produces the existing observable Researcher output contract
- available provider metadata or source context is preserved
- existing Researcher validation still passes
- the pipeline may continue to Curator
- no live OpenAI request is required during the check

## Scenario 7: OpenAI Researcher Zero Items Fails At Researcher
Given Researcher is configured to use OpenAI and receives a controlled provider response containing no research items,
When the pipeline processes that response,
Then:
- the run fails at Researcher
- the failure reason clearly says that no research items were produced
- Curator does not run
- Writer does not run
- delivery does not run
- the latest ledger contains no stale Curator, Writer, or delivery records from any earlier run

## Scenario 8: Zero-Item Researcher Diagnostics Preserve Debug Context
Given OpenAI Researcher receives a controlled zero-item provider response with raw model text and search or source context available,
When diagnostic preservation succeeds,
Then:
- local diagnostic information is preserved
- the diagnostic identifies Researcher as the failed stage
- the diagnostic identifies OpenAI when provider context is available
- the diagnostic identifies the configured model when model context is available
- the diagnostic includes a bounded preview of the raw model text when available
- the diagnostic includes bounded non-secret search or source context when available
- the diagnostic makes clear that the provider output contained no usable research items

## Scenario 9: Secrets Are Not Exposed
Given OpenAI Researcher fails during a provider call or because the provider response contains no research items,
When user-visible errors, ledger entries, and diagnostics are inspected,
Then:
- API keys are not exposed
- authentication headers are not exposed
- tokens are not exposed
- chat IDs are not exposed
- `.env` values are not exposed
- endpoint URLs do not contain secrets

## Scenario 10: Existing Researcher Validation Is Not Weakened
Given Researcher output contains too few complete items or items missing required fields,
When Researcher validation is evaluated,
Then:
- the output is still rejected
- the rejection reason is readable
- invalid Researcher output is not allowed to advance to Curator

## Scenario 11: Diagnostic Files Are Not Required To Be Deleted
Given diagnostic files from earlier runs already exist,
When a new pipeline invocation starts and records its latest ledger,
Then:
- existing diagnostic files may remain on disk
- the latest ledger does not point to diagnostics from earlier runs
- diagnostics for the latest failure are recorded when preservation succeeds

## Scenario 12: Automated Tests Avoid Live External Calls
Given the feature has been implemented,
When the repository's automated implementation tests are run,
Then:
- latest-run ledger behavior is covered with controlled inputs
- OpenAI Researcher web-search request behavior is covered without live OpenAI calls
- zero-item Researcher failure behavior is covered with controlled provider responses
- diagnostic safety behavior is covered without exposing secrets
- no live Gemini, OpenAI, Ollama, Telegram, or other external endpoint call is required

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
