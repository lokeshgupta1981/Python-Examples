"""Answer a business question about shop.db in plain English.

The model writes the SQL and explains the result. Plain code decides whether the SQL runs:
one parsed query on known tables, a row limit, a read-only connection and a time limit.
"""
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

import ollama
import sqlglot
from pydantic import BaseModel
from sqlglot import exp

MODEL = "qwen2.5:7b"
TODAY = "2026-10-25"  # fixed so the example gives the same answers every day
HERE = Path(__file__).parent
DB_URI = (HERE / "shop.db").as_uri() + "?mode=ro"
SCHEMA = (HERE / "schema.md").read_text()
MAX_ROWS = 200
TIME_LIMIT_SECONDS = 5
MAX_SQL_TOKENS = 400  # a longer reply means the model is stuck in a loop
MAX_ANSWER_TOKENS = 200

ALLOWED_TABLES = {"customers", "products", "orders", "order_items"}
WRITE_NODES = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter,
               exp.Merge, exp.TruncateTable, exp.Attach, exp.Pragma, exp.Command)


class SqlAnswer(BaseModel):
    can_answer: bool
    assumptions: str
    sql: str


class Explanation(BaseModel):
    answer: str


class InvalidSql(Exception):
    """The text is not valid SQL. Unlike a blocked query, the model gets one more try."""


def chat(messages, schema, max_tokens):
    """Send one chat request with structured output and a reply length limit."""
    for attempt in range(3):
        try:
            response = ollama.chat(model=MODEL, messages=messages, format=schema,
                                   options={"temperature": 0, "num_predict": max_tokens})
            break
        except ConnectionError:  # the Ollama server is not reachable (yet)
            if attempt == 2:
                raise
            time.sleep(5)
    if response.done_reason == "length":
        raise ValueError(f"the model reply was cut off after {max_tokens} tokens")
    return response.message.content


def generate_sql(question, error=None, previous_sql=None):
    prompt = (f"You write one SQLite SELECT query that answers a business question.\n"
              f"Today is {TODAY}.\n\n{SCHEMA}\n"
              "Use only the tables and columns above. If the data can't answer the question, "
              "set can_answer to false and sql to an empty string.\n"
              "Reply in JSON with can_answer, assumptions and sql. "
              "The sql field holds only the query, without a semicolon.")
    messages = [{"role": "system", "content": prompt},
                {"role": "user", "content": question}]
    if error:
        messages += [{"role": "assistant", "content": previous_sql},
                     {"role": "user", "content": f"That query failed with: {error}. "
                                                 "Write a corrected query."}]
    reply = chat(messages, SqlAnswer.model_json_schema(), MAX_SQL_TOKENS)
    return SqlAnswer.model_validate_json(reply)


def add_limit(query):
    """Return the query as SQLite text with at most MAX_ROWS rows."""
    limit = query.args.get("limit")
    current = limit.expression if limit is not None else None
    if not (isinstance(current, exp.Literal) and current.is_int
            and int(current.this) <= MAX_ROWS):
        query = query.limit(MAX_ROWS)  # adds the clause, or replaces a larger or odd one
    return query.sql(dialect="sqlite")


def check_sql(sql):
    """Return the query to run with a row limit.

    Raise InvalidSql if the text isn't valid SQL, or ValueError if the query is blocked.
    """
    try:
        statements = [s for s in sqlglot.parse(sql, read="sqlite") if s is not None]
    except sqlglot.errors.ParseError as e:
        first = e.errors[0] if e.errors else {}
        raise InvalidSql(f"syntax error near '{first.get('start_context', '')}"
                         f"{first.get('highlight', '')}'") from e
    if len(statements) != 1:
        raise ValueError(f"expected one statement, got {len(statements)}")
    query = statements[0]
    if not isinstance(query, exp.Query):  # SELECT, UNION, INTERSECT, EXCEPT
        raise ValueError(f"only queries are allowed, got {type(query).__name__}")
    for node in query.find_all(*WRITE_NODES):  # look inside CTEs and subqueries too
        raise ValueError(f"{type(node).__name__} is not allowed anywhere in the query")
    cte_names = {cte.alias_or_name.lower() for cte in query.find_all(exp.CTE)}
    for table in query.find_all(exp.Table):
        name = table.name.lower()
        if name not in ALLOWED_TABLES and name not in cte_names:
            raise ValueError(f"unknown table {table.name}")
    return add_limit(query)


