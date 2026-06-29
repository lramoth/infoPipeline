# Eval: Specification and Evaluation Template Standardization

## Purpose

Validate only the observable behavior described in `specs/standardize_spec_eval_templates_feature.md`.

Do not infer requirements that are not stated in the referenced specification.

Do not grade or report implementation details in eval_log.md, including:
- class names
- method names
- helper modules
- internal data structures
- algorithms
- library choices

Write scenario results from the perspective of a future artifact author or project evaluator.

## Evaluation Environment

Unless explicitly required by the spec:
- Do not perform live Gemini, OpenAI, Ollama, Bandcamp, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send messages, write to external systems, or trigger delivery behavior.
- Use repository inspection and controlled local checks only.

## Scenario 1: Specification Template Guides Observable Authoring

Given the reusable specification template is inspected,
When a future author follows its guidance,
Then:
- the author is directed to describe externally observable product or artifact behavior
- the author is not prompted toward internal APIs or implementation mechanisms
- the author is warned not to require file names, class names, function names, data structures, algorithms, or library choices unless those details are observable public requirements

## Scenario 2: Specification Template Provides Required Sections And Build Logging

Given the reusable specification template is inspected,
When its structure and completion guidance are reviewed,
Then:
- it provides sections for objective, background, observable requirements, inputs and outputs, behavior, failure behavior, constraints, out-of-scope work, and completion logging
- it tells build-session authors to append a build log entry
- it does not tell build-session authors to write an evaluation entry
- the build-log guidance asks for the spec used, observable work completed, assumptions made, and gaps or suspected bugs

## Scenario 3: Evaluation Template Guides Black-Box Scenarios

Given the reusable evaluation template is inspected,
When a future evaluator follows its guidance,
Then:
- the evaluator is directed to evaluate only behavior stated in the referenced specification
- the evaluator is guided to define successful observable behavior
- the evaluator is guided to define required failure, rejection, halted-work, or preserved-state behavior when the specification requires it
- the evaluator is told not to infer unstated requirements

## Scenario 4: Evaluation Template Provides Evaluation-Log Guidance

Given the reusable evaluation template is inspected,
When its grading and logging guidance are reviewed,
Then:
- it tells evaluation-session authors to append an evaluation entry
- it requires scenario-level PASS or FAIL results
- it requires one-sentence reasons written in product or artifact behavior language
- it requires an overall verdict
- it tells evaluation sessions not to write build-log entries
- it discourages implementation identifiers in evaluation-log reporting

## Scenario 5: External Side Effects Are Rejected Unless Required

Given the reusable evaluation template is inspected,
When its evaluation environment guidance is reviewed,
Then:
- live external API calls are discouraged unless the referenced specification explicitly requires them
- external system modifications are discouraged unless the referenced specification explicitly requires them
- messages, notifications, or delivery actions are discouraged unless the referenced specification explicitly requires them
- controlled local inputs are presented as the default evaluation approach

## Scenario 6: Runtime Pipeline Behavior Is Unchanged

Given the completed feature changes are inspected,
When runtime-facing files and behavior surfaces are reviewed,
Then:
- command-line pipeline behavior is unchanged
- provider integration behavior is unchanged
- prompt content is unchanged
- runtime configuration is unchanged
- delivery behavior is unchanged
- no live external call is required to verify the template standardization

## Grading instructions

For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.

Append an evaluation entry to `eval_log.md` using the format in `AGENTS.md`:
- eval file used
- PASS/FAIL result for each scenario
- one-sentence product-behavior reason for each scenario result
- overall verdict

Overall verdict is PASS only if every scenario passes.

Evaluation sessions must not write build-log entries.
