"use client";

import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from "react";
import type { Plate, Shape } from "@/lib/geo";

export type Tile = {
  id: string;
  label: string;
  score: number;
  /** Missing on the two baselines. */
  model?: {
    released: string;
    scores: number[];
    shown: number;
    points: number;
    noDrawing: boolean;
    over400: boolean;
    drewModern: boolean;
  };
};
export type StripTarget = {
  id: string;
  name: string;
  polity: string;
  year: string;
  kind: "modern" | "history";
  plate: Plate;
  tiles: Tile[];
};

const TILE_MIN = 104; // px; keep in step with .strip in globals.css
const TILE_GAP = 12;
const ARROWS = { n: "↑", e: "→", s: "↓", w: "←" } as const;

const pct = (score: number) => score.toFixed(1);
const month = (iso: string, long = false) => {
  if (!iso) return "date not recorded"; // the scorer writes "" for a model with no release date
  const date = new Date(iso);
  return Number.isNaN(date.getTime())
    ? iso
    : new Intl.DateTimeFormat("en", { month: long ? "long" : "short", year: "numeric", timeZone: "UTC" }).format(date);
};
const roman = (n: number) => {
  let out = "";
  for (const [s, v] of [["X", 10], ["IX", 9], ["V", 5], ["IV", 4], ["I", 1]] as const) for (; n >= v; n -= v) out += s;
  return out;
};

const Paths = ({ d }: { d: string[] }) =>
  d.map((p, i) => <path key={i} d={p} fillRule="evenodd" vectorEffect="non-scaling-stroke" />);

/**
 * One drawing over the truth. The browser works out missed and invented land with two masks:
 * missed = the truth, kept only outside the drawing; invented = the drawing, kept only outside the truth.
 * So the coloured area is, by construction, exactly what the score counts against the model.
 */
function Drawing({ plate, shape, truth, uid, foil }: { plate: Plate; shape: Shape; truth: string; uid: string; foil?: boolean }) {
  const { w, h } = plate;
  const box = { maskUnits: "userSpaceOnUse" as const, x: 0, y: 0, width: w, height: h };
  return (
    <svg className="map" viewBox={`0 0 ${w} ${h}`} aria-hidden="true" focusable="false">
      <defs>
        <mask id={`${uid}-d`} {...box}>
          <rect width={w} height={h} fill="#fff" />
          <g fill="#000"><Paths d={shape.d} /></g>
        </mask>
        <mask id={`${uid}-t`} {...box}>
          <rect width={w} height={h} fill="#fff" />
          <use href={`#${truth}`} fill="#000" />
        </mask>
      </defs>
      <use href={`#${truth}`} className="land" />
      <use href={`#${truth}`} className="missed" mask={`url(#${uid}-d)`} />
      <g className="invented" mask={`url(#${uid}-t)`}><Paths d={shape.d} /></g>
      {foil && <use href={`#${truth}f`} className="foil" />}
      <g className="line"><Paths d={shape.d} /></g>
    </svg>
  );
}

/** The frame around a drawing, with arrows where it runs off, or the empty "no drawing" state. */
function Frame(props: { plate: Plate; shape: Shape | null; truth: string; uid: string; foil?: boolean; className?: string }) {
  const { plate, shape, className = "" } = props;
  const style = { aspectRatio: `${plate.w} / ${plate.h}` };
  if (!shape)
    return (
      <span className={`frame frame-empty ${className}`} style={style}>
        <em>no drawing</em>
      </span>
    );
  return (
    <span className={`frame ${className}`} style={style}>
      <Drawing {...props} shape={shape} />
      {[...shape.off].map((edge) => (
        <span key={edge} className={`off off-${edge}`} aria-hidden="true">
          {ARROWS[edge as keyof typeof ARROWS]}
        </span>
      ))}
    </span>
  );
}

