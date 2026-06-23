# Spec: Diagnotics

## Objective
When a pipeline run fails, the application should preserve enough local diagnostic information for a human to understand what failed, where it failed, and what external service returned, without needing to immediately rerun the pipeline or edit source code.

## Background
The pipeline depends on external model/runtime services:
- Researcher calls Gemini for search results and grounding data if available.
- Curator calls Gemini for curation.
- Writer calls local Ollama.
Currently each stage's status, output, validation reason, and timestamp are recorded to the ledger by the Planner. Failure responses returned by external services are not stored anywhere currently. 

## Requirements
- On stage failure, write a local diagnostic record.
- The diagnostic record should identify:
  - stage name
  - timestamp
  - failure category
  - error type
  - human-readable error message
- For external HTTP calls, include:
  - provider name when known
  - model name when known
  - endpoint URL without secrets
  - HTTP method
  - response status when available
  - bounded response body preview when available
- For model-output parsing failures, include:
  - bounded raw model text preview
  - parse error message
- For validation failures, include:
  - validation reason
  - bounded preview of the invalid stage output
- The failed stage ledger entry should include the diagnostic file path when one is written.
- Diagnostics must be best-effort. If diagnostic writing fails, the original pipeline failure should still be reported normally.

## Security
- Do not write API keys, Telegram tokens, chat IDs, or `.env` values into diagnostics.
- Do not write authentication headers.
- Do not write full unbounded request or response bodies.
- Diagnostic previews should be capped to a fixed size.

## Outputs
Diagnostic files should be written as JSON under: `output/diagnostics/YYYY-MM-DD/<stage-name>-<timestamp>.json`
Example ledger addition:
```json
{
  "status": "failed",
  "output": null,
  "validation_reason": "CuratorError: Invalid Gemini API curation response...",
  "timestamp": "2026-06-23T...",
  "diagnostic_path": "output/diagnostics/2026-06-23/curator-20260623T....json"
}
```
## Acceptance Criteria
- A Curator JSON parse failure records the raw model text preview.
- A Gemini API failure records provider/model/endpoint/status context without leaking GEMINI_API_KEY.
- An Ollama failure records the local endpoint and error message.
- A validation failure records the validation reason and output preview.
- Successful stages do not write diagnostics.
- Diagnostic write failure does not obscure the original pipeline error.

## Out of Scope
- Fixing malformed model responses.
- Retrying failed stages.
- Changing prompts.
- Changing stage validation rules.
- Sending diagnostics to Telegram or any external system.
- Running live Gemini, Ollama, or Telegram calls in tests.

## Completion
When implementation is complete, append a build log entry to eval_log.md following the format in AGENTS.md
