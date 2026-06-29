# Specification and Evaluation Templates

## Goal

Standardize the project's specification and evaluation templates based on conventions that have emerged during autonomous feature development.

Before beginning, read:

- `development_workflow.md`
- `governance.md`
- `architecture.md`

Use those documents to guide all workflow decisions while executing this Work File.

---

## Initial Architectural Review

- The feature concerns project workflow artifacts rather than runtime pipeline
  behavior.
- The existing specification and evaluation templates should be standardized to
  reinforce black-box behavioral requirements, observable evaluation scenarios,
  and eval-log conventions from `governance.md`.
- The change should remain limited to reusable template artifacts and supporting
  workflow records. It should not alter the command-line pipeline, provider
  integrations, prompts, configuration, or runtime behavior described in
  `architecture.md`.

## Tasks

- Task 1: Standardize specification and evaluation templates
  - Goal: Update the reusable templates so future specs and evals consistently
    describe observable behavior, avoid implementation requirements, and guide
    agents toward the project's build and evaluation logging conventions.
  - Spec: `specs/standardize_spec_eval_templates_feature.md`
  - Summary: Standardized the reusable specification and evaluation templates
    so future artifact authors are guided toward externally observable
    requirements, explicit success and failure behavior, controlled evaluation
    environments, and distinct build-session versus evaluation-session logging.
  - Implementation Observations:
    - Runtime pipeline behavior was not changed.
    - `git diff --check` passed during implementation.
    - No live provider or delivery calls were run because the task updated
      documentation templates only.
    - Recommendation: Create and run an evaluation artifact for the
      standardized templates.
      - Planner Agent Decision: Handle through the required evaluation phase
        for this task rather than creating a separate implementation task.
  - Recommended Future Work Files: None.

## Recommended Future Work Files

## Governance

## Final Summary
