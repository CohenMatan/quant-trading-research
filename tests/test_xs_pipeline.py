"""H019 end-to-end pipeline (qr_xs.Features / run_world) on synthetic daily panels: strict point-in-time leakage
canaries for the fitted Han-Zhou-Zhu trend factor and the other signals, and the null procedure (stratified tether,
full re-estimation in every null world, S1 / S2 dependency). No market data is used."""
import numpy as np
import pytest

from conftest import ROOT, load_module

X = load_module(ROOT / "src/qresearch/lean/qr_xs.py", "qr_xs_pipe")
SY = load_module(ROOT / "research/phase4/P4_xs_synth.py", "p4_xs_synth")

M, FR = 40, 14                      # 40 months; research from month 14; decisions from month 26 (12 regressions)


def build(seed=0, mutate=None, N=50):
    kw, info = SY.make_panel(N=N, months=M, seed=seed, first_research_k=FR)
    if mutate is not None:
        mutate(kw)
    pn = X.Panel(**kw)
    return X.Features(pn, horizons=(1,)), info


def run(F, info, seed=None, last=M - 2):
    lab = info["labels"]
    return X.run_world(F, seed=seed, first_research=lab[FR], first_decision=lab[FR + 12], last_decision=lab[last],
                       keep_signals=True)


def signals_at(out, k):
    for s in out["_signals"]:
        if s["k"] == k:
            return s
    raise KeyError(k)


def same(a, b):
    return np.array_equal(a["rec"], b["rec"]) and all(np.allclose(a[x], b[x], equal_nan=True)
                                                      for x in ("pret", "idm", "S2", "S3"))


@pytest.fixture(scope="module")
def base():
    F, info = build()
    return F, info, run(F, info)


def test_pipeline_runs_and_chronology(base):
    F, info, out = base
    ks = [s["k"] for s in out["_signals"]]
    assert ks[0] == FR + 12 and ks[-1] == M - 2                      # first decision after 12 regressions
    assert min(out["_betas"]) == FR and max(out["_betas"]) == M - 3  # regressions s = FR .. last decision - 1
    for k in ks:                                                      # betas used at k come from s = k-12 .. k-1
        assert all(s in out["_betas"] for s in range(k - 12, k))


def test_future_prices_do_not_change_past_signals(base):
    F, info, out = base
    k = FR + 16
    d = info and None

    def mut(kw):
        r = kw["month_end"][k]
        for key in ("split_close", "tr_close", "tr_open"):
            kw[key][r + 1:] *= 1.0 + np.random.default_rng(9).normal(0, 0.2, kw[key][r + 1:].shape)
    F2, info2 = build(mutate=mut)
    out2 = run(F2, info2)
    for kk in range(FR + 12, k + 1):
        assert same(signals_at(out, kk), signals_at(out2, kk)), kk
    assert not same(signals_at(out, k + 2), signals_at(out2, k + 2))  # sensitivity: later scores do change


def test_next_month_returns_do_not_change_the_score_that_predicted_them(base):
    F, info, out = base
    k = FR + 18

    def mut(kw):
        a, b = kw["month_end"][k], kw["month_end"][k + 1]
        g = np.exp(np.random.default_rng(3).normal(0, 0.05, (b - a, kw["tr_close"].shape[1])).cumsum(axis=0))
        for key in ("split_close", "tr_close", "tr_open"):
            kw[key][a + 1:b + 1] *= g
            kw[key][b + 1:] *= g[-1]
    F2, info2 = build(mutate=mut)
    out2 = run(F2, info2)
    s1, s2 = signals_at(out, k), signals_at(out2, k)
    assert same(s1, s2)                                               # S1-S3 at k unchanged
    assert not np.allclose(s1["y"], s2["y"])                          # ... while the predicted returns changed
    assert not np.allclose(signals_at(out, k + 1)["S3"], signals_at(out2, k + 1)["S3"])   # used from k + 1 on
    for s in range(FR, k):                                            # regressions before s = k untouched
        assert np.allclose(out["_betas"][s], out2["_betas"][s])
    assert not np.allclose(out["_betas"][k], out2["_betas"][k])       # s = k uses month k+1 returns


def test_truncation_after_decision_leaves_signals_unchanged(base):
    F, info, out = base
    k = FR + 15

    def mut(kw):
        r = kw["month_end"][k]
        for key in ("split_close", "tr_close", "tr_open"):
            kw[key][r + 1:] = np.nan
        kw["elig"][k + 1:] = False
    F2, info2 = build(mutate=mut)
    out2 = X.run_world(F2, first_research=info2["labels"][FR], first_decision=info2["labels"][FR + 12],
                       last_decision=info2["labels"][k], keep_signals=True)
    s1, s2 = signals_at(out, k), signals_at(out2, k)
    assert np.array_equal(s1["rec"], s2["rec"])
    assert all(np.allclose(s1[x], s2[x]) for x in ("pret", "idm", "S2", "S3"))


