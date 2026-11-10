## What shipped
True borders for the contiguous United States, Chile, Indonesia and Croatia, cut from Natural Earth 1:50m (version 5.1.1, public domain). Each target folder has the border, a preview with a scale bar, and a `SOURCE.md` listing the source, checksum and every edit.

## Where it lives
`pipeline/prep.py`, `targets/usa/`, `targets/chile/`, `targets/indonesia/`, `targets/croatia/`, `specs/decisions/truth-modern-scale-and-lakes.md`.

## How to check it
verify: `python3 pipeline/verify.py` pass at 767cdf1
`uv run python -m pipeline.prep` rewrites the four folders with no diff.

## Gaps
Validation step missed: three of four shapes are outside 2% of the published area (USA +3.6%, Indonesia +2.9%, Croatia -3.6%); only Chile passes (-0.8%). The USA shape counts its side of the Great Lakes as territory; Croatia has 12 islands and no gap at Neum. The published areas come from Wikipedia, not a primary source. Chile's frame is stretched by Easter Island.
