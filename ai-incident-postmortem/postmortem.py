"""Drafts a blameless incident postmortem from a Slack export, alerts and a deploy log.

Code builds the timeline and computes every time and duration. A local model on
Ollama writes only the prose sections. Code then checks every value in the
draft and flags blaming wording before a person edits it.

    python postmortem.py incidents/checkout-outage --dry-run
    python postmortem.py incidents/checkout-outage
"""
import argparse
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import ollama
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field

MODEL = "qwen2.5:7b"


# ---------------------------------------------------------------- Step 1: load

@dataclass
class Event:
    time: datetime  # UTC
    kind: str  # chat, status, alert, deploy, or noise (dropped later)
    source: str  # where the row came from, such as slack:1791987310.000500
    text: str
    user: str = ""
    id: str = ""  # E1, E2 ... given after sorting

    @property
    def hhmm(self):
        return self.time.strftime("%H:%M")


def load_slack(folder):
    """Reads every channel folder of a Slack export: one JSON file per day."""
    events = []
    for day_file in sorted(folder.glob("*/*.json")):
        for msg in json.loads(day_file.read_text()):
            if msg.get("type") != "message":
                continue
            when = datetime.fromtimestamp(float(msg["ts"]), tz=timezone.utc)
            kind = "status" if msg.get("subtype") == "bot_message" else "chat"
            if msg.get("subtype") in ("channel_join", "channel_leave"):
                kind = "noise"
            events.append(Event(when, kind, f"slack:{msg['ts']}", msg["text"],
                                msg.get("user", "")))
    return events


