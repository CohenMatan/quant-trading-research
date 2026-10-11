"""H024 Feature Redesign and Selection (owner D201): the pure module qr_h024 and the frozen pins (qresearch.p9h024).
- the library is exactly the pre-registered 11-feature rank-order prefix within the 500-model budget;
- the component rule and the model library (2-4 features, at most one per component); leave-one-out and
  neighbourhood structure;
- the new price features (REV1M, HI52: life rule, contamination, slice exactness) and fundamental features (the
  frozen Score v1 formulas for GPA / ACC / EQA);
- the percentile transform (direction, sector scope) and equal-weight model scores;
- every feature / model / control column equals the frozen H022 procedure (qr_p7_pred.run_world) on its score, in
  the real assignment and in null worlds (one tether permutation for the whole score side);
- D6, the neighbourhood rule, the selection order, cstar, the critical value and the walk-forward (no look-ahead)."""
import hashlib
import math

import numpy as np
import pytest

import qr_h023 as G
import qr_h024 as K
import qr_p7_pred as R
import qr_p7_score as S
import qr_xs as X
from conftest import ROOT


def fake_dates(seed=1, D=83, n0=260, beta=None, nan_rate=0.02):
    """Synthetic H022-population dates: raw library values (some invalid), FF12 sectors, layer subtotals, t(5)
    responses; beta = optional planted signal on the ORIENTED features (dict feature -> loading)."""
    rng = np.random.default_rng(seed)
    uni = [f"S{i:04d}" for i in range(600)]
    F = len(K.LIBRARY)
    out = []
    for i in range(D):
        n = int(n0 + rng.integers(-60, 60))
        ids = sorted(rng.choice(uni, n, replace=False).tolist())
        base = rng.standard_normal((n, 3))
        Xr = rng.standard_normal((n, F)) + base[:, rng.integers(0, 3, F)] * 0.5
        Xr[:, K.LIBRARY.index("LOWVOL")] = np.abs(Xr[:, K.LIBRARY.index("LOWVOL")]) * 0.01 + 0.005
        Xr[rng.random((n, F)) < nan_rate] = np.nan
        y = rng.standard_t(5, n) * 0.07
        if beta:
            for f, b in beta.items():
                j = K.LIBRARY.index(f)
                v = np.nan_to_num(K.DIRECTION[f] * Xr[:, j])
                y = y + b * (v - v.mean()) / (v.std() or 1.0)
        y[rng.random(n) < 0.003] = np.nan
        C = np.column_stack([rng.integers(0, 41, n), rng.integers(0, 46, n), rng.choice([0, 8, 15], n)])
        out.append(dict(ids=ids, X=Xr, sector=rng.integers(0, 12, n), C=C, y=y, y2=y, y3=y, year=2011 + i // 12,
                        day=f"d{i:03d}", S=C.sum(axis=1).astype(float), mom=rng.standard_normal(n),
                        size=rng.standard_normal(n), regime="STRONG"))
    return out


@pytest.fixture(scope="module")
def lib():
    return K.Library(K.model_library())


@pytest.fixture(scope="module")
def dates():
    return fake_dates()


# ----------------------------------------------------------------------------------------------- library
def test_library_is_the_preregistered_prefix():
    assert K.LIBRARY == ("MOM", "LOWVOL", "GPA", "ACC", "BM", "AG", "REV1M", "CBOP", "HI52", "CFP", "EQA")
    fam = {}
    for f in K.LIBRARY:
        fam[K.FAMILY[f]] = fam.get(K.FAMILY[f], 0) + 1
    assert sorted(fam.values()) == [1, 1, 1, 1, 1, 2, 2, 2] and K.model_count(list(fam.values())) == 415
    fam["sector"] = 1
    assert K.model_count(list(fam.values())) == 616 > K.MODEL_BUDGET                  # SECTOR would break the budget
    assert set(K.DIRECTION) == set(K.LIBRARY) and set(K.SCOPE) == {"GPA", "EQA"}
    assert {f: K.DIRECTION[f] for f in ("LOWVOL", "AG", "REV1M")} == dict(LOWVOL=-1, AG=-1, REV1M=-1)
    assert all(K.DIRECTION[f] == 1 for f in K.LIBRARY if f not in ("LOWVOL", "AG", "REV1M"))
    assert len(K.LIBRARY) <= K.MAX_FEATURES and "REVG" in K.EXCLUDED and "SECTOR" not in K.LIBRARY


