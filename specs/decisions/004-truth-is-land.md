# 004: A true border is the outline of the land

- Date: 2026-11-09   Decided by: the maintainer (the reference was wrong), the session lead (the lake rule), the
  agent `eric-3` (the four smaller calls below)   Feature: truth-modern
- Replaces the choice in `truth-modern-scale-and-lakes.md` (keep the 1:50m map, lakes filled in). Settles issue 14 as
  its option C.

## Context
The prompt says "Draw land only." The first true borders counted the United States' side of the Great Lakes as
territory. Claude Fable 5.2 then drew the United States with the lake shores traced, scored 97.1%, and the only land
the picture marked as missed was the lakes. The better drawing was being marked down by the reference.

Maintainer, 2026-11-09, on seeing that picture: "it's us that's wrong the reference cause you see the great lakes".

## Choice
- **Source.** The four modern borders are cut from Natural Earth's 1:10 million countries file instead of its 1:50
  million one, and lakes are cut out with Natural Earth's 1:10 million lakes file. Both are public domain. The
  maintainer approved the two downloads in chat on 2026-11-09.
- **The lake rule** (the session lead's call, in the lead's words): "A true border is the outline of the land. Cut
  out every lake that is connected by water to the country's edge: a lake the border runs through, plus any lake
  joined to one (Lake Michigan is joined to Lake Huron). Leave fully interior lakes in (Great Salt Lake, say): an
  outline cannot leave them out without drawing holes, and the prompt does not ask for holes."
- **Unchanged.** `usa` is the lower 48 states. `chile` has no Antarctic claim and keeps Easter Island (a separate
  question). Names and dates are the same.
- It is one named, repeatable step, `cut_edge_lakes` in `pipeline/prep.py`, with a test on made-up shapes in
  `pipeline/test_prep.py`. No lake is named in the code: Lake Michigan is cut because the rule cuts it.

## How the code reads the rule (the agent's calls)
1. **"A lake"** is one outline in the lakes file. **"Reaches the edge"** means the outline is not wholly inside the
   country: the border runs through it, or it touches the border or the coast. **"Joined"** means two lake outlines
   touch. In these four countries every lake that was cut is on a land border or joined to one; no lake was cut for
   touching a coast.
2. **A lake is cut whole**, however little of it lies across the border. Lake Champlain is cut from the United
   States although 1,171 of its 1,249 km² are inside.
3. **Two of the file's 1,355 lake outlines cross themselves** (one in northern Canada, one in Siberia) and are left
   out. The build stops if a broken outline ever lies near a target.
4. **Croatia's published land area** was missing. It is now the World Bank's figure (55,960 km² for 2023, indicator
   AG.LND.TOTL.K2, which takes it from the FAO).

## What it did (measured by `pipeline/prep.py`)
| Country | Lakes cut | Area removed | Area, old border → new border | Against the published land area, old → new |
|---|---|---|---|---|
| United States (lower 48) | 16 | 158,579 km² | 7,940,194 → 7,783,469 km² | +3.6% → +1.6% |
| Chile | 3 | 1,618 km² | 737,680 → 734,975 km² | -0.8% → -1.2% |
| Indonesia | 0 | 0 | 1,863,915 → 1,879,827 km² | +2.9% → +3.8% |
| Croatia | 0 | 0 | 54,541 → 55,023 km² | -2.5% → -1.7% |

The lakes cut are listed by name in each target's `SOURCE.md`. Lake Michigan lies wholly inside the United States and
is cut because its outline shares a line with Lake Huron's at the Straits of Mackinac.

## Known weaknesses
- **Indonesia still misses the 2% check** against the figure in the repo (1,811,569 km², uncited on Wikipedia). No
  lake reaches its edge, so the lake rule does not touch it; the finer map has more islands and moved it further
  away. Against the World Bank's land figure (1,892,410 km² for 2023) it is -0.7%. Which figure is the right
  yardstick is open; the check is reported as missed, not loosened.
- **The rule follows the lakes file, not the ground.** Lago Argentino is cut from Chile because its outline in the
  file crosses the border line by 6 km²; that lake is usually mapped wholly inside Argentina. Rivers are not in the lakes file
  (one stretch, the St. Marys River, is), so river mouths and the rivers between the Great Lakes stay as land.
- **Lakes wholly inside stay in**: 97 in the United States (30,590 km², the largest the Great Salt Lake at 4,115
  km²), 5 in Chile, 3 in Indonesia. A model that draws around one is marked down a little.
- **The history targets' modern foils** (Germany, Poland) are still cut from the 1:50 million file with lakes filled
  in. In the lakes file Germany's border runs through Lake Constance and Poland's through the Vistula Lagoon. Not
  decided here.

## How to undo
Revert the pull request that added this file: `pipeline/prep.py` then rebuilds the old borders from the 1:50 million
file. Every score changes with the border (table in the pull request), so once the page is public this is a one-way
door.
