"""H023 Score v2 weight search (owner D199): the pure grid module qr_h023 and the frozen pins (qresearch.p8h023).
- the grid is exactly the pre-registered 92 configurations (control 40/45/15 included), adjacency and boundary;
- the exact integer score: the control equals 360 x the Score v1 total; column ranks equal qr_xs.avg_rank;
- every configuration's statistics equal the frozen H022 procedure (qr_p7_pred.run_world on Score_v2), in the real
  assignment and in null worlds (one tether permutation for the whole grid);
- plateau, D1-D5, the selection rule, cstar, the critical value and the walk-forward diagnostic (no look-ahead)."""
import hashlib
import math

import numpy as np
import pytest

import qr_h023 as H
import qr_p7_pred as R
import qr_p7_score as S
import qr_xs as X
from conftest import ROOT
from qresearch import p7pred_v2, p8h023


def _pts(m, f):
    return int(math.floor(m * f + 0.5))


def fake_dates(seed=1, D=83, n0=300, beta=None, nan_rate=0.003):
    """Synthetic population dates with realistic integer layer subtotals (Score v1 point levels) and t(5) responses;
    beta = optional planted (technical, fundamental, sector) signal."""
    rng = np.random.default_rng(seed)
    bf = S.BAND_FRACTION
    uni = [f"S{i:04d}" for i in range(700)]
    out = []
    for i in range(D):
        n = int(n0 + rng.integers(-80, 80))
        ids = sorted(rng.choice(uni, n, replace=False).tolist())
        band = lambda m: np.array([_pts(m, bf[k]) for k in rng.integers(0, 5, n)])  # noqa: E731
        tech = rng.choice([0, 8, 15], n) + band(15) + band(10)
        fund = band(15) + band(10) + band(10) + band(10)
        sect = rng.choice([0, 8, 15], n)
        C = np.column_stack([tech, fund, sect])
        y = rng.standard_t(5, n) * 0.07
        if beta is not None:
            y = y + (C - C.mean(axis=0)) @ np.asarray(beta, float)
        y[rng.random(n) < nan_rate] = np.nan
        out.append(dict(ids=ids, C=C, S=C.sum(axis=1).astype(float), sector=rng.integers(0, 12, n),
                        mom=rng.standard_normal(n), size=rng.standard_normal(n), y=y, year=2011 + i // 12,
                        regime="STRONG", day=f"d{i:03d}"))
    return out


@pytest.fixture(scope="module")
def dates():
    return fake_dates()


@pytest.fixture(scope="module")
def prep(dates):
    return H.prepare(dates)


# ----------------------------------------------------------------------------------------------- grid
def test_grid_is_the_preregistered_92():
    g = H.GRID
    assert len(g) == p8h023.GRID_N == 92 and len(set(g)) == 92 and list(g) == sorted(g)
    assert all(sum(w) == 100 and 10 <= w[0] <= 80 and 10 <= w[1] <= 80 and 0 <= w[2] <= 30 and
               all(x % 5 == 0 for x in w) for w in g)
    full = {(t, f, s) for t in range(10, 81, 5) for f in range(10, 81, 5) for s in range(0, 31, 5) if t + f + s == 100}
    assert set(g) == full
    assert g[H.CONTROL_INDEX] == H.CONTROL == p8h023.CONTROL and H.CONTROL_INDEX == p8h023.CONTROL_INDEX
    by_s = {s: sum(1 for w in g if w[2] == s) for s in range(0, 31, 5)}
    assert by_s == {0: 13, 5: 14, 10: 15, 15: 14, 20: 13, 25: 12, 30: 11}
    assert sum(len(v) for v in H.ADJ.values()) // 2 == p8h023.ADJACENT_PAIRS
    assert sum(H.on_boundary(w) for w in g) == p8h023.BOUNDARY_CONFIGS
    for i, nb in H.ADJ.items():       # one 5-point transfer between two layers, the third unchanged
        for j in nb:
            d = sorted(a - b for a, b in zip(g[i], g[j]))
            assert d == [-5, 0, 5]
    assert sorted(H.ADJ[H.CONTROL_INDEX]) == sorted(g.index(w) for w in (
        (45, 40, 15), (35, 50, 15), (45, 45, 10), (35, 45, 20), (40, 50, 10), (40, 40, 20)))


