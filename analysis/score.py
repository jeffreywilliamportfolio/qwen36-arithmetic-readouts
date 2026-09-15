#!/usr/bin/env python3
"""Re-score all published observations without an API, model, or GPU."""
#!/usr/bin/env python3
from pathlib import Path
import ast
from collections import Counter
from decimal import Decimal
import hashlib
import json
import math
import re
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence-dir', type=Path, default=ROOT / 'evidence')
parser.add_argument('--out', type=Path, default=ROOT / 'results')
parser.add_argument('--check', action='store_true', help='compare recomputed results with the published tables')
args = parser.parse_args()
RUN = args.evidence_dir


def read(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def definitions(path, assignments, functions):
    tree = ast.parse(path.read_text())
    nodes = [n for n in tree.body if
             (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in assignments for t in n.targets))
             or (isinstance(n, ast.FunctionDef) and n.name in functions)]
    ns = {"re": re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), ns)
    return ns


defs = definitions(ROOT / "data/synonyms.py", {"W", "C", "OPS"}, {"forms", "syn"})
decoys = definitions(ROOT / "scripts/read_local.py", {"OP_PREC"}, {"_apply", "derive_decoy"})
syn = defs["syn"]
word_values = {word: n for n, word in defs["W"].items()}
tens = "|".join(defs["W"][n] for n in range(20, 100, 10))
ones = "|".join(defs["W"][n] for n in range(1, 10))
words = "|".join(sorted(word_values, key=len, reverse=True))
number_re = re.compile(r"(?<![\d.])[-−]?\d+(?:\.\d+)?|\b(?:" + tens + r")(?:[- ](?:" + ones + r"))?\b|\b(?:" + words + r")\b", re.I)


def numbers(text):
    vals = []
    for match in number_re.finditer(text):
        s = match.group().lower().replace("−", "-")
        if re.fullmatch(r"-?\d+(?:\.\d+)?", s):
            vals.append(Decimal(s))
        else:
            vals.append(Decimal(sum(word_values[w] for w in re.split("[- ]", s))))
    return vals


def has_leak(vals, intermediate, target):
    for value in vals:
        if value == target:
            return False
        if value == intermediate:
            return True
    return False


def best(layers, synonyms, start=0, stop=63):
    return min((r + 1 for layer in layers[start:stop] for r, text in enumerate(layer[:8])
                if text.strip().lower() in synonyms), default=99)


def token_layers(doc, position=-1):
    toks = [t for t in doc["tokens"] if not t["is_generated"]]
    return toks[position]["results"][0]["top_tokens"]


def rate(k, n):
    return {"k": k, "n": n, "rate": k / n if n else None}


def summary(rows):
    base = [v for r in rows for v in r["baseline_ranks"]]
    wins = sum(r["rank"] < statistics.median(r["baseline_ranks"]) for r in rows)
    losses = sum(r["rank"] > statistics.median(r["baseline_ranks"]) for r in rows)
    p = min(1, 2 * sum(math.comb(wins + losses, j) for j in range(min(wins, losses) + 1)) / 2 ** (wins + losses))
    return {"pass1": rate(sum(r["rank"] <= 1 for r in rows), len(rows)),
            "pass3": rate(sum(r["rank"] <= 3 for r in rows), len(rows)),
            "no_space_pass1": rate(sum(r["no_space_rank"] <= 1 for r in rows), len(rows)),
            "baseline_pass1": rate(sum(r <= 1 for r in base), len(base)),
            "baseline_pass3": rate(sum(r <= 3 for r in base), len(base)),
            "sign_test": {"wins": wins, "losses": losses, "ties": len(rows) - wins - losses, "p": p}}


out = {"scope": "Offline aggregation of the published September 4-5 captures; no new inference"}
for entry in read(ROOT / 'provenance/evidence_files.json'):
    p = RUN / entry['path']
    if not p.is_file() or sha(p) != entry['sha256']:
        raise SystemExit('Evidence file missing or checksum mismatch: ' + entry['path'])

