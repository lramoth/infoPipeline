# Architecture — infoPipeline

## System Purpose

infoPipeline is a command-line, single-run information pipeline designed for
manual or scheduled invocation.

One invocation:

1. collects candidate items through a configured Researcher provider;
2. curates the candidates according to the configured profile;
3. formats the selected items into an outbound message;
4. records the run;
5. delivers the message through enabled delivery providers.

The system is optimized for clear stage boundaries, configurable runtime
behavior, observable command-line results, and controlled failure handling.

## Architectural Invariants

- `config/pipeline.yaml` is the source of truth for the default configured
  pipeline.
- `planner.py` is the command-line entry point.
- Planner coordinates stages and validates outputs; it does not perform model
  reasoning.
- Researcher collects candidates and normalizes them.
- Curator ranks and filters candidates.
- Writer assembles the outbound message.
- Delivery transports the completed message after all configured stages
  succeed.
- Each stage is validated before the next stage runs.
- A failed stage halts later stages and delivery.
- Delivery failure is recorded as delivery failure, not as Writer failure.
- Standard output is the machine-readable command result surface.
- Diagnostics and errors must not expose API keys, authentication headers,
  tokens, chat IDs, or environment values.

## Runtime Components

### Planner

Planner is plain Python. It loads configuration, selects the profile, assembles
the configured pipeline, coordinates execution, validates stage outputs,
records the ledger, and reports command results.

Planner owns pipeline control flow. It does not own provider-specific search,
ranking, prose generation, delivery transport, or external scheduling.

### Researcher

Researcher finds raw candidate items through the configured provider and
returns normalized items for later stages.

Supported providers:

- Gemini as a model-backed search provider;
- OpenAI as a model-backed search provider;
- Bandcamp as a source-backed discovery provider.

Researcher output must contain an item list whose complete items have title,
URL, and summary. Existing validation requires enough complete items before
the pipeline can continue.

Model-backed Researcher providers use configured prompts. Source-backed
Researcher providers may use provider-specific discovery configuration while
still owning source interaction, normalization, diagnostics, and error
handling.

### Curator

Curator is model-backed. It applies the configured profile prompt to Researcher
items and returns ranked, filtered candidates.

Supported providers:

- Gemini;
- OpenAI.

Curator validation requires the documented curated fields and a rank 1 item.

### Writer

Writer uses the configured provider to produce per-item prose and Python logic
to assemble the final outbound message from the configured template.

The current supported Writer provider is local Ollama with model
`gemma4:e4b`.

Curator output remains authoritative for item titles, source URLs, and rank
order. Writer model output supplies item notes only.

### Delivery

Delivery sends the final outbound message through enabled delivery providers
after all configured stages succeed.

The currently implemented delivery provider is Telegram.

Delivery does not generate, edit, rank, filter, or summarize the Writer's
message. Delivery outcomes are recorded separately from stage outcomes.

## Configuration Contracts

`config/pipeline.yaml` defines:

- default profile;
- selectable profiles;
- stage order;
- stage providers;
- model settings required by model-backed providers;
- prompt and template paths;
- source-backed discovery settings where supported;
- enabled delivery providers;
- profile-specific ledger and diagnostics locations.

When no profile is selected, the configured default profile is used.

Profile-specific runs write to profile-specific ledger locations so separate
scheduled jobs do not overwrite one another.

### Stage Providers

Each stage declares a top-level `provider`.

Model-backed Researcher and Curator providers require:

```yaml
provider: openai
model:
  name: gpt-4.1-mini
  endpoint: https://api.openai.com/v1/responses
```

or:

```yaml
provider: gemini
model:
  name: gemini-2.5-flash
  endpoint: https://generativelanguage.googleapis.com/v1beta/models
```

The Writer currently supports:

```yaml
provider: ollama
model:
  name: gemma4:e4b
  endpoint: http://localhost:11434/api/generate
```

Bandcamp is supported only for Researcher and may omit model settings because
it is source-backed.

### Prompt and Template Paths

Prompt and template paths are configured rather than hardcoded into stage
source code.

A profile supplies the prompt and template paths for its topic. Researcher also
supports provider-specific prompt paths through optional
`researcher_prompt_paths`. When present, the configured Researcher provider
selects its matching prompt path. Otherwise it uses the profile's
`researcher_prompt_path`.

Provider-specific prompt routing applies only to Researcher.

### Bandcamp Discovery

Bandcamp Researcher may accept optional stage-level `discovery`
configuration:

```yaml
provider: bandcamp
discovery:
  category_id: 0
  tag_norm_names:
    - hypnotic-techno
    - techno
  geoname_id: 0
  slice: new
  time_facet_id: 0
  cursor: "*"
  size: 24
  include_result_types:
    - a
    - s
```

Accepted Bandcamp discovery fields:

- integer: `category_id`, `geoname_id`, `time_facet_id`, `size`;
- non-empty string: `slice`, `cursor`;
- non-empty list of non-empty strings: `tag_norm_names`,
  `include_result_types`.

Bandcamp discovery configuration accepts only these documented fields.
Unsupported fields are rejected during configuration loading.

When Bandcamp discovery is omitted, the existing default Bandcamp discovery
behavior is used.

