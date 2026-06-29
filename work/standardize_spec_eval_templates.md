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
  - Eval: `evals/standardize_spec_eval_templates_feature.eval.md`
  - Result: PASS
  - Evaluation Observations:
    - The specification template guides future authors toward observable
      artifact behavior and away from internal mechanisms unless those details
      are public requirements.
    - The evaluation template guides future evaluators toward referenced-spec
      grading, success and failure scenarios, controlled local evaluation, and
      evaluation-log entries written in product or artifact behavior language.
    - Runtime pipeline behavior, provider behavior, prompt content, runtime
      configuration, and delivery behavior remain unchanged.

## Recommended Future Work Files

## Governance

- Result: PASS
- Findings:
  - No blocking findings.
  - The feature is well-scoped to documentation and workflow templates.
  - The standardized templates align with `governance.md` by emphasizing
    observable behavior, avoiding implementation prescriptions, separating
    build-session and evaluation-session logging, requiring success and failure
    evaluation scenarios, and discouraging external side effects unless
    explicitly required.
  - The feature fits `architecture.md` because it does not alter command-line
    pipeline behavior, stage responsibilities, provider configuration, ledger
    behavior, or delivery flow.

## Final Summary

- Outcome: Complete pending Director acceptance.
- Summary: The reusable specification and evaluation templates now guide future
  artifact authors toward black-box observable behavior, explicit success and
  failure expectations, controlled local evaluation by default, and the
  project's required build-log and evaluation-log conventions.
- Director Action: Review branch and merge if accepted.
