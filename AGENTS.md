# Agent Instructions — infoPipeline

## Stack & conventions
- Prefer the Python standard library when practical. Add dependencies only when they materially simplify implementation.
- Planner is the coordinator.
- Researcher stage call Gemini API search
- Curator stage takes search results and applies a prompt (via the Gemini
  API) that curates what was found.
- Writer stage call local Ollama (model: gemma4:e4b).
- Delivery stage posts to Telegram.
- Runs under the OpenClaw agent runtime.

## Dependencies
External dependencies may be added when they provide significant value and avoid reimplementing established functionality.
When adding a dependency:
- add it to requirements.txt
- justify it in the build log assumptions
- do not introduce unnecessary dependencies
Well-established third-party libraries may be added when implementing the feature correctly would otherwise require reimplementing substantial functionality.

## Workflow
- Your only source of requirements is the spec file referenced in the prompt.
- If a requirement is ambiguous or missing, log it under "Open questions"
  in eval_log.md and stop — don't guess.
- If implementation details are unspecified, choose the simplest reasonable
  implementation that satisfies the spec. This includes module names,
  function names, class names, internal data structures, and helper methods,
  unless the spec explicitly defines them.
- Calls to Gemini and Telegram aren't needed while implementing logic.
- Real calls happen only during the eval step, run as a separate session:
  it should call the real Gemini API and the real Telegram endpoint, since
  downstream evaluation needs genuine search data and a genuine delivery
  confirmation.
- Do not explore, list, or reference anything outside this directory tree.

## Definition of done
- Code satisfies the spec.
- Tests cover only what the spec explicitly states — no speculative
  edge-case tests for unstated behavior.
- Append a `## Build log — YYYY-MM-DD` entry to eval_log.md: what you built (or
  documented), the spec used, any assumptions, gaps, or suspected bugs.

## Eval log conventions
`eval_log.md` is append-only.
New entries must be written at the end of the file.
Existing entries must never be reordered, modified, or inserted above.

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
