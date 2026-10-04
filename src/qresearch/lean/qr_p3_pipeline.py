# qr_p3_pipeline.py — Phase 3 frozen selection procedure (research/phase3/P3_spec.md §§9-13). Pure numpy, no
# QuantConnect imports (tests/test_p3_pipeline.py). Runs identically inside LEAN for every null world and locally.
#
# Inputs per configuration c and calendar year y (2010 = from the official start 2010-03-01):
#   logex[c, y]   total log excess growth over SPY total return in year y (sum of daily ln(1+r_c) - ln(1+r_SPY))
#   cost[c, y]    commissions + slippage (dollars);  eqsum[c, y] sum of daily equity;  notional[c, y] traded notional
#   maxdd[c, y]   maximum drawdown from the start through the end of year y (negative number)
#   sessions[y], spy_maxdd[y], ew_logex[y] (equal-weight universe index vs SPY)
# Score (§9):  s(c) = median over training folds of 252 x (sum logex / sum sessions); folds = consecutive two-year
#              calendar blocks from 2010 (the last may be a single year).
# Safeguards:  realised cost <= 1.5% a year of mean equity;  maxDD >= SPY maxDD - 10 points;
#              folds with positive excess >= ceil(0.75 x number of folds).
# Plateau:     PS(c) = 25th percentile (linear) of s over c and its neighbours (all neighbours, eligible or not).
# Clusters:    connected components (neighbour graph) of survivors = eligible with PS > tau; size >= 3.
# Centre:      the interior survivor (whole neighbourhood inside the cluster) with the highest PS; if none is interior,
#              the survivor with most in-cluster neighbours, then highest PS, then id.
# Simplicity:  one-standard-error rule: among clusters whose centre PS >= PS* - SE*, SE* = 1.2533 sd(folds of the best
#              centre) / sqrt(folds), choose lexicographically fewest conditions, fewest parameters, lowest turnover,
#              highest PS, lowest id. Ranks 2, 3 = the same rule applied to the remaining clusters.
# Walk-forward: for test year Y = 2014..2017: data through Y-1 only, no tau gate, rank-1 centre -> its year-Y excess.
# Search statistic T (Q1): the largest level t such that the eligible configurations with PS > t contain a connected
#              cluster of >= 3 (the plateau level of the best cluster; -inf if none). T > tau <=> a promotable cluster
#              exists at the null threshold tau, so the null statistic and the promotion rule are the same object.
import math

import numpy as np

FIRST_YEAR = 2010
COST_CAP, DD_TOL, POS_SHARE, PS_Q = 0.015, 0.10, 0.75, 25.0
MIN_CLUSTER = 3
SE_MEDIAN = 1.2533
WF_YEARS = (2014, 2015, 2016, 2017)


def folds_upto(last_year):
    """Two-year calendar blocks from 2010 through last_year (the final one may be a single year)."""
    out, y = [], FIRST_YEAR
    while y <= last_year:
        out.append(tuple(range(y, min(y + 2, last_year + 1))))
        y += 2
    return out


class Inputs:
    def __init__(self, ids, logex, cost, eqsum, notional, maxdd, sessions, spy_maxdd, ew_logex, years):
        self.ids = list(ids)
        self.years = list(years)
        self.logex, self.cost, self.eqsum = np.asarray(logex, float), np.asarray(cost, float), np.asarray(eqsum, float)
        self.notional, self.maxdd = np.asarray(notional, float), np.asarray(maxdd, float)
        self.sessions = np.asarray(sessions, float)
        self.spy_maxdd, self.ew_logex = np.asarray(spy_maxdd, float), np.asarray(ew_logex, float)

    def col(self, y):
        return self.years.index(y)


def fold_scores(inp, last_year):
    fl = folds_upto(last_year)
    F = np.zeros((len(inp.ids), len(fl)))
    for k, ys in enumerate(fl):
        cols = [inp.col(y) for y in ys]
        F[:, k] = inp.logex[:, cols].sum(axis=1) / inp.sessions[cols].sum() * 252.0
    return F


