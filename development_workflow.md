# development_workflow.md

# Autonomous Feature Development Workflow

## Purpose

This document describes the standard workflow used to implement new
features within this project.

The workflow is intentionally designed around long-running autonomous
development while preserving architectural discipline through
specifications, evaluations, and governance reviews.

The workflow is centered around a **Planner Agent** and a **Work File**.

The Planner orchestrates work.

The Work File records decisions rather than conversation. Information that can be derived from the Work File should not be duplicated elsewhere.

------------------------------------------------------------------------

# Principles

-   The Planner is the only long-running agent.
-   All implementation work is performed by short-lived subagents.
-   Every subagent begins with a fresh context.
-   The Work File is the single source of truth for feature progress.
-   Specifications describe observable behavior.
-   Evaluations verify specifications.
-   Governance determines whether the completed feature is
    architecturally acceptable.

------------------------------------------------------------------------

# Feature Lifecycle

## 1. Director Creates Feature

The Director:

-   creates a feature branch from `main`
-   creates a new Work File in `work/`

Example:

``` text
work/telegram_delivery.md
```

Initial structure:

``` markdown
# Telegram Delivery

## Goal

Send the Writer output to Telegram after a successful Planner run.
```

------------------------------------------------------------------------

## 2. Planner Initialization

The Planner reads:

- the Work File
- development_workflow.md
- governance.md
- architecture.md

The Planner performs an initial architectural review.

The Planner initializes the Work File using the project's standard structure.

The standard top-level sections are:

- Goal
- Initial Architectural Review
- Tasks
- Recommended Future Work Files
- Governance
- Final Summary

The Planner records the results of the architectural review.

The Planner decomposes the feature goal into a series of manageable tasks.

The Planner records these tasks in the Work File.

The task list may evolve during development.

The Planner may:

- create new tasks
- reorder tasks
- refine tasks
- remove obsolete tasks

as new implementation observations, evaluation results, or governance findings are produced.

The Planner may add detail within the standard Work File sections as needed.

The Planner should not create additional top-level sections unless the workflow is updated.

Information that can be derived from existing Work File content should not be duplicated.

------------------------------------------------------------------------

# Planner Responsibilities

The Planner:

- owns the Work File
- determines the next unfinished task
- spawns subagents
- collects artifacts
- records results
- maintains the Work File
- reviews implementation recommendations
- creates new tasks
- records recommended future Work Files
- initiates Governance Review

The Planner never edits implementation code.

------------------------------------------------------------------------

# Subagent Workflow

For each task, the Planner spawns a fresh implementation subagent.

The implementation subagent receives:

-   development_workflow.md
-   governance.md
-   architecture.md
-   the current Work File
-   the current task description

The implementation subagent:

1. creates a behavioral specification
2. implements the specification
3. records an implementation summary
4. records implementation observations
5. recommends additional tasks required to complete the feature
6. recommends future Work Files for work outside the current feature

The implementation subagent returns:

- specification filename
- implementation summary
- implementation observations
- recommended new tasks
- recommended future Work Files

The implementation subagent then terminates.

The Planner records the returned information in the Work File.

------------------------------------------------------------------------

# Evaluation

After a task implementation is complete, the Planner spawns a fresh evaluation-authoring subagent.

The evaluation-authoring subagent receives:

- development_workflow.md
- governance.md
- architecture.md
- the current Work File
- the specification

The evaluation-authoring subagent:

1. creates an evaluation for the completed implementation
2. returns the evaluation filename to the Planner

The evaluation-authoring subagent then terminates.

The Planner then spawns a completely fresh Evaluation Agent.

The Evaluation Agent receives:

- development_workflow.md
- governance.md
- architecture.md
- the current Work File
- the specification
- the evaluation

The Evaluation Agent performs the evaluation.

Possible results:

- PASS
- PASS WITH WARNINGS
- FAIL

The Evaluation Agent returns:

- evaluation result
- supporting observations

The Evaluation Agent then terminates.

The Planner records the evaluation results and supporting observations in the Work File.

If the evaluation returns PASS WITH WARNINGS:

- The Planner reviews the warnings.
- If the Planner determines that additional current-scope work is required, it creates one or more new tasks.
- Otherwise, the task is considered complete.

------------------------------------------------------------------------

# Planner Loop

For each task:

1. Spawn a fresh implementation subagent.
2. Record the implementation results.
3. Spawn a fresh evaluation subagent.
4. Record the evaluation results.

