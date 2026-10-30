import json
from pathlib import Path

import pandas as pd

log = json.loads(Path("results/run_log.json").read_text())
labels = pd.read_csv("data/labels.csv", dtype=str).set_index("sku")

invented = caught = missed = false_alarms = 0
for row in log:
    first = row["attempts"][0]
    flagged = any(v.startswith(("invented", "unknown")) for v in first["violations"])
    truth = labels.loc[row["sku"], "invented_first"] == "yes"
    invented += truth
    caught += truth and flagged
    missed += truth and not flagged
    false_alarms += flagged and not truth

total = len(log)
statuses = pd.Series([row["status"] for row in log]).value_counts()
seconds = [a["seconds"] for row in log for a in row["attempts"]]
print(statuses.to_string())
print(f"first answers with an invented fact: {invented} of {total}")
print(f"caught by the checker: {caught}, missed: {missed}, false alarms: {false_alarms}")
print(f"model calls: {len(seconds)}, median {sorted(seconds)[len(seconds) // 2]} s, "
      f"total {sum(seconds):.0f} s")