def test_model_library_components_and_structure(lib):
    ms = K.model_library()
    assert len(ms) == 415 and ms == sorted(ms, key=lambda m: (len(m), m)) and len(set(ms)) == 415
    assert all(2 <= len(m) <= 4 and list(m) == sorted(m) for m in ms)
    for m in ms:
        fams = [K.FAMILY[f] for f in m]
        assert len(set(fams)) == len(fams)                                            # at most one per family
    assert sum(1 for m in ms if len(m) == 2) == 52 and sum(1 for m in ms if len(m) == 4) == 225
    linked = K.model_library(links=[("ACC", "CBOP")])                               # a redundancy link merges
    assert all(len({"ACC", "CBOP", "GPA"} & set(m)) <= 1 for m in linked)         # one component now
    assert len(linked) < 415
    assert K.redundancy_links([[1.0 if i == j else (0.85 if {i, j} == {3, 7} else 0.5) for j in range(11)]
                               for i in range(11)]) == [("ACC", "CBOP")]
    allx = K.redundancy_links([[0.9] * 11 for _ in range(11)])
    assert allx == sorted(tuple(sorted((a, b))) for i, a in enumerate(K.LIBRARY) for j, b in enumerate(K.LIBRARY)
                          if i < j and K.FAMILY[a] != K.FAMILY[b])                 # same-family pairs never listed
    # leave-one-out and neighbours
    m = ("ACC", "BM", "MOM")
    i = lib.models.index(m)
    loo = {tuple(lib.models[c - lib.F]) for c in lib.loo[i] if c >= 0}
    assert loo == {("BM", "MOM"), ("ACC", "MOM"), ("ACC", "BM")}
    j = lib.models.index(("ACC", "MOM"))
    assert sorted(lib.features[c] for c in lib.loo[j] if c >= 0) == ["ACC", "MOM"]
    for x in lib.nbr[i]:
        nb = lib.models[x]
        assert len(nb) == 3 and len(set(nb) ^ set(m)) == 2
    assert lib.sha == K.library_sha(ms) and len(lib.sha) == 64


# ----------------------------------------------------------------------------------------------- feature values
def _series(n=600, seed=3):
    rng = np.random.default_rng(seed)
    P = 100 * np.exp(np.cumsum(rng.standard_normal(n) * 0.01))
    C = P * np.exp(-np.arange(n) * 0.0001)
    return C, P


def test_price_features_formulas_life_and_contamination():
    C, P = _series()
    t = 550
    pf = K.price_features(C, P, t)
    assert pf["REV1M"] == pytest.approx(P[t] / P[t - 21] - 1.0, rel=1e-15)
    assert pf["HI52"] == pytest.approx(C[t] / C[t - 251:t + 1].max(), rel=1e-15)
    full = K.price_features(C, P, t, span=10_000)
    assert full == pf                                                              # slice exactness
    C2, P2 = C.copy(), P.copy()
    C2[400:470] = np.nan                                                           # > 60-session gap: new life
    pf2 = K.price_features(C2, P2, t)
    assert pf2["HI52"] is None and pf2["REV1M"] is not None
    assert K.price_features(C, P, t, unverified_rows=[t - 100])["HI52"] is None
    assert K.price_features(C, P, t, distributions=[(t - 100, 0.15)])["HI52"] is None
    assert K.price_features(C, P, t, distributions=[(t - 100, 0.05)])["HI52"] is not None
    assert K.price_features(C, P, t, distributions=[(t - 300, 0.15)])["HI52"] is not None  # outside the window
    C3, P3 = C.copy(), P.copy()
    C3[t + 1:] *= 5
    P3[t + 1:] *= 5
    assert K.price_features(C3, P3, t) == pf                                       # future prices never used
    assert K.price_features(C[:t + 1], P[:t + 1], t) == pf                         # truncation invariance


