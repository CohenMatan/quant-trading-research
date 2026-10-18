"""P13-CP6 (owner D239): SYNTHETIC equity panels for validating the R1 exposure-matched twin test.

Offline only: no market data, no QuantConnect, no H028 holdings or returns. Every number below is a modelling choice
documented in docs/checkpoints/P13_CP6_h028_repaired_null_synthetic_validation.md.

Model (monthly; decision g, trades at the next open, holding period g -> g+1):
  * a world of stocks, each with persistent latent characteristics (AR(1), correlated innovations): LV (volatility),
    SIZE, BM (book-to-market), PROF (profitability), Q (planted stock-specific predictor, independent of the others),
    N1..N4 (uninformative persistent features); MOM (12-1) and BETA (36-month OLS on the market) are COMPUTED from each
    stock's own simulated past returns, so they are point-in-time by construction;
  * return over period g: r = a0 + beta_i * M_g + S_{sector,g} + sum_k lambda_{k,g} * c_{i,k,g} + sigma_i * eps, with
    sigma_i = idio * exp(lv_vol * LV) (LV really is volatility), true beta correlated with LV, priced characteristics
    c in {-LV, BM, PROF, MOM_z, Q} with premia lambda (stationary or AR(1)-time-varying);
  * dynamic membership: monthly exits from the eligible set (probability p_exit * churn, optionally size-dependent),
    re-entries of earlier members and brand-new stocks (with 24 months of pre-history), genuine delistings (hazard
    rising with volatility; delisting return replaces the period return; the stock never returns), sector
    reclassification, optional universe growth and sector / size composition drift;
  * observed features = latent + measurement noise; percentiles for matching and z-scores for selection are computed
    within the decision date's eligible set only.
"""
import numpy as np

SECTOR_W = np.array([0.07, 0.03, 0.13, 0.06, 0.04, 0.20, 0.03, 0.06, 0.13, 0.14, 0.11])   # 11 FF12 sectors (no Money)
LATENT = ("LV", "SIZE", "BM", "PROF", "Q", "N1", "N2", "N3", "N4")
MATCH_DIMS = ("LV", "SIZE", "BM", "PROF", "MOM", "BETA")                  # percentile characteristics for matching
SEL_FEATS = ("LV", "BM", "PROF", "MOM", "Q", "N1", "N2", "N3", "N4")      # z-scored selection inputs

DEFAULT = dict(
    n_target=475, n_last=None, pre=36, months=84, burn=0,
    p_exit=0.0875, churn=1.0, reentry=0.5, size_exit=0.0,
    delist_base=0.002, delist_mult=1.0, delist_mu=-0.30, delist_sd=0.20, sector_move=0.002,
    rho=dict(LV=0.92, SIZE=0.98, BM=0.95, PROF=0.95, Q=0.90, N1=0.90, N2=0.90, N3=0.90, N4=0.90),
    corr={("LV", "SIZE"): -0.30, ("LV", "BM"): 0.10, ("LV", "PROF"): -0.25, ("BM", "PROF"): -0.30,
          ("SIZE", "PROF"): 0.20},
    noise_corr=0.0,                    # correlation of N1..N4 innovations with LV and BM (S12: correlated predictors)
    prem=dict(LV=0.0, BM=0.0, PROF=0.0, MOM=0.0, Q=0.0), prem_tv=0.0, prem_tv_rho=0.95,
    a0=0.002, mkt_mu=0.006, mkt_sd=0.045, sec_sd=0.03, idio=0.075, lv_vol=0.30, beta_sd=0.30, beta_lv=0.6,
    obs_noise=dict(LV=0.30, SIZE=0.10, BM=0.20, PROF=0.20, Q=0.30, N1=0.0, N2=0.0, N3=0.0, N4=0.0),
    sector_w=None, sector_w_end=None, size_drift=0.0,
)


def config(**kw):
    c = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULT.items()}
    for k, v in kw.items():
        if isinstance(v, dict) and isinstance(c.get(k), dict):
            c[k].update(v)
        else:
            c[k] = v
    return c


def _chol(cfg):
    k = len(LATENT)
    C = np.eye(k)
    for (a, b), v in cfg["corr"].items():
        i, j = LATENT.index(a), LATENT.index(b)
        C[i, j] = C[j, i] = v
    nc = cfg["noise_corr"]
    if nc:
        for n in ("N1", "N2", "N3", "N4"):
            for a in ("LV", "BM"):
                i, j = LATENT.index(n), LATENT.index(a)
                C[i, j] = C[j, i] = nc
        for a, b in (("N1", "N2"), ("N1", "N3"), ("N1", "N4"), ("N2", "N3"), ("N2", "N4"), ("N3", "N4")):
            i, j = LATENT.index(a), LATENT.index(b)
            C[i, j] = C[j, i] = nc
    return np.linalg.cholesky(C)


