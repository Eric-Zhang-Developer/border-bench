"""The parser reads what a model wrote and changes none of it (specs/decisions/002-grading.md, step 1)."""

import json

import pytest

from pipeline.parse import parse

RING = [[0, 0], [4, 0], [4, 3], [0, 3], [0, 0]]
OTHER = [[10, 10], [12, 10], [12, 12], [10, 10]]
SHAPE = [[[[float(x), float(y)] for x, y in RING]]]
OTHER_SHAPE = [[[[float(x), float(y)] for x, y in OTHER]]]


def polygon(ring=RING):
    return json.dumps({"type": "Polygon", "coordinates": [ring]})


def test_fenced_json_is_read():
    assert parse(f"```json\n{polygon()}\n```") == (SHAPE, 5)
    assert parse(f"```geojson\n{polygon()}\n```") == (SHAPE, 5)


def test_json_after_reasoning_text_is_read():
    text = f"The country sits between 0 and 4 east [roughly]. Its corners are easy.\n\n{polygon()}\n\nDone."
    assert parse(text) == (SHAPE, 5)


def test_of_two_json_blocks_the_last_wins():
    assert parse(f"First try:\n{polygon(OTHER)}\nOn reflection:\n{polygon()}") == (SHAPE, 5)
    assert parse(f"```geojson\n{polygon(OTHER)}\n```\nBetter:\n```geojson\n{polygon()}\n```") == (SHAPE, 5)


def test_a_geojson_block_beats_any_other_json_even_later_json():
    """Only the fenced block is scored, as the prompt promises; a stray array after it is not the drawing."""
    text = f"```geojson\n{polygon()}\n```\nCheck points: {json.dumps(OTHER)}"
    assert parse(text) == (SHAPE, 5)


def test_a_broken_geojson_block_falls_back_to_the_last_json_that_holds_coordinates():
    assert parse(f"{polygon()}\n```geojson\n{{\"type\": \"Polygon\", \"coordinates\": [[[1, 2], [3,\n```") == (SHAPE, 5)


def test_an_open_ring_is_closed_and_its_points_are_counted_as_written():
    shape, points = parse(json.dumps({"type": "Polygon", "coordinates": [RING[:-1]]}))
    assert shape == SHAPE
    assert points == 4


@pytest.mark.parametrize("value", [
    {"type": "Polygon", "coordinates": [RING]},
    {"type": "MultiPolygon", "coordinates": [[RING]]},
    {"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [RING]}},
    {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {}, "geometry": {"type": "MultiPolygon", "coordinates": [[RING]]}}]},
    RING,        # a bare ring
    [RING],      # a bare polygon
    [[RING]],    # a bare multipolygon
], ids=["Polygon", "MultiPolygon", "Feature", "FeatureCollection", "bare ring", "bare polygon", "bare multipolygon"])
def test_each_accepted_geometry_type(value):
    assert parse(json.dumps(value)) == (SHAPE, 5)


def test_pieces_and_holes_keep_their_structure():
    hole = [[1, 1], [2, 1], [2, 2], [1, 1]]
    shape, points = parse(json.dumps({"type": "MultiPolygon", "coordinates": [[RING, hole], [OTHER]]}))
    assert [len(polygon) for polygon in shape] == [2, 1]
    assert points == 5 + 4 + 4
    features = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [RING]}},
        {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [OTHER]}}]}
    assert parse(json.dumps(features))[0] == SHAPE + OTHER_SHAPE


@pytest.mark.parametrize("text", [
    "",
    "I'm not able to draw that from memory.",
    '{"type": "MultiPolygon", "coordinates": [[[[12.0, 48.0], [13.5, 48.2], [13.',    # cut off mid-answer
    "[12.5, 48.0]",                                                                     # one point
    "[[12.5, 48.0], [13.0, 49.0]]",                                                     # two points enclose nothing
    '{"type": "LineString", "coordinates": [[0, 0], [4, 0], [4, 3]]}',
    '{"type": "Polygon", "coordinates": [[[0, 0], [NaN, 0], [4, 3]]]}',
    '{"type": "Polygon", "coordinates": [[["0", "0"], ["4", "0"], ["4", "3"]]]}',
    "[" * 100_000,
], ids=["empty", "refusal", "cut off", "one point", "two points", "a line", "not a number", "strings", "deep nesting"])
def test_garbage_is_no_drawing(text):
    assert parse(text) is None


def test_nothing_is_repaired():
    """Swapped coordinates, a wrong sign, an impossible latitude, a self-crossing ring: all come out as written."""
    bow_tie = [[0, 0], [2, 2], [2, 0], [0, 2], [0, 0]]
    swapped = [[49.0, -123.0], [49.0, -95.0], [30.0, -95.0], [49.0, -123.0]]
    for ring in (bow_tie, swapped):
        shape, _ = parse(json.dumps({"type": "Polygon", "coordinates": [ring]}))
        assert shape == [[[[float(x), float(y)] for x, y in ring]]]
