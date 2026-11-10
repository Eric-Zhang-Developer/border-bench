"""The scorer's golden cases (specs/features/scorer/spec.md), on made-up shapes: no real border or answer is needed.

  uv run python -m pipeline.test_score DIR     writes the made-up runs/ and targets/ tree into DIR, for a demo sheet
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

from pipeline import score, sheet
from pipeline.score import baselines, median, overlap, projection, release_order, to_metres
from pipeline.verify import missing_tiles

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "specs" / "features" / "scorer" / "results.example.json"


def square(lon, lat, side):
    return [[[[lon, lat], [lon + side, lat], [lon + side, lat + side], [lon, lat + side], [lon, lat]]]]


# ---------------------------------------------------------------------------------------------- the golden cases

def test_truth_against_itself_is_100():
    assert overlap(square(10, 40, 5), square(10, 40, 5)) == 100.0
    blobland = [[blob(12, 48, 3), blob(12.6, 48.2, 0.6, 40)], [blob(18.6, 45.4, 0.7, 60)]]
    assert overlap(blobland, blobland) == 100.0


def test_two_shapes_that_do_not_touch_score_0():
    assert overlap(square(10, 40, 1), square(30, 40, 1)) == 0.0


def test_two_equal_squares_offset_by_half_their_width_score_33_3():
    assert round(overlap(square(0.5, -0.5, 1), square(0, -0.5, 1)), 1) == 33.3
    assert round(overlap(square(11, 45, 2), square(10, 45, 2)), 1) == 33.3


def test_a_two_point_edge_along_the_49th_parallel_stays_within_1_km_of_it():
    """The USA's northern border as a model would write it: two points, 28 degrees of longitude apart. Flattened
    without added points it would be a straight chord that cuts tens of km south of the parallel."""
    edge = [[-123.0, 49.0], [-95.0, 49.0]]
    proj = projection(square(-125, 24, 25) + square(-66, 24, 25))   # a map centred on the lower 48 states

    def worst_km_from_the_parallel(xy):
        along = np.linspace(0, 1, 11)[:, None, None]
        x, y = (xy[:-1] + (xy[1:] - xy[:-1]) * along).reshape(-1, 2).T    # 11 places along every drawn segment
        _, lat = proj(x, y, inverse=True)
        return np.abs(lat - 49).max() * 111.2

    assert worst_km_from_the_parallel(to_metres(proj, edge)) < 1
    assert worst_km_from_the_parallel(to_metres(proj, edge, step=28)) > 50   # the same check fails without the points


def test_a_self_crossing_outline_scores_the_same_value_on_every_run():
    """Nothing is repaired, so the fill rule decides, and it is pinned here: a cell is land when it is inside an
    odd number of the outline's loops."""
    bow_tie = [[[[0, 0], [2, 2], [2, 0], [0, 2], [0, 0]]]]            # two triangles: half of the 2 x 2 square
    assert {round(overlap(bow_tie, square(0, 0, 2)), 1) for _ in range(3)} == {50.0}
    # Two overlapping 2 x 2 squares drawn as one outline: the part wrapped twice is empty, so 6 of 9 cells.
    twice = [[[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0], [1, 1], [3, 1], [3, 3], [1, 3], [1, 1], [0, 0]]]]
    assert {round(overlap(twice, square(0, 0, 3)), 1) for _ in range(3)} == {66.7}


# -------------------------------------------------------------------------------------- more of the grading rules

def test_holes_are_holes_and_separate_polygons_add_up():
    with_hole = [square(0, 0, 2)[0] + square(0.5, 0.5, 1)[0]]
    assert round(overlap(with_hole, square(0, 0, 2)), 1) == 75.0
    two_overlapping_polygons = square(0, 0, 2) + square(1, 0, 2)      # unlike one outline wrapped twice
    assert round(overlap(two_overlapping_polygons, [[[[0, 0], [3, 0], [3, 2], [0, 2], [0, 0]]]]), 1) == 100.0


def test_coordinates_no_map_can_hold_are_still_scored_as_drawn():
    usa_ish = [[[[-124, 25], [-67, 25], [-67, 49], [-124, 49], [-124, 25]]]]
    swapped = [[[[lat, lon] for lon, lat in usa_ish[0][0]]]]           # latitudes of -124: past the pole
    assert overlap(swapped, usa_ish) == 0.0
    nonsense = [[[[1e9, 3e7], [45, -1e12], [4e5, -95], [1e9, 3e7]]]]
    assert 0 <= overlap(nonsense, usa_ish) == overlap(nonsense, usa_ish) <= 100


