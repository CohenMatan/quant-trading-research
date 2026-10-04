"""Phase 3 frozen evaluation plumbing (research/phase3/P3_eval.py): the published per-configuration line round-trips
into exactly the pipeline inputs, and the selection on the published precision reproduces the full-precision result.
Synthetic numbers only (no market data)."""
import importlib.util
import json
import sys

import numpy as np

from qresearch import config, p3spec

sys.path.insert(0, str(config.REPO_ROOT / "src/qresearch/lean"))
import qr_p3_grammar as G  # noqa: E402
import qr_p3_pipeline as P  # noqa: E402

spec = importlib.util.spec_from_file_location("p3_eval", config.REPO_ROOT / "research/phase3/P3_eval.py")
EV = importlib.util.module_from_spec(spec)
spec.loader.exec_module(EV)


def _world(rng):
    C = G.enumerate_configs()
    n = len(C)
    sess = np.array([214.0] + [252.0] * 6 + [251.0])
    logex = rng.normal(0.0, 0.06, (n, 8)) * sess / 252
    cost = rng.uniform(500, 2500, (n, 8))
    eqsum = rng.uniform(0.9e5, 1.6e5, (n, 8)) * sess
    notional = rng.uniform(2e5, 9e5, (n, 8))
    maxdd = np.minimum.accumulate(-rng.uniform(0.05, 0.4, (n, 8)), axis=1)
    monthly = rng.normal(0, 0.02, (n, 94))
    return C, sess, logex, cost, eqsum, notional, maxdd, monthly


def test_y_line_round_trip_and_selection_reproduced():
    rng = np.random.default_rng(5)
    C, sess, logex, cost, eqsum, notional, maxdd, monthly = _world(rng)
    g = dict(sessions=sess.tolist(), spy_maxdd=[-0.19] * 8, ew_logex=rng.normal(0, 0.03, 8).tolist())
    L = ["G|" + json.dumps(g)] + [P.y_line(c["id"], logex[i], cost[i], eqsum[i], notional[i], maxdd[i], monthly[i])
                                  for i, c in enumerate(C)]
    C2, inp, mon = EV.real_inputs(None, L)
    assert np.allclose(inp.logex, logex, rtol=1e-5, atol=1e-9)
    assert np.allclose(inp.maxdd, maxdd, atol=1e-5)
    assert np.allclose(mon, monthly, rtol=1e-5, atol=1e-9)
    ix = {c["id"]: i for i, c in enumerate(C)}
    nbg = G.neighbours(C)
    nbi = [np.array([ix[o] for o in nbg[c["id"]]], dtype=int) for c in C]
    cpx = [G.complexity(c) for c in C]
    full = P.Inputs([c["id"] for c in C], logex, cost, eqsum, notional, maxdd, sess, np.array(g["spy_maxdd"]),
                    np.array(g["ew_logex"]), list(range(2010, 2018)))
    a, b = P.world_summary(full, nbi, cpx), P.world_summary(inp, nbi, cpx)
    assert abs(a["T"] - b["T"]) <= 1e-5 or a["T"] == b["T"]
    assert a["wf"]["passed"] == b["wf"]["passed"]
    assert [r["centre"] for r in a["ranked"]] == [r["centre"] for r in b["ranked"]]


def test_null_summary_requires_every_world():
    ws = {f"null{i}": dict(T=float(i) / 100, best_ps=float(i) / 100, n_eligible=10, n_clusters=1,
                           wf=dict(passed=i % 3 == 0, total_ex_spy=0.0)) for i in range(1, 501)}
    out = EV.summarise_null(ws, 500)
    assert out["tau"] == 4.76                     # the 25th largest of 0.01 .. 5.00
    assert out["false_pass"]["repetitions"] == 500
    del ws["null7"]
    try:
        EV.summarise_null(ws, 500)
        raise AssertionError("an incomplete null must not be evaluated")
    except SystemExit:
        pass


