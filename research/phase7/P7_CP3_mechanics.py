"""P7-CP3 (owner D171): score availability, portfolio capacity, churn and cost MECHANICS from the E993-01 export.
NO RETURN OF ANY KIND: the inputs are integer scores, disqualifier flags, ADV20, FF12 codes and regime states; the
shadow book uses the frozen planner (qr_p7_score.plan_review / weekly_check) with a constant mechanical notional, so
no price, equity or return exists anywhere. Writes research/phase7/P7_CP3_mechanics.json and P7_CP3_tables.md.

Pre-registered definitions (docs/owner/2026-10-06_p7cp3_mechanics.md, D171): entry 90 / 85 / 80 / 75; profiles H1
(exit E-5, buffer 3), H2 (E-10, 5), H3 (E-15, 10); K = 6 / 8 / 10 / 12; no regime cap; whipsaw = a security re-bought
at one of the 3 monthly reviews following its sale; cost per order = $7 + 10 bps x $100K x min(10%, 1/K) ($200K
sensitivity); 84 reviews = 7.0 years."""
import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_p7_export as E  # noqa: E402
import qr_p7_score as S  # noqa: E402

THRESHOLDS = (90, 85, 80, 75)
PROFILES = dict(H1=(5, 3), H2=(10, 5), H3=(15, 10))
PROFILE_NAMES = dict(H1="Tight", H2="Balanced", H3="Patient")
KS = (6, 8, 10, 12)
WHIPSAW_REVIEWS = 3
COMMISSION = 7.0
SLIPPAGE = 0.0010
CAPITALS = (100_000.0, 200_000.0)
YEARS = 7.0                                  # 84 monthly reviews
BINS = ((0, 49), (50, 59), (60, 69), (70, 74), (75, 79), (80, 84), (85, 89), (90, 94), (95, 100))
COUNT_BUCKETS = (("0", 0, 0), ("1-2", 1, 2), ("3-5", 3, 5), ("6-8", 6, 8), ("9-10", 9, 10), (">10", 11, 10 ** 9))
DQ_FULL = dict(H1_financial="H1_sector_not_scorable", H1_no_sic="H1_sector_not_scorable",
               H2="H2_fundamentals_missing_or_stale", H3="H3_insufficient_history",
               H4="H4_corporate_event_contamination", H5="H5_stale_price", H6="H6_broken_long_term_trend",
               H7="H7_financial_impairment")
DATA_BITS = ("H1_financial", "H1_no_sic", "H2", "H3", "H4", "H5")
DQ_BITS = DATA_BITS + ("H6", "H7")
FUNNEL = (("duplicate share class", "duplicate_class"), ("Financial / REIT (H1)", "H1_financial"),
          ("insufficient history (H3)", "H3"), ("fundamental data (H2)", "H2"), ("sector data: no SIC (H1)", "H1_no_sic"),
          ("corporate event (H4)", "H4"), ("stale price (H5)", "H5"), ("technical DQ: broken trend (H6)", "H6"),
          ("fundamental DQ: impairment (H7)", "H7"))
DIMS = E.DIMS


def q(xs, ps=(10, 25, 50, 75, 90)):
    xs = np.asarray(xs, float)
    if xs.size == 0:
        return dict(n=0)
    out = dict(n=int(xs.size), mean=round(float(xs.mean()), 3), min=float(xs.min()), max=float(xs.max()))
    for p in ps:
        out[f"p{p}"] = round(float(np.percentile(xs, p)), 3)
    return out


def r3(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 4)


# ----------------------------------------------------------------------------------------------- load
def load(path):
    pay = json.loads(gzip.open(path).read())
    sids = pay["sids"]
    revs = []
    for t, tk, enc in pay["reviews"]:
        rows = {sids[r["i"]]: r for r in E.decode_rows(enc)}
        revs.append(dict(t=t, tk=tk, year=tk[:4], rows=rows))
    weekly = []
    for t, tk, members, enc in pay["weekly"]:
        bits = {}
        for part in enc.split(",") if enc else []:
            i, b = part.split(":")
            bits[sids[int(i)]] = int(b)
        weekly.append(dict(t=t, tk=tk, members={sids[i] for i in members}, bits=bits))
    return pay, revs, weekly


def elig(r):
    return E.eligible_flag(r["bits"], r["total"])


def has(r, b):
    return bool(r["bits"] & E.BIT[b])


def layers(r):
    p = r["points"]
    return p[0] + p[1] + p[2], p[3] + p[4] + p[5] + p[6], p[7]


