"""P7-CP1 audit host X992 (strategies/X992_p7_price_technical_audit/main.py): the end-of-run pipeline (panel, error
hunt, features, breadth, independent recomputation, regime availability) runs offline on a fake QuantConnect
environment with SYNTHETIC prices, and the independent recomputation agrees with the panel."""
import json
import sys
import types
from datetime import datetime

import numpy as np
import pandas as pd

from conftest import ROOT, load_module


class Sym:
    def __init__(self, v):
        self.value = v
        self.id = v

    def __repr__(self):
        return self.value


def _market(n=12):
    d = np.arange(np.datetime64("2007-01-01"), np.datetime64("2017-12-30"))
    cal = d[np.is_busday(d)].astype(np.int64)
    D = cal.size
    rng = np.random.default_rng(5)
    RAW = 30 * np.exp(np.cumsum(rng.normal(0.0002, 0.015, (D, n)), axis=0))
    alive = np.ones((D, n), bool)
    alive[:900, 1] = False                       # an IPO in 2010
    alive[2000:, 2] = False                      # delisted in 2014
    alive[1500, 3] = False                       # one missing session
    splits = {4: [(1800, 0.5)]}                  # 2:1 split: raw price halves at row 1800
    RAW[1800:, 4] *= 0.5
    divs = {j: [(b, 0.005 * RAW[b - 1, j], RAW[b - 1, j]) for b in range(60, D, 63)] for j in range(n)}
    O = RAW * np.exp(rng.normal(0, 0.003, (D, n)))
    H = np.maximum(RAW, O) * 1.01
    L = np.minimum(RAW, O) * 0.99
    Vol = rng.uniform(1e6, 3e6, (D, n))
    Vol[1800:, 4] *= 2
    # split / total-return adjusted reference (what QuantConnect's ADJUSTED would give, exact amounts)
    ADJ = RAW.copy()
    for j in range(n):
        m = np.ones(D)
        for b, f in splits.get(j, []):
            m[:b] *= f
        for b, a, r in divs[j]:
            m[:b] *= 1 - a / r
        ADJ[:, j] *= m
    SC = RAW.copy()
    for j, lst in splits.items():
        for b, f in lst:
            SC[:b, j] *= f
    return dict(cal=cal, RAW=RAW, O=O, H=H, L=L, V=Vol, ADJ=ADJ, SC=SC, alive=alive, splits=splits, divs=divs, n=n)


def _ts(days):
    return pd.to_datetime(days.astype("datetime64[D]")) + pd.Timedelta(days=1)


def _host(monkeypatch, M):
    ai = types.ModuleType("AlgorithmImports")
    ai.Resolution = types.SimpleNamespace(DAILY="daily")
    ai.DataNormalizationMode = types.SimpleNamespace(RAW="raw", SCALED_RAW="scaled", ADJUSTED="adjusted")

    class Split:
        pass

    class Dividend:
        pass

    class CBOE:
        pass
    ai.Split, ai.Dividend, ai.CBOE = Split, Dividend, CBOE
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    hm = types.ModuleType("qr_harness")
    cal = M["cal"]
    syms = [Sym(f"S{j:02d}") for j in range(M["n"])]
    spy = Sym("SPY")

    def rows(d0, d1):
        a = np.datetime64(d0.strftime("%Y-%m-%d")).astype(np.int64)
        b = np.datetime64(d1.strftime("%Y-%m-%d")).astype(np.int64)
        return (cal >= a) & (cal < b)            # bars end at midnight after the session

    class QRAlgorithm:
        def __init__(self):
            self.qr_params = {}
            self.qr = {"end": "2017-12-31"}
            self.qr_sec, self.qr_sic = object(), types.SimpleNamespace(sic_on=lambda sid, d: 3500, t={})
            self.spy = spy
            self.msgs = []
            self._qr_log_budget = 0

        def _qr_log(self, line):
            self.msgs.append(line)

        def add_index(self, *a):
            raise RuntimeError("no index data in the test")

        def add_data(self, *a):
            raise RuntimeError("no custom data in the test")

        def history(self, what, *a, **kw):
            if what is spy:
                return pd.DataFrame({"close": np.ones(cal.size)}, index=pd.MultiIndex.from_arrays([[spy] * cal.size, _ts(cal)]))
            if what in (Split, Dividend):
                lst, d0, d1 = a[0], a[1], a[2]
                sel = rows(d0, d1 + pd.Timedelta(days=1))
                ix_s, ix_t, recs = [], [], []
                for s in lst:
                    j = int(s.id[1:])
                    evs = M["splits"].get(j, []) if what is Split else M["divs"][j]
                    for e in evs:
                        if not sel[e[0]]:
                            continue
                        ix_s.append(s)
                        ix_t.append(pd.Timestamp(np.datetime64(int(cal[e[0]]), "D")))
                        recs.append(dict(type="SPLIT_OCCURRED", referenceprice=1.0, splitfactor=e[1]) if what is Split
                                     else dict(distribution=e[1], referenceprice=e[2]))
                if not recs:
                    return pd.DataFrame({"value": [0.0]}, index=pd.MultiIndex.from_arrays([[lst[0]], [pd.Timestamp(d0)]]))
                return pd.DataFrame(recs, index=pd.MultiIndex.from_arrays([ix_s, ix_t]))
            lst, d0, d1 = what, a[0], a[1]
            mode = kw["data_normalization_mode"]
            ix_s, ix_t, cols = [], [], {k: [] for k in ("open", "high", "low", "close", "volume")}
            for s in lst:
                j = int(s.id[1:])
                ok = M["alive"][:, j] & rows(d0, d1)
                src = {"raw": M["RAW"], "scaled": M["SC"], "adjusted": M["ADJ"]}[mode]
                ix_s += [s] * int(ok.sum())
                ix_t += list(_ts(cal[ok]))
                cols["close"] += list(src[ok, j])
                cols["open"] += list(M["O"][ok, j])
                cols["high"] += list(M["H"][ok, j])
                cols["low"] += list(M["L"][ok, j])
                cols["volume"] += list(M["V"][ok, j])
            return pd.DataFrame(cols, index=pd.MultiIndex.from_arrays([ix_s, ix_t]))

    hm.QRAlgorithm = QRAlgorithm
    monkeypatch.setitem(sys.modules, "qr_harness", hm)
    mod = load_module(ROOT / "strategies/X992_p7_price_technical_audit/main.py", "x992_test")
    a = mod.P7PriceAudit()
    a.qr_initialize()
    # eligible sets: every selection day from 2010-02-01 (alive on the previous session)
    for r in range(1, cal.size):
        day = int(cal[r])
        if day < np.datetime64("2010-02-01").astype(np.int64):
            continue
        el = tuple(sorted(s.id for j, s in enumerate(syms) if M["alive"][r - 1, j]))
        a.sel[day] = el
        for j, s in enumerate(syms):
            a.sym[s.id] = s
        if np.datetime64(day, "D").astype("datetime64[M]") != np.datetime64(int(cal[r - 1]), "D").astype("datetime64[M]"):
            a.ff12_m[day] = {s: "Manuf" for s in el}
    return a


def test_x992_end_pipeline_on_synthetic_market(monkeypatch):
    M = _market()
    a = _host(monkeypatch, M)
    a.qr_on_end()
    st = json.loads("".join(m.split("|", 2)[2] for m in a.msgs if m.startswith("QRP7P|")))
    pan = st["panel"]
    assert pan["securities"] == M["n"] and pan["duplicate_bars"] == 0 and pan["out_of_order_securities"] == 0
    assert pan["split"]["n"] == 1 and pan["split"]["aligned"] == 1
    assert pan["missing_inside_life"] == 1 and pan["adj_dev_nonevent_gt_1e6"] == 0
    assert pan["adj_dev_event_beyond_cent"] == 0 and pan["jumps_gt_50pct"] == 0
    fid = st["fidelity"]
    assert fid["pairs"] > 0 and fid["mismatch"] == 0 and fid["agree"] == fid["pairs"] - fid["missing"]
    assert st["alignment_price"]["violations"] == 0
    assert st["eligibility"]["eligible_after_last_bar"] == 0
    assert st["breadth_dead_stock_days_in_denominator"] > 0           # the delisted security counted before it died
    assert "2012" in st["breadth"]["above200"] and st["breadth_survivor_bias"]["above200"]["days"] > 0
    assert st["young"]["2010"]["lt252_bars"] > 0                        # the 2010 IPO
    assert st["regime_inputs"]["SPY"]["bars"] > 0 and st["overlap"]["dates"] == 0      # < 30 securities: no matrix
    assert st["missing_sessions_detail"]["securities"] == 1 and st["jumps_on_eligible_days"]["n"] == 0
    assert any(m.startswith("AP|") for m in a.msgs)


