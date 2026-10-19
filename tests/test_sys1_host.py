"""SYS-1 host S032 (owner D252) on the fake QuantConnect environment extended to 2021 (SYNTHETIC data, synthetic SPLV /
USMV): canary C1-C7 (no SYS-1 arm result), the evaluation (every arm, both slippages, BM-X, sleeve comparison) and its
STOP conditions (frozen reproduction, SPLV data), the pre-registered offline canary / evaluation rules on the fake
output, the runner upload rule (49 files, no chart modules) and the S032 config rule."""
import json
import math
import shutil
import sys
import types

import numpy as np
import pandas as pd
import pytest

import qr_sys1 as Y
import qr_p7_export as E
import test_p7_export as TE
import test_p7_hosts as TH
import test_p11_h026_host as T26
import test_p13_h028_host as T30
from conftest import ROOT

S032 = "strategies/S032_sys1_account/main.py"
ETF_ID = {"SPLV": "SPLV UWBCA8CFMB1H", "USMV": "USMV V0WRDXSSH205"}
_CACHE = {}


def _etf_series(cal, spy_px, tk):
    D = cal.size
    t = np.arange(D)
    c = (0.5 if tk == "SPLV" else 0.4) * spy_px * (1 + 0.02 * np.cos(t / 45.0))
    first = int(np.searchsorted(cal, np.datetime64("2011-05-05" if tk == "SPLV" else "2011-10-18").astype(np.int64)))
    alive = t >= first
    if tk == "USMV":                    # a 10-session hole in 2016: USMV fails C4 (diagnostic only)
        g = int(np.searchsorted(cal, np.datetime64("2016-03-01").astype(np.int64)))
        alive[g:g + 10] = False
    divs = [(r, 0.25, float(c[r - 1])) for r in range(first + 40, D, 63)]
    return c, c * 0.999, alive, divs


def _wrap(a, M, bad_splv=False):
    ai = sys.modules["AlgorithmImports"]
    cal = M["cal"]
    hist = a.history
    syms = {}

    def create(tk, *x):
        return syms.setdefault(tk, TH.Sym(ETF_ID.get(tk, tk)))
    ai.Symbol.create = staticmethod(create)
    spy_px = hist(a.spy, None, None)["close"].to_numpy(dtype=float)
    etf = {}
    for tk in ETF_ID:
        c, o, alive, divs = _etf_series(cal, spy_px, tk)
        if tk == "SPLV" and bad_splv:
            alive[int(np.searchsorted(cal, np.datetime64("2018-06-01").astype(np.int64))):][:3] = False
        etf[ETF_ID[tk]] = (c, o, alive, divs)

    def rows(d0, d1):
        lo = np.datetime64(d0.strftime("%Y-%m-%d")).astype(np.int64)
        hi = np.datetime64(d1.strftime("%Y-%m-%d")).astype(np.int64)
        return (cal >= lo) & (cal <= hi)               # inclusive, as the fake SPY history (whole calendar)

    def history(what, *x, **kw):
        if what is a.spy or (isinstance(what, list) and what and what[0] is a.spy):
            df = hist(a.spy, *x, **kw)
            return df.assign(open=df["close"] * 0.998)
        if isinstance(what, list) and what and what[0].id in etf:
            c, o, alive, _ = etf[what[0].id]
            ok = alive & rows(x[0], x[1])
            return pd.DataFrame({"open": o[ok], "close": c[ok]},
                                index=pd.MultiIndex.from_arrays([[what[0]] * int(ok.sum()), TH._ts(cal[ok])]))
        if what in (ai.Split, ai.Dividend) and x[0] and x[0][0].id in etf:
            s = x[0][0]
            sel = rows(x[1], x[2] + pd.Timedelta(days=1))
            evs = [] if what is ai.Split else [e for e in etf[s.id][3] if sel[e[0]]]
            if not evs:
                return pd.DataFrame({"value": [0.0]}, index=pd.MultiIndex.from_arrays([[s], [pd.Timestamp(x[1])]]))
            return pd.DataFrame([dict(distribution=e[1], referenceprice=e[2]) for e in evs],
                                index=pd.MultiIndex.from_arrays([[s] * len(evs),
                                                                 [pd.Timestamp(np.datetime64(int(cal[e[0]]), "D"))
                                                                  for e in evs]]))
        return hist(what, *x, **kw)
    a.history = history


