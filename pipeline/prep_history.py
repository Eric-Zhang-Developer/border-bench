"""Build the two history targets (Prussia 1816, Poland 1938) and their modern foils. No coordinate is edited.

  uv run python -m pipeline.prep_history

Prussia comes from HistoGIS (one shape, valid 9 June 1815 to 31 May 1834), Poland from CShapes 2.0 (the record
valid on 1 January 1938). Each gets a foil, the modern country a model might draw instead, from the same Natural
Earth file as the modern targets. Running it twice changes nothing. No source file is in the repo: each is fetched
once to ~/.cache/borderbench/ and must match its checksum, so a changed upstream file fails loudly.
"""

import json
import sys
import zipfile

from shapely import MultiPolygon, Point
from shapely.geometry import mapping, shape as to_shape
from shapely.geometry.polygon import orient

from pipeline.prep import (CACHE, NE_FETCHED, NE_SHA256, NE_STEM, NE_URL, ROOT, area_km2, draw_preview, fetch,
                           read_shapefile, write_target)


FETCHED = "2026-11-09"  # the day the two files with the checksums below were downloaded

# HistoGIS shape 10039: "Preußen", Kingdom, valid 1815-06-09 to 1834-05-31.
PRUSSIA_URL = "https://histogis.acdh.oeaw.ac.at/api/tempspatial/10039.json"
PRUSSIA_SHA256 = "412793a97504b92580657b51d6766c08b1a446cf14f7ff648c64e2c88e7f86f7"
PRUSSIA_PERMALINK = "https://histogis.acdh.oeaw.ac.at/shapes/permalink/4052e0f206241cc152c6e867033a9db3/"

CSHAPES_URL = "https://icr.ethz.ch/data/cshapes/CShapes-2.0.geojson"
CSHAPES_SHA256 = "384b1ea90b9419f30a858d7ec237c85a22c60d1b35b5f85f215a1204f9989d42"
POLAND_GWCODE = 290  # Poland's number in the Gleditsch and Ward list of states, which CShapes uses
POLAND_PUBLISHED_KM2 = 388_634  # "388 634 km² (1 stycznia 1938 r.)", https://pl.wikipedia.org/wiki/II_Rzeczpospolita

# Who to credit, written into target.toml for the scorer and the page. Both licences require the credit.
PRUSSIA_SOURCE = {
    "name": 'Antonia Dückelmann / Peter Paul Marckhgott-Sanabria, \\"German Confederation State Borders 1830\\", HistoGIS',
    "licence": "CC BY 4.0 as published by HistoGIS; built from Census Mosaic data, whose terms are non-commercial",
    "url": PRUSSIA_PERMALINK,
}
POLAND_SOURCE = {
    "name": "CShapes 2.0 (Schvitz, Rüegger, Girardin, Cederman, Weidmann, Gleditsch 2022)",
    "licence": "CC BY-NC-SA 4.0",
    "url": "https://icr.ethz.ch/data/cshapes/",
}

PRUSSIA_WHAT_IT_IS = """The plan called this "the HGIS Germany 1820 state boundaries". It is not quite that, in three ways.
- **There is no 1820 file to take Prussia from.** HistoGIS keeps one outline per state for each stretch of time in which that state's border did not change. Its record named "German States Stateborders 1820" holds four small Saxon duchies and nothing else. Prussia's outline is this one, and its dates cover 1 January 1816 directly, so no later map stands in for 1816.
- **The outline is HistoGIS's own work, not the HGIS Germany file.** HistoGIS describes it: "Geometries of the features in the data sets (the administrative units) were adopted from data provided by the Census Mosaic Project, http://www.censusmosaic.org/. A stateborders data set was created by merging the features provided, editing them where necessary (using additional spatial data) and adding attribute information, such as state name and administrative type. Attributes of the features were then compared to data provided by the HGIS Germany Project". The HGIS Germany file itself was not downloaded and not compared.
- **The licence upstream is stricter than the licence on the label.** See "Licence" above. The credit line also names "© OpenStreetMap contributors", whose own licence (the Open Database Licence) is share-alike; HistoGIS says nothing more about that.

**Judgment calls:** HistoGIS's outline and its dates are taken as published, and the outline is treated as non-commercial. See `specs/decisions/truth-history-prussia-source.md`."""

