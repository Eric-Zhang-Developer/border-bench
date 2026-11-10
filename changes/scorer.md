## What shipped
A model's answer is read into the shape it drew with nothing repaired (`parse.py`); every drawing gets an overlap %, the rectangle and circle baselines are scored, the three flags are set, and `results/results.json` is written in exactly the shape of `results.example.json` (`score.py`); a contact sheet shows each drawing over the truth with missed land in orange and invented land in blue (`sheet.py`). Built and tested on made-up shapes only.

## Where it lives
`pipeline/parse.py`, `pipeline/score.py`, `pipeline/sheet.py`, `pipeline/test_parse.py`, `pipeline/test_score.py`, `specs/decisions/scorer-judgment-calls.md` (eleven calls the grading rules left open), `specs/features/scorer/synthetic-sheet-modern.png` and `-history.png`.

## How to check it
verify: `python3 pipeline/verify.py` pass at c100aa3
`uv run pytest pipeline/test_parse.py pipeline/test_score.py` -> 44 passed, including the rectangle baseline of each modern target pinned to one decimal (USA 56.5, Chile 4.6, Indonesia 19.8, Croatia 25.6). The first real contact sheets, Claude Sonnet 4.5 under all three candidate prompts: `specs/features/scorer/archive-usa.png`, `-chile.png`, `-indonesia.png`, `-croatia.png`, each made with `uv run python -m pipeline.sheet runs/archive pilot-a,pilot-b,pilot-c <target>`.

## Gaps
No `results/results.json` exists yet: `python -m pipeline.score` writes nothing until `runs/p1/p1/` holds answers (the verify line still says "scores rebuilt"). Only the four modern targets can be scored; Prussia and Poland wait for `truth-history`, and five archived targets have no true border at all. Three fields have no source in the inputs and are filled with the plainest true value: a model's label is its id, a target's source is empty unless `target.toml` has a `[source]` table, a missing release date is `""` (issue #18). Two grading questions the real answers raised are open for the maintainer and unchanged in the code: a broken answer is scored on its last complete piece (issue #27), and land an outline covers twice counts as empty (issue #28). The contact sheet does not draw the modern foil, only the tag.
