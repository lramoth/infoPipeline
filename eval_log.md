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

## Evaluation — 2026-06-23

- Eval file used: `evals/shared_url_fix.eval.md`.
- Scenario 1, One Complete Curated Item: PASS — `Curator.validate()` returns `True` for a single-item list with all required non-empty fields and `rank=1`.
- Scenario 2, Multiple Complete Items With Distinct URLs: PASS — `Curator.validate()` returns `True` for a multi-item list where all fields are present and non-empty, rank 1 exists, and every URL is distinct.
- Scenario 3, Multiple Complete Items Sharing One URL: PASS — `Curator.validate()` returns `True` when two items share the same URL but are otherwise complete; no items are removed and each item's URL is preserved exactly as provided.
- Scenario 4, Non-List Curator Output: PASS — `Curator.validate()` returns `False` for any non-list input (dict, string, None, int), citing "Curator output is not a list".
- Scenario 5, Empty Curated List: PASS — `Curator.validate([])` returns `False` citing no items.
- Scenario 6, Missing Required Fields: PASS — `Curator.validate()` returns `False` when any item is missing `title`, `url`, `summary`, `curation_reason`, or `rank`, citing missing fields.
- Scenario 7, Empty Required Fields: PASS — `Curator.validate()` returns `False` when any required field is an empty string, citing missing fields.
- Scenario 8, No Rank 1 Item: PASS — `Curator.validate()` returns `False` when no item has `rank=1`, citing the missing rank.
- Scenario 9, No URL Rewriting Or Canonicalization: PASS — `Curator.validate()` is a static method with no network calls, no URL parsing, and no URL mutation; it checks only field presence, field non-emptiness, and rank, leaving all URL values exactly as provided.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/writer_url_validation_fix.md`.
- Summary of work completed: Writer validation now accepts Telegram messages where multiple curated items cite the same source URL, provided each ranked item section contains that item's title, summary text, and source URL. Validation still rejects messages with missing item titles, missing source URLs, missing summary text, or items shown out of rank order.
- Assumptions made: An item's message section starts at its title and continues until the next ranked item title, or the end of the message for the final item. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-23

- Eval file used: `evals/writer_url_validation_fix.eval.md`.
- Scenario 1, Distinct URLs In Ranked Item Sections: PASS — a message containing two items with distinct source URLs, each appearing with its title, summary text, and URL in ascending rank order, is accepted.
- Scenario 2, Shared URL Repeated In Each Ranked Item Section: PASS — a message where two items share the same source URL and that URL appears in each item's section is accepted; the repeated URL alone does not cause rejection.
- Scenario 3, Shared URL Present In Only One Item Section: PASS — a message where a shared source URL appears in only one item's section is rejected; the item section lacking the URL is treated as having a missing source URL.
- Scenario 4, Missing Item Title: PASS — a message where an item title is absent is rejected.
- Scenario 5, Missing Item URL: PASS — a message where an item's source URL does not appear in that item's section is rejected.
- Scenario 6, Missing Summary Text: PASS — a message where an item section contains a title and source URL but no summary text is rejected.
- Scenario 7, Items Out Of Rank Order: PASS — a message where items appear out of ascending rank order is rejected.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/outbound_message_terminology_cleanup.md`.
- Summary of work completed: The Writer now describes and validates its output as an outbound message, uses a destination-agnostic default prompt path, and keeps producing the same final message string for the current pipeline. The default Writer prompt now asks for an outbound briefing, pipeline configuration points to the renamed Writer prompt, Writer tests describe outbound-message behavior, and documentation no longer describes the Writer as producing a Telegram message.
- Assumptions made: Historical eval entries and append-only build logs were left unchanged, while current Writer contract, prompt, configuration, tests, and Writer-related documentation were updated. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-23

- Eval file used: `evals/outbound_message_terminology_cleanup.eval.md`.
- Scenario 1, Writer Responsibility Uses Outbound Message Terminology: PASS — the Writer contract describes its output as an outbound message in all descriptions, does not reference Telegram as a delivery responsibility, and related documentation describes Telegram only in delivery context.
- Scenario 2, Writer Prompt Is Destination-Agnostic: PASS — the default Writer prompt describes the task as writing a daily outbound briefing, contains no Telegram references, and preserves the existing briefing format suitable for the daily pipeline.
- Scenario 3, Writer Prompt Path Is Destination-Agnostic: PASS — the default Writer prompt file is named `outbound_brief.md`, both the Writer default path and the pipeline configuration point to that destination-agnostic file, and no reference to `prompts/writers/telegram_brief.md` exists in current code or configuration.
- Scenario 4, Writer Validation Language Uses Outbound Message Terminology: PASS — validation failure reasons cite missing title, URL, and summary text in the outbound message, the success reason names the outbound message, and no validation reason mentions a Telegram message.
- Scenario 5, Writer Tests Describe Destination-Agnostic Behavior: PASS — Writer tests use destination-agnostic helper and prompt names, test assertions reference outbound briefing content, and no Telegram message or Telegram-ready message terminology appears in any Writer test.
- Scenario 6, Telegram References Remain Only For Concrete Delivery Concerns: PASS — Telegram references in AGENTS.md and architecture.md describe delivery behavior, credentials, bot token, and chat ID; no current Writer code, prompt, test, or configuration file describes Writer output as a Telegram message; historical append-only log entries that preserve prior wording are not treated as failures.
- Scenario 7, Runtime Message Generation Behavior Is Preserved: PASS — the Writer returns a non-empty final message string under a controlled local-model response, no Telegram API call is made during message generation, and no new Delivery stage or delivery module is required to generate the message.
- Scenario 8, Repository Tests Still Pass: PASS — all 78 repository tests pass without live external service calls after the terminology and prompt-path updates.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/delivery_stage_feature.md`.
- Summary of work completed: The pipeline can now configure Telegram delivery separately from content stages, runs enabled delivery only after a successful final outbound message is produced, leaves the outbound message as the run output and command-line stdout on success, records delivery results separately from stage results, reports delivery failures separately from stage failures, and skips disabled delivery providers. Telegram delivery sends the outbound message to the configured Telegram destination without changing the message.
- Assumptions made: A delivery failure makes the overall run fail while preserving the generated outbound message as the run output; the command-line entry point prints that generated message to stdout and reports the delivery failure to stderr. Injected custom stage lists keep delivery disabled unless providers are explicitly supplied, while the default configured pipeline loads delivery from `config/pipeline.yaml`. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-23

- Eval file used: `evals/delivery_stage_feature.eval.md`.
- Scenario 1, Delivery Configuration Is Separate From Stages: PASS — the pipeline configuration defines delivery providers in a top-level delivery section distinct from the stages list, Telegram appears only as a delivery provider, and the three content stages remain in their existing order.
- Scenario 2, Enabled Delivery Runs After Successful Writer Output: PASS — delivery is invoked only after all configured stages complete successfully, receives the Writer's outbound message as its input, and the run output remains the Writer outbound message.
- Scenario 3, Delivery Does Not Modify The Outbound Message: PASS — the exact Writer message is handed to the delivery provider without alteration, and the run output available to callers matches the Writer message.
- Scenario 4, Stage Failure Prevents Delivery: PASS — when a configured stage fails, no delivery provider is invoked, the failed stage is identified as the cause of the run failure, no delivery entry appears in the ledger, stdout remains empty, and the stage failure reason is reported on stderr.
- Scenario 5, Disabled Delivery Providers Do Not Run: PASS — a provider configured with enabled: false is excluded from the run, no delivery event occurs, the final run output remains the Writer outbound message, and no delivery entry is created in the ledger.
- Scenario 6, Delivery Results Are Recorded Separately: PASS — stage results remain under the stages section, delivery results appear under a separate delivery section, the delivery entry is not represented as a pipeline stage, the Writer stage output remains recorded as the outbound message, and a successful delivery record identifies the provider and reports success.
- Scenario 7, Delivery Failure Is Observable And Attributed: PASS — a delivery transport failure is reported clearly and attributed to the named provider, the Writer stage remains recorded as successful, and the Writer outbound message remains available as the run output without implying that message generation failed.
- Scenario 8, Command-Line Output Preserves Message Semantics: PASS — on full success, stdout contains the Writer outbound message and the command exits with code 0; when the Writer succeeds but delivery fails, the outbound message still appears on stdout, the delivery failure is reported separately on stderr identifying delivery rather than generation, and the command exits with a nonzero code.
- Scenario 9, Telegram Uses Configured Destination: PASS — the Telegram provider sends the outbound message to the destination specified in the project environment configuration, reports success when the Telegram endpoint accepts the message, and reports failure when the transport fails or Telegram rejects the message, without performing any Writer formatting or Curator filtering.
- Scenario 10, Repository Tests Do Not Require Live Telegram: PASS — all delivery behavior is exercised under controlled HTTP behavior without sending a real Telegram message, and all 24 delivery and planner tests pass.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/writer_authoritative_assembly_feature.md`.
- Summary of work completed: The Writer now returns an outbound message that includes every curated item in ascending rank order while preserving each curated title and source URL exactly, even when the local model response omits or changes those fields. Final message wording and markdown presentation now come from the Writer template, and missing, empty, or incomplete templates fail with readable errors. Local model output is used only for per-item prose, and unusable prose is rejected before an outbound message is returned.
- Assumptions made: The Writer template contains a complete-message section with `{items}` and an item section marked by `# Item Template` containing `{title}`, `{note}`, and `{url}`. The optional `# Message Template` heading is treated as template metadata rather than visible outbound-message text. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-23