def parse_utc(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_alerts(path):
    """One "alert" event per entry in alerts.json."""
    events = []
    for n, a in enumerate(json.loads(path.read_text()), 1):
        text = f"{a['alert']} {a['event']}: {a['detail']}"
        events.append(Event(parse_utc(a["at"]), "alert", f"{path.name}:{n}", text))
    return events


def load_deploys(path):
    """One "deploy" event per line of deploys.log, with the line number in the source."""
    events = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        stamp, text = line.split(" ", 1)
        events.append(Event(parse_utc(stamp), "deploy", f"{path.name}:{n}", text))
    return events


# ------------------------------------------------- Step 2: timeline and facts

EMOJI_ONLY = re.compile(r"^(\s*(:[\w+\-]+:|\+1)\s*)+$")


def build_timeline(folder):
    events = (load_slack(folder / "slack") + load_alerts(folder / "alerts.json")
              + load_deploys(folder / "deploys.log"))
    events = [e for e in events
              if e.kind != "noise" and not EMOJI_ONLY.match(e.text)]
    events.sort(key=lambda e: e.time)
    for n, e in enumerate(events, 1):
        e.id = f"E{n}"
    return events


def minutes(start, end):
    """Whole minutes between two HH:MM times, so the numbers match the times we show."""
    start = start.replace(second=0, microsecond=0)
    end = end.replace(second=0, microsecond=0)
    return int((end - start).total_seconds() // 60)


def compute_facts(events):
    alerts = [e for e in events if e.kind == "alert"]
    start = next(e for e in alerts if " triggered" in e.text)
    ack = next(e for e in alerts if " acknowledged" in e.text)
    impact_end = [e for e in alerts if " resolved" in e.text][-1]
    mitigated = next(e for e in events if e.text == "Status changed to Mitigated")
    resolved = next(e for e in events if e.text == "Status changed to Resolved")
    changes = [e for e in events if e.kind == "deploy" and e.time <= start.time]

    facts = {
        "date": start.time.strftime("%Y-%m-%d"),
        "impact_start": start.hhmm,
        "acknowledged": ack.hhmm,
        "mitigated": mitigated.hhmm,
        "impact_end": impact_end.hhmm,
        "resolved": resolved.hhmm,
        "minutes_to_acknowledge": minutes(start.time, ack.time),
        "minutes_to_mitigate": minutes(start.time, mitigated.time),
        "impact_minutes": minutes(start.time, impact_end.time),
        "minutes_to_resolve": minutes(start.time, resolved.time),
    }
    if changes:
        facts["last_change"] = f"{changes[-1].hhmm} {changes[-1].text}"
        facts["minutes_change_to_impact"] = minutes(changes[-1].time, start.time)
    return facts


# ------------------------------------------------- Step 3: mask names, secrets

SECRET = re.compile(r"(?i)\b(\w*(?:password|passwd|pwd|token|secret|api_key))"
                    r"(\s*[=:]\s*)\S+")


def load_people(folder):
    """Returns {user id: role} and {name: role} from roles.json and the Slack users.json."""
    roles = json.loads((folder / "roles.json").read_text())
    names = {}
    users_file = folder / "slack" / "users.json"
    users = json.loads(users_file.read_text()) if users_file.exists() else []
    for u in users:
        role = roles.get(u["id"])
        if not role:
            continue
        for name in (u.get("real_name", ""), u.get("name", "")):
            if name:
                names[name] = role
                names[name.split()[0]] = role
    return roles, names


def mask_text(text, roles, names):
    for uid, role in roles.items():
        text = text.replace(f"<@{uid}>", f"the {role}")
        text = re.sub(rf"\bby={uid}\b", f"by the {role}", text)
        text = re.sub(rf"\b{uid}\b", f"the {role}", text)
    for name in sorted(names, key=len, reverse=True):  # full names before first names
        text = re.sub(rf"(?i)\b{re.escape(name)}\b", f"the {names[name]}", text)
    return SECRET.sub(r"\1\2<SECRET>", text)


def mask(events, roles, names):
    """Replaces names, mentions and user ids with roles, and masks secrets. Returns the count."""
    masked = 0
    for e in events:
        new = mask_text(e.text, roles, names)
        masked += new != e.text
        e.text = new
        e.user = roles.get(e.user, e.user)
    return masked


# ------------------------------------------------- Step 4: prompt and schema

RULES = """You write the first draft of a blameless incident postmortem.
Rules:
1. Use only the timeline{facts_rule}. Don't add events, causes or numbers.
2. Describe what happened and how, not who. Name people only by role.
   A person's action is never the root cause. Don't say that anyone
   forgot, missed or failed to do something; describe the missing check.
3. Write times as HH:MM UTC, copied from the timeline.{duration_rule}
4. End the root cause and each contributing factor with the event ids that
   support it, like (E4, E9).
5. Start each action item with a verb and give an owner role, never a name."""

FACT_ORDER = ["impact_start", "impact_end", "impact_minutes", "acknowledged",
              "minutes_to_acknowledge", "mitigated", "minutes_to_mitigate",
              "resolved", "minutes_to_resolve", "last_change",
              "minutes_change_to_impact"]


def timeline_line(e):
    who = f"{e.user}: " if e.kind == "chat" and e.user else ""
    return f"{e.id} {e.hhmm} [{e.kind}] {who}{e.text}"


def build_prompt(name, facts, events, with_facts=True):
    system = RULES.format(
        facts_rule=" and the facts list" if with_facts else "",
        duration_rule=" Copy durations from the facts list." if with_facts else "")
    lines = [f"Incident {name}, {facts['date']}, all times UTC."]
    if with_facts:
        lines.append("Facts computed from the timeline:")
        lines += [f"- {k}: {facts[k]}" for k in FACT_ORDER if k in facts]
    lines.append("Timeline:")
    lines += [timeline_line(e) for e in events]
    return system, "\n".join(lines)


class ActionItem(BaseModel):
    action: str
    owner_role: str
    priority: Literal["P1", "P2", "P3"]


class Narrative(BaseModel):
    summary: str
    impact: str
    root_cause: str
    contributing_factors: list[str] = Field(max_length=4)
    action_items: list[ActionItem] = Field(max_length=5)


# ------------------------------------------------- Step 5: draft with Ollama

def draft(system, user):
    started = time.perf_counter()
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        format=Narrative.model_json_schema(),
        options={"temperature": 0, "num_predict": 800},
    )
    narrative = Narrative.model_validate_json(response.message.content)
    return narrative, round(time.perf_counter() - started, 1), response


# ------------------------------------------------- Step 6: check the values

EVENT_ID = re.compile(r"\bE(\d+)\b")
DURATION = re.compile(r"\b(?:(\d+)\s*hours?"  # 1 hour
                      r"(?:\s*(?:and\s*)?(\d+)[\s\-]*min(?:ute)?s?)?"  # and 15 minutes
                      r"|(\d+)[\s\-]*min(?:ute)?s?)\b", re.I)  # or 40 minutes
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
CLOCK = re.compile(r"\b(?:[01]\d|2[0-3]):[0-5]\d\b")
NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)?")


def duration_minutes(m):
    hours, extra, mins = m.groups()
    return int(hours) * 60 + int(extra or 0) if hours else int(mins)


def values_in(text):
    """Yields (kind, value) for every date, clock time, duration and other number."""
    found = []

    def take(pattern, kind, value):
        nonlocal text
        for m in pattern.finditer(text):
            if kind:
                found.append((kind, value(m)))
        text = pattern.sub(" ", text)  # so a number is never counted twice

    take(DATE, "date", lambda m: m.group(0))
    take(CLOCK, "time", lambda m: m.group(0))
    take(DURATION, "duration", duration_minutes)
    take(EVENT_ID, None, None)
    take(NUMBER, "number", lambda m: m.group(0))
    return found


def narrative_texts(n):
    texts = {"summary": n.summary, "impact": n.impact, "root cause": n.root_cause}
    texts.update({f"factor {i}": f for i, f in enumerate(n.contributing_factors, 1)})
    texts.update({f"action {i}": a.action for i, a in enumerate(n.action_items, 1)})
    return texts


