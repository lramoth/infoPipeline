## Open questions

- What requirements should `specs/researcher_feature.md` contain? The requested spec exists but is empty (zero bytes), so the Researcher behavior cannot be implemented without guessing.
- What requirements should `evals/planner_feature.eval.md` contain? The requested spec exists but is empty (zero bytes), so there is no defined behavior to implement.
- Where is the requested spec `eval/planner_feature.eval.md`? That path does not exist, so its requirements cannot be read or implemented.
- What are the exact stage attribute/method names and signatures for the name, executable work, and validation criteria?
- What is the exact validation-result type and shape containing pass/fail plus reason?
- What are the Planner's module/class/function name, constructor arguments, run entry point, and success result?
- How exactly is a validation failure or caught stage exception reported to the caller (returned result or raised exception, including its type/shape)?
- When stage execution raises before producing output, what value must be stored in the ledger's required `output` field?

## Build log

- 2026-06-20: Read `AGENTS.md`, `architecture.md`, and `specs/researcher_feature.md`. The requested Researcher spec is empty (zero bytes). Per `AGENTS.md`, logged the missing requirements under Open questions and stopped without changing implementation or tests. Spec used: `specs/researcher_feature.md` (empty). Assumptions: none. Gap: the spec needs requirement content before implementation can proceed.

- 2026-06-19: Read `AGENTS.md`, `architecture.md`, and the corrected `evals/planner_feature.eval.md`. The requested spec exists but is empty (zero bytes). Per `AGENTS.md`, logged the missing requirements under Open questions and stopped without changing implementation or tests. Spec used: `evals/planner_feature.eval.md` (empty). Assumptions: none. Gap: the spec needs requirement content before implementation can proceed.

- 2026-06-19: Read `AGENTS.md` and `architecture.md`, then attempted to read the requested `eval/planner_feature.eval.md`. The requested spec file does not exist. Per `AGENTS.md`, logged the missing requirement under Open questions and stopped without changing implementation or tests. Spec used: none (requested spec missing). Assumptions: none. Gap: the required spec path must be supplied or corrected.

- 2026-06-19: Read `AGENTS.md`, `architecture.md`, and the latest `specs/planner_feature.md`. The spec defines treatment of errors during stage execution or validation, but still provides only behavioral descriptions rather than the public Python contract required for implementation and tests. No implementation or tests were added because choosing names, signatures, result types, failure reporting, or the missing-output ledger value would be guessing. Spec used: `specs/planner_feature.md`. Assumptions: none. Gaps: public stage/Planner interfaces and execution-error output representation remain unspecified.

## Build log

- 2026-06-19: Implemented the pure-stdlib Planner in `planner.py` from `specs/planner_feature.md`, including ordered run/validation, per-stage ledger persistence, daily reset/reuse behavior, overwrite-on-rerun, clean halting, caller-visible results, and run/validation exception handling. Added six focused `unittest` tests in `test_planner.py`; all pass. Following the updated `AGENTS.md` instruction for unspecified implementation details, selected `Stage(name, run, validate)`, validation results shaped as `(bool, reason)`, `Planner.run()` returning `RunResult`, UTC ISO 8601 timestamps, and `null` output when execution fails before producing a value. Gaps or suspected bugs: none.

## Eval results — Planner Feature

- Scenario 1, Successful run: PASS — all test stages execute, every stage is persisted as `done`, and the returned result reports success.
- Scenario 2, Validation failure: PASS — the failed stage and reason are persisted, subsequent stages do not run, and the returned result identifies the stage and reason.
- Scenario 3, Stage execution error: PASS — the errored stage and exception reason are persisted, subsequent stages do not run, and the returned result identifies the stage and reason.
- Scenario 4, Ledger lifecycle: PASS — a prior-day ledger is replaced for today, while today's same-name stage entry is overwritten with its latest result.
- Overall verdict: PASS.

## Build log

- 2026-06-19: Evaluated and completed the Planner against `evals/planner_feature.eval.md`. The existing pure-stdlib implementation satisfies all four specified scenarios. Updated the successful-run test to explicitly verify that every executed stage is recorded as `done`; ran all six focused tests successfully. Assumptions: none. Gaps or suspected bugs: none.

