# Source: Chile as of 1 January 2024

- **Source:** Natural Earth, Admin 0 – Countries, 1:50m, version 5.1.1. Record `Chile` (`ADM0_A3` = `CHL`).
- **File:** `ne_50m_admin_0_countries.zip` from https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip
- **Checksum (SHA-256):** `5fed433373581fa648920435f937d95f2d3c0200e067409c6478dcdf1b853139`
- **Fetched:** 2026-11-09
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Built by:** `uv run python -m pipeline.prep`. Nothing here is edited by hand.

## Edits
1. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

## What the shape includes
- 31 separate piece(s), 2006 points.
- Lakes and rivers inside the border are not cut out: the shape is the territory inside the border and coastline.
- Disputed areas follow Natural Earth's default (de facto) view. Nothing was added or removed for a dispute.
- The shape includes Chile's Pacific islands as Natural Earth has them. The westernmost piece is at 109.4°W (Easter Island), far from the mainland, and it widens the frame of the picture a great deal.

## Area check
- Area on the WGS84 ellipsoid: measured 737,680 km² against a published land area of 743,812 km²: -0.8% (and -2.4% against the published total, 756,102 km²).
- **Within the 2% the spec asks for.**
- Published figure from: Wikipedia, "Geography of Chile"; the total is cited there to the CIA World Factbook, the land figure is uncited. Both exclude the Antarctic claim and include Easter Island. Read on 2026-11-09.
