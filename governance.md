# Governance Notes
This project is intentionally developed through:
- behavioral specifications
- implementation by coding agents
- evaluation against specifications

## Principles
- Specs describe observable behavior, not implementation.
- Evals test both success and failure conditions.
- Code is treated as a black box whenever possible.
- Runtime observations should drive future specs.
- Build logs describe capabilities, not implementation details.
- Dependencies are allowed when they avoid reimplementing established functionality.
- Human review and acceptance are required for all features.

## Governance Model
The human acts as Director rather than primary implementer.
Agents may propose specifications, implementations, evaluations, and improvements. These proposals are advisory until reviewed and accepted by the Director.
The Director is responsible for:
- defining the problem or desired outcome
- approving specifications
- approving evaluation criteria
- selecting between competing solutions
- accepting or rejecting completed work
Agent-generated specifications and evaluations are allowed and encouraged when they improve clarity, coverage, or quality. Human approval is required before they become project requirements.

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

## Development Flow
The preferred workflow is:
```text
Intent
↓
Specification
↓
Implementation
↓
Evaluation
↓
Selection
```
A typical feature may follow this process:
```text
Human → define problem
Agent → draft specification
Human → review and approve specification
Agent → implement feature
Agent or independent agent → draft evaluation
Human → review and approve evaluation
Independent agent → execute evaluation
Human → accept, reject, or revise the feature
```

## Separation of Responsibilities
Whenever practical, proposal, implementation, and evaluation should be performed by different actors.
Example:
```text
Director → defines intent and approves artifacts
Agent A → proposes specification
Agent A → implements feature
Agent B → evaluates feature
Director → makes final acceptance decision
```
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
1. An approved specification exists.
2. The implementation satisfies the specification.
3. An approved evaluation exists.
4. The evaluation passes.
5. The Director accepts the result.
Passing tests alone does not guarantee acceptance. The Director may reject a feature that does not align with project goals, user experience expectations, or intended behavior.

## Goal
The goal is not to maximize automation.
The goal is to maximize confidence that accepted behavior matches the intended outcome.