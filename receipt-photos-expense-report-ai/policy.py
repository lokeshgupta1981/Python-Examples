"""Step 6: apply the expense policy to the extracted receipts."""
from datetime import date

import yaml

PER_RECEIPT_LIMITS = ("lodging", "transport", "supplies")


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def apply_policy(results, policy, trip):
    """Give every receipt a status: approved, flagged (with reasons) or review."""
    rates = policy["currencies"]
    limits = policy["limits"]
    start, end = trip["start"], trip["end"]
    seen, meals_per_day, lines = {}, {}, []
    for item in results:
        r = item["receipt"]
        line = {"file": item["file"], **(r or {}), "total_eur": None}
        if item["problems"]:
            line.update(status="review", reason="; ".join(item["problems"]))
            lines.append(line)
            continue

        day = date.fromisoformat(r["date"])
        eur = round(r["total"] * rates[r["currency"]], 2)
        reasons = []
        key = ((r["merchant"] or "").lower().strip(), r["date"], r["total"])
        if key in seen:
            reasons.append(f"possible duplicate of {seen[key]}")
        else:
            seen[key] = item["file"]
        if not start <= day <= end:
            reasons.append("outside trip dates")
        if day.weekday() >= 5 and r["category"] not in policy["weekend_allowed"]:
            reasons.append("weekend expense")

        if r["category"] == "meals" and not reasons:  # duplicates don't count twice
            spent = round(meals_per_day.get(r["date"], 0) + eur, 2)
            meals_per_day[r["date"]] = spent
            if spent > limits["meals_per_day"]:
                reasons.append(f"meals on {r['date']} reach {spent:.2f} EUR, "
                               f"limit {limits['meals_per_day']:.2f}")
        if r["category"] in PER_RECEIPT_LIMITS:
            limit = limits[f"{r['category']}_per_receipt"]
            if eur > limit:
                reasons.append(f"{r['category']} {eur:.2f} EUR, limit {limit:.2f}")

        line.update(total_eur=eur, status="flagged" if reasons else "approved",
                    reason="; ".join(reasons))
        lines.append(line)
    return lines
