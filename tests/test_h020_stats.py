"""H020 statistics, null and gates (src/qresearch/lean/qr_h020_stats.py). SYNTHETIC latent panels only
(research/phase5/h020_synth_panel.py): no market data, no chart of a real stock, no real return."""
import sys
from collections import Counter

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research" / "phase5"))
import h020_synth_panel as P  # noqa: E402
import qr_h020_stats as H  # noqa: E402


@pytest.fixture(scope="module")
def null_panel():
    return P.make_dates(n_dates=150, n_stocks=200, seed=3)


@pytest.fixture(scope="module")
def edge_panel():
    return P.make_dates(n_dates=150, n_stocks=200, edge_ic=0.08, rho=0.0, seed=4)


def test_fast_path_equals_reference_date_stats(edge_panel):
    prep = H.prepare(edge_panel)
    rng = np.random.default_rng(0)
    for p, d in list(zip(prep, edge_panel))[:12]:
        for ix in (None, rng.permutation(len(p["ids"]))):
            f = H.fast_date_stats(p, ix)
            Q, G = (d["Q"], d["G"]) if ix is None else (d["Q"][ix], d["G"][ix])
            r = H.date_stats(Q, G, d["mom"], d["trend"], d["y"])
            assert f["ic"] == pytest.approx(r["ic"], abs=1e-12) and f["inc"] == pytest.approx(r["inc"], abs=1e-10)
            assert np.allclose(f["g"], r["g"], equal_nan=True) and f["n"] == r["n"]
            assert f["high"] == pytest.approx(r["high"], nan_ok=True) and f["low"] == pytest.approx(r["low"], nan_ok=True)


def test_tether_is_an_exact_within_stratum_permutation_without_self_matches(null_panel):
    prep = H.prepare(null_panel)
    T = H.ChartTether(7)
    prev, kept, total, selfm = None, 0, 0, 0
    for p in prep:
        src = T.step(p["ids"], p["strata"])
        lab = dict(zip(p["ids"], p["strata"]))
        assert sorted(src) == sorted(p["ids"])                                   # a permutation of this date's stocks
        assert all(lab[i] == lab[s] for i, s in zip(p["ids"], src))              # within the stratum
        assert Counter(np.asarray(p["Q"])[[p["ids"].index(s) for s in src]].tolist()) == Counter(p["Q"].tolist())
        selfm += sum(i == s for i, s in zip(p["ids"], src))
        if prev is not None:
            for i, s in zip(p["ids"], src):
                if i in prev and prev[i] == s:
                    kept += 1
            total += len(src)
        prev = dict(zip(p["ids"], src))
    assert selfm / sum(len(p["ids"]) for p in prep) < 0.005                        # only singleton strata
    assert kept / total > 0.6                                                     # tethered: partners persist


def test_null_breaks_a_planted_chart_edge_and_the_real_world_finds_it(edge_panel):
    prep = H.prepare(edge_panel)
    real = H.run_world(prep)
    nulls = [H.run_world(prep, seed=s) for s in range(15)]
    t_ic = np.array([w["t_ic"] for w in nulls])
    assert abs(t_ic.mean()) < 0.8 and t_ic.max() < real["t_ic"]
    assert real["t_ic"] > 4 and real["t_inc"] > 4 and real["mono"] >= 0.9
    assert real["group_mean_ann"][4] > real["group_mean_ann"][1]


def test_null_is_reproducible_and_seed_dependent(null_panel):
    prep = H.prepare(null_panel)
    a, b, c = H.run_world(prep, seed=5), H.run_world(prep, seed=5), H.run_world(prep, seed=6)
    assert a["t_ic"] == b["t_ic"] and a["t_inc"] == b["t_inc"] and a["t_ic"] != c["t_ic"]


def test_null_preserves_dates_counts_and_returns(null_panel):
    prep = H.prepare(null_panel)
    a = H.run_world(prep, keep_series=True)
    b = H.run_world(prep, seed=9, keep_series=True)
    assert a["_years"] == b["_years"]
    assert [d["n"] for d in a["_series"]] == [d["n"] for d in b["_series"]]     # group counts per date preserved


def test_critical_values_are_per_statistic():
    worlds = [dict(t_ic=float(i), t_inc=float(-i)) for i in range(1, 5001)]
    c = H.critical_values(worlds)
    assert c == dict(t_ic=4951.0, t_inc=-50.0)                                      # 50th largest of each


def _s(**kw):
    s = dict(high_ann=0.05, low_ann=-0.01, mono=1.0, t_ic=4.0, t_inc=4.0, inc_mean=0.01, halves=[0.01, 0.02],
             block_max=0.3)
    s.update(kw)
    return s


def test_gates():
    c = dict(t_ic=3.0, t_inc=3.0)
    assert H.promotion(_s(), c)["pass"]
    for kw, gate in ((dict(high_ann=0.029), "G1_economic"), (dict(low_ann=0.06), "G1_economic"),
                     (dict(mono=0.8), "G2_monotonic"), (dict(t_ic=3.0), "G3_significant"),
                     (dict(halves=[-0.001, 0.02]), "G4_stable"), (dict(block_max=0.51), "G4_stable"),
                     (dict(t_inc=2.9), "G5_incremental"), (dict(inc_mean=-0.001), "G5_incremental")):
        g = H.promotion(_s(**kw), c)
        assert not g[gate] and not g["pass"], (kw, gate)


def test_thirteen_week_diagnostic_path(null_panel):
    s = H.run_world(H.prepare(null_panel, "y13"), lag=H.DIAG_NW_LAG, ann=H.ANN_DIAG)
    assert np.isfinite(s["t_ic"]) and len(s["group_mean_ann"]) == 5


def test_frozen_constants():
    assert (H.NW_LAG, H.DIAG_NW_LAG, H.ANN, H.ECON_MIN_HIGH, H.MONO_MIN, H.ALPHA, H.N_MOM_Q) == \
        (3, 12, 13.0, 0.03, 0.90, 0.01, 5)
    assert H.HIGH_GROUPS == (3, 4) and H.LOW_GROUPS == (0, 1) and H.BLOCK_MAX_SHARE == 0.5
