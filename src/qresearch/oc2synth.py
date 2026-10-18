"""OC-2 Stage 2 (owner D248): synthetic-only calibration of the universe-wide Fama-MacBeth signal test.

Everything here is SYNTHETIC: characteristics, the F5-like signal and returns are generated from stated parameters.
No real signal, return or market data is read. The population structure (cross-section size by year, quarterly
refresh clustering, churn, sector mix) and the signal-control correlations come from committed NON-RETURN
aggregates (OC-CP3 Stage 1 audit, P14-CP1); everything else is a labelled assumption (protocol section 3).

Primary inference (protocol section 4): monthly cross-sectional OLS of the demeaned next-month return on the
centred signal rank, eight centred control ranks and 11 sector dummies; statistic t = mean(slope) / NW(3) SE,
one-sided, Student t with T-1 degrees of freedom.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field, replace

import numpy as np
from scipy.stats import t as student_t

# ----------------------------------------------------------------------------------------------- fixed structure
T = 118                                   # reviews 2012-02 .. 2021-11 (OC-CP3)
WARMUP = 24
START_CAL_MONTH = 2                       # first review = February
YEAR_N = {2012: 446.5, 2013: 542.9, 2014: 709.8, 2015: 751.2, 2016: 740.6, 2017: 765.8, 2018: 800.9,
          2019: 839.3, 2020: 847.1, 2021: 1018.6}       # vendor-side valid F5 per review (OC2_S1_posthoc.json)
SECTORS = {"BusEq": 157.9, "Chems": 35.1, "Durbl": 25.4, "Enrgy": 50.8, "Hlth": 81.6, "Manuf": 89.0,
           "NoDur": 57.8, "Other": 135.3, "Shops": 98.0, "Telcm": 24.8, "Utils": 57.9}  # OC2_S1_audit 2016
PHASE_P = (0.62, 0.10, 0.28)              # refresh in Feb/May/Aug/Nov-type, Mar/Jun/Sep/Dec-type, Jan/Apr/Jul/Oct-type
EXIT_RATE = 0.024                         # OC2_S1_audit stage2 exit share per review
CHARS = ("size", "beta", "lowvol", "mom", "bm", "gpa", "ag", "acc", "growth")
CONTROLS = CHARS[:8]                      # growth is never a control (latent)
RHO_F5 = dict(size=0.0, beta=0.0, lowvol=-0.05, mom=0.175, bm=-0.07, gpa=0.105, ag=0.078, acc=-0.177, growth=0.30)
# characteristic correlation matrix (assumption; order CHARS)
_C = {("size", "lowvol"): .3, ("size", "mom"): .05, ("size", "bm"): -.1, ("size", "gpa"): .1,
      ("beta", "lowvol"): -.5, ("beta", "gpa"): -.1, ("beta", "ag"): .1, ("beta", "growth"): .1,
      ("lowvol", "mom"): .1, ("lowvol", "gpa"): .15, ("lowvol", "ag"): -.1, ("lowvol", "growth"): -.1,
      ("mom", "bm"): -.2, ("mom", "gpa"): .05, ("mom", "growth"): .2,
      ("bm", "gpa"): -.3, ("bm", "ag"): -.2, ("bm", "growth"): -.3,
      ("gpa", "ag"): .05, ("gpa", "acc"): .05, ("gpa", "growth"): .2,
      ("ag", "acc"): .2, ("ag", "growth"): .4, ("acc", "growth"): .1}
# literature-signed premia at the reference magnitude (top-quintile excess per year) when 'priced'
PREMIA_SIGN = dict(size=-1, beta=-1, lowvol=+1, mom=+1, bm=+1, gpa=+1, ag=-1, acc=-1, growth=+1)
Z80 = 1.3998585                            # E[Z | Z > z_0.8] (as lh_cp4_power.QUINTILE_TOP_MEAN_Z)
SD_TOTAL = 0.065                           # target cross-sectional sd of monthly returns (LH-CP4 assumption)


def corr_matrix():
    k = len(CHARS)
    C = np.eye(k)
    for (a, b), v in _C.items():
        i, j = CHARS.index(a), CHARS.index(b)
        C[i, j] = C[j, i] = v
    return C


def theta_from_annual(e):
    """Monthly coefficient per 1 sd of a standard-normal characteristic giving a top-quintile annual excess e."""
    return e / (12.0 * Z80)


@dataclass(frozen=True)
class World:
    name: str
    iid: bool = False                      # N0i: no structure at all
    priced: tuple = ()                     # characteristics with a premium of `premium` (literature sign)
    premium: float = 0.03
    tv_premia: bool = False                # N6
    sigma_sector: float = 0.025
    sigma_factor: float = 0.010
    sigma_market: float = 0.045
    churn: float = 1.0
    signal_ar: float = 0.70                # quarterly AR of the idiosyncratic signal part
    own_tv_premium: bool = False           # N9: zero-mean AR(0.5) premium on the signal itself
    mnar: bool = False                     # N11
    tails: float = 5.0                     # Student-t df of idiosyncratic shocks
    hetero: float = 0.30
    reliability: float = 1.0               # N5: controls observed with this reliability (squared correlation)
    latent_growth_priced: bool = False     # N2L
    horizon: int = 1                       # N13: 3-month overlapping response (diagnostic)
    planted: float = 0.0                   # top-quintile annual excess attributable to the signal
    fresh_only: bool = False               # planted effect only in the month after a refresh (x3)
    corr_scale: float = 1.0                # signal-control correlation scale (power sensitivity)


def seed_of(name, rep):
    return (int(hashlib.sha256(f"OC2-S2|{name}".encode()).hexdigest()[:8], 16) + rep) % (2 ** 32)


def n_by_month():
    """Cross-section size per review: linear interpolation between year means (mid-year anchors)."""
    out = []
    for t in range(T):
        cal = START_CAL_MONTH - 1 + t
        y, m = 2012 + cal // 12, cal % 12 + 1
        a = YEAR_N[y]
        if m >= 7:
            b = YEAR_N.get(y + 1, a)
            v = a + (b - a) * (m - 6.5) / 12
        else:
            b = YEAR_N.get(y - 1, a)
            v = a + (b - a) * (6.5 - m) / 12
        out.append(int(round(v)))
    return np.array(out)


def calendar(t):
    """(year, calendar month) of review t (t may be negative during warm-up)."""
    cal = START_CAL_MONTH - 1 + t
    return 2012 + cal // 12, cal % 12 + 1


def phase_of_month(m):
    return {2: 0, 5: 0, 8: 0, 11: 0, 3: 1, 6: 1, 9: 1, 12: 1}.get(m, 2)


# ----------------------------------------------------------------------------------------------- generator
class Panel:
    """One synthetic world: yields per review t the regression cross-section and the next-month response."""

    def __init__(self, w: World, seed: int):
        self.w, self.rng = w, np.random.default_rng(seed)
        self.C = corr_matrix()
        self.L = np.linalg.cholesky(self.C)
        rho = np.array([RHO_F5[c] for c in CHARS]) * w.corr_scale
        self.beta = np.linalg.solve(self.C, rho)
        q = float(self.beta @ self.C @ self.beta)
        assert q < 1.0
        self.u_scale = math.sqrt(1.0 - q)
        self.N = n_by_month()
        self.S = int(self.N.max() * 1.6) + 10
        sec_w = np.array(list(SECTORS.values()))
        self.sec_p = sec_w / sec_w.sum()
        k = len(CHARS)
        self.pool_scale = 1.0 / 0.82 if w.mnar else 1.0      # MNAR: the SAMPLE (not the pool) matches YEAR_N
        # premia (monthly, per sd)
        th = np.zeros(k)
        for c in w.priced:
            th[CHARS.index(c)] = PREMIA_SIGN[c] * theta_from_annual(w.premium)
        if w.latent_growth_priced:
            th[CHARS.index("growth")] = theta_from_annual(w.premium)
        self.theta = th
        self.theta_sig = theta_from_annual(w.planted) * (3.0 if w.fresh_only else 1.0)
        self.theta_own = theta_from_annual(0.03)
        # idiosyncratic sd keeps the total cross-sectional sd at SD_TOTAL
        var_sys = w.sigma_sector ** 2 + (k - 1) * w.sigma_factor ** 2 + (0.3 * w.sigma_market) ** 2
        self.sig_idio = math.sqrt(max(SD_TOTAL ** 2 - var_sys, 1e-6)) if not w.iid else SD_TOTAL
        self.alive = np.zeros(self.S, bool)
        self._new(np.arange(self.S))
        self.alive[:int(round(self.N[0] * self.pool_scale))] = True
        self.tv = np.zeros(k)
        self.own = 0.0

    def _new(self, idx):
        n = len(idx)
        if n == 0:
            return
        if not hasattr(self, "Z"):
            k = len(CHARS)
            self.Z = np.zeros((self.S, k))
            self.sec = np.zeros(self.S, int)
            self.phase = np.zeros(self.S, int)
            self.u = np.zeros(self.S)
            self.sig = np.zeros(self.S)
            self.age = np.zeros(self.S, int)
            self.noise = np.zeros((self.S, k))
            self.miss_bias = np.zeros(self.S)
        self.sec[idx] = self.rng.choice(len(SECTORS), n, p=self.sec_p)
        self.Z[idx] = self.rng.standard_normal((n, len(CHARS))) @ self.L.T
        self.phase[idx] = self.rng.choice(3, n, p=PHASE_P)
        self.u[idx] = self.rng.standard_normal(n)
        self.noise[idx] = self.rng.standard_normal((n, len(CHARS)))
        self.miss_bias[idx] = self.rng.standard_normal(n)
        self._refresh(idx)

    def _refresh(self, idx):
        self.sig[idx] = self.Z[idx] @ self.beta + self.u_scale * self.u[idx]
        self.age[idx] = 0

    def step(self, t):
        """Advance to review t; returns (sample, live): the regression sample and all live stocks."""
        w, rng = self.w, self.rng
        k = len(CHARS)
        if w.iid:
            idx = np.arange(self.N[max(t, 0)])
            self.Z[idx] = rng.standard_normal((len(idx), k))
            self.u[idx] = rng.standard_normal(len(idx))
            self._refresh(idx)
            return idx, idx
        # characteristics evolve (common monthly AR 0.95, stationary correlation C)
        a = 0.95
        live = np.flatnonzero(self.alive)
        self.Z[live] = a * self.Z[live] + math.sqrt(1 - a * a) * (rng.standard_normal((len(live), k)) @ self.L.T)
        self.age[live] += 1
        # churn: exits replaced by entrants
        if w.churn > 0:
            ex = live[rng.random(len(live)) < EXIT_RATE * w.churn]
            self._new(ex)
        # growth of the cross-section
        tt = max(t, 0)
        need = int(round(self.N[tt] * self.pool_scale)) - int(self.alive.sum())
        if need > 0:
            free = np.flatnonzero(~self.alive)[:need]
            self._new(free)
            self.alive[free] = True
        elif need < 0:
            drop = np.flatnonzero(self.alive)[need:]
            self.alive[drop] = False
        live = np.flatnonzero(self.alive)
        # quarterly refresh in the stock's phase month
        _y, m = calendar(t)
        ref = live[self.phase[live] == phase_of_month(m)]
        b = w.signal_ar
        self.u[ref] = b * self.u[ref] + math.sqrt(1 - b * b) * rng.standard_normal(len(ref))
        self._refresh(ref)
        sample = live
        if w.mnar:
            p = 1 / (1 + np.exp(-(-1.75 - 0.5 * self.Z[live, CHARS.index("lowvol")] + 0.5 * self.miss_bias[live]
                                  + 0.4 * (self.sec[live] == list(SECTORS).index("Shops")))))
            sample = live[rng.random(len(live)) >= p]
        return sample, live

    def controls(self, idx):
        Z = self.Z[idx][:, :8]
        r = self.w.reliability
        if r < 1.0:
            Z = math.sqrt(r) * Z + math.sqrt(1 - r) * self.noise[idx][:, :8]
        return Z

    def returns(self, idx):
        """Next-month returns of stocks idx (the response of review t)."""
        w, rng = self.w, self.rng
        n = len(idx)
        if w.iid:
            return rng.standard_normal(n) * SD_TOTAL
        k = len(CHARS)
        if w.tv_premia:
            self.tv = 0.3 * self.tv + math.sqrt(1 - 0.09) * rng.standard_normal(k)
            th = self.theta * (1 + 2 * self.tv)
        else:
            th = self.theta
        fshock = rng.standard_normal(k) * w.sigma_factor
        fshock[CHARS.index("growth")] = 0.0
        Z = self.Z[idx]
        mu = Z @ (th + fshock)
        mkt = rng.standard_normal() * w.sigma_market
        mu += (0.3 * Z[:, CHARS.index("beta")]) * mkt
        mu += (rng.standard_normal(len(SECTORS)) * w.sigma_sector)[self.sec[idx]]
        s = self.sig[idx]
        if w.planted:
            eff = self.theta_sig * s
            if w.fresh_only:
                eff = eff * (self.age[idx] == 0)
            mu += eff
        if w.own_tv_premium:
            self.own = 0.5 * self.own + math.sqrt(1 - 0.25) * rng.standard_normal()
            mu += self.theta_own * self.own * s
        lv = Z[:, CHARS.index("lowvol")]
        h = np.exp(-w.hetero * lv)
        h = h / math.sqrt(np.mean(h * h))
        df = w.tails
        e = rng.standard_t(df, n) * math.sqrt((df - 2) / df) if df < 100 else rng.standard_normal(n)
        return mu + self.sig_idio * h * e


# ----------------------------------------------------------------------------------------------- inference
def crank(x):
    """Centred ranks in (-0.5, 0.5)."""
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(len(x))
    return (r + 0.5) / len(x) - 0.5


def design(sig, Z, sec):
    n = len(sig)
    X = np.empty((n, 1 + Z.shape[1] + len(SECTORS)))
    X[:, 0] = crank(sig)
    for j in range(Z.shape[1]):
        X[:, 1 + j] = crank(Z[:, j])
    X[:, 1 + Z.shape[1]:] = 0.0
    X[np.arange(n), 1 + Z.shape[1] + sec] = 1.0
    return X


def ols_first(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta[0]


def nw_t(b, lag):
    b = np.asarray(b, float)
    n = len(b)
    m = b.mean()
    d = b - m
    v = d @ d / n
    for l in range(1, lag + 1):
        v += 2 * (1 - l / (lag + 1)) * (d[l:] @ d[:-l]) / n
    se = math.sqrt(max(v, 1e-30) / n)
    return m / se


def block_boot_p(b, rng, B=499, mean_block=6):
    """One-sided stationary-bootstrap p-value of mean(b) > 0 (diagnostic)."""
    b = np.asarray(b, float)
    n = len(b)
    d = b - b.mean()
    p = 1.0 / mean_block
    idx = np.empty((B, n), int)
    idx[:, 0] = rng.integers(0, n, B)
    for j in range(1, n):
        jump = rng.random(B) < p
        idx[:, j] = np.where(jump, rng.integers(0, n, B), (idx[:, j - 1] + 1) % n)
    means = d[idx].mean(axis=1)
    return float((1 + np.sum(means >= b.mean())) / (B + 1))


def crit(alpha, df=T - 1):
    return float(student_t.ppf(1 - alpha, df))


def run_world(w: World, rep: int, boot=False):
    """One replication: monthly slope series and the real-test statistics. The response of review t is the
    next-month return (horizon 1) or the sum of the next `horizon` monthly returns of the same stocks (N13, churn 0:
    overlapping responses share months)."""
    P = Panel(w, seed_of(w.name, rep))
    for t in range(-WARMUP, 0):
        _s, live = P.step(t)
        if not w.iid:
            P.returns(live)
    H = w.horizon
    recs, R = [], []
    for t in range(T + H - 1):
        sample, live = P.step(t)
        full = np.full(P.S, np.nan)
        full[live] = P.returns(live)
        R.append(full)
        if t < T:
            recs.append((sample, P.sig[sample].copy(), P.controls(sample), P.sec[sample].copy(),
                         P.age[sample].copy(), P.Z[sample, :8].copy(), calendar(t)[1]))
    slopes, tq, sizes, fresh, rets_sd = [], [], [], {0: [], 1: [], 2: []}, []
    corr_acc = np.zeros(8)
    n_corr = 0
    for t, (sample, sig, Zc, sec, age, Ztrue, m) in enumerate(recs):
        r = R[t][sample]
        for h in range(1, H):
            r = r + R[t + h][sample]
        X = design(sig, Zc, sec)
        y = r - r.mean()
        slopes.append(ols_first(X, y))
        Xq = X.copy()
        Xq[:, 0] = (X[:, 0] >= 0.3).astype(float)        # top quintile of the centred rank
        tq.append(ols_first(Xq, y))
        sizes.append(len(sample))
        fresh[phase_of_month(m)].append(float(np.mean(age == 0)))
        rets_sd.append(float(np.std(R[t][sample])))
        if t % 12 == 6:
            for j in range(8):
                corr_acc[j] += np.corrcoef(sig, Ztrue[:, j])[0, 1]
            n_corr += 1
    b = np.array(slopes)
    lag = 3 if H == 1 else 3 + H - 1
    out = dict(t_nw3=nw_t(b, lag), t_iid=nw_t(b, 0), t_nw6=nw_t(b, 6),
               mean_slope=float(b.mean()), tq_annual=float(12 * 0.8 * np.mean(tq) / H),
               half1=float(b[:59].mean()), half2=float(b[59:].mean()),
               rho1=float(np.corrcoef(b[1:], b[:-1])[0, 1]), sd_slope=float(b.std()),
               mean_n=float(np.mean(sizes)), fresh_by_phase=[float(np.mean(fresh[k])) for k in range(3)],
               ret_sd=float(np.mean(rets_sd)), corr=(corr_acc / max(n_corr, 1)).tolist(),
               g4=year_concentration_ok(b))
    if boot:
        out["p_boot"] = block_boot_p(b, np.random.default_rng(seed_of(w.name + "|boot", rep)))
    return out


def year_concentration_ok(b):
    """G4: no calendar year supplies > 50% of the total sum of monthly slopes (total must be positive)."""
    tot = float(np.sum(b))
    if tot <= 0:
        return False
    years = {}
    for t, v in enumerate(b):
        y, _m = calendar(t)
        years[y] = years.get(y, 0.0) + float(v)
    return max(years.values()) <= 0.5 * tot


def full_rule(o, c1, g2_floor=0.03):
    return bool(o["t_nw3"] > c1 and o["tq_annual"] >= g2_floor and o["half1"] > 0 and o["half2"] > 0 and o["g4"])
