"""Build the four modern targets (USA, Chile, Indonesia, Croatia) from Natural Earth. No coordinate is edited.

  uv run python -m pipeline.prep

Reads Natural Earth's 50m countries file, cuts each target out, and rewrites targets/<id>/ with target.toml,
truth.geojson, SOURCE.md and preview.png. Running it twice changes nothing. The source file is not in the repo: it is
fetched once to ~/.cache/borderbench/ and must match the checksum below, so a changed upstream file fails loudly.
"""

import hashlib
import json
import struct
import sys
import urllib.request
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pyproj import Geod, Transformer
import numpy as np
import shapely
from shapely import MultiPolygon, Polygon
from shapely.geometry import LinearRing, mapping
from shapely.geometry.polygon import orient

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache" / "borderbench"

NE_URL = "https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip"
NE_SHA256 = "5fed433373581fa648920435f937d95f2d3c0200e067409c6478dcdf1b853139"
NE_FETCHED = "2026-11-09"  # the day the file with this checksum was downloaded
NE_STEM = "ne_50m_admin_0_countries"

# The lower 48 states: keep the pieces of Natural Earth's United States whose centre lies inside this box.
# It drops Alaska (north of 50°N) and Hawaii (west of 125°W). Territories are separate records and never loaded.
LOWER_48_BOX = (-125.0, 24.0, -66.0, 50.0)  # west, south, east, north

# Published areas the truth is checked against (the spec asks for 2% of the published land area). All four were read
# from Wikipedia on 2026-11-09; `published_from` says which article and what it cites. None is a primary source.
TARGETS = [
    {"id": "usa", "adm0_a3": "USA", "date": "2024-01-01",
     "name": "the contiguous United States (the lower 48 states) as of 1 January 2024",
     "edits": [f"Kept only the pieces whose centre lies inside longitude {LOWER_48_BOX[0]} to {LOWER_48_BOX[2]}, "
               f"latitude {LOWER_48_BOX[1]} to {LOWER_48_BOX[3]}. This removes Alaska and Hawaii. Territories "
               "(Puerto Rico, Guam and others) are separate records in the source and were never part of the shape."],
     "land_km2": 7_663_942, "total_km2": 8_080_464,
     "published_from": 'Wikipedia, "Contiguous United States", which cites the CIA World Factbook\'s area listing',
     "area_note": "The border with Canada runs through the Great Lakes, and the shape counts the United States' side "
                  "of the lakes as territory. That water is in the published total but not in the land figure."},
    {"id": "chile", "adm0_a3": "CHL", "date": "2024-01-01", "name": "Chile as of 1 January 2024", "edits": [],
     "land_km2": 743_812, "total_km2": 756_102,
     "published_from": 'Wikipedia, "Geography of Chile"; the total is cited there to the CIA World Factbook, the land '
                       "figure is uncited. Both exclude the Antarctic claim and include Easter Island",
     "area_note": "The shape includes Chile's Pacific islands as Natural Earth has them. The westernmost piece is at "
                  "109.4°W (Easter Island), far from the mainland, and it widens the frame of the picture a great deal."},
    {"id": "indonesia", "adm0_a3": "IDN", "date": "2024-01-01", "name": "Indonesia as of 1 January 2024", "edits": [],
     "land_km2": 1_811_569, "total_km2": 1_904_569,
     "published_from": 'Wikipedia, "Geography of Indonesia"; the total is cited there to the CIA World Factbook, the '
                       "land figure is uncited",
     "area_note": "The measured area falls between the published land and total figures. Which of the two a map at "
                  "this scale should match is not clear: small islands are missing, inland water is not cut out."},
    {"id": "croatia", "adm0_a3": "HRV", "date": "2024-01-01", "name": "Croatia as of 1 January 2024", "edits": [],
     "land_km2": None, "total_km2": 56_594,
     "published_from": 'Wikipedia, "Geography of Croatia", which cites Croatia\'s Statistical Yearbook 2011. No '
                       "separate land figure was found",
     "area_note": "At 1:50 million the coast is drawn with few points and only 12 islands are kept (Wikipedia "
                  "counts 1,246 islands and islets). The strip of Bosnian coast at Neum, which cuts Croatia's "
                  "mainland in two, is not shown: the mainland is one piece."},
]


def area_check(t: dict, measured: float) -> tuple[str, bool]:
    """A sentence comparing the measured area with the published one, and whether it is within 2%."""
    against, label = (t["land_km2"], "land") if t["land_km2"] else (t["total_km2"], "total")
    off = (measured - against) / against * 100
    line = f"measured {measured:,.0f} km² against a published {label} area of {against:,.0f} km²: {off:+.1f}%"
    if t["land_km2"]:
        line += f" (and {(measured - t['total_km2']) / t['total_km2'] * 100:+.1f}% against the published total, {t['total_km2']:,.0f} km²)"
    return line, abs(off) <= 2.0