def pct(x):
    """Cross-sectional percentile in (0, 1): (rank - 0.5) / n, average ranks for ties."""
    x = np.asarray(x, float)
    n = x.size
    if n == 0:
        return x
    order = np.argsort(x, kind="mergesort")
    r = np.empty(n)
    r[order] = np.arange(n)
    sx = x[order]
    i = 0
    while i < n:                                                    # ties -> average rank
        j = i
        while j + 1 < n and sx[j + 1] == sx[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return (r + 0.5) / n


def zscore(x):
    x = np.asarray(x, float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else np.zeros_like(x)


def panel(seed, cfg):
    """One synthetic panel: a list of decision-month dicts (evaluation months only), each with
    ids (sorted int), sector, pct {dim: percentile}, z {feature: z-score}, r (period return), dl (delisted during the
    period), spy (benchmark period return), plus panel-level factor paths for R3."""
    rng = np.random.default_rng(seed)
    pre, T = cfg["pre"], cfg["burn"] + cfg["months"]
    G = pre + T
    K = len(LATENT)
    L = _chol(cfg)
    rho = np.array([cfg["rho"][f] for f in LATENT])
    s_rho = np.sqrt(1.0 - rho ** 2)
    nsec = SECTOR_W.size
    w0 = np.asarray(cfg["sector_w"] if cfg["sector_w"] is not None else SECTOR_W, float)
    w1 = np.asarray(cfg["sector_w_end"] if cfg["sector_w_end"] is not None else w0, float)
    n_first = cfg["n_target"]
    n_last = cfg["n_last"] if cfg["n_last"] is not None else n_first
    target = [int(round(n_first * (n_last / n_first) ** (t / max(T - 1, 1)))) for t in range(T)]
    churn = cfg["p_exit"] * cfg["churn"]
    cap = int(max(n_first, n_last) * (1.3 + churn * T * 1.2)) + 200
    # factor paths, drawn month by month in time order (so a shorter panel is an exact prefix of a longer one)
    M = np.zeros(G)
    S = np.zeros((G, nsec))
    pk = ("LV", "BM", "PROF", "MOM", "Q")
    lam0 = np.array([cfg["prem"][k] for k in pk])
    lam = np.zeros((G, len(pk)))
    u_prev = np.zeros(len(pk))

    def factors_for(g):
        nonlocal u_prev
        M[g] = rng.normal(cfg["mkt_mu"], cfg["mkt_sd"])
        S[g] = rng.normal(0.0, cfg["sec_sd"], nsec)
        if cfg["prem_tv"]:
            u_prev = cfg["prem_tv_rho"] * u_prev + np.sqrt(1 - cfg["prem_tv_rho"] ** 2) * rng.standard_normal(len(pk))
        lam[g] = lam0 * (1.0 + cfg["prem_tv"] * u_prev)
    # stock state
    lat = np.zeros((cap, K))
    sector = np.zeros(cap, np.int64)
    btrue = np.ones(cap)
    alive = np.zeros(cap, bool)
    ever = np.zeros(cap, bool)                                           # was ever a member
    R = np.full((G, cap), np.nan, np.float32)                           # return history (alive stocks)
    nxt = 0

    def new_stocks(n, g_from, progress):
        nonlocal nxt
        ids = np.arange(nxt, nxt + n)
        nxt += n
        z = (L @ rng.standard_normal((K, n))).T
        if cfg["size_drift"]:
            z[:, LATENT.index("SIZE")] += cfg["size_drift"] * progress
        lat[ids] = z
        w = w0 + (w1 - w0) * progress
        sector[ids] = rng.choice(nsec, n, p=w / w.sum())
        btrue[ids] = np.clip(1.0 + cfg["beta_sd"] * (cfg["beta_lv"] * z[:, 0] + np.sqrt(1 - cfg["beta_lv"] ** 2)
                                                     * rng.standard_normal(n)), 0.3, 2.2)
        alive[ids] = True
        # pre-history: returns for months g_from - 24 .. g_from - 1 with latents evolved forward
        for g in range(max(g_from - 24, 0), g_from):
            R[g, ids] = period_returns(ids, g)
            evolve(ids)
        return ids

    def period_returns(ids, g):
        z = lat[ids]
        sig = cfg["idio"] * np.exp(cfg["lv_vol"] * z[:, 0])
        prem = -lam[g, 0] * z[:, 0] + lam[g, 1] * z[:, 2] + lam[g, 2] * z[:, 3] + lam[g, 4] * z[:, 4]
        if lam[g, 3] != 0.0:
            prem = prem + lam[g, 3] * _mom_z(ids, g)
        return cfg["a0"] + btrue[ids] * M[g] + S[g, sector[ids]] + prem + sig * rng.standard_normal(ids.size)

    def _mom_z(ids, g):
        if g < 12:
            return np.zeros(ids.size)
        h = R[g - 12:g - 1, ids]
        m = np.nansum(h, 0)
        return zscore(m)

    def evolve(ids):
        e = (L @ rng.standard_normal((K, ids.size))).T
        lat[ids] = rho * lat[ids] + s_rho * e

    # initial universe with pre-history (months 0 .. pre-1)
    n0 = target[0]
    first = np.arange(n0)
    nxt = n0
    z0 = (L @ rng.standard_normal((K, n0))).T
    lat[first] = z0
    sector[first] = rng.choice(nsec, n0, p=w0 / w0.sum())
    btrue[first] = np.clip(1.0 + cfg["beta_sd"] * (cfg["beta_lv"] * z0[:, 0] + np.sqrt(1 - cfg["beta_lv"] ** 2)
                                                   * rng.standard_normal(n0)), 0.3, 2.2)
    alive[first] = True
    for g in range(pre):
        factors_for(g)
        R[g, first] = period_returns(first, g)
        evolve(first)
    members = set(first.tolist())
    ever[first] = True
    away = []
    months = []
    obs_sd = np.array([cfg["obs_noise"][f] for f in LATENT])
    for t in range(T):
        g = pre + t
        progress = t / max(T - 1, 1)
        factors_for(g)
        if t:
            # membership update at decision g
            mem = np.array(sorted(members), dtype=np.int64)
            mem = mem[alive[mem]]                                       # delisted stocks are gone
            p = np.full(mem.size, churn)
            if cfg["size_exit"]:
                zs = lat[mem, LATENT.index("SIZE")]
                p = np.clip(churn * np.exp(-cfg["size_exit"] * zs) / np.mean(np.exp(-cfg["size_exit"] * zs)), 0, 1)
            ex = rng.random(mem.size) < p
            stay = mem[~ex].tolist()
            left = mem[ex].tolist()
            away = [s for s in away if alive[s]]
            need = max(target[t] - len(stay), 0)
            new = []
            fresh = 0
            for _ in range(need):
                if away and rng.random() < cfg["reentry"]:
                    new.append(away.pop(int(rng.integers(len(away)))))
                else:
                    fresh += 1
            if fresh:
                new.extend(new_stocks(fresh, g, progress).tolist())
            away.extend(left)
            members = set(stay) | set(new)
            ever[np.array(new, dtype=np.int64)] = True
            if cfg["sector_move"]:
                mv = [s for s in members if rng.random() < cfg["sector_move"]]
                if mv:
                    w = w0 + (w1 - w0) * progress
                    sector[np.array(mv)] = rng.choice(nsec, len(mv), p=w / w.sum())
        ids = np.array(sorted(members), dtype=np.int64)
        # observed features at decision g (point in time: latents now, returns up to g-1)
        z = lat[ids] + obs_sd * rng.standard_normal((ids.size, K))
        h = R[max(g - 36, 0):g, ids]
        mk = M[max(g - 36, 0):g]
        ok = np.isfinite(h)
        n_ok = ok.sum(0)
        X = np.where(ok, mk[:, None], 0.0)
        Y = np.where(ok, h, 0.0)
        with np.errstate(invalid="ignore", divide="ignore"):
            mx, my = X.sum(0) / n_ok, Y.sum(0) / n_ok
            cov = (ok * (X - mx) * (Y - my)).sum(0) / n_ok
            var = (ok * (X - mx) ** 2).sum(0) / n_ok
            beta = np.where((n_ok >= 12) & (var > 0), cov / var, np.nan)       # 36-month OLS, >= 12 months
        beta = np.where(np.isfinite(beta), beta, np.nanmedian(beta) if np.isfinite(beta).any() else 1.0)
        mom = np.nansum(R[g - 12:g - 1, ids], 0)
        raw = dict(LV=z[:, 0], SIZE=z[:, 1], BM=z[:, 2], PROF=z[:, 3], Q=z[:, 4], N1=z[:, 5], N2=z[:, 6],
                   N3=z[:, 7], N4=z[:, 8], MOM=mom, BETA=beta)
        # period return g -> g+1 for every alive stock (history for future betas / momentum)
        live = np.flatnonzero(alive[:nxt])
        R[g, live] = period_returns(live, g)
        haz = cfg["delist_base"] * cfg["delist_mult"] * np.exp(0.5 * lat[live, 0])
        dl_live = rng.random(live.size) < haz
        if dl_live.any():
            d = np.clip(rng.normal(cfg["delist_mu"], cfg["delist_sd"], int(dl_live.sum())), -0.95, 0.5)
            R[g, live[dl_live]] = d
            alive[live[dl_live]] = False
        pos = {s: i for i, s in enumerate(live.tolist())}
        li = np.array([pos[s] for s in ids], dtype=np.int64)
        r = R[g, ids].astype(float)
        dl = dl_live[li]
        evolve(np.flatnonzero(alive[:nxt]))
        if t >= cfg["burn"]:
            months.append(dict(t=t - cfg["burn"], ids=ids, sector=sector[ids].copy(),
                               pct={d_: pct(raw[d_]) for d_ in MATCH_DIMS},
                               z={f: zscore(raw[f]) for f in SEL_FEATS},
                               r=r, dl=dl, spy=float(cfg["a0"] + M[g]), mkt=float(M[g])))
    return months
