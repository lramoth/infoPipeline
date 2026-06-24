# Spec: Writer Validation Supports Shared Source URLs

## Objective
Writer validation should correctly validate Telegram messages when multiple curated items share the same source URL.

## Background
Curator now allows shared source URLs because URLs are treated as citations, not unique item identifiers. A Writer run produced a message containing all curated item titles and URLs, but validation failed because two items shared the same URL.
The validation failure reported a missing title even though the title appeared in the message. The issue was caused by validating repeated URLs as if each URL were unique.

## Requirements
- Writer validation shall support multiple curated items sharing the same URL.
- Writer validation shall not assume each item URL appears only once in the message.
- Writer validation shall validate each item using its title, summary text, and source URL within that item's own message section.
- Writer validation shall continue to require every curated item title to appear in the message.
- Writer validation shall continue to require every curated item URL to appear in the message.
- Writer validation shall continue to require summary text for each item.
- Writer validation shall continue to require items to appear in ascending rank order.
- Writer validation shall fail when an item's title is absent.
- Writer validation shall fail when an item's URL is absent.
- Writer validation shall fail when an item has no summary text.
- Writer validation shall fail when items appear out of rank order.

## Acceptance Criteria
- Given two curated items with distinct URLs, Writer validation passes when both items appear correctly.
- Given two curated items sharing the same URL, Writer validation passes when both titles appear with summary text and the shared URL appears in each item section.
- Given a shared URL that appears only once for two items, Writer validation fails for the item missing its source URL.
- Given an item title missing from the message, Writer validation fails.
- Given an item URL missing from the message, Writer validation fails.
- Given items out of rank order, Writer validation fails.