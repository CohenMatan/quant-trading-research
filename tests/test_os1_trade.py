"""H032 R1 / R2 trading layer (owner D282): the pure module qr_os1_trade (targets on actual holdings, priority, slot-
limited entries with exiting names still occupying their slot, turnover-matched controls, the frictionless equal-weight
index, P&L attribution), the shadow engine copy (byte-identical to the LEAN-verified Phase 3 engine; sizing identical
to the harness's plan_orders at the H032 portfolio rules), and an END-TO-END run of the REAL harness + the pinned X807
host + the S033 trading host on a fake broker (tests/fake_lean.py) with splits, dividends, a delisting, a stale holding,
cash scaling and turnover: the LEAN B1 book and its shadow replay must have IDENTICAL daily equity; every LEAN fill is
after its signal date at the next open +/- slippage with $7; no negative cash; at most 15 positions; outputs carry no
identifiers."""
import json
import math
from datetime import date, timedelta

import numpy as np
import pytest

import qr_os1 as O
import qr_os1_trade as T
from conftest import ROOT, load_module
from test_commission import _load_harness

BOOKS = load_module(ROOT / "src/qresearch/lean/qr_os1_books.py", "qr_os1_books_t")
PF = {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 5000, "max_positions": 15,
      "buy_funding": "settled_cash_only", "gap_reserve": 0.15}


# ---------------------------------------------------------------- pure layer
def test_engine_copy_is_byte_identical():
    a = (ROOT / "src/qresearch/lean/qr_p3_engine.py").read_bytes()
    b = (ROOT / "src/qresearch/lean/qr_os1_books.py").read_bytes()
    assert a == b


def test_shadow_sizing_equals_harness_at_h032_rules(monkeypatch):
    h = _load_harness(monkeypatch)
    rng = np.random.default_rng(11)
    for trial in range(400):
        B = BOOKS.Books(1, 15, 10 ** 9, 100_000, slip=0.001, fee=7.0, buffer=0.02, gap=0.15, min_pos=5000.0,
                        max_w=0.10)
        n_held = int(rng.integers(0, 15))
        prices = rng.uniform(5, 600, 80)
        for k in range(n_held):
            B.state[0, k], B.sid[0, k], B.qty[0, k] = BOOKS.HELD, 60 + k, int(rng.integers(5, 300))
        B.cash[0] = float(rng.uniform(-300, 60_000))
        pv = float(B.equity(prices)[0])
        n_sells = int(rng.integers(0, min(n_held, 4) + 1))
        stocks = list(rng.choice(50, size=15 - n_held, replace=False))
        w = h.slot_weight(15, pv, PF)
        items = [(f"X{k}", 0.0, prices[60 + k], B.qty[0, k], 0.0, False) for k in range(n_sells)]
        items += [(s, w, prices[s], 0.0, 0.0, False) for s in stocks]
        ref = h.plan_orders(items, pv, float(B.cash[0]), PF, 0.001, lambda q: 7.0, 0.0, n_held)
        got = B.plan_entries(0, stocks, prices, pv, n_sells)
        assert [(int(s), q) for s, q in got] == [(int(s), q) for s, q in ref["buys"]], trial


def test_ranked_targets_priority_and_buffer():
    sc = {f"k{i:02d}": (100 - i, 1.0) for i in range(40)}
    tgt, pri = T.ranked(sc, set())
    assert tgt == sorted(f"k{i:02d}" for i in range(15)) and pri == [f"k{i:02d}" for i in range(15)]
    tgt2, pri2 = T.ranked(sc, {"k29", "k31"})
    assert "k29" in tgt2 and "k31" not in tgt2 and pri2[0] == "k00" and len(tgt2) == 15
    assert T.ranked({}, {"x"}) == ([], [])
    assert T.pending_after(pri2, {"k00", "k29"}) == [x for x in pri2 if x not in ("k00", "k29")]


def test_exits_entries_slot_rule():
    held = {"a", "b", "c"}
    ex, en = T.exits_entries(["a", "x", "y"], ["x", "y", "a"], held, held, n_slots=3, decision=True)
    assert ex == ["b", "c"] and en == []                    # exiting names keep their slots until sold (D051)
    ex, en = T.exits_entries(["a", "x", "y"], ["x", "y", "a"], {"a"}, {"a"}, n_slots=3, decision=False)
    assert ex == [] and en == ["x", "y"]                    # the next close: freed slots filled in priority order
    assert T.exits_entries(["a"], ["a", "z"], {"a"}, {"a", "q"}, n_slots=2)[1] == []


