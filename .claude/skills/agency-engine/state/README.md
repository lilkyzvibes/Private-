# State

`state.json` is the business's memory. It survives between sessions; the
conversation doesn't.

Read it before making decisions (`python3 ../scripts/pipeline.py show`) and write
to it after making them. Anything decided in a session and not written here is
lost, and the next session will make confident decisions on stale numbers.

It's plain JSON on purpose — readable, diffable, and safe to edit by hand.

| Key | Holds |
|---|---|
| `company` | Name, crafts sold, positioning. Set `owner_out_of_delivery` to `true` once true — it's a valuation driver. |
| `targets` | The thresholds the scripts check against: new-revenue goal, 50% margin floor, 20% concentration cap, 3× pipeline coverage. |
| `overhead_monthly` | Fixed costs. Keep it near zero for as long as possible. |
| `leads` | Pipeline. Stages: `new` → `contacted` → `call` → `proposal` → `won` / `lost`. |
| `clients` | Live engagements with retainer and contractor cost — the inputs to every margin number. |
| `talent` | The roster: craft, cost rate, tier, engagement and incident counts, paperwork status. |

Commit it. The history of this file is the history of the company.