# Spot checks: (place, longitude, latitude, inside the outline?, what it shows). Positions are approximate and typed
# by hand; they only ever answer "inside or outside?" and are never written into a border.
PRUSSIA_PLACES = [
    ("Königsberg", 20.51, 54.71, True, "East Prussia."),
    ("Danzig", 18.65, 54.35, True, "West Prussia."),
    ("Posen", 16.93, 52.41, True, "The province of Posen."),
    ("Greifswald", 13.38, 54.09, True, 'Swedish Pomerania, handed to Prussia before the target date: "Die Übergabe an Preußen erfolgte am 23. Oktober 1815." https://de.wikipedia.org/wiki/Greifswald'),
    ("Saarbrücken", 6.99, 49.24, True, 'Taken over from France before the target date: "Am 30. November 1815 erfolgte [...] die feierliche Besitzergreifung Saarbrückens und der übrigen Saarorte". https://de.wikipedia.org/wiki/Saarbrücken'),
    ("Arnsberg", 8.06, 51.40, True, "The Duchy of Westphalia, which became Prussian only **after** the target date (see below)."),
    ("St. Wendel", 7.17, 49.47, False, "The Principality of Lichtenberg (see below)."),
    ("Birkenfeld", 7.17, 49.65, False, "The Principality of Birkenfeld (see below)."),
    ("Meisenheim", 7.67, 49.71, False, "The district of Meisenheim (see below)."),
    ("Emden", 7.21, 53.37, False, 'East Frisia, given up before or around the target date: "Preußen musste Ostfriesland an das Königreich Hannover abtreten." https://de.wikipedia.org/wiki/Ostfriesland The day of the hand-over was not found.'),
]
POLAND_PLACES = [
    ("Danzig", 18.65, 54.35, False, 'The Free City of Danzig was not part of Poland; CShapes has it as its own record. It "remained distinct from both the post-war Weimar Republic and the newly independent Polish Republic". https://en.wikipedia.org/wiki/Free_City_of_Danzig'),
    ("Gdynia", 18.53, 54.52, True, "Poland's strip of Baltic coast."),
    ("Wilno (Vilnius)", 25.28, 54.69, True, "Today in Lithuania."),
    ("Lwów (Lviv)", 24.03, 49.84, True, "Today in Ukraine."),
]

