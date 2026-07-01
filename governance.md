# Governance

## Purpose

Governance keeps autonomous development aligned with project intent. It is not
ceremony for its own sake. It exists to protect correctness, architectural
coherence, independent verification, and useful durable memory.

The goal is confidence that accepted behavior matches the Director's intent.

## Authority

The Director defines goals and accepts or rejects completed work.

Agents may propose behavior contracts, implementations, evaluations, and
future work. Those proposals are advisory until the Planner records a scope
decision and the Director accepts the completed result.

The Planner owns workflow scope during autonomous development. Implementation
observations, tests, specifications, and evaluations inform Planner decisions
but do not independently narrow the Goal or Director Intent.

## Canonical Sources

For active work:

- the Work File is the canonical workflow memory;
- the Behavior Contract is the canonical feature requirement;
- `architecture.md` is the canonical product architecture and public contract
  map;
- `eval_log.md` is append-only historical evidence;
- source code and tests are the canonical implementation state.

If two artifacts duplicate the same requirement, the Planner should identify
which one is canonical and remove or stop extending the duplicate in future
work.

## Behavioral Discipline

Requirements, evaluations, build logs, and governance findings should describe
observable behavior.

Observable behavior includes:

- command-line inputs and outputs;
- configuration acceptance and rejection;
- stage outputs and validation outcomes;
- ledger and diagnostic artifacts;
- provider requests and external side effects;
- delivery outcomes;
- user-visible failure reasons;
- documented operational contracts.

Internal implementation details should not appear in behavior contracts unless
they are themselves part of a public interface.

## Architecture Principles

Review changes against these principles:

- **Modularity**: The capability can change without unnecessary effects on
  unrelated components.
- **Separation of Responsibilities**: Each stage owns a clear job. Planner
  coordinates, Researcher collects, Curator filters, Writer formats, Delivery
  transports.
- **Configurability**: Runtime choices that operators reasonably need to vary
  belong in configuration rather than hardcoded source behavior.
- **Bounded Contracts**: Public configuration and output contracts reject
  unsupported shapes when practical.
- **Observable Verification**: Completed behavior can be checked without
  trusting implementation claims.
- **Complexity Control**: The solution is no broader than needed for the Goal.
- **Backward Compatibility**: Existing documented behavior remains unchanged
  unless the Goal explicitly changes it.
- **Safety and Privacy**: Diagnostics and errors do not expose secrets,
  credentials, tokens, chat IDs, or sensitive environment values.
- **Project Fit**: The design matches the existing command-line, provider,
  ledger, and delivery architecture.

## Workflow Lanes

Governance is proportional to risk.

### Lightweight

Appropriate for low-risk changes governed by existing contracts.

Governance may be waived if the Planner records:

- why the existing contract is sufficient;
- what evidence was checked;
- why independent evaluation is not needed.

### Standard

Appropriate for bounded observable behavior changes.

Governance should confirm:

- the Behavior Contract is complete enough;
- tests and evidence cover success and failure behavior;
- changed public behavior is documented;
- future work is separated from current scope.

### High-Assurance

Required for public contracts, configuration, providers, delivery, ledger
behavior, security/privacy, cross-stage responsibilities, or high-blast-radius
changes.

Governance must confirm:

- independent holdout evaluation occurred;
- public contracts are explicit and bounded;
- failure behavior is defined;
- side effects are intentional and verified;
- architecture responsibilities remain intact.

## Specifications

Standalone specifications are optional governance tools.

A standalone specification is required only when the Behavior Contract is too
large or important to live comfortably in the Work File, or when independent
evaluation needs a stable long-form reference.

Whether standalone or embedded, specifications must:

- describe observable behavior;
- include success and failure behavior;
- identify unchanged behavior when compatibility matters;
- avoid prescribing internal implementation details;
- state constraints such as no live external calls when relevant.

## Evaluation

Evaluation exists to provide confidence beyond implementation claims.

A strong evaluation:

- is performed from a fresh context when practical;
- reads the Behavior Contract rather than the implementation plan;
- checks externally observable behavior;
- includes failure cases and forbidden side effects;
- uses controlled providers or fixtures unless live calls are explicitly
  required;
- produces a clear PASS, PASS WITH WARNINGS, or FAIL.

Evaluation should not own scope. It may report that completed behavior does
not match the contract, that evidence is incomplete, or that side effects were
observed. The Planner decides what to do with those findings.

## Goal Reconciliation

Goal Reconciliation is a Planner responsibility and the primary gate before
evaluation.

The Planner must not accept a task merely because the assigned implementation
was completed. The Planner must ask whether the Goal and Director Intent are
satisfied by the completed observable behavior.

Current-scope work is required when a finding affects:

- the stated Goal;
- Director Intent;
- public contracts;
- required failure behavior;
- compatibility promises;
- ability to verify the behavior;
- architecture responsibilities;
- secret handling or external side effects.

Future work is appropriate when a finding is useful but not necessary to
satisfy the current Goal.

## Documentation Governance

Durable documentation should be updated only where it remains useful after the
feature branch is complete.

Highest-value durable documents:

- `architecture.md` for product architecture and public contracts;
- active Work Files for feature memory and decisions;
- `eval_log.md` for append-only evidence;
- configuration examples and operator-facing docs when behavior changes.

Avoid duplicating the same behavior across Work File, standalone spec,
evaluation file, architecture, build log, and final summary. Prefer one
canonical description plus short references elsewhere.

## Build and Evaluation Logs

Build logs describe completed capabilities, assumptions, gaps, and suspected
bugs. They should avoid implementation mechanics unless required to explain a
public contract decision.

Evaluation logs describe observable behavior and verdicts. They should not
name internal functions, helper inputs, class names, algorithms, or test
mechanics as the reason for PASS or FAIL.

Build sessions do not write evaluation entries. Evaluation sessions do not
write build-log entries.

## Governance Review

Governance Review is intentionally small. It should not repeat all task
history or re-run evaluation.

Review checklist:

- The completed behavior matches the Behavior Contract.
- The chosen workflow lane was appropriate.
- Required independent evaluation was performed or deliberately waived.
- Architecture responsibilities remain intact.
- Public contracts are documented and reject unsupported behavior where
  practical.
- Existing behavior remains compatible except where intentionally changed.
- Side effects and secret handling are acceptable.
- Current-scope gaps are not mislabeled as future work.
- The Director has enough evidence to decide.

Governance outcomes:

- **PASS**: ready for Director acceptance.
- **PASS WITH WARNINGS**: acceptable if the Planner records why warnings do
  not require current-scope work.
- **FAIL**: not ready; Planner must create or revise current-scope tasks.

## Acceptance

A change is ready for Director acceptance when:

1. the Work File contains a clear Goal, Discovery Brief, Behavior Contract,
   evidence, and final status;
2. implementation satisfies the Behavior Contract;
3. Goal Reconciliation finds no missing current-scope behavior;
4. required evaluation passes or is intentionally waived under the workflow
   lane;
5. Governance passes when required;
6. durable documentation reflects changed public behavior;
7. the Director accepts the completed work.

Passing automated tests alone is not acceptance.

## Architectural Evolution

Agents should surface architectural improvements discovered during work.

The Planner may include an improvement in current scope only when it is
necessary to satisfy the Goal, preserve architecture, make behavior
verifiable, or avoid an undocumented public contract.

Otherwise the improvement belongs in Future Work.
