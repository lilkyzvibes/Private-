#!/usr/bin/env python3
"""Money for the agency engine: engagement margin, P&L, cash cycle, valuation.

Run these rather than doing the arithmetic in your head -- the numbers drive
real decisions (take the deal / don't, hire / don't) and a slip compounds.

  python3 economics.py engagement --retainer 12000 --contractor-cost 4200
  python3 economics.py pnl
  python3 economics.py cash --retainer 12000 --contractor-cost 4200
  python3 economics.py valuation
"""

import argparse

import _state as S


def cmd_engagement(args):
    oversight = args.hours_oversight * args.oversight_rate
    gross = args.retainer - args.contractor_cost - oversight
    margin = gross / args.retainer if args.retainer else 0
    multiple = args.retainer / args.contractor_cost if args.contractor_cost else 0

    st = S.load()
    floor = st["targets"]["margin_floor"]

    print("\nENGAGEMENT")
    print("  Client retainer          %10s / mo" % S.money(args.retainer))
    print("  Contractor cost          %10s      (%s of retainer)"
          % ("-" + S.money(args.contractor_cost),
             S.pct(args.contractor_cost / args.retainer if args.retainer else 0)))
    print("  Oversight (%.0fh @ $%.0f)     %10s"
          % (args.hours_oversight, args.oversight_rate, "-" + S.money(oversight)))
    print("  " + "-" * 42)
    print("  Gross profit             %10s / mo" % S.money(gross))
    print("  Gross margin             %10s" % S.pct(margin))
    print("  Billing multiple         %10.1fx on contractor cost" % multiple)
    print("  Annualised gross profit  %10s" % S.money(gross * 12))

    print("\n  VERDICT")
    if margin >= 0.60:
        print("  Healthy. At or above the 60% target.")
    elif margin >= floor:
        print("  Acceptable but thin (floor is %s). One redo erodes this."
              % S.pct(floor))
        print("  Consider trimming a deliverable or moving to a cheaper tier.")
    else:
        print("  BELOW THE %s FLOOR. Do not discount further." % S.pct(floor))
        print("  Fix the scope instead: cut deliverables until the margin works,")
        print("  then show the client the smaller scope at the price they can pay.")
    if multiple and multiple < 2.5:
        print("  Billing multiple under 2.5x -- no room to absorb a redo.")
    print()


def cmd_pnl(args):
    st = S.load()
    clients = S.active_clients(st)
    if not clients:
        print("\nNo active clients in state. Add them with:")
        print('  python3 pipeline.py add-client --name "X" --retainer 9000 --contractor-cost 3200\n')
        return

    revenue = S.mrr(st)
    cost = sum(c.get("contractor_cost", 0) for c in clients)
    gross = revenue - cost
    overhead = st.get("overhead_monthly", 0)
    ebitda = gross - overhead

    print("\nMONTHLY P&L  (%d active clients)" % len(clients))
    print("  Revenue                  %10s" % S.money(revenue))
    print("  Cost of delivery         %10s" % ("-" + S.money(cost)))
    print("  " + "-" * 42)
    print("  Gross profit             %10s   %s"
          % (S.money(gross), S.pct(gross / revenue if revenue else 0)))
    print("  Overhead                 %10s" % ("-" + S.money(overhead)))
    print("  " + "-" * 42)
    print("  EBITDA                   %10s   %s"
          % (S.money(ebitda), S.pct(ebitda / revenue if revenue else 0)))
    print("\n  Annualised revenue       %10s" % S.money(revenue * 12))
    print("  Annualised EBITDA        %10s" % S.money(ebitda * 12))

    print("\nBY CLIENT")
    for c in sorted(clients, key=lambda x: -x.get("retainer", 0)):
        m = (c["retainer"] - c.get("contractor_cost", 0)) / c["retainer"] if c["retainer"] else 0
        share = c["retainer"] / revenue if revenue else 0
        flags = []
        if m < st["targets"]["margin_floor"]:
            flags.append("below margin floor")
        if share > st["targets"]["concentration_cap"]:
            flags.append("over concentration cap")
        note = ("   <-- " + "; ".join(flags)) if flags else ""
        print("  %-24s %9s  margin %4s  share %4s%s"
              % (c["name"][:24], S.money(c["retainer"]), S.pct(m), S.pct(share), note))

    blended = gross / revenue if revenue else 0
    if blended < 0.55:
        print("\n  Blended margin is %s, under the 55%% target." % S.pct(blended))
        print("  Margin drifts one unpriced favour at a time -- check scope creep first.")
    print()


