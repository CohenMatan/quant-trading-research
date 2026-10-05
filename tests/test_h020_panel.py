"""H020 real-run plumbing (src/qresearch/lean/qr_h020_panel.py, qr_h020_diag.py): decision calendar, eligibility and
history rule, score table, momentum, total-shareholder-return responses (dividends, splits, delisting) and their
independent recomputation, truncation invariance, digests. SYNTHETIC data only."""
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research" / "phase5"))
import p5_synth as S  # noqa: E402
import qr_chart as C  # noqa: E402
import qr_h020_diag as HD  # noqa: E402
import qr_h020_panel as HP  # noqa: E402
import qr_h020_stats as HS  # noqa: E402

N = 5


def _calendar():
    d = np.arange(np.datetime64("2006-11-01"), np.datetime64("2011-06-30"))
    d = d[np.is_busday(d)]
    return d.astype(np.int64)


@pytest.fixture(scope="module")
def panel():
    cal = _calendar()
    D = cal.size
    rng = np.random.default_rng(5)
    O, H, L, Cl, V = (np.full((D, N), np.nan) for _ in range(5))
    for j in range(N):
        b = S.make_bars(seed=10 + j, n=D, kind="random")
        start = 0 if j != 3 else D - 300                       # stock 3 lists late: < 504 bars at every decision
        O[start:, j], H[start:, j], L[start:, j], Cl[start:, j], V[start:, j] = (
            b[k][start:] for k in ("o", "h", "l", "c", "v"))
    end4 = D - 120                                             # stock 4 delists inside the sample
    O[end4:, 4] = H[end4:, 4] = L[end4:, 4] = Cl[end4:, 4] = V[end4:, 4] = np.nan
    # raw prices with a 2:1 split for stock 0 at row s0 and quarterly dividends for stock 1
    s0 = D - 200
    mult = np.ones((D, N))
    mult[:s0, 0] = 0.5
    rawC = Cl / mult
    rawO = O / mult
    divs = [(r, 0.4, float(rawC[r - 1, 1])) for r in range(800, D, 63)]
    dm = np.ones((D, N))
    for b_, amt, ref in divs:
        dm[:b_, 1] *= 1 - amt / ref
    TRC, TRO = Cl * dm, O * dm
    rows = HP.decision_rows(cal, HP.H_PRIMARY)
    K = rows.size
    elig = np.zeros((K, N), bool)
    elig[::7] = True                                           # a subset of decisions keeps the test fast
    mcap = np.full((K, N), 3e9)
    sector = [["BusEq", "Money", "Hlth", "Shops", "Unclassified"] for _ in range(K)]
    T = HP.ScoreTable(cal, rows, elig, mcap, sector, O, H, L, Cl, V, TRC, TRO)
    return dict(cal=cal, rows=rows, elig=elig, T=T, O=O, H=H, L=L, Cl=Cl, V=V, TRC=TRC, TRO=TRO, rawC=rawC,
                rawO=rawO, s0=s0, divs=divs, D=D, mcap=mcap, sector=sector)


def test_decisions_are_iso_week_ends_from_2010_and_windows_end_in_sample(panel):
    cal, rows = panel["cal"], panel["rows"]
    wk = HP.iso_week_ids(cal)
    assert all(wk[r] != wk[r + 1] for r in rows)
    assert str(np.datetime64(int(cal[rows[0]]), "D")) == "2010-01-08"
    assert rows[-1] + HP.H_PRIMARY <= cal.size - 1
    later = HP.week_end_rows(cal)
    later = later[later > rows[-1]]
    assert later.size == 0 or later[0] + HP.H_PRIMARY > cal.size - 1


def test_history_rule_and_exclusions(panel):
    T = panel["T"]
    assert not T.scored[:, 3].any()                                  # < 504 own bars at every decision
    listed = T.rows >= panel["D"] - 300
    assert T.excl["history_lt_504"].sum() == int(panel["elig"][listed, 3].sum())   # listed, too short
    assert T.excl["no_bar_at_t"].sum() >= int(panel["elig"][~listed, 3].sum())     # eligible before its first bar
    assert (T.nbars[T.scored] >= C.MIN_SESSIONS).all()
    delisted = T.rows > panel["D"] - 120
    assert not T.scored[delisted, 4].any()                           # no bar at t after the delisting
    assert T.excl["no_bar_at_t"].sum() >= int(panel["elig"][delisted, 4].sum())


