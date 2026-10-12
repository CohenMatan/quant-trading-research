"""H027 host S029 (owner D213) on the fake QuantConnect environment extended to 2021 (SYNTHETIC data): memory-reduction
equivalence with the pinned H026 host S028 (identical feature / response panels, reproduction counts, H026 null rows
and real result), canary checks, conditional-null rows, real-mode gates; upload rules; refusals."""
import json
import shutil
import sys
import types

import numpy as np
import pytest

import qr_h026 as H
import qr_h027 as G
import qr_p7_export as E
import test_p7_export as TE
import test_p11_h026_host as T26
from conftest import ROOT

S029 = "strategies/S029_h027_exposure_controlled/main.py"
_CACHE = {}


def _run(monkeypatch, tmp_path, mode, **params):
    key = (mode, json.dumps(params, sort_keys=True))
    if key in _CACHE:
        return _CACHE[key]
    mod = types.ModuleType("qr_data_v21")
    mod.load_table = T26._table21
    monkeypatch.setitem(sys.modules, "qr_data_v21", mod)
    d = tmp_path / "lean29"
    d.mkdir(exist_ok=True)
    shutil.copy(ROOT / T26.X801, d / "qr_x801.py")
    shutil.copy(ROOT / T26.S028, d / "qr_s028.py")
    monkeypatch.syspath_prepend(str(d))
    for m in ("qr_x801", "qr_s028"):
        monkeypatch.delitem(sys.modules, m, raising=False)
    monkeypatch.setattr(TE, "_fund", T26._fund21())

    def mutate(f, nd):
        f.security_reference = types.SimpleNamespace(security_type="ST00000001", is_depositary_receipt=False,
                                                     is_primary_share=True)
        f.company_reference.country_id = "USA"
    base = dict(spec_sha256="spec", h027_code_sha256="code", data_v21_manifest_sha256="manifest",
                h026_feature_panel_sha256=params.pop("fp", "f"), h026_response_panel_sha256=params.pop("rp", "r"))
    a = TE._host(monkeypatch, T26._market21(), path=S029, cls="H027Conditional", params=dict(base, mode=mode, **params),
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
    for tag in ("QRGN", "QRGR"):
        ps = sorted((m for m in a.msgs if m.startswith(tag + "|")), key=lambda m: int(m.split("|")[1]))
        if ps:
            blobs[tag] = json.loads(E.unpack("".join(m.split("|", 2)[2] for m in ps)))
    _CACHE[key] = (a, st, blobs)
    return _CACHE[key]


def _h026(monkeypatch, tmp_path):
    _, st, _ = T26._run(monkeypatch, tmp_path, "canary")
    _, stn, bn = T26._run(monkeypatch, tmp_path, "null", feature_panel_sha256=st["feature_panel_sha256"], seeds=[1, 25])
    return st, stn, bn


def test_canary_equivalence_with_s028(monkeypatch, tmp_path):
    st26, stn26, bn26 = _h026(monkeypatch, tmp_path)
    rows26 = bn26["QRWN"]["worlds"]
    import hashlib
    rows_sha = hashlib.sha256(json.dumps(rows26, separators=(",", ":")).encode()).hexdigest()
    a, st, blobs = _run(monkeypatch, tmp_path, "canary", fp=st26["feature_panel_sha256"],
                        rp=stn26["response_panel_sha256"], h026_null_rows_sha256=rows_sha)
    assert not blobs
    assert st["equivalence"] == dict(feature_panel=True, response_panel=True)
    assert st["reproduction"] == st26["reproduction"]                        # H022 / H024 digests + per-decision counts
    assert st["coverage"] == st26["coverage"]
    ck = st["canary"]
    assert ck["real_h027_result_computed"] is False
    assert ck["h026_null_rows"]["equal_to_e028_04"] is True and ck["h026_null_rows"]["rows"] == rows26
    pc = ck["conditional_permutation"]
    assert pc["months"] > 0 and pc["lowvol_changed"] == pc["other_not_donor_row"] == pc["self_matches"] == 0
    assert pc["persistence_within_splice_bound"] and pc["permutation_not_exact"] == 0 and pc["responses_unchanged"]
    assert ck["lv15_picks"]["mismatch"] == 0 and ck["lv15_picks"]["months"] == 84
    assert ck["costs_by_hand"]["ok"] and ck["critical_value_50th_of_5000"]
    syn = ck["synthetic"]
    assert set(syn) >= {"A", "B", "world_s"} and len(syn["A"]["replicates"]) == 5 and len(syn["B"]["replicates"]) == 3
    assert all(r["repeat_identical"] for r in syn["A"]["replicates"] + syn["B"]["replicates"])
    names = [m[0] for m in st["memory"]]
    assert names[:4] == ["on_end_start", "after_run_state_released", "after_repair", "after_x801_build_hl_freed"]
    assert a.store is None and a.H is None and a.L is None and a.C is None      # released


def test_null_and_real_modes(monkeypatch, tmp_path):
    st26, stn26, bn26 = _h026(monkeypatch, tmp_path)
    pins = dict(fp=st26["feature_panel_sha256"], rp=stn26["response_panel_sha256"])
    _, st, b = _run(monkeypatch, tmp_path, "null", seeds=[1, 3], **pins)
    W = b["QRGN"]["worlds"]
    assert [w[0] for w in W] == [1, 2, 3] and b["QRGN"]["fields"] == list(G.FIELDS)
    assert set(b["QRGN"]["coef"]) == {"1", "2", "3"} and st["null"]["nonfinite"] == 0
    _, st2, b2 = _run(monkeypatch, tmp_path, "null", seeds=[2, 3], **pins)
    assert b2["QRGN"]["worlds"] == W[1:]                                    # batch-independent, deterministic
    # real mode = the frozen H026 real result exactly, plus LV15 and the gates
    _, _, r26 = T26._run(monkeypatch, tmp_path, "real", feature_panel_sha256=st26["feature_panel_sha256"],
                         c_wealth=0.1, null_result_sha256="n", threshold_commit="t",
                         response_panel_sha256=stn26["response_panel_sha256"])
    ref = r26["QRWR"]
    real = dict(c_wealth_conditional=0.1, null_result_sha256="n", threshold_commit="t",
                h026_real_wealth=ref["h026"]["wealth"], h026_real_s_wealth=ref["rec"]["S_WEALTH"])
    _, st3, b3 = _run(monkeypatch, tmp_path, "real", **pins, **real)
    out = b3["QRGR"]
    assert out["reproduction"]["ok"] is True
    assert out["h027"] == ref["h026"] and out["coefficients"] == ref["coefficients"]
    assert set(out["gates"]) >= {"A1", "A2", "A3", "A4", "A5", "A6", "all", "S_WEALTH", "L_vs_lv15"}
    assert {"lowvol_factor_regression", "sector_neutral", "march_2020", "capital_200k", "top10", "top20",
            "regime"} <= set(out["diagnostics"])
    assert out["lv15"]["wealth"] > 0 and set(out["years_lv15"]) == {str(y) for y in H.OUTER_YEARS}
    with pytest.raises(Exception, match="differs from the pinned H026"):
        _run(monkeypatch, tmp_path, "null", seeds=[1, 2], fp="0" * 64, rp=pins["rp"])


def test_runner_uploads_s028_and_h027():
    from qresearch import run
    cfg = json.loads((ROOT / "experiments/E801-01/config.json").read_text())
    cfg = dict(cfg, strategy_id="S029", strategy_dir="strategies/S029_h027_exposure_controlled")
    files = run.assemble_files(cfg, None, False)
    need = {"qr_s028.py", "qr_h027.py", "qr_x801.py", "qr_h026.py", "qr_h024.py", "qr_h023.py", "qr_p7_pred.py",
            "qr_data_v21.py"}
    assert need <= set(files)
    assert files["qr_s028.py"] == (ROOT / T26.S028).read_text()
    assert len(files) <= 50 and all(len(v) <= 64000 for v in files.values())