## Build log — 2026-06-20

- Spec used: `specs/researcher_feature.md`.
- Summary: Implemented `researcher.py` with a no-input Gemini search-grounded API call, the specified seven-day techno-production prompt, JSON item extraction, preservation of Gemini grounding metadata when available, and output validation for item count and required fields. Added focused tests in `test_researcher.py`; all 11 repository tests pass.
- Assumptions: Used the Gemini `generateContent` REST endpoint with the `google_search` tool, defaulted to `gemini-2.5-flash`, represented the JSON-safe result as `{"items": [...], "grounding_metadata": ...}`, and surfaced API or malformed-response failures as `ResearcherError` so the Planner records validation failure and halts.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-20

- Eval file used: `evals/researcher_feature.eval.md`.
- Scenario 1, Successful run: PASS — the Researcher returns at least three complete items, preserves available grounding metadata, and validation accepts the output.
- Scenario 2, Too Few Items: PASS — validation rejects an output containing fewer than three items.
- Scenario 3, Incomplete Items: PASS — validation rejects an output when any item lacks a title, URL, or summary.
- Scenario 4, Gemini Errors: PASS — Gemini API errors are surfaced as `ResearcherError`, providing an error report instead of valid output.
- Overall verdict: PASS.

## Build log — 2026-06-20

- Spec used: `specs/env_config_feature.md`.
- Summary of work completed: Added a standard-library `.env` configuration loader for the declared Gemini and Telegram values, including explicit missing-file and missing-key errors. Updated the Researcher so its Gemini request loads `GEMINI_API_KEY` from the project `.env` file at call time. Added focused tests without making external API calls.
- Assumptions made: Basic dotenv syntax consists of blank lines, comments, and `KEY=VALUE` entries with optional matching single or double quotes. The reusable loader will be called by future Curator and Telegram delivery modules because those external-call boundaries do not exist yet.
- Gaps or suspected bugs: Curator and Telegram delivery are described by the architecture but are not implemented in the current repository, so there are no calls in those components to wire yet.

## Evaluation — 2026-06-20

- Eval file used: `evals/env_config_features.eval.md`.
- Scenario 1, `.env` file missing: PASS — loading a required value from a nonexistent `.env` file raises `EnvConfigError` to the caller.
- Scenario 2, required key missing: PASS — loading a required key absent from an existing `.env` file raises `EnvConfigError` to the caller.
- Scenario 3, required value missing: PASS — required keys with unquoted or quoted empty values raise `EnvConfigError` to the caller.
- Overall verdict: PASS.

## Build log — 2026-06-20

- Spec used: `specs/curator_feature.md`.
- Summary: Implemented `curator.py` with a `Curator` class that sends researcher items to Gemini via a plain `generateContent` call (no `google_search` tool), parses the JSON response into a ranked curated list, and exposes static validation. Validation checks that the output is a non-empty list, every item contains all five required fields (`title`, `url`, `summary`, `curation_reason`, `rank`), no duplicate URLs exist, and at least one item carries `rank=1`. API and parse failures surface as `CuratorError`. Added ten focused `unittest` tests in `test_curator.py`; all 24 repository tests pass.
- Assumptions: `Curator.run(items)` takes the items list explicitly rather than reading the ledger directly; pipeline assembly will bind the researcher output via a closure when a main entry point is written. Defaulted to `gemini-2.5-flash` and the Gemini v1beta REST endpoint, consistent with the Researcher.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-21

- Eval file used: `evals/curator_feature.eval.md`.
- Scenario 1, Valid curated items: PASS — `Curator.validate()` returns `True` when the list is non-empty, all five required fields are present on every item, no URLs are duplicated, and at least one item carries `rank=1`.
- Scenario 2, Empty item list: PASS — `Curator.validate([])` returns `False` with a reason citing no items.
- Scenario 3, Duplicate URLs: PASS — `Curator.validate()` detects when `len(urls) != len(set(urls))` and returns `False` with a reason citing duplicate URLs.
- Scenario 4, Incomplete item data: PASS — `Curator.validate()` iterates all five required fields (`title`, `url`, `summary`, `curation_reason`, `rank`) and returns `False` with a reason citing missing fields when any are absent or empty.
- Scenario 5, Gemini API error: PASS — `Curator.run()` catches `urllib.error.URLError` and `json.JSONDecodeError` and raises `CuratorError`, reporting the failure to the caller.
- Overall verdict: PASS.

