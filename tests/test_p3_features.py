"""Phase 3 features (qr_p3_features) and grammar (qr_p3_grammar): every indicator against an independent loop
implementation, point-in-time truncation (a feature for day t uses no bar after t), the frozen configuration count,
ids, the neighbourhood graph and the composed configuration masks."""
import math
from collections import Counter

import numpy as np
import pytest

from conftest import ROOT, load_module

F = load_module(ROOT / "src/qresearch/lean/qr_p3_features.py", "qr_p3_features_t")
G = load_module(ROOT / "src/qresearch/lean/qr_p3_grammar.py", "qr_p3_grammar_t")


def panel(S=12, L=F.WINDOW, seed=1):
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0004, 0.02, (S, L))
    c = 50 * np.exp(np.cumsum(r, axis=1))
    h = c * (1 + np.abs(rng.normal(0, 0.01, (S, L))))
    l = c * (1 - np.abs(rng.normal(0, 0.01, (S, L))))
    v = rng.lognormal(13, 0.4, (S, L))
    spy = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, L)))
    return c, h, l, v, spy


def rsi_ref(x, n, span):
    d = np.diff(x[-span - 1:])
    ag = np.mean(np.clip(d[:n], 0, None))
    al = np.mean(np.clip(-d[:n], 0, None))
    for i in range(n, span):
        ag = (ag * (n - 1) + max(d[i], 0)) / n
        al = (al * (n - 1) + max(-d[i], 0)) / n
    return 100 - 100 / (1 + ag / al) if al > 0 else 100.0


def ema_ref(x, n):
    a = 2 / (n + 1)
    e = np.mean(x[:n])
    out = [np.nan] * (n - 1) + [e]
    for v in x[n:]:
        e = a * v + (1 - a) * e
        out.append(e)
    return np.array(out)


def adx_ref(H, L, C, n, span):
    H, L, C = H[-span - 1:], L[-span - 1:], C[-span - 1:]
    tr, pdm, ndm = [], [], []
    for i in range(1, len(C)):
        up, dn = H[i] - H[i - 1], L[i - 1] - L[i]
        pdm.append(up if up > dn and up > 0 else 0.0)
        ndm.append(dn if dn > up and dn > 0 else 0.0)
        tr.append(max(H[i] - L[i], abs(H[i] - C[i - 1]), abs(L[i] - C[i - 1])))
    atr, sp, sn = sum(tr[:n]), sum(pdm[:n]), sum(ndm[:n])
    dx = []
    for i in range(n, span):
        atr = atr - atr / n + tr[i]
        sp = sp - sp / n + pdm[i]
        sn = sn - sn / n + ndm[i]
        pdi, ndi = 100 * sp / atr, 100 * sn / atr
        dx.append(100 * abs(pdi - ndi) / (pdi + ndi) if pdi + ndi > 0 else 0.0)
    a = np.mean(dx[:n])
    for x in dx[n:]:
        a = (a * (n - 1) + x) / n
    return a


def test_indicators_match_reference_loops():
    c, h, l, v, spy = panel()
    f = F.features(c, h, l, v, spy)
    for i in range(len(c)):
        x = c[i]
        assert f["sma200"][i] == pytest.approx(x[-200:].mean())
        assert f["slope100"][i] == pytest.approx(x[-100:].mean() / x[-121:-21].mean() - 1)
        assert f["rets252"][i] == pytest.approx(x[-22] / x[-22 - 252] - 1)
        assert f["ret63"][i] == pytest.approx(x[-1] / x[-64] - 1)
        assert f["xret126"][i] == pytest.approx(x[-1] / x[-127] - 1 - (spy[-1] / spy[-127] - 1))
        assert f["max126"][i] == pytest.approx(x[-126:].max())
        for n in (2, 5, 14):
            assert f[f"rsi{n}"][i] == pytest.approx(rsi_ref(x, n, F.RSI_SPAN))
        w = x[-20:]
        assert f["pctb"][i] == pytest.approx((w[-1] - (w.mean() - 2 * w.std())) / (4 * w.std()))
        e12, e26 = ema_ref(x[-200:], 12), ema_ref(x[-200:], 26)
        line = e12 - e26
        assert f["macd"][i] == pytest.approx(line[-1])
        assert f["macdsig"][i] == pytest.approx(ema_ref(line[25:], 9)[-1])
        assert f["adx14"][i] == pytest.approx(adx_ref(h[i], l[i], x, 14, F.RSI_SPAN))
        assert f["vol63"][i] == pytest.approx(np.std(np.diff(np.log(x[-64:])), ddof=1))
        assert f["rv"][i] == pytest.approx(v[i, -20:].mean() / v[i, -120:].mean())


