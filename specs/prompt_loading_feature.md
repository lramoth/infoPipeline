# Spec: Prompt Loading

## Objective
Researcher, Curator and Writer prompt content is stored in markdown files and loaded at runtime, allowing prompt changes without modifying Python source code. The Writer prompt directory and placeholder file are created for future use.

## Background
- The Curator uses the contents of its intialized markdown file to generate its Gemini request.
- The Researcher uses the contents of its initialized markdown file when it generates its Gemini search.
- The Writer uses the contents of its initialized markdown file when it generates the outbound brief

## Requirements
- The following folder 'prompts/curators/' contain the curator prompt as a markdown file called 'polegroup_techno.md'
- The following folder 'prompts/researchers/' contain the researcher prompt as a markdown file called 'techno_news.md'
- The following folder 'prompts/writers/' contains a blank prompt for now called 'outbound_brief.md'
- allow the corresponding markdown file to be loaded at runtime

## Behavior
- The stage (Curator or Researcher) can be configured to use a specific markdown prompt file.

## Failure Handling
- When a required prompt file cannot be loaded, the stage reports failure with a clear reason.
- When a required prompt file cannot be read, the stage reports failure with a clear reason.

## Out of Scope
- Since the Writer doesn't exist yet only create its directory structure and a blank markdown file
