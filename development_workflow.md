# Autonomous Development Workflow

## Purpose

This workflow is designed for autonomous feature development with strong
engineering discipline, independent verification, and low artifact drag.

The workflow exists to preserve confidence that accepted behavior matches the
Director's intent. It should not maximize documentation volume. Each artifact
must either help the next agent reason correctly, help an evaluator verify
behavior independently, or preserve durable project memory.

The central durable artifact is the **Work File**. It records decisions,
behavior contracts, status, evidence, and unresolved questions. Standalone
specifications and evaluations are optional tools used when risk warrants them.

## Core Principles

- The Planner is the long-running coordinator and architectural owner.
- Implementation and independent evaluation are performed by fresh contexts
  whenever practical.
- The Work File is the canonical memory for active work.
- Observable behavior is the unit of planning, implementation, and evaluation.
- Goal Reconciliation is the main acceptance gate before independent
  evaluation.
- Holdout evaluation checks completed behavior independently; it does not
  design the implementation.
- Governance is a small architectural and process confidence gate.
- Documentation is written once in the place where it will remain useful.
- A smaller workflow is preferred when it preserves confidence.

## Roles

### Director

The Director defines desired outcomes, approves final behavior, and decides
whether completed work may merge.

Director Intent may include public interfaces, compatibility requirements,
configuration contracts, operational constraints, or user-visible workflows.
Director Intent should not prescribe internal algorithms, class names, helper
functions, or file layouts unless those details are themselves public
requirements.

### Planner

The Planner owns scope, sequencing, architectural reasoning, and durable memory.
The Planner does not edit implementation code.

The Planner:

- reads the active Work File, this workflow, governance rules, and architecture
  contracts;
- performs Discovery before planning implementation;
- decides the workflow lane;
- records the behavior contract;
- delegates implementation to fresh contexts;
- reconciles completed work against the Goal and Director Intent;
- decides whether observations require another planning iteration;
- requests independent evaluation when warranted;
- records accepted future work;
- initiates Governance Review;
- prepares the Director-ready final summary.

### Implementation Agent

The Implementation Agent receives the Work File and the current task. It
implements the agreed behavior, adds focused tests appropriate to the risk, and
reports observations that may affect scope.

It may propose implementation choices, but it does not redefine the Goal,
Director Intent, or public behavior contract.

### Evaluation Agent

The Evaluation Agent receives the Work File, the behavior contract, and any
evaluation instructions. It independently judges completed behavior from the
outside whenever practical.

It reports PASS, PASS WITH WARNINGS, or FAIL. It may identify behavioral gaps,
side effects, or evidence limitations. The Planner decides whether those
findings create current-scope work.

### Governance Reviewer

The Governance Reviewer performs a compact architectural and process review. It
does not repeat the full evaluation. It asks whether the completed change fits
the project architecture, preserves discipline, and gives the Director enough
evidence to accept or reject the work.

## Work File

Every feature or meaningful change has one Work File under `work/`. The Work
File is the active memory spine. It should be concise, append-friendly, and
decision-oriented.

Recommended structure:

```markdown
# Feature Name

## Goal

## Director Intent

## Discovery Brief

## Workflow Lane

## Behavior Contract

## Task Plan

## Iterations

## Evidence

## Open Questions

## Future Work

## Governance

## Final Summary
```

The Work File should not duplicate information that is already canonical in
`architecture.md`, checked-in tests, build logs, or evaluation artifacts. It may
link to those artifacts and record the decision made from them.

## Workflow Lanes

The Planner chooses the lightest lane that preserves correctness.

### Lightweight Lane

Use for documentation-only work, tiny internal refactors, test maintenance, or
bug fixes where the desired behavior is already defined by an existing
contract.

Required:

- Discovery Brief
- Behavior Contract or explicit reference to an existing contract
- implementation by a fresh agent when practical
- focused tests or static checks when applicable
- Goal Reconciliation
- Work File final summary

