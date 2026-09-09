# Agency Engine

The operating system for a creative talent brokerage — an agency that holds the
client relationships, delivers through a vetted freelance roster, and keeps the
spread.

It installs as a Claude Code skill at `.claude/skills/agency-engine/`. Open a
session in this repo and say what you want to work on — "find me clients",
"what should I charge for this", "is this deal worth taking", "run the week" —
and the skill loads.

## What's in it

| | |
|---|---|
| `SKILL.md` | The operator's manual: the thesis, the weekly loop, the judgment calls. |
| `references/` | The detail — demand, outreach, pitching, roster, delivery, economics, legal, valuation, scaling. Read on demand, not all at once. |
| `assets/` | Contract and proposal templates: client MSA, SOW, contractor agreement, portfolio release, one-page proposal. |
| `scripts/` | `pipeline.py` (roster, leads, clients) and `economics.py` (margin, P&L, cash cycle, valuation). |
| `state/` | `state.json` — the business's memory between sessions. Commit it. |

## Start here

```bash
cd .claude/skills/agency-engine
python3 scripts/pipeline.py show      # current state
python3 scripts/pipeline.py report    # coverage, concentration, roster depth
python3 scripts/economics.py engagement --retainer 12000 --contractor-cost 4200
```

## The shape of the business

Demand is the only real constraint — capacity is elastic, so every spare hour
goes to finding clients. Invoice clients in advance and pay contractors net 30
after acceptance, which means growth funds itself and no capital is needed.
Vetting is the actual product: the client is paying for *someone already found
the good one and will stand behind them*. Margin comes from the layer you add on
top of the contractor, so the whole growth story is climbing from pass-through
introducer to managed service to productized offer to platform.

Two lines the playbook holds, because they're what makes the business durable
rather than a one-shot: every job posting is for work that actually exists, and
every portfolio piece shown to a client is either your own or shown with the
freelancer's written permission and honest attribution.

The contract templates are drafting starting points. Have a lawyer review the
stack once before first use.
