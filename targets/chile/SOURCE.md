# Source: Chile as of 1 January 2024

- **Source:** Natural Earth, Admin 0 – Countries, 1:10m, version 5.1.1. Record `Chile` (`ADM0_A3` = `CHL`).
  - File: `ne_10m_admin_0_countries.zip` from https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip
  - Checksum (SHA-256): `ce1ac7036499a0edd641fbc093cd209a98f96a49d2eca8480aaacad35138a7f6`
- **Lakes from:** Natural Earth, Lakes + Reservoirs, 1:10m, version 5.0.0.
  - File: `ne_10m_lakes.zip` from https://naciscdn.org/naturalearth/10m/physical/ne_10m_lakes.zip
  - Checksum (SHA-256): `0803a06f9c3cb4671d89b68c48b142aad9366ba40f665245e12a913fbc61722a`
- **Fetched:** 2026-11-09 (both files)
- **Licence:** public domain. Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." https://www.naturalearthdata.com/about/terms-of-use/
- **Built by:** `uv run python -m pipeline.prep`. Nothing here is edited by hand.

## Edits
1. Cut out the 3 lakes that reach the edge of the shape, as the lakes file draws them: Lago Argentino, Lago Buenos Aires, Lago San Martín. A lake reaches the edge when the border or the coast runs through it or touches it, or when it is joined to a lake that does. This removed 1,618 km². Where a lake's outline crosses the border, the crossing point is computed; no other coordinate is new.
2. Ring order was changed to the GeoJSON convention (outlines counter-clockwise). No coordinate changed.

## What the shape includes
- 164 separate piece(s), 17496 points, no holes.
- The shape is the outline of the land (`specs/decisions/004-truth-is-land.md`). Lakes that reach the edge are cut out. Lakes that lie wholly inside stay in, because an outline cannot leave them out without a hole: 5 in the lakes file, 1,823 km² in all. Rivers are not cut out.
- Disputed areas follow Natural Earth's default (de facto) view. Nothing was added or removed for a dispute.
- The shape includes Chile's Pacific islands as Natural Earth has them. The westernmost piece is at 109.4°W (Easter Island), far from the mainland, and it widens the frame of the picture a great deal.

## Area check
- Area on the WGS84 ellipsoid: measured 734,975 km² against a published land area of 743,812 km²: -1.2% (and -2.8% against the published total, 756,102 km²).
- **Within the 2% the spec asks for.**
- Published figure from: Wikipedia, "Geography of Chile"; the total is cited there to the CIA World Factbook, the land figure is uncited. Both exclude the Antarctic claim and include Easter Island. Read on 2026-11-09.