def _run(monkeypatch, tmp_path, sys1_mode, bad_splv=False, **params):
    key = (sys1_mode, bad_splv, json.dumps(params, sort_keys=True))
    if key in _CACHE:
        return _CACHE[key]
    mod = types.ModuleType("qr_data_v21")
    mod.load_table = T26._table21
    monkeypatch.setitem(sys.modules, "qr_data_v21", mod)
    d = tmp_path / "lean32"
    d.mkdir(exist_ok=True)
    shutil.copy(ROOT / T26.X801, d / "qr_x801.py")
    shutil.copy(ROOT / T26.S028, d / "qr_s028.py")
    shutil.copy(ROOT / T30.S029, d / "qr_s029.py")
    shutil.copy(ROOT / T30.S030, d / "qr_s030.py")
    monkeypatch.syspath_prepend(str(d))
    for m in ("qr_x801", "qr_s028", "qr_s029", "qr_s030"):
        monkeypatch.delitem(sys.modules, m, raising=False)
    monkeypatch.setattr(TE, "_fund", T26._fund21())
    real_load = TE.load_module

    def load(path, name):                       # the fake AlgorithmImports gains Symbol / SecurityType / Market
        ai = sys.modules["AlgorithmImports"]
        ai.Symbol = type("Symbol", (), {})
        ai.SecurityType = types.SimpleNamespace(EQUITY="equity")
        ai.Market = types.SimpleNamespace(USA="usa")
        return real_load(path, name)
    monkeypatch.setattr(TE, "load_module", load)

    def mutate(f, nd):
        f.security_reference = types.SimpleNamespace(security_type="ST00000001", is_depositary_receipt=False,
                                                     is_primary_share=True)
        f.company_reference.country_id = "USA"
    tol = params.pop("tolerance")
    base = dict(mode="real", spec_sha256="spec", h028_code_sha256="code", data_v21_manifest_sha256="manifest",
                h026_feature_panel_sha256=params.pop("fp"), h026_response_panel_sha256=params.pop("rp"),
                h027_real_wealth=1.0, h027_real_s_wealth=0.0, h027_lambda_schedule=[0.01] + [100.0] * 6,
                c_wealth_h028=0.1, null_result_sha256="n", threshold_commit="t", tolerance=tol["tolerance"],
                tolerance_sha256=tol["tolerance_sha256"], sys1_mode=sys1_mode, sys1_protocol_sha256="p",
                sys1_code_sha256="c")
    base.update(params)
    M = T26._market21()
    a = TE._host(monkeypatch, M, path=S032, cls="SYS1Account", params=base, end=T26.END, mutate=mutate, sec_off=True)
    _wrap(a, M, bad_splv)
    a.qr_on_end()

    def block(tag):
        ps = sorted((m for m in a.msgs if m.startswith(tag + "|")), key=lambda m: int(m.split("|")[1]))
        return "".join(m.split("|", 2)[2] for m in ps)
    st = json.loads(block("QRG"))
    q = block("QRSY")
    out = (a, st, json.loads(E.unpack(q)) if q else None, q)
    _CACHE[key] = out
    return out


def _fixtures(monkeypatch, tmp_path):
    pins = T30._pins(monkeypatch, tmp_path)
    _, stc, _ = T30._run(monkeypatch, tmp_path, "canary", h027_null_rows_sha256="x", **pins)
    cal = stc["canary"]["calibration"]
    return dict(pins, tolerance=dict(tolerance=cal["tolerance"], tolerance_sha256=cal["tolerance_sha256"]))


FROZEN_DUMMY = dict(frozen_h028=dict(wealth=1.0, commissions=1.0, buys=1, sells=1, slippage=1.0),
                    frozen_spy_wealth=1.0, frozen_spy_wealth_200k=1.0, frozen_lv15_wealth=1.0)


