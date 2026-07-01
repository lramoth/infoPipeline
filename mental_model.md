# Engineering Mental Model

This document explains why autonomous development in this project is organized
the way it is.

The procedural details live in:

- `development_workflow.md` — how work moves from intent to acceptance;
- `governance.md` — what confidence rules completed work must satisfy;
- `architecture.md` — the product architecture and public contract map;
- `work/work_template.md` — the standard shape of active Work Files.

The mental model is simple: preserve correctness by separating intent,
construction, verification, and acceptance, while keeping durable memory small
enough to stay useful.

## Core Philosophy

The project does not optimize for the number of artifacts produced. It
optimizes for confidence that accepted behavior matches the Director's intent.

Confidence comes from:

- clear intent;
- explicit behavior contracts;
- fresh implementation contexts when practical;
- independent verification proportional to risk;
- Planner-owned scope reconciliation;
- small, useful durable memory;
- human acceptance before merge.

The workflow should become lighter when risk is low and stricter when the
change affects public behavior, configuration, providers, ledgers, delivery,
security, or cross-stage responsibilities.

## The Development Loop

Autonomous work follows an evidence-seeking loop:

```text
Director intent
    |
    v
Discovery
    |
    v
Behavior Contract
    |
    v
Implementation
    |
    v
Observation
    |
    v
Goal Reconciliation
    |
    +--> more planning when the goal is not yet satisfied
    |
    v
Independent Evaluation when warranted
    |
    v
Governance Review when warranted
    |
    v
Director acceptance
```

Each pass through the loop should increase understanding of the problem or
confidence in the result. If a step only repeats information already recorded
elsewhere, it should be shortened or removed in future work.

## Responsibility Separation

Different participants own different kinds of judgment:

```text
Director
    owns intent and final acceptance

Planner
    owns scope, memory, discovery, lane choice, and reconciliation

Implementation Agent
    owns construction

Evaluation Agent
    owns independent behavioral verification

Governance Reviewer
    owns compact architecture and process confidence review
```

No participant is responsible for every concern. This reduces self-validation:
the agent that builds the change should not be the only authority deciding
whether the change satisfies the goal.

## Director

The Director owns intent.

The Director defines the desired outcome and may specify public interfaces,
compatibility promises, operational constraints, or evaluation expectations.
The Director also accepts or rejects completed work.

Director Intent guides the workflow, but it should describe externally
observable needs rather than internal implementation details unless those
details are themselves public requirements.

## Planner

The Planner owns scope and durable memory.

The Planner is the long-running coordinator. Its most important job is not to
produce artifacts; it is to preserve the relationship between the original
Goal, the discovered architecture, the Behavior Contract, implementation
observations, and the evidence gathered along the way.

The Planner:

- performs Discovery before implementation planning;
- chooses the workflow lane;
- records or references the Behavior Contract;
- delegates implementation;
- interprets implementation observations;
- performs Goal Reconciliation;
- decides whether evaluation is required;
- separates current-scope work from future work;
- prepares the Director-ready summary.

The Planner does not edit implementation code. It also does not treat an
implementation agent's scope choices as authoritative. If implementation
reveals missing behavior needed to satisfy the Goal, the Planner creates
another planning iteration.

## Implementation Agent

The Implementation Agent owns construction.

It receives the active Work File, the Behavior Contract, architecture rules,
and the current task. It implements the smallest change that satisfies the
contract, adds tests proportional to risk, updates durable product
documentation when public behavior changes, and reports observations.

Implementation observations are evidence for the Planner. They may reveal:

- the Goal is not yet satisfied;
- a public contract is incomplete;
- an implementation tradeoff was made;
- an optional improvement exists;
- future work may be valuable.

The Implementation Agent may recommend, but it does not decide, whether those
observations become current-scope work.

## Evaluation Agent

The Evaluation Agent owns independent verification.

Evaluation is not mandatory ceremony for every change. It is a confidence tool
used when risk warrants it. It is required for high-assurance changes and
normally expected for standard observable behavior changes.

Evaluation reads the Behavior Contract rather than the implementation plan. It
checks what a caller, configuration author, downstream stage, operator, ledger
reader, provider endpoint, or delivery target can observe.

Evaluation reports behavior. It does not design the implementation or own
scope. If evaluation finds a mismatch, the Planner decides whether the finding
requires current-scope work, a warning, or future work.

## Governance Reviewer

Governance owns architecture and process confidence.

