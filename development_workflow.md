# Lightweight Autonomous Development Workflow

This document is the source of truth for the autonomous feature development
workflow. Other project guidance may refer to it, but workflow behavior should
be defined here rather than restated elsewhere.

## Purpose

This workflow automates the Director's existing engineering handoffs without
creating a separate software engineering methodology.

The workflow preserves:

- independent implementation
- independent evaluation
- durable feature history
- clear separation of responsibilities

The Director remains responsible for feature selection and final acceptance.

## Artifact Locations

- `work/` contains Director requests and the Planner Agent's durable execution
  record for each feature.
- `specs/` contains Planner Agent-authored behavioral specifications.
- `evals/` contains Planner Agent-authored evaluation specifications.

The Work File is the durable record for a feature. Historical records may
remain in the repository, but they are not part of the active workflow and are
not updated for new work.

The active workflow records implementation and evaluation results in the Work
File.

## Roles

### Director

The Director defines the desired feature through a Work File.

The Director provides:

- the feature title
- the desired observable behavior
- any required public interfaces
- any explicit non-negotiable requirements
- optional Director intent

The Director does not write specifications, implementation plans, or
evaluations.

The Director accepts, rejects, or requests additional work after reviewing the
completed Work File.

Planner Agent-authored specifications and evaluations may be executed without
separate Director approval unless the Director explicitly requests an approval
checkpoint.

### Planner Agent

The Planner Agent owns engineering coordination.

The Planner Agent is responsible for:

- understanding the requested feature
- reviewing the architecture
- identifying assumptions
- identifying implementation risks
- creating an implementation plan
- writing the behavioral specification
- coordinating implementation
- recording implementation observations
- recording assumptions, limitations, and future work
- writing the evaluation specification
- coordinating independent evaluation
- recording evaluation results
- summarizing the completed work

The Planner Agent never implements code.

The Planner Agent never evaluates its own implementation.

The Planner Agent records implementation and evaluation reports in the Work
File using externally observable behavior and completed capabilities, not
internal implementation details.

### Implementation Agent

The Implementation Agent reads:

- `AGENTS.md`
- `architecture.md`
- the Planner Agent's specification

The Implementation Agent is responsible for:

- implementing the specification
- executing appropriate tests
- reporting implementation observations
- reporting assumptions
- reporting limitations
- reporting future work recommendations

The Implementation Agent does not evaluate correctness against the
specification.

Implementation reports must include:

- spec used
- summary of observable work completed
- tests or checks run
- assumptions made
- limitations or gaps
- future work recommendations, when applicable

Implementation summaries, observations, assumptions, limitations, and future
work must describe externally observable behavior and completed capabilities.
Implementation details may be included only under assumptions, limitations,
future work, or when required to explain a public contract decision.

### Evaluation Agent

The Evaluation Agent runs in fresh context.

The Evaluation Agent reads:

- `AGENTS.md`
- `architecture.md`
- the Planner Agent's specification
- the Planner Agent's evaluation

The Evaluation Agent is responsible for independently determining whether the
implementation satisfies the specification.

The Evaluation Agent may:

- execute tests
- inspect observable behavior
- identify specification violations
- identify implementation gaps

The Evaluation Agent does not modify implementation.

Evaluation reports must include:

- evaluation file used
- PASS/FAIL result for each scenario
- one-sentence product-behavior reason for each scenario result
- overall verdict

Evaluation results must describe observable behavior and must not mention
implementation identifiers or test mechanics, including class names, function
names, method names, file paths, return values, booleans, exception class
names, exact helper inputs, or internal algorithms.

## Project Rules

For code changes, new features, bug fixes, or any change that affects how the
application works, the only source of requirements is the specification file
referenced by the Planner Agent.

Documentation-only changes may be made without a specification when the
Director asks for documentation updates and does not require application
behavior changes.

If a requirement is ambiguous or missing, the Implementation Agent reports the
ambiguity to the Planner Agent for recording in the Work File and stops rather
than guessing.

If implementation details are unspecified, the Implementation Agent chooses the
simplest reasonable implementation that satisfies the specification. This
includes module names, function names, class names, internal data structures,
and helper methods, unless the specification explicitly defines them.

Calls to Gemini, OpenAI, Ollama, and Telegram are not needed while implementing
logic. Real calls happen only during evaluation, in a separate session, when
the evaluation scenario requires genuine search, model, or delivery
confirmation.

Agents must not explore, list, or reference anything outside this repository
directory tree.

## Work File Lifecycle

The Work File starts as a lightweight Director-owned request:

```markdown
# <Feature Title>

## Goal

...

## Director Intent

...
```

The Planner Agent constructs and maintains the remaining sections while
executing the workflow.

The Work File records:

- the original request
- Planner Agent decisions
- specification path
- implementation summary
- implementation observations
- tests or checks run
- assumptions
- limitations
- future work
- evaluation path
- evaluation result
- final summary
- Director acceptance status

The Work File records paths to the specification and evaluation. It does not
duplicate their contents.

Recording implementation or evaluation commits is optional unless the Director
explicitly requests commit tracking for the feature.

## Specification Lifecycle

The Planner Agent writes a behavioral specification in `specs/`.

The specification is the implementation contract. It describes observable
behavior, public interfaces, inputs, outputs, failure handling, acceptance
criteria, constraints, and out-of-scope work.

Specifications must not prescribe implementation details unless those details
are observable public requirements.

If public or operational behavior changes, update the durable product
documentation that describes that behavior.

## Evaluation Lifecycle

The Planner Agent writes an evaluation specification in `evals/`.

The evaluation is derived from the specification rather than the
implementation. It describes observable scenarios and grading instructions.

Evaluation is performed independently by an Evaluation Agent in fresh context.
The Planner Agent records the evaluation result in the Work File.

## Workflow Lifecycle

1. The Director creates a Work File describing the desired feature.
2. The Planner Agent performs architectural review, identifies assumptions and
   risks, and records an implementation plan in the Work File.
3. The Planner Agent writes a behavioral specification in `specs/` and records
   its path in the Work File.
4. The Planner Agent delegates implementation to an Implementation Agent.
5. The Implementation Agent implements the specification, runs appropriate
   tests, and reports observations.
6. The Planner Agent records the implementation summary, observations, tests
   or checks run, assumptions, limitations, and future work in the Work File.
7. The Planner Agent writes an evaluation specification in `evals/` and records
   its path in the Work File.
8. The Planner Agent delegates evaluation to a fresh-context Evaluation Agent.
9. The Evaluation Agent reports scenario results and an overall verdict.
10. The Planner Agent records the evaluation result and final summary in the
    Work File.
11. The Planner Agent stops.
12. The Director reviews the completed Work File and accepts, rejects, or
    requests additional work.

## Planner Agent Stopping Condition

The Planner Agent's responsibility is complete after it records:

- implementation summary
- implementation observations
- tests or checks run
- assumptions
- limitations
- future work
- evaluation result
- final summary

The Planner Agent does not:

- merge branches
- delete branches
- push commits
- accept completed work

Final acceptance remains the Director's responsibility.

## Guiding Principle

If additional workflow complexity cannot be justified by improving the
Director's original engineering process, it should not be added.
