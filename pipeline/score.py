"""Overlap % for every drawing, the two baselines, and results/results.json. Reads runs/ and targets/ only.

  uv run python -m pipeline.score [RUNS] [PROMPT_ID] [--targets DIR] [--out FILE]     defaults: runs/p1  p1

How a score is computed (specs/decisions/002-grading.md), with nothing repaired on the way:
1. A point is added at least every 0.1 degrees along each edge, in longitude and latitude, so a long edge along a
   parallel still follows the parallel once the map is flattened.
2. Drawing and truth go onto one equal-area map centred on the truth.
3. Both are filled onto one grid, 2048 cells on its longer side, that covers both shapes. A cell is land when its
   centre is inside an odd number of a polygon's rings (so holes are holes, and where an outline crosses itself the
   doubly wrapped part is empty). Separate polygons add up.
4. Score = cells in both / cells in either, times 100.

A shape is MultiPolygon coordinates: a list of polygons, each a list of rings, each a list of [lon, lat].
The file written has exactly the shape of specs/features/scorer/results.example.json.
"""

import argparse
import json
import sys
import tomllib
from math import pi, sqrt
from pathlib import Path

import numpy as np
import pyproj
import shapely

from pipeline.parse import parse, polygons

ROOT = Path(__file__).resolve().parent.parent
STEP = 0.1            # degrees between added points when scoring
GRID = 2048           # cells on the longer side of the scoring grid
MAX_POINTS = 400      # more than this is scored as drawn, and flagged
DISPLAY_STEP = 1.0    # degrees between added points in the outlines the page draws
DISPLAY_TOLERANCE = 0.02   # degrees (about 2 km) of simplification for the truth and foil outlines on the page
ABOUT = ("Written by pipeline/score.py from the answers in runs/ and the true borders in targets/. "
         "Rebuild it with that script; do not edit it by hand.")
SETTINGS_NOTE = "Each model ran with its default settings."


def densify(ring, step: float = STEP) -> np.ndarray:
    """The ring with points added so no edge spans more than `step` degrees of longitude or latitude."""
    a = np.asarray(ring, dtype=float).reshape(-1, 2)
    if len(a) < 2:
        return a
    span = np.abs(np.diff(a, axis=0)).max(axis=1)
    # 3600 pieces carry an edge all the way round the globe; the cap only bites on numbers that are not degrees.
    pieces = np.clip(np.ceil(span / step), 1, 3600).astype(int)
    edge = np.repeat(np.arange(len(pieces)), pieces)
    along = (np.arange(pieces.sum()) - np.repeat(np.cumsum(pieces) - pieces, pieces)) / pieces[edge]
    return np.vstack([a[edge] + (a[edge + 1] - a[edge]) * along[:, None], a[-1:]])


def projection(shape) -> pyproj.Proj:
    """An equal-area map (Lambert azimuthal, WGS84) centred on the middle of the shape's bounding box."""
    points = np.concatenate([np.asarray(ring, dtype=float) for polygon in shape for ring in polygon])
    lon, lat = (points.min(axis=0) + points.max(axis=0)) / 2
    return pyproj.Proj(proj="laea", lon_0=lon, lat_0=lat, ellps="WGS84")


def to_metres(proj: pyproj.Proj, ring, step: float = STEP) -> np.ndarray:
    """The densified ring on the equal-area map. A latitude past a pole comes down the other side, as the
    trigonometry says, rather than being clamped or dropped; a point with no place on the map (the exact far side
    of the globe) is left out."""
    lon, lat = densify(ring, step).T
    over_the_pole = np.cos(np.radians(lat)) < 0
    lat = np.where(np.abs(lat) > 90, np.degrees(np.arcsin(np.sin(np.radians(lat)))), lat)
    xy = np.column_stack(proj(lon + 180 * over_the_pole, lat))
    return xy[np.isfinite(xy).all(axis=1)]


