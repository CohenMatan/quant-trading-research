"""S008 (H008) pure signal functions. Windows end at the completed signal bar T (last element).

Residual relative strength as in Blitz, Huij & Martens (2011), one-factor (SPY) version, D074 option A
(owner approval 2026-09-29). The market exposure (alpha, beta) is estimated over a LONG window of
`est` daily returns (36 months) ending at T-1; the score sums that regression's residuals over the
SHORTER formation window only (12-1 or 6-1 months), divided by their standard deviation. Because the
formation window is a strict part of the estimation window, its residuals do not sum to zero by
construction (the defect of the first version, which regressed and summed over the same window)."""

EST = 756          # 36 months of daily returns for alpha and beta (Blitz et al.)
MIN_EST = 600      # valid return pairs required in the estimation window; else unscorable


def _returns(closes):
    """Daily returns aligned to their end bar; None where the previous close is not positive."""
    c = list(closes)
    return [(c[i] / c[i - 1] - 1.0) if c[i - 1] > 0 else None for i in range(1, len(c))]


def residual_score(stock_closes, market_closes, window=252, skip=21, scaled=True, est=EST, min_est=MIN_EST):
    """Score at the close of T. Returns are indexed by their end bar; the last return ends at T.
    Estimation: OLS of stock on market returns over the `est` returns ending at T-1.
    Formation: the returns T-window+1 .. T-skip (12-1 months for window 252, skip 21).
    Score = sum of formation residuals (stock - alpha - beta x market), divided by their sample
    standard deviation if `scaled`. Needs est + 1 returns (est + 2 closes) in both windows, which must
    end on the same bar T; returns None (unscorable) otherwise, or with fewer than `min_est` valid
    estimation pairs or 80% of the formation days. No substitute history is ever used."""
    s, m = list(stock_closes), list(market_closes)
    if min(len(s), len(m)) < est + 2 or window > est or skip >= window:
        return None
    rs, rm = _returns(s[-(est + 2):]), _returns(m[-(est + 2):])      # est + 1 returns, last ends at T
    pairs = [(a, b) for a, b in zip(rm[:-1], rs[:-1]) if a is not None and b is not None]   # ending T-1
    if len(pairs) < min_est:
        return None
    n = len(pairs)
    mx = sum(a for a, _ in pairs) / n
    my = sum(b for _, b in pairs) / n
    sxx = sum((a - mx) ** 2 for a, _ in pairs)
    if sxx <= 0:
        return None
    beta = sum((a - mx) * (b - my) for a, b in pairs) / sxx
    alpha = my - beta * mx
    k = len(rs)
    form = [(rm[i], rs[i]) for i in range(k - window, k - skip)]        # returns T-window+1 .. T-skip
    resid = [b - (alpha + beta * a) for a, b in form if a is not None and b is not None]
    if len(resid) < 0.8 * (window - skip) or len(resid) < 2:
        return None
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
