# Configurable Researcher Discovery

## Goal

Allow source-backed Researcher providers to obtain their discovery behavior from configuration rather than embedding it in provider code.

Discovery configuration should define the observable candidate collection behavior while preserving the provider's responsibility for interacting with its underlying source.

The feature should improve configurability without changing the responsibilities of the Researcher, Curator, Writer, or Delivery stages.

When no discovery configuration is supplied, the existing discovery behavior should remain available as the default.

Before beginning, read:
- `development_workflow.md`
- `governance.md`
- `architecture.md`

Use those documents to guide all workflow decisions while executing this Work File.

---

## Initial Architectural Review

The current architecture already separates Researcher provider selection from
Curator, Writer, and Delivery responsibilities. Model-backed Researcher
providers obtain prompt-driven discovery behavior from configuration, while the
Bandcamp source-backed provider currently owns both source interaction and the
hardcoded discovery criteria it sends to Bandcamp Discover.

This feature should preserve the Researcher boundary: configuration may define
the observable collection criteria for a source-backed provider, but the
provider should continue to own source-specific request execution,
normalization, diagnostics, and error handling. Configuration validation should
remain the point where invalid configured runtime behavior is rejected before a
pipeline run.

The existing default Bandcamp discovery behavior must remain available when no
discovery configuration is supplied, so current invocations continue to work.
Because the feature changes configuration contracts and documented runtime
behavior, durable documentation updates are current-scope work under
`governance.md`.

---

## Tasks

- Task 1: Add configurable source-backed Researcher discovery
    - Scope: Define a behavioral specification, implement configuration-owned
      discovery behavior for source-backed Researcher providers, preserve the
      existing default behavior when no discovery configuration is supplied,
      keep provider/source responsibilities separated, update applicable
      documentation, and append the required build log entry.
    - Status: Pending

---

## Recommended Future Work Files

---

## Governance

---

## Final Summary
