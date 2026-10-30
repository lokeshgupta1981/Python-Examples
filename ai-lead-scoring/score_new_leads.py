"""Trains the combined model on the first 2,000 past leads and scores the new leads.
Writes leads_scored.csv, sorted by score, for the CRM import.

Run evaluate.py first; it fills signals_cache.json. Messages missing from the cache
are read here.
"""
import json
from datetime import datetime, timezone

import pandas as pd

import scorer
from scorer import TRAIN_ROWS


def main() -> None:
    history = scorer.load_leads("history.csv").iloc[:TRAIN_ROWS]  # the same 2,000 leads
    new_leads = scorer.load_leads("new_leads.csv")
    cache = scorer.load_signals()
    for text in set(new_leads["message"]) - set(cache):
        signals, _ = scorer.read_message(text)
        cache[text] = signals.model_dump()
    scorer.SIGNALS_CACHE.write_text(json.dumps(cache, indent=2))

    model = scorer.train(scorer.features(history, cache), history["converted"])
    table = scorer.features(new_leads, cache).reindex(
        columns=model.feature_names_in_, fill_value=0)
    probability = model.predict_proba(table)[:, 1]

    scored_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for (index, lead), p in zip(new_leads.iterrows(), probability):
        score = round(p * 100)
        signals = cache[lead["message"]]
        rows.append({
            "lead_id": lead["lead_id"],
            "score": score,
            "tier": scorer.tier(score),
            "intent": signals["intent"],
            "urgency": signals["urgency"],
            "reason": scorer.full_reason(scorer.fit_reason(model, table.loc[index]),
                                         signals["reason"]),
            "model": scorer.MODEL,
            "prompt_version": scorer.PROMPT_VERSION,
            "scored_at": scored_at,
        })

    scored = pd.DataFrame(rows).sort_values("score", ascending=False, kind="stable")
    scored.to_csv("leads_scored.csv", index=False)
    print(scored["tier"].value_counts().reindex(["hot", "warm", "cold"]).to_dict())
    print(scored.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