def test_the_baselines_are_the_bounding_box_and_a_circle_of_the_same_area():
    truth = square(0, -0.5, 1)
    (_, _, rectangle), (_, _, circle) = baselines(truth)
    assert round(overlap(rectangle, truth), 1) == 100.0
    # A circle with a square's area shares 83.4% with it (four slivers stick out, four corners are missed).
    assert overlap(circle, truth) == pytest.approx(83.4, abs=0.15)
    two_pieces = square(10, 10, 4) + [[[[17, 10], [24, 10], [24, 14], [17, 14], [17, 10]]]]
    assert baselines(two_pieces)[0][2] == [[[[10, 10], [24, 10], [24, 14], [10, 14], [10, 10]]]]


@pytest.mark.parametrize("target, expected", [("usa", 55.4), ("chile", 4.6), ("indonesia", 19.8), ("croatia", 25.5)])
def test_the_rectangle_baseline_of_each_modern_target_is_pinned(target, expected):
    """The real true borders in targets/, scored against their own bounding boxes. A change to the scorer or to a
    border that moves one of these moves every score on that strip, and has to be said out loud. Chile's is tiny
    because its box stretches 3,700 km west to Easter Island."""
    truth = score.load_target(ROOT / "targets" / target)["truth"]
    assert round(overlap(baselines(truth)[0][2], truth), 1) == expected


def test_the_median_sample_is_shown_and_models_run_in_release_order():
    assert median([{"exact": 41.0}, {"exact": 52.0}, {"exact": 47.5}]) == 2
    assert median([{"exact": 0.0}, {"exact": 0.0}, {"exact": 0.0}]) == 0             # equal scores: the earliest
    assert median([{"exact": 60.0}, {"exact": 40.0}]) == 1             # two samples: the lower
    assert median([{"exact": 88.0}]) == 0
    runs = {("new", "t"): [{"model_created_at": "2026-06-01T00:00:00+00:00"}],
            ("undated", "t"): [{"model_created_at": None}],
            ("old", "t"): [{"model_created_at": "2025-09-29T00:00:00+00:00"}]}
    assert release_order(runs) == [("old", "2025-09-29"), ("new", "2026-06-01"), ("undated", "")]


# ------------------------------------------------------------------- a made-up runs/ and targets/ tree, end to end

PROMPT = "Draw {target} from memory.\nEnd with one ```geojson block.\n"


def blob(lon, lat, size, points=120, turn=0.0):
    """A made-up coastline: a lumpy closed curve about `size` degrees across."""
    t = np.linspace(0, 2 * np.pi, points, endpoint=False)
    r = size * (1 + 0.22 * np.sin(3 * t + turn) + 0.10 * np.cos(5 * t))
    ring = np.column_stack([lon + 1.4 * r * np.cos(t), lat + r * np.sin(t)]).round(2).tolist()
    return ring + [ring[0]]


def fenced(shape, kind="MultiPolygon"):
    body = {"type": kind, "coordinates": shape if kind == "MultiPolygon" else shape[0]}
    return f"The coast bulges in three places, so I will place those first.\n\n```geojson\n{json.dumps(body)}\n```\n"


