export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center gap-4 px-6 py-24">
      <h1 className="text-3xl font-semibold tracking-tight">BorderBench</h1>
      <p className="text-lg leading-8">
        AI models draw countries from memory. Each drawing is laid over the
        real border, with one number under it: how much of it overlaps the
        truth.
      </p>
      <p className="text-lg leading-8">
        This page is in progress. No model has been asked to draw anything
        yet, so there is nothing to show.
      </p>
      <p>
        <a
          className="underline underline-offset-4"
          href="https://github.com/Eric-Zhang-Developer/border-bench"
        >
          Follow the work on GitHub
        </a>
      </p>
    </main>
  );
}
