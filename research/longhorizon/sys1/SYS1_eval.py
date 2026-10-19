"""SYS-1 (owner D252): the frozen offline evaluation of E032-02 -> SYS1_result.json.

Written and committed BEFORE any SYS-1 run (protocol section 12; hash pinned in qresearch.sys1). It reads the host's
QRSY block (every arm at 0.10% and 0.20% slippage), checks its digest, applies FS-1 .. FS-6 exactly as frozen and
reports the descriptive outputs of protocol section 13. Classifications are only NOT EXECUTABLE, NOT SUPPORTED or
NOT FALSIFIED — DEVELOPMENT-CONSISTENT; nothing here is a validation, a qualification or evidence of persistent alpha.

    PYTHONPATH=src python research/longhorizon/sys1/SYS1_eval.py [E032-02]
"""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
from P7_CP3R_extract import joined, lines  # noqa: E402
import qr_p7_export as E  # noqa: E402
from qresearch import sys1 as P  # noqa: E402

YEARS = tuple(range(2015, 2022))
EARLY, LATE = (2015, 2016, 2017), (2018, 2019, 2020, 2021)
EPISODES = (2018, 2020)
SYSTEMS = ("A1", "A2", "A3")
LABS = ("s10", "s20")
ROLL = 36
CLASSES = ("NOT EXECUTABLE", "NOT SUPPORTED", "NOT FALSIFIED — DEVELOPMENT-CONSISTENT")


def wealth(arms, name, lab="s10"):
    return arms[name][lab]["summary"]["wealth"]


def years(arms, name, lab="s10"):
    y = arms[name][lab]["metrics"]["years"]
    return {int(k): float(v) for k, v in y.items()}


def log_rel(arms, a, b, lab="s10"):
    ya, yb = years(arms, a, lab), years(arms, b, lab)
    return {y: math.log1p(ya[y]) - math.log1p(yb[y]) for y in YEARS}


def fs5(lr):
    """Protocol section 12: sum > 0, largest year <= 50% of the sum, 2015-2017 > 0, 2018-2021 > 0."""
    tot = sum(lr.values())
    early, late = sum(lr[y] for y in EARLY), sum(lr[y] for y in LATE)
    top = max(lr.values())
    ok = tot > 0 and top <= 0.50 * tot and early > 0 and late > 0
    return dict(ok=bool(ok), total=tot, largest_year=max(lr, key=lr.get), largest=top,
                largest_share=top / tot if tot > 0 else None, sum_2015_2017=early, sum_2018_2021=late)


def rolling_ahead(a, b, n=ROLL):
    """Share of rolling n-month windows (month-end marks, capital first) in which a grows more than b."""
    a, b = [float(x) for x in a], [float(x) for x in b]
    w = [(a[t] / a[t - n]) > (b[t] / b[t - n]) for t in range(n, len(a))]
    return dict(windows=len(w), share_ahead=sum(w) / len(w) if w else None)


def violations_zero(arms):
    bad = {}
    for name, d in arms.items():
        for lab in LABS:
            v = d[lab]["summary"]["violations"]
            if any(v.values()):
                bad[f"{name}/{lab}"] = v
    return bad


def screens(arms, name, canary_ok, integrity_ok, completed, bad):
    """FS-1 .. FS-5 for one system (FS-6 for A1 only, added by the caller)."""
    bm = f"BMX_{name}"
    lr = log_rel(arms, name, bm)
    fs = {
        "FS-1": bool(canary_ok and integrity_ok and completed and not bad),
        "FS-2": wealth(arms, name) > wealth(arms, bm),
        "FS-3": wealth(arms, name) >= wealth(arms, "A0"),
        "FS-4": wealth(arms, name, "s20") > wealth(arms, bm, "s20")
            and wealth(arms, name, "s20") >= wealth(arms, "A0", "s20"),
    }
    f5 = fs5(lr)
    fs["FS-5"] = f5["ok"]
    return fs, f5, lr


def classify(fs):
    if not fs["FS-1"]:
        return CLASSES[0]
    if not all(v for k, v in fs.items() if k != "FS-1"):
        return CLASSES[1]
    return CLASSES[2]


