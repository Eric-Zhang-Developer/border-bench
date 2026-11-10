## What shipped
A model's answer is read into the shape it drew with nothing repaired (`parse.py`); every drawing gets an overlap %, the rectangle and circle baselines are scored, the three flags are set, and `results/results.json` is written in exactly the shape of `results.example.json` (`score.py`); a contact sheet shows each drawing over the truth with missed land in orange and invented land in blue (`sheet.py`). Built and tested on made-up shapes only.

## Where it lives
`pipeline/parse.py`, `pipeline/score.py`, `pipeline/sheet.py`, `pipeline/test_parse.py`, `pipeline/test_score.py`, `specs/decisions/scorer-judgment-calls.md` (eleven calls the grading rules left open), `specs/features/scorer/synthetic-sheet-modern.png` and `-history.png`.

## How to check it
verify: `python3 pipeline/verify.py` pass at 9634762
`uv run pytest pipeline/test_parse.py pipeline/test_score.py` -> 39 passed. A sheet from made-up shapes: `uv run python -m pipeline.test_score /tmp/demo && uv run python -m pipeline.sheet /tmp/demo/runs/demo p1 blobland --targets /tmp/demo/targets --out /tmp/demo/sheet.png`.

## Gaps
No real drawing or merged true border has been scored, and no `results/results.json` exists yet: `python -m pipeline.score` writes nothing until `runs/p1/p1/` holds answers (the verify line still says "scores rebuilt"). The spec's follow-up (rectangle baselines pinned for the four modern targets, the first real contact sheet) waits for `truth-modern` and `sonnet-45-archive`. Three fields have no source in the inputs and are filled with the plainest true value: a model's label is its id, a target's source is empty unless `target.toml` has a `[source]` table, a missing release date is `""` (issue #18). The contact sheet does not draw the modern foil, only the tag. A cut-off answer is scored on its complete pieces, as the rule reads; the maintainer has not confirmed that reading.
