# Spec: Exact URL Uniqueness Validation

## Objective
Curator validation shall reject only true duplicate item URLs, not URLs that merely share a provider, domain, redirect pattern, or visual similarity.

## Background
A real Curator run failed validation with “duplicate URLs.” The returned Curator items used Gemini grounding redirect URLs. These URLs share a common provider path and visual pattern, but distinct redirect URLs may represent distinct sources.

The validation behavior must be precise enough to distinguish exact duplicate URLs from similar-looking provider redirect URLs.

## Requirements
- Curator validation shall compare the complete URL value for each curated item.
- Curator validation shall not treat URLs as duplicates solely because they share the same domain.
- Curator validation shall not treat URLs as duplicates solely because they share the same path prefix.
- Curator validation shall not treat URLs as duplicates solely because they are Gemini grounding redirect URLs.
- Curator validation shall not compare truncated URL previews.
- Curator validation shall not compare only source titles, source domains, or grounding metadata.
- Curator validation shall fail when two or more curated items contain the same complete URL value.
- When URL duplicate validation fails, the validation reason shall identify which curated items are considered duplicates.
- The duplicate report shall include enough observable information to debug the comparison, such as item rank, item title, and the compared URL value.
- Existing Curator validation rules for required fields and rank requirements shall remain unchanged.

## Validation Success
- Curated items with distinct complete URL values pass URL uniqueness validation.
- Curated items with the same URL domain but different complete URL values pass URL uniqueness validation.
- Curated items with the same Gemini grounding redirect prefix but different complete URL values pass URL uniqueness validation.
- Curated items with different long redirect tokens pass URL uniqueness validation.

## Validation Failure
- Curated items with exactly the same complete URL value fail URL uniqueness validation.
- Validation failure identifies the duplicate URL and the affected item ranks or titles.
- Validation failure does not occur merely because URLs look visually similar.

## Constraints
- Must not perform network calls to resolve redirects.
- Must not fetch canonical URLs.
- Must not change Curator ranking or relevance behavior.
- Must not change Researcher behavior.
- Must not require live Gemini calls in tests.

## Out of Scope
- Canonical URL resolution.
- Redirect following.
- Item identity deduplication beyond URL uniqueness.
- Prompt changes.
- Retry behavior.
