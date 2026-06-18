import duckdb
import pandas as pd
from itertools import combinations

DB_FILE = "profiling.duckdb"
GOLD_FILE = "verbund/gold_cluster.csv"

con = duckdb.connect(DB_FILE)

gold = pd.read_csv(GOLD_FILE)

def make_key(praxis, quell_id):
    praxis = str(praxis).upper()
    quell_id = str(quell_id)

    if praxis == "JUCK":
        return f"juckstadt_{quell_id}"
    if praxis == "WALD":
        return f"waldrand_{quell_id}"
    if praxis == "SCHM":
        return f"schmidt_schm_{quell_id}"
    if praxis == "BERG":
        return f"bergblick_berg_{quell_id}"

    return None

gold["kunden_key"] = gold.apply(
    lambda r: make_key(r["praxis"], r["quell_id"]),
    axis=1
)

gold_pairs = set()

for cluster_id, group in gold.groupby("cluster_id"):
    keys = list(group["kunden_key"].dropna())

    if len(keys) < 2:
        continue

    for a, b in combinations(keys, 2):
        gold_pairs.add(tuple(sorted([a, b])))

pred = con.execute("""
SELECT id_1, id_2
FROM transform.ai_matches
WHERE is_duplicate = true
""").fetchdf()

pred_pairs = set()

for _, r in pred.iterrows():
    pred_pairs.add(tuple(sorted([r["id_1"], r["id_2"]])))

tp = len(pred_pairs & gold_pairs)
fp = len(pred_pairs - gold_pairs)
fn = len(gold_pairs - pred_pairs)

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0

print("=== W9 Evaluation gegen gold_cluster.csv ===")
print(f"Gold-Dublettenpaare: {len(gold_pairs)}")
print(f"Vorhergesagte Dublettenpaare: {len(pred_pairs)}")
print(f"TP: {tp}")
print(f"FP: {fp}")
print(f"FN: {fn}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1: {f1:.4f}")

result = pd.DataFrame([{
    "gold_pairs": len(gold_pairs),
    "predicted_pairs": len(pred_pairs),
    "tp": tp,
    "fp": fp,
    "fn": fn,
    "precision": precision,
    "recall": recall,
    "f1": f1
}])

con.execute("CREATE SCHEMA IF NOT EXISTS transform")
con.register("tmp_eval", result)

con.execute("""
CREATE OR REPLACE TABLE transform.matching_evaluation AS
SELECT * FROM tmp_eval
""")

result.to_csv("output/w9/matching_evaluation.csv", index=False)

print("Ergebnis gespeichert in transform.matching_evaluation")
print("CSV gespeichert in output/w9/matching_evaluation.csv")

con.close()