def test_fund_features_equal_the_frozen_score_v1_formulas():
    vals = (1000.0, 400.0, 80.0, 120.0, 2000.0, 900.0)
    ff = K.fund_features(vals, 1600.0, 5000.0)
    fi, _ = S.fundamental_inputs(*vals, 950.0)
    assert ff["GPA"] == fi["gpa"] and ff["ACC"] == fi["cash_conversion"] and ff["EQA"] == fi["eqa"]
    assert ff["CBOP"] == 120.0 / 2000.0 and ff["BM"] == 900.0 / 5000.0 and ff["CFP"] == 120.0 / 5000.0
    assert ff["AG"] == 2000.0 / 1600.0 - 1.0
    assert K.fund_features(vals, None, 5000.0)["AG"] is None
    assert K.fund_features((1000.0, 400.0, 80.0, 120.0, 2000.0, -5.0), 1600.0, 5000.0)["BM"] is None
    assert all(v is None for k, v in K.fund_features(vals, 1600.0, None).items() if k in ("BM", "CFP"))
    row = K.feature_row(dict(mom_12_1=0.2, vol60=0.01), dict(REV1M=0.03, HI52=None), ff)
    assert row[0] == 0.2 and row[1] == 0.01 and math.isnan(row[K.LIBRARY.index("HI52")])


def test_percentiles_direction_and_scope():
    rng = np.random.default_rng(4)
    n = 60
    Xr = rng.standard_normal((n, len(K.LIBRARY)))
    sec = np.r_[np.zeros(30, int), np.ones(25, int), np.full(5, 2)]
    Pm = K.percentiles(Xr, sec)
    assert Pm.min() >= 0 and Pm.max() <= 1
    j = K.LIBRARY.index("LOWVOL")
    assert Pm[np.argmin(Xr[:, j]), j] == 1.0                                       # lower volatility = best
    j = K.LIBRARY.index("MOM")
    assert Pm[np.argmax(Xr[:, j]), j] == 1.0
    j = K.LIBRARY.index("GPA")                                                     # sector scope (groups >= 10)
    for g in (0, 1):
        ix = np.flatnonzero(sec == g)
        assert Pm[ix, j].max() == 1.0 and Pm[ix, j].min() == 0.0
    ix = np.flatnonzero(sec == 2)                                                  # small group -> market-wide
    r = X.avg_rank(Xr[:, j])
    assert np.allclose(Pm[ix, j], (r[ix] - 1) / (n - 1))


# ----------------------------------------------------------------------------------------------- engine
CHECK = ("t_ic", "ic_mean", "ic_se", "hi_ann", "mono", "q5_minus_q1_ann", "block_max", "hi_n_mean", "hi_months")


@pytest.mark.parametrize("seed", [None, 950001])
def test_every_column_equals_the_frozen_h022_procedure(dates, lib, seed):
    prep = K.prepare(dates, lib)
    w = G.world(prep, seed)
    s = G.summarise(w)
    cols = [0, 1, 6, lib.F, lib.F + 60, lib.F + lib.M - 1, lib.ctrl_cols[0], lib.ctrl_cols[1]]
    for c in cols:
        dd = []
        for d in dates:
            ok = K.population(d)
            Pm = K.percentiles(np.asarray(d["X"])[ok], np.asarray(d["sector"])[ok])
            Sc = K.score_matrix(Pm, lib, np.asarray(d["C"])[ok])[:, c]
            dd.append(dict(ids=np.asarray(d["ids"])[ok], S=Sc, sector=np.asarray(d["sector"])[ok],
                           mom=np.asarray(d["mom"])[ok], size=np.asarray(d["size"])[ok],
                           y=np.asarray(d["y"])[ok], year=d["year"], regime="STRONG"))
        rw = R.run_world(R.prepare(dd), seed=seed)
        for k in CHECK:
            a, b = rw[k], float(s[k][c])
            assert a == b or (math.isnan(a) and math.isnan(b)) or abs(a - b) < 1e-12, (seed, c, k, a, b)
        assert abs(rw["halves"][1] - s["half2"][c]) < 1e-12


