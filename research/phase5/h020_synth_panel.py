"""H020 SYNTHETIC decision panels for the statistics / null / power tests (P5-CP2 sections 27-30). No market data, no
chart of any real stock, no real return: latent variables only.

Each stock has a latent chart quality z (AR(1) across weekly decisions) and a latent momentum m (AR(1)); corr(z, m) =
rho. Weekly returns r = a_z * z + a_m * m + sigma * e; the 4-week response y at decision w = r[w+1] + ... + r[w+4] (so
consecutive responses overlap by 3 weeks, as in the real design); y13 likewise over 13 weeks. Score Q = round(10 + 4 z)
clipped to 0..20; disqualified (Q = -1) when z < -1.6; G from Q as in qr_chart.score_group; mom = m + small noise; trend
= 1{m > -0.3}. Universe membership is a persistent two-state chain (a member leaves with probability `churn` per
week, a non-member returns with probability 10 x churn; about 10% of names are absent at any time) so entries / exits
exercise the tether as in a real >= $2B universe.
`edge_ic` sets a_z so that the per-date rank IC of z with y is about edge_ic (4-week horizon)."""
import math

import numpy as np

WEEKS_PER_YEAR = 52


def _group(Q):
    return np.where(Q < 0, 0, np.where(Q <= 5, 1, np.where(Q <= 10, 2, np.where(Q <= 15, 3, 4))))


def make_dates(n_dates=417, n_stocks=300, edge_ic=0.0, mom_ic=0.0, rho=0.5, phi_z=0.85, phi_m=0.97,
               sigma=0.045, churn=0.01, seed=0, start_year=2010):
    rng = np.random.default_rng(seed)
    T = n_dates + 13
    z = np.empty((T, n_stocks))
    m = np.empty((T, n_stocks))
    m[0] = rng.normal(size=n_stocks)
    z[0] = rho * m[0] + math.sqrt(1 - rho * rho) * rng.normal(size=n_stocks)
    for w in range(1, T):
        m[w] = phi_m * m[w - 1] + math.sqrt(1 - phi_m ** 2) * rng.normal(size=n_stocks)
        u = phi_z * (z[w - 1] - rho * m[w - 1]) + math.sqrt(1 - phi_z ** 2) * math.sqrt(1 - rho * rho) * \
            rng.normal(size=n_stocks)
        z[w] = rho * m[w] + u
    # corr(y4, z) ~ 4 a / (2 sigma) for a small a  ->  a = ic * sigma / 2
    a_z, a_m = edge_ic * sigma / 2.0, mom_ic * sigma / 2.0
    r = a_z * z + a_m * m + sigma * rng.normal(size=(T, n_stocks))
    cs = np.vstack([np.zeros(n_stocks), np.cumsum(r, axis=0)])
    ids = np.arange(n_stocks)
    dates = []
    present = None
    for w in range(n_dates):
        u = rng.random(n_stocks)
        present = np.where(present, u >= churn, u < 10 * churn) if w else rng.random(n_stocks) >= 0.09
        y4 = cs[w + 5] - cs[w + 1]                 # returns of weeks w+1 .. w+4 (r[w+1..w+4])
        y13 = cs[w + 14] - cs[w + 1]
        Q = np.clip(np.round(10 + 4 * z[w]), 0, 20).astype(int)
        Q[z[w] < -1.6] = -1
        dates.append(dict(ids=ids[present], Q=Q[present], G=_group(Q)[present],
                          mom=(m[w] + 0.05 * rng.normal(size=n_stocks))[present],
                          trend=(m[w] > -0.3)[present], y=y4[present], y13=y13[present],
                          year=start_year + w // WEEKS_PER_YEAR))
    return dates