def make_tree(root: Path) -> tuple[Path, Path]:
    """Two made-up targets (one modern, one history with a foil) and four made-up models. Returns (runs, targets)."""
    modern = [[blob(12, 48, 3), blob(12.6, 48.2, 0.6, 40)], [blob(18.6, 45.4, 0.7, 60)]]   # mainland, lake, island
    old = [[blob(8.5, 48, 1.7, 80)], [blob(15.5, 48.4, 2.1, 90, turn=1.0)]]                # a country in two pieces
    targets = {
        "blobland": ("Blobland as of 1 January 2024", "2024-01-01", modern, None,
                     '\n[source]\nname = "Made up for the tests"\nlicence = "MIT, with the code"\nurl = ""\n'),
        "old-blobland": ("Old Blobland as of 1 January 1900", "1900-01-01", old, modern, ""),
    }
    for key, (name, date, truth, foil, source) in targets.items():
        folder = root / "targets" / key
        folder.mkdir(parents=True)
        (folder / "target.toml").write_text(f'id = "{key}"\nname = "{name}"\ndate = "{date}"\n{source}')
        (folder / "truth.geojson").write_text(json.dumps({"type": "MultiPolygon", "coordinates": truth}))
        if foil:
            (folder / "foil.geojson").write_text(json.dumps({"type": "MultiPolygon", "coordinates": foil}))

    t = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    figure_eight = np.column_stack([12 + 4.6 * np.sin(t), 48 + 2.6 * np.sin(2 * t)]).round(2).tolist()
    one_big_loop = np.column_stack([14 + 6.5 * np.cos(t), 47 + 4 * np.sin(t)]).round(2).tolist()
    close = [[blob(12, 48, 2.95, 300), blob(12.6, 48.2, 0.6, 40)], [blob(18.6, 45.4, 0.68, 80)]]
    no_drawing = ["I'm not able to draw that from memory.", "",
                  '```geojson\n{"type": "MultiPolygon", "coordinates": [[[[12.0, 48.0], [13.5, 48.2], [13.']
    answers = {   # model: (released, {target: [raw answers]})
        "example-model-a": ("2025-09-01T00:00:00+00:00", {
            "blobland": [
                "Nine points will do.\n" + json.dumps(blob(12, 48, 3, 9)[:-1]),                 # coarse, ring left open
                fenced([[blob(13.4, 48.6, 3, 40)]], "Polygon"),                                # right shape, shifted
                fenced([[[[lat, lon] for lon, lat in blob(12, 48, 3, 40)]]]),                  # latitude first
            ],
            "old-blobland": [fenced([[blob(12, 48, size, 30)]]) for size in (3.0, 2.8, 3.1)],  # the modern country
        }),
        "example-model-b": ("2026-03-01T00:00:00+00:00", {
            "blobland": [fenced([[figure_eight]]), fenced([[blob(12, 48, 4.2, 60)]]), fenced([[one_big_loop]])],
            "old-blobland": [fenced([old[1]]), fenced([[blob(9.3, 48.5, 1.7, 40)], [blob(16.3, 48.9, 2.1, 40)]]),
                             fenced([[one_big_loop]])],
        }),
        "example-model-c": ("2026-06-01T00:00:00+00:00", {
            "blobland": [json.dumps({"type": "FeatureCollection", "features": [
                {"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": polygon}}
                for polygon in close]})],                                                       # 423 points
            "old-blobland": [fenced([[blob(8.5, 48, 1.65, 60)], [blob(15.5, 48.4, 2.05, 70, turn=1.0)]])],
        }),
        "example-model-d": ("2026-10-01T00:00:00+00:00", {"blobland": no_drawing, "old-blobland": no_drawing}),
    }
    for model, (released, by_target) in answers.items():
        for key, raws in by_target.items():
            for n, raw in enumerate(raws, start=1):
                path = root / "runs" / "demo" / "p1" / model / key / f"{n}.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({   # the fields pipeline/run.py writes that the scorer reads
                    "prompt_id": "p1", "prompt": PROMPT.replace("{target}", targets[key][0]), "model": model,
                    "model_created_at": released, "target_id": key, "target": targets[key][0], "raw": raw,
                    "stop_reason": "end_turn"}, indent=2))
    return root / "runs" / "demo", root / "targets"


@pytest.fixture(scope="module")
def tree(tmp_path_factory):
    return make_tree(tmp_path_factory.mktemp("tree"))


@pytest.fixture(scope="module")
def results(tree):
    return score.build(tree[0], "p1", tree[1])


def keys_and_types(*values) -> dict:
    """The shape of some JSON values taken together: every object's keys and every leaf's type, all the way down.
    Objects that sit side by side must have identical keys. A GeoJSON geometry counts as one leaf."""
    out: dict = {}
    for v in values:
        if isinstance(v, dict) and set(v) == {"type", "coordinates"}:
            out.setdefault("types", set()).add(v["type"])
        elif isinstance(v, dict):
            out.setdefault("objects", []).append(v)
        elif isinstance(v, list):
            out.setdefault("items", []).extend(v)
        else:
            out.setdefault("types", set()).add("number" if type(v) in (int, float) else type(v).__name__)
    if "objects" in out:
        keys = {frozenset(o) for o in out["objects"]}
        assert len(keys) == 1, f"objects side by side with different keys: {sorted(map(sorted, keys))}"
        out["objects"] = {k: keys_and_types(*(o[k] for o in out["objects"])) for k in sorted(keys.pop())}
    if "items" in out:
        out["items"] = keys_and_types(*out["items"])
    return out


def test_the_results_file_has_exactly_the_keys_of_the_example(results):
    """The page is built against results.example.json, so the two must agree field for field."""
    assert keys_and_types(results) == keys_and_types(json.loads(EXAMPLE.read_text()))
    assert list(results) == list(json.loads(EXAMPLE.read_text()))    # and in the same order at the top level


