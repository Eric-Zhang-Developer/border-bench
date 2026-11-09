---
name: One command asks a model to draw a target and saves the raw answer
depends_on: [scaffold]
owns: [pipeline/run.py, pipeline/test_run.py]
assignee: ""
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
- The prompt text sent is the file's bytes with only `{target}` replaced.
- A run file that already exists is never overwritten and never re-requested.
- Spend: a running total in dollars across the whole `runs/` tree, from recorded usage and a price table in the
  code. Before each call, stop if the total has reached the cap (default $60). A model with no known price is
  treated as $50 per million output tokens.
- A refusal, an empty answer or a `max_tokens` stop is saved as it is, with its stop reason. Transport errors and
  rate limits retry; nothing else does.
- `--dry-run` prints the calls it would make and their estimated cost, and makes none.

## Validation
- `uv run pytest pipeline/test_run.py` passes with the SDK mocked: prompt substitution is byte-exact, existing files
  are skipped, the cap stops the loop, a refusal is recorded.
- `uv run python -m pipeline.run --dry-run ...` -> a table of calls and a dollar estimate, no network call.
- One real call on the cheapest model -> a run file whose `raw` contains coordinates. Paste the file's metadata (not
  the key) in the PR, with the dollars spent.

## Defaults
If the Models API omits a release date, order that model last and flag it.
