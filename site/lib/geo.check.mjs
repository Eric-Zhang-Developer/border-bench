// The smallest check that fails if the shared frame breaks. Runs before every build: node lib/geo.check.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import { written } from "./answer.ts";
import { chart, plate } from "./geo.ts";
import { loadRuns } from "./results.ts";

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

// The replay follows each vertex of a ring in order, and never loses or reorders one when points are added.
{
  const ring = [[0, 0], [3, 0], [3, 0.1], [0, 0]];
  const placed = chart(mp(square(0, 0, 3, 3)), [mp([ring])]).shapes[0].rings[0][0];
  assert.equal(placed.stops.length, ring.length);
  assert.ok(placed.stops.every((s, i) => i === 0 || s > placed.stops[i - 1]), "stops are out of order");
  assert.equal(placed.stops.at(-1), placed.pts.length - 1);
  assert.deepEqual(placed.pts[placed.stops[0]], placed.pts[placed.stops[3]], "a closed ring does not end where it began");
}

// The head-to-head replays the points each model wrote, read from its saved answer. They must be the saved
// outline: the same pieces in the same order, every written point present in order (to the outline's 4 decimals),
// and nothing between two of them but points on the straight edge that joins them. The count must be the file's.
const real = new URL("../../results/results.json", import.meta.url);
let replayed = 0;
if (fs.existsSync(real)) {
  const results = JSON.parse(fs.readFileSync(real, "utf8"));
  const runs = loadRuns(results.prompt.id);
  const near = (a, b) => Math.abs(a[0] - b[0]) < 6e-5 && Math.abs(a[1] - b[1]) < 6e-5;
  for (const target of results.targets)
    for (const model of target.models) {
      const run = runs.samples(model.id, target.id)[model.median_sample];
      const own = run?.raw ? written(run.raw) : null;
      if (!model.outline) continue;
      const where = `${model.id} on ${target.id}`;
      assert.ok(own, `${where}: the saved answer could not be read`);
      const saved = model.outline.coordinates;
      assert.deepEqual(own.shape.map((p) => p.length), saved.map((p) => p.length), `${where}: different pieces`);
      let count = 0;
      own.shape.forEach((polygon, pi) =>
        polygon.forEach((ring, ri) => {
          const outline = saved[pi][ri];
          let at = 0;
          ring.forEach((point, i) => {
            const from = at;
            while (at < outline.length && !near(outline[at], point)) at++;
            assert.ok(at < outline.length, `${where}: point ${i} of piece ${pi} is not in the saved outline, in order`);
            for (let j = from; j < at; j++) {
              const [a, b, q] = [ring[i - 1], point, outline[j]];
              const cross = (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]);
              assert.ok(i > 0 && Math.abs(cross) < 2e-4 * Math.max(1, Math.hypot(b[0] - a[0], b[1] - a[1])), `${where}: the saved outline leaves the written edge`);
            }
            at++;
          });
          assert.equal(at, outline.length, `${where}: the saved outline goes on after the last written point`);
          count += ring.length - (own.added[pi][ri] ? 1 : 0);
        }),
      );
      assert.equal(count, model.points, `${where}: point count`);
      replayed++;
    }
}

process.stdout.write(`geo.check: ok${replayed ? ` (${replayed} replays match their saved outlines)` : ""}\n`);
