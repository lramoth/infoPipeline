# Governance Notes
This project is intentionally developed through:
- behavioral specifications
- implementation by coding agents
- evaluation against specifications

## Principles
- Specs describe observable behavior, not implementation.
- Evals test both success and failure conditions.
- Code is treated as a black box whenever possible.
- Runtime observations should inform future work.
- Durable project documents should reflect implemented application behavior.
- Build logs describe capabilities, not implementation details.
- Dependencies are allowed when they avoid reimplementing established functionality.
- Human review and acceptance are required for all features.

## Governance Model
The human acts as Director rather than primary implementer.
Agents may propose specifications, implementations, evaluations, and improvements. These proposals are advisory until reviewed and accepted by the Director.
The Director is responsible for:
- defining the problem or desired outcome
- establishing project governance
- selecting between competing solutions
- accepting or rejecting completed work
Agent-generated specifications and evaluations are allowed and encouraged.

During autonomous feature development, the Planner agent uses these artifacts to coordinate implementation, evaluation, and governance.

The Planner agent owns workflow scope decisions during autonomous feature
development. Agent-authored specifications, evaluations, and implementation
observations are advisory artifacts; they do not narrow the Director's intent
or the Work File goal unless the Planner records that scope decision in the
Work File.

The Director accepts or rejects the completed feature. Specifications, evaluations, and governance findings serve as supporting evidence for that decision.

### Director Intent

The Director may specify intended aspects of the externally observable behavior or public interface for a feature.

Examples include configuration contracts, command-line interfaces,
compatibility requirements, public artifacts, and user-facing workflows.

Director Intent guides architectural direction but must not prescribe
implementation details.

The Planner agent retains responsibility for determining how Director Intent is
realized within the project's architectural and governance constraints.

If the Planner agent determines that Director Intent conflicts with governance
principles or the existing architecture, it should surface the conflict for
Director review rather than silently replacing the intended behavior with an
alternative design.

### Specification Boundary
Specifications describe observable behavior.
Specifications must not prescribe:
- file names
- class names
- function names
- data structures
- implementation algorithms
- library choices
unless those details are themselves observable requirements.
Implementation decisions belong to design discussions, code reviews,
or implementation plans, not behavioral specifications.

## Separation of Responsibilities
Whenever practical, implementation, evaluation, and governance review should be performed by different actors.
During autonomous feature development, specification authoring and implementation for an individual task may be performed by the same implementation subagent.
Separation of responsibilities reduces self-validation and increases
confidence in accepted behavior.

### Agent Expectations
Before beginning work, agents should review this document.
Agents should ensure that their work remains consistent with these
governance principles throughout implementation.
If a proposed specification, implementation, evaluation, or architectural
change conflicts with these principles, the conflict should be surfaced
before continuing.

## Architectural Principles
When proposing or implementing changes, agents should consider:
- Modularity
    Can the capability be added, removed, or replaced without affecting unrelated components?
- Configurability
    Should important runtime behavior be configurable rather than hardcoded?
- Scalability
    Does this design make the next similar implementation easier?
- Complexity Control
    Does this reduce overall system complexity rather than increase it?
- Separation of Responsibilities
    Does each component own a single, well-defined responsibility?
- Observable Behavior
    Can the resulting behavior be evaluated without knowledge of the implementation?
- Project Fit
    Does the solution align with the existing project architecture and direction?

## Architectural Evolution

Implementation may reveal architectural improvements that were not
anticipated when the feature was proposed.

Agents are encouraged to surface these improvements.

The Planner agent may incorporate improvements into the current feature when
they are necessary to satisfy governance or complete the intended
behavior.

When a feature changes how the application functions, the Planner agent has
authority to create current-scope tasks to update durable project documents
that describe that behavior. This includes documented configuration contracts,
runtime behavior, stage responsibilities, provider responsibilities,
command-line behavior, external dependencies, and artifact or ledger behavior.

Documentation updates are current-scope when stale or missing documentation
would make the completed behavior harder to understand, operate, evaluate, or
govern. They should be recorded as future Work Files only when they describe
follow-on improvements rather than the behavior completed by the current
feature.

Configuration contracts are part of the application's observable behavior.
Features that introduce or modify configuration should ensure the documented
configuration contract and the application's configuration validation behavior
remain consistent so unsupported or undocumented configuration is rejected
before runtime whenever practical.

## Approval Semantics
During autonomous feature development, specifications and evaluations are workflow artifacts produced by agents.
Specifications and evaluations do not require separate Director approval before implementation or evaluation unless the Director explicitly requests it.
The Director accepts or rejects the completed feature.
Specifications, evaluations, evaluation results, governance findings, and the Work File together provide the supporting evidence for the Director's final acceptance decision.

## Acceptance Criteria
A feature is considered complete only when:
1. A completed specification exists.
2. The implementation satisfies the specification.
3. A completed evaluation exists.
4. The evaluation passes.
5. Governance Review passes.
6. The Director accepts the result.
Passing tests alone does not guarantee acceptance. The Director may reject a feature that does not align with project goals, user experience expectations, or intended behavior.

## Goal
The goal is not to maximize automation.
The goal is to maximize confidence that accepted behavior matches the intended outcome.
