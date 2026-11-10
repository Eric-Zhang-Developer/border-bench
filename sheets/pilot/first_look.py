"""Two rows per target on one contact sheet: Sonnet 4.5 from the archive and Fable 5.2 from the pilot set, both
under candidate C. Uses pipeline/sheet.py's own drawing and pipeline/score.py's own scoring; only the loading of two
run sets is done here. Run from the repo root: PYTHONPATH=. uv run python sheets/pilot/first_look.py"""
from pipeline.score import ROOT, load_runs, load_target
from pipeline.sheet import entries_for, sheet

runs = load_runs(ROOT / "runs/archive", "pilot-c") | load_runs(ROOT / "runs/pilot", "pilot-c")
(ROOT / "sheets/pilot").mkdir(parents=True, exist_ok=True)
for target_id in ("usa", "chile", "indonesia", "croatia"):
    target = load_target(ROOT / "targets" / target_id)
    entries = entries_for(target, {"pilot-c": runs})
    out = ROOT / "sheets/pilot" / f"first-look-{target_id}.png"
    sheet(target, entries, "first look · prompt candidate C, not frozen · drawings from memory").save(out)
    print(out.relative_to(ROOT), [(e["name"], e["score"], e["notes"]) for e in entries[2:]])
