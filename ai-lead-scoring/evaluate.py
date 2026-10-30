"""Reads every distinct message once, trains two models on 2,000 past leads and
compares three scorers on the 500 held-out leads. Writes results.json.

Usage: python evaluate.py [--skip-llm-alone]
"""
import json
import sys
import time

import pandas as pd

import scorer
from scorer import TRAIN_ROWS

INJECTION_LEAD = "P2018"
SAMPLE_SIZE = 24  # held-out leads for the LLM-alone scorer, plus INJECTION_LEAD


def read_with_retry(text: str) -> tuple[scorer.LeadSignals, bool]:
    """A server restart looks like a fallback, so try once more after 30 seconds."""
    signals, from_model = scorer.read_message(text)
    if not from_model:
        time.sleep(30)
        signals, from_model = scorer.read_message(text)
    return signals, from_model


def fill_cache(history: pd.DataFrame, new_leads: pd.DataFrame) -> tuple[dict, int]:
    cache = scorer.load_signals()  # signals_cache.json, if it exists
    messages = sorted(set(history["message"]) | set(new_leads["message"]))
    fallbacks = 0
    for text in messages:
        if text in cache:
            continue  # read in an earlier run
        start = time.perf_counter()
        signals, from_model = read_with_retry(text)
        fallbacks += not from_model
        print(f"{time.perf_counter() - start:6.1f}s {signals.intent:11} {signals.urgency:12} "
              f"{signals.quantity:4} {text[:50]}")
        cache[text] = signals.model_dump()
        scorer.SIGNALS_CACHE.write_text(json.dumps(cache, indent=2))
    return cache, fallbacks


def llm_alone_sample(holdout: pd.DataFrame) -> pd.DataFrame:
    """24 held-out leads with the holdout's share of converted leads, plus the injection lead."""
    pool = holdout[holdout["lead_id"] != INJECTION_LEAD]
    buyers = round(SAMPLE_SIZE * holdout["converted"].mean())
    sample = pd.concat([
        pool[pool["converted"] == 1].sample(buyers, random_state=7),
        pool[pool["converted"] == 0].sample(SAMPLE_SIZE - buyers, random_state=7),
        holdout[holdout["lead_id"] == INJECTION_LEAD],
    ])
    return sample.sort_index()


def main() -> None:
    history = scorer.load_leads("history.csv")
    new_leads = scorer.load_leads("new_leads.csv")
    print(f"{len(history)} past leads, {history['converted'].mean():.1%} converted")

    cache, fallbacks = fill_cache(history, new_leads)

    train, holdout = history.iloc[:TRAIN_ROWS], history.iloc[TRAIN_ROWS:]  # 2,000 / 500
    fields_only = scorer.train(scorer.features(train), train["converted"])
    with_llm = scorer.train(scorer.features(train, cache), train["converted"])

    weights = pd.Series(with_llm.coef_[0], index=with_llm.feature_names_in_)
    print("Signal weights:", weights.filter(regex="^(intent|urgency|quantity)").round(2).to_dict())

    scores = pd.DataFrame({
        "fields_only": fields_only.predict_proba(scorer.features(holdout))[:, 1],
        "with_llm": with_llm.predict_proba(scorer.features(holdout, cache))[:, 1],
        "hidden_rule": holdout["true_probability"],
    }, index=holdout.index)
    converted = holdout["converted"]

    results = {
        "holdout_leads": len(holdout),
        "holdout_converted": round(converted.mean(), 3),
        "fallbacks": fallbacks,
        "holdout": {name: scorer.metrics(converted, scores[name]) for name in scores},
    }

    if "--skip-llm-alone" not in sys.argv:
        sample = llm_alone_sample(holdout)
        llm_scores = []
        for _, lead in sample.iterrows():
            start = time.perf_counter()
            score = scorer.llm_score(lead)
            print(f"{time.perf_counter() - start:6.1f}s {lead['lead_id']} LLM alone: {score}")
            llm_scores.append(score if score is not None else 50)
        sample_scores = scores.loc[sample.index].assign(llm_alone=llm_scores)
        results["sample"] = {
            "leads": len(sample),
            "converted": int(sample["converted"].sum()),
            "metrics": {name: scorer.metrics(sample["converted"], sample_scores[name])
                        for name in sample_scores},
            "llm_alone_values": sorted(set(llm_scores)),
        }
        injection = sample_scores.loc[sample["lead_id"] == INJECTION_LEAD].iloc[0]
        results["injection_lead"] = {
            "fields_only": round(injection["fields_only"] * 100),
            "with_llm": round(injection["with_llm"] * 100),
            "llm_alone": int(injection["llm_alone"]),
        }

    scorer.Path("results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
