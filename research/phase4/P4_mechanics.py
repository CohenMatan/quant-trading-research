"""P4-CP1 design study: MECHANICAL portfolio-size study for a Weekly, state-exit, slot-filling book. NO market data and
NO strategy returns: synthetic prices (one market factor + idiosyncratic noise) and synthetic holding durations, run
through the fidelity-verified Phase 3 book engine (qr_p3_engine.Books: the harness D051 sizing, settled cash, 2% buffer,
15% gap reserve, $4,000 minimum, $7 per order, 10 bps slippage, next-open fills).

Weekly mechanics simulated exactly as proposed: one decision per week at the last session's close; exits flagged at the
decision (state invalidated) fill at the next open; entries fill free slots at the same decision (exiting slots are
still occupied, so a slot is re-used one week later); no fixed horizon.

Holding durations are SCENARIOS (unknown before any data is touched): geometric with mean H weeks, optionally with a
share of whipsaw entries that exit after 1-2 weeks. For each N in {10, 12, 15, 20} the study reports the position size,
the cost a year, the invested share, scaled / skipped buys, and the idiosyncratic tracking error implied by N (scaled
from the measured 10-slot random control books, P3_calibration.json).

    PYTHONPATH=src python research/phase4/P4_mechanics.py -> P4_mechanics.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_p3_engine as EN  # noqa: E402

NS = (10, 12, 15, 20)
HS = (8, 13, 26, 52)                 # mean holding (weeks)
WHIP = (0.0, 0.3)                    # share of entries that are whipsaws (exit after 1-2 weeks)
CASHES = (100_000, 200_000)
YEARS, U, BOOKS, SEED = 8, 400, 24, 20261005
MKT_MU, MKT_VOL, IDIO_VOL = 0.08, 0.16, 0.28


def prices(rng):
    n = YEARS * 252
    m = rng.normal(MKT_MU / 252 - MKT_VOL ** 2 / 504, MKT_VOL / np.sqrt(252), n)
    e = rng.normal(-IDIO_VOL ** 2 / 504, IDIO_VOL / np.sqrt(252), (n, U))
    close = 50 * np.exp(np.cumsum(m[:, None] + e, axis=0))
    gap = np.exp(rng.normal(0, 0.008, (n, U)))
    opn = np.vstack([close[:1], close[:-1]]) * gap
    return opn, close


def run(N, H, whip, cash, rng, opn, close):
    B = EN.Books(BOOKS, N, 10 ** 9, cash)
    n = len(close)
    dur = np.zeros((BOOKS, N), dtype=np.int64)     # remaining weeks for each held slot (synthetic state persistence)
    inv, cost, eq_sum, scaled0, skipped0, entries0 = [], 0.0, 0.0, 0, 0, 0
    has = np.ones(U, dtype=bool)
    sizes = []
    for t in range(n):
        B.open_fills(opn[t], has, t)
        newly = (B.state == EN.HELD) & (dur == 0)
        if newly.any():                              # duration drawn when the position is opened
            k = int(newly.sum())
            d = rng.geometric(1.0 / H, k)
            w = rng.random(k) < whip
            d[w] = rng.integers(1, 3, int(w.sum()))
            dur[newly] = d
        pv = B.equity(close[t])
        if t % 5 == 4:                                 # weekly decision at the last session of the week
            held = (B.state == EN.HELD) & ~B.psell
            dur[held] -= 1
            extra = held & (dur <= 0)
            due = B.exits_due(t, extra=extra)
            n_sells = due.sum(axis=1)
            free = B.free()
            for b in range(BOOKS):
                if free[b] > 0:
                    blocked = B.blocked(b)
                    cand = [s for s in rng.permutation(U)[: free[b] + len(blocked) + 5] if s not in blocked][: free[b]]
                    out = B.plan_entries(b, cand, close[t], float(pv[b]), int(n_sells[b]))
                    sizes += [q * close[t][s] for s, q in out]
            dur[B.state == EN.EMPTY] = 0
        c, sl, _nt = B.reset_costs()
        cost += float((c + sl).sum())
        eq_sum += float(pv.sum())
        held_val = pv - B.cash
        inv.append(float((held_val / pv).mean()))
    years = n / 252
    mean_eq = eq_sum / n / BOOKS
    return dict(cost_pa=cost / BOOKS / years / mean_eq, invested_share=float(np.mean(inv)),
                buys=B.counts["entries"] / BOOKS / years, scaled_rounds=B.counts["scaled"] / BOOKS / years,
                skipped_min=B.counts["skipped_min"] / BOOKS / years,
                median_new_position=float(np.median(sizes)) if sizes else 0.0,
                mean_positions=float(np.mean([(B.state == EN.HELD).sum(axis=1).mean()])))


def main():
    cal = json.loads((ROOT / "research/phase3/P3_calibration.json").read_text())["model"]
    te10_tr, te10_oos = cal["selection_te_train"], cal["selection_te_oos"]
    rng = np.random.default_rng(SEED)
    opn, close = prices(rng)
    out = dict(model=dict(years=YEARS, synthetic_stocks=U, books_per_cell=BOOKS, market=(MKT_MU, MKT_VOL),
                          idio_vol=IDIO_VOL, note="synthetic prices; holding durations are scenarios"),
               analytic={}, simulated={}, diversification={})
    for cash in CASHES:
        for N in NS:
            pos = 0.98 * cash / N
            out["analytic"][f"${cash // 1000}K_N{N}"] = dict(
                target_position=pos, min_position_ok=pos >= 4000 * 1.01,
                commission_per_round_trip_pct=14 / pos, slippage_per_round_trip_pct=0.002,
                cost_pa_by_mean_hold_weeks={f"H{h}": round(52 / h * (2 * 0.001 * 0.98 + 14 * N / cash), 4) for h in HS})
    for N in NS:
        k = np.sqrt(10 / N)
        out["diversification"][f"N{N}"] = dict(selection_te_vs_ew_train=te10_tr * k, selection_te_vs_ew_oos=te10_oos * k,
                                               note="idiosyncratic part scaled by sqrt(10/N) from the 10-slot controls")
    for cash in CASHES:
        for N in NS:
            for H in HS:
                for wp in WHIP:
                    r = run(N, H, wp, cash, np.random.default_rng([SEED, N, H, int(wp * 10), cash]), opn, close)
                    out["simulated"][f"${cash // 1000}K_N{N}_H{H}_W{int(wp * 100)}"] = r
                    print(cash, N, H, wp, {k: round(v, 4) for k, v in r.items()})
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
