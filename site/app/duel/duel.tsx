"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import { flushSync } from "react-dom";
import { chart, paths, type Pt, type Ring } from "@/lib/geo";

export type DuelModel = {
  id: string;
  name: string;
  released: string;
  score: number;
  drewModern: boolean;
  /** The drawing as MultiPolygon coordinates, every ring closed; null for "no drawing". */
  shape: number[][][][] | null;
  /** Per ring: true when the closing point was added by the reader, not written by the model. */
  added: boolean[][] | null;
};
export type DuelTarget = {
  id: string;
  name: string;
  polity: string;
  truth: number[][][][];
  foil: number[][][][] | null;
  models: DuelModel[];
};

// ---- the clock -------------------------------------------------------------------------------------------
// Everything on the stage is a function of one number, the time in milliseconds. Nothing on it uses a CSS
// animation, so the recorder can step the clock frame by frame and always get the same picture.
const TYPE = 1000; // the sentence is typed
const SET = 1500; // it moves up and the two panels come in
const DRAW = 2200; // the first point lands
const DRAW_FOR = 8000; // how long the longer drawing takes
const BEAT = 400; // a breath between the last point and the colours
const WASH_FOR = 900;
const LAND = [500, 750]; // each number lands this long after the wash starts
const LAND_FOR = 550;
const HOLD = 2500; // the last frame
const FRAME = 1000 / 60; // the scrubber and the recorder both move in sixtieths of a second

const PER_ROW = 5; // coordinate pairs per line of the stream
// The stage in its own units (1920 wide). A map is as wide as its column or as tall as MAP_TALL, whichever binds;
// the stream of coordinates takes the height that is left.
const MAP_WIDE = 832, MAP_TALL = 480, COLUMN = 600, ROW = 25;
const FINE_PRINT = "same prompt · at most 400 points · no tools · borderbench";

const clamp = (x: number) => Math.min(1, Math.max(0, x));
const ease = (x: number) => 1 - (1 - clamp(x)) ** 3;
const u = (n: number) => `calc(${n} * var(--u))`;
// An element that has finished arriving carries no style at all, so the browser draws it as plain content and
// the last frame is the same picture whether the clock walked there or jumped there.
const fade = (x: number, rise = 0): CSSProperties | undefined =>
  x >= 1 ? undefined : { opacity: x, transform: rise ? `translateY(${u((1 - x) * rise)})` : undefined };
const mp = (coordinates: number[][][][]) => ({ type: "MultiPolygon" as const, coordinates });
const month = (iso: string) => {
  const date = new Date(iso);
  return !iso || Number.isNaN(date.getTime())
    ? ""
    : new Intl.DateTimeFormat("en", { month: "short", year: "numeric", timeZone: "UTC" }).format(date);
};
const clock = (ms: number) => `0:${String(Math.floor(ms / 1000)).padStart(2, "0")}`;

// ---- one side's drawing, ready to replay ---------------------------------------------------------------------
type Side = {
  pieces: Ring[];
  /** The step at which each piece starts. A step is one point of the outline, in order. */
  starts: number[];
  steps: number;
  /** written[k]: how many of the first k steps are points the model wrote (a closing point we added is not). */
  written: number[];
  /** The stream: lines of coordinate pairs, each tagged with its count among the written points. */
  rows: { n: number; text: string }[][];
  full: string[];
  off: string;
};

function side(rings: Ring[][], off: string, model: DuelModel): Side {
  const pieces: Ring[] = [], starts: number[] = [], written = [0], rows: Side["rows"] = [];
  let steps = 0;
  rings.forEach((polygon, pi) =>
    polygon.forEach((ring, ri) => {
      if (!ring.pts.length) return;
      pieces.push(ring);
      starts.push(steps);
      steps += ring.stops.length;
      let row: Side["rows"][number] | null = null; // every piece starts a new line
      model.shape![pi][ri].forEach(([lon, lat], i, all) => {
        const own = !(model.added?.[pi]?.[ri] && i === all.length - 1);
        const n = written[written.length - 1] + (own ? 1 : 0);
        written.push(n);
        if (!own) return;
        if (!row || row.length === PER_ROW) rows.push((row = []));
        row.push({ n, text: `[${lon.toFixed(2)}, ${lat.toFixed(2)}]` });
      });
    }),
  );
  return { pieces, starts, steps, written, rows, full: paths(rings), off };
}