def test_constants_match_pins():
    c = p8h023.CONSTANTS
    assert (H.LAYER_MAX, H.SCALE, H.MULT, H.STEP, H.TOTAL) == (c["LAYER_MAX"], c["SCALE"], c["MULT"], c["STEP"], c["TOTAL"])
    assert (H.W_T[0], H.W_T[-1]) == c["W_T"] and (H.W_F[0], H.W_F[-1]) == c["W_F"] and (H.W_S[0], H.W_S[-1]) == c["W_S"]
    assert (H.ENTRY, H.THRESHOLDS, H.NW_LAG, H.ANN, H.N_Q, H.BLOCKS) == (
        c["ENTRY"], c["THRESHOLDS"], c["NW_LAG"], c["ANN"], c["N_Q"], c["BLOCKS"])
    assert (H.ECON_MIN, H.MONO_MIN, H.BLOCK_MAX_SHARE, (H.D5_MONTHS, H.D5_OF, H.D5_MEAN)) == (
        c["ECON_MIN"], c["MONO_MIN"], c["BLOCK_MAX_SHARE"], c["D5"])
    assert (H.R_NULL, H.ALPHA, H.CRIT_FLOOR, H.PLATEAU_MIN, H.PLATEAU_FRAC, H.FOLD_YEARS) == (
        c["R_NULL"], c["ALPHA"], c["CRIT_FLOOR"], c["PLATEAU_MIN"], c["PLATEAU_FRAC"], c["FOLD_YEARS"])
    # the frozen H022 conventions are reused, not redefined
    assert (H.ENTRY, H.NW_LAG, H.BLOCKS, H.N_Q) == (R.ENTRY, R.NW_LAG, R.BLOCKS, R.N_Q)
    assert (H.ECON_MIN, H.MONO_MIN, H.BLOCK_MAX_SHARE, H.CRIT_FLOOR, H.ALPHA) == (
        R.ECON_MIN, R.MONO_MIN, R.BLOCK_MAX_SHARE, R.CRIT_FLOOR, R.ALPHA)


def test_exact_integer_score():
    rng = np.random.default_rng(3)
    C = np.column_stack([rng.integers(0, 41, 500), rng.integers(0, 46, 500), rng.choice([0, 8, 15], 500)])
    Z = H.z_scores(C)
    assert Z.dtype.kind == "i" and Z.shape == (500, 92)
    assert np.array_equal(Z[:, H.CONTROL_INDEX], 360 * C.sum(axis=1))           # control = Score v1 total exactly
    for c, w in enumerate(H.GRID):
        v = H.score_v2(C, w)
        ref = w[0] * C[:, 0] / 40 + w[1] * C[:, 1] / 45 + w[2] * C[:, 2] / 15
        assert np.allclose(v, ref, atol=1e-12) and np.array_equal(Z[:, c] >= 28800, v >= 80)
    full = H.z_scores(np.array([[40, 45, 15]]))
    assert (full == 36000).all()                                                  # every configuration's maximum = 100
    assert H.layer_split((15, 8, 10, 15, 3, 7, 10, 8)) == (33, 35, 8)


def test_avg_rank_cols_equals_qr_xs():
    rng = np.random.default_rng(5)
    Z = rng.integers(0, 12, (257, 9))                                             # heavy ties
    r = H.avg_rank_cols(Z)
    for c in range(Z.shape[1]):
        assert np.array_equal(r[:, c], X.avg_rank(Z[:, c]))


# ----------------------------------------------------------------------------------------------- statistics
CHECK = ("t_ic", "ic_mean", "ic_se", "hi_ann", "mono", "q5_minus_q1_ann", "block_max", "hi_n_mean", "hi_months")


