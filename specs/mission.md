# Mission

## Why
Most AI benchmarks report a number that goes up, and almost nobody can say what the number means. BorderBench asks
models to draw countries from memory and puts each drawing next to the real border, so progress is something a person
can see. The long form of the idea, with tiers and a paper, is Eric's pitch (not in this repo yet); this file covers
the MVP.

## Who
A curious person who does not read benchmark tables: a professor, a student, a history fan. They should be able to
look at one row of drawings and say whether the models got better.

## What
One static page. For each of six targets it shows a strip of drawings, one per Claude model in release order, each
laid over the true border with one percentage under it. The MVP exists to answer one question before anything else is
built: do the strips show progress?

## Non-negotiables
- **No number without its picture.** If a viewer cannot check a score with their own eyes, it does not go on the page.
- **Never invent data.** No coordinate, border, date, source or score is made up. A truth file with no named source
  does not merge. Unknown stays empty and visible.
- **The score is overlap %**: the area the drawing and the truth share, divided by the area either one covers, times
  100, measured on an equal-area grid. Truth against itself is 100. Two shapes that do not touch are 0.
- **Nothing is repaired.** Swapped coordinates, wrong signs, self-crossing outlines and stray pieces are scored as
  drawn. Closing a ring whose last point does not repeat its first is parsing, not repair.
- **One prompt, one slot.** Only `{target}` changes between calls. A frozen prompt file is never edited; a new prompt
  is a new id and a full rerun.
- **Models run as they ship**: no thinking, effort or sampling parameters, and no fallback model. A refusal or an
  empty answer is recorded as "no drawing".
- **Raw answers are committed unedited.** Every score rebuilds from committed files with no API call.
- **Spend stops at $60** for the MVP. The runner enforces it.
- **MIT covers the code only.** Each file under `targets/` keeps the licence of its source, named in its `SOURCE.md`.

## Not doing
- Other providers, tools, web access, structured output, or retries that ask a model to correct itself.
- Oracle ceilings, disputed-area masks, the foil-region score, average miss in km, compliance scores (all v1).
- Partition targets: Africa 1914, the German Confederation, the Holy Roman Empire (v1 and later).
- Polygon morphing, share images, per-model pages, a leaderboard table.
- Paradox map data, or any data we cannot redistribute.
