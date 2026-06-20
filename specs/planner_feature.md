# Spec: Planner

Reference `architecture.md` for system context. This spec covers only the
Planner — the coordinator. The planner spec does not implement Researcher, Curator, or
Writer; 

## What to build

A pure-Python coordinator for the techno briefing pipeline. The Planner
owns the task ledger and the logic for running pipeline stages in
sequence, validating each stage's output before advancing, and halting
cleanly on the first failure. It has no knowledge of what a stage actually
does — it just runs whatever stage list it's given and enforces the
validate-before-advance rule.

## Interface

**Ledger** — `output/ledger.json`, one per day:

```json
{
  "date": "2026-06-20",
  "stages": {
    "<stage_name>": {
      "status": "done" | "failed",
      "output": "<whatever the stage returned>",
      "validation_reason": "<why it passed or failed>",
      "timestamp": "<ISO 8601>"
    }
  }
}
```

**Stage contract** — each stage the Planner runs is described by:
- A stage has a name, a way to produce output, and a way to say pass/fail-with-reason

## Failure handling

- On failure halt the planner
- On failure the caller is told which stage failed and why

## Behavior

- Runs stages strictly in the order given in the `stages` list.
- For each stage run and validate output.
  - If valid: write `status: "done"` to the ledger for that stage, with
    the output and reason, then continue to the next stage.
  - If invalid: write `status: "failed"` to the ledger for that stage,
    then **stop** — do not run any remaining stages.
- The ledger is written after every stage, not just at the end, so a run
  that fails partway through still leaves a complete, inspectable record
  of what happened up to that point.
- At the start of a run: if `output/ledger.json`'s `date` doesn't match today,
  start a fresh ledger. If it matches today, reuse the
  existing ledger — re-running a stage overwrites that stage's entry.


## Out of scope

- Researcher, Curator, and Writer logic — each gets its own spec and
  plugs into the stage contract above.
- Cron/scheduling/OpenClaw integration — a deployment concern, not this
  spec.
- Telegram or any other delivery mechanism — the Planner only reports
  failure to the caller 