Standalone specification, standalone evaluation, and Governance Review are
optional unless the Planner identifies risk.

### Standard Lane

Use for most feature work that changes observable behavior in a bounded area.

Required:

- Discovery Brief
- Behavior Contract in the Work File
- implementation by a fresh agent
- focused automated tests
- Goal Reconciliation
- independent evaluation or explicit Planner rationale for skipping it
- compact Governance Review
- final Work File summary

Standalone specifications and evaluation files are optional. Use them when the
contract or evaluation matrix is too large to keep readable in the Work File.

### High-Assurance Lane

Use when work changes public contracts, provider behavior, configuration
format, ledger/output shape, delivery behavior, security/privacy expectations,
cross-stage boundaries, or anything expensive to repair after release.

Required:

- Discovery Brief
- explicit Behavior Contract
- standalone specification when the contract is large or reusable
- implementation by a fresh agent
- automated tests covering stated success and failure behavior
- Goal Reconciliation before evaluation
- independent holdout evaluation
- Governance Review
- durable documentation updates for public behavior
- final Work File summary

## Discovery

Discovery happens before implementation planning. Its purpose is to turn a
Goal into an actionable, testable behavior contract while exposing ambiguity
early.

The Discovery Brief must answer:

- What existing behavior is relevant?
- What public or operational behavior is intended to change?
- What must remain unchanged?
- Which components, configuration contracts, command-line surfaces, prompts,
  templates, providers, ledgers, diagnostics, or delivery paths are affected?
- What failure behavior is implied?
- What backward-compatibility expectations apply?
- What side effects are allowed or forbidden?
- What evidence would prove the Goal is satisfied?
- What is ambiguous enough to require Director input?

If Discovery reveals missing or conflicting requirements, the Planner records
the question and stops instead of guessing.

## Behavior Contract

The Behavior Contract is the canonical statement of what the current work must
deliver. For many changes it lives directly in the Work File.

It should include:

- public inputs or triggers;
- successful observable behavior;
- failure behavior;
- side effects;
- unchanged behavior;
- compatibility requirements;
- validation or security expectations;
- required evidence.

The contract describes behavior, not implementation details. Internal module
names, helper functions, data structures, and algorithms belong in
implementation notes only when they are part of a public interface.

## Standalone Specifications

A standalone specification is no longer mandatory for every feature.

Create one when:

- the behavior contract is large enough to obscure the Work File;
- the feature changes public configuration, CLI, provider, delivery, ledger,
  diagnostic, or cross-stage contracts;
- multiple implementation iterations are likely;
- the specification will be reused by future work;
- independent evaluation needs a stable long-form reference.

Do not create one merely to satisfy ceremony. If the Behavior Contract in the
Work File is clear, complete, and durable enough, it is the specification.

## Task Planning

The Planner decomposes work into tasks only after Discovery and the initial
Behavior Contract exist.

Good tasks produce a complete observable increment. Avoid tasks that only
mirror file boundaries unless the file boundary is also a behavior boundary.

Each task should record:

- scope;
- lane;
- required evidence;
- whether independent evaluation is required;
- known non-goals;
- dependencies on prior tasks.

## Implementation

The Implementation Agent receives:

- this workflow;
- `governance.md`;
- `architecture.md`;
- the active Work File;
- the current task and Behavior Contract.

The Implementation Agent:

1. confirms the relevant contract and open questions;
2. implements the smallest change that satisfies the contract;
3. adds tests proportional to risk and blast radius;
4. avoids live external calls unless the Work File requires them;
5. updates durable product documentation when public behavior changes;
6. appends the required build log entry for build sessions;
7. commits its changes on the active feature branch when instructed by the
   repository workflow;
8. reports implementation observations.

Implementation observations should distinguish:

- evidence that the Goal may not yet be satisfied;
- risks or gaps in the public contract;
- implementation tradeoffs;
- optional improvements;
- future work beyond the current Goal.

## Goal Reconciliation

