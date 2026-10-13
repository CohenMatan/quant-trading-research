"""P13-CP5 (owner D238): the H028 conditional-null structural audit is synthetic only, runs the frozen H026 / H027 /
H028 code unchanged, its donor re-mapping accounting is exact, and the stored classification follows from the stored
results under the pre-registered (amended) rule."""
import hashlib
import json
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path[:0] = [str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase13/cp5")]
import P13_CP5_audit as A  # noqa: E402

OUT = ROOT / "research/phase13/cp5/P13_CP5_audit.json"


def test_membership_no_churn_and_growth():
    mem, n = A.membership(np.random.default_rng(1), 0.09, 0.0)
    assert n == A.N_NOCHURN and all(m == list(range(A.N_NOCHURN)) for m in mem) and len(mem) == A.N_MONTHS
    mem, n = A.membership(np.random.default_rng(1), 0.09, 1.0)
    assert len(mem[0]) == A.N_FIRST and len(mem[-1]) == A.N_LAST
    assert all(m == sorted(m) and len(set(m)) == len(m) for m in mem)
    seen, back = set(mem[0]), 0
    for a, b in zip(mem, mem[1:]):
        back += len([s for s in b if s not in a and s in seen])
        seen |= set(b)
    assert back > 0                                    # earlier members do return (REENTRY_SHARE)


def test_reform_accounting_identity():
    mem, _ = A.membership(np.random.default_rng(2), 0.09, 1.0)
    c = A.reform(mem, 1)
    assert c["rows"] == c["kept"] + c["new_recipient"] + c["donor_exited"] + c["splice"]
    assert c["possible"] == c["kept"] + c["splice"]
    assert c["splice"] <= A.N_MONTHS                   # the frozen tether breaks at most one possible pair a month
    c0 = A.reform(A.membership(np.random.default_rng(2), 0.09, 0.0)[0], 1)
    assert c0["new_recipient"] == c0["donor_exited"] == 0 and c0["reform_share"] < 0.01


def test_panel_feeds_the_frozen_pipeline_and_null_keeps_lowvol():
    ms = A.panel(1, "strong", "S2_realistic_churn")
    assert len(ms) == A.N_MONTHS and ms[0]["test_year"] == 2011 and ms[-1]["test_year"] == 2021
    Xs = A.G.conditional_permuted(ms, 3)
    for m, X in zip(ms, Xs):
        assert np.array_equal(X[:, A.LV], m["X"][:, A.LV])
        assert sorted(map(tuple, X[:, list(A.G.OTHER)])) == sorted(map(tuple, m["X"][:, list(A.G.OTHER)]))
    st, w = A.run_full(ms, [m["X"] for m in ms], None)
    assert w["rec"]["lam"] == [100.0] * 7
    assert 0.0 <= st["name_turnover"] <= 1.0 and 0.0 <= st["top15_survival"] <= 1.0
    assert st["total_cost"] == pytest.approx(st["commissions"] + st["slippage"])
    assert st["commissions"] == pytest.approx(7.0 * st["trades"])


def test_structure_hand_example():
    ms = [dict(ids=[1, 2, 3, 4]), dict(ids=[1, 2, 3, 5])]
    h = dict(picks=[[1, 2], [2, 5]], trades=4, commissions=28.0, slippage=1.0, turnover=[1.0, 0.5], wealth=100.0)
    st = A.structure(ms, [np.array([4.0, 3, 2, 1]), np.array([4.0, 3, 2, 1])], h)
    assert st["new_names"] == 1 and st["name_turnover"] == pytest.approx(1 / 15)
    assert st["top15_survival"] == 0.5 and st["rank_autocorr"] == pytest.approx(1.0)


def _fake(pos):
    res = {A.MAIN: {}}
    for rg in A.REGIMES:
        res[A.MAIN][rg] = [dict(bands={k: dict(position=pos[rg][k][i], real_below_all=False) for k in A.METRICS})
                           for i in range(5)]
    return res


def test_criterion_rule():
    ok = {rg: {k: ["inside"] * 5 for k in A.METRICS} for rg in A.REGIMES}
    assert A.criterion(_fake(ok))["classification"] == "A"
    one = {rg: {k: list(v) for k, v in d.items()} for rg, d in ok.items()}
    one["strong"]["name_turnover"] = ["above", "above", "above", "inside", "inside"]
    assert A.criterion(_fake(one))["classification"] == "B"            # Amendment 1: either regime
    mix = {rg: {k: list(v) for k, v in d.items()} for rg, d in ok.items()}
    mix["moderate"]["total_cost"] = ["above", "below", "inside", "inside", "inside"]
    assert A.criterion(_fake(mix))["classification"] == "C"


@pytest.mark.skipif(not OUT.exists(), reason="audit output not generated")
def test_stored_result_consistent():
    body = json.loads(OUT.read_text())
    assert body["synthetic_only"] and body["quantconnect_runs"] == 0 and not body["holdout_accessed"]
    assert not body["returns_read"] and not body["new_null"]
    for f, h in body["frozen_code_sha256"].items():
        assert hashlib.sha256((ROOT / "src/qresearch/lean" / f).read_bytes()).hexdigest() == h
    assert A.criterion(body["results"])["classification"] == body["criterion"]["classification"]
    for scen, (p, w) in A.SIZES.items():
        for rg in A.REGIMES:
            assert len(body["results"][scen][rg]) == p and all(r["worlds"] == w for r in body["results"][scen][rg])
