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

Five conceptual pieces make up the configured pipeline. Planner and Delivery
are plain code. Curator and Writer are model-backed in the default pipeline;
Researcher may be model-backed or source-backed depending on its configured
provider.

- **Planner** (pure Python — no LLM) — coordinates the pipeline. Reads and
  writes a JSON task ledger, validates each stage's output before
  advancing to the next, and records the run outcome. It is designed to be
  started manually or by an external scheduling mechanism.
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
`researcher_prompt_paths` profile field. When present, the configured
Researcher provider selects its matching prompt path; otherwise Researcher uses
the profile's `researcher_prompt_path`. This provider-specific prompt routing
applies only to Researcher.

Each stage declares a top-level `provider`. Model-backed providers require a
`model` block with name and endpoint. Source-backed providers may omit model
settings, prompts, and endpoints when the provider owns those details. Gemini
and OpenAI are supported for Researcher and Curator stages; Bandcamp is
supported for the Researcher stage; Ollama is currently supported for the
Writer stage.

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

## Command-line interface

`planner.py` is the command-line entry point. Each invocation either runs one
configured pipeline pass or handles an application-level command that exits
before the pipeline runs.

Supported arguments:

- `--profile <profile_name>` selects the configured profile to run or validate.
  When omitted, the configured `default_profile` from `config/pipeline.yaml` is
  used. Profile-specific runs write to that profile's ledger location.
- `--validate-config` loads and assembles the configured pipeline for the
  selected or default profile, reports whether configuration validation
  succeeded, and exits without running pipeline stages.
- `--version` prints the application version and exits without running the
  pipeline. When combined with other supported options, `--version` takes
  precedence.

Normal pipeline invocation:

```text
python3 planner.py
```

Runs one pipeline pass for the configured default profile.

Profile-selected invocation:

```text
python3 planner.py --profile techno-releases
```

Runs one pipeline pass for the selected configured profile.

Configuration validation:

```text
python3 planner.py --validate-config
python3 planner.py --validate-config --profile techno-releases
```

Validation checks that the selected or default profile can be loaded and
assembled. It validates profile selection, stage configuration, required model
settings, enabled delivery configuration, and configured prompt and template
paths. It does not run Researcher, Curator, Writer, or Delivery providers; does
not require live provider credentials or network access; does not write a
ledger; and does not send delivery messages.

Version reporting:

```text
python3 planner.py --version
```

Prints the application name and version as a single standard-output line and
exits successfully.

Command results:

Normal pipeline runs and configuration validation print one parseable JSON
result object to standard output. Successful results report success, include a
readable summary, identify the selected profile when known, and include relevant
output or validation details. Failed results report failure, include a readable
summary and reason, identify the failed stage or delivery provider when
applicable, and include artifact paths when available.

The process exit code agrees with the reported JSON status. Incidental output
from underlying stages may appear on standard error, but standard output is the
machine-readable result surface for callers and monitoring tools.

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
Planner ──▶ Researcher ──▶ Curator ──▶ Writer
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
                  Planner records stages
                          │
                          ▼
          Delivery sends via enabled providers
```

Each stage is validated before the next runs. A failed check halts the
pipeline at that stage rather than passing bad output forward.

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
files are written under that profile's diagnostics directory. Delivery failures
are recorded as delivery outcomes in the ledger; they do not currently create
stage diagnostic files.

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