def test_population_is_common_and_controls_are_score_v1(dates, lib):
    prep = K.prepare(dates, lib)
    d = dates[0]
    ok = K.population(d)
    assert prep[0]["n"] == int(ok.sum()) and prep[0]["Z"].shape[1] == lib.ncol
    Pm = K.percentiles(np.asarray(d["X"])[ok], np.asarray(d["sector"])[ok])
    Sm = K.score_matrix(Pm, lib, np.asarray(d["C"])[ok])
    assert np.allclose(Sm[:, lib.ctrl_cols[0]], np.asarray(d["C"])[ok].sum(axis=1))
    m = lib.models.index(("ACC", "BM", "MOM"))
    exp = 100 * Pm[:, [K.LIBRARY.index(f) for f in ("ACC", "BM", "MOM")]].mean(axis=1)
    assert np.allclose(Sm[:, lib.F + m], exp, rtol=0, atol=1e-12)


def test_null_record_and_tether(dates, lib):
    prep = K.prepare(dates, lib)
    r1 = K.null_record(prep, lib, 7)
    assert r1 == K.null_record(prep, lib, 7) and r1 != K.null_record(prep, lib, 8)
    f = dict(zip(K.NULL_FIELDS, r1))
    s = G.summarise(G.world(prep, 7))
    assert f["max_t_feature"] == float(s["t_ic"][:lib.F].max())
    assert f["max_t_model"] == float(s["t_ic"][lib.F:lib.F + lib.M].max())
    assert f["cstar"] == K.cstar(s, lib)


def test_no_lookahead_in_the_score_side(dates, lib):
    a = K.prepare(dates, lib)
    rng = np.random.default_rng(2)

    def scramble(y):
        out, fin = y.copy(), np.isfinite(y)
        out[fin] = rng.permutation(y[fin]) * 3.0 + 1.0
        return out
    b = K.prepare([dict(d, y=scramble(np.asarray(d["y"], float))) for d in dates], lib)
    for p, q in zip(a, b):
        assert p["ids"] == q["ids"] and np.array_equal(p["RQc"], q["RQc"]) and np.array_equal(p["hi"], q["hi"])


# ----------------------------------------------------------------------------------------------- gates / selection
def _summary(lib, t=None, ic=None, hi=None, q51=None, mono=None, h1=None, h2=None, bmax=None, months=None, nmean=None):
    g = lib.ncol
    f = lambda v, d: np.full(g, d, float) if v is None else np.asarray(v, float)  # noqa: E731
    return dict(n_dates=83, t_ic=f(t, 3.0), ic_mean=f(ic, 0.02), hi_ann=f(hi, 0.05), q5_minus_q1_ann=f(q51, 0.03),
                mono=f(mono, 1.0), half1=f(h1, 0.01), half2=f(h2, 0.01), block_max=f(bmax, 0.4),
                hi_months=f(months, 83), hi_n_mean=f(nmean, 5.0))