# ----------------------------------------------------------------------------------------------- availability
def universe_and_funnel(revs):
    by = defaultdict(list)
    for rv in revs:
        rows = list(rv["rows"].values())
        stages = [("base eligible universe", len(rows))]
        rem = rows
        for name, b in FUNNEL:
            rem = [r for r in rem if not has(r, b)]
            stages.append((name, len(rem)))
        stages.append(("fully scorable and eligible (no hard disqualifier)", len(rem)))
        assert all(elig(r) for r in rem) and len(rem) == sum(1 for r in rows if elig(r))
        for th in sorted(THRESHOLDS):
            stages.append((f"score >= {th}", sum(1 for r in rem if r["total"] >= th)))
        by[rv["year"]].append(stages)
    out = {}
    for y, lst in sorted(by.items()):
        out[y] = [[lst[0][i][0], round(float(np.mean([s[i][1] for s in lst])), 1),
                   int(min(s[i][1] for s in lst)), int(max(s[i][1] for s in lst))] for i in range(len(lst[0]))]
    allr = [s for lst in by.values() for s in lst]
    out["all"] = [[allr[0][i][0], round(float(np.mean([s[i][1] for s in allr])), 1)] for i in range(len(allr[0]))]
    return out


def dq_counts(revs):
    cnt, uniq, pair = Counter(), Counter(), Counter()
    n = 0
    by_year = defaultdict(Counter)
    for rv in revs:
        for r in rv["rows"].values():
            if has(r, "duplicate_class"):
                continue
            n += 1
            on = [b for b in DQ_BITS if has(r, b)]
            for b in on:
                cnt[b] += 1
                by_year[rv["year"]][b] += 1
            if len(on) == 1:
                uniq[on[0]] += 1
            for i, a in enumerate(on):
                for b in on[i + 1:]:
                    pair[f"{a}&{b}"] += 1
            if not on:
                cnt["none"] += 1
            by_year[rv["year"]]["rows"] += 1
    return dict(rows=n, any_flag=dict(cnt), only_this_flag=dict(uniq), pairs=dict(pair.most_common(20)),
                share_of_rows={b: r3(cnt[b] / n) for b in DQ_BITS},
                by_year={y: {b: r3(c[b] / c["rows"]) for b in DQ_BITS} for y, c in sorted(by_year.items())},
                note="raw flags on every kept-class row with the inputs (H6 needs a trend state, H7 needs the "
                     "fundamental inputs); the frozen score applies H6 / H7 to the data-scorable set only")


def baseline_diag(revs):
    out = {}
    for rv in revs:
        c = out.setdefault(rv["year"], Counter())
        for r in rv["rows"].values():
            if has(r, "duplicate_class") or has(r, "H1_financial") or has(r, "H1_no_sic"):
                continue
            c["nonfin_rows"] += 1
            c["H2"] += has(r, "H2")
            c["H2_baseline_only"] += has(r, "H2_baseline_only")
            c["baseline_in_store_12m_earlier"] += has(r, "baseline_in_store")
    return {y: dict(c) for y, c in sorted(out.items())}


def distributions(revs):
    res = {}
    for pop in ("data_scorable", "eligible"):
        hist = defaultdict(Counter)
        vals = defaultdict(list)
        for rv in revs:
            for r in rv["rows"].values():
                if r["total"] is None or (pop == "eligible" and not elig(r)):
                    continue
                for lo, hi in BINS:
                    if lo <= r["total"] <= hi:
                        hist[rv["year"]][f"{lo}-{hi}"] += 1
                        hist["all"][f"{lo}-{hi}"] += 1
                vals[rv["year"]].append(r["total"])
                vals["all"].append(r["total"])
        res[pop] = {y: dict(n=len(vals[y]), share={k: r3(hist[y][k] / len(vals[y])) for k in
                                                     [f"{lo}-{hi}" for lo, hi in BINS]},
                            at_least={th: r3(np.mean(np.array(vals[y]) >= th)) for th in THRESHOLDS},
                            quantiles=q(vals[y], (10, 25, 50, 75, 90, 99)))
                    for y in sorted(vals)}
    return res


