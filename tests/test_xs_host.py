"""H019 host X985 on a fake harness (SYNTHETIC data only): the panel assembled from RAW / SCALED_RAW / split-event
histories equals the panel built directly from the true split-adjusted and total-return series (split alignment,
misdated events, dividends, IPOs, delistings), and the canary / null / real modes publish what the spec says.
Also the pure helpers of qr_xs_panel and qr_xs_diag."""
import json
import sys
import types
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from conftest import ROOT, load_module

sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
import qr_xs as X  # noqa: E402
import qr_xs_diag as XD  # noqa: E402
import qr_xs_panel as XP  # noqa: E402


# ---------------------------------------------------------------- pure helpers
def test_session_days_shift_midnight_stamps_to_the_session():
    t = pd.to_datetime(["2014-06-10 00:00", "2014-06-09 16:00", "2014-06-09 00:00"]).values
    d = XP.session_days(t).astype("datetime64[D]")
    assert [str(x) for x in d] == ["2014-06-09", "2014-06-09", "2014-06-08"]
    e = XP.event_days(pd.to_datetime(["2014-06-09 00:00"]).values).astype("datetime64[D]")
    assert str(e[0]) == "2014-06-09"


def test_month_ends():
    cal = np.array(["2010-01-28", "2010-01-29", "2010-02-01", "2010-02-26", "2010-03-01"], "datetime64[D]").astype(np.int64)
    months, me = XP.month_ends(cal)
    assert months == [(2010, 1), (2010, 2), (2010, 3)] and me == [1, 3, 4]


def _series(D=60, split_at=30, f=0.5, div_at=40, d=0.02):
    q = 100 * np.exp(np.cumsum(np.random.default_rng(1).normal(0, 0.01, D)))   # true split-adjusted closes
    raw = q.copy()
    raw[:split_at] /= f                                                           # pre-split raw prices are higher
    div = np.ones(D)
    div[:div_at] *= 1 - d
    return q, raw, q * div


def test_split_multiplier_aligned_realigned_unverified():
    q, raw, sc = _series()
    m, st = XP.split_multiplier(raw, sc, [(30, 0.5)])
    assert st == dict(n=1, aligned=1, realigned=0, unverified=0, outside=0)
    assert np.allclose(raw * m, q)
    m, st = XP.split_multiplier(raw, sc, [(32, 0.5)])                            # event stamped two rows late
    assert st["realigned"] == 1 and np.allclose(raw * m, q)
    m, st = XP.split_multiplier(raw, sc, [(30, 0.25)])                           # wrong factor: kept, flagged
    assert st["unverified"] == 1
    raw2 = raw.copy()
    raw2[25:35] = np.nan                                                          # no bars around the split
    sc2 = sc.copy()
    sc2[25:35] = np.nan
    m, st = XP.split_multiplier(raw2, sc2, [(30, 0.5)])
    assert st["aligned"] == 1 and np.allclose((raw2 * m)[np.isfinite(raw2)], q[np.isfinite(raw2)])
    m, st = XP.split_multiplier(raw, sc, [(80, 0.5)])                            # after the last bar
    assert st["outside"] == 1 and np.allclose(raw * m / (raw * m)[-1], raw / raw[-1])


def test_residual_jumps():
    q, raw, sc = _series()
    assert XP.residual_jumps(q, sc) == (0, 0)
    assert XP.residual_jumps(raw, sc) == (0, 1)                                   # an unadjusted 2:1 split is flagged


def test_ff12_and_helpers():
    assert XD.ff12(None) == "Unclassified" and XD.ff12(6020) == "Money" and XD.ff12(7372) == "BusEq"
    assert XD.ff12(2834) == "Hlth" and XD.ff12(1311) == "Enrgy" and XD.ff12(9999) == "Other"
    x = np.random.default_rng(0).normal(size=200)
    assert XD.effective_sample(x)["ess"] == pytest.approx(200, rel=0.35)
    ids = np.arange(100)
    s = np.arange(100, dtype=float)
    assert XD.retention(ids, s, ids, s, 10) == 1.0 and XD.rank_autocorr(ids, s, ids, s) == pytest.approx(1.0)
    pret = np.random.default_rng(2).normal(size=300)
    key = np.random.default_rng(3).normal(size=300)
    assert XD.s2_structure_violations(pret, key, X.smooth_momentum_score(pret, key)) == 0
    assert XD.s2_structure_violations(pret, key, X.smooth_momentum_score(pret, -key)) > 0
    g = np.repeat(np.arange(4), 25)
    y = np.random.default_rng(4).normal(size=100) + g                             # pure sector effect
    assert abs(XD.group_demeaned_corr(g + 0.0 + 1e-9 * np.arange(100), y, g)) < 0.5