def score_table(inp, last_year):
    """s(c), fold scores, eligibility, cost a year, turnover a year, through last_year."""
    F = fold_scores(inp, last_year)
    s = np.median(F, axis=1)
    cols = [inp.col(y) for y in range(FIRST_YEAR, last_year + 1)]
    sess = inp.sessions[cols].sum()
    mean_eq = inp.eqsum[:, cols].sum(axis=1) / sess
    yrs = sess / 252.0
    cost_pa = inp.cost[:, cols].sum(axis=1) / mean_eq / yrs
    turnover = inp.notional[:, cols].sum(axis=1) / mean_eq / yrs
    dd_ok = inp.maxdd[:, inp.col(last_year)] >= inp.spy_maxdd[inp.col(last_year)] - DD_TOL
    need = math.ceil(POS_SHARE * F.shape[1])
    eligible = (cost_pa <= COST_CAP) & dd_ok & ((F > 0).sum(axis=1) >= need)
    return dict(s=s, F=F, eligible=eligible, cost_pa=cost_pa, turnover=turnover)


def plateau_scores(s, nb_index):
    """PS(c) = 25th percentile of s over c and its neighbours. nb_index: list of neighbour index arrays."""
    return np.array([np.percentile(np.concatenate([[s[i]], s[nb]]), PS_Q) for i, nb in enumerate(nb_index)])


def clusters(survive, nb_index, ps, ids):
    """Connected components of survivors (size >= MIN_CLUSTER) with their centres."""
    seen = np.zeros(len(survive), dtype=bool)
    out = []
    for i in np.nonzero(survive)[0]:
        if seen[i]:
            continue
        comp, stack = [], [i]
        seen[i] = True
        while stack:
            j = stack.pop()
            comp.append(j)
            for k in nb_index[j]:
                if survive[k] and not seen[k]:
                    seen[k] = True
                    stack.append(k)
        if len(comp) < MIN_CLUSTER:
            continue
        cs = set(comp)
        interior = [j for j in comp if all(k in cs for k in nb_index[j])]
        if interior:
            centre = max(interior, key=lambda j: (ps[j], -_idkey(ids[j])))
        else:
            centre = max(comp, key=lambda j: (sum(k in cs for k in nb_index[j]), ps[j], -_idkey(ids[j])))
        out.append(dict(members=sorted(comp), centre=int(centre), interior=bool(interior), size=len(comp)))
    return out


def _idkey(cid):
    return int(cid[1:], 16)


def cluster_level(ps, eligible, nb_index):
    """T = max t such that {eligible c : PS(c) > t} contains a connected component of size >= MIN_CLUSTER. Adds
    eligible configurations in decreasing PS order (ties by index) with union-find; T = the PS of the configuration
    whose addition first creates such a component; -inf if none ever does."""
    parent, size = {}, {}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in sorted(np.nonzero(eligible)[0].tolist(), key=lambda j: (-ps[j], j)):
        parent[i], size[i] = i, 1
        for k in nb_index[i]:
            k = int(k)
            if k in parent:
                a, b = find(i), find(k)
                if a != b:
                    if size[a] < size[b]:
                        a, b = b, a
                    parent[b] = a
                    size[a] += size[b]
        if size[find(i)] >= MIN_CLUSTER:
            return float(ps[i])
    return float("-inf")


def rank_clusters(cl, ps, F, complexity, turnover, ids, k=3):
    """Promotion order by the one-standard-error simplicity rule (re-applied to the remaining clusters)."""
    rest = list(cl)
    order = []
    while rest and len(order) < k:
        best = max(rest, key=lambda c: ps[c["centre"]])
        f = F[best["centre"]]
        se = SE_MEDIAN * float(np.std(f, ddof=1)) / math.sqrt(len(f)) if len(f) > 1 else 0.0
        band = [c for c in rest if ps[c["centre"]] >= ps[best["centre"]] - se]
        pick = min(band, key=lambda c: (complexity[c["centre"]][0], complexity[c["centre"]][1], turnover[c["centre"]],
                                        -ps[c["centre"]], _idkey(ids[c["centre"]])))
        order.append(dict(pick, se=se, best_ps=float(ps[best["centre"]])))
        rest.remove(pick)
    return order