def cmd_cash(args):
    """Show why this business funds itself, and where that breaks."""
    client_day = args.client_terms
    contractor_day = 30 + args.contractor_terms  # delivery lands ~day 30
    float_days = contractor_day - client_day
    held = args.retainer

    print("\nCASH CYCLE  (one engagement, one month)")
    print("  Day   1   Invoice client, net %d" % args.client_terms)
    print("  Day %3d   Client pays                    %10s"
          % (client_day, "+" + S.money(held)))
    print("  Day  30   Work delivered and accepted")
    print("  Day %3d   Contractor paid, net %d         %10s"
          % (contractor_day, args.contractor_terms,
             "-" + S.money(args.contractor_cost)))
    print("\n  You hold the client's cash for %d days before the contractor's bill lands."
          % float_days)
    print("  Float per engagement     %10s" % S.money(args.contractor_cost))
    print("  Negative working capital -- every new client funds the next one.")

    st = S.load()
    n = len(S.active_clients(st))
    if n:
        total_float = sum(c.get("contractor_cost", 0) for c in S.active_clients(st))
        print("\n  Across %d live clients, float in hand is roughly %s at any time."
              % (n, S.money(total_float)))

    print("\n  This breaks in exactly one way: paying a contractor before the client")
    print("  has paid you. That turns you into a lender with no balance sheet.")
    print("  Invoice in advance, chase at day %d, pay net %d after acceptance.\n"
          % (args.client_terms + 1, args.contractor_terms))


def cmd_valuation(args):
    st = S.load()
    clients = S.active_clients(st)
    revenue = S.mrr(st) * 12
    if not revenue:
        print("\nNo revenue in state yet -- nothing to value.\n")
        return
    gross = S.gross_profit(st) * 12
    ebitda = gross - st.get("overhead_monthly", 0) * 12
    margin = gross / revenue

    total_mrr = S.mrr(st)
    top_share = max(c.get("retainer", 0) for c in clients) / total_mrr if total_mrr else 1.0

    print("\nVALUATION SNAPSHOT")
    print("  Annual revenue           %10s" % S.money(revenue))
    print("  Gross margin             %10s" % S.pct(margin))
    print("  EBITDA (est.)            %10s" % S.money(ebitda))

    # Score the five drivers. Each is worth roughly a point of multiple.
    drivers = []
    drivers.append((
        "Client concentration",
        top_share <= st["targets"]["concentration_cap"],
        "largest client is %s of revenue (cap %s)"
        % (S.pct(top_share), S.pct(st["targets"]["concentration_cap"])),
    ))
    drivers.append((
        "Gross margin >= 55%",
        margin >= 0.55,
        "currently %s" % S.pct(margin),
    ))
    drivers.append((
        "Client count >= 8",
        len(clients) >= 8,
        "%d active clients" % len(clients),
    ))
    drivers.append((
        "Recurring revenue",
        all(c.get("retainer", 0) > 0 for c in clients),
        "all revenue on monthly retainers",
    ))
    drivers.append((
        "Owner out of delivery",
        bool(st["company"].get("owner_out_of_delivery")),
        'set company.owner_out_of_delivery in state when true',
    ))

    print("\nDRIVERS")
    met = 0
    for name, ok, detail in drivers:
        print("  [%s] %-26s %s" % ("x" if ok else " ", name, detail))
        met += 1 if ok else 0

    low = 2.0 + met * 0.7
    high = 3.0 + met * 1.0
    print("\n  Drivers met: %d of 5" % met)
    print("  Indicative multiple      %.1f - %.1fx EBITDA" % (low, high))
    print("  Indicative value         %s - %s"
          % (S.money(ebitda * low), S.money(ebitda * high)))
    print("\n  This is a rough directional estimate, not an appraisal. The point is")
    print("  the gap: closing the unmet drivers is worth more than a year of growth.")
    print("  See references/valuation.md.\n")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    a = sub.add_parser("engagement", help="margin on a single engagement")
    a.add_argument("--retainer", type=float, required=True)
    a.add_argument("--contractor-cost", type=float, required=True)
    a.add_argument("--hours-oversight", type=float, default=8)
    a.add_argument("--oversight-rate", type=float, default=75)
    a.set_defaults(fn=cmd_engagement)

    a = sub.add_parser("pnl", help="monthly P&L across live clients")
    a.set_defaults(fn=cmd_pnl)

    a = sub.add_parser("cash", help="cash cycle for one engagement")
    a.add_argument("--retainer", type=float, required=True)
    a.add_argument("--contractor-cost", type=float, required=True)
    a.add_argument("--client-terms", type=int, default=15)
    a.add_argument("--contractor-terms", type=int, default=30)
    a.set_defaults(fn=cmd_cash)

    a = sub.add_parser("valuation", help="multiple ladder against current state")
    a.set_defaults(fn=cmd_valuation)

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return
    args.fn(args)


if __name__ == "__main__":
    # Don't traceback when output is piped into head/less.
    try:
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (ImportError, AttributeError, ValueError):
        pass
    main()