Discovery configuration is rejected for model-backed Researcher providers,
which continue to use prompts for discovery behavior.

## Command-Line Interface

`planner.py` handles either one configured pipeline run or an application-level
command that exits before stages run.

Supported arguments:

- `--profile <profile_name>` selects the configured profile to run or validate.
- `--validate-config` loads and assembles the selected or default profile and
  reports whether configuration validation succeeded without running stages.
- `--version` prints the application name and version and exits successfully.
  When combined with other supported options, `--version` takes precedence.

Normal run:

```text
python3 planner.py
python3 planner.py --profile techno-releases
```

Configuration validation:

```text
python3 planner.py --validate-config
python3 planner.py --validate-config --profile techno-releases
```

Version:

```text
python3 planner.py --version
```

Normal pipeline runs and configuration validation print one parseable JSON
result object to standard output. The process exit code agrees with the JSON
status.

Incidental provider or diagnostic output may appear on standard error, but
standard output remains the machine-readable result surface.

`--validate-config` validates profile selection, stage configuration, required
model settings, enabled delivery configuration, and configured prompt/template
paths. It does not run providers, call the network, write a ledger, or send
delivery messages.

## Writer Template Contract

Writer templates are markdown files with a message-level section containing
`{items}` and an item-level section introduced by `# Item Template`.

The message-level section may optionally start with `# Message Template`.

The item-level section must include:

- `{title}`;
- `{note}`;
- `{url}`.

Example:

```markdown
Daily briefing

{items}

# Item Template

• {title}

{note}

Source:
{url}
```

Python assembles the final message from the configured template, Curator
titles, Curator URLs, Curator rank order, and Writer notes.

## Data Flow

```text
Invocation
    |
    v
Configuration load and profile selection
    |
    v
Planner
    |
    v
Researcher -> validate candidate items
    |
    v
Curator -> validate ranked curated items
    |
    v
Writer -> validate final message coverage
    |
    v
Ledger update
    |
    v
Delivery through enabled providers
    |
    v
Command result on stdout
```

Each validation step must pass before the next stage runs. Invalid output is
recorded with a readable reason and halts the pipeline.

## Ledger and Diagnostics

Each configured invocation writes the current ledger for the selected profile.
Re-running the same profile updates that profile's ledger location with the
current run.

The ledger records:

- run date;
- selected profile;
- stage statuses;
- stage outputs;
- validation reasons;
- timestamps;
- diagnostic file paths when available;
- delivery outcomes.

Representative shape:

```json
{
  "date": "2026-06-20",
  "profile": "<profile_name>",
  "stages": {
    "<stage_name>": {
      "status": "done",
      "output": "<stage output>",
      "validation_reason": "<reason>",
      "timestamp": "<ISO 8601>",
      "diagnostic_path": "<optional diagnostic path>"
    }
  },
  "delivery": {
    "<provider_name>": {
      "provider": "<provider_name>",
      "status": "done",
      "reason": "<delivery result>",
      "timestamp": "<ISO 8601>"
    }
  }
}
```

When a stage raises an error or produces invalid output, best-effort diagnostic
JSON files are written under that profile's diagnostics directory.

Delivery failures are recorded as delivery outcomes. They do not currently
create stage diagnostic files.

## External Dependencies

Runtime dependencies:

- Gemini API for supported Researcher and Curator model-backed behavior;
- OpenAI API for supported Researcher and Curator model-backed behavior;
- Bandcamp Discover for source-backed Researcher discovery;
- Ollama local endpoint for Writer prose generation;
- Telegram Bot API for delivery;
- local `.env` values for provider and delivery credentials.

Implementation and local tests should avoid live external calls unless the
active Work File explicitly requires them. Evaluation uses controlled endpoints
or fixtures by default.

## Failure Model

Configuration loading failures occur before stages run.

Stage failures halt the pipeline at the failed stage. Later stages do not run.

Delivery runs only after all configured stages have completed successfully.
Delivery failure is recorded separately and does not alter the Writer output or
turn the Writer stage into a failed stage.

Readable failure reasons should be exposed through command results, ledger
entries, or diagnostics as appropriate. Failure reporting must not expose
secrets.

## Change Impact Guide

Use this guide during Discovery:

- CLI changes affect command results, exit codes, stdout/stderr contracts, and
  operator docs.
- Configuration changes affect loading, validation, examples, and
  `--validate-config`.
- Researcher changes affect candidate item contracts, provider boundaries,
  diagnostics, and Curator inputs.
- Curator changes affect ranking/filtering contracts and Writer inputs.
- Writer changes affect template contracts, outbound message shape, and
  delivery inputs.
- Delivery changes affect external side effects and delivery ledger outcomes.
- Ledger changes affect diagnostics, monitoring, and scheduled-run
  observability.
- Provider changes affect credentials, network calls, failure modes, and
  secret handling.

## Scheduling and Operation

The application does not own scheduling. External scheduling is responsible for
starting `planner.py` with the configured working directory, environment, and
credentials.

Schedulers and operators should observe:

- process exit status;
- standard output JSON result;
- standard error incidental output;
- profile ledger;
- diagnostic artifacts.
