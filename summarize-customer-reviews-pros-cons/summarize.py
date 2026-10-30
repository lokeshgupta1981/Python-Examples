"""Summarize customer reviews into pros and cons.

The model extracts, merges and words; plain code cleans, checks and counts.
Every function here is shown in the article, in this order.
"""
import re
from typing import Literal

import ollama
import pandas as pd
from pydantic import BaseModel, Field

# --- Step 1: load and clean the reviews -------------------------------------

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b")

def load_reviews(path, sku):
    df = pd.read_csv(path)
    df = df[df["sku"] == sku].copy()
    df["text"] = df["text"].fillna("").str.strip()
    df = df[df["text"] != ""] # empty reviews
    df = df.drop_duplicates(subset="text") # the same review posted twice
    df["text"] = df["text"].str.replace(EMAIL, "<EMAIL>", regex=True)
    df["text"] = df["text"].str.replace(PHONE, "<PHONE>", regex=True)
    return df[["review_id", "rating", "text"]].to_dict("records")

# --- Step 2: split reviews into batches -------------------------------------

def estimate_tokens(text):
    return len(text) // 4 + 4 # about 4 characters per token, plus the id

def make_batches(reviews, token_budget=400, max_reviews=10):
    batches, current, used = [], [], 0
    for review in reviews:
        cost = estimate_tokens(review["text"])
        if current and (used + cost > token_budget or len(current) == max_reviews):
            batches.append(current)
            current, used = [], 0
        current.append(review)
        used += cost
    if current:
        batches.append(current)
    return batches

# --- Step 3: extract pros and cons per review -------------------------------

MODEL = "qwen2.5:7b"

class Point(BaseModel):
    review_id: str
    aspect: str = Field(max_length=40, description="1 to 3 words, like 'battery life'")
    polarity: Literal["pro", "con"]
    quote: str = Field(max_length=150, description="words copied exactly from the review")

class BatchPoints(BaseModel):
    points: list[Point] = Field(max_length=40)

EXTRACT_PROMPT = """You read customer reviews of a headlamp.
For each review, list every pro and every con it mentions about the product.
- aspect: a short label of 1 to 3 words for what the point is about
- polarity: pro or con
- quote: the words from the review that state the point, copied exactly
Skip delivery, packaging and plans to use the product. Skip reviews with no pros or cons.

Reviews:
{reviews}"""

def call_model(prompt, schema, num_predict):
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        format=schema.model_json_schema(),
        options={"temperature": 0, "num_predict": num_predict},
    )
    return schema.model_validate_json(response.message.content), response

def extract_points(batch):
    lines = "\n".join(f"[{r['review_id']}] {r['text']}" for r in batch)
    result, _ = call_model(EXTRACT_PROMPT.format(reviews=lines), BatchPoints, 1024)
    return [p.model_dump() for p in result.points]

# --- Step 4: check every quote against its review ---------------------------

def normalize(text):
    return " ".join(text.lower().split()).strip(" .,!\"'")

def check_quotes(points, reviews):
    texts = {r["review_id"]: normalize(r["text"]) for r in reviews}
    kept, rejected = [], []
    for p in points:
        review = texts.get(p["review_id"])
        quote = normalize(p["quote"])
        if review is not None and quote and quote in review:
            kept.append(p)
        else:
            rejected.append(p)
    return kept, rejected

# --- Step 5: merge similar aspects ------------------------------------------

class Group(BaseModel):
    aspect: str = Field(max_length=40, description="the shared name for these labels")
    label_ids: list[int] = Field(max_length=40)

class AspectGroups(BaseModel):
    groups: list[Group] = Field(max_length=20)

MERGE_PROMPT = """These labels describe aspects of a headlamp in customer reviews.
Each line has a number, a label, and one quote where a customer used the label.
Group the labels by the part or feature of the headlamp they are about, even when
they are worded differently. Give each group a short name of 1 to 3 words.
Use at most 8 groups. Put every label number in exactly one group.

Labels:
{labels}"""

def merge_aspects(points):
    examples = {}
    for p in points: # one example quote per label
        examples.setdefault(p["aspect"].strip().lower(), p["quote"])
    labels = sorted(examples)
    lines = "\n".join(f'{i}. {label} ("{examples[label]}")'
                      for i, label in enumerate(labels, 1))
    result, _ = call_model(MERGE_PROMPT.format(labels=lines), AspectGroups, 1024)
    mapping = {}
    for group in result.groups:
        for i in group.label_ids:
            if 1 <= i <= len(labels): # ignore numbers we never sent
                mapping.setdefault(labels[i - 1], group.aspect.strip().lower())
    missing = [label for label in labels if label not in mapping]
    for label in missing: # keep an unmapped label as its own aspect
        mapping[label] = label
    return mapping, missing

