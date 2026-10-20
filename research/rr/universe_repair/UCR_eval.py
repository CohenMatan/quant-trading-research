"""UCR-1 (owner D269): offline evaluation of the ONE repair re-audit run (E806-01; E806-02 only as the documented
retry). Frozen with the protocol (research/rr/universe_repair/UCR_protocol.md, pinned in qresearch.rr_ucr). It reads
only the run's aggregate 'UCR|' lines and:
  - re-applies the frozen re-audit rule (qr_ucr.reaudit_verdict with qr_sca.year_verdict) to the exported year
    records; the in-run verdicts must agree;
  - snapshot check (reported, never gating): the ORIGINAL vendor-eligible counts per year vs SCA-1's E805-02;
  - external reference check (reported, never gating): the REPAIRED eligible counts per year vs Data v1 (old vendor
    dataset + our earlier SEC layer; 2011-2017) and Data v2.1 (2018-2021), from the committed RR4 reconciliation.
Writes research/rr/universe_repair/UCR_result_<run>.json and the extracted lines.

    PYTHONPATH=src python research/rr/universe_repair/UCR_eval.py E806-01"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_sca as A  # noqa: E402
import qr_ucr as U  # noqa: E402


def parse(lines):
    res = dict(years={})
    for ln in lines:
        if not ln.startswith("UCR|"):
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
    again = {y: U.reaudit_verdict(r["repaired"], r["original"], r["repair"], A.year_verdict) for y, r in years.items()}
    mismatch = [y for y in years if again[y]["verdict"] != years[y]["verdict"]["verdict"]]
    windows = {w: A.window_verdict({y: dict(verdict=again[y]) for y in years}, a, b) for w, (a, b) in A.WINDOWS.items()}
    if res.get("windows") and any(windows[w]["outcome"] != res["windows"][w]["outcome"] for w in windows):
        mismatch.append("windows")
    sca = {}
    p = ROOT / "research/rr/sec_classification/SCA_result_E805-02.json"
    if p.exists():
        sca = {y: r["E"] for y, r in json.loads(p.read_text())["evaluation"]["years"].items()}
    ref = {}
    q = ROOT / "research/rr/universe_risk/RR4_universe_reconciliation.json"
    if q.exists():
        for y, r in json.loads(q.read_text())["by_year"].items():
            if r.get("data_v1"):
                ref[y] = ("data_v1", r["data_v1"])
            elif r.get("data_v2x"):
                ref[y] = ("data_v2.1", r["data_v2x"]["eligible"])
    table = {}
    for y, r in sorted(years.items()):
        o, n, rp = r["original"], r["repaired"], r["repair"]
        table[y] = dict(E_original=o["E"], E_repaired=n["E"], repaired=rp.get("repaired", 0),
                        repaired_securities=r["repaired_exits"].get("repaired_securities"),
                        C_original=o["confirmed"], C_remaining=n["confirmed"], P_remaining=n["possible"],
                        U_remaining=n["unresolved"], gap_C=n["gap_C"], gap_CP=n["gap_CP"], gap_max=n["gap_max"],
                        validation=again[y]["repair_validation"], verdict=again[y]["verdict"],
                        reasons=again[y]["reasons"],
                        snapshot_vs_E805_02=(o["E"] - sca[y]) if y in sca else None,
                        reference=dict(source=ref[y][0], count=ref[y][1],
                                       repaired_short_pct=round((ref[y][1] - n["E"]) / ref[y][1], 4))
                        if y in ref else None)
    return dict(windows=windows, years=table, in_run_agrees=not mismatch, mismatches=mismatch)


def main(eid):
    from qresearch import results
    r = json.loads((ROOT / "experiments" / eid / "result.json").read_text())
    lines = results.lines_from_statistics(r["qc_statistics"])
    res = parse(lines)
    out = dict(run=eid, meta=res.get("meta"), evaluation=evaluate(res), raw_years=res["years"])
    (ROOT / f"research/rr/universe_repair/{eid}_ucr_lines.txt").write_text(
        "\n".join(ln for ln in lines if ln.startswith("UCR|")) + "\n")
    (ROOT / f"research/rr/universe_repair/UCR_result_{eid}.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    o = main(sys.argv[1])
    print(json.dumps(o["evaluation"]["windows"], indent=1))
