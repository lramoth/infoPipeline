# Engineering Mental Model

This document describes the conceptual model used to organize autonomous software development within this project.

It explains **why** responsibilities are divided as they are.

The implementation details of this model are described in:

- `development_workflow.md` — how features are developed
- `governance.md` — how completed work is evaluated and accepted

---

# Core Philosophy

Software development consists of several distinct responsibilities.

Rather than assigning every responsibility to a single agent, this project intentionally separates them.

Each participant owns one concern.

```text
Director
    owns intent

Planner
    owns state

Implementation Agents
    own construction

Evaluation Authoring Agents
    own evaluation design

Evaluation Agents
    own verification

Governance
    owns architecture

Director
    owns acceptance
```

No participant is responsible for every concern.

This separation reduces self-validation, improves architectural quality, and enables long-running autonomous development.

---

# Responsibilities

## Director

**Owns intent.**

The Director defines the desired outcome for a feature.

The Director approves completed work and remains accountable for the final product.

The Director does not perform implementation.

---

## Planner

**Owns state.**

The Planner coordinates the complete feature lifecycle.

The Planner maintains the Work File as the persistent memory of the feature, delegates work to specialized subagents, records durable decisions, and determines what should happen next.

The Planner does not implement code or evaluate results.

---

## Implementation Agents

**Own construction.**

Implementation agents transform approved specifications into working software.

During implementation they may identify architectural improvements, missing behavior, or opportunities for future work.

Implementation agents recommend these findings to the Planner but never decide whether they become additional work.

---

## Evaluation Authoring Agents

**Own evaluation design.**

After implementation is complete, evaluation authoring agents create evaluations based on the completed implementation and the approved specification.

Separating evaluation authoring from implementation preserves the project's holdout philosophy and reduces implementation bias.

---

## Evaluation Agents

**Own verification.**

Evaluation agents execute evaluations without modifying the implementation.

Their responsibility is to determine whether observable behavior satisfies the specification.

Evaluation agents report results back to the Planner.

---

## Governance

**Owns architecture.**

Governance evaluates completed work against the project's architectural principles.

Examples include:

- modularity
- configurability
- scalability
- complexity control
- separation of responsibilities
- observable behavior
- project fit

Governance determines whether the implementation is architecturally acceptable.

Governance does not direct implementation details.

---

# Why This Model Exists

The objective is not simply to automate software development.

The objective is to maximize confidence that accepted software satisfies both its intended behavior and the project's architectural standards.

Separating responsibilities improves:

- independent verification
- architectural discipline
- explainability
- long-running autonomous execution
- confidence in accepted behavior

Each participant focuses on a single responsibility rather than attempting to optimize every concern simultaneously.

---

# Relationship Between Documents

```text
mental_model.md
        │
        ├── explains WHY the system is organized this way
        │
        ├── development_workflow.md
        │       explains HOW features are developed
        │
        └── governance.md
                explains HOW completed work is judged
```

Together these documents define the philosophy, workflow, and governance model that guide development throughout the project.
