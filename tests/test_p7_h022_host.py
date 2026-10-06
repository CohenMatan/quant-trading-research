"""P7-CP5 (D177): the H022 host S023 (X994 = byte copy) on a fake QuantConnect environment with SYNTHETIC prices and
fundamentals: canary checks pass and compute no IC of the real assignment; null worlds equal the frozen qr_p7_pred
procedure; the real mode refuses a panel that differs from the null's; config / runner wiring."""
import copy
import json

import numpy as np
import pytest

import qr_p7_export as E
import qr_p7_pred as R
from conftest import ROOT
from qresearch import p7pred
from test_p7_export import _host
from test_p7_hosts import _market

S023 = "strategies/S023_h022_predictive/main.py"
X994 = "strategies/X994_h022_canary/main.py"
BASE = dict(spec_sha256=p7pred.SPEC_SHA256, pred_code_sha256=p7pred.CODE_SHA256["src/qresearch/lean/qr_p7_pred.py"])


def _chunks(msgs, tag):
    parts = sorted((m for m in msgs if m.startswith(tag + "|")), key=lambda m: int(m.split("|")[1]))
    return "".join(m.split("|", 2)[2] for m in parts)


_CACHE = {}


def _mk():
    """The P7 synthetic market plus splits (2:1, 3:1, 1:2) and mid-month delistings of several securities."""
    M = _market(n=34)
    for j, b, f in ((20, 1310, 0.5), (21, 1460, 1 / 3), (22, 1625, 2.0), (23, 1790, 0.5), (24, 1955, 0.5),
                    (25, 2110, 0.5)):
        for k in ("RAW", "O", "H", "L"):
            M[k][b:, j] *= f
        M["splits"][j] = [(b, f)]
        M["SC"][:, j] = M["RAW"][:, j]
        M["SC"][:b, j] *= f
        m = np.where(np.arange(M["cal"].size) < b, f, 1.0)
        for e, amt, ref in M["divs"][j]:
            m[:e] *= 1 - amt / ref
        M["ADJ"][:, j] = M["RAW"][:, j] * m
    for j, b in ((26, 1322), (27, 1488), (28, 1650), (29, 1811), (30, 1977)):
        M["alive"][b:, j] = False
        M["divs"][j] = [e for e in M["divs"][j] if e[0] < b - 40]      # no distribution near or after the delisting
    return M


def _run(monkeypatch, mode, **params):
    key = (mode, json.dumps(params, sort_keys=True))
    if key not in _CACHE:
        a = _host(monkeypatch, _mk(), path=S023, cls="H022Predictive", params=dict(BASE, mode=mode, **params))
        a.qr_on_end()
        _CACHE[key] = (a, json.loads(_chunks(a.msgs, "QRP7S")))
    return _CACHE[key]


def test_canary_checks_pass_and_compute_no_real_ic(monkeypatch):
    a, st = _run(monkeypatch, "canary")
    ck = st["canary"]
    assert st["decisions"] == dict(n=83, first="2011-01-31", last="2017-11-30", last_response_end="2017-12-29")
    assert ck["real_ic_computed"] is False and ck["gates_computed"] is False
    assert not any(m.startswith(("QRN|", "QRR|")) for m in a.msgs)
    tm = ck["timing"]
    assert tm["rows"] > 1000 and tm["truncated"] > 0
    for k in ("entry_not_after_t", "entry_on_or_before_t_day", "exit_outside", "value_mismatch", "status_mismatch",
              "response_end_after_last_session"):
        assert tm[k] == 0, k
    assert all(ck["event_classes"][c] > 0 for c in ("split", "dividend", "truncated", "plain")), ck["event_classes"]
    fr = ck["fresh_recomputation"]
    assert fr["checked"] > 20 and fr["agree_1e9"] == fr["checked"] == fr["status_agree"], fr
    inv = ck["response_invariance"]
    assert inv["checked"] > 50 and inv["future_changed"] == inv["past_changed"] == inv["truncation_changed"] == 0
    sc = ck["score_invariance"]
    assert len(sc["reviews"]) == 6 and sc["rows"] > 0
    assert sc["truncated_mismatch"] == sc["future_mismatch"] == sc["regime_mismatch"] == 0
    assert ck["responses_repeat_identical"]
    nm = ck["null_machinery"]
    assert nm["repeat_identical"] and nm["distinct_worlds"] > 1 and nm["synthetic_responses"]
    assert nm["tether"]["not_permutation"] == nm["tether"]["self_matches"] == 0
    assert st["coverage"]["mcap_missing"] == st["coverage"]["mom_missing"] == 0
    assert sum(st["coverage"]["status"].values()) == sum(n for _, n, _ in st["coverage"]["population"])
    assert st["modules"]["qr_p7_pred.py"] == BASE["pred_code_sha256"]
    assert st["spec_sha256"] == p7pred.SPEC_SHA256