def test_score_table_matches_direct_snapshots(panel):
    T, cal = panel["T"], panel["cal"]
    for k in np.flatnonzero(T.scored[:, 0])[:3]:
        t = int(T.rows[k])
        rows = HP.clean_rows(panel["O"][:, 0], panel["H"][:, 0], panel["L"][:, 0], panel["Cl"][:, 0])
        sel = rows[rows <= t][-C.HIST_SESSIONS:]
        s = C.snapshot(*(panel[x][sel, 0] for x in ("O", "H", "L", "Cl", "V")), HP.iso_week_ids(cal)[sel])
        assert T.Q[k, 0] == C.quality_level(s) and T.G[k, 0] == C.score_group(s)
        assert T.bits[k, 0] == HP.cond_bits(s) and T.dq[k, 0] == HP.dq_bits(s)
        assert T.trend[k, 0] == (panel["Cl"][t, 0] > s["ma"]["ma40w"])


def test_responses_are_total_shareholder_returns_and_match_the_slow_path(panel):
    T, D = panel["T"], panel["D"]
    TRC, TRO = panel["TRC"], panel["TRO"]
    s0 = panel["s0"]
    splits = {0: [(s0, 0.5)], 1: [], 2: [], 4: []}
    divs = {0: [], 1: panel["divs"], 2: [], 4: []}
    n = 0
    for j in (0, 1, 2, 4):
        trows = np.flatnonzero(np.isfinite(TRC[:, j]) & (TRC[:, j] > 0))
        rws = np.flatnonzero(np.isfinite(panel["rawC"][:, j]))
        for k in np.flatnonzero(T.scored[:, j]):
            t = int(T.rows[k])
            for h in (HP.H_PRIMARY, HP.H_DIAG):
                if t + h > D - 1:
                    continue
                a = HP.response(TRC[:, j], TRO[:, j], trows, t, h)
                b = HP.response_slow(panel["rawC"][:, j], panel["rawO"][:, j], splits[j], divs[j], t, h, rws)
                assert a == pytest.approx(b, rel=1e-12, abs=1e-12)
                n += 1
            assert T.y[k, j] == pytest.approx(HP.response(TRC[:, j], TRO[:, j], trows, t, HP.H_PRIMARY))
    assert n > 20
    # the dividend payer's TSR exceeds its price return over a window containing an ex-date
    j = 1
    trows = np.flatnonzero(np.isfinite(TRC[:, j]))
    for k in np.flatnonzero(T.scored[:, j]):
        t = int(T.rows[k])
        if any(t + 1 < b <= t + HP.H_PRIMARY for b, _, _ in panel["divs"]):
            tsr = HP.response(TRC[:, j], TRO[:, j], trows, t, HP.H_PRIMARY)
            pr = panel["Cl"][t + HP.H_PRIMARY, j] / panel["O"][t + 1, j] - 1
            assert tsr > pr
            break
    else:
        pytest.fail("no dividend window")


def test_delisted_stock_is_valued_at_its_last_real_close():
    c = np.array([10.0, 10, 10, 11, 12, np.nan, np.nan, np.nan])
    o = np.array([10.0, 10, 10, 10.5, 11.5, np.nan, np.nan, np.nan])
    rows = np.flatnonzero(np.isfinite(c))
    assert HP.response(c, o, rows, 2, 5) == pytest.approx(12 / 10.5 - 1)
    assert np.isnan(HP.response(c, o, rows, 4, 3))                 # no bar at t+1: excluded


def test_momentum_convention():
    D = 400
    trc = np.linspace(10, 20, D)
    rows = np.arange(D)
    t = 300
    assert HP.momentum(trc, rows, t) == pytest.approx(trc[t - 21] / trc[t - 252] - 1)
    gap = np.setdiff1d(rows, np.arange(t - 260, t - 245))          # 15-session hole around t-252
    assert np.isnan(HP.momentum(trc, gap, t))