## Build log — 2026-06-21

- Spec used: `specs/prompt_loading_feature.md`.
- Summary of work completed: Moved the Researcher and Curator prompts from Python source into `prompts/researchers/techno_news.md` and `prompts/curators/polegroup_techno.md`; added the blank `prompts/writers/telegram_brief.md` placeholder; added shared UTF-8 runtime prompt loading; made both implemented stages configurable with a prompt path; and added focused tests for configured prompt use plus missing and unreadable prompt failures. All 29 repository tests pass.
- Assumptions made: Prompt files are UTF-8 text, are configured through an optional `prompt_path` constructor argument, and are read on each stage run so prompt edits take effect without restarting or modifying Python source.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-21

- Eval file used: `evals/prompt_loading_feature.eval.md`.
- Scenario 1, Missing prompt file: PASS — running either implemented stage with a nonexistent configured markdown prompt reports an error and does not produce a successful result.
- Scenario 2, Alternate prompt file: PASS — each implemented stage uses the contents of its configured markdown file in the outgoing stage prompt under controlled inputs.
- Scenario 3, Default prompt files exist: PASS — all three required Researcher, Curator, and Writer markdown prompt paths exist in the repository.
- Overall verdict: PASS.

## Build log — 2026-06-21

- Spec used: `specs/writer_feature.md`.
- Summary of work completed: Implemented `writer.py` with a `Writer` class that accepts a list of Curator items, loads a configurable prompt from `prompts/writers/telegram_brief.md` by default, sends the prompt and items to a local Ollama endpoint, and returns the generated Telegram message as a string. Raises `WriterError` for empty input, missing or empty prompt file, model execution failures, and empty model responses. Added a `validate` static method that checks the output is a string, each Curator item's title and URL appear in the message with non-empty summary text between them, and items appear in ascending rank order. Added 14 focused `unittest` tests in `test_writer.py`; all 43 repository tests pass.
- Assumptions made: Ollama API uses the `/api/generate` endpoint with `{"model", "prompt", "stream": false}` request body and a `{"response": ...}` response shape. Prompt and curator items are combined as `"{prompt}\n\nCurated items:\n{json.dumps(items, indent=2)}"`. Summary text is validated as any non-whitespace content between a item's title and URL occurrences, excluding the literal "Source:" label specified in the prompt's output format. Rank order is verified by comparing the first-occurrence positions of each item's URL in the output, sorted by ascending rank. Unlike `Researcher.validate` and `Curator.validate`, `Writer.validate` takes both the output string and the curator items list because per-item title, URL, and order correctness cannot be checked without them.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-22

- Eval file used: `evals/writer_feature.eval.md`.
- Scenario 1, Local Model Failures: PASS — when Ollama raises a connection error the Writer raises `WriterError` with "Ollama model execution failed", and when Ollama returns an empty response it raises `WriterError` citing an empty response, both surfacing a readable error.
- Scenario 2, Missing Input: PASS — when the curated item list is empty the Writer raises `WriterError` citing empty input, and when the configured prompt file is missing or empty the Writer raises `WriterError` before calling the model.
- Scenario 3, Output Errors: PASS — when the validate method receives a non-string output it returns failure with a reason stating the output is not a string.
- Scenario 4, Generated String Errors: PASS — validate returns failure when an item's URL is absent from the message, when an item's title does not precede its URL, or when no summary text exists between an item's title and its URL.
- Scenario 5, Ordering Error: PASS — validate returns failure when items' URL positions in the message do not follow the ascending rank order of the curated items.
- Scenario 6, Successful message structure: PASS — with valid curated items and a valid prompt the Writer returns a non-empty string, and validate confirms each item's title and URL are present with summary text and that all items appear in ascending rank order.
- Overall verdict: PASS.