rows = []
for group, filename in [("paper", "order_ops.json"), ("new", "items_new50.json")]:
    for it in read(ROOT / "data" / filename)["items"]:
        num = next(s for s in it["intermediates"] if s.isdigit())
        tag = f"{group}_{it['name']}"
        doc = read(RUN / "v2_api/raw_A" / f"{tag}_space.json")
        no_doc = read(RUN / "v2_api/raw_A" / f"{tag}_nospace.json")
        ls = token_layers(doc)
        old = read(RUN / "v2_box/continuations" / f"{tag}_space.json")
        gate = read(RUN / "v2_box_full/continuations" / f"{tag}_space.json")
        used = set(re.findall(r"\d", it["prompt"] + str(it["target"]) + num))
        target = numbers(str(it["target"]))[0]
        first = numbers(old["greedy"]["text"])
        decoy = str(it["decoy"]) if it.get("decoy") else decoys["derive_decoy"](it["prompt"], num, str(it["target"]))
        sample_nums = [numbers(s["text"]) for s in gate["samples"]]
        reparsed_rate = sum(bool(v) and v[0] == target for v in sample_nums) / len(sample_nums)
        reparsed_leak = any(has_leak(v, Decimal(num), target) for v in sample_nums + [numbers(gate["greedy"]["text"])])
        row = {"tag": tag, "group": group, "prompt": it["prompt"], "target": str(it["target"]), "intermediate": int(num), "rank": best(ls, syn(num)),
               "no_cjk_rank": best(ls, syn(num, False)), "no_space_rank": best(token_layers(no_doc), syn(num)),
               "previous_token_rank": best(token_layers(doc, -2), syn(num)), "next_token_rank": best(ls, syn(num), 63, 64),
               "baseline_ranks": [best(ls, {str(i)}) for i in range(10) if str(i) not in used],
               "cjk_rank": best(ls, defs["forms"](int(num))["cjk"]),
               "decoy": decoy, "decoy_rank": best(ls, syn(decoy)) if decoy else None,
               "correct_stored": old["greedy"]["correct"], "correct_reparsed": bool(first) and first[0] == target,
               "admissible_stored": gate["admissible"], "admissible_reparsed": reparsed_rate >= 0.8 and not reparsed_leak,
               "assert_rate_stored": gate["assert_rate"], "assert_rate_reparsed": reparsed_rate,
               "leak_stored": gate["leak_any"], "leak_reparsed": reparsed_leak}
        for lens in ("hosted_n1000", "pile5"):
            box = read(RUN / "v2_box" / lens / f"{tag}_space.json")
            exact = box["rank_exact"]["keys"]["intermediate"]
            row[lens + "_rank"] = min(exact["min_rank_by_layer"][:63])
            row[lens + "_jacobian_rank"] = min(exact["min_rank_by_layer"][l] for l in box["meta"]["layers_with_jacobian"])
            row[lens + "_top8_rank"] = best(token_layers(box), syn(num))
            if lens == "pile5":
                no = read(RUN / "v2_box" / lens / f"{tag}_nospace.json")
                row["pile5_no_space_rank"] = min(no["rank_exact"]["keys"]["intermediate"]["min_rank_by_layer"][:63])
                no_cjk = [e for e in exact["ids"] if e["str"].strip().lower() in syn(num, False)]
                row["pile5_no_cjk_rank"] = min((min(e["ranks"][:63]) for e in no_cjk), default=99)
        rows.append(row)

out["metrics"] = {group: summary([r for r in rows if group == "all" or r["group"] == group]) for group in ("paper", "new", "all")}
out["correct_paper"] = summary([r for r in rows if r["group"] == "paper" and r["correct_stored"]])
out["admissible"] = {group: summary([r for r in rows if r["admissible_stored"] and (group == "all" or r["group"] == group)]) for group in ("paper", "new", "all")}
out["cjk"] = {"two_digit_rank1": sum(r["intermediate"] >= 10 and r["rank"] == 1 for r in rows),
              "of_these_cjk_rank1": sum(r["intermediate"] >= 10 and r["rank"] == 1 and r["cjk_rank"] == 1 for r in rows)}
for key, selected in [("new_two_digit", [r for r in rows if r["group"] == "new" and r["intermediate"] >= 10]),
                      ("new_single_digit", [r for r in rows if r["group"] == "new" and r["intermediate"] < 10])]:
    out["cjk"][key] = {"with_cjk": rate(sum(r["rank"] == 1 for r in selected), len(selected)),
                       "without_cjk": rate(sum(r["no_cjk_rank"] == 1 for r in selected), len(selected)),
                       "pile5_with_cjk": rate(sum(r["pile5_rank"] == 1 for r in selected), len(selected)),
                       "pile5_without_cjk": rate(sum(r["pile5_no_cjk_rank"] == 1 for r in selected), len(selected))}