def test_plans_turnover_matched_and_deterministic():
    rng = np.random.default_rng(2)
    keys = [f"s{i:03d}" for i in range(60)]
    s_b1 = {k: (float(rng.normal()), 1.0) for k in keys[:30]}
    rev = dict(s_b1=s_b1, s_vb1={k: v for k, v in s_b1.items() if k < "s020"}, s_b0=s_b1,
               mom={k: (float(rng.normal()), 1.0) for k in keys}, pool_b2=sorted(s_b1), pool_cov=keys,
               quint={k: 1 + i % 5 for i, k in enumerate(keys)})
    held = {b: set() for b in T.SHADOW}
    p1, n1, pairs, att, mat = T.plans(rev, held, set(), {}, 0)
    p2 = T.plans(rev, held, set(), {}, 0)[0]
    assert p1 == p2 and n1 == 15 and att == 5 * 15 and mat == 75
    assert all(len(p1[b][0]) == 15 for b in p1)
    lean = set(p1["LEAN"][0])
    held = {b: set(p1[b][0]) for b in T.SHADOW}
    s_b1b = dict(s_b1)
    for k in sorted(lean)[:3]:
        s_b1b.pop(k)                                         # three LEAN names leave the passing pool
    rev2 = dict(rev, s_b1=s_b1b, pool_b2=sorted(s_b1b))
    p3, n3, pairs3, _, _ = T.plans(rev2, held, lean, pairs, 1)
    assert n3 == 3
    for b in [x for x in T.SHADOW if x.startswith("RND_")]:
        assert len(set(p1[b][0]) - set(p3[b][0])) == 3      # the random books replace as many names as B1 entered
    for s in O.SEEDS_BETA:
        assert set(pairs3[s]) == set(p3["LEAN"][0])         # one control per LEAN B1 name


def test_ew_return_and_pnl():
    r, n, miss = T.ew_return([10, 20, np.nan, 5], [11, np.nan, 3, 6])
    assert n == 3 and miss == 1 and r == pytest.approx((0.1 + 0.0 + 0.2) / 3)
    assert T.ew_return([np.nan], [1.0])[0] is None
    p = T.PnL()
    p.fill("buy", 1, 10, 100.0, 7.0)
    p.fill("sell", 1, -10, 110.0, 7.0)
    p.add(1, 5.0)
    p.fill("buy", 2, 5, 10.0, 7.0)
    tot = p.total({2: 60.0})
    assert tot[1] == pytest.approx(100 - 14 + 5) and tot[2] == pytest.approx(-57 + 60)


# ---------------------------------------------------------------- end to end on the fake broker
def _business_days(a, b):
    d = np.arange(np.datetime64(a), np.datetime64(b))
    return [date.fromisoformat(str(x)) for x in d[np.is_busday(d)]]


def _filings():
    out = []
    for y in range(2009, 2014):
        for m, dd, form in ((3, 1, "10-K"), (5, 10, "10-Q"), (8, 10, "10-Q"), (11, 10, "10-Q")):
            f = date(y, m, dd)
            if date(2009, 8, 1) <= f <= date(2013, 5, 31):
                out.append((f, form))
    return out


NC = 40
SPLIT_C, DIV_C, DELIST_C, STALE_C = 5, 6, 11, 19   # 11 and 19 pass both filters with high 2012 repurchase rates
SPLIT_DAY, DELIST_DAY, STALE_FROM = date(2011, 6, 1), date(2012, 3, 15), date(2012, 6, 29)


def _rate(c, y):
    return ((c * 7 + y * 3) % 11 - 3) / 100.0


