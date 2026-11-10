// Turns one target's borders and drawings into SVG path strings, all in one shared frame.
//
// Every tile of a target uses the same projection, the same scale and the same frame, so tiles can be compared.
// Shapes are read the way the scorer reads them (specs/decisions/002-grading.md): straight edges in
// longitude/latitude, with points added along each edge, then projected point by point to an equal-area
// projection centred on the truth. Nothing is repaired or reordered. d3-geo is used only as that point
// projection: its own path builder treats rings as spherical and would flip a ring wound the "wrong" way.
import { geoAzimuthalEqualArea } from "d3-geo";
import type { MultiPolygon, Target } from "./results";

/** One drawing: a path per polygon, and the frame edges it runs past ("n", "e", "s", "w" joined, or ""). */
export type Shape = { d: string[]; off: string };
export type Plate = { w: number; h: number; truth: string[]; foil: string[] | null; shapes: (Shape | null)[] };

type Pt = [number, number];
type Box = [number, number, number, number]; // x0, y0, x1, y1

const RAD = Math.PI / 180;
const STEP = 0.25; // degrees between added points; the scorer uses 0.1, which no screen can tell apart
const REACH = 1.8; // the frame grows to hold wild drawings, but never past this many times the truth's size
const PAD = 0.07; // breathing room, as a share of the frame's longer side
const TALLEST = 0.5; // width / height limits, so a very thin country still gets a usable tile
const WIDEST = 1.8;

/** Mean of the truth's vertices on the sphere: safe across the antimeridian and for any ring winding. */
function centre(mp: MultiPolygon): Pt {
  let x = 0, y = 0, z = 0;
  for (const poly of mp.coordinates)
    for (const ring of poly)
      for (const [lon, lat] of ring) {
        x += Math.cos(lat * RAD) * Math.cos(lon * RAD);
        y += Math.cos(lat * RAD) * Math.sin(lon * RAD);
        z += Math.sin(lat * RAD);
      }
  return [Math.atan2(y, x) / RAD, Math.atan2(z, Math.hypot(x, y)) / RAD];
}

function densify(ring: number[][]): Pt[] {
  const out: Pt[] = [];
  ring.forEach(([lon, lat], i) => {
    if (i > 0) {
      const [lon0, lat0] = ring[i - 1];
      const n = Math.ceil(Math.max(Math.abs(lon - lon0), Math.abs(lat - lat0)) / STEP);
      for (let k = 1; k < n; k++) out.push([lon0 + ((lon - lon0) * k) / n, lat0 + ((lat - lat0) * k) / n]);
    }
    out.push([lon, lat]);
  });
  return out;
}

function bounds(polys: Pt[][][]): Box | null {
  let box: Box | null = null;
  for (const poly of polys)
    for (const ring of poly)
      for (const [x, y] of ring)
        box = box
          ? [Math.min(box[0], x), Math.min(box[1], y), Math.max(box[2], x), Math.max(box[3], y)]
          : [x, y, x, y];
  return box;
}

export function plate(target: Target): Plate {
  const [lon, lat] = centre(target.truth);
  const projection = geoAzimuthalEqualArea().rotate([-lon, -lat]).scale(1).translate([0, 0]);
  const project = (mp: MultiPolygon): Pt[][][] =>
    mp.coordinates.map((poly) =>
      poly.map((ring) =>
        densify(ring)
          .map((p) => projection(p))
          .filter((p): p is Pt => p !== null && Number.isFinite(p[0]) && Number.isFinite(p[1])),
      ),
    );

  const truth = project(target.truth);
  const drawn = [...target.baselines, ...target.models].map((m) => (m.outline ? project(m.outline) : null));

  // The frame: the truth, grown to hold the drawings, but capped so one wild drawing cannot shrink the rest.
  const t = bounds(truth) ?? [0, 0, 0, 0];
  const size = Math.max(t[2] - t[0], t[3] - t[1], 1e-9);
  const cx = (t[0] + t[2]) / 2, cy = (t[1] + t[3]) / 2;
  const cap: Box = [
    cx - ((t[2] - t[0]) / 2) * REACH, cy - ((t[3] - t[1]) / 2) * REACH,
    cx + ((t[2] - t[0]) / 2) * REACH, cy + ((t[3] - t[1]) / 2) * REACH,
  ];
  let f: Box = [...t];
  for (const polys of drawn) {
    const b = polys && bounds(polys);
    if (b) f = [Math.min(f[0], b[0]), Math.min(f[1], b[1]), Math.max(f[2], b[2]), Math.max(f[3], b[3])];
  }
  f = [Math.max(f[0], cap[0]), Math.max(f[1], cap[1]), Math.min(f[2], cap[2]), Math.min(f[3], cap[3])];
  const pad = Math.max(f[2] - f[0], f[3] - f[1], size) * PAD;
  f = [f[0] - pad, f[1] - pad, f[2] + pad, f[3] + pad];
  let fw = f[2] - f[0], fh = f[3] - f[1];
  if (fw / fh < TALLEST) { f[0] -= (fh * TALLEST - fw) / 2; fw = fh * TALLEST; }
  if (fw / fh > WIDEST) { f[1] -= (fw / WIDEST - fh) / 2; fh = fw / WIDEST; }
  f = [f[0], f[1], f[0] + fw, f[1] + fh];

  const k = 1000 / Math.max(fw, fh);
  const n = (v: number) => Math.round(v * 10) / 10;
  const paths = (polys: Pt[][][]) =>
    polys.map((poly) =>
      poly
        .filter((ring) => ring.length > 1)
        .map((ring) => "M" + ring.map(([x, y]) => `${n((x - f[0]) * k)},${n((y - f[1]) * k)}`).join("L") + "Z")
        .join(""),
    );

  return {
    w: n(fw * k),
    h: n(fh * k),
    truth: paths(truth),
    foil: target.foil ? paths(project(target.foil)) : null,
    shapes: drawn.map((polys) => {
      const b = polys && bounds(polys);
      if (!polys || !b) return null;
      const off = (b[1] < f[1] ? "n" : "") + (b[2] > f[2] ? "e" : "") + (b[3] > f[3] ? "s" : "") + (b[0] < f[0] ? "w" : "");
      return { d: paths(polys), off };
    }),
  };
}