def _compare(dates, prep, seed, cols):
    w = H.world(prep, seed)
    s = H.summarise(w)
    worst = 0.0
    for c in cols:
        dd = [dict(d, S=H.score_v2(d["C"], H.GRID[c])) for d in dates]
        rw = R.run_world(R.prepare(dd), seed=seed)
        for k in CHECK:
            a, b = rw[k], float(s[k][c])
            assert a == b or (math.isnan(a) and math.isnan(b)) or abs(a - b) < 1e-12, (seed, c, k, a, b)
        assert abs(rw["halves"][0] - s["half1"][c]) < 1e-12 and abs(rw["halves"][1] - s["half2"][c]) < 1e-12
        assert max(abs(a - b) for a, b in zip(rw["q_mean_ann"], s["q_mean_ann"][c])) < 1e-12
        assert max(abs(rw["years"][y] - s["years"][y][c]) for y in rw["years"]) < 1e-12
        worst = max(worst, abs(rw["t_ic"] - s["t_ic"][c]))
    return worst


@pytest.mark.parametrize("seed", [None, 950001, 7])
def test_grid_equals_frozen_h022_procedure(dates, prep, seed):
    cols = [H.CONTROL_INDEX, 0, 13, 30, 61, 91]
    assert _compare(dates, prep, seed, cols) < 1e-12


def test_ic_is_bitwise_the_h022_ic(dates, prep):
    """Ranks are half-integers: every IC numerator / denominator is exact, so the real-assignment IC of the control is
    bit-identical to qr_p7_pred.date_stats."""
    w = H.world(prep)
    rp = R.prepare(dates)
    for i, p in enumerate(rp):
        assert R.date_stats(p)["ic"] == w["IC"][i, H.CONTROL_INDEX]


def test_null_tether_shared_by_the_whole_grid(dates, prep):
    """One permutation per date for every configuration: the control column of an H023 null world is the H022 null
    world of the same seed (the P8-CP1 integrity check against the committed Data v2 null worlds)."""
    for seed in (1, 2, 4999):
        rec = H.null_record(prep, seed)
        rw = R.run_world(R.prepare(dates), seed=seed)
        f = dict(zip(H.NULL_FIELDS, rec))
        assert abs(f["t_control"] - rw["t_ic"]) < 1e-12 and abs(f["ic_control"] - rw["ic_mean"]) < 1e-15
        assert f["seed"] == seed and f["max_t"] >= f["t_control"] and 0 <= f["argmax"] < 92
    assert H.null_record(prep, 11) == H.null_record(prep, 11)                       # deterministic
    assert H.null_record(prep, 11) != H.null_record(prep, 12)


def test_null_breaks_the_link_but_keeps_the_score_side(prep):
    T = R.Tether(31)
    for p in prep[:10]:
        part = T.step(p["ids"])
        pos = {s: j for j, s in enumerate(p["ids"])}
        ix = np.array([pos[s] for s in part])
        assert sorted(ix.tolist()) == list(range(len(ix))) and not np.any(ix == np.arange(len(ix)))
        # the permuted score side of every configuration is the same multiset (distribution, 80+ count preserved)
        assert np.array_equal(np.sort(p["Z"][ix], axis=0), np.sort(p["Z"], axis=0))
        ic, qm, hm, nh = H.date_grid(p, ix)
        assert np.array_equal(nh, p["nhi"])


def test_responses_never_enter_the_score_side(dates):
    """Look-ahead: the score side (Z, ranks, quintiles, 80+ group, counts) is identical whatever the responses."""
    a = H.prepare(dates)
    rng = np.random.default_rng(2)

    def scramble(y):
        out, fin = y.copy(), np.isfinite(y)
        out[fin] = rng.permutation(y[fin]) * 3.0 + 1.0
        return out
    b = H.prepare([dict(d, y=scramble(d["y"])) for d in dates])
    for p, q in zip(a, b):
        assert p["ids"] == q["ids"]
        for k in ("Z", "RQc", "Q", "hi", "qcnt", "nhi", "thr"):
            assert np.array_equal(p[k], q[k])


def test_thresholds_and_counts(prep):
    p = prep[0]
    for j, t in enumerate(H.THRESHOLDS):
        assert np.array_equal(p["thr"][j], (p["Z"] >= 360 * t).sum(axis=0))
    assert np.array_equal(p["thr"][1], p["nhi"])


def test_nw_cols_equals_qr_xs():
    rng = np.random.default_rng(9)
    A = rng.standard_normal((83, 7)) * 0.05 + 0.003
    m, se, t = H.nw_cols(A, 2)
    for c in range(7):
        mm, ss, tt = X.nw_tstat(A[:, c], 2)
        assert abs(mm - m[c]) < 1e-15 and abs(ss - se[c]) < 1e-15 and abs(tt - t[c]) < 1e-12


