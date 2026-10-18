"""P13-CP6 (owner D239): the R1 synthetic-validation library is synthetic-only and point-in-time, the H028-style
portfolio accounting is exact, twin worlds reproduce the real portfolio when the twins are the real stocks (both cost
modes), Mode B twins trade exactly like the real portfolio when nothing leaves the universe, matching respects sector,
caliper and minimum support, and the stored feasibility study is a development fixture only."""
import json

import numpy as np
import pytest

from conftest import ROOT
from qresearch import r1synth as G
from qresearch import r1twin as T

FEAS = ROOT / "research/phase13/cp6/P13_CP6_feasibility.json"


@pytest.fixture(scope="module")
def panel():
    return G.panel(424242, G.config(months=36))


def test_generator_prefix_truncation():
    """A shorter panel is an exact prefix of a longer one: nothing at month t depends on later draws (look-ahead)."""
    a = G.panel(11, G.config(months=20))
    b = G.panel(11, G.config(months=36))
    for x, y in zip(a, b):
        assert np.array_equal(x["ids"], y["ids"]) and np.array_equal(x["r"], y["r"])
        assert all(np.array_equal(x["pct"][d], y["pct"][d]) for d in x["pct"])
        assert all(np.array_equal(x["z"][f], y["z"][f]) for f in x["z"])


def test_generator_membership(panel):
    for m in panel:
        assert np.all(np.diff(m["ids"]) > 0)
        assert all((m["pct"][d] > 0).all() and (m["pct"][d] < 1).all() for d in m["pct"])
    for a, b in zip(panel, panel[1:]):
        gone = set(a["ids"][a["dl"]].tolist())
        assert not gone & set(b["ids"].tolist())                       # a delisted stock never returns
    entries = np.mean([len(set(b["ids"]) - set(a["ids"])) for a, b in zip(panel, panel[1:])])
    assert 30 < entries < 60                                           # calibrated to ~44 a month (E029-01 canary)


def test_real_sim_accounting(panel):
    sc = T.scores(panel, "P1")
    r = T.real_sim(panel, sc)
    assert r["commissions"] == pytest.approx(7.0 * (r["buys"] + r["sells"]))
    for m, rec in zip(panel, r["trace"]):
        held = [s for _, s in rec["held"]]
        assert len(held) <= T.K and len(set(held)) == len(held)
        secs = [int(m["sector"][np.searchsorted(m["ids"], s)]) for s in held]
        assert max(np.bincount(secs)) <= T.SECTOR_CAP if secs else True
    assert np.prod(1.0 + r["monthly"]) * T.CAPITAL == pytest.approx(r["wealth"], rel=1e-12)


def test_real_sim_truncation():
    a = G.panel(12, G.config(months=20))
    b = G.panel(12, G.config(months=36))
    ra, rb = T.real_sim(a, T.scores(a, "P1")), T.real_sim(b, T.scores(b, "P1"))
    for x, y in zip(ra["trace"][:-1], rb["trace"][:19]):
        assert x["held"] == y["held"] and x["buys"] == y["buys"]


class _Self(T.Pools):
    def get(self, t, sid):
        return np.zeros(0, np.int64), 0, self.pos[t][sid]


@pytest.mark.parametrize("mode", ["A", "B"])
def test_self_match_reproduces_real(panel, mode):
    real = T.real_sim(panel, T.scores(panel, "P1"))
    o = T.twin_sim(panel, real, _Self(panel, ("LV", "SIZE"), 10, 0.1, 3), 3, np.random.default_rng(0), mode=mode)
    assert np.allclose(o["wealth"], real["wealth"], rtol=1e-10)
    assert o["abstain"] == o["draws"]


def test_mode_b_no_churn_trades_equal_real():
    ms = G.panel(13, G.config(months=24, churn=0.0, delist_base=0.0, sector_move=0.0))
    real = T.real_sim(ms, T.scores(ms, "P1"))
    pools = T.Pools(ms, ("LV", "SIZE"), 10, 0.3, 1)
    o = T.twin_sim(ms, real, pools, 50, np.random.default_rng(1), mode="B")
    assert np.all(o["buys"] == real["buys"]) and np.all(o["sells"] == real["sells"])
    assert np.all(o["repl_inelig"] == 0) and np.all(o["repl_delist"] == 0)


def test_m3_pool_rules(panel):
    m = panel[5]
    for i in range(0, len(m["ids"]), 37):
        p, lvl = T.m3_pool(m, i, ("LV", "SIZE"), 10, 0.15, 3)
        assert i not in p.tolist() and p.size <= 10
        if lvl:
            assert p.size >= 3 and np.all(m["sector"][p] == m["sector"][i])
            d = np.sqrt(((np.column_stack([m["pct"]["LV"][p], m["pct"]["SIZE"][p]])
                          - [m["pct"]["LV"][i], m["pct"]["SIZE"][i]]) ** 2).mean(1))
            assert d.max() <= 0.15 + 1e-12
        else:
            assert p.size == 0


def test_mc_p_value():
    assert T.mc_p(10.0, [1, 2, 3]) == pytest.approx(1 / 4)
    assert T.mc_p(1.0, [1, 2, 3]) == pytest.approx(4 / 4)


def test_nw_ols_recovers_coefficients():
    rng = np.random.default_rng(3)
    x = rng.normal(size=500)
    y = 0.5 + 2.0 * x + rng.normal(scale=0.01, size=500)
    b, se, t = T.nw_ols(y, [x])
    assert b == pytest.approx([0.5, 2.0], abs=0.01) and np.all(se > 0)


@pytest.mark.skipif(not FEAS.exists(), reason="feasibility study not generated")
def test_feasibility_is_a_development_fixture():
    d = json.loads(FEAS.read_text())
    assert d["kind"].startswith("DEVELOPMENT FIXTURE") and d["synthetic_only"] and not d["rejection_rates_computed"]
    assert min(d["seeds"]) >= 900001


R3J = ROOT / "research/phase13/cp6/P13_CP6_r3_diagnostic.json"


@pytest.mark.skipif(not FEAS.exists(), reason="feasibility study not generated")
def test_feasibility_records_the_size_sensitivity_and_all_methods():
    d = json.loads(FEAS.read_text())
    assert {"n475_P1", "n950_P1", "n1900_P1"} <= set(d["universe_size_sensitivity"])
    for proc in ("P1", "P1L", "P2", "P3"):
        assert {"M1", "M2", "M3", "M4"} <= set(d["results"][proc])


@pytest.mark.skipif(not R3J.exists(), reason="R3 diagnostic not generated")
def test_r3_diagnostic_is_synthetic_and_secondary():
    d = json.loads(R3J.read_text())
    assert d["synthetic_only"] and "not R1 validation" in d["kind"] and d["n_panels"] == 200
    assert all(r["R3b_1pct"]["n"] == 200 for r in d["results"].values())
