# Source: the contiguous United States (the lower 48 states) as of 1 January 2024

- **Source:** Natural Earth, Admin 0 – Countries, 1:50m, version 5.1.1. Record `United States of America` (`ADM0_A3` = `USA`).
- **File:** `ne_50m_admin_0_countries.zip` from https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip
- **Checksum (SHA-256):** `5fed433373581fa648920435f937d95f2d3c0200e067409c6478dcdf1b853139`
- **Fetched:** 2026-11-09
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Built by:** `uv run python -m pipeline.prep`. Nothing here is edited by hand.

## Edits
1. Kept only the pieces whose centre lies inside longitude -125.0 to -66.0, latitude 24.0 to 50.0. This removes Alaska and Hawaii. Territories (Puerto Rico, Guam and others) are separate records in the source and were never part of the shape.
2. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

## What the shape includes
- 52 separate piece(s), 2490 points.
- Lakes and rivers inside the border are not cut out: the shape is the territory inside the border and coastline.
- Disputed areas follow Natural Earth's default (de facto) view. Nothing was added or removed for a dispute.
- The border with Canada runs through the Great Lakes, and the shape counts the United States' side of the lakes as territory. That water is in the published total but not in the land figure.

## Area check
- Area on the WGS84 ellipsoid: measured 7,940,194 km² against a published land area of 7,663,942 km²: +3.6% (and -1.7% against the published total, 8,080,464 km²).
- **Outside the 2% the spec asks for.**
- Published figure from: Wikipedia, "Contiguous United States", which cites the CIA World Factbook's area listing. Read on 2026-11-09.
