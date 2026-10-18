"""LH-CP3 (owner D244) fiscal-label reconstruction rules — pure functions, no I/O. Implements LH_CP3_protocol.md
sections 4-6. Frozen (SHA-256 in LH_CP3_rules_freeze.json) after development, before the held-back evaluation.

Days are integers (days since 2000-01-01, as qresearch.data_v3.dn). Labels: 1-3 = Q1-Q3, 4 = FY, None = unknown."""
from __future__ import annotations

import hashlib
import math
from collections import Counter
from datetime import date, timedelta

ANNUAL = (357, 378)                 # days between consecutive fiscal-year ends (52/53-week years included)
GAP = (80, 100)                     # frozen Stage C quarter gap
CMP_END_TOL = 3
DUR_OK = {4: ((350, 380),), 1: ((80, 100),), 2: ((80, 100), (170, 190)), 3: ((80, 100), (260, 280))}
K_FORMS = ("10-K", "10-K405")
Q_FORMS = ("10-Q",)
T_FORMS = ("10-KT", "10-QT", "10-KT/A", "10-QT/A")
ORIGINAL_FORMS = K_FORMS + Q_FORMS + ("10-KT", "10-QT")
_EPOCH = date(2000, 1, 1)


# ----------------------------------------------------------------------------------------------- split
def split(cik) -> str:
    """Protocol 5: 'heldback' if the first hex digit of sha256('LH-CP3-split|' + CIK) is 8-f, else 'dev'."""
    h = hashlib.sha256(f"LH-CP3-split|{int(cik)}".encode()).hexdigest()
    return "heldback" if h[0] in "89abcdef" else "dev"


# ----------------------------------------------------------------------------------------------- label status (= LH-CP2)
def label_status(labels):
    """Identical to LH-CP2 label_status: labels newest first -> consistent / broken / unknown."""
    if any(x is None for x in labels):
        return "unknown"
    cycle = all(labels[k] == labels[k + 1] % 4 + 1 for k in range(len(labels) - 1))
    same = all(labels[k] == labels[k + 4] for k in range(len(labels) - 4))
    return "consistent" if cycle and same else "broken"


def rule_v(lstatus, transition, mapping_fail):
    """Identical to LH-CP2 rule V."""
    if lstatus == "broken" or transition or mapping_fail:
        return "invalid"
    if lstatus == "unknown":
        return "unknown"
    return "valid"


# ----------------------------------------------------------------------------------------------- M-SEQ
def dedupe_originals(filings):
    """filings: iterable of (period_day, form, filed_day). One row per report period (+-7 days; earliest filed),
    original forms only, in period order."""
    rows = sorted((p, f, fd) for p, f, fd in filings if f in ORIGINAL_FORMS and p is not None)
    out = []
    for p, f, fd in rows:
        if out and p - out[-1][0] <= 7:
            if fd < out[-1][2]:
                out[-1] = (out[-1][0], f, fd)
            continue
        out.append((p, f, fd))
    return out


def seq_labels(filings, D, transitions=()):
    """M-SEQ (protocol 4). filings: (period_day, form, filed_day) of the registrant's original filings; only rows
    filed <= D - 1 are used. transitions: report days of 10-KT / 10-QT (incl. amendments) filed <= D - 1.
    Returns {period_day: label} for periods inside at least one valid annual bracket."""
    seq = dedupe_originals((p, f, fd) for p, f, fd in filings if fd <= D - 1)
    trans = [r for r in transitions]
    out = {}
    ks = [i for i, r in enumerate(seq) if r[1] in K_FORMS]
    for ia, ib in zip(ks, ks[1:]):
        a, b = seq[ia], seq[ib]
        if not (ANNUAL[0] <= b[0] - a[0] <= ANNUAL[1]):
            continue
        mid = seq[ia + 1:ib]
        if len(mid) != 3 or any(r[1] not in Q_FORMS for r in mid):
            continue
        span = seq[ia:ib + 1]
        if not all(GAP[0] <= y[0] - x[0] <= GAP[1] for x, y in zip(span, span[1:])):
            continue
        if any(a[0] - 7 <= t <= b[0] + 7 for t in trans):
            continue
        for lab, r in zip((4, 1, 2, 3, 4), span):
            prev = out.get(r[0])
            out[r[0]] = lab if prev in (None, lab) else "conflict"
    return out


