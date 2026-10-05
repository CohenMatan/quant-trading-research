# qr_h020_diag.py — H020 real-run descriptive and NON-GATING diagnostics (research/phase5/H020_spec_addendum_1.md).
# Pure numpy, no QuantConnect imports (tests/test_h020_panel.py). Nothing here feeds a gate: the gates are
# qr_h020_stats.promotion on qr_h020_stats.run_world. Descriptives (score distribution, condition / disqualifier
# frequencies, score-baseline relationships) involve no return; the sector diagnostic is the frozen G5 regression with
# point-in-time FF12 industry dummies added, reported separately and labelled NON-GATING.
import numpy as np

import qr_chart as C
import qr_h020_panel as HP
import qr_h020_stats as H
import qr_xs as X


def _years(dates):
    return sorted({d["year"] for d in dates})


def score_distribution(T, dates):
    """Counts of the quality level Q (-1 = disqualified, 0..20) and of groups G0..G4, overall and by year, over the
    evaluation cross-sections (scored, momentum defined). Also per-date group sizes."""
    lv = list(range(-1, 21))
    by_year = {}
    allq = np.zeros(len(lv), np.int64)
    allg = np.zeros(5, np.int64)
    per_date = []
    for d in dates:
        q = np.bincount(np.asarray(d["Q"]) + 1, minlength=22)
        g = np.bincount(np.asarray(d["G"]), minlength=5)
        allq += q
        allg += g
        y = by_year.setdefault(d["year"], dict(Q=np.zeros(22, np.int64), G=np.zeros(5, np.int64), dates=0))
        y["Q"] += q
        y["G"] += g
        y["dates"] += 1
        per_date.append([d["day"]] + [int(x) for x in g])
    n = max(int(allq.sum()), 1)
    return dict(levels=lv, Q_all=allq.tolist(), G_all=allg.tolist(), G_share_all=(allg / n).tolist(),
                by_year={str(y): dict(Q=v["Q"].tolist(), G=v["G"].tolist(), dates=v["dates"],
                                      G_share=(v["G"] / max(int(v["G"].sum()), 1)).tolist())
                         for y, v in sorted(by_year.items())},
                group_sizes_by_date=per_date,
                group_size_min=[int(min(r[1 + g] for r in per_date)) for g in range(5)],
                group_size_median=[float(np.median([r[1 + g] for r in per_date])) for g in range(5)],
                dates_with_empty_group=[int(sum(1 for r in per_date if r[1 + g] == 0)) for g in range(5)])


def condition_frequencies(T, dates):
    """Share of evaluation observations with each condition / disqualifier true, overall and by year; conditions also
    among non-disqualified observations. Descriptive only."""
    rows = {}
    for d in dates:
        k, j = d["k"], d["ids"]
        rows.setdefault(d["year"], []).append((T.bits[k, j], T.dq[k, j]))
    out = dict(conditions=list(C.CONDITIONS), disqualifiers=list(C.DISQUALIFIERS), by_year={})
    tb, td = [], []
    for y in sorted(rows):
        b = np.concatenate([r[0] for r in rows[y]])
        q = np.concatenate([r[1] for r in rows[y]])
        tb.append(b)
        td.append(q)
        cb, cq = HP.unpack(b, 20), HP.unpack(q, 5)
        out["by_year"][str(y)] = dict(n=int(b.size), cond=cb.mean(axis=0).tolist(), dq=cq.mean(axis=0).tolist(),
                                      any_dq=float(cq.any(axis=1).mean()))
    b, q = np.concatenate(tb), np.concatenate(td)
    cb, cq = HP.unpack(b, 20), HP.unpack(q, 5)
    ok = ~cq.any(axis=1)
    out.update(n=int(b.size), cond=cb.mean(axis=0).tolist(), dq=cq.mean(axis=0).tolist(),
               any_dq=float((~ok).mean()), cond_not_dq=cb[ok].mean(axis=0).tolist() if ok.any() else None,
               dq_count_hist=np.bincount(cq.sum(axis=1), minlength=6).tolist())
    return out


