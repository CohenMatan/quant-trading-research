"""S011 (H011) pure signal functions. Inputs end at the completed signal bar T."""


def monthly_returns(month_closes):
    """{yyyymm: return} from consecutive completed month-end closes [[yyyymm, close], ...]."""
    out = {}
    mc = list(month_closes)
    for (ym0, c0), (ym1, c1) in zip(mc, mc[1:]):
        y0, m0 = divmod(ym0, 100)
        consecutive = (ym1 == ym0 + 1) if m0 < 12 else (ym1 == (y0 + 1) * 100 + 1)
        if consecutive and c0 > 0:
            out[ym1] = c1 / c0 - 1.0
    return out


def seasonal_score(month_closes, target_year, target_month, lags_years):
    """Average of the stock's returns in calendar month `target_month` over the previous
    `lags_years` years (target_year-1 ... target_year-lags). All lags are required, else None."""
    rets = monthly_returns(month_closes)
    vals = []
    for k in range(1, lags_years + 1):
        ym = (target_year - k) * 100 + target_month
        if ym not in rets:
            return None
        vals.append(rets[ym])
    return sum(vals) / len(vals)


def next_month(year, month):
    return (year + 1, 1) if month == 12 else (year, month + 1)