def layer_stats(revs):
    T, F, Sx, Tot = [], [], [], []
    rho = []
    for rv in revs:
        lt, lf, ls, lo = [], [], [], []
        for r in rv["rows"].values():
            if r["total"] is None:
                continue
            a, b, c = layers(r)
            lt.append(a)
            lf.append(b)
            ls.append(c)
            lo.append(r["total"])
        T += lt
        F += lf
        Sx += ls
        Tot += lo
        X = np.array([lt, lf, ls, lo], float)
        R = np.argsort(np.argsort(X, axis=1), axis=1).astype(float)
        if X.shape[1] >= 30 and np.all(X.std(axis=1) > 0):
            rho.append(np.corrcoef(R))
    X = np.array([T, F, Sx, Tot], float)
    names = ["technical", "fundamental", "sector", "total"]
    return dict(population="data-scorable rows (all reviews)",
                technical=q(T), fundamental=q(F), sector=q(Sx), total=q(Tot),
                sector_values={str(k): r3(v / len(Sx)) for k, v in sorted(Counter(Sx).items())},
                names=names, pearson_pooled=np.round(np.corrcoef(X), 3).tolist(),
                spearman_mean_per_review=np.round(np.mean(rho, axis=0), 3).tolist() if rho else None)


def composition(revs, ff_names):
    out = {}
    uni_ff = Counter()
    n_uni = 0
    for rv in revs:
        for r in rv["rows"].values():
            if elig(r):
                uni_ff[ff_names[r["ff"]]] += 1
                n_uni += 1
    for th in sorted(THRESHOLDS):
        rs, ids = [], set()
        for rv in revs:
            for sid, r in rv["rows"].items():
                if elig(r) and r["total"] >= th:
                    rs.append(r)
                    ids.add(sid)
        if not rs:
            out[th] = dict(n=0)
            continue
        P = np.array([r["points"] for r in rs], float)
        L = np.array([layers(r) for r in rs], float)
        ff = Counter(ff_names[r["ff"]] for r in rs)
        out[th] = dict(stock_months=len(rs), distinct_stocks=len(ids),
                       layer_quantiles=dict(technical=q(L[:, 0], (10, 50)), fundamental=q(L[:, 1], (10, 50)),
                                            sector=q(L[:, 2], (10, 50))),
                       share_with_a_weak_layer=dict(
                           technical_below_half=r3(np.mean(L[:, 0] < 20)), fundamental_below_half=r3(np.mean(L[:, 1] < 22.5)),
                           sector_zero=r3(np.mean(L[:, 2] == 0)),
                           any=r3(np.mean((L[:, 0] < 20) | (L[:, 1] < 22.5) | (L[:, 2] == 0)))),
                       max_possible_without_layer=dict(technical=60, fundamental=55, sector=85),
                       mean_layers=dict(technical=r3(L[:, 0].mean()), fundamental=r3(L[:, 1].mean()),
                                        sector=r3(L[:, 2].mean())),
                       mean_points={d: r3(P[:, i].mean()) for i, d in enumerate(DIMS)},
                       share_at_max={d: r3(np.mean(P[:, i] == S.POINTS[d])) for i, d in enumerate(DIMS)},
                       share_zero={d: r3(np.mean(P[:, i] == 0)) for i, d in enumerate(DIMS)},
                       trend_state={"strong": r3(np.mean(P[:, 0] == 15)), "moderate": r3(np.mean(P[:, 0] == 8)),
                                    "weak": r3(np.mean(P[:, 0] == 0))},
                       sector_state={"supportive": r3(np.mean(P[:, 7] == 15)), "neutral": r3(np.mean(P[:, 7] == 8)),
                                     "weak": r3(np.mean(P[:, 7] == 0))},
                       ff12_share={k: r3(v / len(rs)) for k, v in ff.most_common()},
                       ff12_universe_share={k: r3(v / n_uni) for k, v in uni_ff.most_common()},
                       adv20_musd=q([r["adv_k"] / 1000.0 for r in rs], (25, 50, 75)))
    return out


def candidate_counts(revs):
    out = {}
    for th in THRESHOLDS:
        c = [sum(1 for r in rv["rows"].values() if elig(r) and r["total"] >= th) for rv in revs]
        yrs = defaultdict(list)
        for rv, x in zip(revs, c):
            yrs[rv["year"]].append(x)
        arr = np.array(c, float)
        out[th] = dict(per_review=c, stats=q(c, (10, 25, 50, 75, 90)),
                       buckets={k: r3(np.mean((arr >= lo) & (arr <= hi))) for k, lo, hi in COUNT_BUCKETS},
                       zero_months=int((arr == 0).sum()),
                       by_year={y: dict(mean=r3(np.mean(v)), median=float(np.median(v)), min=int(min(v)),
                                        max=int(max(v)), zero_months=int(sum(1 for x in v if x == 0)),
                                        cv=r3(np.std(v) / np.mean(v)) if np.mean(v) > 0 else None)
                                for y, v in sorted(yrs.items())},
                       lag1_autocorr=r3(np.corrcoef(arr[:-1], arr[1:])[0, 1]) if arr.std() > 0 else None)
    return out


