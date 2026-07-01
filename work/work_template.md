# <Feature Title>

## Goal

Describe the desired end result in product or operational terms.

Before beginning, read:

- `development_workflow.md`
- `governance.md`
- `architecture.md`

Use those documents to guide all workflow decisions while executing this Work
File.

---

## Director Intent

Optional. Include only when the Director needs to preserve a specific public
interface, compatibility promise, operational constraint, or user-visible
workflow beyond the Goal.

Examples:

- configuration contract;
- command-line interface;
- output or ledger contract;
- delivery behavior;
- compatibility requirement;
- external side-effect boundary;
- evaluation requirement.

Do not prescribe implementation details such as class names, function names,
algorithms, internal data structures, helper modules, or file organization
unless those details are themselves public requirements.

---

## Discovery Brief

Planner completes this section before implementation planning. If any answer
is unknowable from local context and materially affects the behavior contract,
record it under Open Questions and stop for Director input.

### Current Behavior

- What existing behavior, contracts, or project documents are relevant?
- What is the baseline behavior before this work?

### Intended Change

- What public or operational behavior should change?
- What user, operator, configuration author, downstream stage, or external
  system observes the change?

### Unchanged Behavior

- What behavior must remain compatible?
- Which stages, configuration surfaces, prompts, templates, providers, ledgers,
  diagnostics, or delivery paths should not change?

### Affected Surfaces

Record only affected surfaces.

- CLI:
- configuration:
- stage contracts:
- provider requests:
- prompt/template paths:
- ledger:
- diagnostics:
- delivery:
- external dependencies:
- documentation:

### Failure And Side Effects

- What failure cases are implied by the Goal?
- What side effects are allowed?
- What side effects are forbidden?
- Are live provider, network, model, or delivery calls allowed during
  implementation or evaluation?
- Are there secrets or sensitive values that must not appear in output,
  diagnostics, logs, or errors?

### Evidence Needed

- What would prove the Goal is satisfied?
- What automated tests, controlled runs, command outputs, or holdout evaluation
  checks are needed?
- What evidence would be enough to waive independent evaluation, if this is a
  low-risk change?

---

## Workflow Lane

Planner selects the lightest lane that preserves correctness.

- Lane: `<Lightweight | Standard | High-Assurance>`
- Rationale:
- Standalone specification required? `<yes | no>`
- Independent evaluation required? `<yes | no>`
- Governance Review required? `<yes | no>`

Use:

- **Lightweight** for documentation-only work, tiny internal refactors, test
  maintenance, or bug fixes governed by an existing contract.
- **Standard** for bounded observable behavior changes.
- **High-Assurance** for changes to public contracts, configuration, providers,
  delivery, ledger behavior, security/privacy expectations, cross-stage
  boundaries, or high-blast-radius behavior.

---

## Behavior Contract

This section is the canonical requirement unless a standalone specification is
created and referenced here.

### Contract Source

- Embedded in this Work File, or:
- Standalone spec: `<specs/...>`

### Inputs Or Triggers

- What command, configuration, file, profile, provider response, scheduled run,
  or user/operator action triggers the behavior?

### Success Behavior

- What observable behavior must occur when valid inputs are supplied?
- What outputs, artifacts, side effects, or stage transitions are expected?

### Failure Behavior

- What invalid inputs, provider failures, validation failures, or operational
  errors must be handled?
- What must be reported to the caller, ledger, diagnostics, or delivery
  outcome?
- What later behavior must not occur after failure?

### Compatibility And Non-Goals

- What existing behavior must remain unchanged?
- What is explicitly out of scope for this work?

### Acceptance Evidence

- What checks must pass before Goal Reconciliation can accept the work?
- What must an independent evaluator be able to observe?

---

## Task Plan

Tasks should produce complete observable increments. Avoid task boundaries that
only mirror file boundaries unless the file boundary is also a behavior
boundary.

- Task 1: `<title>`
  - Status: `<pending | in progress | complete>`
  - Scope:
  - Lane:
  - Required evidence:
  - Evaluation required? `<yes | no>`
  - Dependencies:

---

## Iterations

Record completed work, observations, and Planner decisions. Keep this section
decision-oriented; do not duplicate full specs, test output, or evaluation
logs.

### Task `<number>` — `<title>`

- Iteration:
- Implementation summary:
- Tests or checks:
- Build log entry: `<eval_log.md entry date or not required>`
- Implementation observations:
  - Observation:
  - Planner decision: `<current scope | future work | accepted | rejected>`
- Commit(s):

---

## Goal Reconciliation

Planner completes this section after Discovery, after each implementation
iteration, after evaluation findings when needed, and before Governance Review.

### Reconciliation `<date or iteration>`

- Inputs considered:
  - Goal:
  - Director Intent:
  - Discovery Brief:
  - Behavior Contract:
  - implementation observations:
  - evidence:
- Result: `<satisfied | needs another planning iteration | blocked on Director input>`
- Reason:
- Current-scope follow-up tasks:
- Future work accepted:
- Questions for Director:

---

## Evidence

Record concise evidence pointers. Do not paste long command output unless the
exact output is itself the artifact being reviewed.

- Automated checks:
- Controlled provider or fixture checks:
- Command-line checks:
- Documentation checks:
- Independent evaluation:
  - Required? `<yes | no>`
  - Evaluation artifact, if any: `<evals/...>`
  - Result:
  - Notes:

---

## Open Questions

Record ambiguities that materially affect the behavior contract. Stop for
Director input when guessing would create public behavior, broaden scope, or
weaken verification.

- Question:
  - Why it matters:
  - Related contract or architecture reference:
  - Status:

---

## Future Work

Record useful follow-on work that is not necessary to satisfy the current Goal.
Do not use this section for missing current-scope behavior.

- Future work:
  - Origin:
  - Reason it is not current scope:
  - Suggested Work File:

---

## Governance

Complete when required by the selected lane or requested by the Director.

- Required? `<yes | no>`
- Result: `<PASS | PASS WITH WARNINGS | FAIL>`
- Findings:
- Warnings requiring Planner decision:
  - Warning:
  - Planner decision:
- Current-scope tasks created from Governance:

---

## Final Summary

Complete when the feature is ready for Director acceptance or intentionally
closed.

- Outcome: `<ready for Director acceptance | closed | blocked>`
- Completed behavior:
- Evidence:
- Durable documentation updated:
- Known gaps or suspected bugs:
- Future work:
- Director action:
