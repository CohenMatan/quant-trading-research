"""P7-CP3 (D171): the X993 score / mechanics export host and its pure helpers (qr_p7_export).
- tech_at (sliced) equals the frozen technical_inputs / contamination on the full history (gaps, new lives, young
  listings, events before / inside the slice);
- the host runs end to end on a fake QuantConnect environment with SYNTHETIC prices and fundamentals: reviews from the
  session calendar, frozen score, disqualifier bits, one class per company, weekly states, no return in the payload."""
import json
import sys
import types
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

import qr_p7_export as E
import qr_p7_score as S
from conftest import ROOT, load_module
from test_p7_hosts import Sym, _fund, _market, _ts

FIELDS = ("close", "sma50", "sma200", "sma200_lag", "mom_12_1", "vol60", "trend_state", "broken_trend", "age")


def _series(rng, D, gaps=(), start=0):
    c = 50 * np.exp(np.cumsum(rng.normal(0.0003, 0.02, D)))
    p = c * np.exp(np.cumsum(np.full(D, 0.0001)))
    c[:start] = np.nan
    p[:start] = np.nan
    for a, b in gaps:
        c[a:b] = np.nan
        p[a:b] = np.nan
    return c, p


def test_tech_at_equals_full_history():
    rng = np.random.default_rng(11)
    D = 1500
    cases = [_series(rng, D), _series(rng, D, gaps=[(700, 780)]), _series(rng, D, gaps=[(900, 950), (1000, 1050)]),
             _series(rng, D, start=1100), _series(rng, D, gaps=[(300, 340), (500, 545), (650, 700), (800, 860)])]
    n = 0
    for C, P in cases:
        unv = [600, 1210]
        dist = [(950, 0.15), (1300, 0.05), (1320, 0.12)]
        for t in range(250, D, 37):
            ti, c, why, clear, _ = E.tech_at(C, P, t, unv, dist)
            full = S.technical_inputs(C[:t + 1], P[:t + 1], t)
            cf = S.contamination(full, unv, dist)
            assert all(ti[f] == full[f] for f in FIELDS), (t, [f for f in FIELDS if ti[f] != full[f]])
            assert (ti["bars"] >= S.MIN_HISTORY) == (full["bars"] >= S.MIN_HISTORY)
            assert (c, why, clear) == cf[:3]
            n += 1
    assert n > 150


def test_fund_inputs_baseline_only_flag():
    vals = [100.0, 40.0, 10.0, 12.0, 500.0, 200.0]
    fi, why, bo = E.fund_inputs(vals, None)
    assert fi is None and bo
    fi, why, bo = E.fund_inputs([None] + vals[1:], None)
    assert fi is None and not bo
    fi, why, bo = E.fund_inputs(vals, 90.0)
    assert fi is not None and abs(fi["rev_growth"] - 1 / 9) < 1e-12 and not bo


def test_encode_roundtrip():
    rows = {"A": (0, 72, (15, 10, 7, 15, 3, 7, 0, 15)), "B": (E.BIT["H2"], None, None)}
    txt = E.encode_rows(rows, {"A": 0, "B": 1}, {"A": 2.5e7, "B": 6e6}, {"A": "BusEq", "B": "Manuf"},
                        ["BusEq", "Manuf"])
    d = E.decode_rows(E.unpack(E.pack(txt)))
    assert d[0] == dict(i=0, bits=0, adv_k=25000, ff=0, total=72, points=(15, 10, 7, 15, 3, 7, 0, 15))
    assert d[1]["total"] is None and d[1]["bits"] == E.BIT["H2"]


# ----------------------------------------------------------------------------------------------- the host
SIC = {"S05": 6798, "S06": None}
CIK = {"S07": "c7", "S08": "c7"}


def _host(monkeypatch, M):
    ai = types.ModuleType("AlgorithmImports")
    ai.Resolution = types.SimpleNamespace(DAILY="daily")
    ai.DataNormalizationMode = types.SimpleNamespace(RAW="raw", SCALED_RAW="scaled", ADJUSTED="adjusted")

    class Split:
        pass

    class Dividend:
        pass
    ai.Split, ai.Dividend = Split, Dividend
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    hm = types.ModuleType("qr_harness")
    cal = M["cal"]
    spy = Sym("SPY")
    spy_px = np.linspace(100, 250, cal.size) * (1 + 0.05 * np.sin(np.arange(cal.size) / 60.0))
    days = [date.fromisoformat(str(np.datetime64(int(x), "D"))) for x in cal]

    def rows(d0, d1):
        a = np.datetime64(d0.strftime("%Y-%m-%d")).astype(np.int64)
        b = np.datetime64(d1.strftime("%Y-%m-%d")).astype(np.int64)
        return (cal >= a) & (cal < b)

    class Hours:
        def get_next_market_open(self, t, extended):
            d = t.date()
            i = int(np.searchsorted(cal, np.datetime64(d.strftime("%Y-%m-%d")).astype(np.int64)))
            if i < cal.size and t.hour >= 10 and days[i] == d:
                i += 1
            nd = days[i] if i < cal.size else date(2018, 1, 2)
            return datetime(nd.year, nd.month, nd.day, 9, 30)

    def sic_on(sid, d):
        return SIC.get(sid, 3570)

    sic_history = {f"S{j:02d}": [["2008-01-02", SIC.get(f"S{j:02d}", 3570), CIK.get(f"S{j:02d}", f"c{j}")]]
                   for j in range(M["n"])}

    class QRAlgorithm:
        def __init__(self):
            self.qr = {"end": "2017-12-31"}
            self.qr_params = {}
            self.qr_sec = types.SimpleNamespace(feed=lambda *a, **k: None, has=lambda sid: False,
                                                sic_history=sic_history)
            self.qr_sic = types.SimpleNamespace(sic_on=sic_on)
            self.qr_timing_holds = self.qr_quarantine_releases = self.qr_restatement_blocks = {}
            self.qr_field_releases = {}
            self.spy = spy
            self.securities = {spy: types.SimpleNamespace(exchange=types.SimpleNamespace(hours=Hours()))}
            self.msgs = []
            self._qr_log_budget = 0

        def _qr_log(self, line):
            self.msgs.append(line)

        def on_data(self, data):
            pass

        def _qr_select(self, fl):
            r = int(np.searchsorted(cal, np.datetime64(self.time.strftime("%Y-%m-%d")).astype(np.int64))) - 1
            self.qr_eligible = [f.symbol for f in fl if M["alive"][r, int(f.symbol.id[1:])]]
            self.qr_eligible_info = {s: (3e9, 1e7 + int(s.id[1:]) * (1 if s.id != "S08" else 0) + 7)
                                     for s in self.qr_eligible}
            self.qr_corrected = set()
            return []

        def history(self, what, *a, **kw):
            if what is spy:
                return pd.DataFrame({"close": spy_px}, index=pd.MultiIndex.from_arrays([[spy] * cal.size, _ts(cal)]))
            if what in (Split, Dividend):
                lst, d0, d1 = a[0], a[1], a[2]
                sel = rows(d0, d1 + pd.Timedelta(days=1))
                ix_s, ix_t, recs = [], [], []
                for s in lst:
                    if s is spy:
                        continue
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
    mod = load_module(ROOT / "strategies/X993_p7_score_mechanics_export/main.py", "x993_test")
    a = mod.P7ScoreExport()
    a.qr_initialize()
    data = types.SimpleNamespace(bars=types.SimpleNamespace(count=1))
    syms = {}
    for i, d in enumerate(days):
        if d < date(2008, 7, 1):
            continue
        a.time = datetime(d.year, d.month, d.day, 16, 0)
        a.on_data(data)
        nd = d + timedelta(days=1)
        a.time = datetime(nd.year, nd.month, nd.day, 0, 0)
        fl = []
        for j in range(M["n"]):
            if not M["alive"][i, j]:
                continue
            f = _fund(f"S{j:02d}", f"T{j}", nd, 0, f"c{j}")
            f.symbol = syms.setdefault(j, f.symbol)
            fl.append(f)
        a._qr_select(fl)
    return a


def test_x993_export_on_synthetic_market(monkeypatch):
    M = _market()
    a = _host(monkeypatch, M)
    a.qr_on_end.__globals__["WEEKLY_FROM_SCORE"] = 55          # synthetic scores stay below 75: exercise the path
    a.qr_on_end()
    st = json.loads("".join(m.split("|", 2)[2] for m in sorted((m for m in a.msgs if m.startswith("QRP7S|")),
                                                                 key=lambda m: int(m.split("|")[1]))))
    blob = "".join(m.split("|", 2)[2] for m in sorted((m for m in a.msgs if m.startswith("QRP7X|")),
                                                      key=lambda m: int(m.split("|")[1])))
    cc = st["calendar_check"]
    assert cc["reviews"] == cc["expected_reviews"] == 84 and cc["reviews_match"] and cc["weekly_match"]
    assert cc["first_review"] == "2011-01-31" and cc["last_review"] == "2017-12-29"
    assert st["slice_spot_check"]["checked"] > 0 and st["slice_spot_check"]["mismatch"] == 0
    text = E.unpack(blob)
    for bad in ("return", "forward", "alpha", "future", "cagr", "sharpe"):
        assert bad not in text.lower(), bad
    pay = json.loads(text)
    sids = pay["sids"]
    assert len(pay["reviews"]) == 84 and len(pay["regimes"]) == 84
    n_scored = 0
    seen_dup = set()
    for t, tk, enc in pay["reviews"]:
        for r in E.decode_rows(enc):
            sid = sids[r["i"]]
            if sid == "S05":
                assert r["bits"] & E.BIT["H1_financial"] and r["total"] is None
            if sid == "S06":
                assert r["bits"] & E.BIT["H1_no_sic"] and r["total"] is None
            if sid in ("S07", "S08") and r["bits"] & E.BIT["duplicate_class"]:
                seen_dup.add(sid)
            if r["total"] is not None:
                n_scored += 1
                assert r["total"] == sum(r["points"]) and 0 <= r["total"] <= 100
                assert r["points"][0] in (0, 8, 15) and r["points"][7] in (0, 8, 15)
                assert not r["bits"] & (E.BIT["H1_financial"] | E.BIT["H2"] | E.BIT["H3"] | E.BIT["H5"])
    assert n_scored > 300
    assert seen_dup == {"S08"}                       # S07 has the higher ADV20 -> S08 is the removed class
    r0 = {sids[r["i"]]: r for r in E.decode_rows(pay["reviews"][0][2])}
    assert r0["S01"]["bits"] & E.BIT["H2"]           # IPO 2010: no revenue baseline recorded 12 months earlier
    assert all(x[7] in ("STRONG", "NORMAL", "WEAK", "RISK_OFF") for x in pay["regimes"])
    assert len(pay["weekly"]) == cc["expected_weekly"] and pay["candidates_ever_75"] > 0
    assert sum(len(w[2]) for w in pay["weekly"]) > 0 and any(w[3] for w in pay["weekly"])
    assert st["score_code_sha256"] == "84b67317023683da5d6f35c640e6b8adcaf42a9b9e106c0ab8183a26edb91572"


def test_runner_uploads_frozen_score_and_config_rule():
    import copy

    import pytest

    from qresearch import experiment, p7score, run
    cfg = json.loads((ROOT / "experiments/E993-01/config.json").read_text())
    experiment.validate(cfg)
    files = run.assemble_files(cfg, None, False)
    import hashlib
    assert hashlib.sha256(files["qr_p7_score.py"].encode()).hexdigest() == \
        p7score.CODE_SHA256["src/qresearch/lean/qr_p7_score.py"]
    assert {"qr_p7.py", "qr_p7_export.py", "qr_xs_panel.py", "qr_xs_diag.py"} <= set(files)
    for k, v in (("end", "2018-12-31"), ("start", "2010-01-04"), ("kind", "research")):
        bad = copy.deepcopy(cfg)
        bad[k] = v
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)