def _fund(sid, ticker, day, k, cid):
    """A fake vendor Fundamental object: a quarterly filer whose latest report (as of `day`) is quarter k."""
    from datetime import date, timedelta
    NS = types.SimpleNamespace
    qend = [date(2008, 3, 31), date(2008, 6, 30), date(2008, 9, 30), date(2008, 12, 31)]
    pes = []
    y = 2008
    while len(pes) < 45:
        for m, d_ in ((3, 31), (6, 30), (9, 30), (12, 31)):
            pes.append(date(y, m, d_))
        y += 1
    vis = [p for p in pes if p + timedelta(days=40) < day]
    pe = vis[-1]
    fd = pe + timedelta(days=40)
    i = pes.index(pe)
    q = 100.0 + i
    fy_end = [p for p in pes[:i + 1] if p.month == 12]
    fy = None
    if fy_end:
        j = pes.index(fy_end[-1])
        fy = sum(100.0 + x for x in range(j - 3, j + 1))

    def per(three, twelve=None):
        return NS(three_months=three, twelve_months=twelve)
    inc = NS(total_revenue=per(q, fy), gross_profit=per(q / 2, fy / 2 if fy else None), cost_of_revenue=per(q / 2, fy / 2 if fy else None),
             operating_income=per(q / 4, fy / 4 if fy else None), net_income=per(q / 10, fy / 10 if fy else None))
    bs = NS(total_assets=per(5000.0), stockholders_equity=per(2000.0), total_debt=per(100.0))
    cf = NS(operating_cash_flow=per(q / 5, fy / 5 if fy else None), free_cash_flow=per(q / 8, fy / 8 if fy else None))
    er = NS(period_ending_date=NS(three_months=datetime(pe.year, pe.month, pe.day)),
            file_date=NS(three_months=datetime(fd.year, fd.month, fd.day)), accession_number=NS(three_months="0001-%02d-000001" % (fd.year % 100)))
    return NS(symbol=Sym(sid), has_fundamental_data=True, price=50.0, adjusted_price=50.0,
              company_reference=NS(company_id=cid), asset_classification=NS(morningstar_sector_code=311),
              earning_reports=er, financial_statements=NS(income_statement=inc, balance_sheet=bs, cash_flow_statement=cf))


def test_x991_snapshot_pipeline_on_fake_fundamentals(monkeypatch):
    from datetime import date, timedelta
    ai = types.ModuleType("AlgorithmImports")
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    hm = types.ModuleType("qr_harness")
    hm._attr = lambda o, n, d=None: getattr(o, n, d)

    class QRAlgorithm:
        def __init__(self):
            self.qr = {"end": "2017-12-31"}
            self.qr_params = {}
            self.qr_sec = types.SimpleNamespace(feed=lambda *a, **k: None)
            self.qr_sic = types.SimpleNamespace(sic_on=lambda sid, d: 3570 if sid != "B" else 6798,
                                                t={"A": [(date(2009, 1, 5), 3570)], "B": [(date(2009, 1, 5), 6798)]})
            self.qr_timing_holds = self.qr_quarantine_releases = self.qr_restatement_blocks = {}
            self.qr_field_releases = {}
            self.msgs = []
            self._qr_log_budget = 0

        def _qr_log(self, line):
            self.msgs.append(line)

        def on_data(self, data):
            pass

        def _qr_select(self, fl):
            self.qr_eligible = [f.symbol for f in fl]
            self.qr_eligible_info = {f.symbol: (3e9 + i, 1e7) for i, f in enumerate(fl)}
            self.qr_corrected = set()
            return []

    hm.QRAlgorithm = QRAlgorithm
    monkeypatch.setitem(sys.modules, "qr_harness", hm)
    mod = load_module(ROOT / "strategies/X991_p7_fundamental_universe_audit/main.py", "x991_test")
    a = mod.P7FundamentalAudit()
    a.qr_initialize()
    d = date(2008, 7, 1)
    while d <= date(2012, 12, 31):
        if d.weekday() < 5:
            a.time = datetime(d.year, d.month, d.day, 0, 0)
            fl = [_fund("A", "AAA", d, 0, "c1"), _fund("B", "BBB", d, 0, "c2"), _fund("A2", "AAA.B", d, 0, "c1")]
            a._qr_select(fl)
            a.prev_session = d
        d += timedelta(days=1)
    a.qr_on_end()
    out = json.loads("".join(m.split("|", 2)[2] for m in a.msgs if m.startswith("QRP7F|")))
    c = out["checks"]
    assert all(c[k] == 0 for k in c if k[0] in "CA"), c
    y = out["years"]["2011"]
    assert y["nonfin_eligible"] == 24 and y["fin_eligible"] == 12             # A, A2 operating; B a REIT
    assert y["nonfin_combo|tech+all_core+GP"] == 24 and y["nonfin_yoy|revenue"] == 24
    assert y["companies_with_multiple_eligible_classes"] == 12
    assert out["msector_changed"] == 0 and any(m.startswith("A|") for m in a.msgs)
    al = [json.loads(m[2:]) for m in a.msgs if m.startswith("A|")]
    assert all(x["ok"] for x in al)
