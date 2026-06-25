# Spec: Provider-Specific Researcher Prompt Paths

## Objective
Profiles should be able to define provider-specific Researcher prompt paths so Gemini and OpenAI can be tested or run by changing the configured Researcher provider without manually swapping prompt files.

## Background
Gemini and OpenAI Researcher providers can require different prompt output contracts. Gemini-backed Researcher currently works best with item records that omit URLs because URLs are derived from provider grounding metadata. OpenAI-backed Researcher currently expects a JSON array of items with title, URL, and summary.

Using one shared Researcher prompt for both providers makes provider switching fragile. A prompt optimized for Gemini can fail OpenAI parsing, and a prompt optimized for OpenAI can ask Gemini to produce URLs that should instead come from grounding metadata.

The existing configuration already owns prompt paths. This feature extends that ownership so profiles may provide provider-specific Researcher prompts while preserving the existing single `researcher_prompt_path` behavior as a fallback.

## Requirements
- A profile may define provider-specific Researcher prompt paths keyed by Researcher provider.
- When assembling the default pipeline, the configured Researcher provider shall determine which provider-specific Researcher prompt path is used when one is available.
- If a provider-specific Researcher prompt path is available for the configured Researcher provider, that prompt path shall be used for Researcher.
- If no provider-specific Researcher prompt path is available for the configured Researcher provider, the existing profile-level Researcher prompt path shall be used as a fallback.
- Existing profiles that define only the current Researcher prompt path shall continue to work unchanged.
- Provider-specific Researcher prompt selection shall apply only to Researcher prompt selection.
- Curator prompt selection, Writer prompt selection, Writer template selection, provider selection, stage order, and delivery configuration shall remain unchanged.
- Missing or nonexistent selected Researcher prompt paths shall remain configuration errors.
- Unknown provider-specific Researcher prompt entries shall not affect runs for other configured providers.

## Behavior

### Provider-Specific Prompt Is Present
1. A profile defines a Researcher prompt path for the configured Researcher provider.
2. The default pipeline is assembled.
3. Researcher receives the provider-specific prompt path for that provider.
4. The pipeline can switch Researcher providers by changing the configured Researcher provider without manually editing the shared Researcher prompt path.

### Provider-Specific Prompt Is Absent
1. A profile does not define a Researcher prompt path for the configured Researcher provider.
2. The profile defines the existing Researcher prompt path.
3. The default pipeline is assembled.
4. Researcher receives the existing Researcher prompt path.

### Missing Selected Prompt
1. A profile selects a provider-specific Researcher prompt path for the configured Researcher provider.
2. The selected prompt path is missing or points to a nonexistent file.
3. Pipeline configuration loading fails with a readable configuration error.
4. No pipeline stages are executed.

### Provider Isolation
1. A profile defines provider-specific Researcher prompt paths for more than one provider.
2. The configured Researcher provider is changed.
3. Only the prompt path for the configured Researcher provider is selected.
4. Prompt paths for other providers do not affect the selected run.

## Validation

### Success Conditions
- A profile with provider-specific Gemini and OpenAI Researcher prompt paths selects the Gemini prompt when Researcher is configured with Gemini.
- A profile with provider-specific Gemini and OpenAI Researcher prompt paths selects the OpenAI prompt when Researcher is configured with OpenAI.
- A profile without a provider-specific prompt for the configured Researcher provider falls back to the existing Researcher prompt path.
- Existing profiles that define only the existing Researcher prompt path continue to load.
- Curator prompt path, Writer prompt path, Writer template path, stage order, model provider selection, and delivery configuration remain unchanged.
- Automated tests cover provider-specific prompt selection without live Gemini, OpenAI, Ollama, Telegram, or other external calls.

### Failure Conditions
- A configured provider-specific Researcher prompt path is ignored in favor of the fallback path.
- A missing provider-specific prompt for the configured provider prevents fallback to the existing Researcher prompt path.
- A nonexistent selected Researcher prompt file does not fail configuration loading.
- Provider-specific Researcher prompt paths affect Curator, Writer, stage order, provider selection, or delivery configuration.
- A prompt path for an unconfigured provider affects the selected Researcher run.

## Out of Scope
- Changing provider response parsing.
- Changing Gemini or OpenAI API request behavior.
- Changing Curator prompts.
- Changing Writer prompts or templates.
- Changing stage order.
- Changing profile selection behavior.
- Running live Gemini, OpenAI, Ollama, Telegram, or other external calls in automated tests.

## Completion
When implementation is complete, append a build log entry to `eval_log.md` following the format in `AGENTS.md`.
