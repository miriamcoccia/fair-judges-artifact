import json, shutil, sys
from collections import Counter
from pathlib import Path

TYPES = {"technical_quality", "standard_presentation"}
src, dst = Path("runs/results"), Path("runs/results_stale_blurrot")
apply = len(sys.argv) > 1 and sys.argv[1] == "apply"
dst.mkdir(exist_ok=True)

counts = Counter()
for f in src.glob("*.json"):
    r = json.loads(f.read_text())
    if r.get("mutation_type") in TYPES:
        counts[(r["mutation_type"], r.get("model"), r.get("strategy"))] += 1
        if apply:
            shutil.move(str(f), dst / f.name)

for k, n in sorted(counts.items()):
    print(n, *k)
print("moved" if apply else "dry run, nothing moved")
