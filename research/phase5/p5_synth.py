"""P5-CP1 SYNTHETIC daily bars for plumbing tests and demo charts. SYNTHETIC ONLY: no market data, no returns analysed.

make_bars(seed, n, kind):
  'random' : a random walk with volatility clustering;
  'base'   : a scripted shape (uptrend -> base with shrinking pullbacks and falling volume -> breakout on volume at the
             last bar), so every chart element (pivots, zones, trendline, base, breakout) is exercised.
Calendar: business days from 2011-01-03 (labels only); week_id = ISO year * 100 + ISO week.
"""
import numpy as np


def calendar(n, start="2011-01-03"):
    d = np.arange(np.datetime64(start), np.datetime64(start) + 3 * n)
    d = d[np.is_busday(d)][:n]
    iso = [x.astype(object).isocalendar() for x in d]
    return d, np.array([y * 100 + w for y, w, _ in iso])


def _ohlc_from_close(c, rng, vol):
    o = np.r_[c[0], c[:-1]] * np.exp(rng.normal(0, vol * 0.3, c.size))
    hi = np.maximum(o, c) * np.exp(np.abs(rng.normal(0, vol * 0.5, c.size)))
    lo = np.minimum(o, c) * np.exp(-np.abs(rng.normal(0, vol * 0.5, c.size)))
    return o, hi, lo


def make_bars(seed=0, n=600, kind="random"):
    rng = np.random.default_rng(seed)
    if kind == "random":
        sig = 0.015 * np.exp(np.cumsum(rng.normal(0, 0.05, n)) * 0.3)
        r = rng.normal(0.0004, 1, n) * sig
        c = 50 * np.exp(np.cumsum(r))
        o, hi, lo = _ohlc_from_close(c, rng, 0.015)
        v = 1e6 * np.exp(rng.normal(0, 0.3, n))
    else:
        seg = [np.full(n - 220, 0.0012)]                           # long advance
        for move, length in ((-0.15, 25), (0.145, 30), (-0.10, 20), (0.095, 25), (-0.06, 15), (0.058, 20),
                             (-0.03, 10), (0.025, 74)):                # base: shrinking pullbacks below the left high
            seg.append(np.full(length, move / length))
        r = np.concatenate(seg)[:n - 1]
        r = r + rng.normal(0, 0.004, r.size) * np.linspace(1.5, 0.5, r.size)
        r = np.r_[0.0, r]
        r[-1] = 0.045                                              # breakout day
        c = 40 * np.exp(np.cumsum(r))
        o, hi, lo = _ohlc_from_close(c, rng, 0.006)
        hi[-1] = c[-1] * 1.002
        lo[-1] = o[-1] * 0.995
        v = 1e6 * np.exp(rng.normal(0, 0.2, n)) * np.r_[np.ones(n - 220), np.linspace(1.0, 0.6, 220)]
        v[-1] = v[-60:-1].mean() * 2.2
    d, wk = calendar(n)
    return dict(o=o, h=hi, l=lo, c=c, v=v, dates=d, week_id=wk)
