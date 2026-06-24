# Architecture — infoPipeline

## What this system does
A daily automated pipeline that searches for a configured topic, curates the
results down to what's actually worth seeing by applying the configured taste
profile, formats the result into a clean outbound message, and delivers it via
the configured delivery providers on schedule.

## Components

The default pipeline is assembled from `config/pipeline.yaml`, which defines
stage order, prompt paths, model settings, and enabled delivery providers.

Five conceptual pieces make up the configured pipeline. Only three involve an
LLM call — the Planner and Delivery pieces are plain code.

- **Planner** (pure Python — no LLM) — coordinates the pipeline. Reads and
  writes a JSON task ledger, validates each stage's output before
  advancing to the next, and records the run outcome. It is designed to be
  invoked on a schedule by OpenClaw or cron.
- **Researcher** (Gemini, search-grounded API) — finds raw candidate
  items via search. Structured extraction, low reasoning demand.
- **Curator** (Gemini API prompt) — uses a configured prompt to ask Gemini to
  rank and filter the researcher's raw items. Validation checks that the
  curated output has required fields and includes a rank 1 item.
- **Writer** (local `gemma4:e4b` via Ollama) — formats the curator's
  ranked list into the final outbound message. The model generates item prose;
  Python assembles the final message from the configured template and curator
  titles/URLs.
- **Delivery** (plain Python) — transports the final outbound message to
  enabled delivery providers after all configured stages succeed. Telegram is
  the currently implemented provider.

## Configuration

`config/pipeline.yaml` is the source of truth for the default pipeline. It
defines stage order, each stage's prompt path, model provider/name/endpoint
settings, Writer's template path, and enabled delivery providers.

Prompt and template paths are supplied through configuration rather than Python
source defaults. This keeps Researcher, Curator, and Writer reusable across
topics and presentations without changing source code.

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
order. The local model supplies only per-item prose used as `{note}`; Python
assembles the final message from the configured template.

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

- **Gemini API** — Researcher search results and Curator ranking/filtering.
- **Ollama (local)** — Writer item prose generation.
- **Telegram Bot API** — currently implemented delivery provider.
- **Local `.env` file** — contains `GEMINI_API_KEY`,
  `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID`.

## Ledger

`output/ledger.json` records the current day's stage status, stage output,
validation reason, delivery outcomes, timestamps, and any diagnostic file path.
When a stage fails or produces invalid output, best-effort diagnostic JSON files
are written under `output/diagnostics/...`.

```json
{
  "date": "2026-06-20",
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