def _world():
    cal = _business_days("2009-05-01", "2013-07-01")
    rng = np.random.default_rng(7)
    ucr, ext = {}, {}
    for c in range(1, NC + 1):
        tk = f"C{c:02d}"
        p, s, k = [], [], []
        sh = 1e8
        for f, form in _filings():
            sh *= 1 - _rate(c, f.year) / 4
            v = sh * (2.0 if (c == SPLIT_C and f > SPLIT_DAY) else 1.0)
            p.append([f.isoformat(), tk, 1, v, (f - timedelta(days=5)).isoformat()])
            s.append("6022" if c in (1, 2) else ("2834" if c % 3 == 0 else "3571"))
            if form == "10-K":
                ocf = -1e7 if c % 7 == 0 else 5e8
                g = 0.05 if (c + f.year) % 4 else -0.03
                k.append([f.isoformat(), date(f.year - 1, 12, 31).isoformat(), ocf, 1e9 * (1 + g), 1e9])
        fl = [[f.isoformat(), date(f.year - 1, 6, 30).isoformat(), 3e9] for f, form in _filings() if form == "10-K"]
        ucr[str(c)] = dict(p=p, f=fl)
        ext[str(c)] = dict(s=s, k=k)
    syms = {c: None for c in range(1, NC + 1)}
    close = {}
    lvl = {c: 40.0 + c for c in range(1, NC + 1)}
    spy = 100.0
    prices, spy_px = {}, {}
    rm_all = rng.normal(0.0003, 0.01, len(cal))
    for i, d in enumerate(cal):
        day = {}
        spy_o = spy * math.exp(rng.normal(0, 0.002))
        spy *= math.exp(rm_all[i])
        spy_px[d] = (spy_o, spy)
        for c in lvl:
            if c == DELIST_C and d >= DELIST_DAY:
                continue
            if c == STALE_C and d >= STALE_FROM:
                continue
            prev = lvl[c]
            lvl[c] = prev * math.exp((0.5 + c / 40) * rm_all[i] + rng.normal(0.0002 * (c % 5), 0.012))
            o = prev * math.exp(rng.normal(0, 0.004))
            f = 0.5 if (c == SPLIT_C and d >= SPLIT_DAY) else 1.0
            day[c] = (o * f, lvl[c] * f)          # raw prices halve on the split day
        prices[d] = day
    return cal, ucr, ext, prices, spy_px


def _fundamental(fake, x_syms, prices, adj, d):
    """Objects reflecting session d (the stream stamped d + 1)."""
    out = []
    for c, sym in x_syms.items():
        if d not in prices or c not in prices[d]:
            continue
        o, cl = prices[d][c]
        restored = c in (3, 4)
        sf = 0.5 if (c == SPLIT_C and d < SPLIT_DAY) else 1.0
        sr = fake._ns(exchange_id="NYS", security_type="ST00000001", is_depositary_receipt=False, is_primary_share=True,
                      share_class_description="Common Stock")
        cr = fake._ns(country_id="USA", is_limited_partnership=False, is_limited_liability_company=False,
                      industry_template_code="N")
        out.append(fake._ns(symbol=sym, dollar_volume=2e7, price=cl, split_factor=sf, adjusted_price=adj[c][d],
                            has_fundamental_data=not restored, market_cap=0.0 if restored else cl * 1e8 * 1.3,
                            security_reference=sr, company_reference=cr, asset_classification=fake._ns(sic=3571)))
    return out


def _run(monkeypatch, slip_bps=10):
    import fake_lean as F
    import hashlib
    cal, ucr, ext, prices_c, spy_px = _world()
    store = {"rr/ucr.json": json.dumps({"meta": {}, "r": ucr}), "rr/os1.json": json.dumps({"meta": {}, "r": ext})}
    sha = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in store.items()}
    exp = dict(start="2010-08-31", end="2021-12-31", warmup_start="2009-05-01", cash=100000, experiment_id="E033-T",
               costs=dict(slippage_bps=slip_bps, commission_per_order=7.0),
               universe=dict(min_market_cap=2e9, min_price=5.0, min_avg_dollar_volume=5e6, adv_days=20),
               portfolio=dict(PF), params=dict(start_review="2010-08-31", ucr_object_key="rr/ucr.json",
                                               ucr_reference_sha256=sha["rr/ucr.json"], os1_object_key="rr/os1.json",
                                               os1_reference_sha256=sha["rr/os1.json"]))
    ai, h, x, s = F.load_stack(monkeypatch, exp)
    a = s.H032Trading()
    a.fake_setup(cal, store)
    a.initialize()
    syms = {c: F.Sym(f"SID{c}", f"C{c:02d}") for c in range(1, NC + 1)}
    # adjusted (total-return, split-continuous) prices for the stream
    adj = {}
    for c in syms:
        adj[c] = {}
        for d in cal:
            if c in prices_c[d]:
                f = 0.5 if (c == SPLIT_C and d < SPLIT_DAY) else 1.0
                adj[c][d] = prices_c[d][c][1] * f
    prices = {d: {syms[c]: v for c, v in day.items()} for d, day in prices_c.items()}
    for d in cal:
        prices[d][a.spy] = spy_px[d]
    divs, splits, warn, delist = {}, {}, {}, {}
    for d in cal:
        if d.month in (2, 5, 8, 11) and d.day <= 7 and not any(x for x in divs.get(d, [])):
            if d == next(x for x in cal if x.year == d.year and x.month == d.month):
                divs.setdefault(d, []).append((syms[DIV_C], 0.30))
                divs.setdefault(d, []).append((a.spy, 0.55))
    prev_split = max(x for x in cal if x < SPLIT_DAY)
    splits[SPLIT_DAY] = [(syms[SPLIT_C], 0.5, prices_c[prev_split][SPLIT_C][1])]
    warn[max(x for x in cal if x < DELIST_DAY)] = [syms[DELIST_C]]
    delist[DELIST_DAY] = [syms[DELIST_C]]
    m = F.Market(a, ai, cal, prices, lambda d: _fundamental(F, syms, prices_c, adj, d), splits=splits,
                 dividends=divs, delist=delist, warn=warn)
    m.run()
    return a


