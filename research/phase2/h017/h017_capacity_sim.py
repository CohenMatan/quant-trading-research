"""H017 proposal support (P2-CP13): event frequency, slot occupancy, turnover and mechanical trading costs of an
asynchronous earnings-event book. Uses ONLY event timing metadata (Event Data v1 rules, SEC 8-K Item 2.02 events
mapped to the E981-01 eligible universe) and the frozen cost model. NO prices, NO returns, NO reactions are computed.

Mechanics simulated (the proposed H017 rules, with the reaction-based selection replaced by its only property that
matters for capacity: a signal = an event in the top decile of reactions, i.e. ~10% of events, drawn at random):
  * events of eligible, identity-verified, domestic-filer securities (foreign private issuers have no 8-K events);
  * event session E per Event Data v1; decision at the close of E+1 (two-session reaction); entry at the open of E+2;
  * fixed holding period H sessions; slots = N; new signals taken only into free slots, strongest first (here random);
  * D051 cash: target slot value 0.98/N of equity; entries scaled by the 15% gap reserve when cash is short.
Outputs per N: events/yr, signals/yr, entries/yr, mean slots occupied, idle slot share, invested share, round trips,
commissions, slippage and total cost a year at $100K and $200K (equity held constant: mechanical only).

    PYTHONPATH=src python research/phase2/h017/h017_capacity_sim.py -> h017_capacity_sim.json
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research/phase2/earnings_audit"))
from qresearch import sec_events as S  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import earnings_event_audit as A  # noqa: E402

HOLD = 60
TOP = 0.10
NS = (8, 10, 12, 15, 20)
SEEDS = range(20)
FEE, SLIP, BUFFER, GAP = 7.0, 0.001, 0.02, 0.15
OK_IDENTITY = ("verified (dated ticker evidence)", "verified (identity v2, SEC-corrected security)")


def build_event_days():
    U = A.load_universe()
    cal = A.calendar()
    sess = cal.sessions
    pos = {d: i for i, d in enumerate(sess)}
    tzc = {int(k): v["convention"] for k, v in
           json.loads((ROOT / "research/phase2/earnings_audit/tz_conventions.json").read_text())["ciks"].items()}
    import gzip
    from collections import defaultdict as dd
    xb = json.load(gzip.open(ROOT / "data/sec_derived/xbrl_filings.json.gz"))
    pbc = dd(list)
    for r in xb:
        if r.get("prefix") and r.get("filed"):
            pbc[int(r["cik"])].append((int(r["filed"][:4]) * 100 + int(r["filed"][5:7]), r["prefix"].upper()))
    sec = SECClient()
    per_day = Counter()          # decision-session index -> number of eligible events
    per_year = Counter()
    excluded = Counter()
    for sid, u in U.items():
        idc = A.identity_check(u, pbc)
        if idc not in OK_IDENTITY:
            excluded[idc] += 1
            continue
        months = set(u["months"])
        for cik in u["ciks"]:
            conv = tzc.get(cik, "UNRESOLVED")
            if conv == "UNRESOLVED":
                continue
            sub = sec.submissions(cik)
            if sub is None:
                continue
            for e in S.build_events(cik, filings_table(sub), cal, tz=conv)["events"]:
                if e.event_session is None or e.event_session not in pos:
                    continue
                i = pos[e.event_session] + 1                     # decision at close of E+1
                if i >= len(sess) - 1:
                    continue
                d = sess[i]
                if d.year < 2010 or d.year > 2021 or (d.year * 12 + d.month - 1) not in months:
                    continue                                       # eligible in the decision month only
                per_day[i] += 1
                per_year[d.year] += 1
    return sess, per_day, per_year, excluded


def simulate(sess, per_day, n, seed, equity=100_000.0):
    rng = random.Random(seed)
    slots = []                 # (exit index, value)
    cash = equity
    target = (1 - BUFFER) / n * equity
    entries = signals = 0
    occ, invested = [], []
    start = next(i for i, d in enumerate(sess) if d.year >= 2010 and d.month >= 3)
    end = max(i for i, d in enumerate(sess) if d.year <= 2021)
    pending = []               # entries decided at the previous close: (size)
    eqs = []
    for i in range(start, end):
        # ---- open of day i: exits due today (holding H sessions from the entry open), then decided entries
        keep = []
        for ex, v in slots:
            if ex <= i:
                cash += v * (1 - SLIP) - FEE
            else:
                keep.append((ex, v))
        slots = keep
        for size in pending:
            cash -= size * (1 + SLIP) + FEE
            slots.append((i + HOLD, size))
            entries += 1
        pending = []
        # ---- close of day i: signals of decision day i, sized from cash settled at this close (D051)
        k = sum(1 for _ in range(per_day.get(i, 0)) if rng.random() < TOP)
        signals += k
        free = n - len(slots)
        eq_now = cash + sum(v for _, v in slots)            # current equity (no returns modelled; costs only)
        target = (1 - BUFFER) / n * eq_now
        avail = cash - BUFFER * eq_now
        for _ in range(min(free, k)):
            size = min(target, max(0.0, avail - FEE) / ((1 + GAP) * (1 + SLIP)))
            if size < 1000:
                break
            pending.append(size)
            avail -= size * (1 + SLIP) * (1 + GAP) + FEE
        occ.append(len(slots))
        invested.append(sum(v for _, v in slots) / (cash + sum(v for _, v in slots)))
        eqs.append(cash + sum(v for _, v in slots))
    years = (sess[end] - sess[start]).days / 365.25
    rt = entries / years
    notional = sum(v for _, v in slots)
    mean_eq = sum(eqs) / len(eqs)
    avg_pos = (sum(invested) / len(invested)) * mean_eq / max(1e-9, sum(occ) / len(occ))
    comm = rt * 2 * FEE
    slip = rt * 2 * SLIP * avg_pos
    equity = mean_eq
    return dict(signals_per_year=signals / years, entries_per_year=rt, mean_slots_occupied=sum(occ) / len(occ),
                idle_slot_share=1 - sum(occ) / len(occ) / n, mean_invested=sum(invested) / len(invested),
                avg_position=avg_pos, commission_pa=comm / equity, slippage_pa=slip / equity,
                total_cost_pa=(comm + slip) / equity, years=years)


def main():
    sess, per_day, per_year, excluded = build_event_days()
    out = dict(rules=dict(hold_sessions=HOLD, top_share=TOP, fee=FEE, slippage=SLIP, buffer=BUFFER, gap_reserve=GAP),
               eligible_verified_events_by_year=dict(sorted(per_year.items())),
               excluded_securities_by_identity=dict(excluded), by_slots={})
    dist = Counter()
    for i, c in per_day.items():
        dist[min(c, 40)] += 1
    days_with_events = sum(1 for c in per_day.values() if c > 0)
    out["decision_days_with_events"] = days_with_events
    out["events_per_decision_day_hist"] = dict(sorted(dist.items()))
    for equity in (100_000.0, 200_000.0):
        for n in NS:
            runs = [simulate(sess, per_day, n, s, equity) for s in SEEDS]
            avg = {k: sum(r[k] for r in runs) / len(runs) for k in runs[0]}
            out["by_slots"][f"${int(equity / 1000)}K, N={n}"] = avg
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("events/yr", out["eligible_verified_events_by_year"])
    for k, v in out["by_slots"].items():
        print(k, {a: round(b, 4) for a, b in v.items()})


if __name__ == "__main__":
    main()
