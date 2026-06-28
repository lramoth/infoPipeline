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

The Director accepts or rejects the completed feature. Specifications, evaluations, and governance findings serve as supporting evidence for that decision.

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
Otherwise, improvements should be recorded as recommendations for future
Work Files.

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