# ----------------------------------------------------------------------------------------------- plateau / selection
def _stats(t, ic=None, hi=None, q51=None, h1=None, h2=None, mono=None, bmax=None, months=None, nmean=None, n=83):
    g = len(H.GRID)
    f = lambda v, d: np.full(g, d, float) if v is None else np.asarray(v, float)  # noqa: E731
    return dict(n_dates=n, t_ic=f(t, 0.0), ic_mean=f(ic, 0.01), hi_ann=f(hi, 0.05), q5_minus_q1_ann=f(q51, 0.02),
                half1=f(h1, 0.01), half2=f(h2, 0.01), mono=f(mono, 1.0), block_max=f(bmax, 0.4),
                hi_months=f(months, 83), hi_n_mean=f(nmean, 5.0))


def _bump(center, peak, width):
    g = H.GRID
    return np.array([peak * math.exp(-H.l1(w, center) / width) for w in g])


def test_plateau_definition():
    # a broad bump around (30, 55, 15): connected, >= 80% of the region maximum -> one plateau, the isolated far
    # configurations below 80% are excluded
    t = _bump((30, 55, 15), 4.0, 60.0)
    s = _stats(t)
    regions, plats = H.plateaus(s)
    assert len(regions) == 1 and len(regions[0]) == 92
    assert len(plats) == 1
    top = int(np.argmax(t))
    assert top in plats[0] and all(t[i] >= 0.8 * t[top] for i in plats[0])
    comp = H.components(plats[0])
    assert comp == [plats[0]]
    # a sharp isolated peak is never a plateau
    sharp = _bump((30, 55, 15), 4.0, 2.0)
    assert H.plateaus(_stats(sharp))[1] == []
    # base conditions split regions: configurations with a negative half are not members
    h2 = np.where(np.array([w[2] for w in H.GRID]) == 15, -0.01, 0.01)
    regions, plats = H.plateaus(_stats(t, h2=h2))
    assert all(H.GRID[i][2] != 15 for r in regions for i in r)


def test_selection_rule_and_tie_breaks():
    t = _bump((30, 55, 15), 4.0, 60.0)
    s = _stats(t)
    sel = H.select(s, 2.5)
    assert sel["winner"] is not None and sel["candidate"] in sel["winner"]
    q = sel["filters"]["qualified"]
    assert q[sel["candidate"]]
    members = sel["winner"]
    tot = lambda i: sum(H.l1(H.GRID[i], H.GRID[j]) for j in members)  # noqa: E731
    best = min(tot(i) for i in members if q[i])
    assert tot(sel["candidate"]) == best
    # the candidate is restricted to qualified members; the unrestricted medoid is reported only
    hi = np.full(92, 0.05)
    hi[sel["candidate"]] = 0.02                                                     # fails D2 only
    s2 = _stats(t, hi=hi)
    sel2 = H.select(s2, 2.5)
    assert sel2["candidate"] != sel["candidate"] and sel2["filters"]["qualified"][sel2["candidate"]]
    assert sel2["unrestricted_medoid"] == sel["candidate"]
    # no qualified member anywhere -> no candidate, even with plateaus
    sel3 = H.select(s, 99.0)
    assert sel3["plateaus"] and sel3["candidate"] is None and sel3["eligible"] == []


def test_plateau_ranking_prefers_size_then_median_t():
    g = H.GRID
    t = np.zeros(92)
    a = [g.index(w) for w in ((20, 70, 10), (25, 65, 10), (20, 65, 15), (25, 60, 15), (30, 60, 10))]
    b = [g.index(w) for w in ((70, 10, 20), (65, 15, 20), (70, 15, 15), (65, 10, 25))]
    t[a] = 3.0
    t[b] = 6.0
    ic = np.where(t > 0, 0.01, -0.01)
    s = _stats(t, ic=ic)
    sel = H.select(s, 2.5)
    assert len(sel["plateaus"]) == 2 and sorted(sel["winner"]) == sorted(a)        # larger plateau wins despite lower t
    assert H.GRID[sel["argmax"]] in [g[i] for i in b]                               # the absolute best differs