PRUSSIA_CHANGES = """**By the source's own dating there is none:** HistoGIS gives this one outline the dates 9 June 1815 to 31 May 1834, and its next outline of Prussia starts on 1 June 1834.

**Reading about the places along the border says otherwise.** The outline shows the settlement of the Congress of Vienna as it stood once the hand-overs listed below were finished (the last one found is dated April 1817). Some of them came after 1 January 1816. **Judgment call: the outline is used for 1 January 1816 anyway**, because the spec asks for this source and the differences found are small pieces of a 275,000 km² kingdom. Their sizes were not measured, except where a page gives one.

Dated after 1 January 1816, and already shown in the outline:
- **The Duchy of Westphalia (around Arnsberg) is inside.** On the target date it still belonged to Hesse-Darmstadt: "Doch dauerte es noch bis zum 15. Juli 1816, bis der Großherzog von Hessen-Darmstadt es abtrat." https://de.wikipedia.org/wiki/Herzogtum_Westfalen This is the largest difference found.
- **The Principality of Lichtenberg (around St. Wendel, 537 km²) is outside.** Saxe-Coburg-Saalfeld took it over later in the year: "Am 11. September 1816 erfolgte die förmliche Besitzergreifung." It was sold to Prussia "mit Staatsvertrag vom 31. Mai 1834", which is the day this outline ends. https://de.wikipedia.org/wiki/Fürstentum_Lichtenberg
- **Meisenheim (176 km²) is outside.** "Der Landgraf von Hessen-Homburg erhielt ebenfalls noch im September 1816 den Kanton Meisenheim". https://de.wikipedia.org/wiki/Département_de_la_Sarre (area: https://de.wikipedia.org/wiki/Oberamt_Meisenheim)
- **Birkenfeld is outside.** "Am 16. April 1817 ging das Gebiet unter dem Namen „Fürstentum Birkenfeld“ in den Besitz der Oldenburger." https://de.wikipedia.org/wiki/Fürstentum_Birkenfeld
- For Lichtenberg, Meisenheim and Birkenfeld, **who held the land on 1 January 1816 was not established**: no page read says so directly. So it is not known whether the outline is right or wrong about them on the target date.

Found in reading, dated 1816 to 1819, and **not tested** against the outline (too small for a hand-typed point, or the place is not named):
- Exchanges with the Schwarzburg principalities, June 1816: "Am 15. Juni 1816 wurde das Amt Ebeleben dem Staatsgebiet von Schwarzburg-Sondershausen angegliedert". https://de.wikipedia.org/wiki/Teilung_des_Königreiches_Sachsen
- The Wittgenstein principalities and Nassau-Siegen: "1817 folgten die Wittgensteiner Fürstentümer [...] sowie das Fürstentum Nassau-Siegen." https://de.wikipedia.org/wiki/Provinz_Westfalen
- The border with the Netherlands, fixed by treaties signed at Aachen (26 June 1816) and Kleve (7 October 1816). https://nl.wikipedia.org/wiki/Traktaat_van_Aken https://nl.wikipedia.org/wiki/Traktaat_van_Kleef
- The border with Saxony, exchanged in places in 1818 and settled on 28 August 1819. https://de.wikipedia.org/wiki/Teilung_des_Königreiches_Sachsen

What was checked: the ten spot checks above, HistoGIS's catalogue of Prussia outlines and their dates, and the pages cited here, read on 2026-11-09. All are encyclopedia pages, not treaties. No treaty text was read.

**Area.** No exact published area for 1816 was found. The German Historical Museum gives a round figure: "Die Fläche der preußischen Herrschaft umfasste nun ungefähr 280.000 km2". https://www.dhm.de/lemo/kapitel/vormaerz-und-revolution/wiener-kongress/neuordnung-europas-181415.html The outline measures 1.6% less than that round figure."""

POLAND_LICENCE_NOTE = """- **Where the licence is stated.** Only on the download page: "CShapes by Schvitz, Rüegger, Girardin, Cederman, Weidmann, Gleditsch is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License." The data file carries no licence text. The "codebook" offered beside it is an instruction sheet for the project's coders and has none either. The library record that some catalogues point to (https://doi.org/10.3929/ethz-b-000487987) is the journal article about the dataset, licensed CC BY-NC 4.0 without the share-alike part, which is probably why catalogues disagree. **Judgment call:** the download page speaks for the data, and it is also the stricter of the two."""

POLAND_NOTES = """- **Published area:** "388 634 km² (1 stycznia 1938 r.)" https://pl.wikipedia.org/wiki/II_Rzeczpospolita The shape measures {off:+.2f}% against it.
- **One outline for 24 years.** CShapes uses this outline for the whole of {start} to {end}. Its coding rules leave out any change smaller than 10,000 km² and wartime changes that were later undone (its codebook, page 4). So the land Poland took from Czechoslovakia after the target date ("po zajęciu Zaolzia w październiku 1938 r.", same page as the area) is not in the dataset at all, and no change of that size falls before 1 January 1938 that the outline would be missing by those rules.
- **It is coarse.** The whole border is {points} points. Compare the Prussia outline, which has about seven times as many for a smaller country.
- Spot checks, repeated on every build. Positions are approximate, typed by hand, and only ever answer "inside or outside?".
{checks}"""