def test_canary_checks_and_no_arm_result(monkeypatch, tmp_path):
    fx = _fixtures(monkeypatch, tmp_path)
    a, st, blob, q = _run(monkeypatch, tmp_path, "canary", **fx, **FROZEN_DUMMY)
    assert blob is None and not q and st["sys1_mode"] == "canary"
    ck = st["canary"]
    assert ck["sys1_arm_result_computed"] is False
    assert st["equivalence"] == dict(feature_panel=True, response_panel=True)
    assert ck["C1"]["engine_equals_frozen_simulate"] is True and ck["C1"]["decision_months"] == 84
    assert ck["C1"]["ok"] is False                       # dummy frozen values: the reproduction check must fail
    assert ck["C2"]["equals_spy_simulate_100k"] and ck["C2"]["equals_spy_simulate_200k"]
    assert ck["C3"]["engine_equals_frozen_lv15"] is True
    c4 = ck["C4"]
    assert c4["splv"]["ok"] and c4["spy"]["ok"] and not c4["usmv"]["ok"] and c4["usmv"]["missing_rows"] == 10
    assert c4["splv"]["distributions"] > 0 and c4["splv"]["window"][0] < "2014-12-31"
    assert st["y_etf"]["splv"]["symbol"] == ETF_ID["SPLV"]
    assert ck["C5"]["ok"] and len(ck["C5"]["random"]) == 6 and len(ck["C5"]["etf"]) == 2 and len(ck["C5"]["zero"]) == 3
    assert ck["C6"]["ok"]
    c7 = ck["C7"]
    assert c7["ok"] and c7["compared"] == 3 * (8 + 2) and c7["max_abs_diff"] <= 1e-9
    b = ck["betas"]
    assert b["stock_betas"] > 0 and b["insufficient"] < b["stock_betas"]
    assert a.store is None and a.C is None


def test_frozen_reproduction_failure_stops_the_evaluation(monkeypatch, tmp_path):
    fx = _fixtures(monkeypatch, tmp_path)
    with pytest.raises(Exception, match="frozen H028 / SPY / LV15 reproduction failed"):
        _run(monkeypatch, tmp_path, "eval", **fx, **FROZEN_DUMMY, canary_result_sha256="x")


