"""Step 8: move the approved emails into category folders and write digest.md.

Nothing is sent or deleted. Skipped emails stay in mailbox/inbox.
Usage: python apply.py [results.json]
"""
import csv
import json
import shutil
import sys
from pathlib import Path

from mail_reader import parse_message
from triage import TriageResult, ungrounded

FOLDERS = {"URGENT": "urgent", "NEEDS_REPLY": "needs-reply", "FYI": "fyi",
           "SPAM_LIKE": "spam-like"}


def grounded_items(entry: dict, path: Path) -> list[dict]:
    """The model's action items without the ones whose quote is not in the email."""
    answer = entry["guarded"]["result"]
    if entry["rule"] or not answer:
        return []
    result = TriageResult.model_validate(answer)
    bad = set(ungrounded(result, parse_message(path.name, path.read_bytes())))
    return [a for a in answer["action_items"] if a["quote"] not in bad]


def main() -> None:
    results = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else "results.json").read_text())
    with open("decisions.csv", newline="") as f:
        decisions = list(csv.DictReader(f))

    inbox = Path("mailbox/inbox")
    digest = {"URGENT": [], "NEEDS_REPLY": []}
    counts = {}
    for row in decisions:
        category = row["decision"]
        counts[category] = counts.get(category, 0) + 1
        source = inbox / row["file"]
        if category == "SKIP" or not source.exists():
            continue
        if category in digest:
            item = parse_message(source.name, source.read_bytes())
            digest[category].append((item, grounded_items(results[row["file"]], source)))
        target = Path("mailbox") / FOLDERS[category]
        target.mkdir(exist_ok=True)
        shutil.move(source, target / source.name)

    lines = ["# Inbox digest", ""]
    for category, title in (("URGENT", "Urgent"), ("NEEDS_REPLY", "Needs a reply")):
        lines += [f"## {title} ({len(digest[category])})", ""]
        for item, actions in digest[category]:
            lines.append(f"- **{item.subject}** from {item.sender} ({item.file})")
            for action in actions:
                due = f", due {action['due']}" if action["due"] else ""
                lines.append(f"  - {action['task']} ({action['owner']}{due}): "
                             f"\"{action['quote']}\"")
        lines.append("")
    lines.append("Also filed: " + ", ".join(
        f"{counts.get(c, 0)} {c}" for c in ("FYI", "SPAM_LIKE", "SKIP")))
    Path("digest.md").write_text("\n".join(lines) + "\n")
    print(f"Moved {sum(v for k, v in counts.items() if k != 'SKIP')} emails, "
          f"{counts.get('SKIP', 0)} left in the inbox, wrote digest.md")


if __name__ == "__main__":
    main()