PRUSSIA_MD = """# Source: {name}

- **Source:** HistoGIS, Austrian Academy of Sciences (Austrian Centre for Digital Humanities and Cultural Heritage). Shape 10039: `Preußen`, type `Kingdom`, which HistoGIS dates **{start} to {end}**. HistoGIS files it under its record "{source_name}".
- **File:** `{file}` from {url} (permanent link to the same shape: {permalink})
- **Checksum (SHA-256):** `{sha}`
- **Fetched:** {fetched}
- **Licence, as published:** Creative Commons Attribution 4.0 (CC BY 4.0), which by itself would let anyone copy, change and publish the outline, also commercially, with credit. The HistoGIS imprint: "This website and its content is, unless indicated otherwise, licensed under a creative commons CC-BY 4.0 International licence (Attribution)." https://histogis.acdh.oeaw.ac.at/imprint The shape's own record states no other licence.
- **Licence, upstream: treat this outline as non-commercial.** HistoGIS built it from Census Mosaic files, and the Mosaic project's terms are narrower: "The data provided on this page can be freely used for non-commercial scientific purposes, as long as you register as a user with the Mosaic project and the source of the data is properly cited." https://mosaic.ipums.org/historical-gis-datafiles (read 2026-11-09). HistoGIS does not say how the two fit together. Until someone asks HistoGIS, this repo credits both and makes no commercial use of the outline. Maintainer, 2026-11-09, asked whether to include it with this flagged: "Yes, flagged".
- **Credit, as HistoGIS asks for it:** Antonia Dückelmann / Peter Paul Marckhgott-Sanabria, "German Confederation State Borders 1830", based on Census Mosaic: German Union, 1830; Woldan: Floder, Oesterreich, 1835; Census Mosaic: Europe Main, 1900 and © OpenStreetMap contributors published by Histogis.
- **Built by:** `uv run python -m pipeline.prep_history`. Nothing here is edited by hand.

## What this source is, and is not
{what_it_is}

## Edits
1. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

Nothing else. No piece was dropped, no hole was filled, no point was moved, added or removed.

## What the shape includes
- {described}. HistoGIS lists the area as {listed:,.0f} km².
- Enclaves (other states' land wholly inside Prussia, such as the Anhalt duchies) are holes, as in the source.
- Where its land lies on today's map (Natural Earth 1:50m borders):
{breakdown}
- Only {in_foil:.1f}% of it lies inside today's Germany, the foil.

## The check the spec asks for first: are the eastern provinces in?
Yes. East Prussia, West Prussia and Posen lay outside the German Confederation, so a map of "the German states" could
have left them out. This outline has them: the build stops unless more than 1,000 km² of the shape lies in each of
today's Poland, Russia (the Kaliningrad region, once northern East Prussia) and Lithuania (the Memel strip).

Spot checks, repeated on every build. Town positions are approximate, typed by hand to two decimals, and used only
to ask "inside or outside?". None of them is written into a border.
{checks}

## Border changes between 1816 and 1820
{changes}

{foil}
"""

POLAND_MD = """# Source: {name}

- **Source:** CShapes 2.0 (Schvitz, Rüegger, Girardin, Cederman, Weidmann and Gleditsch, ETH Zurich). The one record for Poland (number {gwcode} in the Gleditsch and Ward list of states) whose dates contain 1 January 1938: valid **{start} to {end}**.
- **File:** `{file}` from {url} (download page: https://icr.ethz.ch/data/cshapes/)
- **Checksum (SHA-256):** `{sha}`
- **Fetched:** {fetched}
- **Licence:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0). In plain words: you may copy and change this outline **only for non-commercial use**, you must credit the authors, and anything you build from it and share **must carry this same licence**. The MIT licence on this repo's code does not apply to this folder.
{licence_note}
- **Credit, as the authors ask for it:** Schvitz, Guy, Seraina Rüegger, Luc Girardin, Lars-Erik Cederman, Nils Weidmann, and Kristian Skrede Gleditsch. 2022. "Mapping The International System, 1886-2017: The CShapes 2.0 Dataset." Journal of Conflict Resolution 66(1): 144–61.
- **Built by:** `uv run python -m pipeline.prep_history`. Nothing here is edited by hand.

## Edits
1. The source stores this border as a single Polygon. It was wrapped, unchanged, as a MultiPolygon with one piece, the form every target uses.
2. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

## What the shape includes
- {described}. CShapes lists the area as {listed:,.0f} km².
- Where its land lies on today's map (Natural Earth 1:50m borders):
{breakdown}
- {in_foil:.1f}% of it lies inside today's Poland, the foil. Its easternmost point is at {east:.2f}°E; today's Poland ends at {foil_east:.2f}°E.
{notes}

{foil}
"""