const lerp = (a: Pt, b: Pt, f: number): Pt => [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
const xy = ([x, y]: Pt) => `${Math.round(x * 10) / 10},${Math.round(y * 10) / 10}`;

/** The line after `k` steps (a fraction is part of the way to the next point) and where the pen is. */
function drawn(s: Side, k: number): { d: string; pen: Pt | null } {
  let d = "", pen: Pt | null = null;
  for (let p = 0; p < s.pieces.length; p++) {
    const { pts, stops } = s.pieces[p];
    const local = k - s.starts[p];
    if (local <= 0) break;
    if (local < 1) {
      // Pen up: it travels to the next piece and no line is drawn between pieces.
      const previous = p > 0 ? s.pieces[p - 1].pts : pts;
      pen = lerp(previous[previous.length - 1], pts[stops[0]], p > 0 ? local : 1);
      break;
    }
    const placed = Math.min(stops.length, Math.floor(local));
    let upto = stops[placed - 1], tail = "";
    pen = pts[upto];
    if (placed < stops.length) {
      const along = (local - placed) * (stops[placed] - upto);
      const whole = Math.min(Math.floor(along), stops[placed] - upto - 1);
      upto += whole;
      pen = lerp(pts[upto], pts[upto + 1], along - whole);
      tail = "L" + xy(pen);
    }
    d += "M" + pts.slice(0, upto + 1).map(xy).join("L") + tail + (placed === stops.length ? "Z" : "");
  }
  return { d, pen: k >= s.steps ? null : pen };
}

const Paths = ({ d }: { d: string[] }) =>
  d.map((p, i) => <path key={i} d={p} fillRule="evenodd" vectorEffect="non-scaling-stroke" />);

// ---- the stage --------------------------------------------------------------------------------------------
type Scene = {
  target: DuelTarget;
  models: [DuelModel, DuelModel];
  w: number;
  h: number;
  truth: string[];
  foil: string[] | null;
  sides: [Side | null, Side | null];
  rate: number; // steps per millisecond
  mapHeight: number;
  rows: number; // lines of the stream that fit under the map
  drawEnd: number;
  wash: number;
  duration: number;
};

function scene(target: DuelTarget, a: DuelModel, b: DuelModel): Scene {
  // One frame for both maps, fitted to the true border and these two drawings.
  const c = chart(mp(target.truth), [a, b].map((m) => (m.shape ? mp(m.shape) : null)), 3);
  const mapHeight = Math.round(Math.min(MAP_TALL, (MAP_WIDE * c.h) / c.w));
  const sides = [a, b].map((m, i) => (c.shapes[i] ? side(c.shapes[i]!.rings, c.shapes[i]!.off, m) : null)) as Scene["sides"];
  const longest = Math.max(sides[0]?.steps ?? 0, sides[1]?.steps ?? 0);
  const drawEnd = DRAW + (longest ? DRAW_FOR : 0);
  const wash = drawEnd + BEAT;
  return {
    target, models: [a, b], w: c.w, h: c.h, sides,
    truth: paths(c.truth),
    foil: target.foil ? paths(c.place(mp(target.foil))) : null,
    rate: longest / DRAW_FOR,
    mapHeight,
    rows: Math.max(3, Math.floor((COLUMN - mapHeight) / ROW)),
    drawEnd, wash,
    duration: wash + LAND[1] + LAND_FOR + HOLD,
  };
}

function Panel({ s, i, t }: { s: Scene; i: 0 | 1; t: number }) {
  const model = s.models[i], sd = s.sides[i];
  const k = sd ? Math.min(sd.steps, Math.max(0, (t - DRAW) * s.rate)) : 0;
  const line = sd ? drawn(sd, k) : null;
  const count = sd ? sd.written[Math.floor(k)] : 0;
  const wash = ease((t - s.wash) / WASH_FOR);
  const land = ease((t - s.wash - LAND[i]) / LAND_FOR);
  const first = sd ? Math.max(0, sd.rows.findIndex((row) => row[row.length - 1].n >= count) - s.rows + 1) : 0;
  const rows = sd ? sd.rows.slice(first, first + s.rows).filter((row) => row[0].n <= count) : [];
  const box = { maskUnits: "userSpaceOnUse" as const, x: 0, y: 0, width: s.w, height: s.h };
  const id = `duel-${i}`;

  return (
    <div className="st-col">
      <div className="st-head">
        <div>
          <p className="st-name">{model.name}</p>
          <p className="st-label">{month(model.released)}</p>
        </div>
        {/* No number is on the stage before its drawing is finished. */}
        {land > 0 && (
          <p className={`st-score ${sd ? "" : "text-muted"}`} style={fade(land, 28)}>
            {model.score.toFixed(1)}
            <small>%</small>
          </p>
        )}
      </div>

      <div className={`st-map ${sd ? "" : "st-none"}`} style={{ height: u(s.mapHeight) }}>
        {!sd ? (
          <em>no drawing</em>
        ) : (
          <>
            <svg className="map" viewBox={`0 0 ${s.w} ${s.h}`} aria-hidden="true" focusable="false">
              <defs>
                <mask id={`${id}-d`} {...box}>
                  <rect width={s.w} height={s.h} fill="#fff" />
                  <g fill="#000"><Paths d={sd.full} /></g>
                </mask>
                <mask id={`${id}-t`} {...box}>
                  <rect width={s.w} height={s.h} fill="#fff" />
                  <use href="#duel-truth" fill="#000" />
                </mask>
              </defs>
              {/* The true border is there from the start, faint, so a mistake shows while it is being made. */}
              <use href="#duel-truth" className="land" style={{ opacity: 0.42 + 0.58 * wash }} />
              {wash > 0 && (
                <g style={fade(wash)}>
                  <use href="#duel-truth" className="missed" mask={`url(#${id}-d)`} />
                  <g className="invented" mask={`url(#${id}-t)`}><Paths d={sd.full} /></g>
                  {model.drewModern && s.foil && <use href="#duel-foil" className="foil" />}
                </g>
              )}
              <path className="line" d={line!.d} vectorEffect="non-scaling-stroke" />
              {line!.pen && (
                <>
                  <circle className="st-halo" cx={line!.pen[0]} cy={line!.pen[1]} r={s.w / 60} />
                  <circle className="st-pen" cx={line!.pen[0]} cy={line!.pen[1]} r={s.w / 190} />
                </>
              )}
            </svg>
            {wash > 0 && [...sd.off].map((edge) => (
              <span key={edge} className={`off off-${edge}`} style={fade(wash)}>
                {{ n: "↑", e: "→", s: "↓", w: "←" }[edge]}
              </span>
            ))}
          </>
        )}
      </div>

      <div className="st-stream">
        <p className="st-label">
          {sd && t >= DRAW ? `${count} ${count === 1 ? "point" : "points"}` : " "}
          {model.drewModern && wash > 0 && <span className="st-tag" style={fade(wash)}>drew the modern country</span>}
        </p>
        {rows.map((row) => (
          <p key={row[0].n}>
            {row.filter((pair) => pair.n <= count).map((pair) => (
              <span key={pair.n} data-new={pair.n === count && k < sd!.steps ? "" : undefined}>{pair.text}</span>
            ))}
          </p>
        ))}
      </div>
    </div>
  );
}

function Stage({ s, sentence, t }: { s: Scene; sentence: [string, string]; t: number }) {
  const words = sentence[0] + s.target.name + sentence[1];
  const typed = Math.round(clamp(t / TYPE) * words.length);
  // The sentence leaves first, then the stage arrives: the two are never on top of each other.
  const leave = ease((t - SET) / 280);
  const set = ease((t - SET - 240) / (DRAW - SET - 240));
  const part = (from: number, text: string, className?: string) => (
    <span className={className}>
      {text.slice(0, Math.max(0, typed - from))}
      {typed < words.length && typed >= from && typed < from + text.length && <i className="st-caret" />}
      <span style={{ opacity: 0 }}>{text.slice(Math.max(0, typed - from))}</span>
    </span>
  );
  return (
    <div className="stage" role="img" aria-label={`${s.models[0].name} and ${s.models[1].name} draw ${s.target.name} from memory, point by point.`}>
      {/* Every true border once; both maps point at it. */}
      <svg width="0" height="0" className="absolute" aria-hidden="true" focusable="false">
        <defs>
          <g id="duel-truth"><Paths d={s.truth} /></g>
          {s.foil && <g id="duel-foil"><Paths d={s.foil} /></g>}
        </defs>
      </svg>

      {/* The words the models were sent: typed alone, then kept as the heading. */}
      {leave < 1 && (
        <p className="st-intro" style={{ opacity: 1 - leave, transform: `translate(-50%, calc(-50% - ${u(leave * 36)}))` }}>
          {part(0, sentence[0])}
          {part(sentence[0].length, s.target.name, "st-target")}
          {part(sentence[0].length + s.target.name.length, sentence[1])}
        </p>
      )}
      <div style={fade(set)}>
        <p className="st-top">
          <span>
            {sentence[0]}
            <span className="st-target">{s.target.name}</span>
            {sentence[1]}
          </span>
        </p>
        <div className="st-cols">
          <Panel s={s} i={0} t={t} />
          <Panel s={s} i={1} t={t} />
        </div>
        <p className="st-fine">{FINE_PRINT}</p>
      </div>
    </div>
  );
}

// ---- the page around the stage -----------------------------------------------------------------------------
declare global {
  interface Window {
    /** For the recorder: which pair is up, how long the clip is, and a way to put the clock anywhere. */
    duel?: { key: string; duration: number; seek: (ms: number) => Promise<void> };
  }
}

export default function Duel({ targets, sentence }: { targets: DuelTarget[]; sentence: [string, string] }) {
  // Opens on Indonesia, the oldest model against the newest. Models are in release order in the results file.
  const home = Math.max(0, targets.findIndex((x) => x.id === "indonesia"));
  const [pick, setPick] = useState({ target: home, left: 0, right: Math.max(0, (targets[home]?.models.length ?? 1) - 1) });
  const [t, setT] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [bare, setBare] = useState(false); // ?frame=1: the stage alone, filling the window, for the recorder
  const ready = useRef(false);

  const target = targets[pick.target];
  const a = target?.models[pick.left], b = target?.models[pick.right];
  const s = useMemo(() => (target && a && b ? scene(target, a, b) : null), [target, a, b]);
  const duration = s?.duration ?? 0;

  // The choice lives in the query string, so a reload and the recorder land on the same pair.
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const ti = targets.findIndex((x) => x.id === q.get("target"));
    const models = targets[ti < 0 ? home : ti]?.models ?? [];
    const find = (id: string | null, otherwise: number) => {
      const i = models.findIndex((m) => m.id === id);
      return i < 0 ? otherwise : i;
    };
    setPick({ target: ti < 0 ? home : ti, left: find(q.get("left"), 0), right: find(q.get("right"), Math.max(0, models.length - 1)) });
    setBare(q.get("frame") === "1");
    ready.current = true;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // A new pair plays from the top. With reduced motion it opens on the finished frame and waits to be asked.
  useEffect(() => {
    if (!ready.current || !s) return;
    const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setT(still ? s.duration : 0);
    setPlaying(!still);
    const q = new URLSearchParams(window.location.search);
    q.set("target", s.target.id);
    q.set("left", s.models[0].id);
    q.set("right", s.models[1].id);
    window.history.replaceState(null, "", `?${q}`);
    window.duel = {
      key: [s.target.id, s.models[0].id, s.models[1].id].join("|"),
      duration: s.duration,
      seek: (ms) => {
        flushSync(() => {
          setPlaying(false);
          setT(Math.min(s.duration, Math.max(0, ms)));
        });
        return new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(() => done())));
      },
    };
  }, [s]);

  useEffect(() => {
    if (!playing) return;
    let frame = 0, last = performance.now();
    const tick = (now: number) => {
      const dt = now - last;
      last = now;
      setT((was) => {
        const next = Math.min(duration, was + dt);
        if (next >= duration) setPlaying(false);
        return next;
      });
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, duration]);

  if (!s) return <p className="px-4 py-16 text-2xl italic text-muted">No targets in the results file yet.</p>;

  const done = t >= s.duration;
  const play = () => {
    if (done) setT(0);
    setPlaying(true);
  };
  const choose = (change: Partial<typeof pick>) => {
    const next = { ...pick, ...change };
    const count = targets[next.target].models.length;
    setPick({ target: next.target, left: Math.min(next.left, count - 1), right: Math.min(next.right, count - 1) });
  };
  const select = (label: string, value: number, options: string[], onChange: (i: number) => void) => (
    <label className="duel-pick">
      <span className="label">{label}</span>
      <select value={value} onChange={(e) => onChange(Number(e.target.value))}>
        {options.map((text, i) => (
          <option key={i} value={i}>{text}</option>
        ))}
      </select>
    </label>
  );

  if (bare)
    return (
      <div className="stage-wrap stage-bare">
        <Stage s={s} sentence={sentence} t={t} />
      </div>
    );

  return (
    <div className="mx-auto w-full max-w-[105rem] flex-1 px-4 pb-12 sm:px-8 lg:px-12">
      <header className="flex items-baseline justify-between border-b border-ink pt-5 pb-3 sm:pt-7">
        <p className="label text-ink">
          <Link href="/" className="no-underline hover:underline">BorderBench</Link> · Head to head
        </p>
        <Link className="label hover:text-ink" href="/">
          <span aria-hidden="true">←</span> All strips
        </Link>
      </header>

      <main>
        <h1 className="sr-only">Head to head: two models draw the same country</h1>
        <div className="my-5 grid gap-3 sm:grid-cols-3">
          {select("Country", pick.target, targets.map((x) => x.polity.replace(/^./, (c) => c.toUpperCase())), (i) => choose({ target: i }))}
          {select("Left", pick.left, target.models.map((m) => m.name), (i) => choose({ left: i }))}
          {select("Right", pick.right, target.models.map((m) => m.name), (i) => choose({ right: i }))}
        </div>

        <div className="stage-wrap border border-rule">
          <Stage s={s} sentence={sentence} t={t} />
        </div>

        <div className="mt-3 flex items-center gap-3">
          <button type="button" className="step" aria-label={playing ? "Pause" : done ? "Replay" : "Play"} onClick={() => (playing ? setPlaying(false) : play())}>
            {playing ? "❙❙" : done ? "↺" : "▶"}
          </button>
          <input
            className="scrub min-w-0 flex-1"
            type="range"
            min={0}
            max={Math.ceil(s.duration / FRAME)}
            step={1}
            value={Math.round(t / FRAME)}
            onChange={(e) => {
              setPlaying(false);
              setT(Math.min(s.duration, Number(e.target.value) * FRAME)); // whole frames, so End is the end
            }}
            aria-label="Clip time"
            aria-valuetext={`${clock(t)} of ${clock(s.duration)}`}
          />
          <span className="label shrink-0 whitespace-nowrap tabular-nums">
            {clock(t)} / {clock(s.duration)}
          </span>
        </div>
        <p className="sr-only" aria-live="polite">
          {done && s.models.map((m) => `${m.name}: ${m.shape ? "" : "no drawing, "}${m.score.toFixed(1)} percent overlap.`).join(" ")}
        </p>
      </main>
    </div>
  );
}
