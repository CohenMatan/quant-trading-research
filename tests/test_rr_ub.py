"""Universe Baseline Audit UB-1 (owner D263): the pure statistics module qr_ub on SYNTHETIC records (gap, censoring,
survivorship bias with bootstrap bounds, split / timing / staleness tests, no identifiers in the output), the
offline gate rule UB_eval, the X804 host on a fake QuantConnect environment, the runner upload guard / rule and the
X804 config rule."""
import json
import sys
import types
from collections import deque
from datetime import date, datetime, timedelta

import numpy as np
import pytest

import qr_ub as U
from conftest import ROOT, load_module

sys.path.insert(0, str(ROOT / "research/rr/universe_baseline"))
import UB_eval as EV  # noqa: E402


def _points():
    pts = []
    for y in range(1999, 2022):
        for m in range(1, 13):
            if (y, m) < (1999, 2) or (y, m) > (2021, 11):
                continue
            ny, nm = (y + (m == 12), m % 12 + 1)
            pts.append((y, m, date(ny, nm, 1).toordinal()))
    return pts


def _synthetic(n_e=60, n_m=10, n_inv=6, n_nc=4, n_nx=5, unr_exit=True, split=True, lead=False, death=100):
    """E: vendor cap >= $2B; M: no vendor cap, valid S (R >= $2B); M_inv: no S; N_c: common earlier then no
    fundamentals; N_x: never common. Unrepaired names (M_inv, N_c) delist after 30 months if unr_exit."""
    a = U.Audit()
    pts = _points()
    final = pts[-1][2]
    life = {}
    for i in range(n_e):
        life[f"E{i}"] = final if i % 10 else pts[death][2]        # a tenth of E delist (point 100 = 2007)
    for i in range(n_m):
        life[f"M{i}"] = final
    for i in range(n_inv):
        life[f"I{i}"] = pts[30][2] if unr_exit else final
    for i in range(n_nc):
        life[f"C{i}"] = pts[30][2] if unr_exit else final
    for i in range(n_nx):
        life[f"X{i}"] = final
    for kk, (y, m, call) in enumerate(pts):
        rows = []
        for key, end in life.items():
            if call > end:
                continue
            a.observe(key, call)
            adv = 5e7
            px = 50.0
            if key[0] == "E":
                S = 1e8
                SF = 1.0
                if split and key == "E1" and kk >= 50:
                    px = 25.0                                    # 2:1 split at point 50: raw price halves
                if split and key == "E1" and kk < 50:
                    SF = 0.5
                mc = S * px * SF
                if lead and key == "E2" and kk >= 40:
                    S = 1.2e8                                    # shares change at 40; vendor follows at 41
                if lead and key == "E2":
                    mc = (1.2e8 if kk >= 41 else 1e8) * px * SF
                if key == "E3" and kk >= 60:
                    S, mc = 1.1e8, 1.1e8 * px * SF               # a same-month share change
                rows.append((key, U.CAT_A, mc, S, SF, px, adv, True))
            elif key[0] == "M":
                rows.append((key, U.CAT_M, 0.0, 6e7, 1.0, px, adv, False))
            elif key[0] == "I":
                rows.append((key, U.CAT_M, 0.0, None, 1.0, px, adv, False))
            elif key[0] == "C":
                if kk < 10:
                    rows.append((key, U.CAT_A, 3e9, 6e7, 1.0, px, adv, True))
                else:
                    rows.append((key, U.CAT_N, 0.0, None, None, px, adv, False))
            else:
                rows.append((key, U.CAT_N, 0.0, None, None, px, adv, False))
        a.audit_point(y, m, call, rows)
    return a