def select(inp, nb_index, complexity, last_year, tau=-np.inf, k=3):
    """The frozen procedure on data through last_year. Returns the score table summary and the promotion order."""
    t = score_table(inp, last_year)
    ps = plateau_scores(t["s"], nb_index)
    surv = t["eligible"] & (ps > tau)
    cl = clusters(surv, nb_index, ps, inp.ids)
    ranked = rank_clusters(cl, ps, t["F"], complexity, t["turnover"], inp.ids, k)
    best_ps = max((ps[c["centre"]] for c in cl), default=-np.inf)
    return dict(table=t, ps=ps, n_eligible=int(t["eligible"].sum()), n_survivors=int(surv.sum()), clusters=cl,
                ranked=ranked, best_ps=float(best_ps), T=cluster_level(ps, t["eligible"], nb_index))


def walk_forward(inp, nb_index, complexity, years=WF_YEARS):
    """Procedure-level walk-forward: re-select on data through Y-1 (no tau gate) and record the rank-1 centre's
    year-Y log excess vs SPY and vs the EW universe. Abstention (no cluster) = no pick that year."""
    out = []
    for Y in years:
        r = select(inp, nb_index, complexity, Y - 1, k=1)
        if not r["ranked"]:
            out.append(dict(year=Y, pick=None, ex_spy=0.0, ex_ew=0.0))
            continue
        c = r["ranked"][0]["centre"]
        x = float(inp.logex[c, inp.col(Y)])
        out.append(dict(year=Y, pick=inp.ids[c], ex_spy=x, ex_ew=x - float(inp.ew_logex[inp.col(Y)])))
    picks = sum(1 for o in out if o["pick"] is not None)
    tot_spy, tot_ew = sum(o["ex_spy"] for o in out), sum(o["ex_ew"] for o in out)
    return dict(years=out, picks=picks, total_ex_spy=tot_spy, total_ex_ew=tot_ew,
                passed=bool(picks >= 3 and tot_spy > 0 and tot_ew > 0))


def apparent_winners(inp, table, last_year=2017):
    """REPORTING ONLY (owner 2026-10-04, item 15: keep the fake-winner effect visible); never used for selection.
    The most impressive raw numbers the search finds in a world: the best fold-median score s, the best total log
    excess over SPY (log terminal-wealth ratio) over 2010-03 .. last_year, over all configurations and over eligible
    ones, and how many configurations end with more wealth than SPY."""
    tot = inp.logex[:, [inp.col(y) for y in range(FIRST_YEAR, last_year + 1)]].sum(axis=1)
    el = table["eligible"]
    mx = lambda x: float(np.max(x)) if len(x) else float("-inf")  # noqa: E731
    return dict(best_s=mx(table["s"]), best_s_eligible=mx(table["s"][el]), best_total_logex=mx(tot),
                best_total_logex_eligible=mx(tot[el]), median_total_logex=float(np.median(tot)),
                n_beat_spy=int((tot > 0).sum()), n_configs=int(len(tot)))


def world_summary(inp, nb_index, complexity, tau=-np.inf):
    """Everything the null calibration needs from one world (real or null): the search statistic T and the best
    cluster-centre plateau score on the full training window, the promotion order, and the walk-forward outcome."""
    full = select(inp, nb_index, complexity, 2017, tau=tau, k=3)
    wf = walk_forward(inp, nb_index, complexity)
    return dict(T=full["T"], best_ps=full["best_ps"], apparent=apparent_winners(inp, full["table"]), n_eligible=full["n_eligible"], n_survivors=full["n_survivors"],
                n_clusters=len(full["clusters"]),
                ranked=[dict(centre=inp.ids[c["centre"]], ps=float(full["ps"][c["centre"]]), size=c["size"],
                             se=c["se"]) for c in full["ranked"]],
                wf=wf)


def y_line(cid, logex, cost, eqsum, notional, maxdd, monthly):
    """The published per-configuration line of the real world (derived results only): yearly log excess, costs, equity
    sums, notional, drawdown to date, then monthly log excess. Parsed by parse_y_line / research/phase3/P3_eval.py."""
    f6 = lambda xs: ",".join(f"{x:.6g}" for x in xs)  # noqa: E731
    return (f"Y|{cid}|{f6(logex)}|{f6(cost)}|{f6(eqsum)}|{f6(notional)}|" + ",".join(f"{x:.5f}" for x in maxdd) + "|"
            + f6(monthly))


def parse_y_line(line):
    """(configuration id, [logex, cost, eqsum, notional, maxdd, monthly] as float arrays)."""
    f = line.split("|")
    return f[1], [np.array([float(v) for v in part.split(",")]) if part else np.zeros(0) for part in f[2:]]
