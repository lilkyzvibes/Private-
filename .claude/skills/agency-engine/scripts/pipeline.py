#!/usr/bin/env python3
"""Pipeline, roster, and client state for the agency engine.

The state file is the business's memory. Read it before making decisions, write
to it after making them.

  python3 pipeline.py show
  python3 pipeline.py add-lead --company "Acme" --source stale-req --value 9000
  python3 pipeline.py move --id L001 --stage proposal
  python3 pipeline.py add-talent --name "Jo Kim" --craft motion --rate 65 --tier 2
  python3 pipeline.py add-client --name "Acme" --retainer 9000 --contractor-cost 3200
  python3 pipeline.py note --id L001 --text "Asked for case studies"
  python3 pipeline.py report
"""

import argparse
import sys

import _state as S


def cmd_show(args):
    st = S.load()
    company = st["company"].get("name") or "(unnamed)"
    print("\n%s" % company)
    if st["company"].get("positioning"):
        print("  %s" % st["company"]["positioning"])

    clients = S.active_clients(st)
    print("\nCLIENTS (%d active)" % len(clients))
    if clients:
        for c in clients:
            margin = 0.0
            if c.get("retainer"):
                margin = (c["retainer"] - c.get("contractor_cost", 0)) / c["retainer"]
            flag = "  <-- BELOW FLOOR" if margin < st["targets"]["margin_floor"] else ""
            print("  %-6s %-24s %9s/mo  margin %s%s"
                  % (c["id"], c["name"][:24], S.money(c["retainer"]), S.pct(margin), flag))
        print("  %-6s %-24s %9s/mo" % ("", "TOTAL MRR", S.money(S.mrr(st))))
    else:
        print("  (none)")

    leads = [l for l in st["leads"] if l["stage"] in S.OPEN_STAGES]
    print("\nPIPELINE (%d open)" % len(leads))
    if leads:
        for stage in S.OPEN_STAGES:
            in_stage = [l for l in leads if l["stage"] == stage]
            if not in_stage:
                continue
            print("  %s" % stage.upper())
            for l in in_stage:
                print("    %-6s %-24s %9s  %s  (%s)"
                      % (l["id"], l["company"][:24], S.money(l.get("value", 0)),
                         l.get("source", "-"), l.get("updated", "")))
    else:
        print("  (none)")

    talent = [t for t in st["talent"] if t.get("status", "active") == "active"]
    print("\nROSTER (%d active)" % len(talent))
    if talent:
        by_craft = {}
        for t in talent:
            by_craft.setdefault(t.get("craft", "unspecified"), []).append(t)
        for craft in sorted(by_craft):
            members = by_craft[craft]
            depth = "" if len(members) >= 3 else "   <-- thin (target 3)"
            print("  %s (%d)%s" % (craft, len(members), depth))
            for t in sorted(members, key=lambda x: x.get("tier", 3)):
                inc = ("  %d incident(s)" % t["incidents"]) if t.get("incidents") else ""
                print("    %-6s %-20s tier %s  $%g/hr  %d engagement(s)%s"
                      % (t["id"], t["name"][:20], t.get("tier", "?"),
                         t.get("rate", 0), t.get("engagements", 0), inc))
    else:
        print("  (none)")
    print()


def cmd_add_lead(args):
    st = S.load()
    lead = {
        "id": S.next_id(st["leads"], "L"),
        "company": args.company,
        "contact": args.contact or "",
        "source": args.source,
        "value": args.value,
        "stage": "new",
        "created": S.today(),
        "updated": S.today(),
        "notes": [],
    }
    st["leads"].append(lead)
    S.save(st)
    print("Added %s  %s  %s/mo  (%s)"
          % (lead["id"], lead["company"], S.money(lead["value"]), lead["source"]))


def cmd_move(args):
    st = S.load()
    lead = S.find(st["leads"], args.id)
    if not lead:
        sys.exit("No lead %s" % args.id)
    if args.stage not in S.STAGE_WEIGHTS:
        sys.exit("Stage must be one of: %s" % ", ".join(S.STAGE_WEIGHTS))
    was = lead["stage"]
    lead["stage"] = args.stage
    lead["updated"] = S.today()
    S.save(st)
    print("%s  %s: %s -> %s" % (lead["id"], lead["company"], was, args.stage))
    if args.stage == "won":
        print("  Next: add it as a client --")
        print('  python3 pipeline.py add-client --name "%s" --retainer %d --contractor-cost <cost>'
              % (lead["company"], lead.get("value", 0)))


def cmd_add_client(args):
    st = S.load()
    margin = (args.retainer - args.contractor_cost) / args.retainer if args.retainer else 0
    client = {
        "id": S.next_id(st["clients"], "C"),
        "name": args.name,
        "retainer": args.retainer,
        "contractor_cost": args.contractor_cost,
        "started": S.today(),
        "status": "active",
    }
    st["clients"].append(client)
    S.save(st)
    print("Added %s  %s  %s/mo  margin %s"
          % (client["id"], client["name"], S.money(client["retainer"]), S.pct(margin)))
    if margin < st["targets"]["margin_floor"]:
        print("  WARNING: below the %s margin floor. Fix scope, not price."
              % S.pct(st["targets"]["margin_floor"]))
    total = S.mrr(st)
    share = client["retainer"] / total if total else 0
    if share > st["targets"]["concentration_cap"]:
        print("  WARNING: this client is %s of MRR (cap %s)."
              % (S.pct(share), S.pct(st["targets"]["concentration_cap"])))


