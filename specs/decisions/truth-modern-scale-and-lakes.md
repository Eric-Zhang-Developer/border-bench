# truth-modern: the 1:50m map is kept although three shapes miss the area check

> Replaced on 2026-11-09 by `004-truth-is-land.md`: the borders now come from the 1:10m map with border lakes cut
> out (option C below). This file is kept as the record of the first choice.

- Date: 2026-11-09   Decided by: agent (default taken; Eric reviews the pull request)   Feature: truth-modern
- **Context:** the spec names Natural Earth 1:50m as the source and asks that each shape's area be within 2% of the
  published land area. Measured: USA +3.6%, Chile -0.8%, Indonesia +2.9%, Croatia -3.6% (against its total; no land
  figure found). Reasons seen in the previews: the USA shape counts its side of the Great Lakes as territory; Croatia
  at this scale has 12 islands of more than a thousand and no gap at Neum; Indonesia falls between its published land
  and total figures.
- **Options:** A, keep 1:50m as the spec says and record the misses. B, use Natural Earth 1:10m (a new download, same
  licence, finer coast and more islands). C, also cut lakes out with Natural Earth's lakes file (another download), so
  "land only" in the prompt and the truth mean the same thing.
- **Choice:** A. It is what the spec says and it changes nothing that B or C could not redo: no score exists yet, and
  `pipeline/prep.py` rebuilds every target from the source file. The 2% check is not loosened; it is reported as missed.
- **Also decided here:** "the lower 48" is cut with a box (longitude -125 to -66, latitude 24 to 50) applied to each
  piece's centre. It is a named step in `prep.py`, not a hand edit.
- **How to undo:** change the source URL and checksum (and add the lakes step) in `pipeline/prep.py`, run it, and
  review the new previews. Do it before the scorer's rectangle baselines are pinned and before any score is public.