def test_truncation_no_bar_after_today_is_used():
    c, h, l, v, spy = panel(L=F.WINDOW + 30)
    t = F.WINDOW + 10                                     # "today" = column t - 1 of the long history
    a = F.features(c[:, t - F.WINDOW:t], h[:, t - F.WINDOW:t], l[:, t - F.WINDOW:t], v[:, t - F.WINDOW:t], spy[:t])
    c2 = c.copy()
    c2[:, t:] *= 3.0                                      # change the future: nothing for day t may move
    b = F.features(c2[:, t - F.WINDOW:t], h[:, t - F.WINDOW:t], l[:, t - F.WINDOW:t], v[:, t - F.WINDOW:t], spy[:t])
    for k in a:
        assert np.allclose(a[k], b[k], equal_nan=True), k


def test_short_history_makes_conditions_false():
    c, h, l, v, spy = panel()
    c[0, :-150] = np.nan                                  # stock 0 has only 150 bars
    f = F.features(c, h, l, v, spy)
    assert np.isnan(f["sma200"][0]) and np.isnan(f["rets252"][0]) and np.isfinite(f["sma100"][0])
    m, _ = F.primary(f, "T1", {"L": 200})
    assert not m[0]
    assert not F.confirm(f, "cT_sma200", {})[0]


def test_grammar_is_the_frozen_finite_space():
    C = G.enumerate_configs()
    assert len(C) == 1533 and len({c["id"] for c in C}) == 1533
    fam = Counter(c["primary"][1] for c in C)
    assert fam == {"trend": 297, "momentum": 495, "breakout": 405, "pullback": 336}
    for c in C:                                           # confirmation always from a different information family
        assert c["confirm"] is None or c["confirm"][1] != c["primary"][1]
        assert G.complexity(c)[0] <= 3
    nb = G.neighbours(C)
    assert all(a in nb[b] for a, v in nb.items() for b in v)        # symmetric
    assert min(len(v) for v in nb.values()) >= 2 and max(len(v) for v in nb.values()) <= 7
    assert G.enumerate_configs() == C                                # deterministic order and ids


def test_neighbours_differ_by_exactly_one_step():
    C = G.enumerate_configs()
    by = {c["id"]: c for c in C}
    nb = G.neighbours(C)
    for cid in list(nb)[::37]:
        a = by[cid]
        for o in nb[cid]:
            b = by[o]
            diffs = 0
            diffs += a["primary"][0] != b["primary"][0]
            diffs += sum(abs(x - y) for x, y in zip(a["primary"][2], b["primary"][2]))
            ca, cb = a["confirm"], b["confirm"]
            if (ca is None) != (cb is None) or (ca and ca[0] != cb[0]):
                diffs += 5
            elif ca:
                diffs += sum(abs(x - y) for x, y in zip(ca[2], cb[2]))
            diffs += abs(a["risk"] - b["risk"])
            assert diffs == 1


def test_signal_table_composes_masks_from_base_conditions():
    c, h, l, v, spy = panel(S=40)
    f = F.features(c, h, l, v, spy)
    C = G.enumerate_configs()
    T = F.SignalTable(C, G.PRIMARY_TYPES, G.CONFIRM_TYPES, G.RISK_LEVELS)
    masks, strength, p_of = T.evaluate(f)
    assert masks.shape == (1533, 40) and strength.shape[0] == len(T.pv) == 41
    for i in (0, 100, 777, 1532):
        cf = C[i]
        pm, ps = F.primary(f, cf["primary"][0], G.params_of(G.PRIMARY_TYPES, cf["primary"][0], cf["primary"][2]))
        m = pm.copy()
        if cf["confirm"] is not None:
            m &= F.confirm(f, cf["confirm"][0], G.params_of(G.CONFIRM_TYPES, cf["confirm"][0], cf["confirm"][2]))
        m &= F.risk(f, G.RISK_LEVELS[cf["risk"]])
        assert (masks[i] == m).all()
        assert np.allclose(strength[p_of[i]], ps, equal_nan=True)


def test_momentum_rank_top_fraction():
    f = {"rets63": np.array([0.1, 0.5, np.nan, 0.3, -0.2, 0.4, 0.0, 0.2, 0.05, 0.6]), "close": np.ones(10)}
    m, s = F.primary(f, "M1", {"K": 63, "q": 0.30})
    assert m.sum() == math.floor(0.3 * 9 + 0.5) and set(np.nonzero(m)[0]) == {1, 5, 9}