def fetch(url: str, sha256: str) -> Path:
    """The cached download, fetched if missing. Stops if the bytes are not the ones this script was written for."""
    path = CACHE / url.rsplit("/", 1)[1]
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        print(f"prep: downloading {url}")
        with urllib.request.urlopen(url, timeout=120) as r:
            path.write_bytes(r.read())
    if (got := hashlib.sha256(path.read_bytes()).hexdigest()) != sha256:
        sys.exit(f"prep: {path} has checksum {got}, expected {sha256}. The source changed: stop and ask.")
    return path


def read_shapefile(zip_path: Path, stem: str) -> list[tuple[dict, MultiPolygon]]:
    """(attributes, shape) for every polygon record of an ESRI shapefile inside a zip. Standard library + shapely.

    Coordinates are read as stored (64-bit floats) and never changed. A shapefile lists rings flat: clockwise
    rings are outlines and counter-clockwise rings are holes, each hole belonging to the outline that contains it.
    """
    with zipfile.ZipFile(zip_path) as z:
        shp, dbf = z.read(f"{stem}.shp"), z.read(f"{stem}.dbf")

    count, header_len, record_len = struct.unpack("<IHH", dbf[4:12])
    fields, pos = [], 32
    while dbf[pos] != 0x0D:
        fields.append((dbf[pos:pos + 11].split(b"\0")[0].decode(), dbf[pos + 16]))
        pos += 32
    rows = []
    for i in range(count):
        row, pos, attrs = dbf[header_len + i * record_len:header_len + (i + 1) * record_len], 1, {}
        for name, length in fields:
            attrs[name] = row[pos:pos + length].decode("utf-8").strip("\x00 ")
            pos += length
        rows.append(attrs)

    shapes, pos = [], 100
    while pos < len(shp):
        (words,) = struct.unpack(">i", shp[pos + 4:pos + 8])
        body = shp[pos + 8:pos + 8 + 2 * words]
        pos += 8 + 2 * words
        if struct.unpack("<i", body[:4])[0] != 5:
            sys.exit("prep: expected only polygon records (shape type 5)")
        n_parts, n_points = struct.unpack("<ii", body[36:44])
        starts = [*struct.unpack(f"<{n_parts}i", body[44:44 + 4 * n_parts]), n_points]
        flat = struct.unpack(f"<{2 * n_points}d", body[44 + 4 * n_parts:44 + 4 * n_parts + 16 * n_points])
        points = list(zip(flat[0::2], flat[1::2]))
        rings = [LinearRing(points[a:b]) for a, b in zip(starts, starts[1:])]
        outlines = [Polygon(r) for r in rings if not r.is_ccw]
        holes = [[] for _ in outlines]
        for hole in (r for r in rings if r.is_ccw):
            holes[next(i for i, o in enumerate(outlines) if o.contains(Polygon(hole).representative_point()))].append(hole)
        shapes.append(MultiPolygon([Polygon(o.exterior, hs) for o, hs in zip(outlines, holes)]))
    if len(shapes) != len(rows):
        sys.exit("prep: the shapefile and its attribute table disagree on the number of records")
    return list(zip(rows, shapes))


def lower_48(shape: MultiPolygon) -> MultiPolygon:
    west, south, east, north = LOWER_48_BOX
    def inside(p):
        c = p.representative_point()
        return west <= c.x <= east and south <= c.y <= north
    return MultiPolygon([p for p in shape.geoms if inside(p)])


def area_km2(shape) -> float:
    """Area on the WGS84 ellipsoid, in square kilometres."""
    return abs(Geod(ellps="WGS84").geometry_area_perimeter(shape)[0]) / 1e6


def equal_area(shape, centre=None):
    """Project [lon, lat] to metres in a Lambert azimuthal equal-area projection centred on `centre` (default: the
    middle of the shape's bounding box). A point is added at least every 0.1° first, so a long straight edge
    follows its parallel instead of cutting a chord."""
    west, south, east, north = (shape if centre is None else centre).bounds
    to_m = Transformer.from_crs(
        "EPSG:4326", f"+proj=laea +lat_0={(south + north) / 2} +lon_0={(west + east) / 2} +datum=WGS84", always_xy=True)
    flat = shapely.transform(shape.segmentize(0.1), lambda xy: np.column_stack(to_m.transform(xy[:, 0], xy[:, 1])))
    # segmentize hands a one-piece MultiPolygon back as a bare Polygon; callers loop over .geoms
    return MultiPolygon([flat]) if flat.geom_type == "Polygon" else flat


