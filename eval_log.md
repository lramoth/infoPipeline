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