def test_d6_neighbourhood_and_selection_order(lib):
    s = _summary(lib)
    pick, g, ranked = K.select(s, lib, 2.5)
    assert g["qualified"].all() and lib.k[pick] == 2                               # smallest size first
    # D6: a feature carrying the whole signal fails the model
    ic = np.full(lib.ncol, 0.02)
    m = lib.models.index(("ACC", "MOM"))
    ic[lib.F + m] = 0.05
    ic[K.LIBRARY.index("ACC")] = 0.03                                              # drop MOM -> ACC 0.03 >= 0.02
    ic[K.LIBRARY.index("MOM")] = 0.019                                             # drop ACC -> MOM 0.019 < 0.02
    g2 = K.gates(_summary(lib, ic=ic), lib, 2.5)
    assert not g2["D6"][m]
    ic[K.LIBRARY.index("MOM")] = 0.021                                             # above 40% passes
    assert K.gates(_summary(lib, ic=ic), lib, 2.5)["D6"][m]
    # neighbourhood: kill every neighbour of one model
    q51 = np.full(lib.ncol, 0.03)
    for x in lib.nbr[m]:
        q51[lib.F + x] = -0.01
    g3 = K.gates(_summary(lib, q51=q51), lib, 2.5)
    assert not g3["N"][m] and g3["robust_nbrs"][m] == []
    # tie-break 2: highest median t of robust neighbours
    t = np.full(lib.ncol, 3.0)
    two = [i for i in range(lib.M) if lib.k[i] == 2]
    target = two[17]
    for x in lib.nbr[target]:
        t[lib.F + x] = 3.5
    pick, _, _ = K.select(_summary(lib, t=t), lib, 2.5)
    assert pick in two and np.median(t[[lib.F + x for x in lib.nbr[pick]]]) >= np.median(
        t[[lib.F + x for x in lib.nbr[two[0]]]])
    assert K.select(_summary(lib), lib, 99.0)[0] is None


def test_cstar_decides_candidate_existence(lib):
    for k, beta in enumerate((None, dict(ACC=0.01), dict(MOM=0.006, BM=0.006))):
        prep = K.prepare(fake_dates(seed=20 + k, D=60, n0=200, beta=beta), lib)
        for seed in (None, 3):
            s = G.summarise(G.world(prep, seed))
            cs = K.cstar(s, lib)
            for c in (0.5, 2.326, 3.0, 5.0, 10.0):
                assert (K.select(s, lib, c)[0] is not None) == (c < cs), (k, seed, c, cs)


def test_planted_signal_is_found_null_is_quiet_and_walk_forward_has_no_lookahead(lib):
    d0 = fake_dates(seed=40, beta=dict(ACC=0.012, BM=0.012))
    prep = K.prepare(d0, lib)
    ev = K.evaluate(prep, lib, 2.5, [2.5] * 4)
    assert ev["pick"] is not None and {"ACC", "BM"} & set(lib.models[ev["pick"]])
    assert ev["walk_forward"]["pseudo_oos"]["months"] == 47
    ns = G.summarise(G.world(prep, 5))
    assert ns["t_ic"][:lib.F + lib.M].max() < 6.0
    rng = np.random.default_rng(1)
    d1 = [dict(d, y=d["y"] if d["year"] < 2016 else rng.standard_normal(len(d["ids"])) * 0.1) for d in d0]
    wf0 = ev["walk_forward"]["folds"]
    wf1 = K.walk_forward(G.world(K.prepare(d1, lib)), lib, [2.5] * 4)["folds"]
    for a, b in zip(wf0[:2], wf1[:2]):
        assert (a["selected"], a["how"], a["train_t"]) == (b["selected"], b["how"], b["train_t"])


def test_critical_value_convention():
    rng = np.random.default_rng(1)
    v = rng.standard_normal(5000) + 2.0
    assert K.critical_value(v) == float(np.sort(v)[::-1][49]) == X.critical_value(list(v), 0.01)
    assert K.critical_value(np.zeros(5000)) == 2.326


