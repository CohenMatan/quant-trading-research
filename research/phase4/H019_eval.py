"""H019 evaluation (research/phase4/P4_xs_spec.md v2; owner authorisation 2026-10-04, D145).

  python research/phase4/H019_eval.py canary   -> H019_canary_report.json   (E985-01 plumbing / fidelity checks)
  python research/phase4/H019_eval.py null     -> H019_null_result.json + H019_null_worlds.csv (E020-01..05):
                                                  the family null distribution, c = the 50th largest of 5,000 F,
                                                  empirical calibration. Committed and pinned BEFORE E020-06.
  python research/phase4/H019_eval.py real     -> H019_real_result.json (E020-06, judged with the PINNED c)

Every number comes from the published aggregates of the QuantConnect runs (experiments/<id>/result.json); no price
data is stored. The real evaluation refuses to run unless c, the null-result hash and the spec hash match the pins
in qresearch.p4xs.
"""
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
import qr_xs as X  # noqa: E402
from qresearch import p4xs  # noqa: E402

HERE = Path(__file__).resolve().parent
CANARY_RUN = "E985-05"
NULL_RUNS = ("E020-01", "E020-02", "E020-03", "E020-04", "E020-05")
REAL_RUN = "E020-06"
NULL_OUT = HERE / "H019_null_result.json"
NULL_TABLE = HERE / "H019_null_worlds.csv"
REAL_OUT = HERE / "H019_real_result.json"
CANARY_OUT = HERE / "H019_canary_report.json"
STATS = ("t_S1", "t_S2", "t_S3", "t_inc_S2", "t_inc_S3")


def result(exp):
    return json.loads((ROOT / "experiments" / exp / "result.json").read_text())


def lines(exp):
    q = result(exp)["qc_statistics"]
    return "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"]))).split("\n")


def tagged(exp, tag):
    return [ln[len(tag) + 1:] for ln in lines(exp) if ln.startswith(tag + "|")]


def host_summary(exp):
    return json.loads(tagged(exp, "QRX985|summary")[0])


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------------------------- canary
def run_canary():
    ck = json.loads(tagged(CANARY_RUN, "K")[0])
    hs = host_summary(CANARY_RUN)
    pn = hs["panel"]
    months = [f"{y}-{m:02d}" for y in range(2010, 2018) for m in range(1, 13)]
    checks = [
        ("calendar ends on 2017-12-29; no history row after it", pn["last_day"] == "2017-12-29" and pn["late_rows"] == 0),
        ("every research month 2010-01..2017-12 has a month-end universe", pn["research_months_recorded"] == months),
        ("month-end universe dated on the month's last session", pn["month_end_date_mismatches"] == []),
        ("83 decisions 2011-01-31 .. 2017-11-30", ck["decisions"] == 83 and
         ck["decision_dates_first_last"] == ["2011-01-31", "2017-11-30"]),
        ("primary response of the last decision ends 2017-12-29", pn["fwd_end_last_decision"] == "2017-12-29"),
        ("3-month diagnostic response ends 2017-12-29", pn["fwd3_end_last_diag"] == "2017-12-29"),
        ("independent PRET / ID / A_L recomputation identical", ck["slow_features"]["nan_mismatch"] == 0 and
         max(ck["slow_features"]["pret"], ck["slow_features"]["idm"], ck["slow_features"]["A"]) < 1e-9),
        ("S2 two-stage structure: 0 violations; ID in [-1, 1]", ck["s2_structure_violations"] == 0 and ck["id_range_ok"]),
        ("trend-factor regressions estimated for s = 2010-01 .. 2017-10 (the last decision, 2017-11, averages "
         "s = 2016-11 .. 2017-10)", ck["regression_months_first_last"] == ["2010-01", "2017-10"]),
        ("truncation invariance: identical signals and coefficients", ck["truncation"]["max_abs"] == 0 and
         ck["truncation"]["betas_max_abs"] == 0 and ck["truncation"]["id_mismatch"] == 0 and
         ck["truncation"]["dates"] == ck["truncation"]["dates_full"]),
        ("planted response recovered (IC = 1 at every date, h = 1 and 3)", ck["planted"]["h1"]["ic_min"] > 0.999 and
         ck["planted"]["h3"]["ic_min"] > 0.999 and ck["planted"]["h1"]["dates"] == 83 and
         ck["planted"]["h3"]["dates"] == 81),
        ("placebo features: |t| < 3.5 for every statistic", all(abs(v["t"]) < 3.5 and
                                                                (v["t_inc"] is None or abs(v["t_inc"]) < 3.5)
                                                                for v in ck["placebo"].values())),
        ("null world deterministic (same seed twice)", ck["null_repeat_identical"] is True),
        ("prices from RAW x QuantConnect's split and dividend feeds agree with QuantConnect's SCALED_RAW factors "
         "(no large disagreement; small steps <= 2% of dividend events; split-feed / price-factor mismatches listed)",
         pn["factor_steps_big"] == 0 and pn["factor_steps_small"] <= 0.02 * pn["dividend_events"]),
    ]
    out = dict(run=CANARY_RUN, passed=all(ok for _, ok in checks),
               checks=[dict(check=c, ok=bool(ok)) for c, ok in checks],
               numeric=dict(regressions=ck["regressions"], s3_slow_max_abs=ck["s3_slow_max_abs"],
                            s3_slow_rank_deficient_months=ck["s3_slow_rank_deficient_months"],
                            placebo=ck["placebo"], placebo_F=ck["placebo_F"], planted=ck["planted"],
                            null_world_s=ck["null_world_s"], null_world_s_1000=ck["null_world_s_1000"],
                            eval_min_max=ck["eval_min_max"], slow_features=ck["slow_features"],
                            truncation=ck["truncation"]),
               panel=pn, universe=hs["universe"], coverage=hs["coverage"], wall_s=hs["wall_s"],
               max_rss_mb=hs["max_rss_mb"], provenance=result(CANARY_RUN)["provenance"])
    CANARY_OUT.write_text(json.dumps(out, indent=1) + "\n")
    for c in out["checks"]:
        print(("PASS " if c["ok"] else "FAIL ") + c["check"])
    print("canary", "PASSED" if out["passed"] else "FAILED")
    return out


