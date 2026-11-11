// A model's answer, point for point as it wrote them.
//
// The results file holds each drawing with points added along its long edges (pipeline/score.py, `display`), so it
// cannot say which points the model wrote. The replay needs exactly those, so this reads them from the saved
// answer. It is a port of pipeline/parse.py's rule: the last ```geojson block, or failing that the last valid JSON
// value in the answer that holds coordinates, read by how the coordinates nest. The scorer stays the judge:
// lib/geo.check.mjs fails the build if what this reads is ever not the outline the scorer saved.

type Position = [number, number];

const BLOCK = /```geojson[^\n]*\n([\s\S]*?)```/gi;
const DEEPEST = 8;

const isPosition = (p: unknown): p is number[] =>
  Array.isArray(p) && p.length >= 2 && p.slice(0, 2).every((x) => typeof x === "number" && Number.isFinite(x));
const isRing = (v: unknown): v is number[][] => Array.isArray(v) && v.length > 0 && v.every(isPosition);

function polygons(value: unknown, depth = 0): number[][][][] {
  if (depth > DEEPEST || value === null || typeof value !== "object") return [];
  if (!Array.isArray(value)) {
    const v = value as { type?: unknown; coordinates?: unknown; geometry?: unknown; features?: unknown };
    if (v.type === "Polygon" || v.type === "MultiPolygon") return polygons(v.coordinates, depth + 1);
    if (v.type === "Feature") return polygons(v.geometry, depth + 1);
    if (v.type === "FeatureCollection" && Array.isArray(v.features))
      return v.features.flatMap((f) => (f && typeof f === "object" && !Array.isArray(f) ? polygons(f, depth + 1) : []));
    return [];
  }
  if (isRing(value)) return [[value]];
  if (value.length > 0 && value.every(isRing)) return [value];
  return value.flatMap((v) => (Array.isArray(v) ? polygons(v, depth + 1) : []));
}

/** Each outermost JSON object or array in the text, in order; text that does not decode is skipped a character
 * at a time, so the complete pieces of a broken answer are still found. */
function* jsonValues(text: string): Generator<unknown> {
  // ponytail: rescans from every bracket of a broken value, so quadratic on a long broken answer. Two of the 84
  // saved answers take this path and each reads in milliseconds; index the brackets if that ever changes.
  for (let at = 0; at < text.length; at++) {
    if (text[at] !== "[" && text[at] !== "{") continue;
    let depth = 0, inString = false, end = -1;
    for (let i = at; i < text.length; i++) {
      const c = text[i];
      if (inString) {
        if (c === "\\") i++;
        else if (c === '"') inString = false;
      } else if (c === '"') inString = true;
      else if (c === "[" || c === "{") depth++;
      else if ((c === "]" || c === "}") && --depth === 0) {
        end = i;
        break;
      }
    }
    if (end < 0) continue;
    try {
      yield JSON.parse(text.slice(at, end + 1));
      at = end;
    } catch {
      // not a value starting here; try the next bracket
    }
  }
}

/**
 * The shape with every ring closed, as the scorer reads it, and for each ring whether the closing point was
 * added here (`added`: the model left the ring open) rather than written by the model.
 */
export function written(raw: string): { shape: Position[][][]; added: boolean[][] } | null {
  const holds = (value: unknown) => polygons(value).some((polygon) => polygon.some((ring) => ring.length >= 3));
  let chosen: unknown;
  const blocks = [...raw.matchAll(BLOCK)];
  if (blocks.length)
    try {
      const value: unknown = JSON.parse(blocks[blocks.length - 1][1]);
      if (holds(value)) chosen = value;
    } catch {
      // A block that is not valid JSON as a whole (a stray bracket, a cut-off answer): fall through.
    }
  if (chosen === undefined) for (const value of jsonValues(raw)) if (holds(value)) chosen = value; // the last one wins
  if (chosen === undefined) return null;
  const found = polygons(chosen);
  const added: boolean[][] = [];
  const shape = found.map((polygon) => {
    const flags: boolean[] = [];
    added.push(flags);
    return polygon.map((ring) => {
      const points = ring.map((p): Position => [p[0], p[1]]);
      const first = points[0], last = points[points.length - 1];
      const open = first[0] !== last[0] || first[1] !== last[1];
      if (open) points.push([first[0], first[1]]);
      flags.push(open);
      return points;
    });
  });
  return { shape, added };
}
