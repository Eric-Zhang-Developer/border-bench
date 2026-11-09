"""See the whole project running, with no API call: rebuild the scores, build the site, check every strip.

  python3 pipeline/verify.py        (run from the repo root; this is [verify].command in .agents/config.toml)

1. If the scorer exists, rebuild results/results.json from the committed runs.
2. Build the static site.
3. Fail if any strip in results.json is missing a tile: every target must list the same models.
The last line says which of these steps actually ran. Standard library only, so it runs before `uv sync`.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results" / "results.json"


def missing_tiles(results: dict) -> list[str]:
    """One line per (target, model) with no tile. Every target must carry every model seen on any target."""
    strips = {t["id"]: {m["id"] for m in t["models"]} for t in results["targets"]}
    everyone = set().union(*strips.values()) if strips else set()
    return [f"{target}: no tile for {model}" for target, have in strips.items() for model in sorted(everyone - have)]


def main() -> int:
    did = []
    if (ROOT / "pipeline" / "score.py").exists():
        subprocess.run(["uv", "run", "python", "-m", "pipeline.score"], cwd=ROOT, check=True)
        did.append("scores rebuilt from committed runs")
    else:
        did.append("no scorer yet, so no scores rebuilt")

    if not (ROOT / "site" / "node_modules").exists():
        subprocess.run(["npm", "--prefix", "site", "ci"], cwd=ROOT, check=True)
    subprocess.run(["npm", "--prefix", "site", "run", "build"], cwd=ROOT, check=True)
    if not (ROOT / "site" / "out" / "index.html").exists():
        print("verify: FAIL, the site build left no site/out/index.html")
        return 1
    did.append("site built")

    if RESULTS.exists():
        results = json.loads(RESULTS.read_text())
        if gaps := missing_tiles(results):
            print("\n".join(gaps))
            print(f"verify: FAIL, {len(gaps)} missing tile(s)")
            return 1
        did.append(f"{len(results['targets'])} strips complete")
    else:
        did.append("no results.json yet, so no strips checked")

    print("verify: " + "; ".join(did))
    return 0


if __name__ == "__main__":
    sys.exit(main())