def test_filters_d1_to_d5():
    s = _stats(np.full(92, 3.0))
    f = H.filters(s, 2.5)
    assert f["qualified"].all()
    for k, kw, flag in (("D1", dict(ic=np.full(92, -0.01)), "D1"), ("D2", dict(hi=np.full(92, 0.0299)), "D2"),
                        ("D3", dict(mono=np.full(92, 0.89)), "D3"), ("D3", dict(q51=np.full(92, 0.0)), "D3"),
                        ("D4", dict(h2=np.full(92, -1e-9)), "D4"), ("D4", dict(bmax=np.full(92, 0.5001)), "D4"),
                        ("D5", dict(months=np.full(92, 59)), "D5"), ("D5", dict(nmean=np.full(92, 1.99)), "D5")):
        f2 = H.filters(_stats(np.full(92, 3.0), **kw), 2.5)
        assert not f2[flag].any() and not f2["qualified"].any(), k
    assert H.filters(_stats(np.full(92, 3.0), months=np.full(92, 60), nmean=np.full(92, 2.0), bmax=np.full(92, 0.5),
                            hi=np.full(92, 0.03), mono=np.full(92, 0.9)), 2.5)["qualified"].all()
    assert not H.filters(_stats(np.full(92, 2.5)), 2.5)["D1"].any()                 # strictly greater
    # D5 scales to a shorter (walk-forward) window: 60 / 83 of the months
    assert H.filters(_stats(np.full(92, 3.0), months=np.full(92, 27), n=36), 2.5)["D5"].all()
    assert not H.filters(_stats(np.full(92, 3.0), months=np.full(92, 26), n=36), 2.5)["D5"].any()


def test_cstar_decides_candidate_existence(dates):
    for k, beta in enumerate((None, (0.0, 0.0006, 0.0), (0.0004, 0.0, 0.0), (0.0, 0.0002, 0.0002))):
        p = H.prepare(fake_dates(seed=20 + k, D=60, n0=200, beta=beta))
        for seed in (None, 3):
            s = H.summarise(H.world(p, seed))
            cs = H.cstar(s)
            for c in (0.5, 1.5, 2.326, 3.0, 5.0, 10.0):
                assert (H.select(s, c)["candidate"] is not None) == (c < cs), (k, seed, c, cs)


def test_planted_signal_is_found_and_null_is_quiet():
    p = H.prepare(fake_dates(seed=40, beta=(0.0, 0.0008, 0.0)))
    s = H.summarise(H.world(p))
    sel = H.select(s, 2.5)
    assert sel["candidate"] is not None and H.GRID[sel["candidate"]][1] >= 60      # fundamental-heavy region
    ns = H.summarise(H.world(p, 5))
    assert ns["t_ic"].max() < 5.0


def test_critical_value_convention():
    rng = np.random.default_rng(1)
    v = rng.standard_normal(5000) + 2.0
    c = H.critical_value(v)
    assert c == float(np.sort(v)[::-1][49]) == X.critical_value(list(v), 0.01)
    assert H.critical_value(np.zeros(5000)) == 2.326


# ----------------------------------------------------------------------------------------------- walk-forward
def test_walk_forward_uses_training_years_only():
    d0 = fake_dates(seed=50, beta=(0.0, 0.0006, 0.0))
    w0 = H.world(H.prepare(d0))
    wf = H.walk_forward(w0, [2.5] * 4)
    assert [f["year"] for f in wf["folds"]] == [2014, 2015, 2016, 2017]
    assert [f["train_months"] for f in wf["folds"]] == [36, 48, 60, 72]
    assert [f["observe_months"] for f in wf["folds"]] == [12, 12, 12, 11]
    assert wf["pseudo_oos"]["months"] == 47
    # replacing every response from 2016 on changes nothing in the 2014 and 2015 fold selections
    rng = np.random.default_rng(1)
    d1 = [dict(d, y=d["y"] if d["year"] < 2016 else rng.standard_normal(len(d["ids"])) * 0.1) for d in d0]
    wf1 = H.walk_forward(H.world(H.prepare(d1)), [2.5] * 4)
    for a, b in zip(wf["folds"][:2], wf1["folds"][:2]):
        assert (a["selected"], a["how"], a["train_t"]) == (b["selected"], b["how"], b["train_t"])
    assert wf["folds"][0]["observe_ic"] == wf1["folds"][0]["observe_ic"]
    assert all(r[i] == 0 for i, r in enumerate(wf["distances"]))