# ----------------------------------------------------------------------------------------------- persistence
def persistence(revs):
    M = len(revs)
    sids = sorted({s for rv in revs for s in rv["rows"]})
    out = {}
    for th in THRESHOLDS:
        runs, reentries, gaps = [], 0, []
        band = {g: [] for g in (5, 10, 15)}
        for s in sids:
            above = [bool(s in rv["rows"] and elig(rv["rows"][s]) and rv["rows"][s]["total"] >= th) for rv in revs]
            m, prev_end = 0, None
            while m < M:
                if above[m]:
                    st = m
                    while m < M and above[m]:
                        m += 1
                    runs.append((st, m - st, m == M))
                    if prev_end is not None:
                        reentries += 1
                        gaps.append(st - prev_end)
                    prev_end = m
                    # band persistence: months from the start while eligible and score >= th - g
                    for g in band:
                        k = st
                        while k < M and s in revs[k]["rows"] and elig(revs[k]["rows"][s]) and \
                                revs[k]["rows"][s]["total"] >= th - g:
                            k += 1
                        band[g].append((k - st, k == M))
                else:
                    m += 1
        L = [x[1] for x in runs]
        surv = {}
        for k in (2, 3, 6, 12):
            el = [x for x in runs if x[0] <= M - k]
            surv[k] = r3(np.mean([x[1] >= k for x in el])) if el else None
        out[th] = dict(runs=len(runs), run_months=q(L, (25, 50, 75, 90)),
                       censored_runs=sum(1 for x in runs if x[2]),
                       survival={str(k): v for k, v in surv.items()},
                       reentries=reentries, reentries_per_year=r3(reentries / YEARS),
                       reentry_gap_months=q(gaps, (25, 50, 75)),
                       reentries_within_3_reviews=sum(1 for g in gaps if g <= 3),
                       band_persistence={f"exit_{th - g}": dict(q([x[0] for x in v], (25, 50, 75, 90)),
                                                                censored=sum(1 for x in v if x[1]))
                                         for g, v in band.items()})
    return out


def score_changes(revs):
    """Month-to-month change of the total for eligible stocks >= th at review m that are data-scorable at m + 1, and
    which dimensions lost points when the stock fell below th (explains short persistence; scores only)."""
    out = {}
    for th in THRESHOLDS:
        d, lost, n_fell, n = [], Counter(), 0, 0
        for a, b in zip(revs, revs[1:]):
            for s, r in a["rows"].items():
                if not (elig(r) and r["total"] >= th):
                    continue
                r2 = b["rows"].get(s)
                if r2 is None or r2["total"] is None:
                    continue
                n += 1
                d.append(r2["total"] - r["total"])
                if r2["total"] < th:
                    n_fell += 1
                    for i, dim in enumerate(DIMS):
                        if r2["points"][i] < r["points"][i]:
                            lost[dim] += 1
        out[th] = dict(pairs=n, change=q(d, (10, 25, 50, 75, 90)), fell_below=n_fell,
                       dimension_lost_points_share={k: r3(v / n_fell) for k, v in lost.most_common()} if n_fell else {})
    return out


def sector_concentration(revs, ff_names):
    out = {}
    for th in THRESHOLDS:
        mx, top, n50, nrev = [], Counter(), 0, 0
        for rv in revs:
            c = Counter(ff_names[r["ff"]] for r in rv["rows"].values() if elig(r) and r["total"] >= th)
            n = sum(c.values())
            if n < 5:
                continue
            nrev += 1
            g, k = c.most_common(1)[0]
            mx.append(k / n)
            top[g] += 1
            n50 += int(k / n > 0.5)
        per_year = defaultdict(Counter)
        tot = Counter()
        for rv in revs:
            for r in rv["rows"].values():
                if elig(r) and r["total"] >= th:
                    per_year[rv["year"]][ff_names[r["ff"]]] += 1
                    tot[ff_names[r["ff"]]] += 1
        out[th] = dict(reviews_with_ge5=nrev, max_sector_share=q(mx, (50, 90)), reviews_one_sector_gt_50pct=n50,
                       most_frequent_top_sector=dict(top.most_common(5)),
                       mean_candidates_per_review_by_sector={k: r3(v / len(revs)) for k, v in tot.most_common()},
                       share_by_year={y: {k: r3(v / sum(c.values())) for k, v in c.most_common(4)}
                                      for y, c in sorted(per_year.items())})
    return out


