# BorderBench

**Can you see an AI model getting better?**

BorderBench asks AI models to draw countries from memory, as map coordinates, and lays each drawing over the real
border. Under every drawing is one number: how much of it overlaps the truth. Line the models up in release order and
you can watch the drawings improve, or not.

Most benchmarks report a score that goes up without anyone being able to say what it means. The rule here is **no
number without its picture**.

## Status

Work in progress. Nothing is built yet: this repo currently holds the plan.

- What we are building first: [specs/mission.md](specs/mission.md)
- Where it is going: [specs/roadmap.md](specs/roadmap.md)
- Where things stand today: [NOW.md](NOW.md)

## How it works

1. Each model gets the same prompt, with only the target's name changed, for example "Poland as of 1 January 1938".
   No tools and no web access. ([Why the prompt reads the way it does](specs/decisions/001-prompt.md))
2. The answer is a set of polygons in longitude and latitude.
3. The score is **overlap %**: the area the drawing and the true border share, divided by the area either one
   covers. Nothing in the answer is repaired. ([Grading](specs/decisions/002-grading.md))
4. History targets come with a modern "foil". A model that draws today's Poland when asked for 1938 gets tagged.

The first version covers six targets (the contiguous USA, Chile, Indonesia, Croatia, Prussia in 1816, Poland in 1938)
and every Claude model currently served. ([Models and settings](specs/decisions/003-models.md))

## Credit

The format follows Henry Bass's "How Does A Blind Model See The Earth?" (2025), which asked models "land or water?"
at each coordinate. GPT4GEO (Roberts et al., 2023) first asked a model for country outlines as coordinates. Related
work and data sources are listed in [specs/context/findings.md](specs/context/findings.md).

## How this repo is run

The plan lives in `specs/`, and every change arrives as a pull request written to be read by people who do not
program ([the convention](specs/context/pull-requests.md)). Coding agents do much of the building under the rules in
[AGENTS.md](AGENTS.md).

## Licence

Code: [MIT](LICENSE). Map data under `targets/` keeps the licence of its source, named in each target's `SOURCE.md`.
Some sources are non-commercial.
