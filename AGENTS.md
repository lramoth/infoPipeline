# Agent Instructions — infoPipeline

## Stack & conventions
- Prefer the Python standard library when practical. Add dependencies only when
  they materially simplify implementation.
- Researcher stage uses the configured model provider for search. Supported
  providers: Gemini and OpenAI.
- Curator stage takes search results and applies a prompt using the configured
  model provider. Supported providers: Gemini and OpenAI.
- Writer stage uses configured provider logic, currently supporting only local
  Ollama (model: gemma4:e4b).
- Delivery stage posts to Telegram.
- Designed for command-line invocation.

## Dependencies
External dependencies may be added when they provide significant value and
avoid reimplementing established functionality.
When adding a dependency:
- add it to requirements.txt
- report the reason for the Work File assumptions
- do not introduce unnecessary dependencies
Well-established third-party libraries may be added when implementing the
feature correctly would otherwise require reimplementing substantial
functionality.

## Workflow
- Follow `development_workflow.md` for feature workflow execution, role
  responsibilities, artifact lifecycles, reporting requirements, stopping
  conditions, and acceptance.
- Do not explore, list, or reference anything outside this directory tree.

## Definition of done
- Follow the completion and stopping conditions in `development_workflow.md`.

## Governance
Read `governance.md` for project principles before drafting specifications,
evaluations, or Work File entries.
