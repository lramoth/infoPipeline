# Spec: Writer Authoritative Message Assembly

## Objective

Prevent model-generated text from changing curator-provided titles, source URLs, or item ordering while keeping final outbound message presentation configurable through a Writer template.

## Background

The Writer currently uses a local model to turn curated items into an outbound message. A Writer run produced a readable outbound message, but one source URL differed from the Curator's URL because the model omitted a slug segment.

The Curator output is the authoritative source for each item's title, URL, summary, curation reason, and rank. The local model is useful for concise prose, but it should not be the authority for fields that must be preserved exactly.

The Writer prompt may change over time to alter tone, length, or prose guidance. Final outbound message presentation may also change over time. Preserving curator-provided titles, URLs, and order must not depend on parsing a model-generated final briefing layout or embedding prompt-specific presentation details in code.

The Writer template is stored alongside the Writer prompt as `prompts/writers/template.md`. The template owns final outbound message presentation.

Related specs:
- `specs/writer_feature.md`
- `specs/writer_url_validation_fix.md`
- `specs/outbound_message_terminology_cleanup.md`

## Requirements

- The Writer shall preserve each curated item's title exactly in the final outbound message.
- The Writer shall preserve each curated item's source URL exactly in the final outbound message.
- The Writer shall present curated items in ascending rank order in the final outbound message.
- The Writer shall include every curated item in the final outbound message.
- The Writer shall use the configured local model only for generated item prose.
- The Writer shall not treat model-generated titles, source URLs, or rank order as authoritative.
- The Writer shall not require model-generated final briefing headings, source labels, bullets, or markdown structure to be parsed in order to preserve curator-provided titles, URLs, or rank order.
- The Writer prompt shall communicate that the model is responsible for item prose, not authoritative titles, URLs, or item ordering.
- The Writer shall load a configurable outbound message template from `prompts/writers/template.md` by default.
- The Writer template shall define the final outbound message presentation using placeholders for the complete item list and for each item's title, generated note, and source URL.
- The Writer shall produce the final outbound message by combining curator-provided fields, generated item prose, and the configured template.
- The Writer shall not hard-code prompt-specific final message headings, source-label wording, bullet styles, or markdown presentation in Writer logic.
- The Writer shall continue to return a single outbound message string.
- The Writer shall continue to reject an empty curated item list.
- The Writer shall continue to reject missing or empty prompt content.
- The Writer shall reject missing or empty template content with a readable error.
- The Writer shall continue to reject model execution failures with a readable error.

## Inputs

- Curator output containing ranked curated items.
- A configured Writer prompt.
- A configured Writer template.
- A local model response containing generated prose for the curated items.

## Outputs

- A single outbound message string.

## Behavior

1. Receive Curator output.
2. Load the configured Writer prompt.
3. Load the configured Writer template.
4. Use the configured local model to generate concise prose for the curated items.
5. Produce a final outbound message containing all curated items by applying the configured template.
6. Ensure the final outbound message uses the exact title and exact source URL from each corresponding Curator item.
7. Ensure the final outbound message presents items in ascending rank order.
8. Validate the final outbound message before returning it.

## Failure Handling

- If the Curator output is empty, the Writer shall fail with a readable reason.
- If the configured Writer prompt is missing or empty, the Writer shall fail with a readable reason.
- If the configured Writer template is missing, empty, or missing required placeholders, the Writer shall fail with a readable reason.
- If the local model cannot produce usable item prose, the Writer shall fail with a readable reason.
- If a final outbound message cannot be produced while preserving curator-provided titles, URLs, and rank order, the Writer shall fail with a readable reason.

## Validation Failure

- The final output is not a string.
- A curated item is missing from the final outbound message.
- A final item section is missing the exact title from the corresponding Curator item.
- A final item section is missing the exact source URL from the corresponding Curator item.
- A final item section contains no readable prose.
- Items do not appear in ascending rank order.

## Validation Success

- The final outbound message is a non-empty string.
- Every curated item appears in the final outbound message.
- Every final item section contains the exact title from the corresponding Curator item.
- Every final item section contains the exact source URL from the corresponding Curator item.
- Every final item section contains readable prose.
- Items appear in ascending rank order.

## Acceptance Criteria

- Given a curated item with a long source URL, the final outbound message contains that exact URL.
- Given a local model response that changes a curated item URL, the final outbound message still contains the Curator's exact URL for that item.
- Given a local model response that omits a curated item URL, the final outbound message still contains the Curator's exact URL for that item.
- Given a local model response that changes a curated item title, the final outbound message still contains the Curator's exact title for that item.
- Given multiple curated items with shared source URLs, the final outbound message includes the shared URL in each corresponding item section.
- Given curated items with ranks out of input-list order, the final outbound message presents them in ascending rank order.
- Given a Writer prompt that changes prose guidance without changing the template, the final outbound message still preserves curator-provided titles, source URLs, and rank order.
- Given a Writer template that changes final-message presentation wording, headings, bullets, source-label wording, or markdown style, the final outbound message follows the configured template while still preserving curator-provided titles, source URLs, and rank order.
- Given a Writer template missing the complete item-list placeholder, title placeholder, note placeholder, or URL placeholder, the Writer fails with a readable reason.
- Given a local model response with no usable item prose, the Writer fails with a readable reason.

## Constraints

- Writer shall not perform ranking or filtering.
- Writer shall not perform additional research.
- Writer shall not make Gemini API calls.
- Writer shall not change Curator output.
- Delivery behavior is unchanged.

## Out of Scope

- Changing Researcher behavior.
- Changing Curator behavior.
- Changing Delivery behavior.
- Adding new external services.
- Evaluating the factual quality of generated prose beyond preserving required curated items.