## Build log — 2026-06-22

- Spec used: `specs/pipeline_config_feature.md`.
- Summary of work completed: Added the default `config/pipeline.yaml` with Researcher, Curator, and Writer in the required order; added runtime loading that validates the configuration and configured prompt files, preserves stage order, applies configured model names and endpoints, and assembles stage instances without executing them; added focused tests for every specified success and failure condition.
- Assumptions made: Stage and model field names are case-sensitive. Prompt paths are project-root-relative. Because every currently known stage is prompt-driven, each known stage requires `prompt_path`. An optional model object requires non-empty `provider` and `name` values, while its optional endpoint is passed to the corresponding stage constructor. Added PyYAML because standards-compliant YAML parsing and malformed-document reporting would otherwise require reimplementing substantial established functionality.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-23

- Eval file used: `evals/pipeline_config_feature.eval.md`.

- Scenario 1, Config Exists: PASS — `config/pipeline.yaml` exists in the repository.
- Scenario 2, Valid config: PASS — the default configuration loads as YAML, assembles Researcher, Curator, and Writer in YAML order, and each assembled stage has a name-defined type plus an existing configured prompt path.
- Scenario 3, Missing or malformed config: PASS — loading a missing config or malformed YAML raises `PipelineConfigError` with a readable message.
- Scenario 4, Missing required stage fields: PASS — loading a stage missing `name` or a prompt-driven stage missing `prompt_path` raises `PipelineConfigError` with a readable message.
- Scenario 5, Invalid stage or prompt path: PASS — loading an unknown stage name or a nonexistent configured prompt path raises `PipelineConfigError` with a readable message.
- Overall verdict: PASS.

## Build log — 2026-06-23

- Spec used: `specs/planner_integration_feature.md`.
- Summary of work completed: The Planner now loads the default configured pipeline when no stage list is supplied, executes configured stages in order, passes each successful stage output into the next stage, validates each output before continuing, writes the ledger after every stage result, stops on stage errors or validation failures, reports the failed stage and reason, and returns the final stage output after a fully successful run. The Curator now accepts the Researcher output envelope produced by the integrated pipeline while retaining direct item-list input support. Added focused integration tests; all 56 repository tests pass.
- Assumptions made: Existing explicit `Stage` objects remain supported for tests and direct callers; configured stage names are derived from their class names in lowercase because assembled Researcher, Curator, and Writer instances do not expose a `name` attribute. Writer validation receives both its output and the curated items it was given, matching the existing Writer validation contract.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-23

- Eval file used: `evals/planner_integration_feature.eval.md`.
- Scenario 1, Executing stages in order: PASS — the default config loads Researcher, Curator, and Writer in order, and controlled configured stages run in order, receive the expected inputs, and write output, validation reason, status, and timestamp ledger entries.
- Scenario 2, Stage output valid: PASS — a valid stage output is recorded as done with its output and validation reason, and the following stage runs.
- Scenario 3, Stage output invalid: PASS — an invalid stage is recorded as failed and later stages do not run.
- Scenario 4, Stage error: PASS — a thrown stage error is reported readably, recorded as failed, and halts subsequent stages.
- Scenario 5, Final stage: PASS — when the final stage output is valid, the planner reports that final output to the caller.
- Overall verdict: PASS.

## Build log — 2026-06-23

- Spec used: `specs/CLI_execution_feature.md`.
- Summary of work completed: `python3 planner.py` now starts one run of the default configured pipeline, prints the final pipeline output on success, exits with status code 0 on success, and prints a readable failure message with a nonzero exit code when pipeline startup or execution fails.
- Assumptions made: Non-string final outputs should be printed as pretty JSON when possible and with `str()` as a fallback, while failure messages are printed to standard error.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-23

