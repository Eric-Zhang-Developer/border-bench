# 002: Grading

- Date: 2026-11-09   Decided by: Eric and Claude   Feature: scorer

## Context
Eric, 2026-11-09: "I think it would just be a simple percentage." And: "the core thing I'm trying to get at, really
is legibility." A viewer must be able to check a score by looking.

## Options
- **Overlap %** (intersection over union). The number is the picture: the shaded mismatch is the missing percent.
- **Shape skill**, (model − floor) ÷ (ceiling − floor). More defensible in a paper, but a ratio nobody can see.
- **Average miss in km.** Very readable, and kinder to thin countries, but needs more scorer code.

## Choice
**Overlap % is the only score in the MVP.** The rectangle and the circle are drawn and scored as the first two tiles
of every strip, so the baseline is a picture too. Shape skill moves to the paper; miss in km is the first v1 addition.

## How it is computed
1. Parse the answer: take the last ```geojson block, or failing that the last valid JSON value that holds
   coordinates. Accept Polygon, MultiPolygon, FeatureCollection or bare coordinate arrays. Close open rings.
2. Add a point at least every 0.1° along each edge. A long straight edge then follows its parallel instead of cutting
   a chord once projected (about 95 km of error on the USA's northern border otherwise).
3. Project drawing and truth to an equal-area projection centred on the truth.
4. Rasterize both onto one 2048-pixel grid that covers both shapes.
5. Count pixels: shared ÷ covered by either.

## Rules
- Nothing is repaired (see `mission.md`).
- An answer that cannot be parsed scores 0 and shows as an empty tile labelled "no drawing".
- More than 400 points is scored as drawn and flagged.
- With three samples the page shows the median sample and its score, with the other two scores beside it.
- A model's overall number is the plain average of its six target scores.
- History targets get one tag and no extra number: "drew the modern country", when the drawing overlaps the foil more
  than it overlaps the truth.

## Known weakness
Overlap % is harsh on thin shapes. Chile averages about 180 km wide, so a 50 km sideways shift removes much of the
overlap. The page will show this honestly; miss in km is the fix.

## How to undo
Scores are rebuilt from committed raw answers, so any change to grading is a rerun of `score.py`, not of the models.
A change to grading after the page is public is a one-way door: file it for Eric.
