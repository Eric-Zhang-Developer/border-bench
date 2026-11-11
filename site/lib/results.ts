// The one file the page reads. Its shape is fixed by specs/features/scorer/results.example.json.
import fs from "node:fs";
import path from "node:path";

export type MultiPolygon = { type: "MultiPolygon"; coordinates: number[][][][] };

export type Baseline = { id: string; label: string; score: number; outline: MultiPolygon };

export type Model = {
  id: string;
  label: string;
  released: string;
  scores: number[];
  median_sample: number;
  score: number;
  points: number;
  outline: MultiPolygon | null;
  flags: { no_drawing: boolean; over_400_points: boolean; drew_modern: boolean };
};

export type Target = {
  id: string;
  name: string;
  date: string;
  kind: "modern" | "history";
  source: { name: string; licence: string; url: string };
  truth: MultiPolygon;
  foil: MultiPolygon | null;
  baselines: Baseline[];
  models: Model[];
};

export type Results = {
  schema: number;
  prompt: { id: string; text: string };
  settings_note?: string;
  targets: Target[];
};

/**
 * Real results win, always. `sample` is true only when the real file does not exist, and it is the single
 * switch for the "sample data" banner, so the banner cannot show over real results.
 * BB_FIXTURE picks another file in site/fixtures/ (the stress fixture) and is ignored once real results exist.
 */
export function loadResults(): { data: Results; sample: boolean } {
  const real = path.join(process.cwd(), "..", "results", "results.json");
  const sample = !fs.existsSync(real);
  const file = sample ? path.join(process.cwd(), "fixtures", process.env.BB_FIXTURE ?? "results.json") : real;
  return { data: JSON.parse(fs.readFileSync(file, "utf8")), sample };
}

/** One saved answer. Only the fields the page reads. */
export type Run = { model_display_name?: string; raw?: string | null };

/**
 * The saved answers behind the published strips: runs/p1/<prompt id>/<model>/<target>/<n>.json, in sample order,
 * so `samples(model, target)[median_sample]` is the answer whose drawing the results file shows.
 * `name` is the name Anthropic gives the model, as the runner saved it. With no run files (the sample fixture)
 * both come back empty and the page falls back to what the results file holds.
 */
export function loadRuns(promptId: string) {
  const root = path.join(process.cwd(), "..", "runs", "p1", promptId);
  const list = (dir: string) => (fs.existsSync(dir) ? fs.readdirSync(dir) : []);
  const samples = (model: string, target: string): Run[] =>
    list(path.join(root, model, target))
      .filter((file) => /^\d+\.json$/.test(file))
      .sort((a, b) => parseInt(a) - parseInt(b))
      .map((file) => JSON.parse(fs.readFileSync(path.join(root, model, target, file), "utf8")));
  const name = (model: string): string | undefined => {
    for (const target of list(path.join(root, model)))
      for (const run of samples(model, target)) if (run.model_display_name) return run.model_display_name;
  };
  return { samples, name };
}
