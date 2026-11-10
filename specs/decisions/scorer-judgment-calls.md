# scorer: the calls the grading rules left open

- Date: 2026-11-09   Decided by: the agent (`eric-3`)   Feature: scorer
- **Context:** `specs/decisions/002-grading.md` fixes the score (overlap %, points every 0.1°, an equal-area map, one
  2048 grid, nothing repaired). Writing the code forced eleven smaller choices it does not name. Each one below took
  the option that changes the drawing least and can be undone by rerunning `pipeline/score.py`: no model is called
  again. None of them is public yet, so none is a one-way door today. All of them become one when the page ships.
- **How to undo (all of them):** change the line named, rerun `uv run python -m pipeline.score`, and say so under
  "Does any score change?" in that pull request.

| # | Question | Choice | Turned down, and why | Where |
|---|---|---|---|---|
| 1 | What counts as inside an outline that crosses itself, or a polygon with holes? | A grid cell is land when its centre is inside an **odd** number of one polygon's rings. Separate polygons add up. The doubly wrapped part of a self-crossing outline is therefore empty, and a hole is a hole. Pinned by a test (a bow tie scores 50.0, a twice-wrapped outline 66.7). | Repairing the outline first (forbidden). The drawing library's own fill: measured here, it fills a 10 × 10 square as 121 cells (it fattens every edge), and its rule for crossings is not documented, so a library update could move scores silently. | `fill` in `pipeline/score.py` |
| 2 | A latitude beyond ±90 (a model that writes latitude first for the USA produces −124). | Read it as the trigonometry does: past the pole and down the other side. The drawing lands far away and scores as drawn, usually 0. | Clamping to ±90 (a repair). Calling it "no drawing" (it is a drawing; the rule says swapped coordinates are scored as drawn). | `to_metres` |
| 3 | What exactly are the rectangle and the circle? | Rectangle: the truth's bounding box in longitude and latitude. Circle: the truth's area, centred on its centre of area, measured on the equal-area map. From the pitch: "the true bounding box, and a correctly sized circle at the true centroid." | An inscribed or enclosing circle: neither is "correctly sized". | `baselines` |
| 4 | Which sample is "the median" when there are two, or a tie? | Two samples: the lower one. Equal scores: the earliest sample. | Averaging two samples: the page must show one real drawing, not a number with no picture. | `median` |
| 5 | "Overlaps the foil more than it overlaps the truth": measured how? | By the same overlap %: the tag is set when the drawing's overlap % against the modern foil is higher than against the truth. | Raw shared area: a drawing that covers everything would then be tagged by whichever shape is bigger. | `score_sample` |
| 6 | Which answers can be read? | Polygon, MultiPolygon, FeatureCollection and bare arrays as the rule says, plus a single Feature (a FeatureCollection is made of them). A Polygon or MultiPolygon is read by how deep its brackets nest, not by which of the two names it carries, because the same array would be accepted bare. A ring needs three points. A line or a point is not a drawing. | Rejecting a MultiPolygon mislabelled "Polygon": that would score a naming slip as zero knowledge. | `polygons` in `pipeline/parse.py` |
| 7 | An answer cut off mid-way (the model hit its length limit). | The rule is applied as written: the last complete JSON value that holds coordinates. A cut-off MultiPolygon whose first pieces are complete is therefore scored on those pieces; one with no complete ring is "no drawing". | Treating every cut-off answer as "no drawing": simpler, but it is not what the rule says. Flagged for the maintainer below. | `_json_values` |
| 8 | Which equal-area map, centred where? | Lambert azimuthal equal-area on the WGS84 ellipsoid, centred on the middle of the truth's bounding box. The grid has 2048 cells on its longer side. | A sphere (areas off by about 1%, by a different amount at each latitude). Centring on the centre of area (needs a map before there is a map). | `projection`, `overlap` |
| 9 | Outlines in `results.json`. | Every outline gets a point at least every 1°, because the page's map library bends longer edges into great-circle arcs, which is not what was scored. The truth and foil are thinned by 0.02° (about 2 km); a model's drawing is never thinned. Numbers have 4 decimals. Scores always come from the full shapes. | Writing drawings exactly as parsed: a two-point edge along the 49th parallel across 28° would be drawn up to 84 km away from where it was scored (measured in the test). | `display` |
| 10 | Numbers that are not degrees (a model answering in metres). | Scored as drawn. An edge is cut into at most 3600 pieces (enough to go all the way round the globe), so a wild number cannot stall the run. A point with no place on the map is left out. | Refusing the answer: any cut-off value for "not a coordinate" would be invented. | `densify`, `to_metres` |
| 11 | Fields of `results.json` the inputs do not hold. | `models[].label` is the model id. `targets[].source` is read from an optional `[source]` table in `target.toml` and is empty strings without one. `models[].released` is `""` when there is no release date. Targets are listed by folder name. A model with no answer for a target gets no tile there, and `pipeline/verify.py` reports the gap. | Deriving a display name from the id, or copying a licence out of `SOURCE.md` by pattern: both are guesses. Filed as a `needs-human` issue. | `build`, `load_target` |

## For the maintainer
- **#7 is the one most worth a look.** If you would rather a cut-off answer always count as "no drawing", it is a
  three-line change before any real score exists.
- **#1 and #5** decide visible things (a tile's filled area, the "drew the modern country" tag). Both are shown on
  the synthetic contact sheets in the scorer pull request.

## What the first real answers showed (2026-11-10, Claude Sonnet 4.5's archive)
- **#7:** no archived answer is cut off, but 8 of the 99 are broken by a bracket slip or by typographic minus signs,
  and the rule as written scores each on its last complete piece only (one Australia drawing would be scored as
  Tasmania alone). None of the 8 is on a target that can be scored yet. Open as issue #27.
- **#1:** on the 36 drawings scored so far the even-odd rule and the non-zero rule agree to within a point on 32.
  The largest gap is one USA drawing of 2,603 points that goes round the country several times: 36.6 as scored,
  80.2 under non-zero (measured in a one-off experiment, not by code in the repo). Open as issue #28.
- **#8:** on the three drawings that are valid shapes and were checked, the grid agrees with exact polygon geometry
  to 0.01 of a point (93.73 against 93.74, 94.53 against 94.53, 37.14 against 37.15).
