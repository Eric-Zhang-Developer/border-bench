## What shipped
True borders for the contiguous United States, Chile, Indonesia and Croatia, each the outline of the land. They are cut from Natural Earth 1:10m countries (version 5.1.1, public domain), and every lake that reaches a country's edge is cut out with Natural Earth 1:10m lakes (version 5.0.0): 16 for the United States, the Great Lakes among them, 3 for Chile, none for Indonesia or Croatia. Each target folder has the border, a preview with a scale bar, and a `SOURCE.md` listing both source files, their checksums, every edit and the lakes cut by name. The first version came from the 1:50m map with lakes filled in; `specs/decisions/004-truth-is-land.md` replaced it.

## Where it lives
`pipeline/prep.py`, `pipeline/test_prep.py`, `targets/usa/`, `targets/chile/`, `targets/indonesia/`, `targets/croatia/`, `specs/decisions/004-truth-is-land.md`, `specs/decisions/truth-modern-scale-and-lakes.md` (the first choice, replaced).

## How to check it
verify: `python3 pipeline/verify.py` pass at f546c4a (the head of pull request 39)
`uv run python -m pipeline.prep` rewrites the four folders with no diff.

## Gaps
Validation step missed: Indonesia is +3.8% from the published land area in the repo (it is -0.7% from the World Bank's land figure; which figure to use is open). The other three pass: USA +1.6%, Chile -1.2%, Croatia -1.7%. The published areas for the USA, Chile and Indonesia come from Wikipedia, not a primary source. Lakes wholly inside a country stay in (97 in the USA), and rivers are not cut. Lago Argentino is cut from Chile for 6 km² because the lakes file draws it across the border. Chile's frame is stretched by Easter Island. The modern foils of the history targets still come from the 1:50m map with lakes filled in.