Goal Reconciliation is the main Planner acceptance gate.

It occurs:

- after Discovery, before implementation starts;
- after each implementation task;
- after evaluation findings when needed;
- before Governance Review.

Goal Reconciliation asks whether completed behavior, together with prior
completed work, satisfies the Goal and Director Intent when read through the
Behavior Contract, architecture, governance rules, and implementation
observations.

The Planner must create another planning iteration when an observation shows:

- the implemented behavior does not satisfy the Goal;
- an implied public behavior is missing;
- a failure mode is undefined;
- a public contract accepts undocumented input;
- a stage boundary or responsibility has shifted accidentally;
- compatibility was broken without being part of the Goal;
- independent verification cannot observe the promised behavior;
- public documentation would be stale after the change.

The Planner records a future work item rather than current-scope work when the
observation improves maintainability, generality, performance, or operator
comfort without being necessary to satisfy the current Goal.

## Evaluation

Evaluation is independent verification of completed behavior. It should add
confidence that implementation tests alone cannot provide.

Evaluation is required for High-Assurance work. It is normally expected for
Standard work. It is optional for Lightweight work when the Planner records why
tests and reconciliation are enough.

Evaluation should:

- read the Behavior Contract, not implementation intent;
- inspect behavior from command-line, configuration, artifact, provider, or
  downstream-user perspectives where practical;
- include success and failure behavior;
- check forbidden side effects;
- avoid live external calls unless required;
- report only observable results as the basis for PASS or FAIL.

Evaluation should not prescribe implementation design. If it finds a gap, it
reports the observed mismatch. The Planner decides whether the mismatch becomes
current-scope work, a warning, or future work.

Standalone evaluation files are optional. Create one when the evaluation
matrix is large, reusable, or high-risk. Otherwise record the evaluation plan
and result in the Work File.

## Governance Review

Governance Review is a compact final check, not a second evaluation.

It asks:

- Does the completed behavior fit the architecture?
- Are responsibilities still separated correctly?
- Are public contracts documented and bounded?
- Are configuration and validation consistent?
- Are side effects intentional and observable?
- Did independent verification happen at the level required by the lane?
- Are current-scope gaps separated from future work?
- Does the Director have enough evidence to accept or reject the change?

Governance outcomes:

- PASS: ready for Director acceptance.
- PASS WITH WARNINGS: architecturally acceptable, but the Planner must decide
  whether warnings require current-scope work.
- FAIL: not ready; Planner creates or revises tasks.

## Logs

`eval_log.md` remains append-only.

Build sessions append build-log entries only when application behavior,
durable product documentation, configuration contracts, tests, or other
project artifacts are changed.

Evaluation sessions append evaluation entries only when independent evaluation
is performed.

Build-log entries describe completed capabilities and assumptions. Evaluation
entries describe observable product behavior and verdicts. Neither should
duplicate the full Work File.

## Durable Documentation

Update durable product documentation when accepted behavior changes:

- configuration contracts;
- command-line behavior;
- provider responsibilities;
- stage contracts;
- ledger or diagnostic behavior;
- delivery behavior;
- external dependencies.

Do not update durable product documentation for temporary implementation
strategy, speculative future work, or internal details that are not part of
the public or operational contract.

## Completion

A feature is ready for Director acceptance when:

- the Work File has a clear Goal, Discovery Brief, Behavior Contract, evidence,
  and final status;
- implementation satisfies the Behavior Contract;
- Goal Reconciliation finds no missing current-scope behavior;
- required evaluation has passed or been deliberately waived under the chosen
  lane;
- Governance Review passes when required;
- durable product documentation reflects changed public behavior;
- future work is separated from current-scope obligations.

Director acceptance remains required before merge.

## Exploration

When multiple architectural approaches are plausible and the cost of choosing
wrong is high, the Director may request exploratory branches.

Exploration branches should still use Discovery, Behavior Contracts, and
evidence. They may use lighter evaluation until one approach is selected for
production-quality implementation.