# ---------------------------------------------------------------- synthetic market for the fake harness
class Sym:
    def __init__(self, sid):
        self.id = sid
        self.value = sid

    def __lt__(self, o):
        return self.id < o.id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, o):
        return isinstance(o, Sym) and o.id == self.id

    def __repr__(self):
        return self.id


def _end_scale(c, alive):
    """Per-stock value of c on the stock's last live row (the host divides every row by SCALED / RAW there)."""
    last = np.array([np.flatnonzero(alive[:, j])[-1] if alive[:, j].any() else 0 for j in range(c.shape[1])])
    return c[last, np.arange(c.shape[1])]


def _market(N=70, seed=7):
    rng = np.random.default_rng(seed)
    cal = np.arange(np.datetime64("2005-11-01"), np.datetime64("2017-12-30"))
    cal = cal[np.is_busday(cal)]
    D = cal.size
    born = np.zeros(N, int)
    died = np.full(N, D)
    ipo = rng.random(N) < 0.2
    born[ipo] = rng.integers(200, D - 400, ipo.sum())
    dl = rng.random(N) < 0.15
    died[dl] = rng.integers(1500, D - 30, dl.sum())
    lr = rng.normal(0.0003, 0.018, (D, N)) + rng.normal(0, 0.01, D)[:, None]
    Qt = 40 * np.exp(np.cumsum(lr, axis=0))                                      # true split-adjusted closes
    alive = (np.arange(D)[:, None] >= born) & (np.arange(D)[:, None] < died)
    Qt[~alive] = np.nan
    divf = np.ones((D, N))
    spin = np.ones((D, N))
    divs = {j: [] for j in range(N)}
    splits = {j: [] for j in range(N)}
    for j in range(N):
        for t in rng.choice(np.arange(5, D), size=24, replace=False):             # quarterly-ish cash dividends
            y = rng.uniform(0.002, 0.01)
            divf[:t, j] *= 1 - y
            divs[j].append((int(t), 100.0 * y, 100.0))                             # (row, distribution, reference)
        if rng.random() < 0.35:
            for t in rng.choice(np.arange(300, D - 5), size=rng.integers(1, 3), replace=False):
                splits[j].append((int(t), float(rng.choice([0.5, 1 / 7, 2.0, 1 / 3]))))
        if rng.random() < 0.1:              # spin-off: a price factor, carried in QuantConnect's DIVIDEND feed
            t, g = int(rng.integers(300, D - 5)), rng.uniform(0.4, 0.7)
            spin[:t, j] *= g
            divs[j].append((t, 100.0 * (1 - g), 100.0))
    split_mult = np.ones((D, N))
    for j, ev in splits.items():
        for t, f in ev:
            split_mult[:t, j] *= f
    RAW = Qt / split_mult
    SC = Qt * divf * spin
    SO = SC * np.exp(rng.normal(0, 0.004, (D, N)))
    SO[~alive] = np.nan
    RAWO = SO / (split_mult * divf * spin)                                         # raw opens
    Pt, Ot = SC.copy(), SO.copy()                                                  # true total-return closes / opens
    late = 5                                                                       # a factor dated after the end
    SC[:, late] *= 0.99
    SO[:, late] *= 0.99
    return dict(cal=cal, Qt=Qt, RAW=RAW, SC=SC, SO=SO, splits=splits, divs=divs, alive=alive, born=born, N=N,
                Qc=Qt, Pn=Pt, On=Ot, RAWO=RAWO)


def _ts(days):
    """Daily bars are stamped with their END time (midnight after the session)."""
    return pd.to_datetime(days.astype("datetime64[ns]")) + pd.Timedelta(days=1)


