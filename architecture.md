# Architecture — infoPipeline

## What this system does
A daily automated pipeline that searches for a configured topic, curates the
results down to what's actually worth seeing by applying the configured taste
profile, formats the result into a clean outbound message, and delivers it via
the configured delivery providers on schedule.

## Components

The default pipeline is assembled from `config/pipeline.yaml`, which defines
stage order, selectable profiles, model settings, and enabled delivery
providers. Each profile supplies the prompt and template paths for one topic.

Five conceptual pieces make up the configured pipeline. Only three involve an
LLM call — the Planner and Delivery pieces are plain code.

- **Planner** (pure Python — no LLM) — coordinates the pipeline. Reads and
  writes a JSON task ledger, validates each stage's output before
  advancing to the next, and records the run outcome. It is designed to be
  invoked on a schedule by OpenClaw or cron.
- **Researcher** (configured search-capable model provider) — finds raw
  candidate items via search. Gemini and OpenAI are supported providers.
  Structured extraction, low reasoning demand.
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

## Writer Template Contract

Writer uses a markdown template to assemble the final outbound message. The
template has a message-level section containing `{items}` and an item-level
section introduced by `# Item Template`. The item-level section must include
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
`{note}`; Python assembles the final message from the configured template.

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
edit, rank, filter, or summarize the Writer's outbound message.

## External dependencies

- **Gemini API** — supported provider for Researcher search results and Curator
  ranking/filtering.
- **OpenAI API** — supported provider for Researcher search results and Curator
  ranking/filtering.
- **Ollama (local)** — supported provider for Writer item prose generation.
- **Telegram Bot API** — currently implemented delivery provider.
- **Local `.env` file** — contains provider and delivery settings such as
  `GEMINI_API_KEY`, `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, and
  `TELEGRAM_CHAT_ID`.

## Ledger

Each profile ledger records the current day's selected profile, stage status,
stage output, validation reason, delivery outcomes, timestamps, and any
diagnostic file path. When a stage fails or produces invalid output,
best-effort diagnostic JSON files are written under that profile's diagnostics
directory.

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
      "diagnostic_path": "<Failure responses returned by external services>"
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

- OpenClaw is the host/runtime, not a participant in the pipeline's logic.
  All decision-making lives in plain Python (`planner.py`) and direct API
  calls. OpenClaw or cron can invoke `planner.py` on a schedule; the Python
  application itself runs one pipeline pass per invocation.
