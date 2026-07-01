# Governance Notes
This project is intentionally developed through behavioral specifications,
implementation by coding agents, and independent evaluation against
specifications.

`development_workflow.md` is the operational source of truth for executing the
autonomous feature development workflow. This document defines the engineering
principles that guide that workflow.

## Principles
- Specs describe observable behavior, not implementation.
- Evals test both success and failure conditions.
- Code is treated as a black box whenever possible.
- Runtime observations should drive future specs.
- The Planner Agent coordinates engineering work.
- The Planner Agent does not implement code.
- The Planner Agent does not evaluate its own implementation.
- Evaluation is performed independently whenever practical.
- Dependencies are allowed when they avoid reimplementing established functionality.
- Human review and acceptance are required for all features.

## Governance Model
The human acts as Director rather than primary implementer.
Agents may propose specifications, implementations, evaluations, and improvements. These proposals are advisory until reviewed and accepted by the Director.
The Director is responsible for:
- defining the problem or desired outcome
- selecting between competing solutions
- accepting or rejecting completed work
Agent-generated specifications and evaluations are allowed and encouraged when they improve clarity, coverage, or quality.

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
Whenever practical, coordination, implementation, and evaluation should be
performed by different actors.

This separation is intended to reduce self-validation and increase confidence in outcomes.

### Agent Expectations
Before drafting a specification or evaluation, agents should review this document.
Agents should verify that proposed specifications:
- describe observable behavior
- avoid implementation prescriptions
- include success and failure conditions
- are testable through evaluation
If a requirement cannot be evaluated, it should be revised before acceptance.

### Evaluation Independence
Whenever practical, evaluations should be authored or executed by an actor different from the implementation author.
Independent evaluation is preferred because it reduces self-validation and increases confidence in accepted behavior.

## Acceptance Criteria
A feature is considered complete only when:
1. A specification exists.
2. The implementation satisfies the specification.
3. An evaluation exists.
4. The evaluation passes.
5. The Director accepts the result.
Passing tests alone does not guarantee acceptance. The Director may reject a feature that does not align with project goals, user experience expectations, or intended behavior.

## Goal
The goal is not to maximize automation.
The goal is to maximize confidence that accepted behavior matches the intended outcome.