# --- Step 6: count pros and cons in code ------------------------------------

MIN_REVIEWS = 3 # aspects mentioned in fewer reviews are left out

def pick_quote(quotes):
    """The quote customers repeated most often; the shorter one on a tie."""
    counts = quotes.value_counts()
    top = counts[counts == counts.max()].index
    return min(top, key=len)

def count_points(points, mapping, total_reviews):
    df = pd.DataFrame(points)
    df["aspect"] = df["aspect"].str.strip().str.lower().map(mapping)
    table = (df.groupby(["aspect", "polarity"])
               .agg(reviews=("review_id", "nunique"),
                    quote=("quote", pick_quote))
               .reset_index())
    table["share"] = (100 * table["reviews"] / total_reviews).round().astype(int)
    table = table[table["reviews"] >= MIN_REVIEWS]
    return table.sort_values(["polarity", "reviews"], ascending=[False, False])

# --- Step 7: write the summary from the table -------------------------------

class Overview(BaseModel):
    overview: str = Field(max_length=500, description="two or three sentences")

SUMMARY_PROMPT = """Write a two or three sentence overview of what {total} customers said
about a headlamp, for its product page. Use only the facts in this table.
If you give a number, use the review count or the share exactly as written.
Say "many" or "some" instead of "most", unless a share is over 50%.

{table}"""

def write_summary(table, total, feedback=""):
    lines = [f"- {r.polarity}: {r.aspect}, {r.reviews} reviews ({r.share}%)"
             for r in table.itertuples()]
    prompt = SUMMARY_PROMPT.format(total=total, table="\n".join(lines)) + feedback
    result, _ = call_model(prompt, Overview, 300)
    return result.overview

def summary_card(sku, overview, table, total):
    lines = [f"### What {total} customers say about the {sku}", "", overview, ""]
    for polarity, title in (("pro", "Pros"), ("con", "Cons")):
        lines.append(f"**{title}**")
        for r in table[table["polarity"] == polarity].itertuples():
            lines.append(f'- {r.aspect.capitalize()}: {r.reviews} reviews ({r.share}%), '
                         f'"{r.quote}"')
        lines.append("")
    return "\n".join(lines)

# --- Step 8: check the summary for invented claims --------------------------

MOST = re.compile(r"\b(most|majority|almost all|nearly all|everyone|all)\b", re.I)

def check_summary(overview, table, total):
    allowed = {total} | set(table["reviews"]) | set(table["share"])
    problems = []
    for number in re.findall(r"\d+", overview):
        if int(number) not in allowed:
            problems.append(f"number {number} is not in the table")
    match = MOST.search(overview)
    if match and table["share"].max() <= 50:
        problems.append(f"says '{match.group(0)}' but no aspect is over 50%")
    if '"' in overview:
        problems.append("contains a quote; quotes come from the table only")
    return problems

def summarize(overview_fn, table, total):
    overview = overview_fn(table, total)
    problems = check_summary(overview, table, total)
    if problems:
        feedback = "\n\nYour previous answer had these problems, fix them:\n- "
        overview = overview_fn(table, total, feedback + "\n- ".join(problems))
        problems = check_summary(overview, table, total)
    return overview, problems

# --- Comparison: one prompt with all reviews --------------------------------

class Claim(BaseModel):
    aspect: str = Field(max_length=40)
    polarity: Literal["pro", "con"]
    reviews: int = Field(ge=0, description="how many reviews mention it")
    quote: str = Field(max_length=150, description="copied exactly from one review")

class AllAtOnce(BaseModel):
    overview: str = Field(max_length=500)
    claims: list[Claim] = Field(max_length=12)

SINGLE_PROMPT = """Here are all {total} customer reviews of a headlamp.
Write a two or three sentence overview for the product page. Then list the main pros
and cons. For each one, give the number of reviews that mention it and one quote copied
exactly from a review.

Reviews:
{reviews}"""

def single_prompt(reviews):
    lines = "\n".join(f"[{r['review_id']}] {r['text']}" for r in reviews)
    prompt = SINGLE_PROMPT.format(total=len(reviews), reviews=lines)
    result, _ = call_model(prompt, AllAtOnce, 1024)
    return result.model_dump()