# ----------------------------------------------------------------------------------------------- regime
def regime_stats(pay):
    R = pay["regimes"]
    seq = [x[7] for x in R]
    yrs = defaultdict(Counter)
    for x in R:
        yrs[x[0][:4]][x[7]] += 1
    runs = []
    i = 0
    while i < len(seq):
        j = i
        while j + 1 < len(seq) and seq[j + 1] == seq[i]:
            j += 1
        runs.append((seq[i], j - i + 1, R[i][0], R[j][0]))
        i = j + 1
    trans = defaultdict(Counter)
    for a, b in zip(seq, seq[1:]):
        trans[a][b] += 1
    changes = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
    longest = max(runs, key=lambda x: x[1])
    return dict(counts=dict(Counter(seq)), share={k: r3(v / len(seq)) for k, v in Counter(seq).items()},
                by_year={y: dict(c) for y, c in sorted(yrs.items())},
                durations={k: q([r[1] for r in runs if r[0] == k], (50,)) for k in S.REGIMES},
                runs=[list(r) for r in runs], transitions={a: dict(b) for a, b in trans.items()},
                changes=changes, changes_per_year=r3(changes / YEARS), longest_run=list(longest),
                spy_trend=dict(Counter(x[1] for x in R)), breadth_level=dict(Counter(x[6] for x in R)),
                breadth=q([x[2] for x in R if x[2] is not None], (10, 50, 90)))


# ----------------------------------------------------------------------------------------------- capacity
def capacity(cc):
    out = {}
    for th in THRESHOLDS:
        c = np.array(cc[th]["per_review"], float)
        out[th] = {}
        for K in KS:
            f = np.minimum(c, K) / K
            out[th][K] = dict(all_slots=r3(np.mean(f >= 1)), ge80=r3(np.mean(f >= 0.8)), ge50=r3(np.mean(f >= 0.5)),
                              lt50=r3(np.mean(f < 0.5)), mean_fill=r3(f.mean()),
                              max_initial_gross=r3(min(K * 0.10, 1.0)), position_size=r3(min(0.10, 1.0 / K)))
    return out


# ----------------------------------------------------------------------------------------------- churn (shadow book)
def records_of(rows):
    rec = {}
    for s, r in rows.items():
        if has(r, "duplicate_class"):
            continue
        dq = [DQ_FULL[b] for b in DATA_BITS if has(r, b)]
        if r["total"] is not None:
            dq += [DQ_FULL[b] for b in ("H6", "H7") if has(r, b)]
        rec[s] = dict(total=r["total"], eligible=elig(r), dq=list(dict.fromkeys(dq)))
    return rec


def cause_of(reason):
    if reason.startswith("left the eligible universe"):
        return "universe_exit"
    if reason.startswith("hard disqualifier"):
        return "dq_review"
    if reason.startswith("score"):
        return "exit_threshold"
    if reason.startswith("replaced by"):
        return "replacement"
    if reason.startswith("regime"):
        return "regime_cap"
    raise ValueError(reason)


def timeline(revs, weekly):
    ev = [("R", rv["tk"], m) for m, rv in enumerate(revs)] + [("W", w["tk"], i) for i, w in enumerate(weekly)]
    ev.sort(key=lambda e: (e[1], 0 if e[0] == "R" else 1))
    return ev


