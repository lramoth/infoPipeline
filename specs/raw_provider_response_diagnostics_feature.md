# Spec: Raw Provider Response Diagnostics

## Objective
When a model-backed stage fails because the provider response does not contain extractable model text, diagnostics should preserve a bounded non-secret preview of the provider response so a human can understand what the provider returned.

## Background
A Gemini-backed Researcher run failed with a readable parse error indicating that the expected model-text field was missing. The diagnostic identified the provider, model, endpoint, and parse error, but the raw model text preview was empty because no model text could be extracted. Without a bounded preview of the provider response or failed candidate, it is not possible to tell whether the provider returned a safety block, empty candidate, finish reason, grounding-only response, or another response envelope.

Existing diagnostics already preserve raw model text when model text is available and bounded response bodies for failed HTTP calls. This feature extends diagnostic coverage to successful provider responses whose shape cannot be parsed into model text.

## Requirements
- When a model-output parsing failure occurs and no raw model text is available, the diagnostic record shall include a bounded preview of the provider response or the relevant failed provider response portion when available.
- The preview shall contain enough response context for a human to understand why model text could not be extracted, such as visible finish reasons, safety indicators, candidate metadata, grounding metadata, or other provider-returned fields when present.
- The failed stage ledger entry shall continue to include the diagnostic file path when one is written.
- Diagnostics shall remain best-effort. If preserving the raw provider response preview fails, the original pipeline failure shall still be reported normally.
- Existing diagnostic behavior for HTTP failures, model text parse failures, validation failures, and successful stages shall remain unchanged except for the additional provider-response preview when applicable.

## Security
- Do not write API keys, Telegram tokens, chat IDs, `.env` values, or authentication headers into diagnostics.
- Do not write full unbounded request or response bodies.
- Provider response previews shall be capped to a fixed size.
- Endpoint URLs in diagnostics shall not include secrets.

## Behavior

### Missing Model Text
1. A model provider returns a successful response.
2. The stage cannot extract model text from that response.
3. The run fails at that stage with a readable model-output parsing failure.
4. A diagnostic record is written on a best-effort basis.
5. The diagnostic includes provider/model/endpoint context when available.
6. The diagnostic includes the parse error.
7. If raw model text is unavailable, the diagnostic includes a bounded preview of the provider response or relevant failed response portion when available.

### Existing Raw Model Text
1. A model provider returns extractable model text that cannot be parsed into the expected structured output.
2. The diagnostic continues to include a bounded raw model text preview.
3. The additional provider-response preview is optional in this case.

## Validation

### Success Conditions
- A Gemini Researcher response that lacks extractable model text fails with a readable reason and writes a diagnostic record.
- The diagnostic for a missing-text Gemini Researcher response includes bounded non-secret provider response context when available.
- The diagnostic for a missing-text response includes the provider name and configured model when available.
- The diagnostic for a missing-text response includes the service endpoint without secrets.
- The diagnostic for a missing-text response includes the parse error.
- Existing model-output parsing failures with raw model text still preserve the bounded raw model text preview.
- Existing validation failures still preserve validation reason and invalid-output preview.
- Successful stages do not write diagnostics.
- Diagnostic preservation failure does not obscure the original pipeline failure.
- Automated tests cover the behavior without live Gemini, OpenAI, Ollama, Telegram, or other external calls.

### Failure Conditions
- A missing-text provider response produces a diagnostic with an empty raw model preview and no provider response context.
- The original failure reason is replaced by diagnostic-preservation failure details.
- Diagnostics expose API keys, authentication headers, tokens, chat IDs, `.env` values, or unbounded provider response bodies.

## Out of Scope
- Fixing malformed provider responses.
- Retrying failed stages.
- Changing prompts.
- Changing stage validation rules.
- Changing provider selection behavior.
- Sending diagnostics to Telegram or any external system.
- Running live Gemini, OpenAI, Ollama, or Telegram calls in automated tests.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in `AGENTS.md`.
