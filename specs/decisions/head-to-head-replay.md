# head-to-head: what the replay shows, and which country got the clip

- Date: 2026-11-10   Decided by: the agent (`eric-4`)   Feature: head-to-head
- **Context:** `specs/features/head-to-head/spec.md` says purely visual choices are the worker's. The five below are
  not purely visual: each decides whether what the stage shows is what the model did.

## 1. The replay steps through the points the model wrote, read from its saved answer
- **Context:** the results file holds each drawing with points added along every edge longer than one degree
  (`pipeline/score.py`, `display`), so its outline cannot say which points are the model's. Claude Fable 5.2's
  Indonesia has 396 written points and 422 in the file. Replaying the file would show a count of 422 under a line
  that reads "at most 400 points", and a stream of numbers the model never wrote.
- **Options:** A, replay the results file's points / B, guess which points were added (a model that writes evenly
  spaced points on a straight border cannot be told apart from added ones) / C, read the points from the saved
  answer, with the same rule the scorer uses.
- **Choice:** C. `site/lib/answer.ts` is a port of `pipeline/parse.py`'s rule. The scorer stays the judge:
  `site/lib/geo.check.mjs` runs before every build and fails unless, for every model on every country, the points
  read this way are the saved outline (same pieces, same order, every written point present, nothing between two
  of them but points on the edge that joins them) and the count is the file's. Today: 84 of 84.
- **How to undo:** drop `written()` from `site/app/duel/page.tsx`; the page then replays the saved outline.

## 2. A closing point the model did not write is drawn but not counted
- **Context:** when a model leaves a ring open, the scorer closes it. That closing edge is part of the scored shape.
- **Choice:** the line closes, as scored; the count and the stream leave that point out, because the model did not
  write it. The final count on the stage is always the results file's `points`.
- **How to undo:** the `added` flag in `site/app/duel/duel.tsx`.

## 3. Coordinates in the stream are shown to two decimals
- **Choice:** `106.8` shows as `106.80`, so the columns line up. The prompt allows at most two decimals; a model
  that wrote more would be shown rounded. None of the 84 drawings the page shows has more than two (27,622
  numbers checked).
- **How to undo:** `toFixed(2)` in `site/app/duel/duel.tsx`.

## 4. The two maps may be wider than a strip tile
- **Context:** the strip keeps tiles near square (at most 1.8 wide to 1 tall) so a row of them lines up. On the
  stage a wide country is already as wide as its column.
- **Choice:** the head-to-head frame may be up to 3 wide to 1 tall. Same projection, same fit rule, same cap on wild
  drawings; only the empty band above and below a wide country is gone. Scores are not affected: the page computes
  none.
- **How to undo:** the third argument to `chart()` in `site/app/duel/duel.tsx`.

## 5. The hero clip is Indonesia
- **Context:** the spec asks for the oldest model against the newest, on whichever of the six countries looks best.
  All six last frames are in `site/clips/`.
- **Options:** Indonesia (38.5 to 87.8) / Croatia (29.4 to 90.1) / Prussia (45.6 to 94.0) / Poland (65.7 to 97.1) /
  the lower 48 (86.9 to 98.8) / Chile (59.1 to 84.9).
- **Choice:** Indonesia. Both models write almost the same number of points (381 and 396), so both sides draw for
  the whole eight seconds and neither sits idle; an archipelago appearing piece by piece out of typed numbers (the
  newer drawing has 29 pieces) is the picture the clip is for; and the older drawing is plainly a worse memory, not a glitch. Croatia has the bigger gap, but its
  left side stops halfway and reads as a tangle. Prussia's newer drawing has 436 points, over the 400 the stage's
  one small line names.
- **How to undo:** `npm --prefix site run record -- --target croatia` (about 75 seconds).
