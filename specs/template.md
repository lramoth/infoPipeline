# Spec: Feature Name

## Objective

A concise description of the observable problem or outcome.

## Background

Why this feature exists.
Relevant context.
Links to related specs.

## Requirements

Describe behavior that a user, caller, operator, evaluator, or generated artifact reader can observe.

- The system shall...
- The system shall...

Do not prescribe implementation details unless they are themselves observable public requirements. Avoid requiring:

- file names
- class names
- function names
- data structures
- algorithms
- library choices
- internal helper behavior

If performance, security, reliability, maintainability, or compatibility matters, state the externally observable requirement.

## Inputs

Describe user-provided, configured, command-line, file, network, or artifact inputs and their observable formats.

## Outputs

Describe visible outputs, generated artifacts, persisted records, messages, exit statuses, diagnostics, or user-facing errors and their observable formats.

## Behavior

### Normal Flow

1. ...
2. ...
3. ...

### Edge Cases

- Empty input
- Invalid data
- Missing resources
- Any boundary cases explicitly required for this feature

## Failure Handling

Describe observable failure behavior, including readable messages, halted work, retained artifacts, exit status, and side effects that must or must not occur.

Only include failures that are in scope for the feature.

## Acceptance Criteria

- [ ] Observable requirement A is satisfied.
- [ ] Observable requirement B is satisfied.
- [ ] Required failure behavior is satisfied.

## Validation

### Success Conditions

Observable checks proving completion.

### Failure Conditions

Observable conditions that must be rejected or reported as failures.

## Constraints

- Must not modify runtime behavior outside the specification.
- Must preserve existing observable behavior unless the specification explicitly changes it.
- Must not perform live external calls unless the specification explicitly requires them.

## Out of Scope

Explicitly excluded work.

## Completion

For build sessions, append a build log entry to `eval_log.md` following `AGENTS.md`.

The build log must include:

- spec used
- summary of observable work completed
- assumptions made
- gaps or suspected bugs

Build sessions must not write evaluation entries.