def test_scores_are_the_x993_scores(monkeypatch):
    """The score side is the frozen X993 v1.1 export, unchanged (same review encodings)."""
    _, st = _run(monkeypatch, "canary")
    x = _host(monkeypatch, _mk())
    x.qr_on_end()
    pay = json.loads(E.unpack(_chunks(x.msgs, "QRP7X")))
    import hashlib
    assert [[r[0], hashlib.sha256(r[2].encode()).hexdigest()] for r in pay["reviews"]] == st["review_sha256"]


def test_null_worlds_equal_the_frozen_procedure(monkeypatch):
    a, st = _run(monkeypatch, "null", seeds=[1, 3])
    _, stc = _run(monkeypatch, "canary")
    assert st["panel_sha256"] == stc["panel_sha256"]
    blob = _chunks(a.msgs, "QRN")
    assert st["null"]["blob_sha256"] == __import__("hashlib").sha256(blob.encode()).hexdigest()
    pay = json.loads(E.unpack(blob))
    assert [w[0] for w in pay["worlds"]] == [1, 2, 3]
    prep = R.prepare(a.h_dates)
    for w in pay["worlds"]:
        ref = R.run_world(prep, seed=w[0])
        row = dict(zip(pay["fields"], w))
        assert row["t_ic"] == ref["t_ic"] and row["half2"] == ref["halves"][1] and row["t_inc"] == ref["t_inc"]


def test_real_mode_refuses_a_different_panel_and_matches_the_frozen_gates(monkeypatch):
    prov = dict(c_ic=2.5, threshold_commit="x" * 40, null_result_sha256="0" * 64, spec_sha256=p7pred.SPEC_SHA256)
    with pytest.raises(Exception, match="differs"):
        _run(monkeypatch, "real", panel_sha256="f" * 64, **{k: v for k, v in prov.items() if k != "spec_sha256"})
    _, stc = _run(monkeypatch, "canary")
    a, st = _run(monkeypatch, "real", panel_sha256=stc["panel_sha256"],
                 **{k: v for k, v in prov.items() if k != "spec_sha256"})
    out = json.loads(E.unpack(_chunks(a.msgs, "QRR")))
    ref = R.run_world(R.prepare(a.h_dates))
    assert out["summary"]["t_ic"] == ref["t_ic"] and out["gates"] == R.promotion(ref, 2.5)
    assert len(out["series"]) == ref["n_dates"] and "h2" in out and "h3" in out


def test_initialisation_refuses_bad_params(monkeypatch):
    for bad in (dict(BASE, mode="search"), dict(BASE, mode="null", seeds=[0, 10]),
                dict(BASE, mode="canary", pred_code_sha256="0" * 64), dict(BASE, mode="real", c_ic=2.5)):
        with pytest.raises(Exception):
            _host(monkeypatch, _market(n=4), path=S023, cls="H022Predictive", params=bad)


def test_x994_is_a_byte_copy_of_s023():
    assert (ROOT / X994).read_bytes() == (ROOT / S023).read_bytes()


def test_configs_and_runner_wiring():
    import hashlib

    from qresearch import experiment, run
    cfgs = {e: json.loads((ROOT / f"experiments/{e}/config.json").read_text())
            for e in ("E994-01", "E023-01", "E023-02", "E023-03", "E023-04", "E023-05")}
    for e, c in cfgs.items():
        experiment.validate(c)
        assert (c["strategy_id"] == "X994") == (e == "E994-01")
        assert bool(c.get("owner_approval_required")) == (e != "E994-01")
    assert [tuple(cfgs[f"E023-0{i}"]["params"]["seeds"]) for i in range(1, 6)] == list(p7pred.NULL_BATCHES)
    files = run.assemble_files(cfgs["E994-01"], None, False)
    for n in ("qr_p7_pred.py", "qr_h020_stats.py", "qr_xs.py", "qr_xs_panel.py", "qr_p7_score.py"):
        assert hashlib.sha256(files[n].encode()).hexdigest() == p7pred.CODE_SHA256[f"src/qresearch/lean/{n}"], n
    bad = copy.deepcopy(cfgs["E023-01"])
    bad["params"].update(mode="real", c_ic=2.5, threshold_commit="x", null_result_sha256="y", panel_sha256="z")
    bad["kind"], bad["split"] = "research", "IS"
    with pytest.raises(experiment.ConfigError):           # refused: no c_IC pinned
        experiment.validate(bad)
    for k, v in (("end", "2018-01-31"), ("start", "2010-01-04")):
        b2 = copy.deepcopy(cfgs["E994-01"])
        b2[k] = v
        with pytest.raises(experiment.ConfigError):
            experiment.validate(b2)
    b3 = copy.deepcopy(cfgs["E023-02"])
    b3["params"]["spec_sha256"] = p7pred.SPEC_SHA256_V1_ORIGINAL
    with pytest.raises(experiment.ConfigError):
        experiment.validate(b3)
    b4 = copy.deepcopy(cfgs["E023-03"])
    b4["params"]["seeds"] = [1, 5000]
    with pytest.raises(experiment.ConfigError):
        experiment.validate(b4)
