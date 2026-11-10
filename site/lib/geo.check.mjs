// The smallest check that fails if the shared frame breaks. Runs before every build: node lib/geo.check.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import { plate } from "./geo.ts";

const square = (x0, y0, x1, y1) => [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]];
const mp = (...polys) => ({ type: "MultiPolygon", coordinates: polys });
const target = (truth, ...outlines) => ({ truth, foil: null, baselines: [], models: outlines.map((outline) => ({ outline })) });
const width = (d) => { const xs = [...d.matchAll(/(-?[\d.]+),/g)].map((m) => +m[1]); return Math.max(...xs) - Math.min(...xs); };

// A drawing identical to the truth gives the identical path and stays inside the frame.
let p = plate(target(mp(square(10, 10, 20, 20)), mp(square(10, 10, 20, 20))));
assert.deepEqual(p.shapes[0].d, p.truth);
assert.equal(p.shapes[0].off, "");

// A failed drawing is null. A drawing on the far side of the world is flagged as off the frame,
// and it does not shrink the truth to a dot: the truth keeps at least a third of the frame's width.
p = plate(target(mp(square(10, 10, 20, 20)), null, mp(square(-170, -60, -150, -40))));
assert.equal(p.shapes[0], null);
assert.notEqual(p.shapes[1].off, "");
assert.ok(width(p.truth[0]) > p.w / 3, "a wild drawing shrank the truth");

// A very thin country still gets a frame at least half as wide as it is tall.
p = plate(target(mp(square(-71, -55, -70, -17))));
assert.ok(p.w / p.h >= 0.499 && p.w / p.h <= 1.801);

// A country cut in two by the antimeridian is framed as one country, not stretched around the globe.
p = plate(target(mp(square(170, 60, 180, 70), square(-180, 60, -170, 70))));
assert.ok(width(p.truth[0]) > p.w / 4, "the antimeridian split the frame");

// The committed sample file renders: one shape per baseline and model, on every target.
for (const t of JSON.parse(fs.readFileSync(new URL("../fixtures/results.json", import.meta.url), "utf8")).targets)
  assert.equal(plate(t).shapes.length, t.baselines.length + t.models.length);

process.stdout.write("geo.check: ok\n");