def simulate(revs, weekly, ev, th, gap, buf, K):
    hold = {}                     # sid -> (entry date, entry review)
    last_sale = {}                # sid -> review index of the latest review at or before the sale
    trades = []                   # (kind, sid, date, review index, cause)
    closed = []                   # (sid, entry date, exit date, cause)
    util, books = [], []
    anomalies = 0
    m_cur = -1
    for kind, tk, i in ev:
        if kind == "R":
            m_cur = i
            rv = revs[i]
            rec = records_of(rv["rows"])
            adv = {s: r["adv_k"] * 1000.0 for s, r in rv["rows"].items()}
            frozen = {h for h in hold if h in rec and "H4_corporate_event_contamination" in rec[h]["dq"]}
            plan = S.plan_review(set(hold), rec, adv, th, th - gap, buf, K, K, frozenset(frozen), set(rv["rows"]))
            for s in plan["sell"]:
                c = cause_of(plan["reasons"][s])
                trades.append(("sell", s, tk, i, c))
                closed.append((s, hold[s][0], tk, c))
                del hold[s]
                last_sale[s] = i
            for s in plan["buy"]:
                rep = plan["reasons"][s].startswith("replacement")
                ws = s in last_sale and 0 < i - last_sale[s] <= WHIPSAW_REVIEWS
                trades.append(("buy", s, tk, i, ("replacement_buy" if rep else "entry") + ("|whipsaw" if ws else "")))
                hold[s] = (tk, i)
            util.append(len(hold) / K)
            books.append((rv["year"], sorted(hold), [rv["rows"][h]["total"] for h in hold]))
        else:
            w = weekly[i]
            recs = {}
            for s in w["members"]:
                b = w["bits"].get(s, 0)
                recs[s] = dict(dq=[DQ_FULL[x] for x in DQ_BITS if b & E.BIT[x]])
            for h in hold:
                if h not in recs:
                    anomalies += 1
            frozen = {h for h in hold if w["bits"].get(h, 0) & E.BIT["H4"]}
            out = S.weekly_check(set(hold), recs, frozenset(frozen))
            for s, dq in out.items():
                trades.append(("sell", s, tk, m_cur, "dq_weekly:" + ",".join(dq)))
                closed.append((s, hold[s][0], tk, "dq_weekly"))
                del hold[s]
                last_sale[s] = m_cur
    end = revs[-1]["tk"]
    open_ = [(s, v[0], end) for s, v in hold.items()]
    return trades, closed, open_, util, books, anomalies