def describe(arms, bmx, name, lab):
    d = arms[name][lab]
    m, s = d["metrics"], d["summary"]
    out = dict(wealth=s["wealth"], ratio_vs_A0=s["wealth"] / wealth(arms, "A0", lab),
               cagr=m["path"]["cagr"], vol=m["path"]["vol"], sharpe=m["path"]["sharpe"], maxdd=m["path"]["maxdd"],
               underwater_share=m["path"]["underwater_share"], underwater_longest=m["path"]["underwater_longest"],
               beta=m["risk"]["beta"], up_capture=m["risk"]["up_capture"], down_capture=m["risk"]["down_capture"],
               strong_up_capture=m["risk"]["strong_up_capture"], strong_up_months=m["risk"]["strong_up_months"],
               commissions=s["commissions"], slippage=s["slippage"], orders=s["trades"], buys=s["buys"],
               sells=s["sells"], etf_orders=s["etf_orders"], turnover_monthly_mean=s["turnover_monthly_mean"],
               skipped_min=s["skipped_min"], scaled_buys=s["scaled_buys"], funding_sales=s["funding_sales"],
               absorber_buys=s["absorber_buys"], stock_positions_max=s["stock_positions_max"],
               stock_positions_mean=s["stock_positions_mean"], alloc=s["alloc"], violations=s["violations"],
               years=years(arms, name, lab))
    if name != "D1":
        lr0 = log_rel(arms, name, "A0", lab)
        out["vs_A0"] = dict(log_rel=lr0, total=sum(lr0.values()), sum_2015_2017=sum(lr0[y] for y in EARLY),
                            sum_2018_2021=sum(lr0[y] for y in LATE),
                            without_2018_2020=sum(v for y, v in lr0.items() if y not in EPISODES),
                            rolling_36m=rolling_ahead(m["month_end"], arms["A0"][lab]["metrics"]["month_end"]))
    if name in SYSTEMS:
        bm = f"BMX_{name}"
        lrb = log_rel(arms, name, bm, lab)
        out["vs_BMX"] = dict(wealth_bmx=wealth(arms, bm, lab), ratio=s["wealth"] / wealth(arms, bm, lab),
                             log_rel=lrb, total=sum(lrb.values()),
                             without_2018_2020=sum(v for y, v in lrb.items() if y not in EPISODES),
                             rolling_36m=rolling_ahead(m["month_end"], arms[bm][lab]["metrics"]["month_end"]))
        b = bmx[name][lab]
        out["bmx"] = dict(mean_weight=b["mean_weight"], min_weight=min(b["weights"]), max_weight=max(b["weights"]),
                          clamps=b["clamps"], realised_beta_system=m["risk"]["beta"],
                          realised_beta_bmx=arms[bm][lab]["metrics"]["risk"]["beta"],
                          realised_beta_gap=m["risk"]["beta"] - arms[bm][lab]["metrics"]["risk"]["beta"])
    if d.get("overlap"):
        out["overlap"] = {k: d["overlap"][k] for k in ("mean_overlap", "max_overlap")}
    return out


def main(exp=P.EVAL):
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRG"))
    blob = joined(ls, "QRSY")
    if hashlib.sha256(blob.encode()).hexdigest() != st["eval"]["blob_sha256"]:
        raise SystemExit("QRSY digest mismatch")
    out = json.loads(E.unpack(blob))
    arms, bmx = out["arms"], out["bmx"]
    can_path = ROOT / P.CANARY_RESULT
    can = json.loads(can_path.read_text())
    canary_ok = bool(can["all_pass"] and P.CANARY_RESULT_SHA256 is not None
                     and hashlib.sha256(can_path.read_bytes()).hexdigest() == P.CANARY_RESULT_SHA256)
    ig = out["integrity"]
    integrity_ok = bool(ig["C1"]["ok"] and ig["C2"]["ok"] and ig["C3"]["ok"] and ig["C4"]["spy"]["ok"]
                        and ig["C4"]["splv"]["ok"] and st["equivalence"] == dict(feature_panel=True,
                                                                                  response_panel=True))
    completed = res["status"] == "completed" and not res["provenance"].get("failure_stage")
    bad = violations_zero(arms)
    verdict = {}
    for name in SYSTEMS:
        fs, f5, lr = screens(arms, name, canary_ok, integrity_ok, completed, bad)
        if name == "A1":
            fs["FS-6"] = wealth(arms, "A1") > wealth(arms, "A2") and wealth(arms, "A1") > wealth(arms, "A3")
        verdict[name] = dict(screens=fs, fs5=f5, log_rel_vs_bmx=lr, classification=classify(fs),
                             role="primary system" if name == "A1" else "comparator (descriptive classification)")
    desc = {lab: {n: describe(arms, bmx, n, lab) for n in sorted(arms)} for lab in LABS}
    two = wealth(arms, "D1") + P.FROZEN_SPY_WEALTH
    result = dict(
        experiment=exp, decision=P.DECISION, protocol_sha256=P.PROTOCOL_SHA256, canary=P.CANARY,
        canary_result_sha256=P.CANARY_RESULT_SHA256, canary_ok=canary_ok, integrity_ok=integrity_ok,
        completed=completed, violations=bad, usmv_verified=out["usmv_verified"], verdict=verdict,
        classification_A1=verdict["A1"]["classification"], descriptive=desc,
        sleeve=out["sleeve"], sleeve_lv15=out["sleeve_lv15"],
        two_account_reference=dict(h028_100k=wealth(arms, "D1"), spy_100k=P.FROZEN_SPY_WEALTH, total=two,
                                   A1=wealth(arms, "A1"), A1_minus_reference=wealth(arms, "A1") - two),
        integrity=ig, months=[out["months"][0], out["months"][-1], len(out["months"])],
        status_statement=("SYS-1 is a development-period account test on fully seen 2015-2021 data. H028 remains "
                          "REJECTED; the Holdout remains sealed; no classification here validates H028 or authorises "
                          "the Holdout, live trading or a D051 production model."))
    (HERE / "SYS1_result.json").write_text(json.dumps(result, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps(dict(verdict={k: dict(v["screens"], classification=v["classification"])
                                   for k, v in verdict.items()},
                          wealth={n: round(wealth(arms, n), 2) for n in sorted(arms)},
                          wealth_s20={n: round(wealth(arms, n, "s20"), 2) for n in sorted(arms)},
                          violations=bad, canary_ok=canary_ok, integrity_ok=integrity_ok), indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
