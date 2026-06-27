# Spec: Writer Structured Note Tolerance

## Objective

Reduce Writer brittleness when the local model returns valid generated item notes with common formatting around the structured note payload, and improve diagnostics when the Writer cannot use the model response.

## Background

Recent pipeline runs reached the Writer with valid curated items but failed because the local model response could not be used as generated item prose. The failure reason showed that the Writer expected structured note content but received text that was not directly parseable at the beginning of the response.

The Writer uses the Curator output as the authority for final item titles, source URLs, and item order. The local model is responsible only for concise item notes. Because the Writer now depends on a structured note response from the local model, it should tolerate common model formatting around otherwise valid structured notes while preserving the existing authoritative assembly contract.

Related specs:
- `specs/writer_feature.md`
- `specs/writer_authoritative_assembly_feature.md`
- `specs/diagnostics_feature.md`
- `specs/model_response_tolerance_feature.md`

## Requirements

### Functional Requirements

- The Writer shall continue to accept Curator output containing ranked curated items.
- The Writer shall continue to use Curator-provided titles, source URLs, and ranks as authoritative final-message content.
- The Writer shall continue to use the local model only for generated item notes.
- The Writer shall accept a local model response containing a valid structured list of note strings.
- The Writer shall accept a valid structured note list when it is wrapped in Markdown code-fence formatting.
- The Writer shall accept a valid structured note list when it is surrounded by non-note explanatory text.
- The Writer shall preserve each accepted generated note's text as the note content for the corresponding curated item, apart from ignoring surrounding non-note formatting or explanatory text.
- The Writer shall require exactly one usable generated note for each curated item.
- The Writer shall preserve the existing final-message requirements for exact Curator titles, exact Curator URLs, inclusion of all curated items, readable item prose, and ascending rank order.
- The Writer shall reject local model responses that contain no valid structured note list.
- The Writer shall reject local model responses whose structured note list is malformed, incomplete, not a list of strings, contains empty notes, or has a note count that differs from the curated item count.
- The Writer shall continue to report unusable local model prose as a readable Writer failure.
- When the Writer rejects a local model response because generated notes cannot be parsed or used, the diagnostic record shall include enough bounded non-secret model-output context for a human to see what the local model returned.
- Writer diagnostics for local model note parsing failures shall identify the failure as a model-output parsing or model-output usability problem, rather than only as a generic stage error.

### Non-Functional Requirements

- The change shall improve Writer reliability without weakening final-message validation.
- Diagnostic records shall remain bounded and shall not include secrets, authentication headers, Telegram tokens, chat IDs, API keys, or `.env` values.
- The Writer shall not perform additional research, curation, delivery, or external network calls beyond its configured local model call.
- The Writer shall not retry failed model requests as part of this feature.

## Inputs

- Curator output containing ranked curated items with titles, source URLs, summaries, curation reasons, and ranks.
- Writer prompt content.
- Writer template content.
- A local model response containing generated note content for the curated items.

## Outputs

- On success, a single outbound message string containing every curated item in ascending rank order, with exact Curator titles and URLs and generated note prose.
- On failure, a readable Writer failure reason.
- When diagnostics are enabled by the existing Planner behavior, a local diagnostic record for Writer failures.

## Behavior

### Normal Flow

1. The Writer receives curated items.
2. The Writer requests generated item notes from the configured local model.
3. The Writer identifies a valid structured note list in the local model response, even when common model formatting or explanatory text surrounds the list.
4. The Writer pairs the generated notes with the curated items in ascending rank order.
5. The Writer assembles the final outbound message using Curator-provided titles, Curator-provided source URLs, generated notes, and the configured message presentation.
6. The Writer validates the final outbound message before returning it.

### Edge Cases

- If the local model returns a valid structured note list directly, the Writer succeeds.
- If the local model returns a valid structured note list inside Markdown code fences, the Writer succeeds.
- If the local model returns a valid structured note list surrounded by explanatory text, the Writer succeeds.
- If the local model returns text with no valid structured note list, the Writer fails with a readable reason.
- If the local model returns a structured note list with too few or too many notes, the Writer fails with a readable reason.
- If the local model returns a structured note list containing a non-text note or an empty note, the Writer fails with a readable reason.
- If the final assembled message would omit or alter any Curator title, omit or alter any Curator URL, omit any curated item, or change item order, the Writer fails with a readable reason.

## Persistence

- Successful Writer runs shall not create diagnostic records.
- Failed Writer runs shall continue to be recorded in the pipeline ledger according to existing Planner behavior.
- Failed Writer runs that produce diagnostics shall write bounded local diagnostic records according to existing diagnostic retention and location behavior.

## Failure Handling

- A local model execution failure remains a Writer failure with a readable reason and diagnostic context about the local model endpoint when available.
- A local model response that cannot be used as generated notes is a Writer failure with a readable reason.
- A diagnostic record for unusable generated notes shall include bounded local model response context when available.
- Diagnostic writing remains best-effort and shall not obscure the original Writer failure.

## Acceptance Criteria

- [ ] Given curated items and a local model response containing a direct valid structured note list with exactly one note per item, the Writer returns a final outbound message.
- [ ] Given curated items and a local model response containing a valid structured note list inside Markdown code fences, the Writer returns a final outbound message.
- [ ] Given curated items and a local model response containing a valid structured note list surrounded by explanatory text, the Writer returns a final outbound message.
- [ ] Successful final outbound messages still contain every Curator title exactly.
- [ ] Successful final outbound messages still contain every Curator source URL exactly.
- [ ] Successful final outbound messages still present items in ascending rank order.
- [ ] Given a local model response with no valid structured note list, the Writer fails with a readable reason.
- [ ] Given a local model response with the wrong number of notes, the Writer fails with a readable reason.
- [ ] Given a local model response with an empty or non-text note, the Writer fails with a readable reason.
- [ ] Given an unusable local model note response, the Writer diagnostic record includes bounded model-output context sufficient for a human to understand what was returned.
- [ ] Writer diagnostics do not expose API keys, authentication headers, Telegram tokens, chat IDs, or `.env` values.

## Validation

### Success Conditions

- The Writer can complete when valid generated notes are returned directly, wrapped in Markdown formatting, or surrounded by explanatory text.
- The final outbound message continues to satisfy the existing Writer authoritative assembly requirements.
- No successful Writer run creates a diagnostic record.

### Failure Conditions

- A response with no valid structured note list is rejected.
- A malformed structured note list is rejected.
- A structured note list with missing, extra, empty, or non-text notes is rejected.
- A final outbound message that does not preserve Curator titles, URLs, inclusion, or rank order is rejected.
- Writer failure diagnostics omit useful bounded model-output context for unusable note responses.
- Writer diagnostics expose secrets or unbounded provider payloads.

## Constraints

- Must not change Researcher behavior.
- Must not change Curator behavior.
- Must not change Delivery behavior.
- Must not change configured provider ownership of Writer.
- Must not add a new external service.
- Must not require live Gemini, OpenAI, Ollama, Telegram, or other external calls in automated tests.
- Must not add dependencies unless they are materially justified according to project instructions.
- Must not weaken final-message validation.

## Out of Scope

- Retrying local model calls.
- Replacing the Writer local model provider.
- Automatically rewriting malformed generated notes.
- Generating fallback notes from Curator summaries when the local model response is unusable.
- Changing Researcher or Curator structured-output behavior.
- Changing Telegram delivery behavior.
- Evaluating the factual quality or taste of generated notes beyond existing Writer validation.

## Completion

When implementation is complete, append a build log entry to `eval_log.md` following the format in `AGENTS.md`.