- Eval file used: `evals/writer_authoritative_assembly_feature.eval.md`.
- Scenario 1, Long Curator URL Is Preserved Exactly: PASS — the outbound message is a non-empty string containing the exact long curator source URL and exact curator title, with readable prose in the item section.
- Scenario 2, Model-Changed URL Is Not Authoritative: PASS — when the local model response shortens or changes the source URL, the outbound message still contains the curator's exact source URL; the model-altered URL does not replace it.
- Scenario 3, Model-Omitted URL Is Not Authoritative: PASS — when the local model response omits the source URL entirely, the outbound message still contains the curator's exact source URL, and the stage succeeds if the generated prose is otherwise usable.
- Scenario 4, Model-Changed Title Is Not Authoritative: PASS — when the local model response changes the title, the outbound message still contains the curator's exact title; the model-altered title does not replace it, and the stage succeeds if the generated prose is otherwise usable.
- Scenario 5, Every Curated Item Is Included In Rank Order: PASS — all curated items appear in the outbound message in ascending rank order regardless of input order, each section contains the exact curator title and source URL, and no item is dropped, merged, split, or reordered by the local model response.
- Scenario 6, Shared Source URLs Are Repeated Per Item Section: PASS — when multiple curator items share the same source URL, each item section in the outbound message contains the shared URL, and the stage does not fail solely because multiple items share a URL.
- Scenario 7, Prompt Changes Do Not Affect Authoritative Fields: PASS — when the configured prompt wording changes while the template remains valid, the outbound message still preserves every curator title and source URL exactly, items still appear in ascending rank order, and the stage succeeds if the generated prose is otherwise usable.
- Scenario 8, Template Controls Final Presentation: PASS — when the configured template changes visible wording, headings, bullet style, source-label wording, or markdown style, the outbound message follows the new template presentation while still preserving every curator title and source URL exactly and presenting items in ascending rank order.
- Scenario 9, Missing Or Invalid Inputs Fail Readably: PASS — an empty curated item list, a missing or empty configured prompt, and a missing or empty configured template each cause the stage to fail with a readable reason before producing an outbound message.
- Scenario 10, Template Missing Required Placeholders Fails Readably: PASS — a template missing the complete item-list placeholder, title placeholder, note placeholder, or URL placeholder causes the stage to fail with a readable reason identifying the missing placeholder(s) before producing an outbound message.
- Scenario 11, Unusable Model Prose Fails Readably: PASS — when the local model cannot produce usable item prose, the stage fails with a readable reason and no outbound message is returned as a successful result.
- Scenario 12, Existing Boundaries Remain Unchanged: PASS — the outbound message is generated using only the local Ollama model call with no Gemini API call, no additional research, no changes to Curator output, and no invocation of delivery behavior.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/config_owned_prompt_paths_feature.md`.
- Summary of work completed: Researcher and Curator now rely on configured prompt paths when the default pipeline is assembled, so changing the pipeline's research and curation prompts is handled through configuration rather than source-level prompt fallbacks. The Researcher stage documentation now uses topic-neutral configured-topic language, and the existing configured prompt-path behavior continues to pass.
- Assumptions made: Direct construction of Researcher or Curator requires an explicit prompt path because prompt selection is now a configuration responsibility. Existing prompt filenames and prompt content were left unchanged because the spec excluded renaming prompts or changing prompt content. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-24

- Eval file used: `evals/config_owned_prompt_paths_feature.eval.md`.
- Scenario 1, Default Pipeline Uses Configured Prompt Paths: PASS — the default pipeline loads the research stage with the prompt path declared in the pipeline configuration, loads the curation stage with the prompt path declared in the pipeline configuration, leaves Writer prompt-path behavior unchanged, and both declared prompt files exist in the repository.
- Scenario 2, Source-Level Researcher Prompt Fallback Is Removed: PASS — the Researcher source defines no module-level default prompt path, requires an explicit prompt path to be supplied on construction with no built-in fallback, and its stage documentation describes the stage as collecting configured-topic research in topic-neutral language.
- Scenario 3, Source-Level Curator Prompt Fallback Is Removed: PASS — the Curator source defines no module-level default prompt path and requires an explicit prompt path to be supplied on construction with no built-in fallback.
- Scenario 4, Configured Prompt Loading Still Works: PASS — each stage loads its supplied prompt from the configured file at runtime, sends that prompt content to the configured model endpoint, and completes its existing behavior without any source-level default prompt path.
- Scenario 5, Missing Prompt Path Remains A Configuration Error: PASS — a prompt-driven stage with no declared prompt path in the pipeline configuration causes loading to fail with a readable configuration error, and no implicit source-level fallback is applied.
- Scenario 6, Missing Configured Prompt File Remains A Configuration Error: PASS — a prompt-driven stage that declares a prompt path pointing to a nonexistent file causes loading to fail with a readable configuration error, and no implicit source-level fallback is applied.
- Scenario 7, Repository Tests Still Pass Without Live External Calls: PASS — all 101 repository tests pass; configured prompt-path behavior and missing prompt-path and missing prompt-file failure conditions are all covered without any live Gemini, Ollama, or Telegram call.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/config_owned_writer_paths_feature.md`.
- Summary of work completed: The default pipeline now supplies both Writer prompt and Writer template paths from configuration, and valid configured paths continue to let Writer generate the same outbound message behavior. Missing Writer prompt paths, missing Writer template paths, nonexistent prompt files, and nonexistent template files are rejected during configuration loading with readable errors. Existing Researcher and Curator configured prompt-path behavior continues to pass.
- Assumptions made: Direct construction of Writer requires explicit prompt and template paths because both path selections are now configuration responsibilities. Existing Writer prompt and template filenames and content were left unchanged because the spec excluded renaming or content changes. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-24

- Eval file used: `evals/config_owned_writer_paths_feature.eval.md`.
- Scenario 1, Default Pipeline Uses Configured Writer Paths: PASS — the default pipeline loads Writer with the prompt path and template path declared in the pipeline configuration, both declared paths point to existing files, and Researcher and Curator configured prompt-path behavior is unchanged.
- Scenario 2, Default Writer Configuration Includes Template Path: PASS — the default Writer stage entry in the pipeline configuration declares both a non-empty prompt path and a non-empty template path.
- Scenario 3, Source-Level Writer Path Fallbacks Are Removed: PASS — the Writer source defines no module-level default prompt path and no module-level default template path; both paths must be supplied explicitly with no source-level fallback.
- Scenario 4, Configured Writer Prompt And Template Loading Still Works: PASS — Writer loads the supplied prompt at runtime, sends its content to the configured local model endpoint, loads the supplied template, and assembles the outbound message from the template and curated items without requiring any source-level path default.
- Scenario 5, Missing Writer Prompt Path Remains A Configuration Error: PASS — a Writer stage missing its prompt path in pipeline configuration causes loading to fail with a readable configuration error, and no implicit source-level fallback is applied.
- Scenario 6, Missing Writer Template Path Is A Configuration Error: PASS — a Writer stage missing its template path in pipeline configuration causes loading to fail with a readable configuration error, and no implicit source-level fallback is applied.
- Scenario 7, Missing Configured Writer Prompt File Remains A Configuration Error: PASS — a Writer stage whose declared prompt path points to a nonexistent file causes loading to fail with a readable configuration error, and no implicit source-level fallback is applied.
- Scenario 8, Missing Configured Writer Template File Is A Configuration Error: PASS — a Writer stage whose declared template path points to a nonexistent file causes loading to fail with a readable configuration error, and no implicit source-level fallback is applied.
- Scenario 9, Existing Stage Boundaries Remain Unchanged: PASS — Writer uses the local model endpoint for item prose generation, preserves curated titles and source URLs in the outbound message, makes no Gemini API call, and does not invoke delivery behavior during outbound message generation.
- Scenario 10, Repository Tests Still Pass Without Live External Calls: PASS — all 103 repository tests pass; Writer prompt loading, template assembly, configured path behavior, missing path and missing file failure conditions, and Researcher and Curator configured prompt-path behavior are all covered without any live Gemini, Ollama, or Telegram call.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/topic_neutral_active_tests_feature.md`.
- Summary of work completed: Active pipeline configuration tests now prove configured prompt and template path behavior using topic-neutral fixture prompt filenames, while the default configuration is checked by confirming its referenced prompt and template files exist rather than requiring specific topic words in filenames. Writer validation tests now use topic-neutral synthetic briefing labels without changing Writer validation behavior.
- Assumptions made: Current prompt filenames, prompt content, and `config/pipeline.yaml` were left unchanged because topic-specific configured prompt paths remain acceptable. Historical specs, evals, and build/evaluation logs were left unchanged. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-24

- Eval file used: `evals/topic_neutral_active_tests_feature.eval.md`.
- Scenario 1, Pipeline Config Tests Use Topic-Neutral Fixture Prompt Names: PASS — controlled pipeline configuration tests create fixture prompt files with names that contain no current topic name, the tests verify that configured prompt and template paths are loaded correctly, and topic-specific names remain acceptable in real configuration values.
- Scenario 2, Default Config Checks Do Not Require Topic-Specific Prompt Names: PASS — the default configuration test confirms that each configured prompt file and the configured Writer template file exist on disk without requiring those files to have any particular topic-specific name, and the check passes with the current topic-specific filenames in place.
- Scenario 3, Writer Test Fixtures Use Topic-Neutral Briefing Labels: PASS — synthetic outbound messages in Writer tests use a generic daily briefing header with no topic-specific wording, Writer validation behavior is unchanged, and no Writer test implies that a specific topic is required for outbound message validation.
- Scenario 4, Prompt Files And Pipeline Configuration Are Not Renamed For This Cleanup: PASS — existing prompt filenames remain topic-specific, prompt content is unchanged, the pipeline configuration continues to reference topic-specific prompt filenames, and those configurations are not treated as failures.
- Scenario 5, Historical Artifacts Are Not Rewritten: PASS — historical build logs, evaluation entries, and prior topic-specific wording remain in the append-only log without modification, and current active test behavior is evaluated separately from those historical records.
- Scenario 6, Repository Tests Still Pass Without Live External Calls: PASS — all 103 repository tests pass; configured prompt-path behavior, Writer template-path behavior, and Writer validation with topic-neutral synthetic briefing labels all succeed without any live Gemini, Ollama, or Telegram call.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/config_path_filename_agnostic_tests_feature.md`.
- Summary of work completed: Active pipeline configuration tests now prove that Researcher, Curator, and Writer prompt paths and Writer template paths are honored from configuration using arbitrary valid fixture filenames, including non-default Writer prompt and template filenames. Default configuration checks continue to confirm that referenced prompt and template files exist without requiring exact filenames, and existing configured path validation failures remain covered.
- Assumptions made: Runtime configuration, prompt files, template files, and prompt/template content were left unchanged because the spec only changed active test expectations. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-24

