# Spec: Writer

## Objective
Transform the Curator’s ranked and filtered output into a Telegram-ready message suitable for daily delivery.

## Background
Researcher stage discovers candidate items.
Curator stage applies judgment and selects the most relevant items.
Writer stage formats those curated results into a concise, readable message intended for Telegram delivery.

## Requirements
- The Writer accepts the successful output of the Curator stage as input.
- The Writer provides the Curator's output and a default prompt in 'prompts/writers/telegram_brief.md' to the local model to process.
- The Writer returns a string containing the Telegram-ready message.
- The Writer's prompt can also be loaded at runtime
- The Writer's Telegram-ready message should contain all the items provided by the Curator ranked by the ascending rank order

## Inputs
- Curator's ouput
- A prompt: (default to location 'prompts/writers/telegram_brief.md')

## Outputs
- A single Telegram-ready message string.

## Behavior
1. Receive Curator output.
2. Load the configured Writer prompt file.
3. Provide the prompt and Curator output to the local Writer model.
4. Generate a Telegram-ready message.
5. Validate the generated output.
6. Return the message.

## Failure Handling
- Empty model responses shall be treated as an error and reported with a readable message.
- Model execution failures shall be treated as an error and reported with a readable message.
- An empty curated item list shall be treated as a failure.
- An empty or missing prompt file shall be treated as a failure

## Validation Failure
- The generated output is not a string.
- An item in the telegram message is missing a title or url defined by a cooresponding Curator item.
- An item in the Telegram message is missing a summary text.
- Items do not appear in the same ascending rank order provided by the Curator.

## Validation Success
- A Telegram-ready message is created.
- Each item in the telegram message contains a title and url defined by a cooresponding Curator item.
- Each item in the Telegram message contains a summary text.
- Items appear in the same ascending rank order provided by the Curator.

## Constraints
- Writer shall not perform ranking or filtering.
- Writer shall not perform additional research.
- Writer shall not make Gemini API calls.
- Writer shall use the configured local Ollama model.
- Writer shall treat Curator output as authoritative.

## Out of Scope
- Researching new information.
- Ranking or scoring items.
- Deduplication.
- Telegram delivery.
- Planner orchestration.
- Prompt authoring.