def test_evaluation_and_offline_rules(monkeypatch, tmp_path):
    fx = _fixtures(monkeypatch, tmp_path)
    _, st0, _, _ = _run(monkeypatch, tmp_path, "canary", **fx, **FROZEN_DUMMY)
    c = st0["canary"]
    fz = dict(frozen_h028=dict(wealth=c["C1"]["wealth"], commissions=c["C1"]["commissions"], buys=c["C1"]["buys"],
                               sells=c["C1"]["sells"], slippage=c["C1"]["slippage"]),
              frozen_spy_wealth=c["C2"]["wealth_100k"], frozen_lv15_wealth=c["C3"]["wealth"],
              frozen_spy_wealth_200k=c["C2"]["wealth_200k"])
    # the canary passes in-host with the synthetic frozen references
    _, stp, _, _ = _run(monkeypatch, tmp_path, "canary", **fx, **fz)
    assert stp["canary"]["all_in_host"] is True
    a, st, out, q = _run(monkeypatch, tmp_path, "eval", **fx, **fz, canary_result_sha256="x")
    assert out is not None and st["eval"]["usmv_verified"] is False
    arms = out["arms"]
    assert set(arms) == {"A0", "A1", "A2", "A3", "BMX_A1", "BMX_A2", "BMX_A3", "D1", "D2"}
    for name, d in arms.items():
        for lab in ("s10", "s20"):
            s = d[lab]["summary"]
            assert all(v == 0 for v in s["violations"].values()), (name, lab)
            assert d[lab]["metrics"]["path"]["wealth"] == s["wealth"]
    assert arms["D1"]["s10"]["summary"]["wealth"] == c["C1"]["wealth"]
    assert arms["A0"]["s10"]["summary"]["wealth"] == c["C2"]["wealth_200k"]
    assert arms["A0"]["s20"]["summary"]["wealth"] < arms["A0"]["s10"]["summary"]["wealth"]
    al = arms["A1"]["s10"]["summary"]["alloc"]
    npos = arms["A1"]["s10"]["summary"]["stock_positions_mean"]      # tickets 0.5 x equity / 15 (synthetic: few names)
    assert abs(al["stock"]["mean"] - npos / 30) < 0.05 and al["cash"]["max"] < 0.05 and al["splv"]["max"] == 0.0
    a3 = arms["A3"]["s10"]["summary"]["alloc"]
    assert abs(a3["splv"]["median"] - 0.5) < 0.02 and a3["stock"]["max"] == 0.0
    for name in ("A1", "A2", "A3"):
        b = out["bmx"][name]["s10"]
        assert len(b["weights"]) == 84 and all(0.0 <= w <= 1.0 for w in b["weights"])
        assert [min(max(r, 0.0), 1.0) for r in b["raw"]] == b["weights"]
    sl = out["sleeve"]
    assert sl["standalone_100k"]["wealth"] == c["C1"]["wealth"]
    assert sl["account"]["skipped_min"] == 0 and sl["account"]["tickets"]["min"] >= Y.MIN_TICKET
    assert len(out["daily"]["A1"]) == len(out["days"])
    assert arms["A1"]["s10"]["overlap"]["mean_overlap"] >= 0.0
    # the pre-registered offline evaluation rules on this output
    sys.path.insert(0, str(ROOT / "research/longhorizon/sys1"))
    sys.path.insert(0, str(ROOT / "research/phase7"))
    import SYS1_eval as EV
    bad = EV.violations_zero(arms)
    assert bad == {}
    fs, f5, lr = EV.screens(arms, "A1", True, True, True, bad)
    assert set(fs) == {"FS-1", "FS-2", "FS-3", "FS-4", "FS-5"} and fs["FS-1"] is True
    assert abs(sum(lr.values()) - f5["total"]) < 1e-12 and set(lr) == set(EV.YEARS)
    assert EV.classify(dict(fs, **{"FS-1": False})) == "NOT EXECUTABLE"
    assert EV.classify({k: True for k in fs}) == "NOT FALSIFIED — DEVELOPMENT-CONSISTENT"
    assert EV.classify(dict({k: True for k in fs}, **{"FS-6": False})) == "NOT SUPPORTED"
    d = EV.describe(arms, out["bmx"], "A1", "s10")
    assert {"vs_A0", "vs_BMX", "bmx", "overlap"} <= set(d) and d["vs_A0"]["rolling_36m"]["windows"] == 85 - 36
    for n in arms:
        EV.describe(arms, out["bmx"], n, "s20")
    json.dumps(d, default=float)


def test_splv_failure_stops_the_evaluation(monkeypatch, tmp_path):
    fx = _fixtures(monkeypatch, tmp_path)
    _, st0, _, _ = _run(monkeypatch, tmp_path, "canary", **fx, **FROZEN_DUMMY)
    c = st0["canary"]
    fz = dict(frozen_h028=dict(wealth=c["C1"]["wealth"], commissions=c["C1"]["commissions"], buys=c["C1"]["buys"],
                               sells=c["C1"]["sells"], slippage=c["C1"]["slippage"]),
              frozen_spy_wealth=c["C2"]["wealth_100k"], frozen_lv15_wealth=c["C3"]["wealth"],
              frozen_spy_wealth_200k=c["C2"]["wealth_200k"])
    with pytest.raises(Exception, match="SPLV failed its historical-data requirements"):
        _run(monkeypatch, tmp_path, "eval", bad_splv=True, **fx, **fz, canary_result_sha256="x")


def test_fs5_rule():
    sys.path.insert(0, str(ROOT / "research/longhorizon/sys1"))
    sys.path.insert(0, str(ROOT / "research/phase7"))
    import SYS1_eval as EV
    base = {y: 0.01 for y in EV.YEARS}
    assert EV.fs5(base)["ok"]
    assert not EV.fs5({**base, 2020: 0.2})["ok"]                       # one year > 50% of the sum
    assert not EV.fs5({**base, 2015: -0.02, 2016: -0.01})["ok"]         # 2015-2017 sum <= 0
    assert not EV.fs5({y: -0.01 for y in EV.YEARS})["ok"]
    r = EV.rolling_ahead([1, 2, 3, 4], [1, 1, 5, 5], n=1)
    assert r == dict(windows=3, share_ahead=2 / 3)


