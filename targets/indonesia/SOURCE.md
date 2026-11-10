# Source: Indonesia as of 1 January 2024

- **Source:** Natural Earth, Admin 0 – Countries, 1:10m, version 5.1.1. Record `Indonesia` (`ADM0_A3` = `IDN`).
  - File: `ne_10m_admin_0_countries.zip` from https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip
  - Checksum (SHA-256): `ce1ac7036499a0edd641fbc093cd209a98f96a49d2eca8480aaacad35138a7f6`
- **Lakes from:** Natural Earth, Lakes + Reservoirs, 1:10m, version 5.0.0.
  - File: `ne_10m_lakes.zip` from https://naciscdn.org/naturalearth/10m/physical/ne_10m_lakes.zip
  - Checksum (SHA-256): `0803a06f9c3cb4671d89b68c48b142aad9366ba40f665245e12a913fbc61722a`
- **Fetched:** 2026-11-09 (both files)
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Built by:** `uv run python -m pipeline.prep`. Nothing here is edited by hand.

## Edits
1. Looked for lakes that reach the edge of the shape (the border or the coast runs through or touches them). The lakes file has none here, so nothing was cut.
2. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

## What the shape includes
- 264 separate piece(s), 19565 points, no holes.
- The shape is the outline of the land (`specs/decisions/004-truth-is-land.md`). Lakes that reach the edge are cut out. Lakes that lie wholly inside stay in, because an outline cannot leave them out without a hole: 3 in the lakes file, 1,502 km² in all. Rivers are not cut out.
- Disputed areas follow Natural Earth's default (de facto) view. Nothing was added or removed for a dispute.
- The measured area falls between the published land and total figures. The two differ by 93,000 km² of inland water, but the lakes file holds only three lakes inside Indonesia and none reaches the edge, so cutting lakes cannot bring the shape to the land figure. The World Bank publishes a land area of 1,892,410 km² for 2023 (indicator AG.LND.TOTL.K2, from the FAO; read 2026-11-09), and the shape is within 2% of that one. Which published figure is the right yardstick is not settled.

## Area check
- Area on the WGS84 ellipsoid: measured 1,879,827 km² against a published land area of 1,811,569 km²: +3.8% (and -1.3% against the published total, 1,904,569 km²).
- **Outside the 2% the spec asks for.**
- Published figure from: Wikipedia, "Geography of Indonesia"; the total is cited there to the CIA World Factbook, the land figure is uncited. Read on 2026-11-09.