Governance Review is intentionally smaller than full evaluation. It does not
re-run the feature history. It asks whether the completed work fits the project
architecture and whether the Director has enough evidence to decide.

Governance checks:

- responsibilities remain separated correctly;
- public contracts are documented and bounded;
- validation and configuration agree;
- side effects are intentional and observable;
- secrets are not exposed;
- the chosen workflow lane was appropriate;
- current-scope gaps are not mislabeled as future work.

## Work File As Memory

The Work File is the active memory spine for a feature.

It should record durable decisions, not a transcript. The most important
sections are:

- Goal;
- Director Intent when needed;
- Discovery Brief;
- Workflow Lane;
- Behavior Contract;
- Task Plan;
- Iterations;
- Goal Reconciliation;
- Evidence;
- Open Questions;
- Future Work;
- Governance;
- Final Summary.

The Work File is canonical for active workflow state. It may point to specs,
evaluations, tests, logs, and docs, but it should not duplicate them at length.

## Behavior Contracts

The Behavior Contract is the project's working definition of done for a
feature.

It states:

- what triggers the behavior;
- what success looks like;
- what failure looks like;
- what side effects are allowed or forbidden;
- what must remain compatible;
- what evidence is required.

For many changes, the Behavior Contract lives directly in the Work File.
Standalone specifications are optional and should be used only when the
contract is large, public, reusable, or high-risk enough to need a separate
artifact.

## Discovery Before Planning

Discovery turns a vague goal into a testable contract.

Before task planning, the Planner should identify:

- current behavior;
- intended change;
- unchanged behavior;
- affected surfaces;
- failure modes;
- allowed and forbidden side effects;
- evidence needed;
- questions requiring Director input.

Discovery is where the workflow avoids guessing. If an ambiguity would create
public behavior, broaden scope, or weaken verification, the Planner stops and
asks instead of inventing a contract.

## Goal Reconciliation

Goal Reconciliation is the main acceptance gate inside the autonomous loop.

It asks whether the completed observable behavior satisfies the Goal and
Director Intent when read through the Behavior Contract, architecture,
governance rules, and implementation observations.

Goal Reconciliation is stronger than checking whether a task was completed.
A task can be completed literally while the feature goal remains incomplete.

The Planner should create another planning iteration when:

- implied public behavior is missing;
- failure behavior is undefined;
- unsupported public input is accepted;
- compatibility is broken unintentionally;
- stage responsibilities shifted accidentally;
- promised behavior cannot be independently observed;
- public documentation would become stale.

## Proportional Rigor

The workflow uses lanes because correctness has different costs in different
contexts.

- **Lightweight** work uses existing contracts and focused evidence.
- **Standard** work uses a Work File Behavior Contract, tests, reconciliation,
  and usually independent evaluation.
- **High-Assurance** work uses explicit contracts, stronger tests, holdout
  evaluation, governance, and durable documentation updates.

The lane choice is not about speed alone. It is about matching verification
cost to risk and blast radius.

## Product Architecture Anchor

Autonomous workflow decisions are grounded in the product architecture.

For infoPipeline, the key product responsibilities are:

- Planner coordinates configured runs and validation;
- Researcher collects and normalizes candidate items;
- Curator ranks and filters;
- Writer assembles the outbound message;
- Delivery transports after successful stages;
- ledger and diagnostics preserve observable run evidence;
- standard output is the machine-readable command result surface.

When a feature touches CLI behavior, configuration, providers, prompts,
templates, ledgers, diagnostics, delivery, or external calls, the workflow must
use the architecture document to identify the affected public contracts.

## Documentation Economy

Durable documentation should be written where it will remain useful.

The project avoids spreading the same requirement across many artifacts. A
fresh Planner should be able to continue work by reading:

- the active Work File;
- `development_workflow.md`;
- `governance.md`;
- `architecture.md`;
- any spec or evaluation explicitly referenced by the Work File.

Build logs and evaluation logs are evidence, not the primary place to discover
current requirements.

## Why This Model Exists

The model exists because autonomous development has two failure modes:

- moving quickly without enough independent confidence;
- producing so much process documentation that artifacts replace reasoning.

This system tries to avoid both.

It keeps the durable strengths of the older workflow: separation of roles,
observable behavior, fresh verification, governance, and Director acceptance.
It reduces the weaknesses by making specs and evaluations conditional,
centering Discovery and Goal Reconciliation, and treating the Work File as the
canonical active memory.

The result should feel like an autonomous engineering loop rather than a
paperwork pipeline: discover, contract, build, observe, reconcile, verify, and
accept.
