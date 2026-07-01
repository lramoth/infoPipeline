# Architecture — infoPipeline

## What this system does
A single-run pipeline, designed for scheduled invocation, that collects
candidate items from a configured Researcher provider, curates the results down
to what's actually worth seeing by applying the configured taste profile,
formats the result into a clean outbound message, and delivers it via the
configured delivery providers.

## Components

The default pipeline is assembled from `config/pipeline.yaml`, which defines
stage order, selectable profiles, model settings, and enabled delivery
providers. Each profile supplies the prompt and template paths for one topic.
The current default profile is `techno-releases`; its default stage path uses
Bandcamp for Researcher collection, OpenAI for Curator ranking/filtering,
Ollama for Writer prose generation, and Telegram delivery when enabled.

Five conceptual pieces make up the configured pipeline. The runtime Planner and
Delivery are plain code. Curator and Writer are model-backed in the default
pipeline; Researcher may be model-backed or source-backed depending on its
configured provider.

- **runtime Planner** (pure Python — no LLM) — coordinates the pipeline. Reads
  and writes a JSON task ledger, validates each stage's output before advancing
  to the next, and records the run outcome. It is designed to be started
  manually or by an external scheduling mechanism.
- **Researcher** (configured collection provider) — finds raw candidate items
  through the configured provider. Gemini and OpenAI are supported as
  search-capable model providers; Bandcamp is supported as a source-backed
  discovery provider. Researcher exposes normalized candidate items to later
  stages regardless of provider.
- **Curator** (configured model provider) — uses a configured prompt to rank
  and filter the researcher's raw items. Gemini and OpenAI are supported
  providers. Validation checks that the curated output has required fields and
  includes a rank 1 item.
- **Writer** (configured provider, currently local `gemma4:e4b` via Ollama) —
  formats the curator's ranked list into the final outbound message. The model
  generates item prose; Python assembles the final message from the configured
  template and curator titles/URLs.
- **Delivery** (plain Python) — transports the final outbound message to
  enabled delivery providers after all configured stages succeed. Telegram is
  the currently implemented provider.

## Configuration

`config/pipeline.yaml` is the source of truth for the default pipeline. It
defines stage order, selectable profiles, stage providers, provider-required
model settings, and enabled delivery providers. A profile supplies prompt and
template paths for providers that use prompts or templates.

Prompt and template paths are supplied through configuration rather than Python
source defaults. This keeps Researcher, Curator, and Writer reusable across
topics and presentations without changing source code.

Researcher also supports provider-specific prompt paths through the optional
`researcher_prompt_paths` profile field. This routing applies only to
prompt-using Researcher providers. Gemini and OpenAI select the prompt path
matching the configured Researcher provider when one is present; otherwise they
use the profile's `researcher_prompt_path`. Bandcamp is source-backed and does
not use Researcher prompt paths.

Each stage declares a top-level `provider`. Model-backed providers require a
`model` block with name and endpoint. Source-backed providers may omit model
settings, prompts, and endpoints when the provider owns those details. Gemini
and OpenAI are supported for Researcher and Curator stages; Bandcamp is
supported for the Researcher stage; Ollama is currently supported for the
Writer stage. Unsupported stage providers are rejected while configuration is
loaded.

Bandcamp Researcher stages may include a stage-level `discovery` block. When
the block is omitted, Bandcamp uses its built-in default discovery criteria.
When present, the configuration must contain only the supported Bandcamp
Discover criteria fields. Integer fields are `category_id`, `geoname_id`,
`time_facet_id`, and `size`; string fields are `slice` and `cursor`; list
fields are `tag_norm_names` and `include_result_types`, and each list must
contain non-empty strings. Missing, malformed, or unsupported Bandcamp
discovery fields are rejected before a run starts. Discovery configuration is
supported only for the Bandcamp Researcher provider; discovery configuration on
model-backed Researcher providers is rejected before a run starts.

Delivery configuration is loaded from the top-level `delivery` list. A delivery
entry must declare a known provider and a boolean `enabled` flag. Disabled
providers are ignored. Telegram is the currently implemented delivery provider.
Malformed delivery configuration is rejected when the pipeline or configuration
validation is assembled.

Gemini-backed Researcher or Curator stage:

```yaml
provider: gemini
model:
  name: gemini-2.5-flash
  endpoint: https://generativelanguage.googleapis.com/v1beta/models
```

OpenAI-backed Researcher or Curator stage:

```yaml
provider: openai
model:
  name: gpt-4.1-mini
  endpoint: https://api.openai.com/v1/responses
```

Bandcamp-backed Researcher stage:

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

Ollama-backed Writer stage:

```yaml
provider: ollama
model:
  name: gemma4:e4b
  endpoint: http://localhost:11434/api/generate
```

Callers may select a profile when invoking the command-line entry point. When
no profile is selected, the configured `default_profile` is used. Profile runs
write to profile-specific ledger locations so separate scheduled jobs do not
overwrite each other's same-day run records.

## Command-line result

Each command-line invocation runs one pipeline pass and prints one parseable
JSON result object to standard output. Successful results report success,
include a readable summary, identify the selected profile when known, include
the final pipeline output, and point to the ledger path. Failed results report
failure, include a readable summary and reason, identify the failed stage or
delivery provider when applicable, and include artifact paths when available.

