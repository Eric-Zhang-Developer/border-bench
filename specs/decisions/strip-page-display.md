# strip-page: how a drawing is put on the page

- Date: 2026-11-09   Decided by: agent (`eric-4`)   Feature: strip-page
- **Context:** the spec fixes what a tile shows (truth filled, drawing outlined, missed and invented land in two
  colours) and says "if a choice is purely visual, make it and show it". Five choices below are not purely visual:
  each one decides what a reader can or cannot check by eye. The results file
  (`specs/features/scorer/results-format.md`) is silent on all five.

## 1. One frame per target, and it stops growing at 1.8 times the truth
- **Options:** A, frame fitted to the truth only (a drawing that overshoots is cut off in most tiles) / B, frame
  fitted to the truth and every drawing (one wild drawing shrinks all the others to dots) / C, B with a cap.
- **Choice:** C. The frame holds the truth and every drawing of that target, but never grows past 1.8 times the
  truth's width or height. A drawing that still leaves it is cut at the edge, gets an arrow on that edge, and the
  big view says so in a sentence. All tiles of a target share the frame, so sizes can be compared.
- **How to undo:** `REACH` in `site/lib/geo.ts`.

## 2. Edges are straight in longitude and latitude, and overlapping loops are read even-odd
- **Options:** A, let d3-geo draw rings as shapes on a sphere (it flips a ring wound the "wrong" way into
  "everything except this", which would repair or wreck drawings depending on winding) / B, read rings the way
  `002-grading.md` describes: add points along each straight edge, project each point, fill the flat result.
- **Choice:** B, so the picture is built the same way the score is. Within one polygon, rings are filled even-odd
  (a self-crossing outline shows its crossing); separate polygons are added together. An edge from 179° to -179° goes
  the long way round, as written. If the scorer settles these differently, the page should follow the scorer.
- **How to undo:** `plate()` in `site/lib/geo.ts`; `fillRule` in `site/app/strips.tsx`.

## 3. A failed drawing shows "no drawing" and a greyed 0.0%
- **Options:** A, no number at all (there is no picture for it to describe) / B, the 0.0 the file holds, greyed.
- **Choice:** B. The file says 0 and `002-grading.md` says a failed answer scores 0; hiding it would make a failed
  model look unscored instead of failed. The empty dashed frame is the picture of "nothing was drawn".
- **How to undo:** the `noDrawing` branches in `site/app/strips.tsx`.

## 4. The big view is a dialog over the page, and its slider covers the two baselines too
- **Options:** A, a permanent large panel above the strip (pushes the strip, which is the point of the page, below
  the fold) / B, a panel under the strip (a tap on a phone changes something off screen) / C, a dialog.
- **Choice:** C, the browser's own dialog: Esc closes it, focus stays inside it, focus returns to the tile last
  shown. The slider and the arrow keys walk the whole strip, rectangle and circle first, so one position means one
  tile everywhere.
- **How to undo:** the `<dialog>` in `site/app/strips.tsx`.

## 5. The modern country is drawn only where the tag is
- **Options:** A, never draw the foil (the tag "drew the modern country" cannot be checked by eye) / B, draw it on
  every history tile (a third outline on every small tile) / C, draw it dotted in the big view of a tagged tile.
- **Choice:** C: the claim gets its picture exactly where the claim is made.
- **How to undo:** the `foil` prop in `site/app/strips.tsx`.
