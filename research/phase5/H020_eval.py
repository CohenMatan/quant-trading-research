"""H020 evaluation (research/phase5/H020_spec.md v1 + addendum 1; owner authorisation 2026-10-05, D154).

  python research/phase5/H020_eval.py canary   -> H020_canary_report.json   (E987-01 plumbing / fidelity checks)
  python research/phase5/H020_eval.py null     -> H020_null_result.json + H020_null_worlds.csv (E021-01..05): the null
                                                  distributions, c_ic / c_inc = the 50th largest of 5,000 each, the
                                                  full-procedure false-promotion rate. Committed and pinned BEFORE E021-06.
  python research/phase5/H020_eval.py real     -> H020_real_result.json (E021-06, judged with the PINNED c_ic / c_inc)

Every number comes from the published aggregates of the QuantConnect runs (experiments/<id>/result.json); no price
data is stored. The real evaluation refuses to run unless the pins in qresearch.p5h020 match the run's config.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
import qr_h020_stats as HS  # noqa: E402
import qr_xs as X  # noqa: E402
from qresearch import p5h020  # noqa: E402

HERE = Path(__file__).resolve().parent
CANARY_RUN = "E987-01"
NULL_RUNS = ("E021-01", "E021-02", "E021-03", "E021-04", "E021-05")
REAL_RUN = "E021-06"
CANARY_OUT = HERE / "H020_canary_report.json"
NULL_OUT = HERE / "H020_null_result.json"
NULL_TABLE = HERE / "H020_null_worlds.csv"
REAL_OUT = HERE / "H020_real_result.json"


def result(exp):
    """The run's result; if the original failed and was recovered (D077, run.py --recover), the latest completed
    recovery of the same QuantConnect backtest."""
    d = ROOT / "experiments" / exp
    r = json.loads((d / "result.json").read_text())
    if r.get("status") == "completed":
        return r
    for rp in sorted((d / "recovery").glob("*/result.json"), reverse=True):
        rr = json.loads(rp.read_text())
        if rr.get("status") == "completed" and rr["provenance"].get("qc_backtest_id") == r["provenance"].get(
                "qc_backtest_id"):
            return rr
    raise SystemExit(f"{exp}: no completed result (status {r.get('status')})")


def lines(exp):
    q = result(exp)["qc_statistics"]
    return "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"]))).split("\n")


def tagged(exp, tag):
    return [ln[len(tag) + 1:] for ln in lines(exp) if ln.startswith(tag + "|")]


def host_summary(exp):
    return json.loads(tagged(exp, "QRX987|summary")[0])


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------------------------- canary
def canary_checks(ck, hs):
    pn = hs["panel"]
    sl, rs, acc = ck["slow_recomputation"], ck["slow_response"], ck["response_accounting"]
    sec = ck["sector_classified_share_by_year"]
    return [
        ("calendar ends on 2017-12-29; no history row after it", pn["last_day"] == "2017-12-29" and pn["late_rows"] == 0),
        ("every research week-end 2010-01-08 .. 2017-12-29 has its recorded PIT universe (none missing, none extra)",
         pn["week_end_universe_missing"] == [] and pn["week_end_universe_extra"] == [] and
         pn["week_ends_recorded"] == pn["week_ends_in_calendar"]),
        ("decisions are the last session of each ISO week; first 2010-01-08; last decision maximal",
         ck["decisions_are_week_ends"] and ck["first_decision_is_first_week_end_2010"] and ck["last_decision_is_maximal"]),
        ("4-week response of the last decision ends on or before 2017-12-29", pn["fwd_end_last_decision"] <= "2017-12-29"),
        ("13-week response of the last diagnostic decision ends on or before 2017-12-29",
         pn["fwd13_end_last_decision"] <= "2017-12-29"),
        ("history requirement: every scored stock has >= 504 own bars", ck["min_bars_scored"] >= 504),
        ("score-table coverage: no snapshot error; every eligible stock with a bar and >= 504 bars is scored",
         ck["coverage"]["exclusions"]["snapshot_error"] == 0 and ck["coverage"]["scored"] ==
         ck["coverage"]["eligible"] - sum(ck["coverage"]["exclusions"][e] for e in
                                          ("no_bar_at_t", "history_lt_504", "bad_bar_at_t", "snapshot_error"))),
        ("independent point-in-time recomputation (fresh history ending at t, split events up to t): identical "
         "conditions / disqualifiers / score / states, ratios within 1e-9",
         sl["missing"] == 0 and sl["exact"] == sl["n"] and sl["max_rel"] < 1e-9 and
         sl["digest_panel"] == sl["digest_pit"]),
        ("total-shareholder-return response = independent recomputation from RAW prices + split / dividend events",
         rs["nan_mismatch"] == 0 and rs["max_abs"] < 1e-9 and rs["n"] > 0),
        ("dividends included: TSR >= price return in every 4-week window with an ex-date",
         acc["with_dividend"] > 0 and acc["tsr_ge_price"] == acc["with_dividend"]),
        ("point-in-time industry (SEC SIC -> FF12) available: >= 70% of evaluation observations in every year and >= 90% "
         "on average (dated SIC starts at a company's first filing in the table, so early 2010 is lower)",
         all(v >= 0.70 for v in sec.values()) and np.mean(list(sec.values())) >= 0.90),
        ("placebo chart side: |t_ic| and |t_inc| < 4", abs(ck["placebo"]["t_ic"]) < 4 and abs(ck["placebo"]["t_inc"]) < 4),
        ("planted response recovered (IC >= 0.95 at every date; its t is degenerate because IC = 1 has no variance) and "
         "destroyed by the null (|t| < 4)",
         ck["planted"]["ic_min"] >= 0.95 and abs(ck["planted"]["null_t_ic"]) < 4),
        ("null worlds deterministic; chart panel digest reproducible", ck["null_repeat_identical"] and
         ck["chart_panel_repeat_identical"]),
    ]


def run_canary():
    ck = json.loads(tagged(CANARY_RUN, "K")[0])
    hs = host_summary(CANARY_RUN)
    checks = canary_checks(ck, hs)
    rep = dict(run=CANARY_RUN, checks=[dict(check=c, ok=bool(ok)) for c, ok in checks],
               passed=sum(bool(ok) for _, ok in checks), total=len(checks), canary=ck, host=hs)
    CANARY_OUT.write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    for c, ok in checks:
        print("PASS" if ok else "FAIL", c)
    print(f"{rep['passed']}/{rep['total']}")


# ---------------------------------------------------------------------------------------------- null
def run_null():
    worlds, panels, resp, info = {}, set(), set(), []
    for exp in NULL_RUNS:
        hs = host_summary(exp)
        panels.add(hs["panel"]["chart_panel_sha256"])
        resp.add(hs["panel"]["response_panel_sha256"])
        info.append(dict(run=exp, backtest=result(exp)["provenance"].get("qc_backtest_id"), seeds=hs["null"]["seeds"],
                         worlds=hs["null"]["worlds"], world_s=hs["null"]["world_s"], wall_s=hs.get("wall_s")))
        for ln in tagged(exp, "N"):
            seed, js = ln.split("|", 1)
            if int(seed) in worlds:
                raise SystemExit(f"duplicate seed {seed}")
            worlds[int(seed)] = json.loads(js)
    seeds = sorted(worlds)
    if seeds != list(range(1, 5001)):
        raise SystemExit(f"incomplete null: {len(seeds)} worlds")
    if len(panels) != 1:
        raise SystemExit(f"chart panel differs across null runs: {panels}")
    W = [worlds[s] for s in seeds]
    nw = [dict(t_ic=w["t_ic"], t_inc=w["t_inc"]) for w in W]
    c = HS.critical_values(nw)
    prom = 0
    gate_fail = {g: 0 for g in ("G1_economic", "G2_monotonic", "G3_significant", "G4_stable", "G5_incremental")}
    for w in W:
        s = dict(high_ann=w["high"], low_ann=w["low"], mono=w["mono"], t_ic=w["t_ic"], t_inc=w["t_inc"],
                 inc_mean=w["inc"], halves=w["halves"], block_max=w["blk"])
        for k in ("high_ann", "low_ann", "mono"):
            if s[k] is None:
                s[k] = float("nan")
        if s["block_max"] is None:
            s["block_max"] = float("inf")
        g = HS.promotion(s, c)
        prom += int(g["pass"])
        for k in gate_fail:
            gate_fail[k] += int(g[k])
    with NULL_TABLE.open("w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["seed", "t_ic", "t_inc", "ic", "inc", "high", "low", "mono", "half1", "half2", "block_max"])
        for s, w in zip(seeds, W):
            wr.writerow([s, w["t_ic"], w["t_inc"], w["ic"], w["inc"], w["high"], w["low"], w["mono"],
                         w["halves"][0], w["halves"][1], w["blk"]])
    t_ic = np.array([w["t_ic"] for w in W])
    t_inc = np.array([w["t_inc"] for w in W])
    out = dict(
        method="H020 null v1: unstratified identity-tethered within-date permutation of the chart side (Q, G), "
               "no self-matches (qr_h020_stats.ChartTether, NULL_STRATIFIED = False); complete procedure per world",
        worlds=len(W), seeds=[1, 5000], failed_worlds=0, retries=0, runs=info, rank_k=50, alpha=HS.ALPHA,
        c_ic=c["t_ic"], c_inc=c["t_inc"],
        null_t_ic=dict(mean=float(t_ic.mean()), sd=float(t_ic.std()), q99=float(np.quantile(t_ic, 0.99))),
        null_t_inc=dict(mean=float(t_inc.mean()), sd=float(t_inc.std()), q99=float(np.quantile(t_inc, 0.99))),
        corr_t_ic_t_inc=float(np.corrcoef(t_ic, t_inc)[0, 1]),
        null_gate_pass_counts=gate_fail, null_full_promotions=prom,
        chart_panel_sha256=panels.pop(), response_panel_sha256_set=sorted(resp),
        null_worlds_csv_sha256=sha256(NULL_TABLE), spec_sha256=p5h020.SPEC_SHA256,
        addendum_sha256=p5h020.ADDENDUM_SHA256, code_sha256=p5h020.CODE_SHA256,
        host_sha256={rel: p5h020.sha256(rel) for rel in p5h020.HOST_CODE})
    NULL_OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("c_ic", "c_inc", "null_full_promotions", "null_gate_pass_counts",
                                          "chart_panel_sha256")}, indent=1))
    print("null result sha256", sha256(NULL_OUT))


# ---------------------------------------------------------------------------------------------- real
def run_real():
    cfg = json.loads((ROOT / "experiments" / REAL_RUN / "config.json").read_text())["params"]
    pins = dict(c_ic=p5h020.C_IC, c_inc=p5h020.C_INC, threshold_commit=p5h020.THRESHOLD_COMMIT,
                null_result_sha256=p5h020.NULL_RESULT_SHA256, spec_sha256=p5h020.SPEC_SHA256,
                addendum_sha256=p5h020.ADDENDUM_SHA256, chart_panel_sha256=p5h020.CHART_PANEL_SHA256)
    for k, v in pins.items():
        if v is None or cfg.get(k) != v:
            raise SystemExit(f"pin mismatch: {k}")
    if sha256(ROOT / p5h020.NULL_RESULT) != p5h020.NULL_RESULT_SHA256:
        raise SystemExit("null result hash mismatch")
    hs = host_summary(REAL_RUN)
    if hs["panel"]["chart_panel_sha256"] != p5h020.CHART_PANEL_SHA256:
        raise SystemExit("real chart panel differs from the calibrated one")
    R = json.loads(tagged(REAL_RUN, "R")[0])
    RS = json.loads(tagged(REAL_RUN, "RS")[0])
    RD = json.loads(tagged(REAL_RUN, "RD")[0])
    R13 = json.loads(tagged(REAL_RUN, "R13")[0])
    s = R["summary"]
    c = dict(t_ic=p5h020.C_IC, t_inc=p5h020.C_INC)
    s2 = dict(s)
    for k in ("high_ann", "low_ann", "mono"):
        if s2[k] is None:
            s2[k] = float("nan")
    gates = HS.promotion(s2, c)                   # recomputed here from the published summary (independent of the host)
    if gates != R["gates"]:
        raise SystemExit(f"gate mismatch host {R['gates']} vs local {gates}")
    null = json.loads((ROOT / p5h020.NULL_RESULT).read_text())
    t_ic_null = np.array([float(r["t_ic"]) for r in csv.DictReader(NULL_TABLE.open())])
    t_inc_null = np.array([float(r["t_inc"]) for r in csv.DictReader(NULL_TABLE.open())])
    out = dict(run=REAL_RUN, backtest=result(REAL_RUN)["provenance"].get("qc_backtest_id"),
               commit=result(REAL_RUN)["provenance"].get("git_commit"), pins=pins, summary=s, gates=gates,
               qualified=gates["pass"],
               p_ic_reporting=float((t_ic_null >= s["t_ic"]).mean()), p_inc_reporting=float((t_inc_null >= s["t_inc"]).mean()),
               high_minus_low_ann=(s["high_ann"] - s["low_ann"]) if None not in (s["high_ann"], s["low_ann"]) else None,
               series=RS, diagnostics=RD, diag_13w=R13, host=hs, null_c=dict(c_ic=null["c_ic"], c_inc=null["c_inc"]))
    REAL_OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(gates=gates, t_ic=s["t_ic"], t_inc=s["t_inc"], high=s["high_ann"], low=s["low_ann"],
                          mono=s["mono"], ic=s["ic_mean"]), indent=1))


if __name__ == "__main__":
    {"canary": run_canary, "null": run_null, "real": run_real}[sys.argv[1]]()
