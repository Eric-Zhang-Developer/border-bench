import { plate } from "@/lib/geo";
import { loadResults } from "@/lib/results";
import Strips, { type StripTarget } from "./strips";

const REPO = "https://github.com/Eric-Zhang-Developer/border-bench";

export default function Home() {
  const { data, sample } = loadResults();

  // Borders are projected here, at build time. The browser gets finished outlines and only does the overlay.
  const targets: StripTarget[] = data.targets.map((t) => ({
    id: t.id,
    name: t.name,
    // Every target string reads "{polity} as of {date}" (specs/decisions/001-prompt.md).
    polity: t.name.split(" as of ")[0],
    year: t.date.slice(0, 4),
    kind: t.kind,
    plate: plate(t),
    tiles: [
      ...t.baselines.map((b) => ({ id: b.id, label: b.label, score: b.score })),
      ...t.models.map((m) => ({
        id: m.id,
        label: m.label,
        score: m.score,
        model: {
          released: m.released,
          scores: m.scores,
          shown: m.median_sample,
          points: m.points,
          noDrawing: m.flags.no_drawing,
          over400: m.flags.over_400_points,
          drewModern: m.flags.drew_modern,
        },
      })),
    ],
  }));

  // One footer line per source, with the targets it was used for.
  const sources = new Map<string, { name: string; licence: string; url: string; used: string[] }>();
  for (const t of data.targets) {
    const key = [t.source.name, t.source.licence, t.source.url].join("|");
    if (!sources.has(key)) sources.set(key, { ...t.source, used: [] });
    sources.get(key)!.used.push(t.name.split(" as of ")[0]);
  }

  return (
    <>
      {sample && (
        <aside className="banner" aria-label="Sample data notice">
          <strong>Sample data</strong> · Every shape, model and score on this page is made up to test the layout.
          Nothing here is a real result.
        </aside>
      )}

      <div className="mx-auto w-full max-w-[105rem] flex-1 px-4 sm:px-8 lg:px-12">
        <header className="pt-5 pb-9 sm:pt-7 lg:pb-12">
          <div className="flex items-baseline justify-between border-b border-ink pb-3">
            <p className="label text-ink">BorderBench</p>
            <a className="label hover:text-ink" href={REPO}>
              GitHub <span aria-hidden="true">↗</span>
            </a>
          </div>
          <div className="mt-7 grid gap-7 lg:mt-10 lg:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] lg:items-end lg:gap-16">
            <h1 className="text-balance text-[clamp(2.5rem,5.4vw,5.25rem)] leading-[0.95] tracking-[-0.025em]">
              We asked each model to draw this <em>from memory.</em>
            </h1>
            <div className="max-w-xl space-y-4 text-lg leading-snug">
              <p>
                Each drawing is laid over the true border. The number under it is the overlap: the area the two
                share, divided by the area either one covers.
              </p>
              <p>{data.settings_note ?? "Each model ran with its default settings."}</p>
              <details className="prompt">
                <summary>Read the exact prompt</summary>
                <pre>{data.prompt.text}</pre>
                <p className="label mt-2">
                  Prompt {data.prompt.id} · only {"{target}"} changes from one drawing to the next
                </p>
              </details>
            </div>
          </div>
        </header>

        <main>
          <Strips targets={targets} sample={sample} />
        </main>

        <footer className="mt-20 grid gap-x-12 gap-y-8 border-t border-ink pt-6 pb-12 text-[0.9375rem] leading-snug md:grid-cols-3">
          <div>
            <h2 className="label mb-2">True borders</h2>
            <ul className="space-y-2">
              {[...sources.values()].map((s) => (
                <li key={s.name + s.licence + s.url}>
                  {/* The scorer writes empty strings when a target names no source. Empty stays visible, never guessed. */}
                  {!s.name ? "Source not recorded" : /^https?:\/\//.test(s.url) ? <a href={s.url}>{s.name}</a> : s.name},{" "}
                  {s.licence || "licence not recorded"}.{" "}
                  <span className="text-muted">Used for {s.used.join(", ")}.</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="label mb-2">The score</h2>
            <p>
              Overlap is measured on an equal-area grid, so a square kilometre counts the same anywhere on Earth.
              Nothing in a drawing is repaired before it is scored.{" "}
              <a href={`${REPO}/blob/main/specs/decisions/002-grading.md`}>How grading works</a>
            </p>
          </div>
          <div>
            <h2 className="label mb-2">The code</h2>
            <p>
              <a href={REPO}>github.com/Eric-Zhang-Developer/border-bench</a>. The code is under the MIT licence.
              Each true border keeps the licence of its source.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