- Eval file used: `evals/config_path_filename_agnostic_tests_feature.eval.md`.
- Scenario 1, Config Tests Use Arbitrary Valid Filenames For All Stage Paths: PASS — all four controlled fixture filenames differ from their current defaults: the controlled Researcher, Curator, Writer prompt, and Writer template fixture files use names that do not match the default filenames declared in `config/pipeline.yaml`.
- Scenario 2, Configured Paths Are Honored Exactly: PASS — the pipeline configuration test assembles stages with arbitrary non-default fixture filenames and verifies that each assembled stage carries the exact prompt and template paths declared in the controlled configuration, with stage order matching the declaration order.
- Scenario 3, Default Config Checks Are Filename-Agnostic: PASS — the default configuration check confirms that each configured prompt file and the configured Writer template file exist on disk without asserting any specific filename, and passes with the current filenames in place.
- Scenario 4, Missing Path Failures Remain Covered: PASS — omitting a prompt path from a prompt-driven stage, or omitting the Writer template path, fails with a readable configuration error and no source-level fallback applies.
- Scenario 5, Missing File Failures Remain Covered: PASS — a configured prompt path or configured Writer template path pointing to a nonexistent file fails with a readable configuration error and no source-level fallback applies.
- Scenario 6, Runtime Behavior Is Unchanged: PASS — prompt and template files retain their original names and content, `config/pipeline.yaml` continues to declare the same configured paths, and no Gemini, Ollama, or delivery behavior changed.
- Scenario 7, Repository Tests Still Pass Without Live External Calls: PASS — all 103 repository tests pass using mocks and controlled inputs, covering configured prompt-path behavior, Writer template-path behavior, and missing path and missing file failures, without any live Gemini, Ollama, or Telegram call.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/profile_selection_feature.md`.
- Summary of work completed: The command-line pipeline can now run a selected configured profile, or use the configured default profile when none is supplied. Profiles provide the Researcher, Curator, Writer prompt, and Writer template paths used for a run, unknown or incomplete profiles fail before stages run, each configured profile uses a profile-specific ledger location, and ledgers record the selected profile so same-day profile runs do not overwrite each other.
- Assumptions made: Profile-specific ledger locations are derived from the selected profile name under `output/<profile>/ledger.json`. The existing configured topic is represented as the default `techno` profile. No new prompt files, prompt content, model behavior, or delivery behavior were added or changed. No new dependencies were added.
- Gaps or suspected bugs: None.

## Evaluation — 2026-06-24

- Eval file used: `evals/profile_selection_feature.eval.md`.
- Scenario 1, Explicit Valid Profile Selects Profile Paths: PASS — invoking the pipeline with an explicit valid profile name causes every stage to receive the Researcher prompt, Curator prompt, Writer prompt, and Writer template paths declared for that profile; stage order and model settings from the configuration remain unchanged.
- Scenario 2, Default Profile Is Used When No Profile Is Provided: PASS — invoking the pipeline without a profile name uses the profile declared as the default in configuration, supplying that profile's prompt and template paths without requiring callers to edit source code or swap configuration files.
- Scenario 3, Different Profiles Can Be Selected Without Source Changes: PASS — two separate pipeline invocations each requesting a different valid profile name each receive the prompt and template paths specific to that profile, using the same configured stage order, with no Python source changes between invocations.
- Scenario 4, Unknown Profile Fails Before Stages Run: PASS — requesting an unknown profile name fails with a readable error citing the unknown profile before any Researcher, Curator, Writer, or delivery stage runs; no implicit fallback profile is used.
- Scenario 5, Missing Default Profile Fails Before Stages Run: PASS — invoking the pipeline without a profile name when no default profile is declared fails with a readable error before any stage runs; no implicit source-level default is used.
- Scenario 6, Incomplete Profile Path Configuration Fails Before Stages Run: PASS — a profile missing a required prompt or template path fails with a readable error that identifies the missing path, before any stage runs and without applying any source-level path fallback.
- Scenario 7, Nonexistent Profile Path Fails Before Stages Run: PASS — a profile whose declared prompt or template path points to a nonexistent file fails with a readable error that identifies the nonexistent configured path, before any stage runs and without applying any implicit fallback.
- Scenario 8, Profile Runs Use Separate Ledger Locations: PASS — each profile writes its run results to a profile-specific ledger location, so same-day runs for two different profiles are recorded at separate locations and neither overwrites the other.
- Scenario 9, Ledger Records Selected Profile: PASS — after a profile run completes, the ledger contains the selected profile name; a default-profile run records the resolved default profile name rather than a blank or placeholder value.
- Scenario 10, Existing Pipeline Behavior Remains Unchanged: PASS — configured stage validation, Writer message assembly, and enabled delivery behavior all continue to operate correctly after profile selection resolves the configured paths, without requiring live Gemini, Ollama, or Telegram calls during automated checks.
- Scenario 11, Repository Tests Still Pass Without Live External Calls: PASS — all 110 repository tests pass; explicit profile selection, default profile behavior, missing and invalid profile failures, and profile-specific ledger behavior are all covered, as are existing configuration, stage, Writer, and delivery behaviors, without any live external service call.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/configurable_model_providers_feature.md`.
- Summary of work completed: Researcher and Curator can now be configured to use either Gemini or OpenAI while preserving their existing observable output contracts, and Writer now has explicit provider handling that accepts Ollama and rejects unsupported providers with a readable error. Pipeline configuration now rejects unsupported stage/provider combinations before a run. Missing selected-provider credentials and provider call failures are reported readably, and automated tests cover provider switching with controlled responses rather than live external service calls.
- Assumptions made: OpenAI Researcher uses the configured model through the OpenAI Responses API with web search enabled, and OpenAI Curator uses the same Responses API without search tooling. OpenAI response text may appear either as top-level output text or message output content, and Researcher preserves available OpenAI web search call records as provider metadata. No new dependencies were added.
- Gaps or suspected bugs: Real OpenAI, Gemini, Ollama, and Telegram endpoints were not called during implementation; live-provider confirmation remains for a separate evaluation session.

## Evaluation — 2026-06-24

- Eval file used: `evals/configurable_model_providers_feature.eval.md`.
- Scenario 1, Configured Provider Selection: PASS — loading the pipeline configuration with Gemini for Researcher, Gemini for Curator, and Ollama for Writer succeeds; both Gemini model names and the Ollama model name are preserved on the assembled stage instances; no stage executes during configuration loading.
- Scenario 2, OpenAI Researcher And Curator Selection: PASS — a configuration selecting OpenAI for Researcher and Curator assembles Researcher and Curator with the OpenAI provider and configured model name at the OpenAI endpoint, while Writer retains its Ollama configuration; switching between Gemini and OpenAI requires only a configuration provider change and the corresponding environment credential.
- Scenario 3, Unsupported Provider Combinations: PASS — loading a Researcher configured for Ollama, a Curator configured for Ollama, and a Writer configured for OpenAI each fail with a readable error identifying the unsupported provider before any stage runs; unsupported providers submitted directly to a stage also produce readable errors at runtime.
- Scenario 4, Gemini Researcher Behavior Remains Available: PASS — under a controlled Gemini provider response, Researcher succeeds, returns the research items, preserves available Gemini grounding metadata, and the existing Researcher output validation accepts the result.
- Scenario 5, OpenAI Researcher Behavior: PASS — under a controlled OpenAI provider response, Researcher succeeds, returns the research items, preserves available web search call metadata from the OpenAI response, and the existing Researcher output validation accepts the result; switching from Gemini to OpenAI requires only configuration and environment changes.
- Scenario 6, Gemini Curator Behavior Remains Available: PASS — under a controlled Gemini provider response, Curator succeeds, returns the curated items, and the existing Curator output validation accepts the result.
- Scenario 7, OpenAI Curator Behavior: PASS — under a controlled OpenAI provider response, Curator succeeds, returns the curated items, and the existing Curator output validation accepts the result; switching from Gemini to OpenAI requires only configuration and environment changes.
- Scenario 8, Writer Ollama Boundary: PASS — under a controlled Ollama response, Writer assembles the outbound message from the configured template, curated titles, curated source URLs, and model-generated item prose, and the existing Writer validation accepts the result; configuring Writer with any provider other than Ollama produces a readable error identifying the unsupported provider.
- Scenario 9, Missing Selected-Provider Credentials: PASS — when the Gemini credential is absent from the environment configuration the stage fails with a readable error naming the missing key before any provider call is made; when the OpenAI credential is absent the same behavior applies; the Ollama Writer requires no API key and operates without a credential check.
- Scenario 10, Provider Failures And Diagnostics: PASS — a provider call failure reports the selected provider name and configured model name in the error context; API keys, authentication headers, and environment values do not appear in diagnostics, logs, or user-visible error context.
- Scenario 11, Automated Tests Avoid Live External Calls: PASS — all 123 repository tests pass using controlled mocked provider responses; provider switching behavior is covered for both Researcher and Curator; no live Gemini, OpenAI, Ollama, or Telegram call is required.
- Scenario 12, Live Provider Smoke Check: SKIP — live-provider credentials are not available in this evaluation session; live-provider confirmation was not run and is not treated as evidence of live-provider behavior.
- Overall verdict: PASS — all eleven evaluated scenarios pass; Scenario 12 is explicitly skipped due to unavailable live credentials.

## Build log — 2026-06-24