# ----------------------------------------------------------------------------------------------- pins
def test_pins_and_constants():
    from qresearch import p9h024
    assert p9h024.SPEC_SHA256 == hashlib.sha256((ROOT / p9h024.SPEC).read_bytes()).hexdigest()
    for path, h in p9h024.CODE_SHA256.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == h, path
    assert hashlib.sha256((ROOT / "src/qresearch/lean/qr_h023.py").read_bytes()).hexdigest() == p9h024.ENGINE_SHA256
    assert p9h024.LIBRARY_CANDIDATES == K.LIBRARY
    c = p9h024.CONSTANTS
    assert (K.MAX_FEATURES, K.MODEL_BUDGET, K.SIZES, K.COVERAGE_MIN, K.REDUNDANCY_RHO, K.ENTRY, K.D6_FRAC, K.NBR_MIN,
            K.MIN_SECTOR_GROUP, K.FOLD_YEARS) == (c["MAX_FEATURES"], c["MODEL_BUDGET"], c["SIZES"], c["COVERAGE_MIN"],
                                                  c["REDUNDANCY_RHO"], c["ENTRY"], c["D6_FRAC"], c["NBR_MIN"],
                                                  c["MIN_SECTOR_GROUP"], c["FOLD_YEARS"])
    assert K.MIN_SECTOR_GROUP == S.MIN_SECTOR_GROUP and K.LARGE_DISTRIBUTION == S.LARGE_DISTRIBUTION
    assert (K.MOM_SKIP, K.MOM_LOOKBACK, K.VOL_WINDOW) == (S.MOM_SKIP, S.MOM_LOOKBACK, S.VOL_WINDOW)
    assert p9h024.PANEL_SHA256 == "09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0"
    assert p9h024.H022_RECORD["status"] == "REJECTED" and p9h024.H023_RECORD["status"] == "NO ROBUST SCORE V2 CANDIDATE"
    text = (ROOT / p9h024.SPEC).read_text()
    for must in ("DEVELOPMENT / TRAINING", "NO ROBUST H024 FEATURE MODEL", "c_IC_VALIDATION", "H024 VALIDATED",
                 "Prior exposure of the validation period", "Machine learning"):
        assert must in text


def test_thresholds_are_pinned_from_the_5000_null_worlds():
    import gzip
    import json
    from qresearch import p9h024
    path = ROOT / p9h024.NULL_RESULT
    assert hashlib.sha256(path.read_bytes()).hexdigest() == p9h024.NULL_RESULT_SHA256
    res = json.loads(path.read_text())
    ws = json.loads(gzip.open(ROOT / p9h024.NULL_WORLDS).read())
    assert hashlib.sha256((ROOT / p9h024.NULL_WORLDS).read_bytes()).hexdigest() == res["worlds_file_sha256"]
    assert [w["seed"] for w in ws] == list(p9h024.NULL_SEEDS)
    assert K.critical_value([w["max_t_feature"] for w in ws]) == p9h024.C_FEATURE == res["c_feature"] > 2.326
    assert K.critical_value([w["max_t_model"] for w in ws]) == p9h024.C_MODEL == res["c_model"] > 2.326
    for y in K.FOLD_YEARS:
        assert K.critical_value([w[f"max_t_model_fold{y}"] for w in ws]) == p9h024.C_FOLD[y] == res["c_fold"][str(y)]
    i = res["integrity"]
    assert i["completed"] == 5000 and i["seeds_exact"] and i["rerun_identical"] and i["zero_orders"]
    assert i["panel_equals_pinned"] and i["population_equals_pinned"] and i["models_equal_pinned"] and i["pit_audit_zero"]
    assert res["false_promotion"] == float(np.mean([w["cstar"] > p9h024.C_MODEL for w in ws]))


def test_p9_cp1_result_is_the_frozen_procedure_outcome():
    import json
    from qresearch import p9h024
    res = json.loads((ROOT / "research/phase9/cp1/P9_CP1_result.json").read_text())
    assert res["verdict"] == "NO ROBUST H024 FEATURE MODEL" and res["selected"] is None and res["candidate_sha256"] is None
    assert all(res["recompute"].values()) and res["orders"] == 0
    assert res["gate_counts"]["D1"] == 0 and res["gate_counts"]["qualified"] == 0 and len(res["models"]) == 415
    assert res["best_model"]["t_ic"] < p9h024.C_MODEL and res["best_feature"]["t_ic"] < p9h024.C_FEATURE
    assert p9h024.CANDIDATE is None
