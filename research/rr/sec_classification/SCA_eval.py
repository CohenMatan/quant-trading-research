"""SCA-1 (owner D267): offline evaluation of the ONE SEC classification audit run (E805-01; E805-02 only as the
documented retry). Frozen with the protocol (research/rr/sec_classification/SCA_protocol.md, pinned in
qresearch.rr_sca). It reads only the run's aggregate 'SCA|' lines, re-applies the frozen verdict rule of qr_sca to
the exported year records (the in-run verdicts must agree), compares the yearly E stock-months with RR3's E804-01 as
a snapshot check (reported, never gating) and writes research/rr/sec_classification/SCA_result_<run>.json.

    PYTHONPATH=src python research/rr/sec_classification/SCA_eval.py E805-01"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_sca as A  # noqa: E402


def parse(lines):
    res = dict(years={})
    for ln in lines:
        if not ln.startswith("SCA|"):
            continue
        _, sec, rest = ln.split("|", 2)
        if sec == "year":
            y, body = rest.split("|", 1)
            res["years"][y] = json.loads(body)
        else:
            res[sec] = json.loads(rest)
    return res


def evaluate(res):
    years = res["years"]
    again = {y: A.year_verdict(rec) for y, rec in years.items()}
    mismatch = [y for y in years if again[y]["verdict"] != years[y]["verdict"]["verdict"]]
    windows = {w: A.window_verdict({y: dict(verdict=again[y]) for y in years}, a, b) for w, (a, b) in A.WINDOWS.items()}
    if res.get("windows") and any(windows[w]["outcome"] != res["windows"][w]["outcome"] for w in windows):
        mismatch.append("windows")
    ub = {}
    p = ROOT / "research/rr/universe_baseline/E804-01_ub_lines.txt"
    if p.exists():
        for ln in p.read_text().splitlines():
            if ln.startswith("UB|year|"):
                y, body = ln.split("|", 3)[2:]
                ub[y] = json.loads(body)["counts"]["E"]["stock_months"]
    snap = {y: dict(E805=years[y]["E"], E804=ub.get(y), diff=(years[y]["E"] - ub[y]) if y in ub else None)
            for y in sorted(years)}
    table = {y: dict(E=r["E"], confirmed=r["confirmed"], possible=r["possible"], unresolved=r["unresolved"],
                     gap_C=r["gap_C"], gap_CP=r["gap_CP"], gap_max=r["gap_max"],
                     E_cover=r["instrument"]["E_cover"], agree=r["instrument"]["agree_share"],
                     verdict=again[y]["verdict"], reasons=again[y]["reasons"]) for y, r in sorted(years.items())}
    return dict(windows=windows, years=table, in_run_agrees=not mismatch, mismatches=mismatch, snapshot_E=snap)


def main(eid):
    from qresearch import results
    r = json.loads((ROOT / "experiments" / eid / "result.json").read_text())
    lines = results.lines_from_statistics(r["qc_statistics"])
    res = parse(lines)
    out = dict(run=eid, meta=res.get("meta"), evaluation=evaluate(res), raw_years=res["years"])
    (ROOT / f"research/rr/sec_classification/{eid}_sca_lines.txt").write_text(
        "\n".join(ln for ln in lines if ln.startswith("SCA|")) + "\n")
    (ROOT / f"research/rr/sec_classification/SCA_result_{eid}.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    o = main(sys.argv[1])
    print(json.dumps(o["evaluation"]["windows"], indent=1))
