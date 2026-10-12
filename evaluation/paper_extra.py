from collections import defaultdict
from pathlib import Path

from evaluation.load import load_results
from evaluation.significance import did_catch_damage, mcnemar_test

rs = [
    r
    for r in load_results(Path("runs/results"))
    if r.model in {"gpt5.6-luna", "gpt5.6-terra"}
]
split = [r for r in rs if r.strategy == "split" and r.model == "gpt5.6-luna"]
keys = {(r.item_id, r.mutation_type, r.severity) for r in split}
comb = [
    r
    for r in rs
    if r.strategy == "combined"
    and r.model == "gpt5.6-luna"
    and (r.item_id, r.mutation_type, r.severity) in keys
]

cs, cc = sum(r.cost for r in split), sum(r.cost for r in comb)
print(f"split ${cs:.2f} | combined ${cc:.2f} | six-property split ${6*cs:.2f}")
print(f"ratio six-split/combined {6*cs/cc:.2f} | combined/split request {cc/cs:.2f}")

print("\nper-operator McNemar (b = split only, c = combined only)")
for mut in sorted({r.mutation_type for r in split}):
    m = mcnemar_test(
        [r for r in split if r.mutation_type == mut],
        [r for r in comb if r.mutation_type == mut],
    )
    print(f"{mut:24s} b={m['b']:3d} c={m['c']:3d} p={m['p_value']:.4f}")

print("\nsame targeted verdict across the 3 identical inputs")
for model in ("gpt5.6-luna", "gpt5.6-terra"):
    for mut in ("functional_relevance", "text_image_coherence"):
        by_item = defaultdict(list)
        for r in rs:
            if r.model == model and r.strategy == "combined" and r.mutation_type == mut:
                by_item[r.item_id].append(did_catch_damage(r))
        full = [v for v in by_item.values() if len(v) == 3]
        same = sum(len(set(v)) == 1 for v in full)
        print(f"{model} {mut}: {same}/{len(full)} = {100*same/len(full):.1f}%")
