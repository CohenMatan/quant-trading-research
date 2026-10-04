"""Phase 3 frozen evaluation plumbing (research/phase3/P3_eval.py): the published per-configuration line round-trips
into exactly the pipeline inputs, and the selection on the published precision reproduces the full-precision result.
Synthetic numbers only (no market data)."""
import importlib.util
import json
import sys

import numpy as np

from qresearch import config

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
    ws = {f"null{i}": dict(T=float(i) / 100, wf=dict(passed=i % 3 == 0, total_ex_spy=0.0)) for i in range(1, 501)}
    out = EV.summarise_null(ws, 500)
    assert out["tau"] == 4.76                     # the 25th largest of 0.01 .. 5.00
    assert out["false_pass"]["repetitions"] == 500
    del ws["null7"]
    try:
        EV.summarise_null(ws, 500)
        raise AssertionError("an incomplete null must not be evaluated")
    except SystemExit:
        pass
