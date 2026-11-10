"""A contact sheet: every drawing for one target laid over the true border, with its score. For pull requests.

  uv run python -m pipeline.sheet RUNS PROMPT_ID TARGET_ID [--targets DIR] [--out FILE]
  uv run python -m pipeline.sheet runs/archive pilot-c usa        -> sheets/archive/pilot-c-usa.png
  uv run python -m pipeline.sheet runs/archive pilot-a,pilot-b,pilot-c usa       one row per model and prompt

The first row is the two baselines (rectangle, circle). Then one row per model, in release order, one tile per answer. In
each tile: grey is land the drawing got right, orange is land it missed, blue is land it invented, the dark line is
the drawing as the model wrote it, and the thin line is the true border. Every tile uses the same map and the same
scale, so tiles can be compared. Scores come from pipeline/score.py; this file only draws.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from pipeline.score import (ROOT, baselines, fill, load_runs, load_target, median, overlap, projection,
                            release_order, score_sample, to_metres)

PAPER, CARD, EDGE = "#FAF7F2", "#FFFFFF", "#E4DFD5"
RIGHT, MISSED, INVENTED = "#CFCAC0", "#E2622D", "#2B7BBB"   # the page reuses this pair: warm = missed, cool = invented
INK, BORDER, MUTED = "#1B1F27", "#8A8478", "#6B665C"
TILE, SHARP = 300, 3          # tile side in pixels; tiles are drawn SHARP times larger, then shrunk, for smooth edges
GAP, MARGIN, CAPTION = 24, 40, 100
COLUMNS = 3   # three samples per model; and about 1000 pixels wide, so a pull request shows it at full size


def rgb(colour: str) -> tuple[int, int, int]:
    return tuple(int(colour[i:i + 2], 16) for i in (1, 3, 5))


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.load_default(size=size)   # Pillow's built-in face: the same on every machine


def tile(truth_m, drawing_m, centre, half) -> Image.Image:
    """One square picture. Shapes are in metres on the target's map; the frame is centre ± half."""
    side = TILE * SHARP
    if drawing_m is None:   # "no drawing" is an empty tile, not a tile of missed land
        blank = Image.new("RGB", (TILE, TILE), CARD)
        pen = ImageDraw.Draw(blank)
        pen.text((TILE / 2, TILE / 2), "no drawing", font=font(18), fill=MUTED, anchor="mm")
        pen.rectangle([0, 0, TILE - 1, TILE - 1], outline=EDGE)
        return blank

    def cells(shape):
        return [[np.column_stack([r[:, 0] - (centre[0] - half), (centre[1] + half) - r[:, 1]]) * side / (2 * half)
                 for r in polygon] for polygon in shape]

    true_px, drawn_px = cells(truth_m), cells(drawing_m)
    true, drawn = fill(true_px, side, side), fill(drawn_px, side, side)
    picture = np.full((side, side, 3), rgb(CARD), dtype=np.uint8)
    picture[true & drawn] = rgb(RIGHT)
    picture[true & ~drawn] = rgb(MISSED)
    picture[drawn & ~true] = rgb(INVENTED)
    image = Image.fromarray(picture)
    pen = ImageDraw.Draw(image)
    for shape, colour, width in ((true_px, BORDER, SHARP), (drawn_px, INK, 2 * SHARP)):
        for polygon in shape:
            for ring in polygon:
                if len(ring) >= 2:
                    pen.line(ring.ravel().tolist(), fill=colour, width=width, joint="curve")
    image = image.resize((TILE, TILE), Image.LANCZOS)
    ImageDraw.Draw(image).rectangle([0, 0, TILE - 1, TILE - 1], outline=EDGE)
    return image