# ---------------------------------------------------------------------------------------------- null
def world_stats(w):
    return dict(t_S1=w["S1"]["t"], t_S2=w["S2"]["t"], t_S3=w["S3"]["t"], t_inc_S2=w["S2"]["t_inc"],
                t_inc_S3=w["S3"]["t_inc"])


def as_summary(w):
    """The promotion inputs of one published world, in qr_xs.summarise form."""
    s = {}
    for k in X.SIGNALS:
        v = w[k]
        s[k] = dict(t=v["t"], top_ann=v["top"], spread_ann=v["spr"], mono=v["mono"], q_gap=v["gap"], sub=v["sub"],
                    block_max=(math.inf if v["blk"] is None else v["blk"]))
        if k in X.INCREMENTAL:
            s[k]["t_inc"] = v["t_inc"]
    return s


def null_worlds():
    ws, digests, prov = {}, {}, {}
    for e in NULL_RUNS:
        hs = host_summary(e)
        digests[e] = hs["panel"]["features_sha256"]
        prov[e] = dict(result(e)["provenance"], seeds=hs["null"]["seeds"], world_s=hs["null"]["world_s"])
        for ln in tagged(e, "N"):
            seed, js = ln.split("|", 1)
            if int(seed) in ws:
                raise SystemExit(f"duplicate null seed {seed}")
            ws[int(seed)] = dict(json.loads(js), run=e)
    return ws, digests, prov


