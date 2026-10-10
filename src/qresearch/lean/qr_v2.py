# qr_v2.py — Data Infrastructure v2 (owner D190) pure layer: no QuantConnect imports, unit-tested offline
# (tests/test_data_v2.py). It holds the APPROVED v2 rules exactly as validated in P7-CP5d / P7-CP5e; nothing here
# changes Score v1 (qr_p7_score, hash-pinned) or the frozen mechanics (qr_p7_mech, hash-pinned).
#   * sec_v1_table: the consolidated table's data-v1 SEC correction layer -> the SECCorrections table format (same
#     filings, same order, same values; accession numbers replaced by their rank, which keeps the D111 sort order);
#   * Reference: the M2 filing reference (EDGAR submissions; original 10-Q / 10-K / 10-KT, amendments only when no
#     original), D111 cover-share rows, identity extension rows, restatement-guard reference, identity check values;
#   * Identity: identity-v2 dated rows + verified extension rows (SAFE / BOUNDED) used only while the security's feed
#     presence has been continuous since the row start;
#   * guard(): the restatement guard (P7-CP5d methodology: a value matching only a later SEC value that was not yet
#     filed on the day it is seen is blocked; quarterly revenue and total assets; tolerance 0.5%);
#   * simulate(): the frozen monthly mechanics (qr_p7_mech.plan + qr_p7_score.weekly_check) on score tables, reporting
#     orders, causes, utilisation and mechanical costs only (no price, no P&L);
#   * power: the P7-CP4 synthetic power study (research/phase7/P7_power.py) ported unchanged in its model, seeds,
#     gates and procedure, run sequentially on Data v2 score tables with SYNTHETIC returns only.
import math
from datetime import date, timedelta

import numpy as np

EPOCH = date(2000, 1, 1)
TOL = 0.005
PE_MATCH = 6
PRESENCE_GAP = 60
GFIELDS = ("revenue_q", "total_assets")


def dd(n):
    return EPOCH + timedelta(days=int(n))


def dn(d):
    return (d - EPOCH).days