def test_gap_censoring_and_bias():
    res = U.Audit.summarize(_synthetic())
    assert res["audit_points"] == len(_points()) and res["first_point"] == "1999-02" and res["last_point"] == "2021-11"
    y = res["years"]["2000"]
    c = y["counts"]
    # 54 alive E (6 die at point 100 = 2007), 10 repaired, 6 + 4 unrepaired in 2000
    assert c["R2B"]["securities"] == 10 and c["M_inv"]["securities"] == 6 and c["Nc"]["securities"] == 4
    assert c["Nx"]["securities"] == 5
    # gap A counts every M + N_c name; gap B only the unrepaired ones
    nE = c["E"]["stock_months"]
    assert y["gap_A"] == pytest.approx(round((10 + 6 + 4) * 12 / (nE + (10 + 6 + 4) * 12), 6))
    assert y["gap_B"] == pytest.approx(round((6 + 4) * 12 / (nE + 10 * 12 + (6 + 4) * 12), 6))
    # unrepaired names all exit within 24 months in 2000: positive bias with a positive lower bound
    sv = y["survivorship"]
    assert sv["horizon"] == 24 and sv["exit_rates"]["UB"]["rate"] == 1.0
    assert sv["bias_B"]["point"] > 0 and sv["bias_B"]["ci_b"][0] > 0
    # censoring: 2020 uses 12 months, 2021 is unassessable, alive-at-end names never count as exits
    assert res["years"]["2020"]["survivorship"]["horizon"] == 12
    assert res["years"]["2021"]["survivorship"]["horizon"] is None
    assert res["years"]["2015"]["survivorship"]["exit_rates"]["R2B"]["exits"] == 0
    # no identifier leaves the module
    txt = json.dumps(res)
    assert not any(s in txt for s in ('"E1"', '"M0"', '"I0"', '"C0"', '"X0"'))


def test_no_bias_when_unrepaired_names_survive():
    res = U.Audit.summarize(_synthetic(unr_exit=False))
    b = res["years"]["2000"]["survivorship"]["bias_B"]
    assert b["point"] <= 0.0


def test_split_and_timing_tests():
    res = U.Audit.summarize(_synthetic(lead=True))
    v = res["validity"]
    assert v["V1"]["2000"]["within_2pct"] == 1.0 and v["V1"]["2000"]["threshold_agree"] == 1.0
    v2 = v["V2"]["W0"]
    assert v2["events"] == 1 and v2["restated"] == 1 and v2["raw_like"] == 0
    assert v2["r_events"] == 1 and v2["r_continuous"] == 1
    v3 = v["V3"]["W0"]
    assert v3["events"] == 2 and v3["lead"] == 1 and v3["same"] == 1   # E2 leads the vendor cap; E3 same month
    v3b = v["V3"]["W1"]
    assert v3b["events"] == 0
    assert v["V5"]["W0"]["S_present"] < 1 and v["V5"]["W0"]["R_valid"] < 1


def test_raw_like_split_detected():
    a = U.Audit()
    pts = _points()[:4]
    for kk, (y, m, call) in enumerate(pts):
        S = 1e8 if kk < 2 else 2e8            # PIT (unrestated) share count doubles at the split
        SF = 0.5 if kk < 2 else 1.0
        px = 50.0 if kk < 2 else 25.0
        a.observe("Z", call)
        a.audit_point(y, m, call, [("Z", U.CAT_A, 1e8 * 50.0, S, SF, px, 6e7, True)])
    v2 = U.Audit.summarize(a)["validity"]["V2"]["W0"]
    assert v2["events"] == 1 and v2["raw_like"] == 1 and v2["restated"] == 0


def test_staleness_and_flat_life():
    res = U.Audit.summarize(_synthetic())
    v4 = res["validity"]["V4"]["W0"]
    assert v4["flat_M"][0] > 0 and v4["flat_M"][1] == v4["flat_M"][0]     # synthetic M shares never change
    assert v4["stale_R2B"] == pytest.approx(1 - 17 / 131, abs=0.02)      # stale after 18 months of W0 (131 points)


def _lines(res):
    out = ["UB|meta|" + json.dumps({k: v for k, v in res.items() if k not in ("years", "validity", "pre2010")})]
    out += [f"UB|year|{y}|" + json.dumps(r) for y, r in res["years"].items()]
    out += ["UB|validity|" + json.dumps(res["validity"]), "UB|pre2010|" + json.dumps(res["pre2010"])]
    return out


