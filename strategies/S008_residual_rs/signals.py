"""S008 (H008) pure signal functions. Windows end at the completed signal bar T (last element)."""


def _returns(closes):
    c = list(closes)
    return [c[i] / c[i - 1] - 1.0 for i in range(1, len(c)) if c[i - 1] > 0]


def residual_score(stock_closes, market_closes, window=252, skip=21, scaled=True, min_obs=None):
    """Regress the stock's daily returns on the market's over the `window` returns ending `skip`
    sessions before T (i.e. returns T-window+1 .. T-skip), and return the sum of the residuals,
    divided by their standard deviation if `scaled` (Blitz, Huij & Martens 2011). The two close
    windows must end on the same bar T. Returns None with fewer than `min_obs` observations
    (default: 80% of the window - skip returns, so v1.1's 6-1 month window is scored too)."""
    s, m = list(stock_closes), list(market_closes)
    n = min(len(s), len(m))
    if n < window + 1:
        return None
    if min_obs is None:
        min_obs = int(0.8 * (window - skip))
    rs, rm = _returns(s[-(window + 1):]), _returns(m[-(window + 1):])
    k = min(len(rs), len(rm))
    y, x = rs[-k:], rm[-k:]
    if skip > 0:
        y, x = y[:-skip], x[:-skip]
    if len(y) < min_obs:
        return None
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx <= 0:
        return None
    beta = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
    alpha = my - beta * mx
    resid = [b - (alpha + beta * a) for a, b in zip(x, y)]
    total = sum(resid)
    if not scaled:
        return total
    mr = total / len(resid)
    sd = (sum((e - mr) ** 2 for e in resid) / (len(resid) - 1)) ** 0.5
    return total / sd if sd > 0 else None


def monthly_targets(ranked, held, top_n, keep_n):
    """Monthly decision. ranked: symbols best first. Held names ranked within keep_n stay; other
    held names are exits. Entries fill free slots from the top of the ranking (top_n slots)."""
    keep = set(ranked[:keep_n])
    exits = [s for s in held if s not in keep]
    return exits, list(ranked)
