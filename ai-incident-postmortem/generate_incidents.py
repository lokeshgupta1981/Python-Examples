"""Writes the four sample incidents used in the article into ./incidents.

Each incident folder gets a Slack export (users.json plus one JSON file per
channel and day), alerts.json, deploys.log and roles.json. The file
incidents/labels.json holds the planted root cause and the keyword lists that
evaluate.py uses for its keyword rubric.
"""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent / "incidents"

USERS = {
    "U01": ("dana", "Dana Whitfield"),
    "U02": ("marco", "Marco Rossi"),
    "U03": ("priya", "Priya Natarajan"),
    "U04": ("sam", "Sam Okafor"),
    "U05": ("lena", "Lena Brandt"),
}

ROLES = {
    "U01": "incident commander",
    "U02": "backend engineer",
    "U03": "on-call engineer",
    "U04": "support lead",
    "U05": "search engineer",
}

# Each row: (UTC time, kind, payload)
#   chat:   payload = (user id, text)
#   bot:    payload = text posted by the incident bot
#   join:   payload = user id (a channel_join message, dropped later)
#   alert:  payload = (alert name, event, detail)
#   deploy: payload = the rest of the deploy.log line
INCIDENTS = {
    "checkout-outage": [
        ("2026-10-14T13:48:12", "deploy", "deploy service=search-api version=2.31.0 by=deploy-bot"),
        ("2026-10-14T14:02:37", "deploy", "config service=checkout-api change=db.pool.max_size 50->5 by=U02"),
        ("2026-10-14T14:06:40", "alert", ("CheckoutErrorRateHigh", "triggered", "checkout 5xx rate 38% (threshold 5%)")),
        ("2026-10-14T14:07:15", "alert", ("CheckoutLatencyHigh", "triggered", "checkout p99 latency 12.4s (threshold 2s)")),
        ("2026-10-14T14:09:02", "alert", ("CheckoutErrorRateHigh", "acknowledged", "acknowledged in the pager app")),
        ("2026-10-14T14:10:05", "bot", "Incident declared: SEV-1 checkout errors"),
        ("2026-10-14T14:10:20", "join", "U04"),
        ("2026-10-14T14:10:40", "chat", ("U01", "I'm IC. Checkout 5xx at 38%, opening a bridge")),
        ("2026-10-14T14:11:30", "chat", ("U04", "support has 30 tickets about failed payments so far")),
        ("2026-10-14T14:11:45", "chat", ("U03", ":eyes:")),
        ("2026-10-14T14:12:10", "chat", ("U03", "checkout-api logs are full of 'timeout waiting for connection from pool'")),
        ("2026-10-14T14:13:00", "chat", ("U03", "the database itself looks healthy, CPU at 22%")),
        ("2026-10-14T14:15:10", "chat", ("U01", "search-api deployed at 13:48, could that be it? search team, please check")),
        ("2026-10-14T14:15:30", "join", "U05"),
        ("2026-10-14T14:21:30", "deploy", "rollback service=search-api version=2.30.4 by=U05"),
        ("2026-10-14T14:23:00", "chat", ("U01", "+1")),
        ("2026-10-14T14:26:05", "chat", ("U03", "found it: db.pool.max_size went from 50 to 5 in the 14:02 config change")),
        ("2026-10-14T14:27:20", "chat", ("U01", "Marco forgot to check the prod value, classic")),
        ("2026-10-14T14:28:00", "chat", ("U02", "reverting the pool size now")),
        ("2026-10-14T14:29:10", "chat", ("U02", "old config for reference: db_password=Ch3ckout!2024 pool=50")),
        ("2026-10-14T14:31:40", "deploy", "config service=checkout-api change=db.pool.max_size 5->50 by=U02"),
        ("2026-10-14T14:33:00", "bot", "Status changed to Mitigated"),
        ("2026-10-14T14:35:50", "chat", ("U03", "5xx down to 2%, latency recovering")),
        ("2026-10-14T14:41:12", "alert", ("CheckoutLatencyHigh", "resolved", "checkout p99 latency 0.8s")),
        ("2026-10-14T14:46:03", "alert", ("CheckoutErrorRateHigh", "resolved", "checkout 5xx rate 0.4%")),
        ("2026-10-14T14:50:30", "chat", ("U04", "ticket volume is back to normal")),
        ("2026-10-14T15:05:00", "chat", ("U01", "closing the incident, the backend team owns the postmortem")),
        ("2026-10-14T15:05:20", "bot", "Status changed to Resolved"),
    ],
    "cert-expiry": [
        ("2026-09-22T09:40:11", "deploy", "deploy service=web-ui version=4.8.2 by=deploy-bot"),
        ("2026-09-22T10:03:25", "alert", ("ApiTlsHandshakeErrors", "triggered", "TLS handshake failures 64% on api.orderdesk.example (threshold 2%)")),
        ("2026-09-22T10:07:10", "alert", ("ApiTlsHandshakeErrors", "acknowledged", "acknowledged in the pager app")),
        ("2026-09-22T10:08:00", "bot", "Incident declared: SEV-1 API TLS errors"),
        ("2026-09-22T10:09:30", "chat", ("U03", "browsers say the certificate for api.orderdesk.example has expired")),
        ("2026-09-22T10:11:00", "chat", ("U01", ":fire: :eyes:")),
        ("2026-09-22T10:12:40", "chat", ("U03", "NotAfter was 2026-09-22 10:00 UTC")),
        ("2026-09-22T10:14:20", "chat", ("U01", "is the web-ui deploy from 09:40 related?")),
        ("2026-09-22T10:15:05", "chat", ("U03", "no, web-ui only serves static files, it never touches the API cert")),
        ("2026-09-22T10:17:30", "chat", ("U02", "the cert-renewer job has failed every night since 2026-09-08 with a rate limit error from the CA")),
        ("2026-09-22T10:18:10", "chat", ("U02", "its failures only go to a log file, nothing alerts on them")),
        ("2026-09-22T10:24:45", "deploy", "manual service=api-gateway change=install renewed certificate by=U03"),
        ("2026-09-22T10:29:00", "bot", "Status changed to Mitigated"),
        ("2026-09-22T10:30:02", "alert", ("ApiTlsHandshakeErrors", "resolved", "TLS handshake failures 0%")),
        ("2026-09-22T10:44:00", "chat", ("U01", "Priya, please add an alert on the renewal job")),
        ("2026-09-22T10:50:30", "bot", "Status changed to Resolved"),
    ],
    "shipping-provider": [
        ("2026-10-03T15:52:30", "deploy", "deploy service=checkout-api version=7.12.0 by=deploy-bot"),
        ("2026-10-03T16:10:20", "alert", ("CheckoutLatencyHigh", "triggered", "checkout p99 latency 31.2s (threshold 2s)")),
        ("2026-10-03T16:13:05", "alert", ("CheckoutLatencyHigh", "acknowledged", "acknowledged in the pager app")),
        ("2026-10-03T16:13:40", "bot", "Incident declared: SEV-2 slow checkout"),
        ("2026-10-03T16:15:00", "chat", ("U03", "traces show checkout waiting on the ShipFast /rates call, 30 s timeouts")),
        ("2026-10-03T16:17:20", "chat", ("U01", "did the 15:52 checkout-api deploy change anything there?")),
        ("2026-10-03T16:19:10", "chat", ("U02", "no, 7.12.0 only changed the coupon code path")),
        ("2026-10-03T16:22:40", "chat", ("U03", "the ShipFast status page says degraded performance on the rates API")),
        ("2026-10-03T16:24:00", "chat", ("U01", "+1")),
        ("2026-10-03T16:26:30", "chat", ("U01", "let's turn on the flat-rate shipping fallback")),
        ("2026-10-03T16:31:15", "deploy", "config service=checkout-api change=shipping.fallback flat_rate=on by=U02"),
        ("2026-10-03T16:33:00", "bot", "Status changed to Mitigated"),
        ("2026-10-03T16:35:40", "alert", ("CheckoutLatencyHigh", "resolved", "checkout p99 latency 0.9s")),
        ("2026-10-03T17:20:10", "chat", ("U03", "ShipFast reports full recovery, turning the fallback off")),
        ("2026-10-03T17:22:30", "deploy", "config service=checkout-api change=shipping.fallback flat_rate=off by=U02"),
        ("2026-10-03T17:25:00", "bot", "Status changed to Resolved"),
    ],
    "disk-full": [
        ("2026-10-08T22:15:00", "deploy", "migration service=orders-db host=db-02->db-07 by=U02"),
        ("2026-10-09T03:12:30", "alert", ("OrdersDbDiskFull", "triggered", "orders-db disk 97% used (threshold 90%)")),
        ("2026-10-09T03:16:20", "alert", ("OrdersDbDiskFull", "acknowledged", "acknowledged in the pager app")),
        ("2026-10-09T03:17:00", "bot", "Incident declared: SEV-2 orders-db disk full"),
        ("2026-10-09T03:19:30", "chat", ("U03", "order writes are failing, the database cannot extend its files")),
        ("2026-10-09T03:22:10", "chat", ("U03", "the database log folder on db-07 holds 180 GB")),
        ("2026-10-09T03:24:40", "chat", ("U02", "db-02 had a log rotation job, the migration playbook did not copy it to db-07")),
        ("2026-10-09T03:25:00", "join", "U01"),
        ("2026-10-09T03:30:15", "deploy", "manual service=orders-db change=delete logs older than 2 days by=U03"),
        ("2026-10-09T03:34:00", "bot", "Status changed to Mitigated"),
        ("2026-10-09T03:38:45", "alert", ("OrdersDbDiskFull", "resolved", "orders-db disk 41% used")),
        ("2026-10-09T03:52:00", "deploy", "config service=orders-db change=enable log rotation by=U02"),
        ("2026-10-09T03:56:10", "bot", "Status changed to Resolved"),
    ],
}