const Legend = ({ foil }: { foil?: boolean }) => (
  <>
    <span><i className="swatch" style={{ "--c": "var(--land)" } as CSSProperties} />land it got right</span>
    <span><i className="swatch" style={{ "--c": "var(--missed)" } as CSSProperties} />land it missed</span>
    <span><i className="swatch" style={{ "--c": "var(--invented)" } as CSSProperties} />land it invented</span>
    <span><i className="swatch swatch-line" />the model’s line</span>
    {foil && <span><i className="swatch swatch-dots" />the modern country</span>}
  </>
);

export default function Strips({ targets, sample }: { targets: StripTarget[]; sample: boolean }) {
  const [ti, setTi] = useState(0);
  const [sel, setSel] = useState<number | null>(null);
  const [open, setOpen] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);
  const scrub = useRef<HTMLInputElement>(null);
  const strip = useRef<HTMLOListElement>(null);
  const buttons = useRef<(HTMLButtonElement | null)[]>([]);

  const t = targets[ti];
  const n = t?.tiles.length ?? 0;
  const cur = sel === null ? null : t?.tiles[sel];
  const step = (by: number) => setSel((s) => (s === null ? s : Math.min(n - 1, Math.max(0, s + by))));

  // Balanced rows: 17 tiles become 9 + 8, never 16 + 1.
  useLayoutEffect(() => {
    const el = strip.current;
    if (!el?.parentElement || !n) return;
    const fit = () => {
      const most = Math.max(1, Math.floor((el.parentElement!.clientWidth + TILE_GAP) / (TILE_MIN + TILE_GAP)));
      el.style.setProperty("--cols", String(Math.ceil(n / Math.ceil(n / most))));
    };
    fit();
    const watch = new ResizeObserver(fit);
    watch.observe(el.parentElement);
    return () => watch.disconnect();
  }, [n]);

  useEffect(() => {
    if (open && dialog.current && !dialog.current.open) {
      dialog.current.showModal();
      scrub.current?.focus({ preventScroll: true }); // so the arrow keys step straight away
    }
  }, [open]);

  if (!t) return <p className="py-16 text-2xl italic text-muted">No targets in the results file yet.</p>;

  const truth = `bb-t${ti}`;
  const m = cur?.model;
  const shape = sel === null ? null : t.plate.shapes[sel];

  return (
    <>
      {/* Every true border once; tiles and thumbnails point at these. */}
      <svg width="0" height="0" className="absolute" aria-hidden="true" focusable="false">
        <defs>
          {targets.map((x, i) => (
            <g key={x.id}>
              <g id={`bb-t${i}`}><Paths d={x.plate.truth} /></g>
              {x.plate.foil && <g id={`bb-t${i}f`}><Paths d={x.plate.foil} /></g>}
            </g>
          ))}
        </defs>
      </svg>

      <fieldset>
        <legend className="label mb-3">Pick a country</legend>
        <div className="picker">
          {targets.map((x, i) => (
            <label key={x.id} className="pick">
              <input
                type="radio"
                name="target"
                checked={i === ti}
                onChange={() => {
                  setTi(i);
                  setSel(null);
                }}
              />
              <svg viewBox={`0 0 ${x.plate.w} ${x.plate.h}`} aria-hidden="true" focusable="false">
                <use href={`#bb-t${i}`} />
              </svg>
              <span className="min-w-0">
                <span className="block leading-tight first-letter:uppercase">{x.polity}</span>
                <span className="label">{x.year}</span>
              </span>
            </label>
          ))}
        </div>
      </fieldset>

      <section aria-labelledby="strip-title" className="mt-12 lg:mt-16">
        <div className="flex flex-wrap items-end justify-between gap-x-12 gap-y-5">
          <div>
            <p className="label">
              Plate {roman(ti + 1)} · {t.kind === "history" ? "History" : "Modern"} · the words each model was sent
            </p>
            <h2 id="strip-title" className="mt-2 text-[clamp(1.75rem,3.4vw,2.75rem)] leading-[1.05] tracking-[-0.015em]">
              <em>{t.name}</em>
            </h2>
          </div>
          <p className="label flex flex-wrap gap-x-5 gap-y-1"><Legend /></p>
        </div>

        <p className="label mt-8 mb-4 border-t border-rule pt-3">
          Two plain shapes to beat, then every model, oldest to newest <span aria-hidden="true">→</span>
        </p>

        <div>
          <ol
            ref={strip}
            className="strip"
            onKeyDown={(e) => {
              const by = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
              const at = buttons.current.indexOf(document.activeElement as HTMLButtonElement);
              if (by && at >= 0 && buttons.current[at + by]) {
                e.preventDefault();
                buttons.current[at + by]?.focus();
              }
            }}
          >
            {t.tiles.map((tile, i) => {
              const s = t.plate.shapes[i];
              const said = [
                tile.label,
                tile.model ? month(tile.model.released, true) : "baseline",
                tile.model?.noDrawing ? "no drawing" : `${pct(tile.score)} percent overlap`,
                tile.model?.drewModern ? "drew the modern country" : "",
                s?.off ? "runs off the frame" : "",
              ];
              return (
                <li key={`${t.id}-${tile.id}`} style={{ "--i": i } as CSSProperties}>
                  <button
                    ref={(el) => {
                      buttons.current[i] = el;
                    }}
                    type="button"
                    className="tile"
                    data-baseline={tile.model ? undefined : ""}
                    aria-current={sel === i ? "true" : undefined}
                    aria-label={`${said.filter(Boolean).join(", ")}. Open the large view.`}
                    onClick={() => {
                      setSel(i);
                      setOpen(true);
                    }}
                  >
                    <Frame plate={t.plate} shape={s} truth={truth} uid={`bb-s${i}`} />
                    <span className="tile-score" style={tile.model?.noDrawing ? { color: "var(--muted)" } : undefined}>
                      {pct(tile.score)}
                      <small>%</small>
                    </span>
                    <span className="tile-name">{tile.label}</span>
                    <span className="label mt-1">{tile.model ? month(tile.model.released) : "baseline"}</span>
                    {tile.model?.drewModern && <span className="tag">drew the modern country</span>}
                  </button>
                </li>
              );
            })}
          </ol>
        </div>
      </section>

      <dialog
        ref={dialog}
        className="big"
        aria-label={cur ? `${cur.label}, large view` : undefined}
        onClose={() => {
          setOpen(false);
          if (sel !== null) buttons.current[sel]?.focus();
        }}
        onClick={(e) => {
          if (e.target === e.currentTarget) e.currentTarget.close(); // a click on the backdrop
        }}
        onKeyDown={(e) => {
          // On the slider the browser already steps; everywhere else in the big view the arrows step too.
          if ((e.key === "ArrowLeft" || e.key === "ArrowRight") && e.target !== scrub.current) {
            e.preventDefault();
            step(e.key === "ArrowLeft" ? -1 : 1);
          }
        }}
      >
        {open && cur && sel !== null && (
          <div className="flex min-h-0 flex-1 flex-col">
            <div className="flex items-center justify-between gap-4 border-b border-rule px-4 py-3 sm:px-6">
              <p className="label">
                {t.polity} · {t.year}
                {sample && <span className="text-missed"> · sample data</span>}
              </p>
              <button type="button" className="label -m-2 shrink-0 cursor-pointer p-2 whitespace-nowrap hover:text-ink" onClick={() => dialog.current?.close()}>
                Close <span aria-hidden="true">✕</span>
              </button>
            </div>

            <div className="grid min-h-0 flex-1 content-start gap-6 overflow-y-auto p-4 sm:p-6 md:grid-cols-[minmax(0,1fr)_17rem] md:gap-10">
              <figure className="min-w-0">
                <Frame plate={t.plate} shape={shape} truth={truth} uid="bb-big" foil={m?.drewModern} className="big-frame" />
                <figcaption className="label mt-3 flex flex-wrap gap-x-5 gap-y-1">
                  <Legend foil={m?.drewModern && !!t.plate.foil} />
                </figcaption>
              </figure>

              <div className="flex flex-col gap-5" aria-live="polite">
                <div>
                  <p className="label">{m ? month(m.released, true) : "Baseline, not a model"}</p>
                  <h2 className="mt-1 text-3xl leading-[1.05] tracking-[-0.01em] [overflow-wrap:anywhere]">{cur.label}</h2>
                </div>
                <div>
                  <p className="big-score" style={m?.noDrawing ? { color: "var(--muted)" } : undefined}>
                    {pct(cur.score)}
                    <small>%</small>
                  </p>
                  <p className="label mt-2">overlap with the true border</p>
                </div>

                {m && m.scores.length > 0 && (
                  <div>
                    <p className="label">
                      {m.scores.length === 1 ? "Drawn once" : `Drawn ${m.scores.length} times · the picture is the marked one`}
                    </p>
                    <ol className="mt-2 flex gap-2">
                      {m.scores.map((s, i) => (
                        <li
                          key={i}
                          aria-current={i === m.shown ? "true" : undefined}
                          className={`flex-1 border px-2.5 py-1.5 ${i === m.shown ? "border-ink bg-ink text-paper" : "border-rule"}`}
                        >
                          <span className="label block text-current opacity-70">
                            No. {i + 1}
                            {i === m.shown && <span className="sr-only">, shown</span>}
                          </span>
                          <span className="text-xl tabular-nums">
                            {pct(s)}
                            <small className="ml-px text-[0.6em] opacity-70">%</small>
                          </span>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}

                <div className="space-y-2 text-[0.9375rem] leading-snug text-muted">
                  {!m && <p>A plain shape, scored the same way as the models. A drawing made from memory should beat it.</p>}
                  {m?.noDrawing && <p>The model’s answer held no outline that could be read, so there is nothing to lay over the border. It scores 0.</p>}
                  {m?.drewModern && (
                    <p>
                      <span className="tag mt-0 mr-1.5 text-ink">drew the modern country</span>
                      This drawing overlaps the modern country (dotted) more than the one that was asked for.
                    </p>
                  )}
                  {shape?.off && (
                    <p>
                      Part of this drawing runs off the frame <span aria-hidden="true">({[...shape.off].map((e) => ARROWS[e as keyof typeof ARROWS]).join(" ")})</span>.
                      Every tile on this strip shares one frame and one scale, so they can be compared.
                    </p>
                  )}
                  {m && !m.noDrawing && (
                    <p>
                      {m.points.toLocaleString("en")} points in the outline{m.over400 && ", flagged for being over 400"}.
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="border-t border-rule px-4 pt-2 pb-4 sm:px-6">
              <div className="flex items-center gap-3">
                <button type="button" className="step" aria-label="Previous tile" disabled={sel === 0} onClick={() => step(-1)}>
                  ←
                </button>
                <div className="min-w-0 flex-1">
                  <input
                    ref={scrub}
                    className="scrub"
                    type="range"
                    min={0}
                    max={n - 1}
                    step={1}
                    value={sel}
                    onChange={(e) => setSel(Number(e.target.value))}
                    aria-label="Step through the strip, oldest to newest"
                    aria-valuetext={`${cur.label}, ${sel + 1} of ${n}`}
                  />
                  <div className="ticks" aria-hidden="true">
                    {t.tiles.map((x, i) => (
                      <i key={x.id} data-on={i === sel ? "" : undefined} />
                    ))}
                  </div>
                </div>
                <button type="button" className="step" aria-label="Next tile" disabled={sel === n - 1} onClick={() => step(1)}>
                  →
                </button>
              </div>
              <p className="label mt-3 flex justify-between gap-4">
                <span>
                  {sel + 1} of {n} · oldest to newest
                </span>
                <span className="max-sm:hidden">← → keys step · Esc closes</span>
              </p>
            </div>
          </div>
        )}
      </dialog>
    </>
  );
}
