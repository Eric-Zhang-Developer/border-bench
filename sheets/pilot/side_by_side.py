"""One country, two large tiles side by side: Claude Sonnet 4.5 (the middle one of its three tries) and Claude
Fable 5.2 (its one try), both under prompt candidate C. A picture that explains itself on a phone.

  PYTHONPATH=. uv run python sheets/pilot/side_by_side.py TARGET_ID      -> sheets/pilot/side-by-side-TARGET_ID.png

The tiles are drawn by pipeline/sheet.py's own `tile` and scored by pipeline/score.py; this file only lays them out.
Model names and release dates come from sheets/pilot/model-names.json, which was read from the Models API.
"""

import json
import sys

import numpy as np
from PIL import Image, ImageDraw

from pipeline import sheet
from pipeline.score import ROOT, load_runs, load_target, median, projection, score_sample, to_metres
from pipeline.sheet import BORDER, INK, INVENTED, MISSED, MUTED, PAPER, RIGHT, font

OLD, NEW = "claude-sonnet-4-5-20250929", "claude-fable-5-2"
WIDTH, HEIGHT, SIDE, TOP = 1600, 900, 480, 204
MONTHS = "January February March April May June July August September October November December".split()


def main(target_id: str) -> None:
    target = load_target(ROOT / "targets" / target_id)
    names = json.loads((ROOT / "sheets/pilot/model-names.json").read_text())["models"]
    old_runs = load_runs(ROOT / "runs/archive", "pilot-c")[(OLD, target_id)]
    new_runs = load_runs(ROOT / "runs/pilot", "pilot-c")[(NEW, target_id)]
    old_samples = [score_sample(r["raw"], target) for r in old_runs]
    middle = median(old_samples)   # the scorer's own rule for which of three tries is shown
    shown = [(OLD, old_runs[middle], old_samples[middle], f"middle of {len(old_runs)} tries"),
             (NEW, new_runs[0], score_sample(new_runs[0]["raw"], target), "1 try")]

    # The same map and the same frame for both tiles, worked out the way pipeline/sheet.py does for a whole sheet.
    proj = projection(target["truth"])
    def metres(shape):
        return [[to_metres(proj, ring) for ring in polygon] for polygon in shape] if shape else None
    truth_m = metres(target["truth"])
    drawn_m = [metres(sample["shape"]) for _, _, sample, _ in shown]
    points = np.concatenate([r for polygon in truth_m for r in polygon])
    centre = (points.min(axis=0) + points.max(axis=0)) / 2
    def reach(shape_m):
        return np.abs(np.concatenate([r for polygon in shape_m for r in polygon]) - centre).max()
    half = min(max([reach(truth_m)] + [reach(d) for d in drawn_m if d]) * 1.08, reach(truth_m) * 1.5)

    page = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    pen = ImageDraw.Draw(page)
    left = (WIDTH - 2 * SIDE - 160) // 2
    title = target["name"][0].upper() + target["name"][1:]
    pen.text((left, 40), title, font=font(40 if len(title) < 50 else 30), fill=INK)
    pen.text((left, 96), "drawn from memory by two AI models", font=font(28), fill=MUTED)
    x = left
    for colour, label in ((RIGHT, "land the drawing got right"), (MISSED, "land it missed"), (INVENTED, "land it invented")):
        pen.rectangle([x, 152, x + 20, 172], fill=colour)
        pen.text((x + 30, 149), label, font=font(21), fill=INK)
        x += 30 + pen.textlength(label, font=font(21)) + 36
    pen.line([x, 162, x + 34, 162], fill=INK, width=3)
    pen.text((x + 44, 149), "the model's drawing", font=font(21), fill=INK)

    sheet.TILE = SIDE   # pipeline/sheet.py draws a tile at its module's size; ask it for a large one
    for i, ((model, run, sample, tries), drawing) in enumerate(zip(shown, drawn_m)):
        x = left + i * (SIDE + 160)
        page.paste(sheet.tile(truth_m, drawing, centre, half), (x, TOP))
        released = names[model]["created_at"]
        pen.text((x, TOP + SIDE + 14), names[model]["display_name"], font=font(30), fill=INK)
        pen.text((x, TOP + SIDE + 52), f"{sample['score']:.1f}%", font=font(64), fill=INK)
        seconds = f"{run['duration_ms'] / 1000:.0f} seconds" if run.get("duration_ms") else "time not recorded"
        for line, text in enumerate((f"released {MONTHS[int(released[5:7]) - 1]} {released[:4]}", tries,
                                     f"{seconds} · ${run['cost_usd']:.2f}")):
            pen.text((x + SIDE, TOP + SIDE + 52 + 27 * line), text, font=font(20), fill=MUTED, anchor="ra")
    pen.text((left, HEIGHT - 44), "The % is overlap: the area the drawing and the true border share, divided by the area "
             "either covers. Nothing in a drawing is repaired.", font=font(17), fill=MUTED)
    pen.text((left, HEIGHT - 22), "Both models got the same prompt (candidate C, not yet frozen), no tools and no web. "
             "The thin line is the true border.", font=font(17), fill=MUTED)
    out = ROOT / "sheets/pilot" / f"side-by-side-{target_id}.png"
    page.save(out)
    print(f"{out.relative_to(ROOT)}: " + ", ".join(f"{names[m]['display_name']} {s['score']}% ({t})" for m, _, s, t in shown))


if __name__ == "__main__":
    main(sys.argv[1])