def _fake_env(monkeypatch, M, mode, params=None, misdate=None):
    ai = types.ModuleType("AlgorithmImports")
    ai.Resolution = types.SimpleNamespace(DAILY="daily")
    ai.DataNormalizationMode = types.SimpleNamespace(RAW="raw", SCALED_RAW="scaled")

    class Split:
        pass

    class Dividend:
        pass
    ai.Split = Split
    ai.Dividend = Dividend
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    h = types.ModuleType("qr_harness")
    syms = [Sym(f"S{j:03d}") for j in range(M["N"])]
    spy = Sym("SPY")

    class QRAlgorithm:
        def __init__(self):
            self.qr_params = dict(mode=mode, **(params or {}))
            self.qr = {"end": "2017-12-31"}
            self.qr_sec = object()
            self.qr_sic = types.SimpleNamespace(sic_on=lambda sid, d: 2000 + 100 * (int(sid[1:]) % 12))
            self.spy = spy
            self.msgs = []
            self._qr_log_budget = 0

        def _qr_log(self, line):
            self.msgs.append(line)

        def history(self, what, *a, **kw):
            cal = M["cal"]
            if what is spy:
                return pd.DataFrame({"close": np.ones(cal.size)},
                                    index=pd.MultiIndex.from_arrays([[spy] * cal.size, _ts(cal)]))
            if what is Split:
                part = a[0]
                rows, ix_s, ix_t = [], [], []
                for s in part:
                    j = int(s.id[1:])
                    for t, f in M["splits"][j]:
                        day = cal[t] + (1 if misdate == j else 0)
                        for typ, ref in (("WARNING", 0.0), ("SPLIT_OCCURRED", 12.5)):
                            ix_s.append(s)
                            ix_t.append(pd.Timestamp(day - (1 if typ == "WARNING" else 0)))
                            rows.append(dict(splitfactor=f, type=typ, referenceprice=ref, value=ref))
                if not rows:
                    return pd.DataFrame()
                return pd.DataFrame(rows, index=pd.MultiIndex.from_arrays([ix_s, ix_t]))
            if what is Dividend:
                rows, ix_s, ix_t = [], [], []
                for s in a[0]:
                    j = int(s.id[1:])
                    for t, amt, ref in M["divs"][j]:
                        ix_s.append(s)
                        ix_t.append(pd.Timestamp(cal[t]))
                        rows.append(dict(distribution=amt, referenceprice=ref, value=amt))
                return pd.DataFrame(rows, index=pd.MultiIndex.from_arrays([ix_s, ix_t])) if rows else pd.DataFrame()
            part = what
            mode_ = kw["data_normalization_mode"]
            ix_s, ix_t, cl, op = [], [], [], []
            for s in part:
                j = int(s.id[1:])
                ok = M["alive"][:, j]
                src = M["RAW"] if mode_ == "raw" else M["SC"]
                ix_s += [s] * int(ok.sum())
                ix_t += list(_ts(cal[ok]))
                cl += list(src[ok, j])
                op += list((M["RAWO"] if mode_ == "raw" else M["SO"])[ok, j])
            return pd.DataFrame({"close": cl, "open": op}, index=pd.MultiIndex.from_arrays([ix_s, ix_t]))

    h.QRAlgorithm = QRAlgorithm
    monkeypatch.setitem(sys.modules, "qr_harness", h)
    mod = load_module(ROOT / "strategies/X985_h019_xs/main.py", f"x985_{mode}")
    a = mod.H019XS()
    a.qr_initialize()
    cal = M["cal"]
    for r in range(cal.size):
        d = cal[r].astype(datetime)
        if d < date(2010, 1, 4):
            continue
        prev = r - 1
        el = [syms[j] for j in range(M["N"]) if M["alive"][prev, j] and prev - M["born"][j] >= 20]
        a.qr_eligible = el
        a.qr_eligible_info = {s: (3e9 + 1e7 * int(s.id[1:]), 1e7) for s in el}
        a.time = datetime(d.year, d.month, d.day, 16, 0)
        a.qr_on_close(None)
    return a, syms


def _direct_features(M, a):
    """The panel built directly from the TRUE series and the host's month-end eligibility."""
    months, me = XP.month_ends(M["cal"].astype(np.int64))
    elig = a.xs_panel.elig
    c = [int(sid[1:]) for sid in a.xs_sids]
    return X.Features(X.Panel(M["Qc"][:, c], M["Pn"][:, c], M["On"][:, c], me, months, elig))


