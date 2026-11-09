---
name: Every drawing gets an overlap % that a person can check by eye
depends_on: [truth-modern, sonnet-45-archive]
owns: [pipeline/parse.py, pipeline/score.py, pipeline/sheet.py, pipeline/test_parse.py, pipeline/test_score.py]
assignee: ""
---

# Scorer

## Plan
1. `parse.py`: answer text -> rings.
2. `score.py`: overlap %, the rectangle and circle baselines, the foil tag, `results/results.json`.
3. `sheet.py`: a contact sheet PNG for pull requests.

## Requirements
- Grading follows `specs/decisions/002-grading.md` exactly.
- `score.py` reads only `runs/` and `targets/`. It makes no network call.
- `results.json` holds, per target: the truth outline, both baselines with scores, and per model the release date,
  every sample's score, the median sample's outline, and the flags `no_drawing`, `over_400_points`, `drew_modern`.
  Outlines are simplified only for display; scores come from the full geometry.
- `sheet.py` takes a run set and a target and writes one PNG: a grid of tiles, each with the truth filled, the
  drawing outlined, missed land in one colour and invented land in another, and the model and score under it.

## Validation
`uv run pytest pipeline/test_parse.py pipeline/test_score.py` passes, and covers:
- Truth scored against itself is 100.
- Two shapes that do not touch score 0.
- Two equal squares offset by half their width score 33.3.
- A two-point edge along the 49th parallel across 28° of longitude stays within 1 km of the parallel after
  densifying.
- A self-crossing outline scores the same value on every run.
- The rectangle baseline for each modern target is pinned to one decimal place.
- The parser handles fenced JSON, JSON after reasoning text, an answer with two JSON blocks (the last wins), an open
  ring, each accepted geometry type, and garbage.

Then, as a person would: `uv run python -m pipeline.sheet runs/archive pilot-c usa` -> a PNG of Sonnet 4.5's three USA
drawings with scores. Embed it in the PR.

## Defaults
Missed land is drawn in a warm colour and invented land in a cool one; the page reuses the same pair.
