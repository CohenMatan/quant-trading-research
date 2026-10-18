"""OC-2 synthetic calibration v2 (owner D249): one controlled methodological repair of v1 (`oc2synth`, frozen).

SYNTHETIC ONLY: characteristics, the F5-like signal and returns are generated; nothing real is read. Population
structure constants (cross-section size by year, sector mix, refresh phases, churn, signal-control correlations,
characteristic correlation matrix) are imported unchanged from the frozen v1 module; their provenance is v1 / OC-CP3.

Changes vs v1 (each traced to the v1 failure-mode audit, `research/longhorizon/oc2/v2/OC2_V2_audit.json`):
  * realistic month-to-month payoff dependence: a zero-mean (under the null) AR(1) payoff g_t on the signal, scaled
    so that the monthly rank-IC sd reaches the scenario target (0.06 / 0.09 / 0.12; LH-CP4 range);
  * controls enter as restricted cubic splines (5 fixed knots) of each control's cross-sectional normal score;
  * Newey-West lag 7 (Andrews AR(1)-Bartlett plug-in at the most persistent assumed dependence, rho = 0.5) with
    fixed-b critical values simulated once under iid Gaussian slopes (`CV`);
  * N13: returns are generated for every stock every month and tracked by stock id, so overlapping responses never
    hit missing months (exit = stop accumulating); N7: a variance-budget guard (systematic share <= 60%);
  * one classification function implementing the protocol's precedence.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

import numpy as np
from scipy.special import ndtri
from scipy.stats import norm

from qresearch import oc2synth as O

T, WARMUP = O.T, O.WARMUP
CHARS, CONTROLS = O.CHARS, O.CONTROLS
SD_TOTAL = O.SD_TOTAL
NW_LAG = 7
SYS_SHARE_MAX = 0.60
KNOT_P = (0.05, 0.275, 0.5, 0.725, 0.95)
KNOTS = tuple(float(norm.ppf(p)) for p in KNOT_P)
# fixed-b critical values of the one-sided NW(7) t (Bartlett) for T = 118, simulated under iid Gaussian slopes
# (`fixed_b_cv`, 2,000,000 draws, seed 118007; computed before the protocol, not from any scenario world)
CV = {0.05: 1.7768983745981166, 0.01: 2.5903943399261284, 0.005: 2.904988356486873, 0.001: 3.5885898416418374}
# stationary sd of the signal payoff g_t per IC regime: calibrated once on the baseline N0 structure with DEV seeds
# (`calibrate_payoff`, engineering only) so that the controls-adjusted (partial) monthly IC has the target sd
G_SD = {0.06: 0.0025457771839916855, 0.09: 0.004513291014499582, 0.12: 0.006309844357589551}


@dataclass(frozen=True)
class World:
    name: str
    iid: bool = False
    priced: tuple = ()
    premium: float = 0.03
    form: str = "normal"                   # premia linear in normal score / in uniform rank / tail deciles
    tv_premia: bool = False
    sigma_sector: float = 0.025
    sigma_factor: float = 0.010
    sigma_market: float = 0.045
    churn: float = 1.0
    signal_ar: float = 0.70
    ic_sd: float = 0.09                    # target monthly rank-IC sd (payoff dependence regime)
    payoff_rho: float = 0.10               # AR(1) of the signal payoff g_t
    mnar: bool = False
    tails: float = 5.0
    hetero: float = 0.30
    reliability: float = 1.0
    latent: float = 0.0                    # premium (top-quintile / yr) of the latent growth G (never a control)
    oracle: bool = False                   # diagnostic only: G added as a control
    horizon: int = 1
    planted: float = 0.0
    fresh_only: bool = False
    corr_scale: float = 1.0
    n_scale: float = 1.0
    irregular: bool = False                # N15: refresh month redrawn each quarter, 10% skipped quarters
    ctrl_missing: float = 0.05             # MAR share of stock-months with a missing control (complete case)


def seed_of(name, rep, tag="FINAL"):
    return (int(hashlib.sha256(f"OC2-V2|{tag}|{name}".encode()).hexdigest()[:8], 16) + rep) % (2 ** 32)


def payoff_sd(w):
    """Stationary sd of the signal payoff g_t for the world's IC regime (fixed per regime: an economic property of
    the market, so small or missing cross-sections add sampling noise on top). w.ic_sd may also be given directly as
    a float payoff via G_SD overrides (calibration only)."""
    v = G_SD.get(w.ic_sd)
    if v is None:
        raise ValueError(f"no calibrated payoff for IC regime {w.ic_sd}")
    return v


def variance_budget(w, g_sd):
    k = len(CONTROLS)
    sys_var = w.sigma_sector ** 2 + k * w.sigma_factor ** 2 + (0.3 * w.sigma_market) ** 2 + g_sd ** 2
    if sys_var > SYS_SHARE_MAX * SD_TOTAL ** 2:
        raise ValueError(f"{w.name}: systematic variance {sys_var:.5f} exceeds {SYS_SHARE_MAX:.0%} of the total")
    return math.sqrt(SD_TOTAL ** 2 - sys_var)


class Panel:
    def __init__(self, w: World, seed: int):
        self.w, self.rng = w, np.random.default_rng(seed)
        C = O.corr_matrix()
        self.L = np.linalg.cholesky(C)
        rho = np.array([O.RHO_F5[c] for c in CHARS]) * w.corr_scale
        self.beta = np.linalg.solve(C, rho)
        q = float(self.beta @ C @ self.beta)
        assert q < 1.0
        self.u_scale = math.sqrt(1.0 - q)
        self.N = np.maximum((O.n_by_month() * w.n_scale).round().astype(int), 30)
        self.pool_scale = 1.0 / 0.82 if w.mnar else 1.0
        self.S = int(self.N.max() * self.pool_scale * 1.6) + 10
        sec_w = np.array(list(O.SECTORS.values()))
        self.sec_p = sec_w / sec_w.sum()
        k = len(CHARS)
        th = np.zeros(k)
        for c in w.priced:
            th[CHARS.index(c)] = O.PREMIA_SIGN[c] * O.theta_from_annual(w.premium)
        if w.latent:
            th[CHARS.index("growth")] = O.theta_from_annual(w.latent)
        self.theta = th
        self.theta_sig = O.theta_from_annual(w.planted) * (3.0 if w.fresh_only else 1.0)
        self.g_sd = 0.0 if w.iid else payoff_sd(w)
        self.sig_idio = SD_TOTAL if w.iid else variance_budget(w, self.g_sd)
        self.next_id = 0
        self.Z = np.zeros((self.S, k))
        self.sec = np.zeros(self.S, int)
        self.phase = np.zeros(self.S, int)
        self.skip = np.zeros(self.S, bool)
        self.u = np.zeros(self.S)
        self.sig = np.zeros(self.S)
        self.age = np.zeros(self.S, int)
        self.noise = np.zeros((self.S, k))
        self.miss_bias = np.zeros(self.S)
        self.sid = np.zeros(self.S, np.int64)
        self._new(np.arange(self.S))
        self.alive = np.zeros(self.S, bool)
        self.alive[:int(round(self.N[0] * self.pool_scale))] = True
        self.tv = np.zeros(k)
        self.g = 0.0

    def _new(self, idx):
        n = len(idx)
        if n == 0:
            return
        rng = self.rng
        self.sec[idx] = rng.choice(len(O.SECTORS), n, p=self.sec_p)
        self.Z[idx] = rng.standard_normal((n, len(CHARS))) @ self.L.T
        self.phase[idx] = rng.choice(3, n, p=O.PHASE_P)
        self.u[idx] = rng.standard_normal(n)
        self.noise[idx] = rng.standard_normal((n, len(CHARS)))
        self.miss_bias[idx] = rng.standard_normal(n)
        self.sid[idx] = np.arange(self.next_id, self.next_id + n)
        self.next_id += n
        self._refresh(idx)

    def _refresh(self, idx):
        self.sig[idx] = self.Z[idx] @ self.beta + self.u_scale * self.u[idx]
        self.age[idx] = 0

    def step(self, t):
        """Advance to review t -> (sample, live)."""
        w, rng = self.w, self.rng
        k = len(CHARS)
        tt = min(max(t, 0), T - 1)
        if w.iid:
            idx = np.arange(self.N[tt])
            self.Z[idx] = rng.standard_normal((len(idx), k))
            self.u[idx] = rng.standard_normal(len(idx))
            self._refresh(idx)
            return idx, idx
        a = 0.95
        self.Z = a * self.Z + math.sqrt(1 - a * a) * (rng.standard_normal((self.S, k)) @ self.L.T)
        self.age += 1
        live = np.flatnonzero(self.alive)
        if w.churn > 0:
            self._new(live[rng.random(len(live)) < O.EXIT_RATE * w.churn])
        need = int(round(self.N[tt] * self.pool_scale)) - int(self.alive.sum())
        if need > 0:
            free = np.flatnonzero(~self.alive)[:need]
            self._new(free)
            self.alive[free] = True
        elif need < 0:
            self.alive[np.flatnonzero(self.alive)[need:]] = False     # leaves the universe, keeps trading
        live = np.flatnonzero(self.alive)
        _y, m = O.calendar(t)
        ph = O.phase_of_month(m)
        if w.irregular and ph == 2:                                  # quarter start: redraw month, 10% skip
            self.phase[live] = rng.choice(3, len(live), p=O.PHASE_P)
            self.skip[live] = rng.random(len(live)) < 0.10
        ref = live[(self.phase[live] == ph) & ~self.skip[live]]
        b = w.signal_ar
        self.u[ref] = b * self.u[ref] + math.sqrt(1 - b * b) * rng.standard_normal(len(ref))
        self._refresh(ref)
        sample = live
        if w.mnar:
            p = 1 / (1 + np.exp(-(-1.75 - 0.5 * self.Z[live, CHARS.index("lowvol")] + 0.5 * self.miss_bias[live]
                                  + 0.4 * (self.sec[live] == list(O.SECTORS).index("Shops")))))
            sample = live[rng.random(len(live)) >= p]
        if w.ctrl_missing > 0:
            sample = sample[rng.random(len(sample)) >= w.ctrl_missing]
        return sample, live

    def controls(self, idx):
        Z = self.Z[idx][:, :8]
        r = self.w.reliability
        if r < 1.0:
            Z = math.sqrt(r) * Z + math.sqrt(1 - r) * self.noise[idx][:, :8]
        if self.w.oracle:
            Z = np.column_stack([Z, self.Z[idx, CHARS.index("growth")]])
        return Z

    def returns_all(self):
        """Next-month return of EVERY slot (stocks outside the universe keep trading)."""
        w, rng = self.w, self.rng
        n = self.S
        if w.iid:
            return rng.standard_normal(n) * SD_TOTAL
        k = len(CHARS)
        if w.tv_premia:
            self.tv = 0.3 * self.tv + math.sqrt(1 - 0.09) * rng.standard_normal(k)
            th = self.theta * (1 + 2 * self.tv)
        else:
            th = self.theta
        Z = self.Z
        if w.form == "normal":
            F = Z
        elif w.form == "rank":
            F = (norm.cdf(Z) - 0.5) * math.sqrt(12)
        else:
            F = (np.where(Z > 1.2815516, 1.0, 0.0) - np.where(Z < -1.2815516, 1.0, 0.0)) / math.sqrt(0.2)
        fshock = rng.standard_normal(k) * w.sigma_factor
        fshock[CHARS.index("growth")] = 0.0
        mu = F @ th + Z @ fshock
        mu += 0.3 * Z[:, CHARS.index("beta")] * (rng.standard_normal() * w.sigma_market)
        mu += (rng.standard_normal(len(O.SECTORS)) * w.sigma_sector)[self.sec]
        rho = w.payoff_rho
        self.g = rho * self.g + math.sqrt(1 - rho * rho) * rng.standard_normal()
        pay = self.g * self.g_sd + self.theta_sig
        if w.fresh_only:
            mu += self.g * self.g_sd * self.sig + self.theta_sig * self.sig * (self.age == 0)
        else:
            mu += pay * self.sig
        h = np.exp(-w.hetero * Z[:, CHARS.index("lowvol")])
        h = h / math.sqrt(np.mean(h * h))
        df = w.tails
        e = rng.standard_t(df, n) * math.sqrt((df - 2) / df) if df < 100 else rng.standard_normal(n)
        return mu + self.sig_idio * h * e


# ----------------------------------------------------------------------------------------------- inference
def crank(x):
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(len(x))
    return (r + 0.5) / len(x) - 0.5


def rcs_basis(x, knots=KNOTS):
    """Restricted (natural) cubic spline basis (Harrell) of x (any shape (..., n)): [x, k-2 nonlinear terms], the
    nonlinear terms scaled by (t_k - t_1)^2. Returns an array with a trailing basis axis."""
    t = knots
    k = len(t)
    d = (t[-1] - t[0]) ** 2
    pk1 = np.maximum(x - t[k - 2], 0.0) ** 3
    pk = np.maximum(x - t[k - 1], 0.0) ** 3
    out = [x]
    for j in range(k - 2):
        out.append((np.maximum(x - t[j], 0.0) ** 3 - pk1 * (t[k - 1] - t[j]) / (t[k - 1] - t[k - 2])
                    + pk * (t[k - 2] - t[j]) / (t[k - 1] - t[k - 2])) / d)
    return np.stack(out, axis=-1)


def designs(sig, Z, sec=None):
    """(X_rcs, X_rank): [centred signal rank | controls | sector dummies]. Controls: 'rcs' (PRIMARY) = RCS of each
    control's cross-sectional normal score (5 fixed knots); 'rank' (diagnostic) = v1 centred ranks. Ranks are
    computed once and shared."""
    n = len(sig)
    R = np.empty((n, Z.shape[1]))
    for j in range(Z.shape[1]):
        R[:, j] = crank(Z[:, j])
    B = rcs_basis(ndtri(R + 0.5))                         # (n, m, 4)
    D = None
    if sec is not None:
        D = np.zeros((n, len(O.SECTORS)))
        D[np.arange(n), sec] = 1.0
    s = crank(sig)[:, None]
    parts_r = [s, B.reshape(n, -1)] + ([D] if D is not None else [])
    parts_k = [s, R] + ([D] if D is not None else [])
    return np.column_stack(parts_r), np.column_stack(parts_k)


def design_controls(sig, Z, spec="rcs", sec=None):
    Xr, Xk = designs(sig, Z, sec)
    return Xr if spec == "rcs" else Xk


def partial_slopes(X, y):
    """Signal slope and top-quintile-dummy coefficient via Frisch-Waugh on the shared control block X[:, 1:]."""
    Q, _ = np.linalg.qr(X[:, 1:])
    res = lambda v: v - Q @ (Q.T @ v)  # noqa: E731
    ry = res(y)
    xs = res(X[:, 0])
    xq = res((X[:, 0] >= 0.3).astype(float))
    pic = float(xs @ ry / math.sqrt((xs @ xs) * (ry @ ry)))
    return float(xs @ ry / (xs @ xs)), float(xq @ ry / (xq @ xq)), pic


def nw_se(b, lag=NW_LAG):
    """Newey-West (Bartlett) standard error of the mean of b."""
    b = np.asarray(b, float)
    n = len(b)
    d = b - b.mean()
    v = d @ d / n
    for l in range(1, lag + 1):
        v += 2 * (1 - l / (lag + 1)) * (d[l:] @ d[:-l]) / n
    return math.sqrt(max(v, 1e-30) / n)


def nw_t(b, lag=NW_LAG):
    return float(np.mean(b) / nw_se(b, lag))


def fixed_b_cv(draws=2_000_000, seed=118007, lag=NW_LAG, chunk=100_000):
    """One-sided critical values of the NW(lag) t under iid Gaussian slopes, T = 118 (reference distribution)."""
    rng = np.random.default_rng(seed)
    ts = []
    for _ in range(draws // chunk):
        b = rng.standard_normal((chunk, T))
        m = b.mean(axis=1, keepdims=True)
        d = b - m
        v = (d * d).mean(axis=1)
        for l in range(1, lag + 1):
            v += 2 * (1 - l / (lag + 1)) * (d[:, l:] * d[:, :-l]).sum(axis=1) / T
        ts.append(m[:, 0] / np.sqrt(v / T))
    t = np.concatenate(ts)
    return {a: float(np.quantile(t, 1 - a)) for a in (0.05, 0.01, 0.005, 0.001)}


def year_ok(b):
    tot = float(np.sum(b))
    if tot <= 0:
        return False
    years = {}
    for t, v in enumerate(b):
        y, _ = O.calendar(t)
        years[y] = years.get(y, 0.0) + float(v)
    return max(years.values()) <= 0.5 * tot


def run_world(w: World, rep: int, tag="FINAL", diag_rank=True):
    """One replication -> statistics, or {'failed': reason} (a computational failure is recorded, never dropped)."""
    try:
        P = Panel(w, seed_of(w.name, rep, tag))
        for t in range(-WARMUP, 0):
            P.step(t)
            P.returns_all()
        H = w.horizon
        R, IDS, recs = [], [], []
        for t in range(T + H - 1):
            sample, _live = P.step(t)
            if t < T:
                recs.append((sample, P.sig[sample].copy(), P.controls(sample), P.sec[sample].copy(),
                             P.age[sample].copy(), P.Z[sample, :8].copy(), O.calendar(t)[1]))
            IDS.append(P.sid.copy())
            R.append(P.returns_all())
        b, tq, br, ics, pics, sizes, fresh, rets_sd = [], [], [], [], [], [], {0: [], 1: [], 2: []}, []
        corr_acc, n_corr = np.zeros(8), 0
        for t, (sample, sig, Zc, sec, age, Ztrue, m) in enumerate(recs):
            r = R[t][sample].copy()
            alive = np.ones(len(sample), bool)
            for h in range(1, H):
                alive &= IDS[t + h][sample] == IDS[t][sample]
                r += np.where(alive, R[t + h][sample], 0.0)
            y = r - r.mean()
            X, Xk = designs(sig, Zc, sec)
            s1, q1, pic = partial_slopes(X, y)
            b.append(s1)
            tq.append(q1)
            pics.append(pic)
            if diag_rank:
                br.append(partial_slopes(Xk, y)[0])
            ics.append(float(np.corrcoef(X[:, 0], crank(y))[0, 1]))
            sizes.append(len(sample))
            fresh[O.phase_of_month(m)].append(float(np.mean(age == 0)))
            rets_sd.append(float(np.std(R[t][sample])))
            if t % 12 == 6:
                for j in range(8):
                    corr_acc[j] += np.corrcoef(sig, Ztrue[:, j])[0, 1]
                n_corr += 1
        b = np.array(b)
        out = dict(t=nw_t(b), t_nw4=nw_t(b, 4), t_iid=nw_t(b, 0), mean_slope=float(b.mean()),
                   sd_slope=float(b.std()), se_nw7=nw_se(b),
                   tq_annual=float(12 * 0.8 * np.mean(tq) / H), half1=float(b[:59].mean()),
                   half2=float(b[59:].mean()), g4=year_ok(b), rho1=float(np.corrcoef(b[1:], b[:-1])[0, 1]),
                   ic_sd=float(np.std(ics)), ic_mean=float(np.mean(ics)), pic_sd=float(np.std(pics)),
                   pic_mean=float(np.mean(pics)), mean_n=float(np.mean(sizes)),
                   min_n=int(min(sizes)), fresh_by_phase=[float(np.mean(fresh[k])) if fresh[k] else None
                                                          for k in range(3)],
                   ret_sd=float(np.mean(rets_sd)), corr=(corr_acc / max(n_corr, 1)).tolist())
        if diag_rank:
            out["t_rank_ctrl"] = nw_t(np.array(br))
        if not all(math.isfinite(v) for v in (out["t"], out["mean_slope"], out["tq_annual"])):
            return dict(failed="non-finite statistic")
        return out
    except Exception as e:                                       # recorded as a computational failure
        return dict(failed=f"{type(e).__name__}: {e}")


def calibrate_payoff(targets=(0.06, 0.09, 0.12), reps=12, g_test=0.006):
    """ENGINEERING (structure only, DEV seeds): partial-IC sd of N0 with no payoff (b0) and with payoff g_test (b1)
    -> kappa = sqrt(b1^2 - b0^2) / g_test -> g_sd(target) = sqrt(target^2 - b0^2) / kappa."""
    def pic(g):
        G_SD[-1.0] = g
        w = World("CAL-N0", ic_sd=-1.0)
        return float(np.mean([run_world(w, r, tag="DEV", diag_rank=False)["pic_sd"] for r in range(reps)]))
    b0, b1 = pic(0.0), pic(g_test)
    kappa = math.sqrt(max(b1 ** 2 - b0 ** 2, 1e-12)) / g_test
    G_SD.pop(-1.0, None)
    return dict(b0=b0, b1=b1, kappa=kappa, g_sd={t: math.sqrt(max(t * t - b0 * b0, 0.0)) / kappa for t in targets})


def full_rule(o, cv1, g2_floor=0.03):
    return bool(o["t"] > cv1 and o["tq_annual"] >= g2_floor and o["half1"] > 0 and o["half2"] > 0 and o["g4"])


def classify(required_complete, adequacy_ok, size_ok, ident_ok, power_3pct, power_target=0.80):
    """Protocol 7 precedence: D (missing / failed required evidence or inadequate framework) > C (any gating
    reliability failure) > A (power >= target) > B."""
    if not required_complete or not adequacy_ok:
        return "D — INSUFFICIENT EVIDENCE"
    if not size_ok or not ident_ok:
        return "C — NOT VALIDATED"
    if power_3pct >= power_target:
        return "A — CALIBRATED AND SUFFICIENTLY POWERED"
    return "B — CALIBRATED BUT UNDERPOWERED"
