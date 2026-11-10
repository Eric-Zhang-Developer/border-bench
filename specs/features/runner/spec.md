---
name: One command asks a model to draw a target and saves the raw answer
depends_on: [scaffold]
owns: [pipeline/run.py, pipeline/test_run.py]
assignee: "eric-1"
---

# Runner

## Plan
1. List models from the Models API; drop Mythos and preview ids; keep `created_at`.
2. Fill `{target}` in a prompt file, send one user message, stream, save the run file.
3. Track spend from token usage and stop at the cap.

## Requirements
- Follows `specs/decisions/003-models.md`: official `anthropic` SDK, streaming, `max_tokens` 64000, no `thinking`,
  `effort`, sampling or fallback parameters, no system prompt, no tools.
- Inputs: a prompt file, a prompt id, a set name (`pilot`, `archive`, `p1`), target names (from
  `targets/<id>/target.toml` or a TOML list), models (default: all listed), samples per model.
- Output: `runs/<set>/<prompt-id>/<model>/<target>/<n>.json` with the fields listed in `specs/tech-stack.md`. The raw
  answer is saved exactly as returned.
- Every run file also records, for later cost, token and time charts (Eric, 2026-11-09: "Let's do that"):
  `started_at` (UTC, when the request was sent), `first_token_ms` (to the first streamed content of any kind),
  `first_text_ms` (to the first visible text; null if none arrived), `duration_ms` (to the end of the stream),
  `attempts` (1 unless the call was retried; timings describe the attempt that succeeded), `usage` (the SDK's usage
  object verbatim, every field), `price_table_date` and `sdk_version`.
- The prompt text sent is the file's bytes with only `{target}` replaced.
- A run file that already exists is never overwritten and never re-requested.
- Spend: a running total in dollars across the whole `runs/` tree, from recorded usage and a price table in the
  code. Before each call, stop if the total plus the most that call could cost (a full 64,000-token answer) would
  pass the cap (default $60), so spend can never end above it. A model with no known price is treated as $10 per
  million input tokens and $50 per million output tokens, the dearest row in the table.
- A refusal, an empty answer or a `max_tokens` stop is saved as it is, with its stop reason. Transport errors and
  rate limits retry, up to five times, inside the runner (the SDK's own hidden retries are off); nothing else does.
- `--dry-run` prints the calls it would make and their estimated cost, and makes none. Because it makes no network
  call it cannot read the live lineup: it uses the ids passed with `--models`, or every id in the price table.
- `--list-models` prints the live lineup with release and retirement dates. It is free and needs the key.

## Validation
- `uv run pytest pipeline/test_run.py` passes with the SDK mocked: prompt substitution is byte-exact, existing files
  are skipped, the cap stops the loop, a refusal is recorded, the timing fields exist and are ordered
  (`first_token_ms` <= `duration_ms`), a dropped connection is retried and counted, a rejected request is not.
- `uv run python -m pipeline.run --dry-run ...` -> a table of calls and a dollar estimate, no network call.
- One real call on the cheapest model -> a run file whose `raw` contains coordinates. Paste the file's metadata (not
  the key) in the PR, with the dollars spent.

## Defaults
If the Models API omits a release date, order that model last and flag it.