@pytest.fixture(scope="module")
def market():
    return _market()


def test_host_panel_equals_direct_panel_and_canary(monkeypatch, market):
    md = min(j for j, ev in market["splits"].items()
             if ev and all(market["alive"][t, j] and market["alive"][t - 1, j] for t, _ in ev) and market["born"][j] == 0
             and market["alive"][-1, j])
    a, syms = _fake_env(monkeypatch, market, "canary", dict(timing_worlds=2), misdate=md)
    a.qr_on_end()
    st = a.xs_st["panel"]
    sp = st["split"]
    cols = [int(sid[1:]) for sid in a.xs_sids]
    assert sp["n"] == sum(len(market["splits"][j]) for j in cols) and sp["unverified"] == 0
    assert md in cols and sp["realigned"] == len(market["splits"][md]) > 0        # the misdated events
    assert st["late_rows"] == 0 and st["unknown_day_rows"] == 0 and st["month_end_date_mismatches"] == []
    def scale_at_end(j):
        r = np.flatnonzero(market["alive"][:, j])[-1]
        return market["SC"][r, j] / market["RAW"][r, j]
    assert st["factor_steps_small"] == 0 and st["factor_steps_big"] == 0           # SCALED_RAW cross-check agrees
    assert st["split_unverified_without_same_day_distribution"] == 0
    assert st["last_scale_not_one"] == sum(abs(scale_at_end(j) - 1) > 1e-6 for j in cols) > 0
    spun = [j for j in cols if any(amt > 25.0 for _, amt, _r in market["divs"][j])]
    assert st["large_distributions"] == len(spun) > 0
    ex = st["large_distribution_exposure"]
    assert 0 < ex["exposed"] < ex["observations"] and ex["stocks"] <= len(spun)
    F, G = a.xs_F, _direct_features(market, a)
    assert np.array_equal(F.dom, G.dom) and np.array_equal(F.full, G.full)
    for name in ("pret", "idm", "A", "reg"):
        x, y = getattr(F, name), getattr(G, name)
        assert np.array_equal(np.isfinite(x), np.isfinite(y))
        assert np.nanmax(np.abs(x - y)) < 1e-9
    for hh in F.fwd:
        assert np.nanmax(np.abs(F.fwd[hh] - G.fwd[hh])) < 1e-12
    # the first research month-end is 2010-01 and every research month has a snapshot dated on its last session
    assert st["research_months_recorded"][0] == "2010-01" and st["research_months_recorded"][-1] == "2017-12"
    assert st["fwd_end_last_decision"] == "2017-12-29"
    k = [ln for ln in a.msgs if ln.startswith("K|")]
    assert len(k) == 1 and not [ln for ln in a.msgs if ln.startswith(("R|", "N|"))]
    ck = json.loads(k[0][2:])
    assert ck["decisions"] == 83 and ck["slow_features"]["nan_mismatch"] == 0
    assert ck["slow_features"]["pret"] < 1e-9 and ck["slow_features"]["A"] < 1e-9
    assert ck["regressions"]["max_abs"] < 1e-6
    assert ck["s3_slow_max_abs"] < 1e-6 and ck["s2_structure_violations"] == 0 and ck["id_range_ok"]
    assert ck["truncation"]["max_abs"] == 0 and ck["truncation"]["betas_max_abs"] == 0
    assert ck["truncation"]["id_mismatch"] == 0 and ck["truncation"]["dates"] == ck["truncation"]["dates_full"]
    assert ck["planted"]["h1"]["ic_min"] > 0.999 and ck["planted"]["h3"]["ic_min"] > 0.999
    assert ck["planted"]["h1"]["dates"] == 83 and ck["planted"]["h3"]["dates"] == 81
    assert ck["null_repeat_identical"] is True
    summ = [ln for ln in a.msgs if ln.startswith("QRX985|summary|")]
    assert len(summ) == 1