def test_chart_side_is_point_in_time_truncation(panel):
    """Cutting every array after a decision row leaves that decision's chart side unchanged."""
    T = panel["T"]
    k = int(np.flatnonzero(T.scored.any(axis=1))[5])
    cut = int(T.rows[k]) + 1
    a = {x: panel[x][:cut] for x in ("O", "H", "L", "Cl", "V", "TRC", "TRO")}
    rows = panel["rows"][:k + 1]
    rows = rows[rows < cut]
    T2 = HP.ScoreTable(panel["cal"][:cut], rows, panel["elig"][:rows.size], panel["mcap"][:rows.size],
                       panel["sector"][:rows.size], a["O"], a["H"], a["L"], a["Cl"], a["V"], a["TRC"], a["TRO"])
    for f in ("Q", "G", "bits", "dq", "trend", "scored"):
        assert np.array_equal(getattr(T2, f)[k], getattr(T, f)[k]), f


def test_digests_and_dates(panel):
    T = panel["T"]
    assert T.chart_digest() == T.chart_digest() and len(T.response_digest()) == 64
    dates = T.dates("y")
    assert len(dates) == T.rows.size
    for d in dates:
        assert np.all(np.isfinite(d["mom"])) and np.all(d["G"] >= 0)
    d13 = T.dates("y13", max_row=panel["D"] - 1 - HP.H_DIAG)
    assert all(d["row"] + HP.H_DIAG <= panel["D"] - 1 for d in d13)


def test_scale_free_comparison():
    b = S.make_bars(seed=3, n=700, kind="random")
    s1 = C.snapshot(b["o"], b["h"], b["l"], b["c"], b["v"], b["week_id"])
    s2 = C.snapshot(b["o"] * 7, b["h"] * 7, b["l"] * 7, b["c"] * 7, b["v"] / 7, b["week_id"])
    ex, rel = HP.compare_scale_free(HP.scale_free(s1), HP.scale_free(s2))
    assert ex and rel < 1e-9
    s3 = dict(HP.scale_free(s1))
    s3["score"] = s3["score"] + 1
    assert not HP.compare_scale_free(HP.scale_free(s1), s3)[0]


def test_bits_roundtrip():
    b = S.make_bars(seed=4, n=700, kind="base")
    s = C.snapshot(b["o"], b["h"], b["l"], b["c"], b["v"], b["week_id"])
    cb = HP.unpack(np.array([HP.cond_bits(s)]), 20)[0]
    assert [bool(x) for x in cb] == [s["conditions"][k] for k in C.CONDITIONS]
    db = HP.unpack(np.array([HP.dq_bits(s)]), 5)[0]
    assert [bool(x) for x in db] == [s["disqualifiers"][k] for k in C.DISQUALIFIERS]


def test_diagnostics_run_on_synthetic_panel(panel):
    T = panel["T"]
    dates = [d for d in T.dates("y") if d["ids"].size]
    sd = HD.score_distribution(T, dates)
    assert sum(sd["Q_all"]) == sum(sd["G_all"]) == sum(d["ids"].size for d in dates)
    cf = HD.condition_frequencies(T, dates)
    assert len(cf["cond"]) == 20 and len(cf["dq"]) == 5
    HD.relationships(T, dates)                                     # runs (few stocks: correlations mostly skipped)


def test_sector_diagnostic_regression_reduces_to_g5_without_dummies():
    """With a single sector the dummy is collinear with the intercept and omitted: the sector-adjusted coefficient
    equals the frozen G5 coefficient exactly."""
    sys.path.insert(0, str(ROOT / "research" / "phase5"))
    import h020_synth_panel as SP
    dates = SP.make_dates(n_dates=40, n_stocks=60, edge_ic=0.05, seed=2)

    class Tab:
        sector = None
    tab = Tab()
    tab.sector = {}
    for k, d in enumerate(dates):
        d["k"] = k
        tab.sector[k] = {int(i): "BusEq" for i in d["ids"]}
    tab.sector = [tab.sector[k] for k in range(len(dates))]
    tab.sector = [[s.get(i, "BusEq") for i in range(60)] for s in tab.sector]
    prep = HS.prepare(dates)
    ser = HD.sector_series(tab, prep, dates)
    g5 = [HS.fast_date_stats(p)["inc"] for p in prep]
    assert np.allclose(ser, g5, atol=1e-12)