def run_query(sql):
    # mode=ro: SQLite refuses every write here, even one that check_sql() missed
    con = sqlite3.connect(DB_URI, uri=True)
    deadline = time.monotonic() + TIME_LIMIT_SECONDS
    # Called every 10,000 SQLite steps; returning a true value stops the query
    con.set_progress_handler(lambda: time.monotonic() > deadline, 10_000)
    try:
        cursor = con.execute(sql)
        columns = [d[0] for d in cursor.description]
        return columns, cursor.fetchall()
    finally:
        con.close()


def explain(question, sql, columns, rows):
    def cell(v):
        return f"{v:.2f}" if isinstance(v, float) else str(v)  # 58826.25, not 58826.2499
    table = "\n".join([", ".join(columns)] + [", ".join(map(cell, r)) for r in rows[:50]])
    messages = [{"role": "system", "content":
                 "Answer the business question in one or two plain English sentences, using "
                 "only the numbers and names in the result table. Don't calculate new numbers. "
                 "Reply in JSON with one field, answer, that holds the sentences."},
                {"role": "user", "content":
                 f"Question: {question}\nSQL: {sql}\nResult table:\n{table}"}]
    reply = chat(messages, Explanation.model_json_schema(), MAX_ANSWER_TOKENS)
    return Explanation.model_validate_json(reply).answer


def numbers_match(sentence, rows, context):
    """Every number in the sentence must appear in the rows, the question or the SQL."""
    found = [float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*\.?\d*", sentence)]
    known = [v for row in rows for v in row if isinstance(v, (int, float))]
    known += [float(n) for row in rows for v in row if isinstance(v, str)
              for n in re.findall(r"\d+\.?\d*", v)]
    known += [float(n) for n in re.findall(r"\d+\.?\d*", context)]  # years, "top 5"

    def matches(n, v):  # 58826.25 or 58826 match 58826.2499, but 58800 doesn't
        return abs(n - v) < 0.006 or any(n == round(v, d) for d in (0, 1, 2))
    unknown = {n for n in found if not any(matches(n, v) for v in known)}
    return not unknown, unknown


def ask(question):
    result = {"question": question, "retries": 0}
    try:
        answer = generate_sql(question)
    except ValueError as e:  # cut-off or invalid JSON from the model
        return {**result, "status": "error", "reason": str(e)}
    if not answer.can_answer:
        return {**result, "status": "refused", "assumptions": answer.assumptions}
    sql = answer.sql
    for attempt in (1, 2):
        try:
            final_sql = check_sql(sql)
            columns, rows = run_query(final_sql)
            break
        except ValueError as e:  # the safety gate said no: never retry
            return {**result, "status": "blocked", "sql": sql, "reason": str(e)}
        except (InvalidSql, sqlite3.Error) as e:
            if attempt == 2:
                return {**result, "status": "error", "sql": sql, "reason": str(e)}
            result["retries"] = 1
            try:
                sql = generate_sql(question, error=str(e), previous_sql=sql).sql
            except ValueError as e2:
                return {**result, "status": "error", "sql": sql, "reason": str(e2)}
    try:
        sentence = explain(question, final_sql, columns, rows)
    except ValueError:  # cut-off or invalid JSON: show the table without a sentence
        sentence = ""
    ok, unknown = numbers_match(sentence, rows, question + " " + final_sql)
    ok = ok and len(sentence.split()) >= 4  # a sentence, not "id: 135"
    return {**result, "status": "answered", "assumptions": answer.assumptions,
            "sql": final_sql, "columns": columns, "rows": rows,
            "answer": sentence if ok else None,
            "unchecked_answer": None if ok else sentence,
            "unknown_numbers": sorted(unknown)}


def main():
    question = " ".join(sys.argv[1:]) or "What are the top 5 products by revenue last quarter?"
    result = ask(question)
    print(f"Question: {question}")
    print(f"Status:   {result['status']} (retries: {result['retries']})")
    if result.get("sql"):
        print(f"SQL:      {result['sql']}")
    if result["status"] != "answered":
        print(f"Reason:   {result.get('reason') or result.get('assumptions')}")
        return
    print(" | ".join(result["columns"]))
    for row in result["rows"][:20]:
        print(" | ".join(map(str, row)))
    if len(result["rows"]) > 20:
        print(f"... {len(result['rows']) - 20} more rows")
    if result["answer"]:
        print(f"Answer:   {result['answer']}")
    else:
        print("Answer:   (not shown: the sentence failed the numbers check, see the table)")
    print(json.dumps({"assumptions": result["assumptions"]}))


if __name__ == "__main__":
    main()