def test_host_null_and_real_modes_match_run_world(monkeypatch, market):
    a, _ = _fake_env(monkeypatch, market, "null", dict(seeds=[1, 2]))
    a.qr_on_end()
    G = _direct_features(market, a)
    lines = [ln for ln in a.msgs if ln.startswith("N|")]
    assert [ln.split("|")[1] for ln in lines] == ["1", "2"]
    w = json.loads(lines[0].split("|", 2)[2])
    ref = X.run_world(G, seed=1)
    assert w["F"] == pytest.approx(X.family_stat(ref), rel=1e-6)
    assert w["S3"]["t_inc"] == pytest.approx(ref["S3"]["t_inc"], rel=1e-6)
    with pytest.raises(Exception):
        _fake_env(monkeypatch, market, "real")                                    # no pinned provenance
    prov = dict(threshold_c=2.7, threshold_commit="abc", null_result_sha256="0" * 64, spec_sha256="1" * 64)
    a, _ = _fake_env(monkeypatch, market, "real", prov)
    a.qr_on_end()
    r = json.loads([ln for ln in a.msgs if ln.startswith("R|")][0][2:])
    ref = X.run_world(G)
    for s in X.SIGNALS:
        assert r[s]["t"] == pytest.approx(ref[s]["t"], rel=1e-8)
        assert r[s]["top_ann"] == pytest.approx(ref[s]["top_ann"], rel=1e-8)
    order = [ln.split("|")[0] for ln in a.msgs if ln.split("|")[0] in ("R", "RS", "RD", "R3")]
    assert order == ["R", "RS", "RD", "R3"]                                       # the 3-month diagnostic comes last
    d = json.loads([ln for ln in a.msgs if ln.startswith("RD|")][0][3:])
    assert set(d) >= {"per_year", "calendar_subperiods", "sector_neutral_ic", "size_half_ic", "signal_corr",
                      "turnover", "tf_decomposition", "tf_expected_beta_path", "realised_power"}
    assert len(d["tf_expected_beta_path"]["rows"]) == 83
    assert a.xs_st["provenance"] == prov
    with pytest.raises(Exception):
        _fake_env(monkeypatch, market, "null", dict(seeds=[4990, 5010]))           # outside the official seeds


# ---------------------------------------------------------------- configs and runner wiring
def _cfg(**kw):
    c = json.loads((ROOT / "experiments/E985-01/config.json").read_text())
    c.update(kw)
    return c


def test_h019_config_rules():
    from qresearch import experiment, p4xs, run
    experiment.validate(_cfg())
    files = run.assemble_files(_cfg(), None, False)
    assert {"qr_xs.py", "qr_xs_diag.py", "qr_xs_panel.py"} <= set(files)
    for bad in (dict(end="2018-01-31"), dict(start="2010-03-01"), dict(warmup_start="2009-01-02"),
                dict(params=dict(mode="null", seeds=[1, 1000])), dict(kind="research", split="IS")):
        with pytest.raises(experiment.ConfigError):
            experiment.validate(_cfg(**bad))
    s = dict(strategy_id="S020", strategy_dir="strategies/X985_h019_xs", experiment_id="E020-01", hypothesis_id="H019",
             owner_approval_required="H019 null (owner 2026-10-04)", params=dict(mode="null", seeds=[1, 1000]))
    experiment.validate(_cfg(**s))
    for bad in (dict(params=dict(mode="null", seeds=[1, 999])), dict(owner_approval_required=None),
                dict(params=dict(mode="canary")), dict(kind="research", split="IS")):
        with pytest.raises(experiment.ConfigError):
            experiment.validate(_cfg(**{**s, **bad}))
    real = dict(s, experiment_id="E020-06", kind="research", split="IS",
                params=dict(mode="real", threshold_c=2.7, threshold_commit="x", null_result_sha256="y",
                            spec_sha256=p4xs.SPEC_SHA256))
    experiment.validate(_cfg(**real))
    with pytest.raises(experiment.ConfigError):
        experiment.validate(_cfg(**{**real, "params": dict(mode="real")}))


def test_s020_is_a_byte_copy_of_the_canary_verified_host_and_null_configs_valid():
    from qresearch import experiment, p4xs
    assert (ROOT / "strategies/S020_h019_xs/main.py").read_bytes() == (ROOT / "strategies/X985_h019_xs/main.py").read_bytes()
    for i, (a, b) in enumerate(p4xs.NULL_BATCHES):
        c = json.loads((ROOT / f"experiments/E020-{i + 1:02d}/config.json").read_text())
        experiment.validate(c)
        assert c["params"] == dict(mode="null", seeds=[a, b]) and c["kind"] == "infrastructure"
