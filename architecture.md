# Architecture — infoPipeline

## What this system does
A daily automated pipeline that searches for techno production news
(labels, gear, artists — Polegroup-adjacent aesthetic, hardware relevant to
a Eurorack/classic-drum-machine studio setup), curates it down to what's
actually worth seeing by applying personal taste, formats it into a clean
message, and delivers it via Telegram every morning.

## Components

Four conceptual pieces. Only three involve an LLM call — the fourth is
plain code.

- **Planner** (pure Python — no LLM) — coordinates the pipeline. Reads and
  writes a JSON task ledger, validates each stage's output before
  advancing to the next, and marks the run done. Runs once daily via cron,
  hosted by OpenClaw.
- **Researcher** (Gemini, search-grounded API) — finds raw candidate
  items via search. Structured extraction, low reasoning demand.
- **Curator** (Gemini API prompt) — ranks and filters the
  researcher's raw items by personal taste. The one stage doing real
  judgment: distinguishing Polegroup-adjacent signal from generic festival
  noise, deduping, applying taste criteria simultaneously.
- **Writer** (local `gemma4:e4b` via Ollama) — formats the curator's
  ranked, reasoned list into the final Telegram message. Not a hard
  reasoning task — local is fine.

## Data flow

```
Cron trigger
     │
     ▼
Planner ──▶ Researcher ──▶ Curator ──▶ Writer
              │              │           │
              ▼              ▼           ▼
         Eval check 1   Eval check 2  Eval check 3
         ≥3 valid       On-taste, no  Length + format
         sources?       duplicates?   ok?
              │              │           │
              └──────────────┴───────────┘
                          │
                          ▼
                   Planner marks done,
                      advances
                          │
                          ▼
                Telegram message sent
```

Each stage is validated before the next runs. A failed check halts the
pipeline at that stage rather than passing bad output forward.

## External dependencies

- **Gemini API** — Researcher's search results, Curator's ranking call. 
- **Telegram** — Final delivery. Bot already paired and confirmed
  bidirectional.
- **Ollama (local)** — Writer. 
- .env contains GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, and TELEGRAM_CHAT_ID

## Ledger

The output/ledger.json is a record of each stage's status, output and validation

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
  }
}
```

## Runtime

- OpenClaw is the host/runtime, not a participant in the pipeline's logic.
  All decision-making lives in plain Python (`planner.py`) and direct API
  calls; OpenClaw provides infrastructure underneath:
  - **Cron scheduling** — triggers `planner.py` daily via a macOS
    LaunchAgent, so it survives terminal closure.