out["position"] = {"equals_hits_in_space_prompt": sum(r["previous_token_rank"] == 1 for r in rows),
                   "pile5_no_space_hits": sum(r["pile5_no_space_rank"] == 1 for r in rows),
                   "previous_equals_vs_no_space_rank_disagreements": [r["tag"] for r in rows if r["previous_token_rank"] != r["no_space_rank"]]}
out["next_token_control"] = {"rank1": sum(r["rank"] == 1 for r in rows),
                             "rank1_and_output_top8": sum(r["rank"] == 1 and r["next_token_rank"] <= 8 for r in rows),
                             "rank3": sum(r["rank"] <= 3 for r in rows),
                             "rank3_absent_output_top8": sum(r["rank"] <= 3 and r["next_token_rank"] > 8 for r in rows)}
out["box"] = {lens: {"pass1": sum(r[lens + "_rank"] == 1 for r in rows),
                     "pass3": sum(r[lens + "_rank"] <= 3 for r in rows),
                     "jacobian_only_pass1": sum(r[lens + "_jacobian_rank"] == 1 for r in rows),
                     "top8_pass1": sum(r[lens + "_top8_rank"] == 1 for r in rows)} for lens in ("hosted_n1000", "pile5")}
out["box"]["api_local_top8_pass1_agreement"] = sum((r["rank"] == 1) == (r["hosted_n1000_top8_rank"] == 1) for r in rows)
dec = [r for r in rows if r["decoy"]]
out["decoys"] = {"n": len(dec), "wins": sum(r["rank"] < r["decoy_rank"] for r in dec),
                 "losses": sum(r["rank"] > r["decoy_rank"] for r in dec), "ties": sum(r["rank"] == r["decoy_rank"] for r in dec)}
out["continuation_reparse"] = {"correctness_disagreements": [r["tag"] for r in rows if r["correct_stored"] != r["correct_reparsed"]],
                              "gate_disagreements": [r for r in rows if r["admissible_stored"] != r["admissible_reparsed"]],
                              "reparsed_admissible": sum(r["admissible_reparsed"] for r in rows)}
out["inventory"] = {}
for relative in ("v2_api", "v2_box/hosted_n1000", "v2_box/pile5", "v2_box/continuations", "v2_box_full"):
    fs = [p for p in (RUN / relative).rglob("*") if p.is_file()]
    out["inventory"][relative] = {"files": len(fs), "bytes": sum(f.stat().st_size for f in fs), "largest_bytes": max(f.stat().st_size for f in fs)}
out["api_c_count"] = len(list((RUN / "v2_api/raw_C").glob("*.json")))

out['box']['pile5_to_hosted_rank1_ratio'] = out['box']['pile5']['pass1'] / out['box']['hosted_n1000']['pass1']
out['box']['pile5_to_hosted_rank3_ratio'] = out['box']['pile5']['pass3'] / out['box']['hosted_n1000']['pass3']
out['box']['rank1_item_overlap'] = sum(r['pile5_rank'] == 1 and r['hosted_n1000_rank'] == 1 for r in rows)
out['coverage'] = {'items': len(rows), 'api_prompt_variants': 2 * len(rows),
                   'strict_gate_complete_items': len(rows), 'partial_api_gate_items': out['api_c_count']}
summary_text = json.dumps(out, ensure_ascii=False, indent=2) + '\n'
row_text = ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows)
if args.check:
    expected = read(ROOT / 'results/summary.json')
    expected_rows = [json.loads(s) for s in (ROOT / 'results/per_item.jsonl').read_text().splitlines()]
    if out != expected or rows != expected_rows:
        raise SystemExit('FAIL: recomputed aggregates or item rows differ from the published results')
    print('PASS: all published aggregates and 105 item rows reproduce from checksum-verified raw reads')
args.out.mkdir(parents=True, exist_ok=True)
(args.out / 'summary.json').write_text(summary_text)
(args.out / 'per_item.jsonl').write_text(row_text)
for group, data in out['metrics'].items():
    print(group, 'rank-1', data['pass1'], 'rank-3', data['pass3'])
print('position', out['position'])
print('CJK', out['cjk']['new_two_digit'])
print('lens', out['box'])