If the evaluation fails:

- The Planner records the evaluation result in the Work File.
- The Planner creates a new iteration for the current task.
- The Planner spawns a fresh implementation subagent for the new iteration.
- The task loop repeats.

If implementation observations identify additional required work:

- Review each recommendation.
- Create a new task for each accepted recommendation.

If implementation observations identify work outside the scope of the current feature:

- Review each recommendation.
- Record an accepted recommendation as a future Work File.

A task is complete only when:

- its latest iteration passes evaluation, and
- all tasks created from its implementation observations are complete.

When a task is complete:

- Continue to the next incomplete task.

------------------------------------------------------------------------

# Governance Review

When every task has completed successfully:

The Planner starts a fresh Governance Review Agent.

The Governance Review Agent receives:

- development_workflow.md
- governance.md
- architecture.md
- the current Work File
- all completed specifications
- all completed evaluations

The Governance Review Agent evaluates the completed feature against:

- governance.md
- architecture.md

Possible outcomes:

- PASS
- PASS WITH WARNINGS
- FAIL

The Governance Review Agent returns:

- governance result
- governance findings

The Governance Review Agent then terminates.

The Planner records the governance results and findings in the Work File.

If Governance Review returns PASS:

- The feature is ready for Director acceptance.

If Governance Review returns PASS WITH WARNINGS:

- The Planner reviews the governance findings.
- If the Planner determines that additional current-scope work is required, it creates one or more new tasks.
- Otherwise, the feature is ready for Director acceptance.

If Governance Review returns FAIL:

- The Planner creates one or more new tasks to address the governance findings.
- The workflow resumes from the next incomplete task.

------------------------------------------------------------------------

# End State

The workflow completes when:

- every task has passed evaluation
- Governance Review passes
- the Director accepts the completed feature
- the Planner records a final implementation summary
- no additional work remains

The completed Work File becomes the permanent history of how the feature evolved.

------------------------------------------------------------------------

## Work File Example with example logging flow

```markdown
# Telegram Delivery

## Goal

Send the Writer output to Telegram after a successful Planner run.

## Tasks

- Task 1: Create Delivery abstraction
    - Spec: `specs/delivery_abstraction.md`
    - Summary: Created generic Delivery abstraction.
    - Eval: `evals/delivery_abstraction.eval.md`
    - Result: PASS

- Task 2: Implement Telegram module
    - Iteration 1
        - Spec: `specs/telegram_delivery.md`
        - Summary: Implemented Telegram delivery.
        - Eval: `evals/telegram_delivery.eval.md`
        - Result: FAIL
        - Reason: Telegram credentials were hardcoded.
    - Iteration 2
        - Spec: `specs/telegram_configuration.md`
        - Summary: Moved Telegram credentials into config.
        - Eval: `evals/telegram_configuration.eval.md`
        - Result: PASS
    - Implementation Observations
        - Retry policy should be configurable.
            - Planner Decision: Create Task 5.
        - Multiple delivery destinations would be valuable.
            - Planner Decision: Recommend Future Work File.
            - Suggested Work File: `work/multi_destination_delivery.md`

- Task 3: Add configuration support
    - Spec: `specs/configuration_support.md`
    - Summary: Added delivery config loading.
    - Eval: `evals/configuration_support.eval.md`
    - Result: PASS

- Task 4: Integrate Planner with Delivery
    - Spec: `specs/planner_delivery_integration.md`
    - Summary: Planner sends Writer output through configured delivery module.
    - Eval: `evals/planner_delivery_integration.eval.md`
    - Result: PASS

- Task 5: Make retry policy configurable
    - Origin: Task 2 Implementation Observation
    - Reason: Retry policy was identified as a configurable concern during implementation.
    - Spec: `specs/retry_configuration.md`
    - Summary: Added configurable retry count.
    - Eval: `evals/retry_configuration.eval.md`
    - Result: PASS

## Governance

- Result: PASS
- Notes: Modular, configurable, observable, and extensible.

## Final Summary

- Outcome: Complete
- Director Action: Review branch and merge if accepted.
```

------------------------------------------------------------------------

# Exploration

When requirements are ambiguous or multiple architectural approaches appear viable, the Director may create multiple feature branches from the same starting point. Each branch follows the standard development workflow independently. The Director evaluates the completed branches and selects one for merging. This exploration strategy is optional and is intended to improve solution quality rather than replace the normal workflow.
