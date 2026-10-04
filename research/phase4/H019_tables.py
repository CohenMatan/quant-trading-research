"""H019 report tables (reporting only; generated after the real evaluation) (markdown) from research/phase4/H019_real_result.json and H019_null_result.json.
python research/phase4/H019_tables.py > research/phase4/H019_tables.md"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = json.loads((HERE / "H019_real_result.json").read_text())
N = json.loads((HERE / "H019_null_result.json").read_text())
SIG = ("S1", "S2", "S3")
NAME = {"S1": "S1 plain 12-1 momentum (reference)", "S2": "S2 smooth momentum (frog-in-the-pan ID)",
        "S3": "S3 Han-Zhou-Zhu trend factor"}


def pct(x, d=2):
    return "n/a" if x is None else f"{100 * x:+.{d}f}%"


def f(x, d=3):
    return "n/a" if x is None else f"{x:.{d}f}"


def yes(b):
    return "PASS" if b else "FAIL"


def out(s=""):
    sys.stdout.write(s + "\n")


def main():
    c = R["c"]
    out(f"Pinned family threshold c = {f(c, 4)} (R = {R['R']}); real family statistic F = {f(R['family_F'], 3)}, "
        f"family p = {f(R['family']['p_family'], 4)}.")
    out()
    out("| Signal | Top decile (ann.) | Bottom decile (ann.) | Top − bottom (ann.) | Mean rank IC | IC t (NW 2) | "
        "Family-null percentile | Empirical p (family) | p vs own null (reporting) | Monotonicity ρ (Q5−Q1 ann.) | Halves IC | Max block share |")
    out("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in SIG:
        r = R["signals"][s]
        out(f"| {s} | {pct(r['top_ann'])} | {pct(r['bottom_ann'])} | {pct(r['spread_ann'])} | {f(r['ic_mean'], 4)} | "
            f"{f(r['t'], 2)} | {f(r['percentile_in_family_null'], 1)} | {f(r['p_family'], 4)} | {f(r['p_marginal'], 4)} | "
            f"{f(r['mono'], 2)} ({pct(r['q_gap_ann'])}) | {f(r['halves'][0], 4)} / {f(r['halves'][1], 4)} | "
            f"{f(r['block_max'], 2)} |")
    out()
    out("| Signal | P1 economic | P2 monotonic | P3 statistical (t > c) | P4 stable | P6 incremental (t_inc > c) | "
        "Overall |")
    out("|---|---|---|---|---|---|---|")
    for s in SIG:
        k = R["signals"][s]["criteria"]
        out(f"| {s} | {yes(k['P1_economic'])} | {yes(k['P2_monotonic'])} | {yes(k['P3_statistical'])} | "
            f"{yes(k['P4_stable'])} | {yes(k['P6_incremental']) if 'P6_incremental' in k else '—'} | "
            f"**{yes(k['pass'])}** |")
    out()
    out(f"Outcome: **{R['outcome']}**; selected: {R['selected']}")
    out()
    out("| Incremental test | Mean within-S1-quintile partial IC | t (NW 2) | Family p | p vs own null | Pass (t_inc > c) | "
        "Partial IC per S1 quintile (Q1 … Q5) |")
    out("|---|---|---|---|---|---|---|")
    for s in ("S2", "S3"):
        r = R["signals"][s]
        out(f"| {s} over S1 | {f(r['inc_mean'], 4)} | {f(r['t_inc'], 2)} | {f(r['incremental']['p_family'], 4)} | "
            f"{f(r['incremental']['p_marginal'], 4)} | "
            f"{yes(r['criteria']['P6_incremental'])} | {' / '.join(f(v, 4) for v in r['inc_q_mean'])} |")
    out()
    out("Decile means of the demeaned next-month return, annualised (D1 = lowest signal … D10 = highest):")
    out()
    out("| Signal | " + " | ".join(f"D{i}" for i in range(1, 11)) + " |")
    out("|---|" + "---|" * 10)
    for s in SIG:
        out(f"| {s} | " + " | ".join(pct(v, 1) for v in R["signals"][s]["dec_ann"]) + " |")
    out()
    out("| Signal | " + " | ".join(f"Q{i}" for i in range(1, 6)) + " |")
    out("|---|" + "---|" * 5)
    for s in SIG:
        out(f"| {s} | " + " | ".join(pct(v, 1) for v in R["signals"][s]["q_ann"]) + " |")
    out()
    D = R["diagnostics"]
    out("Calendar sub-periods (reporting; the gate P4 uses the frozen halves and blocks):")
    out()
    out("| Signal | 2011–2013 IC (t) | 2011–2013 top / spread (ann.) | 2014–2017 IC (t) | 2014–2017 top / spread (ann.) |")
    out("|---|---|---|---|---|")
    for s in SIG:
        a, b = D["calendar_subperiods"][s]["2011_2013"], D["calendar_subperiods"][s]["2014_2017"]
        out(f"| {s} | {f(a['mean'], 4)} ({f(a['t'], 2)}) | {pct(a['top_ann'])} / {pct(a['spread_ann'])} | "
            f"{f(b['mean'], 4)} ({f(b['t'], 2)}) | {pct(b['top_ann'])} / {pct(b['spread_ann'])} |")
    for s in ("S2", "S3"):
        a, b = D["calendar_subperiods"][s]["2011_2013"]["inc"], D["calendar_subperiods"][s]["2014_2017"]["inc"]
        out(f"| {s} incremental | {f(a['mean'], 4)} ({f(a['t'], 2)}) | | {f(b['mean'], 4)} ({f(b['t'], 2)}) | |")
    out()
    out("Per-year mean IC (t), top decile annualised:")
    out()
    yrs = sorted(D["per_year"]["S1"], key=int)
    out("| Signal | " + " | ".join(yrs) + " |")
    out("|---|" + "---|" * len(yrs))
    for s in SIG:
        out(f"| {s} | " + " | ".join(f"{f(D['per_year'][s][y]['ic'], 3)} ({f(D['per_year'][s][y]['t'], 1)}); "
                                     f"{pct(D['per_year'][s][y]['top_ann'], 1)}" for y in yrs) + " |")
    out()
    out("| Diagnostic | S1 | S2 | S3 |")
    out("|---|---|---|---|")
    out("| Sector-neutral IC (t) | " + " | ".join(f"{f(D['sector_neutral_ic'][s]['mean'], 4)} "
                                                  f"({f(D['sector_neutral_ic'][s]['t'], 2)})" for s in SIG) + " |")
    for h in ("small", "large"):
        out(f"| IC, {h}-cap half (t) | " + " | ".join(f"{f(D['size_half_ic'][s][h]['mean'], 4)} "
                                                     f"({f(D['size_half_ic'][s][h]['t'], 2)})" for s in SIG) + " |")
    out("| Correlation with log market cap | " + " | ".join(f(D["corr_log_mcap"][s], 3) for s in SIG) + " |")
    out("| Correlation with trailing 1-month return | " + " | ".join(f(D["signal_corr"][s + "_r1m"], 3)
                                                                       for s in SIG) + " |")
    out("| Rank autocorrelation month to month | " + " | ".join(f(D["turnover"][s]["rank_autocorr"], 3)
                                                                  for s in SIG) + " |")
    out("| Top-decile retention | " + " | ".join(f(D["turnover"][s]["top_decile_retention"], 3) for s in SIG) + " |")
    out("| Top-quintile retention | " + " | ".join(f(D["turnover"][s]["top_quintile_retention"], 3) for s in SIG) +
        " |")
    out("| IC sd / effective sample | " + " | ".join(f"{f(D['realised_power'][s]['ic_sd'], 4)} / "
                                                     f"{f(D['realised_power'][s]['ess'], 1)}" for s in SIG) + " |")
    out("| IC detectable at c (c × NW se) | " + " | ".join(f(c * D["realised_power"][s]["ic_se_nw"], 4) for s in SIG) +
        " |")
    out()
    sc = D["signal_corr"]
    out(f"Mean cross-sectional rank correlations: S1–S2 {f(sc['S1_S2'], 3)}, S1–S3 {f(sc['S1_S3'], 3)}, "
        f"S2–S3 {f(sc['S2_S3'], 3)}.")
    out()
    out("Trend-factor horizon decomposition (EXPLANATORY ONLY):")
    out()
    out("| Component | IC (t) | Incremental over S1 (t) |")
    out("|---|---|---|")
    for g, v in D["tf_decomposition"].items():
        out(f"| {g} | {f(v['ic']['mean'], 4)} ({f(v['ic']['t'], 2)}) | {f(v['incremental']['mean'], 4)} "
            f"({f(v['incremental']['t'], 2)}) |")
    out()
    T3 = R["diagnostic_3m_NON_GATING"]
    out("NON-GATING DIAGNOSTIC — 3-month horizon (81 decisions, NW lag 6; computed after the primary):")
    out()
    out("| Signal | IC | t | Top decile (ann.) | Top − bottom (ann.) | t_inc |")
    out("|---|---|---|---|---|---|")
    for s in SIG:
        r = T3[s]
        out(f"| {s} | {f(r['ic_mean'], 4)} | {f(r['t'], 2)} | {pct(r['top_ann'])} | {pct(r['spread_ann'])} | "
            f"{f(r.get('t_inc'), 2) if s != 'S1' else '—'} |")
    out()
    out("Null calibration:")
    cal = N["calibration"]
    out(f"F quantiles: " + ", ".join(f"p{k} {f(v, 3)}" for k, v in N["F_quantiles"].items()))
    out(f"F > c {cal['F_above_c']:.4f}; full-rule candidate {cal['full_rule_candidate']:.4f}; "
        f"S1 pass {cal['full_rule_S1_pass']:.4f}; any signal pass {cal['any_signal_pass']:.4f}")


if __name__ == "__main__":
    main()