The process exit code agrees with the reported JSON status. Incidental output
from underlying stages may appear on standard error, but standard output is the
machine-readable result surface for callers and monitoring tools.

`--validate-config` loads and assembles the configured pipeline for the
selected profile, or the configured default profile when none is selected, and
then exits without running the pipeline. It reports a parseable JSON success or
failure result to standard output. Validation checks profile selection, stage
providers, required model settings, required prompt and template files,
Bandcamp discovery configuration, and delivery configuration. It does not call
Researcher, Curator, Writer, Delivery, or external providers; it does not write
a ledger; and it does not attempt Telegram delivery.

`--version` prints a single-line version report and exits successfully before
configuration validation or pipeline execution. The current report is:

```text
infoPipeline 0.1.0
```

## Writer Template Contract

Writer uses a markdown template to assemble the final outbound message. The
template has a message-level section containing `{items}` and an item-level
section introduced by `# Item Template`. The message-level section may
optionally start with `# Message Template`. The item-level section must include
`{title}`, `{note}`, and `{url}`.

```markdown
Daily briefing

{items}

# Item Template

• {title}

{note}

Source:
{url}
```

Curator output remains authoritative for item titles, source URLs, and rank
order. The configured Writer model supplies only per-item prose used as
`{note}`. The Writer expects one note per curated item, and Python assembles the
final message from the configured template.

## Data flow

```
Scheduled invocation
     │
     ▼
 runtime Planner ──▶ Researcher ──▶ Curator ──▶ Writer
              │              │           │
              ▼              ▼           ▼
         Validate      Validate      Validate
         ≥3 items      required      every item
         with title,   fields and    appears in
         URL, summary  rank 1        rank order
              │              │           │
              └──────────────┴───────────┘
                          │
                          ▼
             runtime Planner records stages
                          │
                          ▼
          Delivery sends via enabled providers
```

Each stage is validated before the next runs. A failed check halts the
pipeline at that stage rather than passing bad output forward.

Researcher output exposes normalized items as the downstream contract. Provider
metadata can differ by Researcher provider. Gemini-backed Researcher output
includes normalized items, a `raw_provider_response` section with bounded
provider/search context, and a `normalization` section that identifies grounded
search URL provenance. Bandcamp-backed Researcher output includes normalized
items, a `raw_provider_response` section with the endpoint, discovery request
body, and bounded response preview, plus a `normalization` section identifying
Bandcamp Discover URL provenance. OpenAI-backed Researcher output includes
normalized items and available web-search metadata under `grounding_metadata`.
Curator, Writer, and Delivery consume normalized items and do not require
provider-specific metadata to operate.

Delivery runs only after all configured stages have completed successfully.
Delivery is recorded separately from stage results and does not generate,
edit, rank, filter, or summarize the Writer's outbound message. Delivery
failure is reported separately from stage failure and does not change the
recorded Writer output or turn a successful Writer stage into a failed stage.

## External dependencies

- **Gemini API** — supported provider for Researcher search results and Curator
  ranking/filtering.
- **OpenAI API** — supported provider for Researcher search results and Curator
  ranking/filtering.
- **Bandcamp Discover API** — supported source-backed provider for Researcher
  candidate collection.
- **Ollama (local)** — supported provider for Writer item prose generation.
- **Telegram Bot API** — currently implemented delivery provider.
- **Local `.env` file** — contains provider and delivery settings such as
  `GEMINI_API_KEY`, `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, and
  `TELEGRAM_CHAT_ID`.

## Ledger

Each configured invocation writes the current ledger for the selected profile.
Different profiles use separate ledger locations so separate scheduled jobs do
not overwrite each other's records. Re-running the same profile updates that
profile's ledger location with the current run.

The ledger records the selected profile, stage status, stage output, validation
reason, delivery outcomes, timestamps, and any stage diagnostic file path. When
a stage raises an error or produces invalid output, best-effort diagnostic JSON
files are written under a dated directory below the selected profile's ledger
directory, for example `output/<profile>/diagnostics/<YYYY-MM-DD>/`. Delivery
failures are recorded as delivery outcomes in the ledger; they do not currently
create stage diagnostic files.

```json
{
  "date": "2026-06-20",
  "profile": "<profile_name>",
  "stages": {
    "<stage_name>": {
      "status": "done" | "failed",
      "output": "<whatever the stage returned>",
      "validation_reason": "<why it passed or failed>",
      "timestamp": "<ISO 8601>",
      "diagnostic_path": "<optional path to a diagnostic record>"
    }
  },
  "delivery": {
    "<provider_name>": {
      "provider": "<provider_name>",
      "status": "done" | "failed",
      "reason": "<delivery result or failure reason>",
      "timestamp": "<ISO 8601>"
    }
  }
}
```

## Runtime

`planner.py` is the command-line entry point and runs one pipeline pass per
invocation. It may be started manually or by any external scheduling mechanism,
provided the configured environment, working directory, and provider credentials
are available at run time.

All decision-making lives in plain Python (`planner.py`) and direct provider
API calls. External scheduling is responsible only for starting runs and
observing their process status, standard output, standard error, and any
configured artifacts.
