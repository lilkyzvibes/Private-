"""Shared state access for the agency engine.

State lives in ../state/state.json as plain JSON so it stays readable, diffable,
and editable by hand. The business's memory is these files -- a session that
changes something and doesn't write here has done nothing durable.
"""

import json
import os
from datetime import date

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(SKILL_ROOT, "state")
STATE_PATH = os.path.join(STATE_DIR, "state.json")

# Probability of closing, by pipeline stage. Used for weighted coverage.
STAGE_WEIGHTS = {
    "new": 0.05,
    "contacted": 0.10,
    "call": 0.30,
    "proposal": 0.50,
    "won": 1.00,
    "lost": 0.00,
}
OPEN_STAGES = ["new", "contacted", "call", "proposal"]

DEFAULT_STATE = {
    "company": {
        "name": "",
        "crafts": [],
        "positioning": "",
    },
    "targets": {
        "monthly_new_revenue": 10000,
        "margin_floor": 0.50,
        "concentration_cap": 0.20,
        "pipeline_coverage": 3.0,
    },
    "overhead_monthly": 500,
    "leads": [],
    "clients": [],
    "talent": [],
}


def load():
    if not os.path.exists(STATE_PATH):
        return json.loads(json.dumps(DEFAULT_STATE))
    with open(STATE_PATH) as f:
        state = json.load(f)
    # Tolerate older/partial files rather than crashing mid-workflow.
    for key, value in DEFAULT_STATE.items():
        state.setdefault(key, json.loads(json.dumps(value)))
    for key, value in DEFAULT_STATE["targets"].items():
        state["targets"].setdefault(key, value)
    return state


def save(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, sort_keys=False)
        f.write("\n")


def next_id(items, prefix):
    highest = 0
    for item in items:
        raw = str(item.get("id", ""))
        if raw.startswith(prefix) and raw[len(prefix):].isdigit():
            highest = max(highest, int(raw[len(prefix):]))
    return "%s%03d" % (prefix, highest + 1)


def find(items, item_id):
    wanted = item_id.upper()
    for item in items:
        if str(item.get("id", "")).upper() == wanted:
            return item
    return None


def today():
    return date.today().isoformat()


def money(amount):
    return "${:,.0f}".format(amount)


def pct(fraction):
    return "{:.0f}%".format(fraction * 100)


def active_clients(state):
    return [c for c in state["clients"] if c.get("status", "active") == "active"]


def mrr(state):
    return sum(c.get("retainer", 0) for c in active_clients(state))


def gross_profit(state):
    return sum(
        c.get("retainer", 0) - c.get("contractor_cost", 0) for c in active_clients(state)
    )