# ----------------------------------------------------------------------------------------------- M-CMP
def dur_ok(label_e, dur):
    return any(lo <= dur <= hi for lo, hi in DUR_OK.get(label_e, ()))


def cmp_label(p, evidence, D, excluded=frozenset()):
    """M-CMP (protocol 4). evidence: iterable of (accession, period_day_E, filed_day_E, label_E, [(end_day, dur_days)]),
    original 10-Q / 10-K filings of the same CIK. excluded: accessions that must not be used (the period's own filing,
    hidden filings). Returns a label, 'conflict' or None."""
    labs = set()
    for accn, pe, fd, le, facts in evidence:
        if accn in excluded or fd > D - 1 or le not in (1, 2, 3, 4) or pe is None:
            continue
        if not (ANNUAL[0] <= pe - p <= ANNUAL[1]):
            continue
        if any(abs(e - p) <= CMP_END_TOL and dur_ok(le, du) for e, du in facts):
            labs.add(le)
    if not labs:
        return None
    return labs.pop() if len(labs) == 1 else "conflict"


# ----------------------------------------------------------------------------------------------- R*
def combine(seq, cmp):
    """R* (protocol 4) -> (label or None, tier) with tier in L2 / L3 / conflict / none."""
    if seq == "conflict" or cmp == "conflict":
        return None, "conflict"
    if seq is not None and cmp is not None:
        return (seq, "L2") if seq == cmp else (None, "conflict")
    if seq is not None or cmp is not None:
        return (seq if seq is not None else cmp), "L3"
    return None, "none"


# ----------------------------------------------------------------------------------------------- H-FYE
def h_fye(fye, period_day, form):
    """Header- / index-implied fiscal quarter from a fiscal-year-end code 'MMDD' (protocol 4): inference only."""
    try:
        fy = date(2001, int(fye[:2]), int(fye[2:]))
    except (TypeError, ValueError):
        return None
    pd = _EPOCH + timedelta(days=int(period_day))
    try:
        pp = date(2001, pd.month, 28 if (pd.month == 2 and pd.day == 29) else pd.day)
    except ValueError:
        return None
    delta = (pp - fy).days % 365
    if form in K_FORMS:
        return 4 if (delta <= 10 or delta >= 355) else "inconsistent"
    if form in Q_FORMS:
        q = round(delta / 91.31)
        return q if q in (1, 2, 3) and abs(delta - 91.31 * q) <= 15 else None
    return None


# ----------------------------------------------------------------------------------------------- V4 metric
def isolated_off_cycle(labels):
    """labels oldest -> newest (None allowed). Positions i (1 <= i <= n-2) whose label is off the cycle implied by
    BOTH labelled neighbours (which agree with each other): label[i-1] -> label[i+1] spans two steps."""
    out = []
    for i in range(1, len(labels) - 1):
        a, x, b = labels[i - 1], labels[i], labels[i + 1]
        if None in (a, x, b):
            continue
        if b == (a + 1) % 4 + 1 and x != a % 4 + 1:
            out.append(i)
    return out


# ----------------------------------------------------------------------------------------------- statistics
def cp_upper(k, n, alpha=0.05):
    """One-sided Clopper-Pearson upper bound for k successes of n."""
    if n == 0:
        return None
    if k >= n:
        return 1.0
    from scipy.stats import beta
    return float(beta.ppf(1 - alpha, k + 1, n - k))


def cluster_upper(by_reg, reps=2000, seed=20261018, alpha=0.05):
    """by_reg: {registrant: (errors, trials)}. Registrant-cluster bootstrap one-sided upper bound of the pooled
    error rate (protocol 5)."""
    import numpy as np
    regs = [v for v in by_reg.values() if v[1] > 0]
    if not regs:
        return None
    e = np.array([r[0] for r in regs], float)
    n = np.array([r[1] for r in regs], float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(regs), size=(reps, len(regs)))
    rates = e[idx].sum(1) / n[idx].sum(1)
    return float(np.quantile(rates, 1 - alpha))


def rate(k, n):
    return None if not n else k / n


def fmt(x, nd=4):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), nd)
