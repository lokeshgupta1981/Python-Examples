"""Write 12 weeks of BeanBox order lines to orders.csv, with three planted stories.

The stories are listed in planted_events.json:
- Marketplace returns more than double from 2026-W41.
- North region orders halve from 2026-W42.
- A new product, the Cold Brew Kit, launches in 2026-W43.
"""
import json
from datetime import date, timedelta

import numpy as np
import pandas as pd

SEED = 7
FIRST_MONDAY = date(2026, 8, 3)  # Monday of ISO week 2026-W32
WEEKS = 12                       # 2026-W32 to 2026-W43

REGIONS = {"North": 0.28, "East": 0.24, "South": 0.26, "West": 0.22}
CHANNELS = {"Web Shop": 0.55, "Marketplace": 0.30, "Subscription": 0.15}
PRODUCTS = {  # name: (unit price, weight)
    "House Blend 1kg": (24.0, 0.30),
    "Espresso Roast 500g": (16.5, 0.25),
    "Decaf 500g": (15.0, 0.12),
    "Single Origin 250g": (12.5, 0.18),
    "Pour-Over Set": (39.0, 0.08),
    "Grinder Pro": (89.0, 0.07),
}
NEW_PRODUCT = ("Cold Brew Kit", 34.0, 0.10)

MARKETPLACE_RETURNS_FROM = 9   # week index of 2026-W41
NORTH_DROP_FROM = 10           # week index of 2026-W42
LAUNCH_WEEK = 11               # week index of 2026-W43


def make_orders(rng):
    rows, order_id = [], 100000
    for week in range(WEEKS):
        products = dict(PRODUCTS)
        if week >= LAUNCH_WEEK:
            name, price, weight = NEW_PRODUCT
            products[name] = (price, weight)
        names = list(products)
        weights = np.array([products[n][1] for n in names])
        weights = weights / weights.sum()

        for day in range(7):
            when = FIRST_MONDAY + timedelta(days=week * 7 + day)
            for _ in range(rng.poisson(43)):
                region = rng.choice(list(REGIONS), p=list(REGIONS.values()))
                if region == "North" and week >= NORTH_DROP_FROM and rng.random() < 0.5:
                    continue  # half of the North orders disappear
                channel = rng.choice(list(CHANNELS), p=list(CHANNELS.values()))
                return_p = 0.015
                if channel == "Marketplace":
                    return_p = 0.10 if week >= MARKETPLACE_RETURNS_FROM else 0.035
                discount = 0.10 if channel == "Subscription" else rng.choice([0.0, 0.0, 0.0, 0.05])
                order_id += 1
                for product in rng.choice(names, size=rng.choice([1, 2, 3], p=[0.6, 0.3, 0.1]),
                                          replace=False, p=weights):
                    rows.append({
                        "order_id": order_id,
                        "date": when.isoformat(),
                        "region": region,
                        "channel": channel,
                        "product": product,
                        "units": int(rng.choice([1, 1, 2, 2, 3, 3])),
                        "unit_price": products[product][0],
                        "discount": discount,
                        "returned": int(rng.random() < return_p),
                    })
    return pd.DataFrame(rows)


def main():
    orders = make_orders(np.random.default_rng(SEED))
    orders.to_csv("orders.csv", index=False)
    events = [
        {"week": "2026-W41", "fact_id": "marketplace_return_rate",
         "story": "Marketplace returns more than double"},
        {"week": "2026-W42", "fact_id": "north_change",
         "story": "North region orders halve"},
        {"week": "2026-W43", "fact_id": "cold_brew_kit_change",
         "story": "New product Cold Brew Kit launches"},
    ]
    with open("planted_events.json", "w") as f:
        json.dump(events, f, indent=2)
    print(f"Wrote {len(orders)} order lines to orders.csv")


if __name__ == "__main__":
    main()