def fill(shape_px, width: int, height: int) -> np.ndarray:
    """Which cells of a width x height grid are inside the shape, tested at each cell's centre.

    Even-odd within a polygon, union across polygons. Rings are arrays of [x, y] in cell units. Each edge flips one
    flag per row it crosses, at the first cell whose centre lies to its right; a running count along the row then
    says inside or outside. Parts of the shape outside the grid are cut off."""
    inside = np.zeros((height, width + 1), dtype=bool)
    for polygon in shape_px:
        rings = [r for r in polygon if len(r) >= 2]
        if not rings:
            continue
        a = np.concatenate([r[:-1] for r in rings])
        b = np.concatenate([r[1:] for r in rings])
        first = np.ceil(np.minimum(a[:, 1], b[:, 1]) - 0.5).astype(int)
        rows = np.ceil(np.maximum(a[:, 1], b[:, 1]) - 0.5).astype(int) - first   # rows whose centre the edge crosses
        edge = np.repeat(np.arange(len(rows)), rows)
        row = first[edge] + np.arange(rows.sum()) - np.repeat(np.cumsum(rows) - rows, rows)
        on_grid = (row >= 0) & (row < height)
        edge, row = edge[on_grid], row[on_grid]
        if not len(row):
            continue
        x = a[edge, 0] + (row + 0.5 - a[edge, 1]) * (b[edge, 0] - a[edge, 0]) / (b[edge, 1] - a[edge, 1])
        col = np.clip(np.ceil(x - 0.5), 0, width).astype(int)
        top, left = row.min(), col.min()
        h, w = row.max() - top + 1, col.max() - left + 1
        flips = np.bincount((row - top) * w + (col - left), minlength=h * w).reshape(h, w)
        inside[top:top + h, left:left + w] |= np.cumsum(flips, axis=1) % 2 == 1
    return inside[:, :width]


def overlap(drawing, truth, grid: int = GRID) -> float:
    """Overlap %: the area the two shapes share, divided by the area either covers, times 100. Not rounded."""
    proj = projection(truth)
    a, b = ([[to_metres(proj, ring) for ring in polygon] for polygon in shape] for shape in (drawing, truth))
    points = np.concatenate([ring for shape in (a, b) for polygon in shape for ring in polygon])
    low, size = points.min(axis=0), np.ptp(points, axis=0)
    cell = size.max() / grid
    if not cell > 0:
        return 0.0
    width, height = np.maximum(np.ceil(size / cell).astype(int), 1)
    drawn, true = (fill([[(ring - low) / cell for ring in polygon] for polygon in shape], width, height)
                   for shape in (a, b))
    either = np.count_nonzero(drawn | true)
    return 100.0 * int(np.count_nonzero(drawn & true)) / int(either) if either else 0.0


def baselines(truth) -> list[tuple[str, str, list]]:
    """The two shapes anyone could draw knowing only where the country is and how big: its bounding box in
    longitude and latitude, and a circle with its area around its centre of area."""
    points = np.concatenate([np.asarray(ring, dtype=float) for polygon in truth for ring in polygon])
    (west, south), (east, north) = points.min(axis=0), points.max(axis=0)
    rectangle = [[[[west, south], [east, south], [east, north], [west, north], [west, south]]]]

    proj = projection(truth)
    flat = [[to_metres(proj, ring) for ring in polygon] for polygon in truth]
    land = shapely.MultiPolygon([shapely.Polygon(rings[0], rings[1:]) for rings in flat])
    turn = np.radians(np.arange(360))
    radius = sqrt(land.area / pi)
    lon, lat = proj(land.centroid.x + radius * np.cos(turn), land.centroid.y + radius * np.sin(turn), inverse=True)
    ring = np.column_stack([lon, lat]).tolist()
    circle = [[ring + [ring[0]]]]
    return [("rectangle", "Rectangle", rectangle), ("circle", "Circle", circle)]


def display(shape, tolerance: float = 0.0) -> dict:
    """The shape as the page draws it: a GeoJSON MultiPolygon with a point at least every degree (the page's map
    library bends longer edges into great-circle arcs, which is not what was scored), to 4 decimal places.
    `tolerance` thins a detailed true border; a model's drawing is never thinned."""
    if tolerance:
        thinned = shapely.MultiPolygon([shapely.Polygon(p[0], p[1:]) for p in shape]).simplify(tolerance)
        shape = [[list(g.exterior.coords), *(list(hole.coords) for hole in g.interiors)]
                 for g in getattr(thinned, "geoms", [thinned]) if not g.is_empty]
    return {"type": "MultiPolygon",
            "coordinates": [[np.round(densify(ring, DISPLAY_STEP), 4).tolist() for ring in polygon]
                            for polygon in shape]}


def load_shape(path: Path) -> list:
    """A truth or foil file: any GeoJSON holding polygons, rings closed."""
    shape = polygons(json.loads(path.read_text()))
    if not shape:
        sys.exit(f"score: {path} holds no polygon")
    return [[ring if ring[0] == ring[-1] else ring + [ring[0]] for ring in polygon] for polygon in shape]


def load_target(folder: Path) -> dict:
    """targets/<id>/: target.toml (id, name, date, and an optional [source] table), truth.geojson, and foil.geojson
    on history targets. A source field that is not in the file stays empty; it is never guessed."""
    meta = tomllib.loads((folder / "target.toml").read_text())
    foil = folder / "foil.geojson"
    source = meta.get("source", {})
    return {
        "id": meta["id"], "name": meta["name"], "date": str(meta["date"]),
        "kind": "history" if foil.exists() else "modern",
        "source": {key: str(source.get(key, "")) for key in ("name", "licence", "url")},
        "truth": load_shape(folder / "truth.geojson"),
        "foil": load_shape(foil) if foil.exists() else None,
    }