- Eval file used: `evals/CLI_execution_feature.eval.md`.
- Scenario 1, Successful execution: PASS — under controlled execution, the CLI prints the final pipeline output to standard output and returns status code 0.
- Scenario 2, Unsuccessful execution: PASS — under controlled execution, the CLI prints a readable pipeline failure message to standard error and returns a nonzero status code.
- Overall verdict: PASS.

## Build log — 2026-06-23

- Spec used: `specs/diagnostics_feature.md`.
- Summary of work completed: Failed stages now write best-effort local JSON diagnostics under `output/diagnostics/YYYY-MM-DD/`, and failed ledger entries include the diagnostic file path when one is written. Diagnostics identify the failed stage, timestamp, failure category, error type, readable message, external HTTP context for Gemini and Ollama failures, raw model text previews for model-output parsing failures, and validation reasons with invalid output previews. Successful stages do not write diagnostics, and diagnostic write failures leave the original pipeline failure result intact.
- Assumptions made: Diagnostic previews are capped at 2000 characters. Endpoint URLs are stored after removing common secret-bearing query parameters, request headers are never stored, and obvious API key, token, authorization, and chat ID key/value text in previews is redacted. Diagnostic paths are written beneath the configured ledger directory's `diagnostics` folder, which preserves the default `output/diagnostics/...` layout.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-23

- Eval file used: `evals/diagnostics_feature.eval.md`.
- Scenario 1, Model output cannot be parsed: PASS — a Curator JSON parse failure writes a diagnostic with stage name, timestamp, `failure_category: model_output_parse`, a readable parse error message, and a bounded raw model text preview; the ledger entry is recorded as failed.
- Scenario 2, External service failure: PASS — a Gemini HTTP 503 failure writes a diagnostic with provider name, model name, sanitized endpoint URL (API key is in a header, never stored; query params with secret names are stripped), HTTP method, response status, and a bounded response body preview with API key patterns redacted; no secrets appear in the diagnostic.
- Scenario 3, Local model runtime failure: PASS — an Ollama connection error writes a diagnostic with provider name, model name, local endpoint URL, and a human-readable error message; the ledger entry is recorded as failed.
- Scenario 4, Validation failure: PASS — a failed validation writes a diagnostic with stage name, timestamp, `failure_category: validation_failure`, the validation reason, and a bounded preview of the invalid output; subsequent stages do not run.
- Scenario 5, Successful stage: PASS — a successfully validated stage writes no diagnostic file, the ledger entry carries no `diagnostic_path` key, and the diagnostics directory is not created.
- Scenario 6, Diagnostic preservation fails: PASS — when `write_diagnostic` raises an exception the original pipeline failure result, failed stage name, failure reason, and ledger status are all preserved unchanged.
- Overall verdict: PASS.

## Build log — 2026-06-23

- Spec used: `specs/model_response_tolerance_feature.md`.
- Summary of work completed: Researcher and Curator now accept valid structured item lists returned directly, inside Markdown code fences, or surrounded by explanatory text, while still rejecting model responses that contain no usable structured payload or only malformed structured data. Existing validation remains responsible for item counts, required fields, duplicate URL checks, and ranking checks after extraction.
- Assumptions made: The structured payload expected from Gemini for both currently scoped stages is a top-level JSON list, matching the existing Researcher item parsing and Curator curated-list parsing contracts. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-23