def test_eval_parse_and_outcomes():
    res = U.Audit.summarize(_synthetic())
    back = EV.parse(_lines(res))
    assert back["years"]["2000"] == json.loads(json.dumps(res["years"]["2000"]))
    ev = EV.evaluate(back)
    # gaps here are far above 3% and the unrepaired names all delist: FAIL in both windows
    assert ev["windows"]["W0"]["outcome"] == "FAIL" and ev["windows"]["W1"]["outcome"] == "FAIL"
    # a clean market: no missing caps at all -> PASS-A in W1 (pre-2010 dead-company test fails in W0: no deaths 1999)
    clean = U.Audit.summarize(_synthetic(n_m=0, n_inv=0, n_nc=0))
    ev2 = EV.evaluate(EV.parse(_lines(clean)))
    assert ev2["windows"]["W1"]["outcome"] == "PASS-A"
    assert ev2["windows"]["W1"]["view_A"]["unassessable_years"] == ["2021"]
    assert ev2["windows"]["W0"]["outcome"] == "PASS-A" and ev2["windows"]["W0"]["pre2010"]["A"]["dead"]["share"] == 0.1
    # no 1999 member disappears before 2010 (deaths only in 2015): the dead-company test fails W0
    late = U.Audit.summarize(_synthetic(n_m=0, n_inv=0, n_nc=0, death=200))
    ev3 = EV.evaluate(EV.parse(_lines(late)))
    assert ev3["windows"]["W0"]["outcome"] == "FAIL" and not ev3["windows"]["W0"]["pre2010"]["A"]["dead_ok"]


def test_eval_ambiguous_when_bound_exceeds_threshold():
    res = U.Audit.summarize(_synthetic(n_m=0, n_inv=0, n_nc=0))
    for y, r in res["years"].items():
        sv = r["survivorship"]
        if sv.get("horizon"):
            sv["bias_A"]["point"] = 0.001
            sv["bias_A"]["ci_b"] = [-0.001, 0.009]          # point within 0.5 points, upper bound above
    ev = EV.evaluate(EV.parse(_lines(res)))
    assert ev["windows"]["W1"]["outcome"] == "AMBIGUOUS"


# ------------------------------------------------------------------------------------------- X804 host (fake QC)
class _Sym:
    def __init__(self, v):
        self.id = v
        self.value = v


def _fake_host(monkeypatch, days_until=date(2000, 7, 31)):
    ai = types.ModuleType("AlgorithmImports")
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    d = np.arange(np.datetime64("1999-01-04"), np.datetime64("2001-01-01"))
    cal = [date.fromisoformat(str(x)) for x in d[np.is_busday(d)]]

    class Hours:
        def get_next_market_open(self, t, extended):
            dd = t.date()
            nxt = next(c for c in cal if c > dd or (c == dd and t.hour < 9))
            return datetime(nxt.year, nxt.month, nxt.day, 9, 30)

    hm = types.ModuleType("qr_harness")
    hm.EXCHANGES = ("NYS", "NAS")
    hm.is_us_common = lambda f, day=None: getattr(f, "common", True)

    class QRAlgorithm:
        def __init__(self):
            self.qr = {"start": "1999-01-04", "end": "2021-12-31", "experiment_id": "E804-01"}
            self._qr_u = {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20}
            self.spy = "SPY"
            self.securities = {"SPY": types.SimpleNamespace(exchange=types.SimpleNamespace(hours=Hours()))}
            self.msgs = []
            self._qr_log_budget = 0

        def _qr_log(self, line):
            self.msgs.append(line)

        def on_data(self, data):
            pass
    hm.QRAlgorithm = QRAlgorithm
    monkeypatch.setitem(sys.modules, "qr_harness", hm)
    mod = load_module(ROOT / "strategies/X804_universe_baseline/main.py", "x804_test")
    a = mod.UniverseBaseline()
    a.qr_initialize()
    syms = {n: _Sym(f"SID{n}") for n in range(8)}

    def fund(n, day):
        f = types.SimpleNamespace(symbol=syms[n], dollar_volume=2e7 if n != 6 else 1e6, price=40.0,
                                  has_fundamental_data=n != 5, market_cap=3e9 if n not in (3, 4) else 0,
                                  split_factor=1.0, security_reference=types.SimpleNamespace(exchange_id="NYS"),
                                  company_profile=types.SimpleNamespace(shares_outstanding=7.5e7 if n != 4 else 0,
                                                                        share_class_market_cap=0))
        f.common = n != 7
        return f
    data = types.SimpleNamespace(bars=types.SimpleNamespace(count=1))
    for c in cal:
        if c > days_until:
            break
        a.time = datetime(c.year, c.month, c.day, 16, 0)
        a.on_data(data)
        nd = c + timedelta(days=1)
        a.time = datetime(nd.year, nd.month, nd.day, 0, 0)
        alive = [n for n in range(8) if not (n == 2 and c > date(1999, 9, 30))]     # SID2 disappears in 1999
        a._qr_select([fund(n, nd) for n in alive])
    a.qr_on_end()
    return a