def test_runner_uploads_49_files_without_chart_modules():
    from qresearch import run
    cfg = json.loads((ROOT / "experiments/E801-01/config.json").read_text())
    cfg = dict(cfg, strategy_id="S032", strategy_dir="strategies/S032_sys1_account")
    files = run.assemble_files(cfg, None, False)
    assert files["qr_s030.py"] == (ROOT / T30.S030).read_text()
    assert files["qr_sys1.py"] == (ROOT / "src/qresearch/lean/qr_sys1.py").read_text()
    assert files["qr_s029.py"] == (ROOT / T30.S029).read_text()
    assert not {"qr_chart.py", "qr_h020_diag.py", "qr_h020_panel.py"} & set(files)
    assert "qr_h020_stats.py" in files and "qr_p7_pred.py" in files
    assert len(files) == 49 and all(len(v) <= 64000 for v in files.values())
    text = (ROOT / S032).read_text()
    assert "qr_h020" not in text and "qr_chart" not in text


def test_canary_assessment_rules_on_fake_output(monkeypatch, tmp_path):
    """The pre-registered SYS1_canary.assess on the synthetic canary output: every mandatory check passes with the
    synthetic frozen references; a dummy reference, a QRSY line, a wrong ETF id or a failed run each fail it."""
    sys.path.insert(0, str(ROOT / "research/longhorizon/sys1"))
    sys.path.insert(0, str(ROOT / "research/phase7"))
    import SYS1_canary as CA
    from qresearch import sys1 as P
    fx = _fixtures(monkeypatch, tmp_path)
    _, st0, _, _ = _run(monkeypatch, tmp_path, "canary", **fx, **FROZEN_DUMMY)
    c = st0["canary"]
    fz = dict(frozen_h028=dict(wealth=c["C1"]["wealth"], commissions=c["C1"]["commissions"], buys=c["C1"]["buys"],
                               sells=c["C1"]["sells"], slippage=c["C1"]["slippage"]),
              frozen_spy_wealth=c["C2"]["wealth_100k"], frozen_lv15_wealth=c["C3"]["wealth"],
              frozen_spy_wealth_200k=c["C2"]["wealth_200k"])
    _, st, _, _ = _run(monkeypatch, tmp_path, "canary", **fx, **fz)
    st = json.loads(json.dumps(st))
    st.setdefault("max_rss_mb", 1.0)
    monkeypatch.setattr(P, "FROZEN_H028", fz["frozen_h028"])
    monkeypatch.setattr(P, "FROZEN_SPY_WEALTH", fz["frozen_spy_wealth"])
    monkeypatch.setattr(P, "FROZEN_LV15_WEALTH", fz["frozen_lv15_wealth"])
    res = dict(status="completed", provenance=dict(failure_stage=""))
    checks, extra = CA.assess(st, [], res, True)
    assert all(checks.values()), {k: v for k, v in checks.items() if not v}
    assert extra["usmv_c4"] is False
    assert not CA.assess(st, ["QRSY|0|x"], res, True)[0]["no_sys1_arm_result"]
    assert not CA.assess(st, [], dict(status="failed", provenance=dict(failure_stage="run")), True)[0][
        "C9_compliance_completed"]
    bad = json.loads(json.dumps(st))
    bad["y_etf"]["splv"]["symbol"] = "SPLV X"
    assert not CA.assess(bad, [], res, True)[0]["C4_spy_and_splv_data"]
    _, stb, _, _ = _run(monkeypatch, tmp_path, "canary", **fx, **FROZEN_DUMMY)
    assert not CA.assess(json.loads(json.dumps(dict(stb, max_rss_mb=1.0))), [], res, True)[0]["C1_standalone_h028_exact"]
