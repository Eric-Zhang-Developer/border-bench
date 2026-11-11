import type { Metadata } from "next";
import { written } from "@/lib/answer";
import { loadResults, loadRuns } from "@/lib/results";
import Duel, { type DuelTarget } from "./duel";

export const metadata: Metadata = {
  title: "Head to head · BorderBench",
  description: "Two AI models draw the same country from memory, side by side, point by point.",
};

export default function DuelPage() {
  const { data, sample } = loadResults();
  const runs = loadRuns(data.prompt.id);

  // The browser gets every drawing as the points the model wrote, in the order it wrote them, and projects
  // only the pair that is picked. With no saved answers (the sample fixture) it replays the saved outline.
  const targets: DuelTarget[] = data.targets.map((t) => ({
    id: t.id,
    name: t.name,
    polity: t.name.split(" as of ")[0],
    truth: t.truth.coordinates,
    foil: t.foil?.coordinates ?? null,
    models: t.models.map((m) => {
      const answer = runs.samples(m.id, t.id)[m.median_sample]?.raw;
      const own = m.outline && answer ? written(answer) : null;
      return {
        id: m.id,
        name: runs.name(m.id) ?? m.label,
        released: m.released,
        score: m.score,
        drewModern: m.flags.drew_modern,
        shape: m.outline ? (own?.shape ?? m.outline.coordinates) : null,
        added: own?.added ?? null,
      };
    }),
  }));

  // The first line of the prompt is the sentence the stage opens on, with the target's words in the slot.
  // A prompt with no such slot on its first line leaves the stage with the target's words alone.
  const first = data.prompt.text.split("\n")[0];
  const [before, after] = first.includes("{target}") ? first.split("{target}") : ["", ""];

  return (
    <>
      {sample && (
        <aside className="banner" aria-label="Sample data notice">
          <strong>Sample data</strong> · Every shape, model and score on this page is made up to test the layout.
          Nothing here is a real result.
        </aside>
      )}
      <Duel targets={targets} sentence={[before, after]} />
    </>
  );
}