def months(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days / 30.4375


def churn_metrics(revs, weekly, ev, ff_by_sid, th, prof, K):
    gap, buf = PROFILES[prof]
    trades, closed, open_, util, books, anom = simulate(revs, weekly, ev, th, gap, buf, K)
    buys = [t for t in trades if t[0] == "buy"]
    sells = [t for t in trades if t[0] == "sell"]
    cause = Counter(t[4].split(":")[0] for t in sells)
    ws = sum(1 for t in buys if t[4].endswith("|whipsaw"))
    dur = [months(a, b) for _, a, b, _ in closed]
    cens = [months(a, b) for _, a, b in open_]
    alld = dur + cens
    orders = len(buys) + len(sells)
    costs = {}
    for cap in CAPITALS:
        N = cap * min(0.10, 1.0 / K)
        com = orders * COMMISSION / YEARS
        slip = orders * SLIPPAGE * N / YEARS
        costs[str(int(cap))] = dict(notional_per_order=N, commission_usd_yr=r3(com), slippage_usd_yr=r3(slip),
                                    total_usd_yr=r3(com + slip), commission_pct=r3(100 * com / cap),
                                    slippage_pct=r3(100 * slip / cap), total_pct=r3(100 * (com + slip) / cap),
                                    cost_class=("< 0.5%" if 100 * (com + slip) / cap < 0.5 else
                                                "0.5-1.0%" if 100 * (com + slip) / cap <= 1.0 else "> 1.0%"))
    # weekly disqualifier burden and requalification (months until the stock is again an eligible candidate >= th)
    wk = [t for t in sells if t[4].startswith("dq_weekly")]
    wk_names = sorted({f"{t[1].split()[0]} {t[2]} {t[4].split(':')[1]}" for t in wk})
    wk_cat = Counter(x for t in wk for x in t[4].split(":")[1].split(","))
    req = []
    for t in [s for s in sells if s[4] in ("dq_review",) or s[4].startswith("dq_weekly")]:
        m0 = t[3]
        k = next((m for m in range(m0 + 1, len(revs)) if t[1] in revs[m]["rows"] and elig(revs[m]["rows"][t[1]])
                  and revs[m]["rows"][t[1]]["total"] >= th), None)
        req.append(None if k is None else k - m0)
    rq = [x for x in req if x is not None]
    maxsec = []
    for y, hs, sc in books:
        c = Counter(ff_by_sid[h] for h in hs)
        if hs:
            maxsec.append(max(c.values()) / len(hs))
    U = np.array(util)
    return dict(entry=th, profile=prof, exit=th - gap, buffer=buf, K=K,
                entries_per_year=r3(sum(1 for t in buys if t[4].startswith("entry")) / YEARS),
                replacement_buys_per_year=r3(sum(1 for t in buys if t[4].startswith("replacement")) / YEARS),
                buys_per_year=r3(len(buys) / YEARS), sells_per_year=r3(len(sells) / YEARS),
                exits_per_year={k: r3(v / YEARS) for k, v in sorted(cause.items())},
                normal_exits_per_year=r3(cause.get("exit_threshold", 0) / YEARS),
                dq_exits_per_year=r3((cause.get("dq_review", 0) + cause.get("dq_weekly", 0)) / YEARS),
                universe_exits_per_year=r3(cause.get("universe_exit", 0) / YEARS),
                replacements_per_year=r3(cause.get("replacement", 0) / YEARS),
                orders_per_year=r3(orders / YEARS), orders_total=orders,
                sell_then_rebuy=ws, sell_then_rebuy_per_year=r3(ws / YEARS),
                sell_then_rebuy_share_of_sells=r3(ws / len(sells)) if sells else None,
                holding_months_closed=q(dur, (25, 50, 75)), holding_months_open_at_end=q(cens, (50,)),
                positions_closed=len(dur), positions_open_at_end=len(cens),
                held_ge={str(k): r3(np.mean(np.array(dur) >= k)) if dur else None for k in (3, 6, 12)},
                held_ge_incl_open={str(k): r3(np.mean(np.array(alld) >= k)) if alld else None for k in (3, 6, 12)},
                longest_months=r3(max(alld)) if alld else None,
                utilisation=dict(mean=r3(U.mean()), full_reviews=r3(np.mean(U >= 1)), empty_reviews=r3(np.mean(U == 0)),
                                 mean_empty_slots=r3(np.mean(K - U * K)),
                                 by_year={y: r3(np.mean([len(b[1]) / K for b in books if b[0] == y]))
                                          for y in sorted({b[0] for b in books})}),
                book_max_sector_share=q(maxsec, (50, 90)),
                book_median_score=r3(np.median([x for b in books for x in b[2]])) if any(b[2] for b in books) else None,
                weekly_dq_exits_per_year=r3(len(wk) / YEARS), weekly_dq_categories=dict(wk_cat), weekly_dq_names=wk_names,
                weekly_share_of_orders=r3(len(wk) / orders) if orders else None,
                dq_requalified=len(rq), dq_not_requalified=len(req) - len(rq),
                requalify_months=q(rq, (25, 50, 75)),
                costs=costs, weekly_anomalies=anom)


def weekly_burden(revs, weekly):
    """Onsets of a hard disqualifier at weekly checks among the possible holdings (securities eligible at the latest
    review that were ever an eligible candidate >= 75), by year and category."""
    prev = {}
    by = defaultdict(Counter)
    names = defaultdict(set)
    for w in weekly:
        y = w["tk"][:4]
        for s in w["members"]:
            b = w["bits"].get(s, 0)
            pb = prev.get(s, 0)
            for x in ("H1_financial", "H1_no_sic", "H2", "H3", "H4", "H5", "H6", "H7"):
                if b & E.BIT[x] and not pb & E.BIT[x]:
                    by[y][x] += 1
                    names[x].add(s)
            prev[s] = b
        by[y]["member_weeks"] += len(w["members"])
    return dict(onsets_by_year={y: dict(c) for y, c in sorted(by.items())},
                distinct_securities={k: len(v) for k, v in names.items()},
                examples={k: sorted(v)[:8] for k, v in names.items()})


def share_class_audit(pay, revs):
    n_groups, removed, ok, bad, dates = 0, 0, 0, [], 0
    ciks = set()
    examples = {}
    for (t, groups), rv in zip(pay["duplicates"], revs):
        if groups:
            dates += 1
        for cik, members, kept in groups:
            n_groups += 1
            ciks.add(cik)
            removed += len(members) - len(kept)
            adv = {s: rv["rows"][s]["adv_k"] for s in members}
            best = max(adv.values())
            exp = min(s for s in members if adv[s] == best)
            if len(kept) == 1 and (kept[0] == exp or adv[kept[0]] == best):
                ok += 1
            else:
                bad.append([t, cik, members, kept])
            examples.setdefault(cik, [t, members, kept])
    return dict(reviews_with_duplicates=dates, company_review_groups=n_groups, distinct_companies=len(ciks),
                classes_removed=removed, rule_followed=ok, rule_violations=bad[:10],
                examples=[examples[c] for c in sorted(examples)[:20]])


# ----------------------------------------------------------------------------------------------- main
def main(path=HERE / "P7_CP3_E993_payload.json.gz"):
    pay, revs, weekly = load(path)
    assert len(revs) == 84 and revs[0]["tk"] == "2011-01-31" and revs[-1]["tk"] == "2017-12-29"
    assert all(rv["tk"] <= "2017-12-29" for rv in revs) and all(w["tk"] <= "2017-12-29" for w in weekly)
    ff_names = pay["ff12_names"]
    ff_by_sid = {}
    for rv in revs:
        for s, r in rv["rows"].items():
            ff_by_sid[s] = ff_names[r["ff"]]
    out = dict(source="E993-01 (X993 v1.0)", reviews=len(revs), weekly_checks=len(weekly),
               first_review=revs[0]["tk"], last_review=revs[-1]["tk"])
    out["base_universe_by_year"] = {y: q([len(rv["rows"]) for rv in revs if rv["year"] == y], (50,))
                                    for y in sorted({rv["year"] for rv in revs})}
    out["funnel"] = universe_and_funnel(revs)
    out["dq"] = dq_counts(revs)
    out["baseline_diagnostic"] = baseline_diag(revs)
    out["distributions"] = distributions(revs)
    out["layers"] = layer_stats(revs)
    out["composition"] = composition(revs, ff_names)
    cc = candidate_counts(revs)
    out["candidates"] = cc
    out["persistence"] = persistence(revs)
    out["score_changes"] = score_changes(revs)
    out["sector_concentration"] = sector_concentration(revs, ff_names)
    out["regime"] = regime_stats(pay)
    out["capacity"] = capacity(cc)
    ev = timeline(revs, weekly)
    out["churn"] = [churn_metrics(revs, weekly, ev, ff_by_sid, th, p, K) for th in THRESHOLDS for p in PROFILES
                    for K in KS]
    out["weekly_burden"] = weekly_burden(revs, weekly)
    out["share_classes"] = share_class_audit(pay, revs)
    txt = json.dumps(out, indent=1, sort_keys=True, default=str)
    for bad in ("return", "cagr", "sharpe", "alpha", "drawdown", "forward"):
        assert bad not in txt.lower(), bad
    (HERE / "P7_CP3_mechanics.json").write_text(txt + "\n")
    (HERE / "P7_CP3_tables.md").write_text(tables(out) + "\n")
    print("ok", len(out["churn"]))


def tables(o):
    L = ["# P7-CP3 tables (generated by P7_CP3_mechanics.py from E993-01; no returns)", ""]
    L += ["## Availability and capacity", "",
          "| Entry | Median candidates | Zero months | Median persistence (months) | Max 6 filled | Max 8 filled | "
          "Max 10 filled | Max 12 filled |", "|---|---|---|---|---|---|---|---|"]
    for th in THRESHOLDS:
        c, p, cap = o["candidates"][th], o["persistence"][th], o["capacity"][th]
        L.append(f"| {th} | {c['stats'].get('p50', 0):g} | {c['zero_months']} / 84 | "
                 f"{p['run_months'].get('p50', 0):g} | " + " | ".join(f"{100 * cap[K]['all_slots']:.0f}%" for K in KS) + " |")
    L += ["", "## Churn and cost (K = 10; $100K)", "",
          "| Entry | Profile | Exit | Buffer | Orders/yr | Median holding (months) | Sell/rebuy (per yr) | Est. cost |",
          "|---|---|---|---|---|---|---|---|"]
    for r in o["churn"]:
        if r["K"] != 10:
            continue
        c = r["costs"]["100000"]
        L.append(f"| {r['entry']} | {r['profile']} {PROFILE_NAMES[r['profile']]} | {r['exit']} | {r['buffer']} | "
                 f"{r['orders_per_year']:.1f} | {r['holding_months_closed'].get('p50', 0):.1f} | "
                 f"{r['sell_then_rebuy_per_year']:.1f} ({r['sell_then_rebuy']}) | {c['total_pct']:.2f}% "
                 f"(${c['total_usd_yr']:,.0f}) |")
    L += ["", "## Full churn grid", "",
          "| Entry | Profile | K | Orders/yr | Entries/yr | Normal exits/yr | DQ exits/yr | Universe exits/yr | "
          "Replacements/yr | Sell/rebuy/yr | Median hold | Mean utilisation | Cost $100K | Cost $200K |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in o["churn"]:
        L.append(f"| {r['entry']} | {r['profile']} | {r['K']} | {r['orders_per_year']:.1f} | {r['entries_per_year']:.1f} | "
                 f"{r['normal_exits_per_year']:.1f} | {r['dq_exits_per_year']:.1f} | {r['universe_exits_per_year']:.1f} | "
                 f"{r['replacements_per_year']:.1f} | {r['sell_then_rebuy_per_year']:.1f} | "
                 f"{r['holding_months_closed'].get('p50', 0):.1f} | {100 * r['utilisation']['mean']:.0f}% | "
                 f"{r['costs']['100000']['total_pct']:.2f}% | {r['costs']['200000']['total_pct']:.2f}% |")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
