# Agent Instructions — infoPipeline

## Stack & conventions
- Prefer the Python standard library when practical. Add dependencies only when they materially simplify implementation.
- Planner Agent is the coordinator for feature workflow execution.
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
- justify it in the Work File assumptions
- do not introduce unnecessary dependencies
Well-established third-party libraries may be added when implementing the feature correctly would otherwise require reimplementing substantial functionality.

## Workflow
- `development_workflow.md` is the source of truth for the autonomous feature
  development workflow.
- For code changes, new features, bug fixes, or any change that affects how
  the application works, your only source of requirements is the spec file
  referenced in the prompt.
- Documentation-only changes may be made without a spec when the prompt asks
  for documentation updates and does not require application behavior changes.
- If a requirement is ambiguous or missing, report the ambiguity to the
  Planner Agent for recording in the Work File, then stop — don't guess.
- If implementation details are unspecified, choose the simplest reasonable
  implementation that satisfies the spec. This includes module names,
  function names, class names, internal data structures, and helper methods,
  unless the spec explicitly defines them.
- Calls to Gemini, OpenAI, Ollama, and Telegram aren't needed while implementing
  logic.
- Real calls happen only during the evaluation step, run as a separate session:
  it should call the real configured model provider endpoints and the real
  Telegram endpoint when the evaluation scenario requires genuine search,
  model, or delivery confirmation.
- Do not explore, list, or reference anything outside this directory tree.

## Definition of done
- Code satisfies the spec.
- Tests cover only what the spec explicitly states — no speculative
  edge-case tests for unstated behavior.
- Implementation and evaluation results are reported to the Planner Agent for
  recording in the Work File as described in `development_workflow.md`.

Implementation summaries, observations, assumptions, limitations, future work,
and evaluation results must describe externally observable behavior and
completed capabilities, not internal implementation details.

Implementation details may be included only under assumptions, limitations,
future work, or when required to explain a public contract decision.

Evaluation results should describe observable behavior, not implementation
details. Do not mention implementation identifiers or test mechanics, including
class names, function names, method names, file paths, return values, booleans,
exception class names, exact helper inputs, or internal algorithms.

Write reasons from the product behavior perspective.

Good:
- PASS — an empty curated list is rejected with a readable reason that no items are present.

Bad:
- PASS — `Curator.validate([])` returns `False` citing no items.

Implementation Agents must not evaluate correctness against the specification.
Evaluation Agents must not modify implementation.

## Governance
Read `governance.md` before drafting specifications, evaluations, or Work File entries.
This project treats specs and evals as black-box behavioral artifacts: describe observable behavior, not implementation details.