def test_x804_host_on_fake_market(monkeypatch):
    a = _fake_host(monkeypatch)
    res = EV.parse(a.msgs)
    meta = res["meta"]
    assert meta["first_point"] == "1999-02" and meta["last_point"] == "2000-07" and meta["audit_points"] == 18
    c = res["years"]["1999"]["counts"]
    # SID0/1 E; SID2 E until Sep 1999; SID3 M with shares (R = 3e9: repaired); SID4 M without shares; SID5 no
    # fundamentals but never common -> N_x; SID6 illiquid; SID7 not common
    assert c["E"]["securities"] == 3 and c["R2B"]["securities"] == 1 and c["M_inv"]["securities"] == 1
    assert c["Nx"]["securities"] == 1 and c["L"]["securities"] == 6
    assert meta["checks"]["noncommon"] > 0
    assert all(ln.startswith("UB|") for ln in a.msgs)
    assert not any("SID" in ln for ln in a.msgs)               # no identifier leaves the run
    assert res["validity"]["V1"]["1999"]["within_2pct"] == 1.0  # 7.5e7 x 40 x 1 = 3e9 = vendor cap


def test_upload_guard_and_x804_upload_rule():
    from qresearch import run
    run.check_upload({"main.py": "import json\nx = 1\n"})
    for bad in ("import zlib\n", "from base64 import b85decode\n", "x" * 64001):
        with pytest.raises(Exception):
            run.check_upload({"main.py": bad})
    with pytest.raises(Exception):
        run.check_upload({f"f{i}.py": "" for i in range(51)})
    files = run.assemble_files({"strategy_dir": "strategies/X804_universe_baseline", "experiment_id": "E804-01",
                                "start": "1999-01-04", "end": "2021-12-31", "cash": 100000,
                                "universe": {}, "costs": {}, "portfolio": {}, "params": {}}, None, False)
    assert "qr_ub.py" in files and "qr_harness.py" in files
    assert not any(n.startswith(("qr_sec_data", "qr_data_v", "qr_p7_export")) for n in files)
    run.check_upload(files)


def test_pins_and_config():
    from qresearch import experiment, rr_ub as P
    assert P.PROTOCOL_SHA256 and P.file_sha256(P.PROTOCOL) == P.PROTOCOL_SHA256
    changed = [f for f, h in P.CODE_SHA256.items() if h is None or P.file_sha256(f) != h]
    assert not changed, f"pinned UB-1 files changed: {changed}"
    sys.path.insert(0, str(ROOT / "research/rr/universe_baseline"))
    import UB_configs as C
    cfg = json.loads((ROOT / "experiments" / P.RUN / "config.json").read_text())
    experiment.validate(cfg)
    assert cfg == C.build(P.RUN)
    assert cfg["kind"] == "infrastructure" and cfg["end"] == "2021-12-31" and not cfg["universe"].get("sec_corrections")
    for bad in (dict(cfg, experiment_id="E804-03"), dict(cfg, end="2022-06-30"),
                dict(cfg, params=dict(cfg["params"], ub_protocol_sha256="x")),
                dict(cfg, universe=dict(cfg["universe"], sec_corrections=True)),
                {k: v for k, v in cfg.items() if k != "owner_approval_required"}):
        from qresearch.holdout import HoldoutLockedError
        with pytest.raises((experiment.ConfigError, HoldoutLockedError)):
            experiment.validate(bad)
