# Economics

Use `scripts/economics.py` for the arithmetic. This file explains what the
numbers mean and which ones actually change decisions.

## Unit economics of one engagement

A Core-band retainer, worked through:

```
Client retainer                      $12,000 / mo
Contractor cost (35%)                 -$4,200
Your oversight (8 hrs @ $75 notional)   -$600
─────────────────────────────────────────────
Gross profit                           $7,200
Gross margin                              60%
```

Sixty percent is the target and 50% is the floor. Three things push it down and
each has a specific fix:

- **Redos** — caused by bad briefs. Fix the brief template, not the contractor.
- **Scope creep** — caused by silence. Price the addition the day it's asked.
- **Oversight bloat** — caused by a Tier 3 contractor on a job needing Tier 1.
  Match the tier to the risk; the cheaper contractor is more expensive.

## The cash cycle (the reason this needs no capital)

```
Day 1   Invoice client for month 1, net 15
Day 15  Client pays                        +$12,000
Day 30  Work delivered and accepted
Day 60  Contractor paid, net 30              -$4,200
```

You hold the client's cash for 45 days before the contractor's bill lands. That
is negative working capital: **every new client funds the next one.** It is the
whole reason a brokerage can grow without raising money, and it's fragile in one
specific way — pay a contractor before the client pays you and you've become a
lender financing someone else's business with money you don't have.

Two disciplines protect it:

- **Invoice in advance.** Monthly, on the 1st, for the month ahead. Not in
  arrears. This is a contract term, not a preference, and it is the single most
  important line in the MSA.
- **Chase at day 16.** Politely and automatically. A client who is 40 days late
  is not a cash-flow problem, they're a churn signal — start the conversation
  early.

## The metrics that change decisions

Most agency dashboards are decoration. These five actually alter what you do:

| Metric | Target | What it tells you |
|---|---|---|
| **Pipeline coverage** | ≥3× monthly new-revenue target | The only leading indicator. Below 3×, drop everything else. |
| **Gross margin** | ≥55% blended, 50% floor per engagement | Whether you're a business or a payroll service. |
| **Client concentration** | no client >20% of revenue | Your fragility, and later your exit multiple. |
| **Net revenue retention** | >100% | Whether existing clients grow. Above 100% you grow without selling. |
| **Owner hours in delivery** | trending to zero | Whether you own a company or a job. |

Check coverage weekly, the rest monthly. `pipeline.py report` and
`economics.py pnl` produce them from live state.

## Overhead

Keep it near zero for as long as possible. The structural beauty of this model is
that cost of delivery is 100% variable — you have no bench sitting idle — so the
only way to break it is by adding fixed cost early.

Real overhead in year one is a few hundred a month: email, a CRM if you outgrow
the state files, contract e-signing, accounting. No office. No full-time hires
until the case for one survives the test in `scaling.md`.

The first fixed cost worth taking on is almost always a **project manager**,
because it buys back the owner's delivery hours, which is the constraint on both
growth and eventual valuation.

## Worked example: the path to $1M

Twelve clients at an average $8k/month is $960k/year at 60% margin — $576k gross
profit, most of which is owner earnings if overhead stays thin.

Twelve clients is not a lot of clients. At a 25% close rate on booked calls it's
roughly 48 booked calls, which at a 2% reply-to-call rate is about 2,400 targeted
contacts — over a year, ten a day. That's the whole plan, and the fact that it's
unglamorous is why most people don't do it.

The trap at this level is that twelve clients is also the point where the owner
is at capacity on delivery oversight while still being the only salesperson. See
`scaling.md` — that's a stage gate, not a plateau to push through by working more.