def g4(c):
    if c is None:
        return None
    a = abs(int(c))
    return (-1 if c < 0 else 1) * (a // 100) * 10.0 ** (a % 100 - 3)


def near(x, ref):
    return x is not None and ref is not None and ref != 0 and abs(x / ref - 1.0) <= TOL


# ----------------------------------------------------------------------------------------------- SEC layer (data v1)
def sec_v1_table(sv):
    """Consolidated sec_v1 -> qr_sec_corrections.SECCorrections table (status 'repaired' only, as before)."""
    keys, forms = sv["keys"], sv["forms"]

    def iso(n):
        return None if n is None else str(dd(n))
    corr = {}
    for sid, c in sv["corrections"].items():
        rows = []
        for i, (fm, fd, pe, cd, sh, vals) in enumerate(c["rows"]):
            rows.append([f"{i:06d}", forms[fm], iso(fd), iso(pe), iso(cd), sh, {keys[k]: v for k, v in vals}])
        corr[sid] = dict(status="repaired", cik=c["cik"], filings=rows)
    sic = {sid: [[iso(e), s, c] for e, s, c in rows] for sid, rows in sv["sic_history"].items()}
    return dict(corrections=corr, sic_history=sic, timing_holds={}, quarantine_releases={}, restatement_blocks={},
                field_releases={})


# ----------------------------------------------------------------------------------------------- reference
class Reference:
    def __init__(self, t):
        self.forms, self.pes, self.shrows = {}, {}, {}
        for cik, cols in t["f"].items():
            d, pe, sh = {}, 0, []
            for i in range(len(cols[0])):
                pe += cols[0][i]
                fd = pe + cols[1][i]
                code = cols[2][i]
                d.setdefault(pe, []).append((fd, code))
                if cols[4][i]:
                    sh.append([f"{cik}-{i:05d}", "10-K" if code == 2 else "10-Q", str(dd(fd)), str(dd(pe)),
                               str(dd(fd - cols[3][i])), g4(cols[4][i]), {}])
            out = {}
            for pe_, rows in d.items():
                orig = [x for x in rows if x[1] in (1, 2)]
                fd, fm = min(orig or rows)
                out[pe_] = (fd, "Q" if fm in (1, 3) else "K", not orig)
            self.forms[cik], self.pes[cik] = out, sorted(out)
            if sh:
                self.shrows[cik] = sh
        self.ext = {s: (dd(v[0]), str(v[1])) for s, v in t["ext"].items()}
        self.guard_ref = t["guard"]
        self.idv = t["idv"]

    def match(self, cik, pe):
        """(SEC period-end day, original filing day, 'Q'/'K', amendment-only) of the matched period, or None."""
        ps = self.pes.get(cik)
        if not ps:
            return None
        x = dn(pe)
        i = int(np.searchsorted(ps, x))
        best = None
        for j in (i - 1, i):
            if 0 <= j < len(ps) and abs(ps[j] - x) <= PE_MATCH and (best is None or abs(ps[j] - x) < abs(best - x)):
                best = ps[j]
        if best is None:
            return None
        fd, fm, am = self.forms[cik][best]
        return best, fd, fm, am

    def guard(self, cik, sec_pe, vals, today):
        """Restatement guard: (blocked, {field: category}). A field blocks when the value seen today matches the later
        (re-reported) SEC value, does not match the first-filed one, and the later filing was not yet public."""
        row = self.guard_ref.get(cik, {}).get(str(sec_pe))
        cats, blocked = {}, False
        if not row:
            return False, cats
        td = dn(today)
        for i, f in enumerate(GFIELDS):
            first, later, loff = (row + [None] * 6)[3 * i:3 * i + 3]
            v = vals.get(f)
            if later is None or first is None or v is None:
                continue
            fv, lv = g4(first), g4(later)
            lfd = sec_pe + loff
            if near(v, lv) and not near(v, fv):
                if lfd + 1 > td:
                    cats[f] = "later_not_yet_public"
                    blocked = True
                else:
                    cats[f] = "later_public"
        return blocked, cats

    def identity_value(self, cik, sec_pe, vals):
        """{field: 'match' / 'differ' / 'no_ref'} against the SEC first-filed value (identity continuity check)."""
        row = self.idv.get(cik, {}).get(str(sec_pe))
        out = {}
        for i, f in enumerate(GFIELDS):
            ref = g4(row[i]) if row and i < len(row) and row[i] is not None else None
            v = vals.get(f)
            out[f] = "no_ref" if ref is None or v is None else ("match" if near(v, ref) else "differ")
        return out


def old_membership(diag):
    """Data-v1 (E993-02) eligible set per review string, from the per-security hex bitsets (diagnostics only)."""
    revs = diag["reviews"]
    out = {r: set() for r in revs}
    for sid, h in diag["bits"].items():
        b = bin(int(h, 16))[2:].zfill(len(revs))
        for j, r in enumerate(revs):
            if b[j] == "1":
                out[r].add(sid)
    return out


class Identity:
    """Identity-v2 dated rows (sid -> [(effective date, CIK)]) + verified extension rows (sid -> (start, CIK))."""

    def __init__(self, rows, ext):
        self.rows, self.ext = rows, ext

    def v2(self, sid, today):
        out = None
        for eff, c in self.rows.get(sid, ()):
            if eff <= today:
                out = c
            else:
                break
        return out

    def m2(self, sid, today, presence_start, first_day):
        """(CIK, 'v2' / 'ext') for the M2 gate, or (None, None) / (None, 'presence_break')."""
        c = self.v2(sid, today)
        if c is not None:
            return c, "v2"
        e = self.ext.get(sid)
        if e is not None and today >= e[0]:
            if presence_start is not None and presence_start <= max(e[0], first_day):
                return e[1], "ext"
            return None, "presence_break"
        return None, None


# ----------------------------------------------------------------------------------------------- mechanics (no P&L)
DQ_FULL = dict(H1_financial="H1_sector_not_scorable", H1_no_sic="H1_sector_not_scorable",
               H2="H2_fundamentals_missing_or_stale", H3="H3_insufficient_history",
               H4="H4_corporate_event_contamination", H5="H5_stale_price", H6="H6_broken_long_term_trend",
               H7="H7_financial_impairment")
DATA_BITS = ("H1_financial", "H1_no_sic", "H2", "H3", "H4", "H5")
DQ_BITS = DATA_BITS + ("H6", "H7")


def cause_of(reason):
    for p, c in (("left the eligible universe", "universe_exit"), ("hard disqualifier", "dq_review"),
                 ("score", "exit_threshold"), ("regime", "regime_cap"), ("replaced", "replacement")):
        if reason.startswith(p):
            return c
    return "other"


def simulate(reviews, weekly, BIT, eligible_flag, plan, weekly_check, regime_positions, entry=80, exit_=70,
             buffer=5, K=10, capitals=(100_000.0, 200_000.0), commission=7.0, slippage=0.0010):
    """reviews: [dict(t, year, rows={sid: (bits, total, points)}, adv, ff, company, regime)];
    weekly: [dict(t, review_index, bits={sid: bits}, members)] in date order (interleaved by t).
    The frozen P7-CP3R mechanics; returns aggregate order / utilisation / cost statistics and rule checks."""
    ev = sorted([(r["t"], 0, i) for i, r in enumerate(reviews)] + [(w["t"], 1, j) for j, w in enumerate(weekly)])
    hold, out = {}, dict(buys=0, sells={}, utilisation=[], cap_utilisation=[], sector_skips=0, company_skips=0,
                         holding_reviews=[], max_holdings=0, cap_violations=0, sector_violations=0,
                         weekly_dq_exits=0, frozen_kept=0, by_year={})
    for t, kind, i in ev:
        if kind == 0:
            rv = reviews[i]
            rec = {}
            for s, (bits, tot, pts) in rv["rows"].items():
                if bits & BIT["duplicate_class"] and s not in hold:
                    continue
                b = bits & ~BIT["duplicate_class"]
                dq = [DQ_FULL[x] for x in DATA_BITS if b & BIT[x]]
                if tot is None:
                    rec[s] = dict(total=None, eligible=False, dq=list(dict.fromkeys(dq)) or ["no score"])
                    continue
                dq += [DQ_FULL[x] for x in ("H6", "H7") if b & BIT[x]]
                rec[s] = dict(total=tot, fund=sum(pts[3:7]), tech=sum(pts[0:3]), eligible=eligible_flag(b, tot),
                              dq=list(dict.fromkeys(dq)))
            frozen = {h for h in hold if h in rec and "H4_corporate_event_contamination" in rec[h]["dq"]}
            cap = regime_positions.get(rv["regime"], 0) if rv["regime"] else 0
            p = plan(set(hold), rec, rv["adv"], rv["ff"], rv["company"], entry, exit_, buffer, K, cap,
                     frozenset(frozen), set(rv["rows"]))
            out["sector_skips"] += len(p["skipped_sector"])
            out["company_skips"] += len(p["skipped_company"])
            out["frozen_kept"] += len(frozen & set(hold))
            y = out["by_year"].setdefault(rv["year"], dict(buys=0, sells=0, reviews=0, held=0))
            for s in p["sell"]:
                c = cause_of(p["reasons"][s])
                out["sells"][c] = out["sells"].get(c, 0) + 1
                out["holding_reviews"].append(i - hold.pop(s))
                y["sells"] += 1
            for s in p["buy"]:
                hold[s] = i
                out["buys"] += 1
                y["buys"] += 1
            y["reviews"] += 1
            y["held"] += len(hold)
            out["max_holdings"] = max(out["max_holdings"], len(hold))
            out["cap_violations"] += int(len(hold) > max(cap, len(frozen & set(hold))))
            secs = {}
            for h in hold:
                g = rv["ff"].get(h)
                if g is not None:
                    secs[g] = secs.get(g, 0) + 1
            out["sector_violations"] += int(any(v > 3 for v in secs.values()))
            out["utilisation"].append(len(hold) / K)
            out["cap_utilisation"].append(len(hold) / cap if cap else 0.0)
        else:
            w = weekly[i]
            recs = {s: dict(dq=[DQ_FULL[x] for x in DQ_BITS if w["bits"].get(s, 0) & BIT[x]]) for s in w["members"]}
            frozen = {h for h in hold if w["bits"].get(h, 0) & BIT["H4"]}
            exits = weekly_check(set(hold), recs, frozenset(frozen))
            for s in exits:
                out["sells"]["dq_weekly"] = out["sells"].get("dq_weekly", 0) + 1
                out["holding_reviews"].append(w["review_index"] - hold.pop(s))
                out["weekly_dq_exits"] += 1
    n_rev = len(reviews)
    years = n_rev / 12.0
    sells = sum(out["sells"].values())
    orders = out["buys"] + sells
    hr = np.asarray(out["holding_reviews"] or [0], dtype=float)
    res = dict(reviews=n_rev, buys=out["buys"], sells=out["sells"], orders=orders,
               orders_per_year=round(orders / years, 2), buys_per_year=round(out["buys"] / years, 2),
               utilisation_mean=round(float(np.mean(out["utilisation"])), 4),
               cap_utilisation_mean=round(float(np.mean(out["cap_utilisation"])), 4),
               empty_reviews=sum(1 for u in out["utilisation"] if u == 0),
               full_reviews=sum(1 for u in out["utilisation"] if u >= 1.0),
               max_holdings=out["max_holdings"], open_at_end=len(hold), sector_skips=out["sector_skips"],
               company_skips=out["company_skips"], weekly_dq_exits=out["weekly_dq_exits"],
               frozen_holding_reviews=out["frozen_kept"],
               holding_reviews=dict(mean=round(float(hr.mean()), 3), median=float(np.median(hr)),
                                    p75=float(np.percentile(hr, 75)), max=float(hr.max())),
               rule_checks=dict(cap_violations=out["cap_violations"], sector_violations=out["sector_violations"],
                                max_holdings_le_K=out["max_holdings"] <= K),
               by_year={str(y): dict(v, mean_held=round(v["held"] / v["reviews"], 2)) for y, v in out["by_year"].items()})
    res["costs"] = {str(int(c)): dict(commission_usd_yr=round(orders * commission / years, 2),
                                      slippage_usd_yr=round(orders * 0.10 * c * slippage / years, 2),
                                      total_pct_yr=round(100 * orders * (commission + 0.10 * c * slippage) / years / c,
                                                         4))
                    for c in capitals}
    return res


# ----------------------------------------------------------------------------------------------- synthetic power
SEED_BASE = 20261006
KAPPAS = (0.0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.008, 0.010)
N_DATASETS = 200
NULL_DATASETS, NULL_WORLDS = 10, 200
HOLDOUT_DATASETS, HOLDOUT_WORLDS = 5, 200
SIGMA_BY_RISK = {10: 0.045, 7: 0.055, 3: 0.065, 0: 0.085}
SCENARIOS = dict(main=0.0055, optimistic=0.0, pessimistic=0.009)


def _erfinv(x):
    a = 0.147
    ln = math.log(1.0 - x * x)
    t1 = 2.0 / (math.pi * a) + ln / 2.0
    return math.copysign(math.sqrt(math.sqrt(t1 * t1 - ln / a) - t1), x)


def _normal_score(R, S):
    r = R.rank01(S)
    return np.array([math.sqrt(2.0) * _erfinv(2.0 * x - 1.0) for x in r])


def synth(R, tables, kappa, seed, style_sd):
    """research/phase7/P7_power.synth, unchanged (SYNTHETIC returns on the real score cross-sections)."""
    rng = np.random.default_rng(seed)
    beta = {}
    dates = []
    for d in tables:
        n = d["ids"].size
        mkt = rng.normal(0.008, 0.035)
        fac = rng.normal(0.0, 0.025, 16)
        b = np.array([beta.setdefault(s, 1.0 + 0.25 * rng.normal()) for s in d["ids"]])
        sig = np.array([SIGMA_BY_RISK.get(int(k), 0.085) for k in d["risk"]])
        e = rng.standard_t(5, n) / math.sqrt(5.0 / 3.0)
        mom = d["mom_pts"] + rng.random(n)
        style = sum(rng.normal(0.0, style_sd) * _normal_score(R, x) for x in (mom, d["risk"] + rng.random(n),
                                                                               d["fund"] + rng.random(n)))
        y = b * mkt + fac[d["sector"] % 16] + style + sig * e + kappa * _normal_score(R, d["S"])
        dates.append(dict(ids=d["ids"], S=d["S"], sector=d["sector"], mom=mom,
                          size=d["size"], y=y, year=d["year"], regime=d["regime"]))
    return dates


def power_scenario(R, tables, style_sd):
    """research/phase7/P7_power.scenario, sequential (same seeds, worlds, datasets and outputs)."""
    cal = []
    for k in range(NULL_DATASETS):
        prep = R.prepare(synth(R, tables, 0.0, SEED_BASE + 1000 + k, style_sd))
        cal += [R.run_world(prep, seed=s) for s in range(1 + 200 * k, 201 + 200 * k)]
    c_ic = R.critical_value(cal)
    hold = []
    for k in range(HOLDOUT_DATASETS):
        prep = R.prepare(synth(R, tables, 0.0, SEED_BASE + 2000 + k, style_sd))
        hold += [R.run_world(prep, seed=s) for s in range(100001 + 200 * k, 100201 + 200 * k)]
    res = {}
    for kappa in KAPPAS:
        res[kappa] = [R.run_world(R.prepare(synth(R, tables, kappa, SEED_BASE + 10_000 * (1 + KAPPAS.index(kappa)) + j,
                                                  style_sd))) for j in range(N_DATASETS)]
    n_stocks = [d["ids"].size for d in tables]
    out = dict(style_sd=style_sd, n_dates=len(tables),
               stocks_per_date=dict(min=min(n_stocks), median=float(np.median(n_stocks)), max=max(n_stocks)),
               c_ic_synthetic=c_ic, calibration_worlds=len(cal), holdout_worlds=len(hold),
               null_t_ic=dict(mean=float(np.mean([w["t_ic"] for w in cal])), sd=float(np.std([w["t_ic"] for w in cal])),
                              p95=float(np.percentile([w["t_ic"] for w in cal], 95)),
                              p99=float(np.percentile([w["t_ic"] for w in cal], 99))),
               holdout_false_promotion_full=R.false_promotion(hold, c_ic),
               holdout_false_g1=float(np.mean([w["t_ic"] > c_ic for w in hold])),
               holdout_gate_pass_rates={g: float(np.mean([R.promotion(w, c_ic)[g] for w in hold]))
                                        for g in ("G1_significant", "G2_economic", "G3_monotonic", "G4_stable")},
               by_kappa={})
    for kappa, ws in res.items():
        gs = [R.promotion(w, c_ic) for w in ws]
        out["by_kappa"][str(kappa)] = dict(
            kappa_bp_per_month=kappa * 1e4, datasets=len(ws),
            ic_mean=float(np.mean([w["ic_mean"] for w in ws])),
            ic_month_sd=float(np.mean([w["ic_se"] for w in ws]) * math.sqrt(len(tables))),
            t_ic_mean=float(np.mean([w["t_ic"] for w in ws])),
            hi_ann_mean=float(np.mean([w["hi_ann"] for w in ws])), hi_ann_sd=float(np.std([w["hi_ann"] for w in ws])),
            q5_minus_q1_ann_mean=float(np.mean([w["q5_minus_q1_ann"] for w in ws])),
            hi_n_mean=float(np.mean([w["hi_n_mean"] for w in ws])),
            pass_rates={g: float(np.mean([x[g] for x in gs])) for g in gs[0]})
    ks = list(KAPPAS)
    pf = [out["by_kappa"][str(k)]["pass_rates"]["pass"] for k in ks]
    pg = [out["by_kappa"][str(k)]["pass_rates"]["G1_significant"] for k in ks]

    def mde(p, target):
        for (k0, a), (k1, b) in zip(zip(ks, p), zip(ks[1:], p[1:])):
            if a < target <= b:
                return k0 + (target - a) * (k1 - k0) / (b - a)
        return None

    def at(field, kappa):
        if kappa is None:
            return None
        lo = max(k for k in ks if k <= kappa)
        hi_ = min(k for k in ks if k >= kappa)
        a, b = out["by_kappa"][str(lo)][field], out["by_kappa"][str(hi_)][field]
        return a if hi_ == lo else a + (kappa - lo) * (b - a) / (hi_ - lo)
    for name, p in (("full_procedure", pf), ("significance_gate_only", pg)):
        d = {}
        for target in (0.5, 0.8):
            k = mde(p, target)
            d[f"mde{int(target * 100)}"] = dict(kappa_bp_per_month=None if k is None else k * 1e4,
                                                ic=at("ic_mean", k), hi_ann_80plus_excess=at("hi_ann_mean", k),
                                                q5_minus_q1_ann=at("q5_minus_q1_ann_mean", k))
        out[name] = d
    out["null_ic_month_sd"] = out["by_kappa"]["0.0"]["ic_month_sd"]
    return out
