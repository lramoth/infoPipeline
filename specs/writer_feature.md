# Spec: Writer

## Objective
Transform the Curator's ranked and filtered output into an outbound message suitable for daily delivery.

## Background
Researcher stage discovers candidate items.
Curator stage applies judgment and selects the most relevant items.
Writer stage formats those curated results into concise, readable message content intended for delivery.

## Requirements
- The Writer accepts the successful output of the Curator stage as input.
- The Writer provides the Curator's output and a default prompt in 'prompts/writers/outbound_brief.md' to the local model to process.
- The Writer returns a string containing the outbound message.
- The Writer's prompt can also be loaded at runtime
- The Writer's outbound message should contain all the items provided by the Curator ranked by the ascending rank order

## Inputs
- Curator's ouput
- A prompt: (default to location 'prompts/writers/outbound_brief.md')

## Outputs
- A single outbound message string.

## Behavior
1. Receive Curator output.
2. Load the configured Writer prompt file.
3. Provide the prompt and Curator output to the local Writer model.
4. Generate an outbound message.
5. Validate the generated output.
6. Return the message.

## Failure Handling
- Empty model responses shall be treated as an error and reported with a readable message.
- Model execution failures shall be treated as an error and reported with a readable message.
- An empty curated item list shall be treated as a failure.
- An empty or missing prompt file shall be treated as a failure

## Validation Failure
- The generated output is not a string.
- An item in the outbound message is missing a title or url defined by a cooresponding Curator item.
- An item in the outbound message is missing a summary text.
- Items do not appear in the same ascending rank order provided by the Curator.

## Validation Success
- An outbound message is created.
- Each item in the outbound message contains a title and url defined by a cooresponding Curator item.
- Each item in the outbound message contains a summary text.
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