def test_the_results_file_says_what_was_drawn(results):
    modern, history = results["targets"]
    assert (modern["id"], modern["kind"], modern["foil"]) == ("blobland", "modern", None)
    assert (history["id"], history["kind"]) == ("old-blobland", "history")
    assert results["prompt"] == {"id": "p1", "text": PROMPT}
    assert modern["source"] == {"name": "Made up for the tests", "licence": "MIT, with the code", "url": ""}
    assert history["source"] == {"name": "", "licence": "", "url": ""}   # not in target.toml: empty, never guessed
    assert missing_tiles(results) == []                                  # the check the verify command makes

    for target in results["targets"]:
        assert [b["id"] for b in target["baselines"]] == ["rectangle", "circle"]
        assert [m["id"] for m in target["models"]] == [f"example-model-{x}" for x in "abcd"]
        for m in target["models"]:
            assert all(0 <= s <= 100 and s == round(s, 1) for s in m["scores"])
            assert m["score"] == m["scores"][m["median_sample"]]

    a, b, c, d = modern["models"]
    assert a["released"] == "2025-09-01"
    assert a["scores"][2] == 0.0 and a["score"] == sorted(a["scores"])[1]    # latitude first scores 0; median shown
    assert a["flags"] == {"no_drawing": False, "over_400_points": False, "drew_modern": False}
    assert (c["points"], c["flags"]["over_400_points"], len(c["scores"])) == (423, True, 1)
    assert c["score"] > 90
    assert (d["scores"], d["outline"], d["points"]) == ([0.0, 0.0, 0.0], None, 0)
    assert d["flags"] == {"no_drawing": True, "over_400_points": False, "drew_modern": False}

    a, b, c, d = history["models"]
    assert a["flags"]["drew_modern"] and not b["flags"]["drew_modern"] and not c["flags"]["drew_modern"]
    assert c["score"] > 85


def test_outlines_have_a_point_at_least_every_degree_so_the_page_draws_what_was_scored(results):
    for target in results["targets"]:
        shapes = [target["truth"], target["foil"], *(x["outline"] for x in target["baselines"] + target["models"])]
        for shape in filter(None, shapes):
            for polygon in shape["coordinates"]:
                for ring in polygon:
                    assert ring[0] == ring[-1]
                    assert np.abs(np.diff(np.array(ring), axis=0)).max() <= 1.0001


def test_the_command_writes_the_same_file_twice_and_nothing_when_there_are_no_runs(tree, tmp_path, capsys):
    out = tmp_path / "results" / "results.json"
    args = [str(tree[0]), "p1", "--targets", str(tree[1]), "--out", str(out)]
    assert score.main(args) == 0
    first = out.read_bytes()
    assert score.main(args) == 0
    assert out.read_bytes() == first

    nothing = tmp_path / "none.json"
    assert score.main([str(tmp_path / "runs" / "p1"), "p1", "--targets", str(tree[1]), "--out", str(nothing)]) == 0
    assert not nothing.exists()
    assert "nothing was written" in capsys.readouterr().out


def test_run_files_asked_with_two_different_prompts_are_refused(tree, tmp_path):
    runs, _ = make_tree(tmp_path)
    odd = runs / "p1" / "example-model-a" / "blobland" / "1.json"
    odd.write_text(json.dumps(json.loads(odd.read_text()) | {"prompt": "Sketch Blobland as of 1 January 2024."}))
    with pytest.raises(SystemExit, match="2 different prompt texts"):
        score.build(runs, "p1", tmp_path / "targets")


def test_the_contact_sheet_shows_missed_and_invented_land(tree, tmp_path):
    from PIL import Image
    out = tmp_path / "sheet.png"
    assert sheet.main([str(tree[0]), "p1", "blobland", "--targets", str(tree[1]), "--out", str(out)]) == 0
    colours = {c for _, c in Image.open(out).convert("RGB").getcolors(maxcolors=1 << 24)}
    assert {sheet.rgb(sheet.MISSED), sheet.rgb(sheet.INVENTED), sheet.rgb(sheet.RIGHT)} <= colours


def test_a_sheet_can_compare_several_prompts_one_row_per_model_and_prompt(tree):
    target = score.load_target(tree[1] / "blobland")
    runs = score.load_runs(tree[0], "p1")
    names = [e["name"] for e in sheet.entries_for(target, {"p1": runs, "p1-again": runs})]
    assert names[:2] == ["Baseline", "Baseline"]
    assert names[2:8] == ["example-model-a · p1"] * 3 + ["example-model-a · p1-again"] * 3
    assert len(names) == 2 + 2 * 10


if __name__ == "__main__":
    print("wrote %s and %s" % make_tree(Path(sys.argv[1])))
