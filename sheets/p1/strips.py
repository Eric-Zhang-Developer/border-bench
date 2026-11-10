"""One compact picture per target: the two baselines, then the drawing each model is shown by, in release order.

  PYTHONPATH=. uv run python sheets/p1/strips.py        -> sheets/p1/strip-<target>.png

The contact sheets (p1-<target>.png) show every try and are very tall with fourteen models. This is the same
strip the page shows: for a model with three tries, the middle-scoring one. Scores and tiles come from
pipeline/score.py and pipeline/sheet.py; this file only arranges them. Names and dates are the Models API's, as
saved in each run file.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from pipeline.score import ROOT, baselines, load_runs, load_target, median, overlap, projection, release_order, \
    score_sample, to_metres
from pipeline.sheet import GAP, INK, MARGIN, MUTED, PAPER, TILE, font, tile

COLUMNS, CAPTION, HEADER = 4, 96, 70


def strip(target: dict, by_pair: dict) -> Image.Image:
    entries = [{"name": label, "when": "baseline", "score": round(overlap(shape, target["truth"]), 1),
                "shape": shape, "note": ""} for _, label, shape in baselines(target["truth"])]
    for model, released in release_order(by_pair):
        runs = by_pair.get((model, target["id"]), [])
        samples = [score_sample(run.get("raw"), target) for run in runs]
        shown = samples[median(samples)]
        note = ("one try" if len(samples) == 1 else
                "middle of " + ", ".join(f"{s['score']:.1f}" for s in samples))
        entries.append({"name": runs[0]["model_display_name"], "when": released, "score": shown["score"],
                        "shape": shown["shape"], "note": note})

    proj = projection(target["truth"])
    metres = lambda shape: [[to_metres(proj, ring) for ring in polygon] for polygon in shape]  # noqa: E731
    truth_m = metres(target["truth"])
    drawings = [metres(e["shape"]) if e["shape"] else None for e in entries]
    points = np.concatenate([r for polygon in truth_m for r in polygon])
    centre = (points.min(axis=0) + points.max(axis=0)) / 2
    reach = lambda shape: max(np.abs(r - centre).max() for polygon in shape for r in polygon)  # noqa: E731
    # The contact sheet's frame rule: one frame for every tile, never more than half again as wide as the truth.
    half = min(max([reach(truth_m)] + [reach(d) for d in drawings if d]) * 1.08, reach(truth_m) * 1.5)

    rows = -(-len(entries) // COLUMNS)
    width = 2 * MARGIN + COLUMNS * TILE + (COLUMNS - 1) * GAP
    page = Image.new("RGB", (width, HEADER + rows * (TILE + CAPTION + GAP) + MARGIN), PAPER)
    pen = ImageDraw.Draw(page)
    pen.text((MARGIN, MARGIN - 10), target["name"], font=font(26), fill=INK)
    pen.text((MARGIN, MARGIN + 24), "overlap %, oldest model first · grey: right · orange: missed · blue: invented",
             font=font(14), fill=MUTED)
    for i, (entry, drawing) in enumerate(zip(entries, drawings)):
        x = MARGIN + (i % COLUMNS) * (TILE + GAP)
        y = HEADER + MARGIN + (i // COLUMNS) * (TILE + CAPTION + GAP)
        page.paste(tile(truth_m, drawing, centre, half), (x, y))
        pen.text((x, y + TILE + 6), f"{entry['name']} · {entry['when']}", font=font(14), fill=INK)
        pen.text((x, y + TILE + 26), f"{entry['score']:.1f}%", font=font(24), fill=INK)
        pen.text((x, y + TILE + 60), entry["note"], font=font(13), fill=MUTED)
    return page


if __name__ == "__main__":
    by_pair = load_runs(ROOT / "runs" / "p1", "p1")
    for folder in sorted((ROOT / "targets").iterdir()):
        if (folder / "target.toml").exists():
            out = Path(__file__).parent / f"strip-{folder.name}.png"
            strip(load_target(folder), by_pair).save(out)
            print(f"strips: wrote {out.relative_to(ROOT)}")
