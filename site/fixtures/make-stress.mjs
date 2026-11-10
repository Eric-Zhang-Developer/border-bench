// Writes fixtures/stress.json: a results file full of awkward, made-up shapes, to test that real data will not
// break the page. Six targets, fifteen models. Every shape, name and score in it is invented; none is a result.
//
//   node fixtures/make-stress.mjs && BB_FIXTURE=stress.json npm run dev      (or: npm run stress)
//
// What it covers: an archipelago of 70 small islands, a very thin country, a country in two pieces with a modern
// foil, a country cut by the antimeridian, a country about 60 km wide, a failed drawing, a drawing with
// longitude and latitude swapped (far outside the frame), a spike that leaves the frame, a self-crossing outline,
// one loop drawn around a whole archipelago, a drawing over 400 points, one- and two-sample models, a long name.
// Scores are a rough overlap on a longitude/latitude grid, so the pictures and the numbers agree well enough to
// judge the layout. They are not the scorer's numbers.
import fs from "node:fs";

let seed = 20261109;
const rnd = () => {
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const r2 = (v) => Math.round(v * 100) / 100;
const r1 = (v) => Math.round(v * 10) / 10;

/** A lumpy closed shape. `from`/`to` in turns lets a caller draw half of one (for the antimeridian target). */
function blob(lon, lat, rx, ry, n = 80, bump = 0.25, from = 0, to = 1, waves = null) {
  waves ??= [1, 2, 3, 4, 5, 6].map((k) => [(rnd() * bump) / k, rnd() * 2 * Math.PI, k + 1]);
  const ring = [];
  for (let i = 0; i <= n; i++) {
    const a = 2 * Math.PI * (from + ((to - from) * i) / n);
    let r = 1;
    for (const [amp, phase, k] of waves) r += amp * Math.sin(k * a + phase);
    ring.push([r2(lon + rx * r * Math.cos(a)), r2(lat + ry * r * Math.sin(a))]);
  }
  if (to - from === 1) ring[n] = ring[0];
  else ring.push(ring[0]);
  return [ring];
}

const mp = (polys) => ({ type: "MultiPolygon", coordinates: polys });
const bbox = (polys) => {
  const xs = polys.flat(2).map((p) => p[0]), ys = polys.flat(2).map((p) => p[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
};
const area = (ring) => Math.abs(ring.reduce((s, [x, y], i) => s + (i ? ring[i - 1][0] * y - x * ring[i - 1][1] : 0), 0)) / 2;

function inside([x, y], polys) {
  return polys.some((poly) => {
    let hit = false;
    for (const ring of poly)
      for (let i = 1; i < ring.length; i++) {
        const [x1, y1] = ring[i - 1], [x2, y2] = ring[i];
        if (y1 > y !== y2 > y && x < ((x2 - x1) * (y - y1)) / (y2 - y1) + x1) hit = !hit;
      }
    return hit;
  });
}

/** Rough overlap %: shared cells over cells covered by either, on a 240 x 240 longitude/latitude grid. */
function overlap(truth, drawn) {
  if (!drawn) return 0;
  const [x0, y0, x1, y1] = bbox([...truth, ...drawn]);
  let both = 0, either = 0;
  for (let i = 0; i < 240; i++)
    for (let j = 0; j < 240; j++) {
      const p = [x0 + ((x1 - x0) * (i + 0.5)) / 240, y0 + ((y1 - y0) * (j + 0.5)) / 240];
      const w = Math.cos((Math.max(-89, Math.min(89, p[1])) * Math.PI) / 180);
      const a = inside(p, truth), b = inside(p, drawn);
      if (a && b) both += w;
      if (a || b) either += w;
    }
  return either ? r1((100 * both) / either) : 0;
}

/** A model's attempt: fewer pieces, fewer points, more wobble and more drift the lower `q` is (0 to 1). */
function attempt(truth, q, points = null) {
  const [x0, y0, x1, y1] = bbox(truth);
  const span = Math.min(Math.max(x1 - x0, y1 - y0), 4 * Math.min(x1 - x0, y1 - y0));
  const err = (1 - q) ** 1.5;
  const dx = (rnd() - 0.5) * span * 0.3 * err, dy = (rnd() - 0.5) * span * 0.3 * err;
  const grow = 1 + (rnd() - 0.5) * 0.5 * err;
  const pieces = [...truth].sort((a, b) => area(b[0]) - area(a[0]));
  const keep = Math.max(1, Math.round(pieces.length * q ** 1.5));
  return pieces.slice(0, keep).map(([ring]) => {
    const [a0, b0, a1, b1] = bbox([[ring]]);
    const cx = (a0 + a1) / 2, cy = (b0 + b1) / 2, local = Math.min(a1 - a0, b1 - b0) * 0.35 * err;
    const n = points ?? Math.max(4, Math.round((ring.length - 1) * (0.06 + 0.94 * q)));
    const out = [];
    for (let i = 0; i < n; i++) {
      const at = (i * (ring.length - 1)) / n, k = Math.floor(at), f = at - k;
      const x = ring[k][0] + (ring[k + 1][0] - ring[k][0]) * f, y = ring[k][1] + (ring[k + 1][1] - ring[k][1]) * f;
      out.push([r2(cx + (x - cx) * grow + dx + (rnd() - 0.5) * local), r2(cy + (y - cy) * grow + dy + (rnd() - 0.5) * local)]);
    }
    out.push(out[0]);
    return [out];
  });
}

const rectangle = (polys) => {
  const [x0, y0, x1, y1] = bbox(polys);
  return [[[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]];
};
const circle = (polys) => {
  const [x0, y0, x1, y1] = bbox(polys);
  const lat = (y0 + y1) / 2, cos = Math.cos((lat * Math.PI) / 180);
  const r = Math.sqrt((polys.reduce((s, p) => s + area(p[0]), 0) * cos) / Math.PI);
  return [blob((x0 + x1) / 2, lat, r / cos, r, 64, 0)];
};

// ---- the six targets -------------------------------------------------------------------------------------
const islands = Array.from({ length: 70 }, () => {
  const s = 0.15 + 2.6 * rnd() ** 3;
  return blob(r2(100 + 40 * rnd()), r2(-10 + 16 * rnd()), s, s * (0.4 + 0.5 * rnd()), 28, 0.3);
});

const thin = (() => {
  const left = [], right = [];
  for (let lat = -55; lat <= -17; lat += 0.5) {
    const lon = -140 + 1.5 * Math.sin(lat / 6) + 0.4 * Math.sin(lat / 1.7);
    left.push([r2(lon - 0.55), lat]);
    right.push([r2(lon + 0.55), lat]);
  }
  return [[[...left, ...right.reverse(), left[0]]]];
})();

const waves = [1, 2, 3, 4, 5, 6].map((k) => [(rnd() * 0.2) / k, 0, 2 * k]); // even waves: both halves meet at 180
const dateline = [blob(180, 65, 12, 5, 60, 0, 0.25, 0.75, waves), blob(-180, 65, 12, 5, 60, 0, -0.25, 0.25, waves)];
const datelineRound = [blob(180, 65, 9, 4, 32, 0, 0.25, 0.75, []), blob(-180, 65, 9, 4, 32, 0, -0.25, 0.25, [])];

const sample = { name: "Made-up stress fixture", licence: "No licence: invented shapes", url: "https://example.org/" };
const targets = [
  { id: "stress-blob", name: "Blobland as of 1 January 2024", kind: "modern",
    truth: [blob(15, 47, 6, 4, 160, 0.3), blob(23.5, 44, 0.6, 0.4, 24), blob(8, 42.5, 0.4, 0.5, 24)] },
  { id: "stress-islands", name: "The Scatter Islands as of 1 January 2024", kind: "modern", truth: islands },
  { id: "stress-thin", name: "Thinland as of 1 January 2024", kind: "modern", truth: thin },
  { id: "stress-two-piece", name: "Kingdom of Twinmark as of 1 January 1816", kind: "history",
    truth: [blob(8, 51, 2.5, 2, 70), blob(17.5, 53, 6, 3.2, 120)], foil: [blob(11, 50.5, 4.5, 3.6, 90)] },
  { id: "stress-dateline", name: "Dateline Republic as of 1 January 2024", kind: "modern", truth: dateline,
    rectangle: [[[[168, 60], [180, 60], [180, 70], [168, 70], [168, 60]]], [[[-180, 60], [-168, 60], [-168, 70], [-180, 70], [-180, 60]]]],
    circle: datelineRound },
  { id: "stress-speck", name: "Free City of Speck as of 1 January 1938", kind: "history",
    truth: [blob(30, 10, 0.3, 0.25, 40)], foil: [blob(30.3, 10.1, 0.6, 0.5, 40)] },
];

const N = 15;
const label = (k) => (k === 6 ? "Stress Model 7 Extended Thinking Preview" : k === 11 ? "S12" : `Stress Model ${k + 1}`);
const released = (k) => `${2023 + Math.floor((2 + 3 * k) / 12)}-${String(((2 + 3 * k) % 12) + 1).padStart(2, "0")}-01`;

function model(t, ti, k) {
  let drawn = attempt(t.truth, (0.96 * k) / (N - 1));
  const flags = { no_drawing: false, over_400_points: false, drew_modern: false };
  if (ti === 0 && k === 3) drawn = null;                                         // a failed drawing
  if (ti === 0 && k === 4) drawn[0][0].splice(10, 0, [95, 20]);                  // a spike far off the frame
  if (ti === 0 && k === 7) drawn = [[[[9, 43], [21, 51], [21, 43], [9, 51], [9, 43]]]]; // a self-crossing bow-tie
  if (ti === 0 && k === 9) drawn = attempt([t.truth[0]], 0.7, 620);              // far more than 400 points
  if (ti === 1 && k === 0) drawn = rectangle(t.truth);                           // one loop around all the sea
  if (ti === 2 && k === 5) drawn = drawn.map((p) => p.map((r) => r.map(([x, y]) => [y, x]))); // lon/lat swapped
  if (t.foil && k === 2) drawn = attempt(t.foil, 0.85);                          // drew the modern country
  if (drawn === null) flags.no_drawing = true;
  if (t.foil && k === 2) flags.drew_modern = true;
  const points = drawn ? drawn.reduce((s, p) => s + p[0].length - 1, 0) : 0;
  flags.over_400_points = points > 400;

  const score = overlap(t.truth, drawn);
  const count = k === 1 ? 1 : k === 8 ? 2 : 3;
  const spread = drawn ? [r1(Math.max(0, score - 12 * rnd())), score, r1(Math.min(100, score + 12 * rnd()))] : [0, 0, 0];
  // The median goes in a different sample slot from model to model, as it will in real runs.
  const scores = count === 1 ? [score] : count === 2 ? [score, spread[2]] : [[1, 0, 2], [0, 1, 2], [2, 0, 1]][k % 3].map((i) => spread[i]);
  return {
    id: `stress-model-${k + 1}`, label: label(k), released: released(k),
    scores, median_sample: scores.indexOf(score), score, points, outline: drawn && mp(drawn), flags,
  };
}

const results = {
  _about: "STRESS FIXTURE. Every shape, model and score here is made up to test the page's layout. Nothing is a real result.",
  schema: 1,
  prompt: { id: "p1", text: "Draw the land borders and coastline of {target} from memory. ...\n\n(Stress fixture: this is not the real prompt.)" },
  settings_note: "Each model ran with its default settings.",
  targets: targets.map((t, ti) => {
    const shapes = { rectangle: t.rectangle ?? rectangle(t.truth), circle: t.circle ?? circle(t.truth) };
    return {
      id: t.id, name: t.name, date: `${t.name.slice(-4)}-01-01`,
      kind: t.kind, source: sample, truth: mp(t.truth), foil: t.foil ? mp(t.foil) : null,
      baselines: ["rectangle", "circle"].map((id) => ({
        id, label: id[0].toUpperCase() + id.slice(1), score: overlap(t.truth, shapes[id]), outline: mp(shapes[id]),
      })),
      models: Array.from({ length: N }, (_, k) => model(t, ti, k)),
    };
  }),
};

fs.writeFileSync(new URL("./stress.json", import.meta.url), JSON.stringify(results));
process.stdout.write(`stress.json: ${results.targets.length} targets, ${N} models each\n`);