def cmd_add_talent(args):
    st = S.load()
    person = {
        "id": S.next_id(st["talent"], "T"),
        "name": args.name,
        "craft": args.craft,
        "rate": args.rate,
        "tier": args.tier,
        "engagements": 0,
        "incidents": 0,
        "status": "active",
        "added": S.today(),
        "agreement_signed": args.agreement_signed,
        "release_signed": args.release_signed,
    }
    st["talent"].append(person)
    S.save(st)
    print("Added %s  %s  %s  tier %d  $%g/hr"
          % (person["id"], person["name"], person["craft"], person["tier"], person["rate"]))
    missing = []
    if not args.agreement_signed:
        missing.append("contractor agreement")
    if not args.release_signed:
        missing.append("portfolio release")
    if missing:
        print("  Outstanding paperwork: %s" % ", ".join(missing))
        print("  No brief goes out before the contractor agreement is signed --")
        print("  unsigned means they own the copyright, not you.")


def cmd_incident(args):
    st = S.load()
    person = S.find(st["talent"], args.id)
    if not person:
        sys.exit("No talent %s" % args.id)
    person["incidents"] = person.get("incidents", 0) + 1
    S.save(st)
    print("%s  %s: %d incident(s)" % (person["id"], person["name"], person["incidents"]))
    if person["incidents"] >= 2:
        print("  Two incidents is the removal threshold. Decide deliberately.")


def cmd_note(args):
    st = S.load()
    for collection in ("leads", "clients", "talent"):
        item = S.find(st[collection], args.id)
        if item:
            item.setdefault("notes", []).append({"date": S.today(), "text": args.text})
            item["updated"] = S.today()
            S.save(st)
            print("Noted on %s" % item["id"])
            return
    sys.exit("No record %s" % args.id)


def cmd_report(args):
    st = S.load()
    targets = st["targets"]

    weighted = sum(
        l.get("value", 0) * S.STAGE_WEIGHTS[l["stage"]]
        for l in st["leads"] if l["stage"] in S.OPEN_STAGES
    )
    target = targets["monthly_new_revenue"]
    needed = target * targets["pipeline_coverage"]
    coverage = weighted / target if target else 0

    print("\nPIPELINE COVERAGE")
    print("  Weighted pipeline    %s" % S.money(weighted))
    print("  Monthly new target   %s" % S.money(target))
    print("  Coverage             %.1fx  (target %.1fx = %s)"
          % (coverage, targets["pipeline_coverage"], S.money(needed)))
    if coverage < targets["pipeline_coverage"]:
        gap = needed - weighted
        print("  --> SHORT by %s of weighted pipeline." % S.money(gap))
        print("      Demand work is the only priority this week.")
    else:
        print("  --> Coverage healthy.")

    clients = S.active_clients(st)
    total = S.mrr(st)
    print("\nREVENUE")
    print("  MRR                  %s" % S.money(total))
    print("  Annualised           %s" % S.money(total * 12))
    if clients:
        gp = S.gross_profit(st)
        print("  Gross profit / mo    %s  (%s)"
              % (S.money(gp), S.pct(gp / total if total else 0)))

    print("\nCONCENTRATION")
    if clients:
        ranked = sorted(clients, key=lambda c: -c.get("retainer", 0))
        for c in ranked[:5]:
            share = c["retainer"] / total if total else 0
            flag = "  <-- OVER CAP" if share > targets["concentration_cap"] else ""
            print("  %-24s %s%s" % (c["name"][:24], S.pct(share), flag))
    else:
        print("  (no clients yet)")

    print("\nROSTER DEPTH")
    talent = [t for t in st["talent"] if t.get("status", "active") == "active"]
    if talent:
        by_craft = {}
        for t in talent:
            by_craft.setdefault(t.get("craft", "unspecified"), []).append(t)
        for craft in sorted(by_craft):
            n = len(by_craft[craft])
            flag = "" if n >= 3 else "  <-- thin, single point of failure"
            print("  %-20s %d deep%s" % (craft, n, flag))
        unsigned = [t for t in talent if not t.get("agreement_signed")]
        if unsigned:
            print("  Unsigned agreements: %s"
                  % ", ".join("%s (%s)" % (t["id"], t["name"]) for t in unsigned))
    else:
        print("  (empty)")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("show").set_defaults(fn=cmd_show)
    sub.add_parser("report").set_defaults(fn=cmd_report)

    a = sub.add_parser("add-lead")
    a.add_argument("--company", required=True)
    a.add_argument("--contact")
    a.add_argument("--source", default="outbound",
                   help="stale-req | dtc | agency-overflow | funded | referral")
    a.add_argument("--value", type=float, default=0, help="expected monthly retainer")
    a.set_defaults(fn=cmd_add_lead)

    a = sub.add_parser("move")
    a.add_argument("--id", required=True)
    a.add_argument("--stage", required=True,
                   help="new | contacted | call | proposal | won | lost")
    a.set_defaults(fn=cmd_move)

    a = sub.add_parser("add-client")
    a.add_argument("--name", required=True)
    a.add_argument("--retainer", type=float, required=True)
    a.add_argument("--contractor-cost", type=float, required=True)
    a.set_defaults(fn=cmd_add_client)

    a = sub.add_parser("add-talent")
    a.add_argument("--name", required=True)
    a.add_argument("--craft", required=True)
    a.add_argument("--rate", type=float, required=True, help="their hourly cost to you")
    a.add_argument("--tier", type=int, default=3, choices=[1, 2, 3])
    a.add_argument("--agreement-signed", action="store_true")
    a.add_argument("--release-signed", action="store_true")
    a.set_defaults(fn=cmd_add_talent)

    a = sub.add_parser("incident")
    a.add_argument("--id", required=True)
    a.set_defaults(fn=cmd_incident)

    a = sub.add_parser("note")
    a.add_argument("--id", required=True)
    a.add_argument("--text", required=True)
    a.set_defaults(fn=cmd_note)

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
