"""H028 host S030 (owner D217) on the fake QuantConnect environment extended to 2021 (SYNTHETIC data): canary checks
(lambda-100 fit log and call counts, H027 reproduced through the fixed path, H027 conditional rows through the fixed
path, calibration with every pair exact, synthetic A / B), null rows at lambda = 100, real mode = H028 with the
2016-2021 equality vs the recomputed H027 and gates B1-B6; upload rules; refusals."""
import hashlib
import json
import shutil
import sys
import types

import pytest

import qr_h026 as H
import qr_h027 as G
import qr_h028 as F
import qr_p7_export as E
import test_p7_export as TE
import test_p11_h026_host as T26
from conftest import ROOT

S029 = "strategies/S029_h027_exposure_controlled/main.py"
S030 = "strategies/S030_h028_fixed_shrinkage/main.py"
_CACHE = {}


def _run(monkeypatch, tmp_path, mode, **params):
    key = (mode, json.dumps(params, sort_keys=True))
    if key in _CACHE:
        return _CACHE[key]
    mod = types.ModuleType("qr_data_v21")
    mod.load_table = T26._table21
    monkeypatch.setitem(sys.modules, "qr_data_v21", mod)
    d = tmp_path / "lean30"
    d.mkdir(exist_ok=True)
    shutil.copy(ROOT / T26.X801, d / "qr_x801.py")
    shutil.copy(ROOT / T26.S028, d / "qr_s028.py")
    shutil.copy(ROOT / S029, d / "qr_s029.py")
    monkeypatch.syspath_prepend(str(d))
    for m in ("qr_x801", "qr_s028", "qr_s029"):
        monkeypatch.delitem(sys.modules, m, raising=False)
    monkeypatch.setattr(TE, "_fund", T26._fund21())

    def mutate(f, nd):
        f.security_reference = types.SimpleNamespace(security_type="ST00000001", is_depositary_receipt=False,
                                                     is_primary_share=True)
        f.company_reference.country_id = "USA"
    base = dict(spec_sha256="spec", h028_code_sha256="code", data_v21_manifest_sha256="manifest",
                h026_feature_panel_sha256=params.pop("fp", "f"), h026_response_panel_sha256=params.pop("rp", "r"),
                h027_real_wealth=params.pop("w27", 1.0), h027_real_s_wealth=params.pop("s27", 0.0),
                h027_lambda_schedule=params.pop("sch", [0.01] + [100.0] * 6))
    a = TE._host(monkeypatch, T26._market21(), path=S030, cls="H028Fixed", params=dict(base, mode=mode, **params),
                 end=T26.END, mutate=mutate, sec_off=True)
    hist = a.history

    def history(what, *x, **kw):
        if what is a.spy:
            df = hist(what, *x, **kw)
            return df.assign(open=df["close"] * 0.998)
        return hist(what, *x, **kw)
    a.history = history
    a.qr_on_end()
    parts = sorted((m for m in a.msgs if m.startswith("QRG|")), key=lambda m: int(m.split("|")[1]))
    st = json.loads("".join(m.split("|", 2)[2] for m in parts))
    blobs = {}
    for tag in ("QRHN", "QRHR"):
        ps = sorted((m for m in a.msgs if m.startswith(tag + "|")), key=lambda m: int(m.split("|")[1]))
        if ps:
            blobs[tag] = json.loads(E.unpack("".join(m.split("|", 2)[2] for m in ps)))
    _CACHE[key] = (a, st, blobs)
    return _CACHE[key]


def _pins(monkeypatch, tmp_path):
    _, st, _ = T26._run(monkeypatch, tmp_path, "canary")
    _, stn, _ = T26._run(monkeypatch, tmp_path, "null", feature_panel_sha256=st["feature_panel_sha256"], seeds=[1, 2])
    return dict(fp=st["feature_panel_sha256"], rp=stn["response_panel_sha256"])