# ----------------------------------------------------------------------------------------------- pins
def test_pins():
    assert p8h023.SPEC_SHA256 == hashlib.sha256((ROOT / p8h023.SPEC).read_bytes()).hexdigest()
    for path, h in p8h023.CODE_SHA256.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == h, path
    assert p8h023.PANEL_SHA256 == p7pred_v2.PANEL_SHA256 == \
        "09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0"
    assert p8h023.DATA_FREEZE_MANIFEST_SHA256 == \
        "cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb"
    assert p8h023.NULL_BATCHES == ((1, 1000), (1001, 2000), (2001, 3000), (3001, 4000), (4001, 5000))
    assert p8h023.H022_RECORD["status"] == "Rejected / NOT QUALIFIED" and p8h023.H022_RECORD["t_ic"] == 0.47711861682625983
    assert p8h023.TRAINING_PERIOD["status"].startswith("TRAINING / DEVELOPMENT")
    text = (ROOT / p8h023.SPEC).read_text()
    for must in ("TRAINING / DEVELOPMENT", "NO ROBUST SCORE V2 CANDIDATE", "DEVELOPMENT CANDIDATE — NOT YET VALIDATED",
                 "c_IC_VALIDATION", "H023 VALIDATED", "H023 NOT VALIDATED"):
        assert must in text


def test_c_search_is_pinned_from_the_5000_optimiser_null_worlds():
    """c_SEARCH and the fold thresholds are recomputed from the committed per-world records with the frozen rule; the
    null result file is the pinned one; every integrity check passed."""
    import gzip
    import json
    path = ROOT / p8h023.NULL_RESULT
    assert hashlib.sha256(path.read_bytes()).hexdigest() == p8h023.NULL_RESULT_SHA256
    res = json.loads(path.read_text())
    ws = json.loads(gzip.open(ROOT / p8h023.NULL_WORLDS).read())
    assert hashlib.sha256((ROOT / p8h023.NULL_WORLDS).read_bytes()).hexdigest() == res["worlds_file_sha256"]
    assert [w["seed"] for w in ws] == list(p8h023.NULL_SEEDS)
    mt = [w["max_t"] for w in ws]
    assert H.critical_value(mt) == p8h023.C_SEARCH == res["c_search"] == sorted(mt, reverse=True)[49] > 2.326
    for y in H.FOLD_YEARS:
        assert H.critical_value([w[f"max_t_fold{y}"] for w in ws]) == p8h023.C_FOLD[y] == res["c_fold"][str(y)]
    integ = res["integrity"]
    assert integ["completed"] == 5000 and integ["seeds_exact"] and integ["rerun_identical"] and integ["zero_orders"]
    assert integ["panel_equals_pinned"] and integ["components_equal_pinned"] and integ["pit_audit_zero"]
    assert integ["control_equals_h022_null"]["all_within_1e9"]
    assert res["false_promotion"] == float(np.mean([w["cstar"] > p8h023.C_SEARCH for w in ws]))


def test_p8_cp1_result_is_the_frozen_procedure_outcome():
    """The one real development search E025-08: offline recomputation identical; no candidate; nothing frozen."""
    import json
    res = json.loads((ROOT / "research/phase8/cp1/P8_CP1_result.json").read_text())
    assert res["verdict"] == "NO ROBUST SCORE V2 CANDIDATE" and res["selected"] is None and res["candidate_sha256"] is None
    assert all(res["recompute"].values()) and res["orders"] == 0 and res["c_search"] == p8h023.C_SEARCH
    assert res["surface"]["counts"]["qualified"] == 0 and res["surface"]["plateaus"] == []
    assert abs(res["control"]["t_ic"] - p8h023.H022_RECORD["t_ic"]) < 1e-12
    assert res["absolute_best"]["weights"] == [80, 10, 10] and res["absolute_best"]["t_ic"] < p8h023.C_SEARCH
    assert p8h023.CANDIDATE is None