- Eval file used: `evals/model_response_tolerance_feature.eval.md`.
- Scenario 1, Direct Researcher Structured Response: PASS — Researcher.run() with a bare JSON model response succeeds, returns the items unchanged, and Researcher.validate() accepts the output.
- Scenario 2, Markdown-Wrapped Researcher Structured Response: PASS — Researcher.run() with a ```json…``` fenced model response extracts and returns the items unchanged, and Researcher.validate() accepts the output.
- Scenario 3, Explanatory Researcher Structured Response: PASS — Researcher.run() with text surrounding the JSON payload extracts and returns the items unchanged, and Researcher.validate() accepts the output.
- Scenario 4, Direct Curator Structured Response: PASS — Curator.run() with a bare JSON model response succeeds and returns the curated items unchanged.
- Scenario 5, Markdown-Wrapped Curator Structured Response: PASS — Curator.run() with a ```json…``` fenced model response extracts and returns the curated items unchanged, and Curator.validate() accepts the output.
- Scenario 6, Explanatory Curator Structured Response: PASS — Curator.run() with surrounding text extracts and returns the curated items unchanged, and Curator.validate() accepts the output.
- Scenario 7, No Valid Structured Data: PASS — both Researcher.run() and Curator.run() raise a stage error with a readable failure message when the model response contains only human-readable text and no structured payload.
- Scenario 8, Malformed Structured Data: PASS — both Researcher.run() and Curator.run() raise a stage error with a readable failure message when the model response contains truncated or syntactically invalid JSON.
- Scenario 9, Extracted Data Fails Existing Validation: PASS — each stage's validate() returns False with a readable reason when extracted data violates existing rules (item count, required fields, duplicate URLs, missing rank 1), and the Planner records the stage as failed and does not run later stages.
- Scenario 10, Existing Planner Behavior: PASS — when a wrapped but valid structured response passes stage validation, the Planner records the stage as done and continues to the next stage; ordering and failure-handling behavior are unchanged.
- Overall verdict: PASS.

## Build log — 2026-06-23

- Spec used: `specs/url_validation_fix.md`.
- Summary of work completed: Curator validation now accepts curated items whose URLs share a domain, path prefix, Gemini grounding redirect shape, or other visual similarity as long as each complete URL value is distinct. Curator validation still fails when two or more curated items contain the same complete URL value, and the failure reason reports the duplicate URL plus the affected item ranks and titles. Added focused tests for distinct same-domain URLs, distinct same-prefix URLs, distinct Gemini grounding redirect URLs, and exact duplicate URL diagnostics.
- Assumptions made: URL uniqueness is an exact Python value comparison of the `url` field after required-field validation; no URL normalization, canonicalization, redirect resolution, preview truncation, or network lookup is performed. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-23

- Eval file used: `evals/url_validation_fix.eval.md`.
- Scenario 1, Distinct Complete URLs: PASS — `Curator.validate()` returns `True` when every item URL is distinct; no false positive is raised.
- Scenario 2, Same Domain, Different URLs: PASS — items sharing `example.com` but with different full URL values pass validation; the shared domain alone does not cause failure.
- Scenario 3, Same Path Prefix, Different URLs: PASS — items sharing `https://news.example.com/items/source` as a prefix but differing by query string pass validation; the shared prefix alone does not cause failure.
- Scenario 4, Distinct Gemini Grounding Redirect URLs: PASS — items whose URLs share `https://vertexaisearch.cloud.google.com/grounding-api-redirect/` but differ in the long token suffix pass validation; the shared redirect prefix alone does not cause failure.
- Scenario 5, Distinct Long Redirect Tokens: PASS — validation compares the full URL string stored in `item["url"]` without truncation; Gemini redirect URLs with distinct long tokens are treated as distinct.
- Scenario 6, Exact Duplicate URLs: PASS — when two items share the same complete URL value, validation returns `False` with a reason that includes the duplicate URL and the affected item ranks and titles.
- Scenario 7, Existing Required Fields Validation: PASS — items missing any of `title`, `url`, `summary`, `curation_reason`, or `rank` continue to fail validation with a reason citing missing fields.
- Scenario 8, Existing Rank Validation: PASS — items that satisfy all required fields and have no duplicate URLs but lack a `rank=1` entry continue to fail validation with a reason citing the missing rank.
- Overall verdict: PASS.

## Build log — 2026-06-23

- Spec used: `specs/shared_url_fix.md`.
- Summary of work completed: Curator validation now accepts multiple complete curated items that cite the same URL, while still requiring every item to provide a non-empty title, URL, summary, curation reason, and rank, and still requiring at least one rank 1 item. Curator output preserves each item URL exactly as provided and does not drop items because a URL appears more than once.
- Assumptions made: Shared URLs are valid citations even when the URL values are exactly identical; no URL normalization, canonicalization, redirect resolution, network lookup, or item-identity deduplication is performed. No new dependencies were added.
- Gaps or suspected bugs: None.