def run_null():
    ws, digests, prov = null_worlds()
    missing = sorted(set(p4xs.NULL_SEEDS) - set(ws))
    if missing or len(ws) != len(p4xs.NULL_SEEDS):
        raise SystemExit(f"incomplete null: {len(ws)} worlds, missing {missing[:10]}...; do not evaluate")
    if len(set(digests.values())) != 1:
        raise SystemExit(f"null runs saw different inputs: {digests}")
    seeds = sorted(ws)
    F = np.array([ws[s]["F"] for s in seeds], float)
    c = X.critical_value(F, X.ALPHA)
    st = {k: np.array([world_stats(ws[s])[k] for s in seeds], float) for k in STATS}
    prom = [X.promotion(as_summary(ws[s]), c) for s in seeds]
    k = int(math.ceil(X.ALPHA * len(F)))
    out = dict(
        hypothesis="H019", spec=p4xs.SPEC, spec_sha256=p4xs.spec_hash(), spec_version=p4xs.SPEC_VERSION,
        null_method="stratified identity-tethered within-date permutation of joint feature vectors (PRET, ID, A_3..A_1000); "
                    "full re-estimation of the trend-factor regressions and the S2 two-stage sort in every world (spec v2 s.6)",
        runs=list(NULL_RUNS), seeds=[seeds[0], seeds[-1]], worlds=len(seeds), failed_worlds=0,
        retried_runs=[], features_sha256=digests[NULL_RUNS[0]],
        alpha=X.ALPHA, rank_k=k, c=c, family_stat="F = max(t_S1, t_S2, t_S3, t_inc_S2, t_inc_S3)",
        F_quantiles={q: float(np.percentile(F, q)) for q in (1, 5, 10, 25, 50, 75, 90, 95, 97.5, 99, 99.5, 99.9)},
        F_max=float(F.max()), F_mean=float(F.mean()), F_sd=float(F.std(ddof=1)),
        stat_quantiles={k2: {q: float(np.percentile(v, q)) for q in (1, 50, 99)} for k2, v in st.items()},
        stat_sd={k2: float(v.std(ddof=1)) for k2, v in st.items()},
        calibration=dict(
            F_above_c=float(np.mean(F > c)),
            any_stat_above_c=float(np.mean([max(world_stats(ws[s]).values()) > c for s in seeds])),
            per_stat_above_c={k2: float(np.mean(v > c)) for k2, v in st.items()},
            full_rule_candidate=float(np.mean([p["outcome"] == "candidate" for p in prom])),
            full_rule_S1_pass=float(np.mean([p["S1"]["pass"] for p in prom])),
            full_rule_S2_pass=float(np.mean([p["S2"]["pass"] for p in prom])),
            full_rule_S3_pass=float(np.mean([p["S3"]["pass"] for p in prom])),
            any_signal_pass=float(np.mean([any(p[s]["pass"] for s in X.SIGNALS) for p in prom])),
            economic_floor_pass_S1_S2_S3=[float(np.mean([p[s]["P1_economic"] for p in prom])) for s in X.SIGNALS],
            binomial_se_at_1pct=math.sqrt(0.01 * 0.99 / len(F))),
        run_provenance=prov)
    with open(NULL_TABLE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seed", "run", "F"] + list(STATS))
        for s in seeds:
            w.writerow([s, ws[s]["run"], repr(ws[s]["F"])] + [repr(world_stats(ws[s])[k2]) for k2 in STATS])
    out["null_worlds_csv_sha256"] = sha256(NULL_TABLE)
    NULL_OUT.write_text(json.dumps(out, indent=1) + "\n")
    print("c =", c, "| F > c:", out["calibration"]["F_above_c"], "| full-rule candidate:",
          out["calibration"]["full_rule_candidate"], "| null result sha256:", sha256(NULL_OUT))
    return out


# ---------------------------------------------------------------------------------------------- real
def run_real():
    if p4xs.THRESHOLD_C is None:
        raise SystemExit("the threshold is not pinned: the real evaluation cannot be judged")
    if sha256(NULL_OUT) != p4xs.NULL_RESULT_SHA256 or p4xs.spec_hash() != p4xs.SPEC_SHA256:
        raise SystemExit("null result or spec does not match the pins")
    nul = json.loads(NULL_OUT.read_text())
    if nul["c"] != p4xs.THRESHOLD_C:
        raise SystemExit("pinned c differs from the null result")
    res = result(REAL_RUN)
    hs = host_summary(REAL_RUN)
    pv = hs["provenance"]
    if (pv["threshold_c"] != p4xs.THRESHOLD_C or pv["null_result_sha256"] != p4xs.NULL_RESULT_SHA256
            or pv["spec_sha256"] != p4xs.SPEC_SHA256 or pv["threshold_commit"] != p4xs.THRESHOLD_COMMIT):
        raise SystemExit("the real run did not start from the pinned state")
    if hs["panel"]["features_sha256"] != nul["features_sha256"]:
        raise SystemExit("the real run saw different inputs than the null runs")
    c = p4xs.THRESHOLD_C
    sm = json.loads(tagged(REAL_RUN, "R")[0])
    prom = X.promotion(sm, c)
    F_null = np.array([float(r["F"]) for r in csv.DictReader(open(NULL_TABLE))])
    R = F_null.size

    def pval(t):
        return dict(p_family=float((1 + (F_null >= t).sum()) / (R + 1)),
                    percentile_in_family_null=float(100.0 * (F_null < t).mean()))

    per = {}
    for s in X.SIGNALS:
        r = sm[s]
        d = dict(ic_mean=r["ic_mean"], ic_se=r["ic_se"], t=r["t"], top_ann=r["top_ann"],
                 bottom_ann=r["dec_mean"][0] * 12.0, spread_ann=r["spread_ann"],
                 dec_ann=[v * 12.0 for v in r["dec_mean"]], q_ann=[v * 12.0 for v in r["q_mean"]],
                 mono=r["mono"], q_gap_ann=r["q_gap"] * 12.0, halves=r["sub"], block_max=r["block_max"],
                 years=r["years"], **pval(r["t"]), criteria=prom[s])
        if s in X.INCREMENTAL:
            d.update(inc_mean=r["inc_mean"], inc_se=r["inc_se"], t_inc=r["t_inc"], inc_q_mean=r["inc_q_mean"],
                     incremental=pval(r["t_inc"]))
        per[s] = d
    out = dict(hypothesis="H019", run=REAL_RUN, c=c, threshold_commit=p4xs.THRESHOLD_COMMIT,
               null_result_sha256=p4xs.NULL_RESULT_SHA256, spec_sha256=p4xs.SPEC_SHA256, R=R,
               family_F=X.family_stat(sm), family=pval(X.family_stat(sm)), signals=per,
               outcome=prom["outcome"], selected=prom["selected"],
               diagnostics=json.loads(tagged(REAL_RUN, "RD")[0]),
               diagnostic_3m_NON_GATING=json.loads(tagged(REAL_RUN, "R3")[0]),
               universe=hs["universe"], coverage=hs["coverage"], panel=hs["panel"],
               provenance=res["provenance"], host_provenance=pv)
    REAL_OUT.write_text(json.dumps(out, indent=1) + "\n")
    print("outcome", out["outcome"], "| F", out["family_F"], "c", c)
    for s in X.SIGNALS:
        print(s, {k: v for k, v in prom[s].items()})
    return out


if __name__ == "__main__":
    {"canary": run_canary, "null": run_null, "real": run_real}[sys.argv[1]]()
