---
name: Every Claude model draws all six targets with the frozen prompt
depends_on: [prompt-pilot]
owns: [runs/p1/, results/, sheets/p1/]
assignee: ""
---

# Full run

## Plan
1. `--dry-run` first; paste the estimate in the PR.
2. Run every listed model on the six targets with `prompts/p1.txt`: three samples, one for the Fable models.
3. Score, write `results/results.json`, and make one contact sheet per target in `sheets/p1/`.

## Requirements
- Sonnet 4.5 runs first.
- If the spend cap stops the run, commit what exists, say which models and targets are missing, and file a
  `needs-human` issue. Do not raise the cap.
- Pilot or archive answers are not reused as `p1` runs, even where the prompt text is identical.

## Validation
- Run files: 6 targets × (12 models × 3 + 3 models × 1) = 234, or the count the live model list implies, stated in
  the PR.
- `uv run python -m pipeline.score` -> `results/results.json`; a second run produces no diff.
- Six contact sheets embedded in the PR, with one plain sentence under each: what the strip shows.
- The PR states dollars spent, refusals, failed drawings, and every model whose answers hit `max_tokens`.

## Defaults
A model that appears on the Models API after the run starts is left for a later `fix(full-run)` PR.