def prussia() -> tuple[dict, MultiPolygon]:
    """The Kingdom of Prussia as HistoGIS has it. Stops if the record is not the one this script was written for."""
    record = json.loads(fetch(PRUSSIA_URL, PRUSSIA_SHA256).read_text())
    p = record["properties"]
    if (p["title"], p["adm_name"]) != ("Preußen", "Kingdom") or not p["start_date"] <= "1816-01-01" <= p["end_date"]:
        sys.exit("prep_history: the HistoGIS record is not the Kingdom of Prussia valid on 1 January 1816")
    return p, to_shape(record["geometry"])


def poland(year: int, month: int, day: int) -> tuple[dict, MultiPolygon]:
    """The one CShapes record for Poland whose dates contain the given day."""
    features = json.loads(fetch(CSHAPES_URL, CSHAPES_SHA256).read_text())["features"]
    valid = [f for f in features if (p := f["properties"])["gwcode"] == POLAND_GWCODE
             and (p["gwsyear"], p["gwsmonth"], p["gwsday"]) <= (year, month, day) <= (p["gweyear"], p["gwemonth"], p["gweday"])]
    if len(valid) != 1:
        sys.exit(f"prep_history: expected one CShapes record for Poland on {year}-{month}-{day}, found {len(valid)}")
    return valid[0]["properties"], MultiPolygon([to_shape(valid[0]["geometry"])])  # the source has a single Polygon


def on_todays_map(shape: MultiPolygon, countries: dict) -> list[tuple[str, float]]:
    """(modern country, km² of `shape` inside it), largest first, measured against Natural Earth's modern borders."""
    parts = [(attrs["ADMIN"], area_km2(shape.intersection(modern)))
             for attrs, modern in countries.values() if modern.intersects(shape)]
    return sorted(parts, key=lambda part: -part[1])


def breakdown_md(parts: list[tuple[str, float]], total: float) -> str:
    """One line per modern country holding at least 0.5% of the shape; the rest are lumped and explained."""
    big = [(name, km2) for name, km2 in parts if km2 / total >= 0.005]
    lines = [f"  - {name}: {km2:,.0f} km² ({km2 / total * 100:.1f}%)" for name, km2 in big]
    rest = total - sum(km2 for _, km2 in big)
    lines.append(f"  - Everything else: {rest:,.0f} km² ({rest / total * 100:.1f}%). This is sea between the two maps' "
                 "coastlines and thin slivers along borders, because the two maps were not drawn from the same survey.")
    return "\n".join(lines)


def describe(shape: MultiPolygon) -> str:
    holes = sum(len(p.interiors) for p in shape.geoms)
    points = sum(len(p.exterior.coords) + sum(len(h.coords) for h in p.interiors) for p in shape.geoms)
    return f"{len(shape.geoms)} separate piece(s), {holes} hole(s), {points} points, {area_km2(shape):,.0f} km² on the WGS84 ellipsoid"


def write_history_target(*, id: str, name: str, date: str, truth: MultiPolygon, foil: MultiPolygon, foil_label: str,
                         source: dict, source_md: str) -> None:
    """The truth-modern folder, plus foil.geojson, the foil on the preview, and who to credit in target.toml."""
    folder = ROOT / "targets" / id
    write_target(folder, id=id, name=name, date=date, shape=truth, source_md=source_md)
    with (folder / "target.toml").open("a") as toml:  # both licences require credit wherever the outline is shown
        toml.write("\n[source]\n" + "".join(f'{key} = "{value}"\n' for key, value in source.items()))
    wound = MultiPolygon([orient(p, 1.0) for p in foil.geoms])
    (folder / "foil.geojson").write_text(json.dumps(mapping(wound), separators=(",", ":")) + "\n")
    draw_preview(truth, name, folder / "preview.png", outlines=[(foil, foil_label)])
    print(f"prep_history: {id:<13} truth {describe(truth)}; foil {describe(foil)}")


def foil_md(attrs: dict, code: str, version: str) -> str:
    return f"""## The foil (`foil.geojson`)
The modern country a model might draw instead of the historical one. It is never scored as truth.
- **Source:** Natural Earth, Admin 0 – Countries, 1:50m, version {version}. Record `{attrs['ADMIN']}` (`ADM0_A3` = `{code}`).
- **File:** `{NE_URL.rsplit('/', 1)[1]}` from {NE_URL}
- **Checksum (SHA-256):** `{NE_SHA256}`
- **Fetched:** {NE_FETCHED}
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Edits:** ring order changed to the GeoJSON convention. No coordinate changed."""


