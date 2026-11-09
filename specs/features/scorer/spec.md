---
name: Every drawing gets an overlap % that a person can check by eye
depends_on: [scaffold]
owns: [pipeline/parse.py, pipeline/score.py, pipeline/sheet.py, pipeline/test_parse.py, pipeline/test_score.py]
assignee: "eric-3"
---

# Scorer

## Plan
1. `parse.py`: answer text -> rings.
2. `score.py`: overlap %, the rectangle and circle baselines, the foil tag, `results/results.json`.
3. `sheet.py`: a contact sheet PNG for pull requests.

## Requirements
- Grading follows `specs/decisions/002-grading.md` exactly.
- `score.py` reads only `runs/` and `targets/`. It makes no network call.
- **The shape of `results.json` is fixed by `results.example.json` in this folder.** The page is built against that
  file at the same time as this feature, so the output must match it field for field. Changing the shape needs a
  `plan:` PR that both lanes see.
- `results.json` holds, per target: the truth outline, both baselines with scores, and per model the release date,
  every sample's score, the median sample's outline, and the flags `no_drawing`, `over_400_points`, `drew_modern`.
  Outlines are simplified only for display; scores come from the full geometry.
- `sheet.py` takes a run set and a target and writes one PNG: a grid of tiles, each with the truth filled, the
  drawing outlined, missed land in one colour and invented land in another, and the model and score under it.

## Validation
Built and tested on synthetic shapes, so it does not wait for real borders or real answers.
`uv run pytest pipeline/test_parse.py pipeline/test_score.py` passes, and covers:
- Truth scored against itself is 100.
- Two shapes that do not touch score 0.
- Two equal squares offset by half their width score 33.3.
- A two-point edge along the 49th parallel across 28° of longitude stays within 1 km of the parallel after
  densifying.
- A self-crossing outline scores the same value on every run.
- The parser handles fenced JSON, JSON after reasoning text, an answer with two JSON blocks (the last wins), an open
  ring, each accepted geometry type, and garbage.

- `score.py` run on a synthetic `runs/` and `targets/` tree writes a file with exactly the keys of
  `results.example.json`.

Then, as a person would: `sheet.py` on the synthetic tree -> a PNG. Embed it in the PR.

## Follow-up, once `truth-modern` and `sonnet-45-archive` are on main
A `fix(scorer)` PR by the same worker: pin the rectangle baseline of each modern target to one decimal place in a
test, and run `uv run python -m pipeline.sheet runs/archive pilot-c usa` for the first real contact sheet (Sonnet
4.5's three USA drawings with scores), embedded in that PR.

## Defaults
Missed land is drawn in a warm colour and invented land in a cool one; the page reuses the same pair.
