"""P7-CP3 (D171) offline mechanics: the pre-registered definitions (whipsaw within 3 monthly reviews, mechanical cost
notional, weekly disqualifier exits, no regime input to the score) and the committed outputs (84 reviews 2011-01 ..
2017-12, no return-like field)."""
import inspect
import json
import sys

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research/phase7"))
import P7_CP3_mechanics as Mx  # noqa: E402
import qr_p7_export as E  # noqa: E402
import qr_p7_score as S  # noqa: E402


def _row(total, bits=0):
    return dict(bits=bits, adv_k=10000, ff=0, total=total, points=(15, 15, 10, 15, 10, 10, 10, 15) if total else None)


def _revs(seq, extra=None):
    out = []
    for m, x in enumerate(seq):
        rows = {"A": _row(x)}
        if extra:
            rows.update(extra(m))
        out.append(dict(t=f"2011-{m + 1:02d}-28", tk=f"2011-{m + 1:02d}-28", year="2011", rows=rows))
    return out


def test_whipsaw_is_a_rebuy_within_three_reviews():
    revs = _revs([80, 74, 81, 81, 70, 70, 70, 70, 82])     # sold at 1, re-bought at 2 (1 review); sold 4, bought 8
    ev = Mx.timeline(revs, [])
    trades, closed, open_, util, books, anom = Mx.simulate(revs, [], ev, 80, 5, 3, 1)
    buys = [t for t in trades if t[0] == "buy"]
    assert [t[3] for t in buys] == [0, 2, 8]
    assert [t[4].endswith("|whipsaw") for t in buys] == [False, True, False]
    assert [t[4] for t in trades if t[0] == "sell"] == ["exit_threshold", "exit_threshold"]
    assert len(open_) == 1 and anom == 0


def test_weekly_check_sells_on_disqualifier_only_and_frozen_skips_trend():
    revs = _revs([85, 85, 85])
    weekly = [dict(t="2011-01-31", tk="2011-01-31", members={"A"}, bits={"A": E.BIT["H6"] | E.BIT["H4"]}),
              dict(t="2011-02-04", tk="2011-02-04", members={"A"}, bits={"A": E.BIT["H6"]})]
    ev = Mx.timeline(revs, weekly)
    trades = Mx.simulate(revs, weekly, ev, 80, 5, 3, 1)[0]
    sells = [t for t in trades if t[0] == "sell"]
    assert len(sells) == 1 and sells[0][2] == "2011-02-04" and sells[0][4].startswith("dq_weekly:H6")


def test_mechanical_cost_formula():
    revs = _revs([80, 70, 80, 70, 80, 70, 80])               # 4 buys + 3 sells = 7 orders
    ev = Mx.timeline(revs, [])
    r = Mx.churn_metrics(revs, [], ev, {"A": "BusEq"}, 80, "H1", 10)
    assert r["orders_total"] == 7
    c = r["costs"]["100000"]
    assert c["notional_per_order"] == 10_000.0
    assert abs(c["total_usd_yr"] - 7 * (7.0 + 0.001 * 10_000) / 7.0) < 1e-6
    c2 = Mx.churn_metrics(revs, [], ev, {"A": "BusEq"}, 80, "H1", 12)["costs"]["200000"]
    assert abs(c2["notional_per_order"] - 200_000 / 12) < 1e-6


def test_regime_never_enters_the_score():
    assert list(inspect.signature(S.score_date).parameters) == ["stocks", "sector_context"]
    assert "regime" not in inspect.getsource(S.score_date)


def test_committed_outputs_are_score_only():
    o = json.loads((ROOT / "research/phase7/P7_CP3_mechanics.json").read_text())
    assert o["reviews"] == 84 and o["first_review"] == "2011-01-31" and o["last_review"] == "2017-12-29"
    assert len(o["churn"]) == 4 * 3 * 4 and all(r["weekly_anomalies"] == 0 for r in o["churn"])
    txt = json.dumps(o).lower()
    for bad in ("return", "cagr", "sharpe", "alpha", "drawdown", "forward", "win_rate", "profit_factor"):
        assert bad not in txt, bad
    st = json.loads((ROOT / "research/phase7/P7_CP3_E993_stats.json").read_text())
    assert st["calendar_check"]["reviews_match"] and st["calendar_check"]["weekly_match"]
    assert st["slice_spot_check"]["mismatch"] == 0
    ix = (ROOT / "experiments/E993-01/result.json").read_text()
    r = json.loads(ix)
    assert r["harness_summary"]["orders"] == 0


def test_regime_cap_changes_only_the_number_of_positions_never_the_order():
    import gzip
    pay = json.loads(gzip.open(ROOT / "research/phase7/P7_CP3_E993_payload.json.gz").read())
    sids = pay["sids"]
    for t, tk, enc in pay["reviews"][::12]:
        rows = {sids[r["i"]]: r for r in E.decode_rows(enc)}
        rec = Mx.records_of(rows)
        adv = {s: r["adv_k"] * 1000.0 for s, r in rows.items()}
        full = S.plan_review(set(), rec, adv, 75, 65, 5, 12, 12)["buy"]
        for cap in (0, 3, 6, 9):
            assert S.plan_review(set(), rec, adv, 75, 65, 5, 12, cap)["buy"] == full[:cap]