def spot_checks(shape: MultiPolygon, places: list) -> str:
    """One line per place saying inside or outside. Stops if a place is not where this script expects it."""
    lines = []
    for name, lon, lat, expected, why in places:
        if shape.contains(Point(lon, lat)) != expected:
            sys.exit(f"prep_history: {name} should be {'inside' if expected else 'outside'} the shape and is not")
        lines.append(f"- {name} ({lat}°N, {lon}°E): **{'inside' if expected else 'outside'}**. {why}")
    return "\n".join(lines)


def main() -> int:
    countries = {attrs["ADM0_A3"]: (attrs, shape) for attrs, shape in read_shapefile(fetch(NE_URL, NE_SHA256), NE_STEM)}
    with zipfile.ZipFile(CACHE / f"{NE_STEM}.zip") as z:
        version = z.read(f"{NE_STEM}.VERSION.txt").decode().strip()

    # Prussia
    name = "the Kingdom of Prussia as of 1 January 1816"
    p, truth = prussia()
    (attrs, foil), total = countries["DEU"], area_km2(truth)
    today = dict(on_todays_map(truth, countries))
    assert truth.is_valid and len(truth.geoms) >= 2, "Prussia must be a valid shape in at least two pieces"
    assert min(today.get(c, 0) for c in ("Poland", "Russia", "Lithuania")) > 1000, "the eastern provinces are missing"
    write_history_target(
        id="prussia-1815", name=name, date="1816-01-01", truth=truth, foil=foil,
        foil_label="Red line: Germany today, the modern foil", source=PRUSSIA_SOURCE,
        source_md=PRUSSIA_MD.format(
            name=name, url=PRUSSIA_URL, file=PRUSSIA_URL.rsplit('/', 1)[1], sha=PRUSSIA_SHA256, permalink=PRUSSIA_PERMALINK, fetched=FETCHED,
            start=p["start_date"], end=p["end_date"], source_name=p["source_name"], what_it_is=PRUSSIA_WHAT_IT_IS, listed=p["spatial_extent_sqm"],
            described=describe(truth), breakdown=breakdown_md(list(today.items()), total),
            in_foil=today["Germany"] / total * 100, checks=spot_checks(truth, PRUSSIA_PLACES), changes=PRUSSIA_CHANGES,
            foil=foil_md(attrs, "DEU", version)))

    # Poland
    name = "Poland as of 1 January 1938"
    q, truth = poland(1938, 1, 1)
    (attrs, foil), total = countries["POL"], area_km2(truth)
    today = dict(on_todays_map(truth, countries))
    assert truth.is_valid and truth.bounds[2] > foil.bounds[2], "Poland in 1938 must reach east of Poland today"
    start = f"{q['gwsyear']}-{q['gwsmonth']:02}-{q['gwsday']:02}"
    end = f"{q['gweyear']}-{q['gwemonth']:02}-{q['gweday']:02}"
    write_history_target(
        id="poland-1938", name=name, date="1938-01-01", truth=truth, foil=foil,
        foil_label="Red line: Poland today, the modern foil", source=POLAND_SOURCE,
        source_md=POLAND_MD.format(
            name=name, url=CSHAPES_URL, file=CSHAPES_URL.rsplit('/', 1)[1], sha=CSHAPES_SHA256, fetched=FETCHED, gwcode=POLAND_GWCODE,
            start=start, end=end,
            listed=q["area"], described=describe(truth), breakdown=breakdown_md(list(today.items()), total),
            in_foil=today["Poland"] / total * 100, east=truth.bounds[2], foil_east=foil.bounds[2],
            licence_note=POLAND_LICENCE_NOTE,
            notes=POLAND_NOTES.format(off=(total - POLAND_PUBLISHED_KM2) / POLAND_PUBLISHED_KM2 * 100, start=start, end=end,
                                      points=len(truth.geoms[0].exterior.coords),
                                      checks="  " + spot_checks(truth, POLAND_PLACES).replace("\n", "\n  ")),
            foil=foil_md(attrs, "POL", version)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