LABELS = {
    "checkout-outage": {
        "root_cause": "A config change lowered the connection pool from 50 to 5",
        "keywords": [["pool"], ["config", "configuration"]],
    },
    "cert-expiry": {
        "root_cause": "A TLS certificate expired because its renewal job kept failing",
        "keywords": [["certificate", "cert"], ["expire", "expired"], ["renewal", "renew"]],
    },
    "shipping-provider": {
        "root_cause": "The external shipping-rates provider ShipFast had an outage",
        "keywords": [["shipfast", "provider"], ["outage", "degraded"]],
    },
    "disk-full": {
        "root_cause": "Database logs filled the disk after a host migration",
        "keywords": [["log", "logs"], ["disk"], ["migration", "migrated"]],
    },
}


def epoch(iso):
    return datetime.fromisoformat(iso).replace(tzinfo=timezone.utc).timestamp()


def write_incident(name, rows):
    folder = ROOT / name
    channel = folder / "slack" / f"inc-{name}"
    channel.mkdir(parents=True)
    users = [{"id": uid, "name": n, "real_name": real} for uid, (n, real) in USERS.items()]
    (folder / "slack" / "users.json").write_text(json.dumps(users, indent=2))
    (folder / "roles.json").write_text(json.dumps(ROLES, indent=2))

    days, alerts, deploys = {}, [], []
    for n, (iso, kind, payload) in enumerate(rows):
        if kind in ("chat", "bot", "join"):
            ts = f"{int(epoch(iso))}.{(n + 1) * 100:06d}"
            if kind == "chat":
                msg = {"type": "message", "user": payload[0], "text": payload[1], "ts": ts}
            elif kind == "bot":
                msg = {"type": "message", "subtype": "bot_message", "username": "incident-bot",
                       "text": payload, "ts": ts}
            else:
                msg = {"type": "message", "subtype": "channel_join", "user": payload,
                       "text": f"<@{payload}> has joined the channel", "ts": ts}
            days.setdefault(iso[:10], []).append(msg)
        elif kind == "alert":
            alert, event, detail = payload
            alerts.append({"at": iso + "Z", "alert": alert, "event": event, "detail": detail})
        elif kind == "deploy":
            deploys.append(f"{iso}Z {payload}")

    for day, messages in days.items():
        (channel / f"{day}.json").write_text(json.dumps(messages, indent=2))
    (folder / "alerts.json").write_text(json.dumps(alerts, indent=2))
    (folder / "deploys.log").write_text("\n".join(deploys) + "\n")


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    for name, rows in INCIDENTS.items():
        write_incident(name, rows)
    (ROOT / "labels.json").write_text(json.dumps(LABELS, indent=2))
    print(f"wrote {len(INCIDENTS)} incidents to {ROOT}")


if __name__ == "__main__":
    main()