def load_runs(runs: Path, prompt_id: str) -> dict:
    """{(model id, target id): [run file contents, in sample order]} for runs/<set>/<prompt-id>/."""
    found: dict = {}
    for path in sorted((runs / prompt_id).glob("*/*/*.json"), key=lambda p: (p.parent, int(p.stem))):
        run = json.loads(path.read_text())
        if run["prompt_id"] != prompt_id:
            sys.exit(f"score: {path} was asked with prompt {run['prompt_id']!r}, not {prompt_id!r}")
        found.setdefault((run["model"], run["target_id"]), []).append(run)
    return found


def score_sample(raw: str | None, target: dict) -> dict:
    """One answer against one target: the shape as drawn (None for "no drawing"), its score and its flags."""
    shape, points = parse(raw or "") or (None, 0)
    exact = overlap(shape, target["truth"]) if shape else 0.0
    return {
        "shape": shape, "points": points, "exact": exact, "score": round(exact, 1),
        "flags": {
            "no_drawing": shape is None,
            "over_400_points": points > MAX_POINTS,
            # "Drew the modern country": the drawing overlaps the modern foil more than it overlaps the truth.
            "drew_modern": bool(shape and target["foil"] and overlap(shape, target["foil"]) > exact),
        },
    }


def median(samples: list[dict]) -> int:
    """Index of the sample that is shown: the one with the middle score. With two samples that is the lower one;
    of samples with the same score, the earliest."""
    exact = [s["exact"] for s in samples]
    return exact.index(sorted(exact)[(len(exact) - 1) // 2])


def release_order(by_pair: dict) -> list[tuple[str, str]]:
    """[(model id, release date or "")], oldest first. A model with no release date goes last."""
    created = {model: samples[0]["model_created_at"] or "" for (model, _), samples in by_pair.items()}
    return sorted(((m, c[:10]) for m, c in created.items()), key=lambda mc: (not mc[1], mc[1], mc[0]))


def build(runs: Path, prompt_id: str, targets: Path) -> dict | None:
    """The whole results file as a dict, or None when there is no run file to score."""
    by_pair = load_runs(runs, prompt_id)
    if not by_pair:
        return None
    texts = {run["prompt"].replace(run["target"], "{target}") for samples in by_pair.values() for run in samples}
    if len(texts) != 1:
        sys.exit(f"score: the run files under {runs / prompt_id} were asked with {len(texts)} different prompt texts")

    out_targets = []
    for folder in sorted(p.parent for p in targets.glob("*/target.toml")):
        target = load_target(folder)
        models = []
        for model, released in release_order(by_pair):
            if (model, target["id"]) not in by_pair:
                continue  # no tile is written for a drawing that was never asked for; verify.py reports the gap
            samples = [score_sample(run.get("raw"), target) for run in by_pair[model, target["id"]]]
            shown = samples[median(samples)]
            models.append({
                "id": model,
                "label": model,  # run files hold no display name, so the id is the label
                "released": released,
                "scores": [s["score"] for s in samples],
                "median_sample": median(samples),
                "score": shown["score"],
                "points": shown["points"],
                "outline": display(shown["shape"]) if shown["shape"] else None,
                "flags": shown["flags"],
            })
        out_targets.append({
            "id": target["id"], "name": target["name"], "date": target["date"], "kind": target["kind"],
            "source": target["source"],
            "truth": display(target["truth"], DISPLAY_TOLERANCE),
            "foil": display(target["foil"], DISPLAY_TOLERANCE) if target["foil"] else None,
            "baselines": [{"id": key, "label": label, "score": round(overlap(shape, target["truth"]), 1),
                           "outline": display(shape)} for key, label, shape in baselines(target["truth"])],
            "models": models,
        })
    return {"_about": ABOUT, "schema": 1, "prompt": {"id": prompt_id, "text": texts.pop()},
            "settings_note": SETTINGS_NOTE, "targets": out_targets}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", type=Path, nargs="?", default=ROOT / "runs" / "p1", help="a run set, e.g. runs/p1")
    ap.add_argument("prompt_id", nargs="?", default="p1")
    ap.add_argument("--targets", type=Path, default=ROOT / "targets")
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "results.json")
    args = ap.parse_args(argv)

    results = build(args.runs, args.prompt_id, args.targets)
    if results is None:
        print(f"score: no run files under {args.runs / args.prompt_id}, so nothing was written")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, separators=(",", ":"), ensure_ascii=False) + "\n")
    tiles = sum(len(t["models"]) for t in results["targets"])
    print(f"score: wrote {args.out} ({len(results['targets'])} targets, {tiles} model tiles)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