def relationships(T, dates):
    """Score vs the baselines and the category counts (per-date Spearman, averaged; plus pooled shares). Descriptive."""
    r_mom, r_tr, r_cat, r_q_raw = [], [], {c: [] for c in "WBTR"}, []
    hi_tr, hi_nt, q_tr, q_nt, n_tr, n_nt = [], [], [], [], 0, 0
    for d in dates:
        k, j = d["k"], d["ids"]
        Q = np.asarray(d["Q"], float)
        if Q.size < 20:
            continue
        r_mom.append(X.spearman(Q, d["mom"]))
        tr = np.asarray(d["trend"], float)
        if 0 < tr.sum() < tr.size:
            r_tr.append(X.spearman(Q, tr))
        raw = T.cat[k, j].sum(axis=1).astype(float)          # the 0..20 score before disqualifiers
        r_q_raw.append(X.spearman(Q, raw))
        for i, c in enumerate("WBTR"):
            r_cat[c].append(X.spearman(raw, T.cat[k, j][:, i].astype(float)))
        t = np.asarray(d["trend"], bool)
        hi = np.isin(d["G"], H.HIGH_GROUPS)
        n_tr += int(t.sum())
        n_nt += int((~t).sum())
        ok = Q >= 0
        if t.any():
            hi_tr.append(float(hi[t].mean()))
            if (t & ok).any():
                q_tr.append(float(Q[t & ok].mean()))
        if (~t).any():
            hi_nt.append(float(hi[~t].mean()))
            if (~t & ok).any():
                q_nt.append(float(Q[~t & ok].mean()))
    m = lambda v: float(np.nanmean(v)) if len(v) else None
    return dict(spearman_Q_mom=m(r_mom), spearman_Q_mom_sd=float(np.std(r_mom)) if r_mom else None,
                spearman_Q_trend=m(r_tr), spearman_Q_rawscore=m(r_q_raw),
                spearman_rawscore_category={c: m(v) for c, v in r_cat.items()},
                share_high_if_trend=m(hi_tr), share_high_if_no_trend=m(hi_nt),
                mean_score_if_trend_not_dq=m(q_tr), mean_score_if_no_trend_not_dq=m(q_nt),
                obs_trend=n_tr, obs_no_trend=n_nt)


def sector_series(T, prep, dates):
    """NON-GATING SECTOR DIAGNOSTIC: per date, the frozen G5 regression (rank(yd) on rank(Q), rank(mom), trend, with
    an intercept) plus point-in-time FF12 industry dummies (SEC SIC at filing; 'Unclassified' is its own group)."""
    sec_of = {}
    for d in dates:
        sec_of[d["k"]] = (d["ids"], [T.sector[d["k"]][int(j)] for j in d["ids"]])
    out = []
    for p, d in zip(prep, [dd for dd in dates if np.isfinite(dd["y"]).sum() >= 20]):
        ids_all, labs_all = sec_of[d["k"]]
        lab = dict(zip(ids_all.tolist(), labs_all))
        labs = [lab[i] for i in p["ids"]]
        names = sorted(set(labs))
        Dm = np.array([[1.0 if s == nm else 0.0 for nm in names] for s in labs])
        Z = np.column_stack([(p["rq"] - 0.5) / p["rq"].size, p["rmom"], p["trend"], Dm])
        b = X.ols_slopes(Z, p["rydm"])
        out.append(float(b[0]))
    return out


def sector_diagnostic(T, prep, dates, years):
    s = np.asarray(sector_series(T, prep, dates))
    m, se, t = X.nw_tstat(s, H.NW_LAG)
    cover = []
    for d in dates:
        labs = [T.sector[d["k"]][int(j)] for j in d["ids"]]
        cover.append(1.0 - labs.count("Unclassified") / max(len(labs), 1))
    return dict(label="NON-GATING SECTOR DIAGNOSTIC", inc_sector_mean=m, inc_sector_se=se, t_inc_sector=t,
                dates=int(s.size), classified_share_mean=float(np.mean(cover)),
                classified_share_min=float(np.min(cover)))