def test_canary(monkeypatch, tmp_path):
    pins = _pins(monkeypatch, tmp_path)
    a, st, blobs = _run(monkeypatch, tmp_path, "canary", h027_null_rows_sha256="x", **pins)
    assert not blobs and st["hypothesis"] == "H028"
    assert st["equivalence"] == dict(feature_panel=True, response_panel=True)
    ck = st["canary"]
    assert ck["real_h028_result_computed"] is False
    fl = ck["fixed_lambda"]
    assert fl["ok"] and fl["fit_lambdas"] == [100.0] * 7 and fl["simulate_calls"] == 1
    assert ck["h027_real_reproduction"]["fixed_path_equals_run_world"] is True
    assert ck["h027_conditional_rows"]["fixed_path_mismatches"] == 0
    pc = ck["conditional_permutation"]
    assert pc["lowvol_changed"] == pc["other_not_donor_row"] == pc["self_matches"] == 0 and pc["responses_unchanged"]
    assert ck["lv15_picks"]["mismatch"] == 0 and ck["costs_by_hand"]["ok"] and ck["critical_value_50th_of_5000"]
    cal = ck["calibration"]
    assert cal["worlds"] == 100 and cal["exact_failures"] == [] and set(cal["tolerance"]) == {str(y) for y in F.EQUAL_YEARS}
    tol = {k: {q: float(v) for q, v in d.items()} for k, d in cal["tolerance"].items()}
    assert F.tol_sha(tol) == cal["tolerance_sha256"]
    syn = ck["synthetic"]
    assert len(syn["A"]["replicates"]) == 5 and len(syn["B"]["replicates"]) == 3
    assert all(r["repeat_identical"] for r in syn["A"]["replicates"] + syn["B"]["replicates"])
    assert a.store is None and a.C is None


def test_null_and_real_modes(monkeypatch, tmp_path):
    pins = _pins(monkeypatch, tmp_path)
    _, stc, _ = _run(monkeypatch, tmp_path, "canary", h027_null_rows_sha256="x", **pins)
    _, st, b = _run(monkeypatch, tmp_path, "null", seeds=[1, 3], **pins)
    W = b["QRHN"]["worlds"]
    assert [w[0] for w in W] == [1, 2, 3] and b["QRHN"]["fields"] == list(F.FIELDS) and st["null"]["nonfinite"] == 0
    assert all(w[F.FIELDS.index(f"lam_{y}")] == 100.0 for w in W for y in H.OUTER_YEARS)
    _, _, b2 = _run(monkeypatch, tmp_path, "null", seeds=[2, 3], **pins)
    assert b2["QRHN"]["worlds"] == W[1:]
    tol = stc["canary"]["calibration"]["tolerance"]
    real = dict(c_wealth_h028=0.1, null_result_sha256="n", threshold_commit="t", tolerance=tol,
                tolerance_sha256=stc["canary"]["calibration"]["tolerance_sha256"])
    _, st3, b3 = _run(monkeypatch, tmp_path, "real", **pins, **real)
    out = b3["QRHR"]
    assert out["reproduction_h027"]["fixed_path_equals_run_world"] is True
    eq = out["equality"]
    assert eq["same_idx"] and eq["replay_exact"]
    lam27 = out["reproduction_h027"]["lam_y"]
    if lam27[1:] == [100.0] * 6:      # the real situation: H027 chose 100 for 2016-2021 -> the exact parts must hold
        assert eq["exact_ok"] and eq["coefficients_identical"] and eq["scores_identical"] and eq["held_sets_identical"]
    else:                             # the synthetic H027 chose other lambdas -> the analysis must flag it (STOP)
        assert eq["lambda_100_both"] is False and eq["exact_ok"] is False
    assert set(out["gates"]) >= {"A1", "A2", "A3", "A4", "A5", "A6", "all", "S_WEALTH", "L_vs_lv15"}
    assert all(v["lam"] == 100.0 for v in out["coefficients"].values())
    assert out["coefficients_h027"]["2015"]["lam"] == 0.01
    assert {"lowvol_factor_regression", "sector_neutral", "march_2020", "capital_200k", "top10", "top20",
            "regime"} <= set(out["diagnostics"])
    assert len(out["y2015"]["score_spearman"]) == len(out["y2015"]["months"]) > 0
    with pytest.raises(Exception, match="differs from the pinned H026"):
        _run(monkeypatch, tmp_path, "null", seeds=[1, 2], fp="0" * 64, rp=pins["rp"])
    with pytest.raises(Exception, match="tolerance table differs"):
        _run(monkeypatch, tmp_path, "real", **pins, **dict(real, tolerance_sha256="0"))