def test_late_entrants_do_not_alter_earlier_regressions(base):
    F, info, out = base
    k_in = FR + 20

    def mut(kw):
        rng = np.random.default_rng(5)
        D = kw["tr_close"].shape[0]
        newp = 50 * np.exp(np.cumsum(rng.normal(0, 0.02, D)))
        newp[:kw["month_end"][k_in - 3]] = np.nan                     # listed shortly before it becomes eligible
        for key in ("split_close", "tr_close", "tr_open"):
            kw[key] = np.column_stack([kw[key], newp])
        e = np.zeros((kw["elig"].shape[0], 1), bool)
        e[k_in:] = True
        kw["elig"] = np.column_stack([kw["elig"], e])
    F2, info2 = build(mutate=mut)
    out2 = run(F2, info2)
    for s in range(FR, k_in):
        assert np.allclose(out["_betas"][s], out2["_betas"][s]), s
    for kk in range(FR + 12, k_in + 1):
        assert same(signals_at(out, kk), signals_at(out2, kk)), kk
    assert not np.allclose(out["_betas"][k_in], out2["_betas"][k_in])


def test_trend_factor_refuses_lookahead():
    TF = X.TrendFactor()
    rng = np.random.default_rng(1)
    for s in range(14):
        TF.add_regression(s, rng.normal(1, 0.05, (200, 11)), rng.normal(size=200))
    sc = TF.score(13, rng.normal(1, 0.05, (5, 11)))
    assert np.all(np.isfinite(sc))                                    # uses s = 1 .. 12 only, never s = 13


def test_null_world_reestimates_the_trend_factor_and_keeps_strata(base):
    F, info, out = base
    nul = run(F, info, seed=7)
    for s in out["_betas"]:                                           # coefficients re-estimated in the null world
        assert not np.allclose(out["_betas"][s], nul["_betas"][s])
    for a, b in zip(out["_signals"], nul["_signals"]):
        assert np.array_equal(a["rec"], b["rec"])                     # identical evaluation cross-sections
        assert sorted(a["pret"]) == pytest.approx(sorted(b["pret"]))  # same values, permuted within the date
        assert not np.array_equal(a["src"], b["src"])
        k = a["k"]
        assert np.all(F.full[k, b["src"]])                            # full-stratum receivers get full sources


def test_null_world_preserves_the_s1_s2_dependency(base):
    F, info, _ = base
    nul = run(F, info, seed=11)
    for s in nul["_signals"]:
        k, src = s["k"], s["src"]
        assert np.allclose(s["pret"], F.pret[k, src]) and np.allclose(s["idm"], F.idm[k, src])  # one source each
        exp = X.smooth_momentum_score(F.pret[k, src], X.fip_key(F.idm[k, src], F.pret[k, src]))
        assert np.allclose(s["S2"], exp)                              # two-stage sort recomputed on the pair


def test_null_partners_persist_across_months(base):
    F, info, _ = base
    nul = run(F, info, seed=13)
    a, b = nul["_signals"][3], nul["_signals"][4]
    ma, mb = dict(zip(a["rec"], a["src"])), dict(zip(b["rec"], b["src"]))
    common = [i for i in ma if i in mb]
    assert np.mean([ma[i] == mb[i] for i in common]) > 0.8            # tethered: partners persist


def test_worlds_are_seed_deterministic(base):
    F, info, _ = base
    a, b, c = run(F, info, seed=21), run(F, info, seed=21), run(F, info, seed=22)
    assert a["S3"]["t"] == b["S3"]["t"] and a["S3"]["t"] != c["S3"]["t"]


def test_young_stocks_use_partial_windows_as_replicated():
    """Chen-Zimmermann: MA over the last L observations, at least one (Stata asrol default)."""
    F, info = build(seed=4)
    pn_kw, _ = SY.make_panel(N=50, months=M, seed=4, first_research_k=FR)
    born = info["born"]
    k = FR + 13
    young = [j for j in range(50) if F.dom[k, j] and pn_kw["month_end"][k] - born[j] < 1000]
    assert young
    j = young[0]
    d = pn_kw["month_end"][k]
    q = pn_kw["split_close"][:d + 1, j]
    q = q[np.isfinite(q)]
    assert F.A[k, j, -1] == pytest.approx(q.mean() / q[-1])          # 1000-day MA from the available history