def _parse(a):
    out, eq = {}, {}
    for ln in a._qr_msgs:
        if not ln.startswith("OS1R|"):
            continue
        parts = ln.split("|", 3)
        if parts[1] == "eq":
            eq[parts[2]] = [float(v) for v in parts[3].split(",")]
        elif parts[1] in ("dates", "npos", "maxw"):
            out[parts[1]] = ln.split("|", 2)[2].split(",")
        else:
            out[parts[1]] = json.loads(ln.split("|", 2)[2])
    return out, eq


@pytest.fixture(scope="module")
def fake_run():
    mp = pytest.MonkeyPatch()
    try:
        a = _run(mp)
    finally:
        mp.undo()
    return a


def test_end_to_end_lean_equals_shadow_replay(fake_run):
    a = fake_run
    out, eq = _parse(a)
    meta = out["meta"]
    assert meta["first_review_traded"] == "2010-08-31" and meta["reviews_traded"] >= 30
    lean, shadow = np.array(eq["LEAN"]), np.array(eq["B1"])
    assert len(lean) == len(out["dates"]) == len(shadow) and out["dates"][0] == "2010-08-31"
    assert np.max(np.abs(lean - shadow)) < 1e-6 * lean.max()                 # identical accounting and decisions
    assert lean[-1] != pytest.approx(100000.0)                                # it traded
    st = meta["stats"]
    assert st["lean_vs_shadow_target_diff"] == 0 and st["lean_missing_symbol"] == 0 and st["lean_entries"] > 15
    assert meta["engine"]["split_adjust"] > 0 and meta["engine"]["dividends"] > 0
    assert meta["engine"]["forced_stale"] > 0 and meta["engine"]["forced_delist"] > 0
    hs = a._qr_stats
    assert hs["held_delistings"] > 0 and hs["stale_exits"] > 0 and hs["forced_fee_debits"] > 0   # LEAN B1 paths
    assert hs["timing_violations"] == 0 and hs["invalid"] == 0 and hs["negative_qty"] == 0
    assert hs["max_fill_dev"] < 1e-9 and hs["min_cash_frac"] >= 0.0
    assert max(int(x) for x in out["npos"]) <= 15
    assert all(len(eq[b]) == len(lean) for b in T.SHADOW) and len(eq["SPY"]) == len(lean)
    mine = [ln for ln in a._qr_msgs if ln.startswith("OS1R|")]
    assert mine and not any("SID" in ln or "C0" in ln or "C1" in ln for ln in mine)   # the host exports no identifiers


def test_end_to_end_controls_and_indices(fake_run):
    out, eq = _parse(fake_run)
    meta = out["meta"]
    # a 40-name fake world can exhaust a beta quintile (on real data the canary matched 1,234 of 1,234)
    assert 0 < meta["stats"]["beta_matched"] <= meta["stats"]["beta_attempted"]
    ew = out["ew"]
    assert len(ew) == meta["reviews_traded"] and ew[-1][0] == "end"
    assert all(r[1] is not None for r in ew)
    for b in T.SHADOW:
        assert eq[b][-1] != pytest.approx(100000.0), b                       # every control traded
    costs = out["costs"]
    assert costs and all(len(c[1]) == len(T.SHADOW) for c in costs)
    att = meta["pnl_b1_shadow"]
    assert att["n_restored"] + att["n_vendor"] > 0
    total = att["restored"] + att["vendor"] + att["unknown"]
    assert total == pytest.approx(eq["B1"][-1] - 100000.0, abs=1.0)           # P&L attribution adds up to the wealth
    assert len(out["reviews"]) == meta["reviews_total"]