def test_runner_uploads_s029_and_h028():
    from qresearch import run
    cfg = json.loads((ROOT / "experiments/E801-01/config.json").read_text())
    cfg = dict(cfg, strategy_id="S030", strategy_dir="strategies/S030_h028_fixed_shrinkage")
    files = run.assemble_files(cfg, None, False)
    need = {"qr_s029.py", "qr_h028.py", "qr_s028.py", "qr_h027.py", "qr_x801.py", "qr_h026.py", "qr_h024.py",
            "qr_h023.py", "qr_p7_pred.py", "qr_data_v21.py"}
    assert need <= set(files)
    assert files["qr_s029.py"] == (ROOT / S029).read_text() and files["qr_s028.py"] == (ROOT / T26.S028).read_text()
    assert "qr_params.py" in files and len(files) <= 50 and all(len(v) <= 64000 for v in files.values())


def test_result_assessment_script_runs_on_fake_real_output(monkeypatch, tmp_path):
    """The pre-registered P13_CP1_result.assess runs end to end on the synthetic real-mode output (smoke test only:
    the synthetic H027 differs from E029-05, so the status must be a STOP)."""
    sys.path.insert(0, str(ROOT / "research/phase13/cp1"))
    sys.path.insert(0, str(ROOT / "research/phase7"))
    import P13_CP1_result as RES
    from qresearch import p13h028 as P
    pins = _pins(monkeypatch, tmp_path)
    _, stc, _ = _run(monkeypatch, tmp_path, "canary", h027_null_rows_sha256="x", **pins)
    _, _, bn = _run(monkeypatch, tmp_path, "null", seeds=[1, 3], **pins)
    cal = stc["canary"]["calibration"]
    real = dict(c_wealth_h028=0.1, null_result_sha256="n", threshold_commit="t", tolerance=cal["tolerance"],
                tolerance_sha256=cal["tolerance_sha256"])
    _, st3, b3 = _run(monkeypatch, tmp_path, "real", **pins, **real)
    for k, v in dict(C_WEALTH_H028=0.1, NULL_RESULT_SHA256="n", THRESHOLD_COMMIT="t", TOLERANCE=cal["tolerance"],
                     TOLERANCE_SHA256=cal["tolerance_sha256"], ADEQUATE=True,
                     H026_FEATURE_PANEL_SHA256=pins["fp"], H026_RESPONSE_PANEL_SHA256=pins["rp"]).items():
        monkeypatch.setattr(P, k, v)
    rows = [list(r) for r in bn["QRHN"]["worlds"]] * 1667
    out = RES.assess(st3, b3["QRHR"], dict(git_commit="g", lean_version="l", qc_backtest_id="q", code_sha256="c"), rows)
    assert out["status"].startswith("STOP") and set(out["gates"]) >= {"B1", "B2", "B3", "B4", "B5", "B6", "all"}
    assert set(out["y2015"]) >= {"coefficients", "ret", "rel_spy", "rel_lv15", "maxdd", "turnover", "year_end_wealth",
                                 "score_spearman", "top15_overlap"}
    assert set(out["comparison"]) >= {"terminal_wealth", "cagr", "S_WEALTH", "years_beating_lv15", "L_2015_2017_vs_lv15"}
    json.dumps(out, default=float)