- Spec used: `specs/configured_model_endpoints_feature.md`.
- Summary of work completed: The default pipeline configuration now declares endpoints for Researcher, Curator, and Writer. Configured model entries must include a non-empty string endpoint before stages are assembled, and configured stages use the declared endpoint when attempting provider calls. Existing provider support and stage output contracts remain unchanged, and automated tests cover endpoint behavior without live external service calls.
- Assumptions made: Direct stage construction can still supply endpoints explicitly for controlled tests and non-configured use. The configured Gemini endpoint is the shared Gemini model service base URL for Researcher and Curator, the OpenAI endpoint is the Responses API URL when OpenAI is selected, and the Writer endpoint remains the local Ollama generation URL. No new dependencies were added.
- Gaps or suspected bugs: Real Gemini, OpenAI, Ollama, and Telegram endpoints were not called during implementation; live endpoint confirmation remains for a separate evaluation session.

## Build log — 2026-06-24

- Spec used: `specs/configured_model_endpoints_feature.md`.
- Summary of work completed: Removed remaining source-level Researcher and Curator endpoint defaults so those stages no longer embed Gemini or OpenAI service endpoints in code. Configured pipeline assembly now requires every configured model-backed stage to provide a model object with provider, name, and endpoint, and controlled tests pass endpoints explicitly when constructing stages directly.
- Assumptions made: Direct stage construction remains allowed when callers provide an endpoint explicitly. Model names remain as existing constructor defaults for direct construction because this review focused on endpoint ownership. No new dependencies were added.
- Gaps or suspected bugs: Real provider endpoints were not called during this review fix.

## Evaluation — 2026-06-24