def sheet(target: dict, entries: list[dict], subtitle: str) -> Image.Image:
    """The whole sheet. Each entry: name, notes, score, shape (None for no drawing). A new name starts a new row."""
    proj = projection(target["truth"])

    def metres(shape):
        return [[to_metres(proj, ring) for ring in polygon] for polygon in shape]

    truth_m = metres(target["truth"])
    drawings = [metres(e["shape"]) if e["shape"] else None for e in entries]

    def reach(shape_m, centre):
        points = np.concatenate([r for polygon in shape_m for r in polygon] or [np.empty((0, 2))])
        return np.abs(points - centre).max() if len(points) else 0.0

    truth_points = np.concatenate([r for polygon in truth_m for r in polygon])
    centre = (truth_points.min(axis=0) + truth_points.max(axis=0)) / 2
    truth_half = reach(truth_m, centre)
    # One frame for every tile, so tiles can be compared: wide enough for every drawing, but never more than half
    # again as wide as the truth. A drawing that reaches further is cut at the edge and its caption says so.
    half = min(max([truth_half] + [reach(d, centre) for d in drawings if d]) * 1.08, truth_half * 1.5)

    places, row, column = [], 0, 0
    for i, entry in enumerate(entries):
        if i and (column == COLUMNS or entry["name"] != entries[i - 1]["name"]):
            row, column = row + 1, 0
        places.append((row, column))
        column += 1
    rows = row + 1
    header = 132
    width = 2 * MARGIN + COLUMNS * TILE + (COLUMNS - 1) * GAP
    height = header + rows * (TILE + CAPTION) + (rows - 1) * GAP + 2 * MARGIN
    page = Image.new("RGB", (width, height), PAPER)
    pen = ImageDraw.Draw(page)

    pen.text((MARGIN, MARGIN - 6), target["name"], font=font(28), fill=INK)
    pen.text((MARGIN, MARGIN + 34), subtitle, font=font(15), fill=MUTED)
    x, y = MARGIN, MARGIN + 66
    for colour, label in ((RIGHT, "land the drawing got right"), (MISSED, "land it missed"),
                          (INVENTED, "land it invented")):
        pen.rectangle([x, y + 2, x + 14, y + 16], fill=colour)
        pen.text((x + 22, y), label, font=font(15), fill=INK)
        x += 22 + pen.textlength(label, font=font(15)) + 28
    pen.line([x, y + 9, x + 26, y + 9], fill=INK, width=2)
    pen.text((x + 34, y), "the drawing", font=font(15), fill=INK)
    x += 34 + pen.textlength("the drawing", font=font(15)) + 28
    pen.line([x, y + 9, x + 26, y + 9], fill=BORDER, width=1)
    pen.text((x + 34, y), "the true border", font=font(15), fill=INK)

    for entry, drawing, (row, column) in zip(entries, drawings, places):
        x = MARGIN + column * (TILE + GAP)
        y = header + MARGIN + row * (TILE + CAPTION + GAP)
        page.paste(tile(truth_m, drawing, centre, half), (x, y))
        notes = entry["notes"] + (["runs off the frame"] if drawing and reach(drawing, centre) > half else [])
        lines = [""]
        for note in notes:   # as many notes on a line as fit under the tile
            joined = f"{lines[-1]} · {note}" if lines[-1] else note
            if pen.textlength(joined, font=font(13)) <= TILE:
                lines[-1] = joined
            else:
                lines.append(note)
        pen.text((x, y + TILE + 8), entry["name"], font=font(15), fill=INK)
        pen.text((x, y + TILE + 28), f"{entry['score']:.1f}%", font=font(24), fill=INK)
        pen.multiline_text((x, y + TILE + 62), "\n".join(lines), font=font(13), fill=MUTED, spacing=5)
    pen.text((MARGIN, height - MARGIN + 6),
             "Overlap % = the area drawing and truth share, divided by the area either covers, on an equal-area map. "
             "Nothing in a drawing is repaired.", font=font(13), fill=MUTED)
    return page


def entries_for(target: dict, by_prompt: dict[str, dict]) -> list[dict]:
    """The baselines, then every sample of every model that drew this target: models in release order, and under
    each model one row per prompt when several prompts are compared."""
    out = [{"name": "Baseline", "notes": [note], "score": round(overlap(shape, target["truth"]), 1), "shape": shape}
           for (_, _, shape), note in zip(baselines(target["truth"]), (
               "rectangle: the true border's bounding box", "circle: the true area around the true centre"))]
    everyone = {pair: runs for by_pair in by_prompt.values() for pair, runs in by_pair.items()}
    rows = [(model, prompt_id) for model, _ in release_order(everyone) for prompt_id in by_prompt]
    for model, prompt_id in rows:
        runs = by_prompt[prompt_id].get((model, target["id"]), [])
        samples = [score_sample(run.get("raw"), target) for run in runs]
        name = model if len(by_prompt) == 1 else f"{model} · {prompt_id}"
        for i, sample in enumerate(samples):
            notes = [f"sample {i + 1} of {len(samples)}"]
            if len(samples) > 1 and i == median(samples):
                notes.append("the median sample")
            if sample["flags"]["over_400_points"]:
                notes.append(f"{sample['points']} points, over 400")
            if sample["flags"]["drew_modern"]:
                notes.append("drew the modern country")
            out.append({"name": name, "notes": notes, "score": sample["score"], "shape": sample["shape"]})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", type=Path, help="a run set, e.g. runs/archive")
    ap.add_argument("prompt_id", help="e.g. pilot-c, or several to compare: pilot-a,pilot-b,pilot-c")
    ap.add_argument("target_id", help="a folder name under targets/, e.g. usa")
    ap.add_argument("--targets", type=Path, default=ROOT / "targets")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)

    target = load_target(args.targets / args.target_id)
    prompt_ids = args.prompt_id.split(",")
    entries = entries_for(target, {p: load_runs(args.runs, p) for p in prompt_ids})
    drawings = len(entries) - 2
    if not drawings:
        print(f"sheet: no answers for {args.target_id} under {args.runs} for {args.prompt_id}; the sheet shows "
              f"the baselines only")
    out = args.out or ROOT / "sheets" / args.runs.name / f"{'+'.join(prompt_ids)}-{args.target_id}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    subtitle = (f"{args.runs.name} / {', '.join(prompt_ids)} · {drawings} drawing{'' if drawings == 1 else 's'} "
                f"from memory")
    sheet(target, entries, subtitle).save(out)
    print(f"sheet: wrote {out} ({drawings} drawings and 2 baselines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
