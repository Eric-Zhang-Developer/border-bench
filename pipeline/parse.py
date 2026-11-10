"""A model's answer, as text, becomes the shape it drew. Nothing is repaired on the way.

The rule (specs/decisions/002-grading.md): take the last ```geojson block; failing that, the last valid JSON value in
the answer that holds coordinates. Polygon, MultiPolygon, Feature, FeatureCollection and bare coordinate arrays are
read. A ring whose last point does not repeat its first is closed, which is parsing. Everything else stays as
written: swapped coordinates, wrong signs, crossings and stray pieces all reach the scorer untouched.

A shape here is MultiPolygon coordinates: a list of polygons, each a list of rings, each a list of [lon, lat].
"""

import json
import math
import re

GEOJSON_BLOCK = re.compile(r"```geojson[^\n]*\n(.*?)```", re.DOTALL | re.IGNORECASE)
OPENER = re.compile(r"[\[{]")
BRACKETS = re.compile(r"[\[\s]+")
DEEPEST = 8   # a FeatureCollection of MultiPolygons nests lists 5 deep; anything far past that is not a drawing


def _is_position(p) -> bool:
    return (isinstance(p, list) and len(p) >= 2
            and all(type(x) in (int, float) and math.isfinite(x) for x in p[:2]))


def _is_ring(v) -> bool:
    return isinstance(v, list) and bool(v) and all(_is_position(p) for p in v)


def polygons(value, depth: int = 0) -> list:
    """Every polygon in a decoded JSON value, as written. A list of positions is one ring; a list of rings is one
    polygon; deeper lists are several polygons. A Polygon or MultiPolygon is read by how its coordinates are nested,
    not by which of the two names it carries, because the same array would be accepted bare."""
    if depth > DEEPEST:
        return []
    if isinstance(value, dict):
        kind = value.get("type")
        if kind in ("Polygon", "MultiPolygon"):
            return polygons(value.get("coordinates"), depth + 1)
        if kind == "Feature":
            return polygons(value.get("geometry"), depth + 1)
        if kind == "FeatureCollection" and isinstance(value.get("features"), list):
            return [p for f in value["features"] if isinstance(f, dict) for p in polygons(f, depth + 1)]
        return []
    if _is_ring(value):
        return [[value]]
    if isinstance(value, list) and value and all(_is_ring(r) for r in value):
        return [value]
    if isinstance(value, list):
        return [p for v in value if isinstance(v, list) for p in polygons(v, depth + 1)]
    return []


def _holds_coordinates(value) -> bool:
    """A drawing needs at least one ring that could enclose something: three points."""
    return any(len(ring) >= 3 for polygon in polygons(value) for ring in polygon)


def _json_values(text: str):
    """Each outermost JSON object or array in the text, in order. Text that does not decode is skipped a character
    at a time, so the complete pieces of a cut-off answer are still found."""
    decoder = json.JSONDecoder()
    at = 0
    while found := OPENER.search(text, at):
        try:
            value, at = decoder.raw_decode(text, found.start())
            yield value
        except ValueError:
            at = found.start() + 1
        except RecursionError:
            # Thousands of brackets in a row (a model stuck in a loop). Nothing that starts more than DEEPEST
            # brackets before the end of the run could be a drawing, so resume there instead of at every bracket.
            # ponytail: a run of nested objects ({"a": {"a": ...) is still retried one at a time; slow, not wrong.
            run = BRACKETS.match(text, found.start())
            brackets = [m.start() for m in re.finditer(r"\[", run.group())] if run else []
            at = found.start() + (brackets[-DEEPEST] if len(brackets) > DEEPEST else 1)


def parse(text: str) -> tuple[list, int] | None:
    """(shape with every ring closed, number of points as the model wrote them), or None for "no drawing"."""
    chosen = None
    if blocks := GEOJSON_BLOCK.findall(text):
        try:
            value = json.loads(blocks[-1])
            chosen = value if _holds_coordinates(value) else None
        except (ValueError, RecursionError):
            pass
    if chosen is None:
        for value in _json_values(text):
            if _holds_coordinates(value):
                chosen = value  # the last one wins
    if chosen is None:
        return None
    written = polygons(chosen)
    shape = [[[[float(p[0]), float(p[1])] for p in ring] for ring in polygon] for polygon in written]
    for polygon in shape:
        for ring in polygon:
            if ring[0] != ring[-1]:
                ring.append(list(ring[0]))
    return shape, sum(len(ring) for polygon in written for ring in polygon)