- Eval file used: `evals/configured_model_endpoints_feature.eval.md`.
- Scenario 1, Default Pipeline Declares Model Endpoints: PASS — the default pipeline configuration declares non-empty text endpoints for Researcher, Curator, and Writer, and loading succeeds without any source-level endpoint defaults being required.
- Scenario 2, Gemini Endpoints Are Configuration-Owned: PASS — when Researcher and Curator are configured for Gemini, each stage attempts to contact the Gemini endpoint declared in configuration, both preserve their existing output contracts, and changing the endpoint requires only a configuration update.
- Scenario 3, OpenAI Endpoints Are Configuration-Owned: PASS — when Researcher and Curator are configured for OpenAI, each stage attempts to contact the OpenAI endpoint declared in configuration, both preserve their existing output contracts, and changing the endpoint requires only a configuration update.
- Scenario 4, Writer Endpoint Remains Configuration-Owned: PASS — when Writer is configured for Ollama, it attempts to contact the Ollama endpoint declared in configuration, preserves its existing outbound-message contract, and changing the endpoint requires only a configuration update.
- Scenario 5, Missing Endpoint Fails Configuration Loading: PASS — a model object without an endpoint causes configuration loading to fail with a readable error before any provider call is attempted, for Researcher, Curator, and Writer.
- Scenario 6, Invalid Endpoint Fails Configuration Loading: PASS — a model object with an empty endpoint and a model object with a non-text endpoint each cause configuration loading to fail with a readable error before any provider call is attempted.
- Scenario 7, Source-Level Endpoint Fallbacks Are Removed: PASS — Researcher and Curator each require an endpoint to be supplied on construction with no built-in fallback, and neither stage embeds a Gemini or OpenAI service endpoint in source code.
- Scenario 8, Provider Failure Diagnostics Use Configured Endpoint Safely: PASS — a failed provider call produces diagnostic context identifying the endpoint used for the attempted call, the selected provider, and the configured model, without exposing API keys, authentication headers, or environment values.
- Scenario 9, Existing Provider Support Remains Unchanged: PASS — Researcher and Curator continue to support Gemini and OpenAI, Writer continues to support only Ollama, unsupported provider combinations continue to fail with readable errors, and all existing stage output contracts remain unchanged.
- Scenario 10, Automated Tests Avoid Live External Calls: PASS — configured endpoint behavior, missing endpoint failures, and invalid endpoint failures are all covered with controlled inputs and mocked provider responses; all 125 repository tests pass without requiring any live Gemini, OpenAI, Ollama, or Telegram call.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/openai_debugging_feature.md`.
- Summary of work completed: Each pipeline invocation now leaves a ledger containing only the latest run's stage and delivery records. OpenAI-backed research now requires provider web search and requests available source context. If Researcher receives a model response with no research items, the run fails at Researcher, later stages do not run, and a local diagnostic preserves bounded non-secret context about the empty provider output.
- Assumptions made: The existing diagnostic directory is preserved between runs because the spec only requires clearing stale ledger records and diagnostic pointers. Zero-item handling was applied to Researcher model output generally, including Gemini, while the OpenAI-specific request behavior was limited to OpenAI. No new dependencies were added.
- Gaps or suspected bugs: Real OpenAI, Gemini, Ollama, and Telegram endpoints were not called during implementation; live-provider confirmation remains for a separate evaluation session.

## Evaluation — 2026-06-24

- Eval file used: `evals/openai_debugging_feature.eval.md`.
- Scenario 1, Latest Run Ledger Replaces Earlier Run Records: PASS — a second pipeline invocation on the same day produces a ledger containing only that invocation's stage records; stage records from a prior same-day run are absent, and the latest date is recorded.
- Scenario 2, Latest Run Ledger Removes Earlier Delivery Records: PASS — when a later invocation fails before delivery, the resulting ledger contains no delivery section from any earlier run, and skipped stages and delivery providers are absent.
- Scenario 3, Partial Failure Remains Inspectable: PASS — stages that completed before the failure are recorded with their results, the failed stage is recorded with its failure reason and a diagnostic path, and stages that did not run are absent from the ledger.
- Scenario 4, Profile Ledger Isolation Is Preserved: PASS — each profile writes its run results to a separate profile-specific location, the two locations do not share a ledger file, and each ledger records the profile name used for that run.
- Scenario 5, OpenAI Researcher Requires Web Search: PASS — the OpenAI request requires web search rather than making it optional, requests documented source context, and the configured model is identifiable in the provider request.
- Scenario 6, OpenAI Researcher Valid Output Still Passes: PASS — a controlled OpenAI provider response with enough complete items produces the existing Researcher output contract, available provider metadata is preserved, existing validation accepts the output, and the pipeline may continue to Curator.
- Scenario 7, OpenAI Researcher Zero Items Fails At Researcher: PASS — a controlled zero-item OpenAI provider response causes the run to fail at Researcher with a readable reason, Curator and later stages do not run, and the ledger contains no stale records from any earlier run.
- Scenario 8, Zero-Item Researcher Diagnostics Preserve Debug Context: PASS — the diagnostic identifies Researcher as the failed stage, identifies OpenAI and the configured model, includes a bounded preview of the raw provider text, includes bounded search context, and makes clear that no usable research items were produced.
- Scenario 9, Secrets Are Not Exposed: PASS — API keys, authentication headers, and environment values are absent from user-visible errors, ledger entries, and diagnostic files when OpenAI Researcher fails due to a provider call error or a zero-item provider response.
- Scenario 10, Existing Researcher Validation Is Not Weakened: PASS — Researcher output with too few items or items missing required fields is still rejected with a readable reason and does not advance to Curator.
- Scenario 11, Diagnostic Files Are Not Required To Be Deleted: PASS — existing diagnostic files remain on disk after a new invocation, the latest ledger does not contain diagnostic pointers from earlier runs, and diagnostics for the latest failure are recorded when preservation succeeds.
- Scenario 12, Automated Tests Avoid Live External Calls: PASS — latest-run ledger behavior, OpenAI web-search request behavior, zero-item Researcher failure, and diagnostic safety are all covered with controlled inputs and mocked provider responses; all 127 repository tests pass without any live external service call.
- Overall verdict: PASS.

## Build log — 2026-06-24

- Spec used: `specs/raw_provider_response_diagnostics_feature.md`.
- Summary of work completed: Model-backed stage failures now preserve bounded non-secret provider response context when no model text can be extracted, so missing-text provider responses can be diagnosed from local diagnostic records. Existing raw model text parse diagnostics, validation diagnostics, HTTP failure diagnostics, and successful-stage behavior remain unchanged.
- Assumptions made: The additional provider response preview is recorded only when model text is unavailable, because existing raw-text diagnostics already satisfy parse-failure debugging when text exists. The preview is bounded and sanitized by the existing diagnostic preview path. No new dependencies were added.
- Gaps or suspected bugs: Real Gemini, OpenAI, Ollama, and Telegram endpoints were not called during implementation; live-provider confirmation remains for a separate evaluation session.

## Evaluation — 2026-06-24

- Eval file used: `evals/raw_provider_response_diagnostics_feature.eval.md`.
- Scenario 1, Gemini Researcher Missing Model Text: PASS — a Gemini Researcher response with no extractable model text causes the pipeline to fail at Researcher with a readable reason, and the diagnostic identifies the stage, provider, model, sanitized endpoint, parse error, and includes a bounded non-secret preview of the provider response containing the safety reason and grounding metadata.
- Scenario 2, Curator Missing Model Text: PASS — a model-backed Curator response with no extractable model text causes the pipeline to fail at Curator with a readable reason, and the diagnostic identifies the stage, provider, model context, parse error, and includes a bounded non-secret provider response preview showing the safety block reason.
- Scenario 3, Provider Response Context Is Useful: PASS — the provider response preview includes visible fields such as finish reason, safety ratings, and grounding metadata for Gemini, and web search calls and trace metadata for OpenAI, giving a human enough context to understand why model text could not be extracted; the preview is bounded to a fixed size rather than a full unbounded response dump.
- Scenario 4, Existing Raw Model Text Parse Diagnostics Remain: PASS — when extractable model text cannot be parsed, the diagnostic continues to include a bounded raw model text preview and a readable parse error, the stage is recorded as failed, and the new provider response preview behavior does not remove or alter this existing diagnostic path.
- Scenario 5, Validation Diagnostics Remain: PASS — a validation failure continues to write a diagnostic with the validation reason and a bounded preview of the invalid output, later stages do not run, and the new provider response preview behavior does not change validation failure diagnostics.
- Scenario 6, HTTP Failure Diagnostics Remain: PASS — an HTTP transport failure continues to produce a diagnostic identifying the provider, model, sanitized endpoint, HTTP method, response status, and bounded response body preview; API keys and authentication headers are absent from the diagnostic.
- Scenario 7, Successful Stages Do Not Write Diagnostics: PASS — a stage that completes successfully and passes validation writes no diagnostic file, the ledger entry for that stage does not include a diagnostic path, and the diagnostics directory is not created.
- Scenario 8, Diagnostic Preservation Failure Does Not Obscure Original Failure: PASS — when diagnostic preservation fails, the original pipeline failure is still reported with the correct failed stage and failure reason, the ledger records the stage as failed, and no diagnostic path appears in the ledger entry.
- Scenario 9, Secrets Are Not Exposed: PASS — API keys, authentication headers, tokens, chat IDs, and environment values are absent from user-visible errors, ledger entries, and diagnostic files when a missing-text provider response failure occurs; endpoint URLs in diagnostics do not contain secrets, and provider response previews are bounded and sanitized.
- Scenario 10, Automated Tests Avoid Live External Calls: PASS — missing-text provider response diagnostics for both Gemini and OpenAI are covered with controlled provider responses, existing raw model text parse, validation, and HTTP failure diagnostics remain covered, diagnostic safety behavior is confirmed without real credentials, and all 130 repository tests pass without requiring any live external service call.
- Overall verdict: PASS.

## Build log — 2026-06-25

- Spec used: `specs/gemini_raw_search_normalization_feature.md`.
- Summary of work completed: Gemini-backed Researcher runs now produce normalized research items with title, URL, and summary from grounded provider search data, record bounded non-secret raw provider response context in the Researcher output for ledger inspection, fail readably when provider shape, source context, item creation, or item count prevents usable normalized output, and keep Curator, Writer, Delivery, and non-Gemini Researcher behavior on their existing contracts.
- Assumptions made: The normalized Researcher item list remains the authoritative downstream contract; bounded raw provider response context is diagnostic context in the Researcher output. Gemini item text may arrive as JSON title/summary objects or simple line-based item records, while item URLs are taken from provider grounding metadata. No new dependencies were added.
- Gaps or suspected bugs: Real Gemini, OpenAI, Ollama, and Telegram endpoints and live website URL checks were not called during implementation; live-provider confirmation remains for a separate evaluation session.

## Evaluation — 2026-06-25

- Eval file used: `evals/gemini_raw_search_normalization_feature.eval.md`.
- Scenario 1, Gemini Success Produces Normalized Items: PASS — a controlled Gemini grounded search response produces at least three normalized items each containing a non-empty title, URL, and summary; Researcher validation accepts the output and the pipeline may continue to Curator.
- Scenario 2, Gemini URLs Come From Grounded Source Data: PASS — normalized item URLs are taken from provider-grounded chunk metadata rather than model-generated text, and the Researcher output explicitly records that URLs were derived from provider grounding metadata.
- Scenario 3, Raw Gemini Search Context Is Inspectable: PASS — the Researcher output recorded in the ledger includes both the normalized item list as authoritative output and a bounded non-secret raw provider search context entry preserving available search queries, grounding chunks with titles and URIs, grounding supports with text previews, and chunk indices.
- Scenario 4, Curator Receives Normalized Items: PASS — Curator accepts the Researcher output envelope and extracts the normalized item list from it automatically, requiring no knowledge of raw Gemini provider response fields; Curator curation behavior is unchanged.
- Scenario 5, Malformed Gemini Provider Response Fails At Researcher: PASS — a Gemini response with an unexpected shape causes the run to fail at Researcher with a readable reason; Curator, Writer, and Delivery do not run; a best-effort diagnostic is written; available provider response context is bounded and non-secret.
- Scenario 6, Missing Gemini Source Context Fails At Researcher: PASS — a Gemini response containing model text but no usable grounding source URLs causes the run to fail at Researcher with a reason that clearly identifies missing usable source context; no normalized items advance to Curator; a best-effort diagnostic is written with bounded provider context.
- Scenario 7, Item Normalization Failure Fails At Researcher: PASS — when Gemini returns source context but normalized items cannot be produced, the run fails at Researcher with a readable reason that identifies whether the failure was caused by missing titles or summaries, missing source URLs, or insufficient usable items; Curator and later stages do not run.
- Scenario 8, Insufficient Normalized Item Count Fails At Researcher: PASS — Researcher output is rejected when fewer than three normalized items with title, URL, and summary are present; the rejection reason is readable; Curator and later stages do not run; the ledger records the Researcher stage as failed.
- Scenario 9, Required Item Fields Are Still Enforced: PASS — Researcher output containing items missing a title, URL, or summary is rejected with a readable reason; invalid output is not allowed to advance to Curator.
- Scenario 10, Non-Gemini Researcher Behavior Is Unchanged: PASS — when Researcher is configured with OpenAI, the new Gemini raw-search normalization behavior does not affect response parsing, diagnostics, validation, or ledger entries; existing OpenAI Researcher behavior remains intact and no raw provider response field is required.
- Scenario 11, Existing Curator, Writer, And Delivery Behavior Remain: PASS — Curator still ranks and filters from normalized items, Writer still assembles the outbound message from curated items and the configured template, and Delivery still runs only after all configured stages succeed; the raw Gemini provider context does not alter any downstream output contract.
- Scenario 12, Secrets And Payload Bounds: PASS — API keys are passed only in request headers and are never stored in diagnostics or ledger entries; endpoint URLs contain no secret query parameters; raw provider response previews are capped to a fixed size rather than unbounded dumps; pattern-based redaction removes API key, token, chat ID, and authorization key–value pairs from preview text.
- Scenario 13, Diagnostic Preservation Failure Does Not Obscure Original Failure: PASS — when diagnostic preservation fails, the original Researcher failure is still reported with its stage name and failure reason, the ledger records the stage as failed, and the diagnostic-preservation failure does not replace or obscure the original failure.
- Scenario 14, Automated Tests Avoid Live External Calls: PASS — Gemini success with grounded source context, missing source context, malformed response, item normalization failure, insufficient item count, required field validation, non-Gemini provider behavior, and downstream contract preservation are all covered with controlled provider responses; all 132 repository tests pass without any live Gemini, OpenAI, Ollama, Telegram, or other external endpoint call.
- Overall verdict: PASS.

## Build log — 2026-06-25

- Spec used: `specs/researcher_provider_boundary_and_ledger_compaction_feature.md`.
- Summary of work completed: Successful Gemini-backed Researcher output now records normalized items and a single bounded provider context area instead of duplicating equivalent grounding/source context in multiple top-level fields. Gemini and OpenAI Researcher behavior remain provider-bounded while the shared Researcher stage continues to expose the same provider selection and normalized item validation behavior to Planner and downstream stages.
- Assumptions made: OpenAI output keeps its existing `grounding_metadata` provider metadata field because the spec only requires removing duplicate Gemini grounding/source context when the same information is already present in raw provider context. Gemini provider context remains under `raw_provider_response` with provider, model, bounded response preview, and compact search context. No new dependencies were added.
- Gaps or suspected bugs: Real Gemini, OpenAI, Ollama, Telegram, and live website URL checks were not called during implementation; live-provider confirmation remains for a separate evaluation session.

## Evaluation — 2026-06-25

- Eval file used: `evals/researcher_provider_boundary_and_ledger_compaction_feature.eval.md`.
- Scenario 1, Gemini Success Uses Compact Ledger Output: PASS — a controlled Gemini grounded search response produces normalized items recorded in the Researcher output alongside one bounded provider context area; no duplicate grounding field appears at a second top-level location.
- Scenario 2, Gemini Context Remains Useful After Compaction: PASS — the bounded provider context area retains search queries, grounding chunks with source titles and URIs, grounding supports with text previews and chunk indices, and a search entry point preview, giving a human sufficient context to understand how grounded URLs were derived.
- Scenario 3, Gemini Normalized URLs Remain Grounded: PASS — normalized item URLs are taken from provider-grounded chunk metadata; items carry title, URL, and summary; shared Researcher validation accepts at least three complete items and the pipeline may continue to Curator.
- Scenario 4, Gemini Does Not Expose Duplicate Top-Level Grounding Metadata: PASS — Gemini Researcher output contains no separate top-level grounding or source metadata field; URL provenance remains readable through the normalization record without comparing duplicate sections; downstream stages receive normalized items.
- Scenario 5, OpenAI Behavior Remains Unchanged: PASS — OpenAI request behavior, response parsing, provider metadata field, empty-response diagnostics, and ledger behavior remain on the existing OpenAI contract; Gemini-specific compaction does not alter any of these.
- Scenario 6, Provider-Specific Behavior Is Isolated: PASS — Gemini grounded-search normalization does not affect OpenAI behavior; OpenAI web-search handling does not affect Gemini behavior; provider failures remain provider-aware; an unsupported provider produces a readable unsupported-provider error.
- Scenario 7, Shared Researcher Validation Remains Provider-Neutral: PASS — shared validation rejects outputs with fewer than three items or items missing any of title, URL, or summary with a readable reason; invalid output is not allowed to advance to Curator.
- Scenario 8, Downstream Contract Remains Stable: PASS — Curator extracts normalized items from the Researcher output envelope without parsing provider-specific response fields; Writer receives Curator output; Delivery runs only after all configured stages succeed; no downstream output contract changed.
- Scenario 9, Researcher Failure Halts Later Stages: PASS — provider call failure, malformed provider response, missing source context, normalization failure, and invalid normalized output each cause the run to fail at Researcher with a readable provider-aware reason; Curator, Writer, and delivery do not run; the ledger records the Researcher failure without stale later-stage records.
- Scenario 10, Diagnostics Remain Best-Effort: PASS — a Researcher failure diagnostic contains the failed stage, readable provider context when available, and bounded non-secret response or search context; when diagnostic preservation itself fails, the original Researcher failure remains reported normally with the failed stage and failure reason intact.
- Scenario 11, Secrets And Bounds: PASS — API keys, authentication headers, tokens, chat IDs, and environment values are absent from user-visible errors, ledger entries, and diagnostics; endpoint URLs contain no secret query parameters; raw provider response records and previews are bounded rather than unbounded payload dumps.
- Scenario 12, Automated Tests Avoid Live External Calls: PASS — Gemini compact ledger behavior, grounded URL normalization, OpenAI behavior, provider-neutral validation, downstream contract stability, Researcher failure and diagnostic behavior are all covered with controlled provider responses; all 132 repository tests pass without any live Gemini, OpenAI, Ollama, Telegram, or other external endpoint call.
- Overall verdict: PASS.

## Build log — 2026-06-25

- Spec used: `specs/provider_specific_researcher_prompts_feature.md`.
- Summary of work completed: Profiles can now provide provider-specific Researcher prompt paths, and the configured Researcher provider selects its matching prompt when available while existing profiles continue to use the original Researcher prompt path as a fallback. The default techno profile now declares Gemini and OpenAI Researcher prompts so provider testing can be done by changing the configured Researcher provider without manually swapping prompt files.
- Assumptions made: The existing Researcher prompt path remains required and remains the fallback path, preserving previous configuration-error behavior for profiles missing that field. Provider-specific prompt paths apply only to Researcher; Curator, Writer, template, stage order, provider selection, and delivery configuration remain unchanged. No new dependencies were added.
- Gaps or suspected bugs: Real Gemini, OpenAI, Ollama, Telegram, and live website URL checks were not called during implementation; live-provider confirmation remains for a separate evaluation session.

## Evaluation — 2026-06-25

- Eval file used: `evals/provider_specific_researcher_prompts_feature.eval.md`.
- Scenario 1, Gemini Provider Selects Gemini Researcher Prompt: PASS — when the configured Researcher provider is Gemini and the profile declares a Gemini-specific prompt path, the assembled pipeline delivers that Gemini-specific prompt to Researcher; the selected prompt file exists; the fallback path is not used instead.
- Scenario 2, OpenAI Provider Selects OpenAI Researcher Prompt: PASS — when the configured Researcher provider is OpenAI and the profile declares an OpenAI-specific prompt path, the assembled pipeline delivers that OpenAI-specific prompt to Researcher; the selected prompt file exists; the fallback path is not used instead.
- Scenario 3, Missing Provider-Specific Prompt Falls Back: PASS — when the configured Researcher provider has no matching provider-specific prompt path, the pipeline delivers the existing Researcher prompt path to Researcher; assembly succeeds when the fallback file exists; the missing provider-specific entry does not prevent fallback.
- Scenario 4, Existing Profiles Continue To Load: PASS — a profile declaring only the existing Researcher prompt path with no provider-specific paths assembles the pipeline successfully; Researcher receives the existing prompt path; no provider-specific configuration is required for the profile to work.
- Scenario 5, Missing Selected Provider Prompt Is A Configuration Error: PASS — when the selected provider-specific prompt file does not exist, configuration loading fails with a readable error before any stage executes; the missing file does not silently fall back to another prompt.
- Scenario 6, Unconfigured Provider Prompt Is Ignored: PASS — a provider-specific prompt entry for a provider not configured for the Researcher stage is ignored entirely; the configured provider selects its own provider-specific prompt when available, and falls back to the existing Researcher prompt path when not.
- Scenario 7, Other Stage Paths Remain Unchanged: PASS — Curator receives its configured Curator prompt path, Writer receives its configured Writer prompt path and template path, stage order is unchanged, model provider selection is unchanged, and delivery configuration is unchanged.
- Scenario 8, Provider Prompt Selection Does Not Change Provider Behavior: PASS — the configured Researcher provider, model name, and endpoint are all preserved when provider-specific prompt selection applies; only the Researcher prompt path changes according to the configured provider.
- Scenario 9, Automated Tests Avoid Live External Calls: PASS — Gemini and OpenAI provider-specific prompt selection, fallback prompt selection, missing selected prompt failures, and Curator, Writer, stage order, model provider, and delivery configuration stability are all covered with controlled configuration and fixture files; all 32 pipeline configuration tests pass without any live Gemini, OpenAI, Ollama, Telegram, or other external call.
- Overall verdict: PASS.

## Build log — 2026-06-26

- Spec used: `specs/provider_owned_stage_configuration_feature.md`.
- Summary of work completed: Pipeline stages now select their provider at the stage level, while model details, prompt paths, and template paths are required only when the selected provider needs them. Gemini, OpenAI, and Ollama stage capabilities remain available through the new configuration shape, and Researcher can now use a Bandcamp provider that collects Bandcamp Discover new hypnotic-techno/techno releases, normalizes them to title, URL, and summary items, and ignores unused Researcher prompt paths.
- Assumptions made: Bandcamp's Discover today facet is treated as the source of truth for the provider's release window, and the Bandcamp provider owns its request details rather than exposing them in pipeline configuration. Bandcamp responses with fewer than three usable items are allowed to reach existing Researcher validation, which rejects them with the existing item-count rule. No new dependencies were added.
- Gaps or suspected bugs: Real Gemini, OpenAI, Ollama, Telegram, and live Bandcamp endpoints were not called during implementation; live-provider confirmation remains for a separate evaluation session. The existing default-profile declaration test still expects `techno` while the project configuration declares `techno-releases`.

## Evaluation — 2026-06-26

- Eval file used: `evals/provider_owned_stage_configuration_feature.eval.md`.
- Scenario 1, Stage Provider Is Declared At Stage Level: PASS — pipeline configuration succeeds when each stage declares its provider, every stage assembles with the selected provider, and no stage executes during configuration loading.
- Scenario 2, Missing Stage Provider Is A Configuration Error: PASS — a configured stage that omits the provider field is rejected with a readable error before any stage runs.
- Scenario 3, Model-Backed Provider Requirements: PASS — configuration succeeds and the declared model name and endpoint are preserved when a model-backed provider is configured with both; omitting either field is rejected with a readable error before stages run.
- Scenario 4, Unsupported Provider Combinations: PASS — Researcher, Curator, and Writer stages each reject unsupported providers with a readable error and no successful provider response is produced; Researcher with an unsupported provider, Curator with an unsupported provider, and Writer with an unsupported provider are each covered.
- Scenario 5, Prompt And Template Requirements Are Provider-Owned: PASS — a prompt-using provider stage whose profile omits the required prompt path is rejected with a readable error before stages run; a Writer stage whose profile omits the template path is rejected with a readable error before stages run.
- Scenario 6, Existing Model-Backed Providers Remain Available: PASS — Gemini Researcher, OpenAI Researcher, Gemini Curator, OpenAI Curator, and Ollama Writer each produce results under controlled successful provider responses, and existing Researcher, Curator, and Writer validation rules continue to apply.
- Scenario 7, Bandcamp Researcher Loads With Provider Only: PASS — a Researcher configured with only a provider declaration for Bandcamp loads without requiring a model name, endpoint, API credential, or Researcher prompt.
- Scenario 8, Bandcamp Ignores Unused Researcher Prompt Paths: PASS — Bandcamp Researcher loads successfully when the selected profile declares Researcher prompt paths that Bandcamp does not use, including paths pointing to non-existent files.
- Scenario 9, Bandcamp Request Contract: PASS — Bandcamp Researcher issues a POST to the Bandcamp Discover endpoint with all required parameters including the configured tags, slice, time facet, cursor, category, geoname, size, and result types under a controlled response.
- Scenario 10, Bandcamp Normalizes Successful Results: PASS — at least three items are returned each with a title, URL, and summary; tracking query parameters are stripped from returned URLs; existing Researcher validation accepts the output; bounded non-secret source context is preserved in the output.
- Scenario 11, Bandcamp Skips Incomplete Results: PASS — source results missing a title, URL, or summary are excluded from returned items; complete results are still returned when present; when fewer than three complete items remain, the Researcher stage fails with a readable reason.
- Scenario 12, Bandcamp Failure Handling: PASS — Bandcamp network failures and malformed responses cause the Researcher stage to fail with readable reasons and no downstream stage success is reported from invalid Bandcamp output; no API keys, credentials, or environment values appear in failures or diagnostics.
- Scenario 13, No Extra Bandcamp Configuration Is Exposed: PASS — Bandcamp Researcher loads with only a provider declaration; no user-configurable tags, slice, time facet, cursor, result types, size, or endpoint are required in pipeline configuration.
- Scenario 14, Automated Tests Avoid Live External Calls: PASS — stage-level provider selection, provider-specific model requirements, prompt and template requirements, Bandcamp successful responses, and Bandcamp failure conditions are all covered with controlled configuration and controlled provider responses without any live external call; two pre-existing test failures about the configured default profile name are unrelated to provider-owned stage configuration behavior.
- Overall verdict: PASS.

## Build log — 2026-06-27

- Spec used: `specs/openclaw_cron_result_output_feature.md`.
- Summary of work completed: Command-line pipeline runs now print one parseable JSON result object to standard output with an explicit `SUCCESS` or `FAILURE` status, readable summary, selected profile when known, final output on success, stage or delivery failure details when applicable, and ledger or diagnostic paths when available. The process exit code now agrees with the reported JSON status, and incidental run output is kept out of the final standard-output result so OpenClaw can parse the outcome from standard output alone.
- Assumptions made: Standard error may still receive incidental progress output from underlying stages, but OpenClaw does not need standard error to determine the run result or user-facing reason. Startup failures may omit profile and artifact paths when the command cannot resolve them before the run starts. No new dependencies were added.
- Gaps or suspected bugs: Real Gemini, OpenAI, Ollama, Telegram, and live OpenClaw cron execution were not called during implementation; live-provider and runtime confirmation remain for a separate evaluation session. The focused OpenClaw CLI result tests pass, but the full repository suite still has pre-existing default-profile/configuration failures unrelated to this feature.

## Evaluation — 2026-06-26

- Eval file used: `evals/openclaw_cron_result_output_feature.eval.md`.
- Scenario 1, Successful Command Result: PASS — a successful pipeline run produces exactly one parseable JSON result on standard output reporting SUCCESS, including a readable success summary, the selected profile, the final pipeline output, and the ledger path, with a process exit code of 0.
- Scenario 2, Stage Failure Result: PASS — a stage failure produces exactly one parseable JSON result on standard output reporting FAILURE, identifying the failed stage, providing a readable reason and summary, including the profile, ledger path, and diagnostic artifact path when one is available, with a nonzero exit code and no successful reporting of remaining stages or delivery.
- Scenario 3, Delivery Failure Result: PASS — a delivery failure after all stages succeed produces exactly one parseable JSON result on standard output reporting FAILURE, identifying the failed provider, preserving the final pipeline output produced before delivery failed, providing a readable reason and summary, and including the profile and ledger path, with a nonzero exit code.
- Scenario 4, Startup Failure Result: PASS — a pipeline startup failure produces exactly one parseable JSON result on standard output reporting FAILURE with a readable summary and reason; the selected profile is included when it was known at the time of failure; the exit code is nonzero.
- Scenario 5, Standard Output Is Sufficient For OpenClaw: PASS — all run outcomes report success or failure through the JSON status field and user-facing explanation through the summary and reason fields on standard output alone; standard error carries incidental run output and is not needed to determine whether the run succeeded or to identify the user-facing reason for failure; exit code and JSON status agree in all cases.
- Scenario 6, Output Remains Single Parseable JSON: PASS — when incidental terminal output is produced during a pipeline run, it is directed to standard error rather than standard output, leaving standard output as exactly one parseable JSON result with the expected status and required fields intact.
- Scenario 7, Secret And Raw Payload Safety: PASS — the JSON result contains no configured API keys, access tokens, or Telegram credentials; delivery and stage failure reasons use concise readable messages rather than unbounded raw provider responses; diagnostic and ledger artifact paths appear as file path references rather than inline payloads.
- Scenario 8, Existing Pipeline Behavior Is Unchanged: PASS — stage validation, profile command-line selection, and Telegram delivery behavior remain unchanged; no new command-line flag or argument is needed to receive the JSON result; all automated tests for pipeline stage, delivery, and profile behavior pass without live external endpoint calls; the three pre-existing failures about the configured default profile name are unrelated to this feature.
- Overall verdict: PASS.

## Build log — 2026-06-27

- Spec used: `specs/default_profile_agnostic_tests_feature.md`.
- Summary of work completed: Active profile selection tests now verify explicit profile selection, default-profile resolution, missing-default failure, and checked-in configuration consistency without requiring any particular checked-in default profile name or requiring the checked-in configuration to declare a default profile.
- Assumptions made: The checked-in configuration may still declare a default profile, and when it does, active tests may verify that the declaration points to an existing configured profile. No runtime pipeline behavior was changed. No new dependencies were added.
- Gaps or suspected bugs: Real Gemini, OpenAI, Ollama, Telegram, Bandcamp, and OpenClaw calls were not run during implementation; live runtime confirmation remains for separate evaluation work.

## Evaluation — 2026-06-26

- Eval file used: `evals/default_profile_agnostic_tests_feature.eval.md`.
- Scenario 1, Explicit Profile Selection Is Independent Of Checked-In Defaults: PASS — the active explicit-profile test selects a profile by name from a controlled configuration fixture, and passes with no requirement that the checked-in configuration declare any particular default profile.
- Scenario 2, Default-Profile Resolution Uses A Controlled Default: PASS — the active default-profile resolution test uses a controlled configuration that declares an arbitrary default profile name, resolves that profile successfully, and the run uses that resolved profile without assuming the checked-in default profile has any specific value.
- Scenario 3, Missing-Default Failure Uses A Controlled Missing Default: PASS — the active missing-default test uses a controlled configuration that intentionally declares no default profile, confirms that loading fails with a readable reason before any stage runs, and the test is independent of the checked-in configuration.
- Scenario 4, Checked-In Configuration Checks Internal Consistency Only: PASS — the checked-in configuration tests confirm that declared profiles exist and that a declared default profile points to a configured profile; when no default profile is declared the absence is accepted rather than treated as a failure.
- Scenario 5, Checked-In Default Profile May Be Renamed Or Removed: PASS — no active test names `techno`, `techno-releases`, or any other specific profile value; checked-in configuration tests derive expectations from the current configuration state so renaming, replacing, or removing the default profile while the configuration remains internally consistent would not cause those tests to fail.
- Scenario 6, Historical Artifacts Are Not Rewritten: PASS — older profile names and topic-specific wording appear in historical build logs, evaluation entries, and prior specs without modification, and the active-test evaluation does not treat those historical records as failures.
- Scenario 7, Runtime Behavior Is Unchanged: PASS — explicit profile selection, default-profile resolution, and missing-default failure all produce the same observable outcomes as before; no prompt files, template files, profile content, delivery behavior, or model-provider behavior was altered by this cleanup.
- Scenario 8, Repository Tests Still Pass Without Live External Calls: PASS — all 144 repository tests pass under controlled inputs and mocks, covering explicit profile selection, controlled default-profile resolution, controlled missing-default failure, checked-in configuration consistency, and existing configuration, stage, Writer, delivery, and ledger behavior, with no live Gemini, OpenAI, Ollama, Telegram, Bandcamp, or OpenClaw call required.
- Overall verdict: PASS.

## Build log — 2026-06-27

- Spec used: `specs/writer_structured_note_tolerance_feature.md`.
- Summary of work completed: Writer now accepts generated item notes when a valid structured note list is returned directly, wrapped in Markdown formatting, or surrounded by explanatory text. Writer still preserves Curator titles, source URLs, item inclusion, and ascending rank order in the final outbound message, and unusable generated-note responses now produce diagnostics with bounded model-output context.
- Assumptions made: Valid generated notes may be recovered from common local-model formatting as long as the recovered note list has exactly one non-empty text note per curated item. No new dependencies were added.
- Gaps or suspected bugs: Real Gemini, OpenAI, Ollama, Telegram, Bandcamp, and OpenClaw calls were not run during implementation; live runtime confirmation remains for a separate evaluation session.

## Evaluation — 2026-06-26

- Eval file used: `evals/writer_structured_note_tolerance_feature.eval.md`.
- Scenario 1, Direct Structured Notes: PASS — when the model returns a valid note list directly, the Writer succeeds and the final message contains each generated note, every Curator title exactly, every Curator source URL exactly, and items presented in ascending rank order.
- Scenario 2, Markdown-Wrapped Structured Notes: PASS — when the model returns a valid note list inside Markdown code fences, the Writer succeeds, the generated notes appear in the final message without surrounding fence markup, and every Curator title, source URL, and rank order are preserved.
- Scenario 3, Explanatory Structured Notes: PASS — when the model returns a valid note list surrounded by explanatory text, the Writer succeeds, the generated notes appear in the final message without the surrounding explanatory text, and every Curator title, source URL, and rank order are preserved.
- Scenario 4, Curator Fields Remain Authoritative: PASS — the final message uses every Curator-provided title and source URL exactly as supplied, includes all curated items in ascending rank order, and generated notes cannot alter Curator titles, URLs, inclusion, or ordering regardless of what the model returns.
- Scenario 5, No Valid Structured Note List: PASS — when the model returns text containing no valid structured note list, the Writer fails with a readable reason, no partial successful outbound message is produced, and delivery does not run.
- Scenario 6, Wrong Number Of Notes: PASS — when the model returns a note list with fewer or more notes than curated items, the Writer fails with a readable reason indicating that the generated notes cannot be used for all curated items.
- Scenario 7, Empty Or Non-Text Notes: PASS — when the model returns a note list containing an empty note or a note that is not text, the Writer fails with a readable reason and no unusable note is inserted into a successful outbound message.
- Scenario 8, Diagnostics For Unusable Generated Notes: PASS — when the Writer cannot use the model response as generated notes, the ledger records the Writer stage failure, a diagnostic record is written identifying the failure as a model-output parsing or usability problem with bounded model-output context and a readable reason, and no API keys, authentication headers, tokens, or environment values appear in the diagnostic.
- Scenario 9, Successful Writer Runs Do Not Create Diagnostics: PASS — when the Writer succeeds, no diagnostic record is created and the ledger's Writer stage entry contains no reference to diagnostic information.
- Scenario 10, Existing Boundaries Are Preserved: PASS — Researcher and Curator behavior are unchanged, delivery still runs only after all pipeline stages succeed, no new external service is required, the Writer does not perform research or additional external calls, and failed model responses are not retried.
- Overall verdict: PASS.

## Build log — 2026-06-29

- Spec used: `specs/version_command_feature.md`.
- Summary of work completed: `python3 planner.py --version` now reports `infoPipeline 0.1.0` as a single standard-output line, exits successfully, and does not start a pipeline run. When `--version` is provided with another supported option, the version report is still returned without running the pipeline.
- Assumptions made: The first application version is `0.1.0`, and the version report is a plain text command-line response rather than the JSON result object used for pipeline runs. No new dependencies were added.
- Gaps or suspected bugs: Live Gemini, OpenAI, Ollama, Bandcamp, and Telegram calls were not run during implementation; this command is intended to avoid those calls.

## Evaluation — 2026-06-29

- Eval file used: `evals/version_command_feature.eval.md`.
- Scenario 1, Version Output: PASS — invoking the command with `--version` prints exactly `infoPipeline 0.1.0` as one standard-output line and exits successfully.
- Scenario 2, Version Does Not Run Pipeline: PASS — requesting the version completes immediately with no visible pipeline activity, no provider or delivery contact, and no ledger change.
- Scenario 3, Version Takes Precedence With Supported Options: PASS — when a supported profile option is supplied together with `--version`, the command still prints only the version line, exits successfully, and produces no pipeline side effects.
- Scenario 4, Normal Pipeline Invocation Is Unchanged: PASS — controlled normal invocations still report the existing pipeline result behavior, preserve profile selection and delivery outcomes, and do not print a version report unless requested.
- Scenario 5, Repository Checks Cover Version Behavior Without Live Calls: PASS — the controlled automated checks cover the version output, successful exit, absence of pipeline side effects, and precedence with supported options without requiring any live external endpoint.
- Overall verdict: PASS.

## Build log — 2026-06-29

- Spec used: `specs/standardize_spec_eval_templates_feature.md`.
- Summary of work completed: Future specification drafts now start from prompts that emphasize externally observable requirements, explicit scope, visible success and failure behavior, and build-session logging. Future evaluation drafts now start from prompts that emphasize referenced-spec-only grading, success and failure scenarios, controlled evaluation environments, product-behavior result reasons, and evaluation-session logging.
- Assumptions made: The reusable templates are documentation artifacts for future authors, so standardizing their authoring guidance is sufficient without changing runtime pipeline behavior. No new dependencies were added.
- Gaps or suspected bugs: No live Gemini, OpenAI, Ollama, Bandcamp, Telegram, or other external calls were run; this template update does not include the separate evaluation artifact that a later evaluation-authoring session will create.

## Evaluation — 2026-06-29

- Eval file used: `evals/standardize_spec_eval_templates_feature.eval.md`.
- Scenario 1, Specification Template Guides Observable Authoring: PASS — the specification template directs future authors toward externally observable product or artifact behavior and away from internal mechanisms unless those details are public requirements.
- Scenario 2, Specification Template Provides Required Sections And Build Logging: PASS — the specification template provides the required authoring sections and tells build-session authors to record a build log with the required contents without writing an evaluation entry.
- Scenario 3, Evaluation Template Guides Black-Box Scenarios: PASS — the evaluation template directs future evaluators to grade only stated specification behavior, include success and required failure expectations, and avoid unstated requirements.
- Scenario 4, Evaluation Template Provides Evaluation-Log Guidance: PASS — the evaluation template tells evaluation-session authors to append scenario-level PASS or FAIL results, one-sentence product or artifact behavior reasons, and an overall verdict while avoiding build-log entries and internal identifiers.
- Scenario 5, External Side Effects Are Rejected Unless Required: PASS — the evaluation template presents controlled local inputs as the default approach and discourages live external calls, external system changes, messages, notifications, or delivery actions unless the referenced specification requires them.
- Scenario 6, Runtime Pipeline Behavior Is Unchanged: PASS — the completed feature leaves command-line pipeline behavior, provider behavior, prompt content, runtime configuration, and delivery behavior unchanged, and template standardization is verifiable without live external calls.
- Overall verdict: PASS.

## Build log — 2026-06-29

- Spec used: `specs/validate_config_command_feature.md`.
- Summary of work completed: `python3 planner.py --validate-config` now checks whether the configured pipeline can be loaded and assembled for the resolved profile and reports the result to standard output without running the pipeline. With no profile selected it validates the configured default profile; with a profile selected it validates that profile. A loadable configuration produces a readable success result identifying the validated profile and a zero exit status; a configuration that cannot be loaded or assembled produces a readable failure result with a reason, identifies the selected profile when known, and exits non-zero. The reported outcome and the exit status always agree. The command contacts no Researcher, Curator, Writer, or Delivery provider, writes no ledger, and attempts no delivery on either success or failure, and requires no live credentials or network access. Existing normal-run, `--version`, and profile-selection behavior is unchanged.
- Assumptions made: The success and failure results reuse the existing JSON command-result shape (a `status` of `SUCCESS` or `FAILURE` with a readable `summary`, plus a `reason` and `profile` where applicable) for consistency with the established command-line result surface; the spec requires only readable, machine-parseable success/failure reporting and does not prescribe field names. Validation exercises the existing configuration load-and-assemble path, which also confirms enabled delivery providers can be assembled. Incidental output from the load path is directed to standard error so standard output carries only the result object. No new dependencies were added.
- Gaps or suspected bugs: No live Gemini, OpenAI, Ollama, Bandcamp, or Telegram calls were run during implementation; this command is intended to validate configuration loadability without contacting providers or requiring credentials. Configuration loadability does not guarantee that providers will succeed at run time, since credentials and network reachability are not checked, consistent with the spec's stated scope.

## Evaluation — 2026-06-29

- Eval file used: `evals/validate_config_command_feature.eval.md`.
- Scenario 1, Successful Validation Reports Success And Exits 0: PASS — with no profile selected the command prints a single readable result clearly indicating configuration validation succeeded and naming the validated profile, with no incidental text on standard output, and exits with status 0.
- Scenario 2, Successful Validation Has No Run, Provider, Ledger, Or Delivery Side Effects: PASS — the command reports the validation result and stops without starting any pipeline stage or delivery, completing successfully even when all network connections are blocked, and leaving every existing run record unchanged with no new records created.
- Scenario 3, Unloadable Configuration Reports A Readable Failure And Exits Non-Zero: PASS — selecting an unknown profile yields a single readable result clearly indicating failure with a reason explaining the profile is unknown and naming the selected profile, while creating or modifying no run record, and exits with a non-zero status.
- Scenario 4, Reported Outcome And Exit Status Always Agree: PASS — the loadable case reports success paired with a zero exit status and the unloadable case reports failure paired with a non-zero exit status, so reported outcome and exit status agree in both directions.
- Scenario 5, Profile Selection Determines What Is Validated: PASS — invoked with no profile the result reports the configured default profile, and invoked with a named loadable profile the result reports that named profile, each succeeding with an agreeing zero exit status.
- Scenario 6, Existing Command-Line Behavior Is Unchanged: PASS — version reporting still prints the version and exits 0 with no validation result, and normal-run and profile-selection behavior is unchanged, with a validation result printed only when the validate-config option is provided.
- Overall verdict: PASS.

## Build log — 2026-06-30

- Spec used: `specs/configurable_researcher_discovery_feature.md`.
- Summary of work completed: Source-backed Bandcamp Researcher discovery criteria can now be declared in pipeline configuration, validated before a run, and used for Bandcamp Discover candidate collection. Bandcamp Researcher runs without configured discovery continue to use the previous default discovery behavior. The checked-in default pipeline now declares the existing Bandcamp discovery criteria explicitly, and durable documentation describes the source-backed discovery configuration contract.
- Assumptions made: Bandcamp is the only currently supported source-backed Researcher provider, so the new discovery contract is scoped to Bandcamp Discover criteria. Discovery configuration is a stage-level source-provider setting and is rejected for model-backed Researcher providers, which continue to use prompt paths for discovery behavior. No new dependencies were added.
- Gaps or suspected bugs: Live Gemini, OpenAI, Ollama, Bandcamp, and Telegram calls were not run during implementation; live runtime confirmation remains for a separate evaluation session.

## Evaluation — 2026-06-30

- Eval file used: `evals/configurable_researcher_discovery_feature.eval.md`.
- Scenario 1, Configured Bandcamp Discovery Loads And Runs: PASS — a Bandcamp configuration with valid discovery criteria loads successfully, collects at least three complete controlled candidates, returns normalized title, URL, and summary fields, and is accepted for continuation.
- Scenario 2, Configured Criteria Are Sent To Bandcamp Discover: PASS — the controlled Bandcamp endpoint observes the configured category, tags, geography, slice, time facet, cursor, size, and included result types exactly rather than the prior defaults.
- Scenario 3, Omitted Discovery Uses Previous Default Behavior: PASS — when discovery criteria are omitted, Bandcamp collection still loads and sends the previous default criteria while returning complete normalized items.
- Scenario 4, Source Context Includes Bounded Discovery Criteria: PASS — successful Bandcamp output includes readable bounded source context with the discovery criteria that were sent and no observed secret credentials or environment values.
- Scenario 5, Malformed Bandcamp Discovery Is Rejected Before Stages Run: PASS — malformed Bandcamp discovery configuration is rejected during configuration loading with a readable reason before provider contact, stage execution, ledger mutation, or delivery.
- Scenario 6, Discovery On Model-Backed Researcher Is Rejected: PASS — model-backed Researcher configuration that declares source discovery criteria fails validation before stages run, with a readable reason that discovery configuration is invalid for that provider.
- Scenario 7, Model-Backed Researcher Prompt Behavior Remains Unchanged: PASS — controlled Gemini and OpenAI Researcher runs continue to use configured prompt behavior and model request contracts, returning normalized items without requiring or sending Bandcamp discovery criteria.
- Scenario 8, Non-Researcher Behavior Remains Unchanged: PASS — controlled pipeline and configuration checks show discovery criteria affect Bandcamp candidate collection while Curator, Writer, Delivery, profile selection, prompt paths, templates, models, ledgers, and validation behavior continue to follow their existing configuration.
- Scenario 9, Checked-In Default Configuration Is Loadable: PASS — `python3 planner.py --validate-config` reports a machine-parseable success result identifying `techno-releases`, exits with status 0, and does not run pipeline stages or delivery.
- Scenario 10, Bandcamp Source Failures Remain Readable And Halt The Pipeline: PASS — controlled Bandcamp malformed-response and too-few-item cases fail at Researcher with readable reasons, prevent later pipeline progress, and expose no observed API keys, authentication headers, tokens, chat IDs, or environment values.
- Scenario 11, Automated Tests Avoid Live External Calls: PASS — the focused and full automated checks cover configured discovery, default discovery, invalid discovery, model-backed rejection, prompt-backed research, and downstream stability using controlled inputs with no live external calls required.
- Overall verdict: PASS.
