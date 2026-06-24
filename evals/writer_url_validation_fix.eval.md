# Eval: Writer Shared Source URL Validation

Purpose
Validate the observable behavior described in `specs/writer_url_validation_fix.md`.

Do not grade implementation details such as:
- class names
- method names
- helper modules
- validation-result shapes
- internal data structures.

Grade only observable behavior.
Do not infer requirements that are not stated in the specification.

## Evaluation Environment
Unless explicitly required by the spec:
- Do not perform live Gemini, Ollama, Telegram, or other external API calls.
- Do not perform web searches.
- Do not resolve redirects.
- Do not fetch canonical URLs.
- Do not modify external systems.
- Use mocks, fixtures, or controlled test inputs.

## Scenario 1: Distinct URLs In Ranked Item Sections
Given a Telegram message is generated from two curated items with distinct source URLs,
When both items appear in ascending rank order and each item's section contains that item's title, summary text, and source URL,
Then:
- validation passes

## Scenario 2: Shared URL Repeated In Each Ranked Item Section
Given a Telegram message is generated from two curated items that share the same source URL,
When both items appear in ascending rank order and each item's section contains that item's title, summary text, and the shared source URL,
Then:
- validation passes
- validation does not fail solely because the source URL is repeated

## Scenario 3: Shared URL Present In Only One Item Section
Given a Telegram message is generated from two curated items that share the same source URL,
When both item titles and summary text appear but the shared source URL appears in only one item's section,
Then:
- validation fails
- the message is treated as missing a source URL for the item section that does not contain it

## Scenario 4: Missing Item Title
Given a Telegram message is generated from curated items,
When any curated item title is absent from the message,
Then:
- validation fails

## Scenario 5: Missing Item URL
Given a Telegram message is generated from curated items,
When any curated item source URL is absent from that item's message section,
Then:
- validation fails

## Scenario 6: Missing Summary Text
Given a Telegram message is generated from curated items,
When any item section contains the title and source URL but no summary text,
Then:
- validation fails

## Scenario 7: Items Out Of Rank Order
Given a Telegram message is generated from multiple curated items,
When the items appear out of ascending rank order,
Then:
- validation fails

## Grading instructions
For each scenario:
- PASS if the observable behavior matches the specification.
- FAIL if the observable behavior differs from the specification.
Append results to `eval_log.md` and provide an overall verdict.
Overall verdict is PASS only if every scenario passes.
