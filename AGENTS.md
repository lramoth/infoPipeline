# Agent Instructions — infoPipeline

## Stack & conventions
- Prefer the Python standard library when practical. Add dependencies only when they materially simplify implementation.
- Planner is the coordinator.
- Researcher stage uses the configured model provider for search. Supported
  providers: Gemini and OpenAI.
- Curator stage takes search results and applies a prompt using the configured
  model provider. Supported providers: Gemini and OpenAI.
- Writer stage uses configured provider logic, currently supporting only local
  Ollama (model: gemma4:e4b).
- Delivery stage posts to Telegram.
- Designed for command-line invocation.

## Dependencies
External dependencies may be added when they provide significant value and avoid reimplementing established functionality.
When adding a dependency:
- add it to requirements.txt
- justify it in the build log assumptions
- do not introduce unnecessary dependencies
Well-established third-party libraries may be added when implementing the feature correctly would otherwise require reimplementing substantial functionality.

## Workflow
- For code changes, new features, bug fixes, or any change that affects how
  the application works, your only source of requirements is the spec file
  referenced in the prompt.
- Documentation-only changes may be made without a spec when the prompt asks
  for documentation updates and does not require application behavior changes.
- If a requirement is ambiguous or missing, log it under "Open questions"
  at the end of eval_log.md with a reference to the relevant spec, then stop
  — don't guess.
- If implementation details are unspecified, choose the simplest reasonable
  implementation that satisfies the spec. This includes module names,
  function names, class names, internal data structures, and helper methods,
  unless the spec explicitly defines them.
- Calls to Gemini, OpenAI, Ollama, and Telegram aren't needed while implementing
  logic.
- Real calls happen only during the eval step, run as a separate session:
  it should call the real configured model provider endpoints and the real
  Telegram endpoint when the evaluation scenario requires genuine search,
  model, or delivery confirmation.
- Do not explore, list, or reference anything outside this directory tree.

## Definition of done
- Code satisfies the spec.
- Tests cover only what the spec explicitly states — no speculative
  edge-case tests for unstated behavior.
- Append a `## Build log — YYYY-MM-DD` entry to eval_log.md: what you built (or
  documented), the spec used, any assumptions, gaps, or suspected bugs.

## Eval log conventions
- `eval_log.md` is append-only.
- New entries must be written at the end of the file.
- Existing entries must never be reordered, modified, or inserted above.
- Drafting or editing spec/eval artifacts does not require an eval_log.md entry unless explicitly requested.
- Architecture-review-only work does not require an eval_log.md entry, even
  when `architecture.md` is updated to correct or clarify the architectural
  description. If `architecture.md` is revised as part of implementing a spec
  during a build session, include that documentation work in the build-log
  entry for the spec.

Build sessions append entries under:

```markdown
## Build log — YYYY-MM-DD
```

and must include:

- spec used
- summary of work completed
- assumptions made
- gaps or suspected bugs

The summary of work completed must describe externally observable behavior and completed capabilities, not internal implementation details.

Implementation details may be included only under `Assumptions made`, `Gaps or suspected bugs`, or when required to explain a public contract decision.

Evaluation sessions append entries under:

```markdown
## Evaluation — YYYY-MM-DD
```

and must include:

- eval file used
- PASS/FAIL result for each scenario
- one-sentence reason for each scenario result
- overall verdict

Evaluation reasons should describe observable behavior, not internal implementation details.

Evaluation log reasons must be written as black-box observable behavior.
Do not mention implementation identifiers or test mechanics, including class names,
function names, method names, file paths, return values, booleans, exception class
names, exact helper inputs, or internal algorithms.

Write reasons from the product behavior perspective.

Good:
- PASS — an empty curated list is rejected with a readable reason that no items are present.

Bad:
- PASS — `Curator.validate([])` returns `False` citing no items.

Build sessions must never write evaluation entries.
Evaluation sessions must never write build-log entries.

## Governance
Read `governance.md` before drafting specifications, evaluations, or eval-log entries.
This project treats specs and evals as black-box behavioral artifacts: describe observable behavior, not implementation details.
