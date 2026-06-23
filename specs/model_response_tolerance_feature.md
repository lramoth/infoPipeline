# Spec: Structured Model Response Tolerance

## Objective
Pipeline stages that expect structured model output should successfully process valid structured data even when the model response includes common formatting or explanatory text around that data.

## Background
A real Curator run failed even though Diagnostics showed that Gemini returned a valid curated item list. The response was wrapped in Markdown code-fence formatting instead of being returned as bare JSON.
This is not only a Curator concern. Any stage that expects structured model output can encounter the same issue. The Researcher and Curator both expect structured output from Gemini, and future stages may do the same.
This spec defines response-format tolerance for structured model outputs while preserving each stage's existing validation contract.

## Scope
This feature applies to pipeline stages that expect structured model output.
Currently in scope:
- Researcher
- Curator
Future stages are in scope if they define a structured model-output contract.
Currently out of scope:
- Writer final message formatting, because the Writer returns human-readable prose rather than structured data.
- Telegram delivery responses.
- Any stage that does not expect structured model output.

## Requirements
- A structured-output stage shall accept a response that contains valid structured data matching that stage's expected output shape.
- A structured-output stage shall accept valid structured data when it is wrapped in Markdown code-fence formatting.
- A structured-output stage shall accept valid structured data when it is surrounded by non-structured explanatory text.
- A structured-output stage shall preserve the extracted structured data exactly as returned.
- A structured-output stage shall reject responses that do not contain valid structured data.
- A structured-output stage shall reject responses that contain only incomplete, malformed, or unusable structured data.
- A structured-output stage shall continue to report invalid model responses as stage failures with readable reasons.
- A structured-output stage shall continue to rely on its existing validation rules after response-format handling.
- Response-format handling shall not add, remove, rewrite, or invent item content.
- Response-format handling shall not change stage-specific validation requirements.

## Inputs
- Model response content returned to a structured-output pipeline stage.
- The existing stage input, if any.

## Outputs
- On success, the stage returns its expected structured output.
- On failure, the stage reports a readable stage failure.
- Existing Planner failure handling remains responsible for recording failed stages.
- Existing Diagnostics behavior remains responsible for recording diagnostic artifacts when enabled.

## Behavior

### Success Behavior
- If a model returns valid structured data directly, the stage succeeds.
- If a model returns valid structured data inside Markdown formatting, the stage succeeds.
- If a model returns valid structured data with surrounding explanatory text, the stage succeeds.
- The extracted structured data is still subject to the stage's existing validation rules.

### Failure Behavior
- If a model returns no valid structured data, the stage fails.
- If a model returns malformed structured data, the stage fails.
- If a model returns incomplete structured data, the stage fails.
- If extracted structured data fails the stage's existing validation rules, the stage fails.
- If the stage cannot determine a valid structured payload from the response, the stage fails.

## Stage-Specific Expectations

### Researcher
The Researcher expects structured output containing research items.
A successful Researcher response must still satisfy the existing Researcher validation rules, including item count and required item fields.

### Curator
The Curator expects structured output containing curated and ranked research items.
A successful Curator response must still satisfy the existing Curator validation rules, including required item fields, duplicate URL rejection, and ranking requirements.

## Validation Success
- A direct valid structured response is accepted.
- A valid structured response wrapped in Markdown code fences is accepted.
- A valid structured response surrounded by explanatory text is accepted.
- Researcher validation still runs after Researcher response-format handling.
- Curator validation still runs after Curator response-format handling.

## Validation Failure
- A response with no valid structured data is rejected.
- A response with malformed structured data is rejected.
- A response with incomplete structured data is rejected.
- A response that fails the relevant stage's existing validation rules is rejected.
- A response that contains human-readable explanation but no valid structured payload is rejected.

## Constraints
- Must not change Researcher search behavior.
- Must not change Curator ranking or relevance rules.
- Must not change Writer output behavior.
- Must not change Planner stage ordering.
- Must not weaken existing stage validation.
- Must not perform additional web searches.
- Must not retry model requests.
- Must not add, remove, rewrite, or invent item facts.
- Must not require live Gemini, Ollama, Telegram, or other external calls in tests.

## Out of Scope
- Prompt redesign.
- Retry behavior.
- Diagnostics implementation.
- Telegram delivery.
- Writer message normalization.
- Automatic correction of malformed structured data.
- Changes to stage validation rules.
- Changes to pipeline configuration.

## Acceptance Criteria
- Given a direct valid Researcher structured response, the Researcher succeeds.
- Given a valid Researcher structured response wrapped in Markdown formatting, the Researcher succeeds.
- Given a valid Researcher structured response surrounded by explanatory text, the Researcher succeeds.
- Given a direct valid Curator structured response, the Curator succeeds.
- Given a valid Curator structured response wrapped in Markdown formatting, the Curator succeeds.
- Given a valid Curator structured response surrounded by explanatory text, the Curator succeeds.
- Given a structured-output response with no valid structured data, the relevant stage fails.
- Given a structured-output response with malformed structured data, the relevant stage fails.
- Given a structured-output response with incomplete structured data, the relevant stage fails.
- Given extracted structured data that violates existing stage validation rules, the relevant stage fails.
- Existing stage failure reporting remains readable.
- Existing Planner behavior remains unchanged except that wrapped valid structured responses no longer cause stage failure.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in `AGENTS.md`.
