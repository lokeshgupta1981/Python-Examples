"""Re-checks the drafts saved in ./results without calling the model.

Use it after changing a check such as DURATION. If hand_check.json exists
({"<incident>--<variant>": "Right" | "Wrong"}), its verdicts are printed too.
"""
import json
from pathlib import Path

import postmortem as pm
from evaluate import HERE, print_row, score


def main():
    labels = json.loads((HERE / "incidents" / "labels.json").read_text())
    hand_file = HERE / "hand_check.json"
    hand = json.loads(hand_file.read_text()) if hand_file.exists() else {}
    print("| Incident | Variant | Wrong durations | Impact minutes (true / stated) | Keyword rubric |"
          + (" Root cause by hand |" if hand else ""))
    print("|---|---|---|---|---|" + ("---|" if hand else ""))
    for path in sorted((HERE / "results").glob("*.json")):
        saved = json.loads(path.read_text())
        name, variant = saved["incident"], saved["variant"]
        events, facts, names, _ = pm.prepare(HERE / "incidents" / name)
        narrative = pm.Narrative.model_validate(saved["narrative"])
        r = score(name, variant, narrative, events, facts, names, labels[name]["keywords"])
        print_row(r, hand.get(path.stem))


if __name__ == "__main__":
    main()
