# Source: Croatia as of 1 January 2024

- **Source:** Natural Earth, Admin 0 – Countries, 1:50m, version 5.1.1. Record `Croatia` (`ADM0_A3` = `HRV`).
- **File:** `ne_50m_admin_0_countries.zip` from https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip
- **Checksum (SHA-256):** `5fed433373581fa648920435f937d95f2d3c0200e067409c6478dcdf1b853139`
- **Fetched:** 2026-11-09
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Built by:** `uv run python -m pipeline.prep`. Nothing here is edited by hand.

## Edits
1. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

## What the shape includes
- 13 separate piece(s), 374 points.
- Lakes and rivers inside the border are not cut out: the shape is the territory inside the border and coastline.
- Disputed areas follow Natural Earth's default (de facto) view. Nothing was added or removed for a dispute.
- At 1:50 million the coast is drawn with few points and only 12 islands are kept (Wikipedia counts 1,246 islands and islets). The strip of Bosnian coast at Neum, which cuts Croatia's mainland in two, is not shown: the mainland is one piece.

## Area check
- Area on the WGS84 ellipsoid: measured 54,541 km² against a published total area of 56,594 km²: -3.6%.
- **Outside the 2% the spec asks for.**
- Published figure from: Wikipedia, "Geography of Croatia", which cites Croatia's Statistical Yearbook 2011. No separate land figure was found. Read on 2026-11-09.
