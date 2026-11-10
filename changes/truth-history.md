## What shipped
True borders for the Kingdom of Prussia on 1 January 1816 (HistoGIS shape 10039: 31 pieces, 16 enclaves, 275,463 km²) and Poland on 1 January 1938 (CShapes 2.0: one piece, 388,378 km²). Each has the modern country as a foil from Natural Earth, a preview with the foil outlined in red, and a `SOURCE.md` with the source, checksum, licence, every edit and every judgment call.

## Where it lives
`pipeline/prep_history.py`, `targets/prussia-1815/`, `targets/poland-1938/`, `specs/decisions/truth-history-prussia-source.md`.

## How to check it
verify: `python3 pipeline/verify.py` FAIL (exit 1) at 48702db: `verify: FAIL, 8 missing tile(s)`. Expected until the models lane draws the two new targets: verify wants a drawing from every model for every target, and none exist yet for these two.
`uv run python -m pipeline.prep_history` rewrites both folders with no diff. The scorer gives each truth 100.0 against itself.

## Gaps
Both outlines are non-commercial: Poland by its licence (CC BY-NC-SA 4.0), Prussia because HistoGIS (CC BY 4.0) built it from Census Mosaic files with non-commercial terms; nobody has asked HistoGIS how the two fit. Prussia's outline shows the border as it stood by April 1817, not exactly 1 January 1816: the Duchy of Westphalia is already inside (handed over July 1816). The history cited is from encyclopedia pages; no treaty text was read. The folder is named `prussia-1815` while the target date is 1816, as the spec has it.
