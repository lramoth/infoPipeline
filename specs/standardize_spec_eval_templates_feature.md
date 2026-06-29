# Spec: Specification and Evaluation Template Standardization

## Objective

Future project specifications and evaluations should start from reusable templates that guide authors toward black-box, observable behavior and the project's logging conventions.

## Background

The project uses behavioral specifications, separate evaluation artifacts, and append-only entries in `eval_log.md` to coordinate autonomous feature development. The reusable templates should make those conventions clear before authors draft new artifacts.

## Requirements

- The specification template shall direct authors to describe externally observable product or artifact behavior rather than implementation details.
- The specification template shall warn authors not to require file names, class names, function names, data structures, algorithms, or library choices unless those details are observable public requirements.
- The specification template shall provide sections for objective, background, observable requirements, inputs and outputs, behavior, failure behavior, constraints, out-of-scope work, and completion logging.
- The specification template shall tell build-session authors to append a build log entry, not an evaluation entry.
- The evaluation template shall direct authors to evaluate only behavior stated in the referenced specification.
- The evaluation template shall include guidance for both successful and failing observable scenarios.
- The evaluation template shall tell evaluation-session authors to record scenario results in the required evaluation-log style, using product behavior language rather than implementation identifiers.
- The evaluation template shall discourage live external API calls and external side effects unless the referenced specification explicitly requires them.
- The reusable template changes shall not alter runtime pipeline behavior.

## Acceptance Criteria

- A future author can use the specification template without being prompted toward internal APIs or implementation mechanisms.
- A future author can use the evaluation template to define black-box scenarios that include success and failure expectations.
- The templates distinguish build-session logging from evaluation-session logging.
- No command-line pipeline behavior, provider integration, prompt content, runtime configuration, or delivery behavior is changed.

## Out of Scope

- Changing runtime pipeline code.
- Creating the evaluation artifact for this task.
- Performing live Gemini, OpenAI, Ollama, Bandcamp, Telegram, or other external calls.

## Completion

When implementation is complete, append a `## Build log — 2026-06-29` entry to `eval_log.md` describing the template behavior completed for this specification.