def draw_preview(shape: MultiPolygon, title: str, path: Path, outlines=()) -> None:
    """The truth filled on a plain background with a scale bar. `outlines` are (shape, label) drawn as lines over it."""
    size, pad, ss = 1200, 80, 2  # drawn at 2x and shrunk, for smooth edges
    flat = equal_area(shape)
    extra = [(equal_area(o, centre=shape), label) for o, label in outlines]
    xs0, ys0, xs1, ys1 = zip(*[g.bounds for g in [flat, *[e for e, _ in extra]]])
    west, south, east, north = min(xs0), min(ys0), max(xs1), max(ys1)
    scale = (size - 2 * pad) / max(east - west, north - south)  # pixels per metre
    width, height = round((east - west) * scale) + 2 * pad, round((north - south) * scale) + 2 * pad + 60

    def px(ring):
        return [((x - west) * scale * ss + pad * ss, (north - y) * scale * ss + pad * ss) for x, y in ring.coords]

    img = Image.new("RGB", (width * ss, height * ss), "#f6f4ee")
    d = ImageDraw.Draw(img)
    for p in flat.geoms:
        d.polygon(px(p.exterior), fill="#3b4a5a")
        for hole in p.interiors:
            d.polygon(px(hole), fill="#f6f4ee")
    for e, _ in extra:
        for p in e.geoms:
            d.line(px(p.exterior), fill="#d1495b", width=3 * ss, joint="curve")
    img = img.resize((width, height), Image.LANCZOS)
    d = ImageDraw.Draw(img)

    km = min((50, 100, 200, 500, 1000, 2000), key=lambda k: abs(k * 1000 * scale - width / 5))
    bar, y = km * 1000 * scale, height - 40
    d.line([(pad, y), (pad + bar, y)], fill="#222222", width=3)
    for x in (pad, pad + bar):
        d.line([(x, y - 6), (x, y + 6)], fill="#222222", width=3)
    font = ImageFont.load_default(size=18)
    d.text((pad + bar + 12, y - 11), f"{km} km", fill="#222222", font=font)
    d.text((pad, 24), title, fill="#222222", font=font)
    for i, (_, label) in enumerate(extra):
        d.text((pad, 50 + 24 * i), label, fill="#d1495b", font=font)
    img.save(path, optimize=True)


def write_target(folder: Path, *, id: str, name: str, date: str, shape: MultiPolygon, source_md: str) -> None:
    """target.toml, truth.geojson and SOURCE.md. Rings are wound the GeoJSON way (outline counter-clockwise)."""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "target.toml").write_text(f'id = "{id}"\nname = "{name}"\ndate = "{date}"\n')
    wound = MultiPolygon([orient(p, 1.0) for p in shape.geoms])
    (folder / "truth.geojson").write_text(json.dumps(mapping(wound), separators=(",", ":")) + "\n")
    (folder / "SOURCE.md").write_text(source_md)


def main() -> int:
    records = {attrs["ADM0_A3"]: (attrs, shape) for attrs, shape in read_shapefile(fetch(NE_URL, NE_SHA256), NE_STEM)}
    with zipfile.ZipFile(CACHE / f"{NE_STEM}.zip") as z:
        version = z.read(f"{NE_STEM}.VERSION.txt").decode().strip()
    for t in TARGETS:
        attrs, shape = records[t["adm0_a3"]]
        if t["id"] == "usa":
            shape = lower_48(shape)
        assert shape.is_valid and not shape.is_empty, t["id"]
        check, ok = area_check(t, area_km2(shape))
        edits = [*t["edits"],
                 "Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed."]
        source_md = f"""# Source: {t['name']}

- **Source:** Natural Earth, Admin 0 – Countries, 1:50m, version {version}. Record `{attrs['ADMIN']}` (`ADM0_A3` = `{t['adm0_a3']}`).
- **File:** `{NE_URL.rsplit('/', 1)[1]}` from {NE_URL}
- **Checksum (SHA-256):** `{NE_SHA256}`
- **Fetched:** {NE_FETCHED}
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Built by:** `uv run python -m pipeline.prep`. Nothing here is edited by hand.

## Edits
{chr(10).join(f'{i}. {e}' for i, e in enumerate(edits, 1))}

## What the shape includes
- {len(shape.geoms)} separate piece(s), {sum(len(p.exterior.coords) + sum(len(h.coords) for h in p.interiors) for p in shape.geoms)} points.
- Lakes and rivers inside the border are not cut out: the shape is the territory inside the border and coastline.
- Disputed areas follow Natural Earth's default (de facto) view. Nothing was added or removed for a dispute.
- {t['area_note']}

## Area check
- Area on the WGS84 ellipsoid: {check}.
- **{'Within' if ok else 'Outside'} the 2% the spec asks for.**
- Published figure from: {t['published_from']}. Read on 2026-11-09.
"""
        folder = ROOT / "targets" / t["id"]
        write_target(folder, id=t["id"], name=t["name"], date=t["date"], shape=shape, source_md=source_md)
        draw_preview(shape, t["name"], folder / "preview.png")
        print(f"prep: {t['id']:<10} {len(shape.geoms):>3} piece(s)  {'ok  ' if ok else 'MISS'}  {check}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