def check_numbers(narrative, events, facts):
    durations = {v for k, v in facts.items() if k.startswith("minutes") or k == "impact_minutes"}
    allowed = {("date", facts["date"])} | {("number", str(d)) for d in durations}
    for e in events:
        allowed |= {("date", e.time.strftime("%Y-%m-%d")), ("time", e.hhmm)}
        allowed |= set(values_in(e.text))

    report = {"values": 0, "durations": [], "wrong_durations": [], "unsupported": [],
              "bad_event_ids": []}
    for field, text in narrative_texts(narrative).items():
        for kind, value in values_in(text):
            report["values"] += 1
            if kind == "duration":  # durations: computed ones only
                report["durations"].append(value)
                if value not in durations:
                    report["wrong_durations"].append(f"{field}: {value} minutes")
            elif (kind, value) not in allowed:
                report["unsupported"].append(f"{field}: {value}")
        for n in EVENT_ID.findall(text):
            if not 1 <= int(n) <= len(events):
                report["bad_event_ids"].append(f"{field}: E{n}")

    stated = [duration_minutes(m) for m in DURATION.finditer(narrative.impact)]
    report["impact_minutes"] = facts["impact_minutes"]
    report["impact_stated"] = stated
    report["impact_ok"] = facts["impact_minutes"] in stated
    return report


# ------------------------------------------------- Step 7: flag the wording

BLAME = re.compile(r"(?i)\b(forgot|forgetting|should have|careless|negligent|"
                   r"human error|fault of|blame[ds]?)\b")
ROLE_FAILED = re.compile(r"(?i)\b(engineer|commander|lead|responder|team)\s+"
                         r"(did not|didn't|failed to|forgot|missed|neglected)\b")
ACTION_VERBS = {"add", "alert", "audit", "automate", "configure", "create", "define",
                "document", "enable", "establish", "implement", "improve", "introduce",
                "monitor", "notify", "remove", "replace", "require", "review", "run",
                "schedule", "set", "test", "update", "validate", "verify", "write"}


def flag_wording(narrative, names):
    flags = []
    for field, text in narrative_texts(narrative).items():
        for name in names:
            if re.search(rf"\b{re.escape(name)}\b", text):
                flags.append(f"{field}: names a person '{name}'")
        for m in BLAME.finditer(text):
            flags.append(f"{field}: blaming word '{m.group(0)}'")
        for m in ROLE_FAILED.finditer(text):
            flags.append(f"{field}: a person as the subject of a failure '{m.group(0)}'")
    for i, item in enumerate(narrative.action_items, 1):
        first = item.action.split()[0].lower() if item.action.split() else ""
        if first not in ACTION_VERBS:
            flags.append(f"action {i}: doesn't start with a verb from the list '{first}'")
        if "," in item.owner_role or " and " in item.owner_role:
            flags.append(f"action {i}: more than one owner '{item.owner_role}'")
    return flags


def check_flags(report):
    flags = [f"{w} is not a computed duration" for w in report["wrong_durations"]]
    flags += [f"{u} is not in the timeline" for u in report["unsupported"]]
    flags += [f"{b} is not an event id" for b in report["bad_event_ids"]]
    if not report["impact_ok"]:
        flags.append(f"impact: the timeline gives {report['impact_minutes']} minutes, "
                     f"the text states {report['impact_stated'] or 'none'}")
    return flags


# ------------------------------------------------- Step 8: render the draft

def render(name, facts, events, narrative, flags):
    env = Environment(loader=FileSystemLoader(Path(__file__).parent),
                      keep_trailing_newline=True)
    template = env.get_template("postmortem.md.j2")
    return template.render(name=name, facts=facts, events=events, n=narrative,
                           flags=flags, model=MODEL)


def prepare(folder):
    """Steps 1 to 4: timeline, facts and masking. Returns (events, facts, names, masked)."""
    events = build_timeline(folder)
    facts = compute_facts(events)
    roles, names = load_people(folder)
    masked = mask(events, roles, names)
    if "last_change" in facts:  # the change text comes from the log, so mask it too
        facts["last_change"] = mask_text(facts["last_change"], roles, names)
    return events, facts, names, masked


def main():
    global MODEL
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="print the prompt, don't call the model")
    parser.add_argument("--no-facts", action="store_true", help="leave the computed facts out of the prompt")
    parser.add_argument("--model", default=MODEL)
    args = parser.parse_args()
    MODEL = args.model

    name = args.folder.name
    events, facts, names, masked = prepare(args.folder)
    system, user = build_prompt(name, facts, events, with_facts=not args.no_facts)
    if args.dry_run:
        print(user)
        print(f"{len(events)} events, {masked} masked")
        return

    narrative, seconds, _ = draft(system, user)
    report = check_numbers(narrative, events, facts)
    flags = check_flags(report) + flag_wording(narrative, names)
    out = args.folder / "postmortem-draft.md"
    out.write_text(render(name, facts, events, narrative, flags))
    print(f"{out}: {seconds} s, {report['values']} values checked, {len(flags)} review flags")


if __name__ == "__main__":
    main()
