# Eval: Writer Structured Note Tolerance

Purpose  
Validate the observable behavior described in `specs/writer_structured_note_tolerance_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- parsing algorithms
- validation-result shapes
- internal data structures.

Grade only observable behavior.  
Do not infer requirements that are not stated in the specification.

## Evaluation Environment

Unless explicitly required by the spec:
- Do not perform live Gemini, OpenAI, Ollama, Telegram, Bandcamp, or other external API calls.
- Do not perform additional web searches.
- Do not retry model requests.
- Do not modify external systems.
- Do not send messages or notifications.
- Use mocks, fixtures, or controlled test inputs.

## Scenario 1: Direct Structured Notes

Given the Writer receives valid curated items,
And the local model response contains a direct valid structured note list with exactly one non-empty text note per curated item,
When the Writer produces the outbound message,
Then:
- the Writer succeeds
- the outbound message contains every generated note
- the outbound message contains every Curator title exactly
- the outbound message contains every Curator source URL exactly
- the outbound message presents items in ascending rank order

## Scenario 2: Markdown-Wrapped Structured Notes

Given the Writer receives valid curated items,
And the local model response contains a valid structured note list inside Markdown code-fence formatting,
When the Writer produces the outbound message,
Then:
- the Writer succeeds
- the outbound message contains the generated notes
- the surrounding Markdown formatting is not treated as item-note content
- the outbound message still preserves every Curator title, every Curator source URL, and ascending rank order

## Scenario 3: Explanatory Structured Notes

Given the Writer receives valid curated items,
And the local model response contains a valid structured note list surrounded by explanatory text,
When the Writer produces the outbound message,
Then:
- the Writer succeeds
- the outbound message contains the generated notes
- the surrounding explanatory text is not treated as item-note content
- the outbound message still preserves every Curator title, every Curator source URL, and ascending rank order

## Scenario 4: Curator Fields Remain Authoritative

Given the Writer receives valid curated items,
And the local model response contains usable generated notes,
When the final outbound message is produced,
Then:
- every final item uses the exact Curator title for that item
- every final item uses the exact Curator source URL for that item
- every curated item appears in the final message
- items appear in ascending rank order
- generated notes do not replace or alter authoritative Curator titles, URLs, inclusion, or ordering

## Scenario 5: No Valid Structured Note List

Given the Writer receives valid curated items,
And the local model response contains no valid structured note list,
When the Writer processes the response,
Then:
- the Writer fails
- the failure reason is readable
- delivery does not run when evaluated through the full pipeline
- the failure does not produce a partial successful outbound message

## Scenario 6: Wrong Number Of Notes

Given the Writer receives valid curated items,
And the local model response contains a structured note list with fewer or more notes than curated items,
When the Writer processes the response,
Then:
- the Writer fails
- the failure reason is readable
- the failure indicates that the generated notes cannot be used for all curated items

## Scenario 7: Empty Or Non-Text Notes

Given the Writer receives valid curated items,
And the local model response contains a structured note list with an empty note or a non-text note,
When the Writer processes the response,
Then:
- the Writer fails
- the failure reason is readable
- the unusable note is not inserted into a successful outbound message

## Scenario 8: Diagnostics For Unusable Generated Notes

Given the Writer receives valid curated items,
And the local model response cannot be used as generated notes,
When the pipeline records the Writer failure,
Then:
- the ledger reports the Writer stage failure
- a Writer diagnostic record is available when diagnostic writing succeeds
- the diagnostic identifies the failure as a model-output parsing or model-output usability problem
- the diagnostic includes bounded local model output context sufficient for a human to understand what was returned
- the diagnostic includes a readable reason the generated notes could not be used
- the diagnostic does not expose API keys, authentication headers, Telegram tokens, chat IDs, `.env` values, or unbounded provider payloads

## Scenario 9: Successful Writer Runs Do Not Create Diagnostics

Given the Writer receives valid curated items,
And the local model response contains usable generated notes,
When the Writer succeeds and the pipeline records the successful stage,
Then:
- no Writer diagnostic record is created for the successful stage
- the successful Writer stage record does not point to diagnostic information

## Scenario 10: Existing Boundaries Are Preserved

Given the Writer processes generated notes under this feature,
When the Writer succeeds or fails,
Then:
- Researcher behavior is unchanged
- Curator behavior is unchanged
- Delivery behavior is unchanged except that delivery still runs only after all stages succeed
- no new external service is required
- no additional research is performed by the Writer
- failed local model responses are not retried as part of this feature

## Grading instructions

For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
