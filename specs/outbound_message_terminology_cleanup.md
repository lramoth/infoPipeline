# Feature: Outbound Message Terminology Cleanup

## Goal
Remove Telegram-specific terminology from the Writer contract and replace it with destination-agnostic terminology.
The Writer should produce an outbound message, not a Telegram message.
This prepares the system for a future Delivery layer while preserving current runtime behavior.

## Background
The current Writer implementation and related artifacts refer to the Writer output as a Telegram message or Telegram-ready message.
Telegram is the current intended delivery destination, but the Writer should not know or care where the message will be delivered.
The Writer generates message content.
Delivery transports message content.

## Scope
Update Writer-related Telegram terminology in:
- writer.py
- Writer prompt files
- Writer prompt file names and configuration paths
- Writer tests
- Writer-related validation messages
- Writer-related documentation
- architecture.md
- AGENTS.md only where Telegram is used to describe generic Writer output

## Requirements

### Writer Responsibility
The Writer must be described as producing an outbound message.
The Writer must not be described as producing a Telegram message.
The Writer must not be described as producing a Telegram-ready message.
The Writer must not be responsible for Telegram delivery behavior.

### Prompt Content
The Writer prompt should describe the task as writing an outbound briefing.
The Writer prompt should not describe the task as writing a Telegram briefing.
The generated message format should remain suitable for the current pipeline.

### Prompt File Naming
Writer prompt file names and configured prompt paths should use destination-agnostic terminology.
The default Writer prompt should not use a Telegram-specific file name.
For example, prompts/writers/telegram_brief.md should be renamed to a destination-agnostic name such as prompts/writers/outbound_brief.md.
Any default path, configuration file, test, or documentation reference that points to the Writer prompt should be updated to match the new destination-agnostic prompt path.

### Validation Language
Writer validation messages should refer to an outbound message.
Examples:
- 'Item title missing from Telegram message' becomes 'Item title missing from outbound message'
- 'Item URL missing from Telegram message' becomes 'Item URL missing from outbound message'
- 'Item is missing summary text in Telegram message' becomes 'Item is missing summary text in outbound message'
- 'Telegram message contains all curator items' becomes 'Outbound message contains all curator items'

### Tests
Writer tests should be updated to use destination-agnostic terminology where they describe Writer behavior.
Test helper names, test prompt content, and assertions should avoid Telegram-specific wording unless the test is explicitly about Telegram delivery.

### Telegram References That Should Remain
Do not remove Telegram references when they describe Telegram as the actual delivery target.
Telegram references may remain for:
- Telegram credentials
- Telegram bot token
- Telegram chat ID
- Telegram delivery behavior
- Future Telegram delivery module behavior
- Architecture notes that explicitly describe Telegram as the current delivery destination

### Runtime Behavior
The pipeline behavior should remain unchanged.
The Writer should still return the same kind of final message string.
No Delivery stage should be added.
No delivery modules should be implemented.
No Telegram API call should be added or removed.

## Non-Goals
- Implementing Delivery
- Adding modular delivery configuration
- Supporting multiple delivery targets
- Changing message content structure
- Changing Planner execution behavior
- Changing external service behavior
- Adding Telegram delivery implementation

## Acceptance Criteria
A reviewer can observe that:
- Writer terminology uses outbound message instead of Telegram message.
- The Writer prompt content is no longer Telegram-specific.
- Writer validation reasons use outbound message terminology.
- Writer tests no longer describe Writer output as a Telegram message.
- Telegram remains referenced only where it means the concrete Telegram delivery destination.
- Existing tests pass after expected terminology updates.
- eval_log.md receives a build log entry describing the terminology cleanup.

## Rationale
The Writer is responsible for message generation.
Delivery is responsible for message transport.
Using outbound message as the Writer output concept keeps message generation independent from the current delivery destination.
