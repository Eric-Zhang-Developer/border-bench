"""An experiment, not a score: Claude Fable 5.2 drawing one country with the frozen 400-point limit and with a
1000-point limit, side by side, each beside the best score that many points can reach.

  PYTHONPATH=. uv run python sheets/pilot/points_1000.py TARGET_ID      -> sheets/pilot/points-1000-TARGET_ID.png

"Best possible" is measured, not known: the true border itself is thinned to that many points (its largest pieces,
2 decimal places, as the prompt asks) and scored. A cleverer thinning could score a little higher, so it reads
"at least". The tiles are drawn by pipeline/sheet.py and scored by pipeline/score.py.
"""

import sys

import numpy as np
import shapely
from PIL import Image, ImageDraw

from pipeline import sheet
from pipeline.score import ROOT, load_runs, load_target, overlap, projection, score_sample, to_metres
from pipeline.sheet import INK, INVENTED, MISSED, MUTED, PAPER, RIGHT, font

MODEL = "claude-fable-5-2"
ARMS = ((400, "runs/p1", "p1", "the benchmark's limit"), (1000, "runs/pilot", "pilot-c-1000", "experiment"))
WIDTH, HEIGHT, SIDE, TOP = 1600, 900, 480, 204
PIECES = (1, 2, 3, 5, 8, 12, 20, 30, 50, 80)   # how many of the largest pieces to keep; the best one wins


def thinned(parts, limit: int) -> list:
    """These pieces of the true border, thinned just enough to hold at most `limit` points in total."""
    def rings(tolerance):
        return [[[round(x, 2), round(y, 2)] for x, y in g.exterior.coords]
                for part in parts for g in getattr(part.simplify(tolerance), "geoms", [part.simplify(tolerance)])]
    low, high = 0.0, 5.0
    for _ in range(40):
        mid = (low + high) / 2
        low, high = (low, mid) if sum(len(r) for r in rings(mid)) <= limit else (mid, high)
    return [[r] for r in rings(high) if len(r) >= 4]


def best_possible(truth, limit: int) -> float:
    parts = sorted((shapely.Polygon(p[0]) for p in truth), key=lambda g: -g.area)
    return max(overlap(thinned(parts[:k], limit), truth) for k in PIECES if k <= max(len(parts), 1))


def main(target_id: str) -> None:
    target = load_target(ROOT / "targets" / target_id)
    shown = []
    for limit, runs, prompt_id, note in ARMS:
        run = load_runs(ROOT / runs, prompt_id)[(MODEL, target_id)][0]
        shown.append((limit, note, run, score_sample(run["raw"], target), best_possible(target["truth"], limit)))

    proj = projection(target["truth"])
    def metres(shape):
        return [[to_metres(proj, ring) for ring in polygon] for polygon in shape] if shape else None
    truth_m = metres(target["truth"])
    drawn_m = [metres(sample["shape"]) for _, _, _, sample, _ in shown]
    points = np.concatenate([r for polygon in truth_m for r in polygon])
    centre = (points.min(axis=0) + points.max(axis=0)) / 2
    def reach(shape_m):
        return np.abs(np.concatenate([r for polygon in shape_m for r in polygon]) - centre).max()
    half = min(max([reach(truth_m)] + [reach(d) for d in drawn_m if d]) * 1.08, reach(truth_m) * 1.5)

    page = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    pen = ImageDraw.Draw(page)
    left = (WIDTH - 2 * SIDE - 160) // 2
    pen.text((left, 40), target["name"][0].upper() + target["name"][1:], font=font(40), fill=INK)
    pen.text((left, 96), f"drawn from memory by {shown[0][2]['model_display_name']}: does a higher point limit help?",
             font=font(28), fill=MUTED)
    x = left
    for colour, label in ((RIGHT, "land the drawing got right"), (MISSED, "land it missed"), (INVENTED, "land it invented")):
        pen.rectangle([x, 152, x + 20, 172], fill=colour)
        pen.text((x + 30, 149), label, font=font(21), fill=INK)
        x += 30 + pen.textlength(label, font=font(21)) + 36
    pen.line([x, 162, x + 34, 162], fill=INK, width=3)
    pen.text((x + 44, 149), "the model's drawing", font=font(21), fill=INK)

    sheet.TILE = SIDE   # pipeline/sheet.py draws a tile at its module's size; ask it for a large one
    for i, ((limit, note, run, sample, best), drawing) in enumerate(zip(shown, drawn_m)):
        x = left + i * (SIDE + 160)
        page.paste(sheet.tile(truth_m, drawing, centre, half), (x, TOP))
        pen.text((x, TOP + SIDE + 14), f"At most {limit} points ({note})", font=font(30), fill=INK)
        pen.text((x, TOP + SIDE + 52), f"{sample['score']:.1f}%", font=font(64), fill=INK)
        pieces = len(sample["shape"] or [])
        for line, text in enumerate((f"drew {sample['points']} points in {pieces} pieces",
                                     f"best possible: at least {best:.1f}%",
                                     f"{run['duration_ms'] / 1000:.0f} seconds · ${run['cost_usd']:.2f}")):
            pen.text((x + SIDE, TOP + SIDE + 52 + 27 * line), text, font=font(20), fill=MUTED, anchor="ra")
    pen.text((left, HEIGHT - 44), "One try each. Only the 400-point drawing is a benchmark score; the other prompt differs "
             "in that one number. The thin line is the true border.", font=font(17), fill=MUTED)
    pen.text((left, HEIGHT - 22), "Best possible: the true border itself, thinned to that many points and scored the "
             "same way. The % is overlap; nothing is repaired.", font=font(17), fill=MUTED)
    out = ROOT / "sheets/pilot" / f"points-1000-{target_id}.png"
    page.save(out)
    print(f"{out.relative_to(ROOT)}: " + "; ".join(
        f"limit {limit}: {s['score']}% with {s['points']} points, best possible at least {b:.1f}%, ${r['cost_usd']:.2f}"
        for limit, _, r, s, b in shown))


if __name__ == "__main__":
    main(sys.argv[1])
