# Eval: Writer Authoritative Message Assembly

Purpose
Validate the observable behavior described in `specs/writer_authoritative_assembly_feature.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- validation-result shapes
- internal data structures
- parsing or assembly algorithms.

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live Gemini, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not send Telegram messages or modify external systems.
- Use mocks, fixtures, or controlled test inputs for runtime checks.

## Scenario 1: Long Curator URL Is Preserved Exactly
Given the Writer runs with a curated item containing a long source URL,
When the local model provides usable item prose,
Then:
- the outbound message is a non-empty string
- the outbound message contains the exact curated source URL
- the outbound message contains the exact curated title
- the item section contains readable prose

## Scenario 2: Model-Changed URL Is Not Authoritative
Given the Writer runs with a curated item containing a source URL,
When the local model response changes or shortens that source URL,
Then:
- the outbound message contains the exact curated source URL
- the model-changed source URL does not replace the curated source URL
- the stage is considered successful if the generated prose is otherwise usable

## Scenario 3: Model-Omitted URL Is Not Authoritative
Given the Writer runs with a curated item containing a source URL,
When the local model response omits the source URL,
Then:
- the outbound message still contains the exact curated source URL
- the item section contains readable prose
- the stage is considered successful if the generated prose is otherwise usable

## Scenario 4: Model-Changed Title Is Not Authoritative
Given the Writer runs with a curated item containing a title,
When the local model response changes that title,
Then:
- the outbound message contains the exact curated title
- the model-changed title does not replace the curated title
- the stage is considered successful if the generated prose is otherwise usable

## Scenario 5: Every Curated Item Is Included In Rank Order
Given the Writer runs with multiple curated items whose input order differs from their rank order,
When the local model provides usable item prose for the curated items,
Then:
- every curated item appears in the outbound message
- each item section contains that item's exact curated title and exact curated source URL
- items appear in ascending rank order
- no curated item is dropped, merged, split, or reordered by the local model response

## Scenario 6: Shared Source URLs Are Repeated Per Item Section
Given the Writer runs with multiple curated items that share the same source URL,
When the local model provides usable item prose for each item,
Then:
- every curated item appears in the outbound message
- each corresponding item section contains the shared source URL
- the stage does not fail solely because multiple items share the same source URL

## Scenario 7: Prompt Changes Do Not Affect Authoritative Fields
Given the Writer runs with a valid configured prompt and template,
When the configured prompt wording changes its prose guidance but the template remains valid,
Then:
- the outbound message still preserves every curated title exactly
- the outbound message still preserves every curated source URL exactly
- items still appear in ascending rank order
- the stage is considered successful if the generated prose is otherwise usable

## Scenario 8: Template Controls Final Presentation
Given the Writer runs with a valid configured template that changes visible wording, headings, bullet style, source-label wording, or markdown style,
When the local model provides usable item prose,
Then:
- the outbound message follows the configured template presentation
- the outbound message still preserves every curated title exactly
- the outbound message still preserves every curated source URL exactly
- items still appear in ascending rank order

## Scenario 9: Missing Or Invalid Inputs Fail Readably
Given the Writer runs,
When the curated item list is empty, the configured prompt is missing or empty, or the configured template is missing or empty,
Then:
- the stage is considered failed
- the failure reason is readable
- no outbound message is returned as a successful result

## Scenario 10: Template Missing Required Placeholders Fails Readably
Given the Writer runs with a configured template,
When the template is missing the complete item-list placeholder, title placeholder, note placeholder, or URL placeholder,
Then:
- the stage is considered failed
- the failure reason is readable
- no outbound message is returned as a successful result

## Scenario 11: Unusable Model Prose Fails Readably
Given the Writer runs with valid curated items, a valid prompt, and a valid template,
When the local model cannot produce usable item prose for the curated items,
Then:
- the stage is considered failed
- the failure reason is readable
- no outbound message is returned as a successful result

## Scenario 12: Existing Boundaries Remain Unchanged
Given the Writer runs with controlled curated items and controlled local-model behavior,
When the outbound message is generated,
Then:
- no Gemini API call is required
- no additional research is performed
- Curator output is not changed
- Delivery behavior is not invoked or changed by Writer message generation

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` under an `## Evaluation — YYYY-MM-DD` entry and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
