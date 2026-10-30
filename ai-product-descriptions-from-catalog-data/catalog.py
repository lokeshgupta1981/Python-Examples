import pandas as pd

NOT_FOR_COPY = {"sku", "price"}
UNITS = {"weight_g": "{} g", "capacity_l": "{} l", "warranty_years": "{} years"}


def load_catalog(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    products = []
    for row in df.to_dict(orient="records"):
        facts = {}
        for column, value in row.items():
            value = value.strip()
            if column in NOT_FOR_COPY or not value:
                continue
            facts[column] = UNITS.get(column, "{}").format(value)
        products.append({"sku": row["sku"], "facts": facts})
    return products
