# Governance Principles

`development_workflow.md` is the source of truth for executing the autonomous
feature development workflow. This document contains only the principles that
guide that workflow.

## Principles
- Specs describe observable behavior, not implementation.
- Evals test both success and failure conditions.
- Code is treated as a black box whenever possible.
- Runtime observations should drive future specs.
- The Planner Agent coordinates engineering work.
- The Planner Agent does not implement code.
- The Planner Agent does not evaluate its own implementation.
- Evaluation is performed independently whenever practical.
- Dependencies are allowed when they avoid reimplementing established
  functionality.
- Human review and acceptance are required for all features.
- The goal is confidence that accepted behavior matches the intended outcome,
  not maximum automation.
