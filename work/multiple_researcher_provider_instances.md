# Multiple Researcher Provider Instances

## Goal

Allow the configured pipeline to execute more than one Researcher stage before
Curator.

Each configured Researcher stage should run independently using its own
provider configuration.

The normalized candidate output from all configured Researcher stages should be
combined into one candidate pool before Curator runs.

The combined candidate pool should be deduplicated before Curator receives it.

Deduplication should preserve the first occurrence according to configured
Researcher stage order and item order within each Researcher result.

When only one Researcher stage is configured, existing single-Researcher
behavior should remain unchanged.

Each Researcher provider should remain responsible for its own collection
behavior, normalization, diagnostics, and error handling.

## Director Intent

The public configuration should remain repeated flat `researcher` stage entries
in the existing `stages` list.

Do not introduce nested configuration structures such as `researcher.instances`,
`researcher.providers`, or `discovery_sources`.

The initial implementation should use two Bandcamp Researcher stages, each with
its own stage-level Bandcamp `discovery` object.