def _fake_null_worlds(rng, n):
    out = {}
    for i in range(1, n + 1):
        T = float(rng.normal(0.02, 0.02)) if rng.random() > 0.02 else float("-inf")
        out[f"null{i}"] = dict(T=T, best_ps=T + 0.01, n_eligible=int(rng.integers(0, 200)), n_survivors=0,
                               n_clusters=int(rng.integers(0, 8)), ranked=[],
                               wf=dict(passed=bool(rng.random() < 0.3), picks=4, total_ex_spy=0.0, total_ex_ew=0.0,
                                       years=[]),
                               apparent=dict(best_s=0.1, best_s_eligible=0.08, best_total_logex=float(rng.normal(0.4, 0.1)),
                                             best_total_logex_eligible=0.3, median_total_logex=-0.1,
                                             n_beat_spy=int(rng.integers(0, 600)), n_configs=1533))
    return out


def test_null_and_real_evaluation_end_to_end(tmp_path, monkeypatch):
    """The whole frozen evaluation on synthetic published lines: null threshold and report first, then the real
    world against it (decision quantities from the pipeline; reporting tables written)."""
    rng = np.random.default_rng(9)
    nulls = _fake_null_worlds(rng, 600)
    names = list(nulls)
    per_run = {f"E018-{k + 1:02d}": {n: nulls[n] for n in names[100 * k:100 * (k + 1)]} for k in range(5)}
    per_run["E018-06"] = {f"block{1000 + i}": w for i, w in enumerate(nulls[n] for n in names[500:])}
    C, sess, logex, cost, eqsum, notional, maxdd, monthly = _world(rng)
    logex[:40] += 0.02                                       # a few configurations with a planted lift
    g = dict(sessions=sess.tolist(), spy_maxdd=[-0.19] * 8, ew_logex=rng.normal(0, 0.03, 8).tolist())
    ix = {c["id"]: i for i, c in enumerate(C)}
    nbg = G.neighbours(C)
    nbi = [np.array([ix[o] for o in nbg[c["id"]]], dtype=int) for c in C]
    full = P.Inputs([c["id"] for c in C], logex, cost, eqsum, notional, maxdd, sess, np.array(g["spy_maxdd"]),
                    np.array(g["ew_logex"]), list(range(2010, 2018)))
    summ = P.world_summary(full, nbi, [G.complexity(c) for c in C])
    real = ["G|" + json.dumps(g), "W|real|" + json.dumps(summ, default=float)] + [
        P.y_line(c["id"], logex[i], cost[i], eqsum[i], notional[i], maxdd[i], monthly[i]) for i, c in enumerate(C)]

    def fake_lines(exp):
        if exp == "E018-07":
            return real
        return ["W|" + n + "|" + json.dumps(w, default=float) for n, w in per_run[exp].items()]

    monkeypatch.setattr(EV, "lines", fake_lines)
    monkeypatch.setattr(EV, "spy_growth", lambda *a, **k: (2.77, 7.84))
    monkeypatch.setattr(EV, "NULL_OUT", tmp_path / "null.json")
    monkeypatch.setattr(EV, "REAL_OUT", tmp_path / "real.json")
    monkeypatch.setattr(EV, "NULL_TABLE", tmp_path / "null.csv")
    monkeypatch.setattr(EV, "REAL_TABLE", tmp_path / "real.csv.gz")
    monkeypatch.setattr(EV, "_provenance", lambda e: {"experiment": e})
    monkeypatch.setattr(EV, "_block_present", lambda: True)
    nul = EV.run_null()
    p = nul["primary"]
    assert p["stages"]["worlds"] == 500 and p["tau"] == p3spec.tau_of(p["T"])
    assert "fake_winners" in p and p["fake_winners"]["best_terminal_wealth_ratio"]["n"] == 500
    assert nul["secondary_block"]["stages"]["worlds"] == 100
    out = EV.run_real()
    assert out["configurations"] == 1533 and out["Q1"] == p3spec.q1(summ["T"], p["T"])
    assert len(out["ranked"]) <= 3 and len(out["promotion"]["finalists_for_lean_verification"]) <= 2
    assert out["gates"]["eligible"] == out["n_eligible"]
    import csv as _csv
    import gzip as _gz
    rows = list(_csv.DictReader(_gz.open(tmp_path / "real.csv.gz", "rt")))
    assert len(rows) == 1533 and {r["id"] for r in rows} == {c["id"] for c in C}
