"""P10-CP1 (owner D204): the H025 no-return feasibility audit, offline. Reads the two audit runs (S027 audit mode,
E027-01 / E027-02), checks the uploaded files against the pins, joins the in-host part of the event ledger (review,
security id, eligibility / identity status, FF12, market-cap quintile) with the SEC ledger, writes the frozen event
ledger research/phase10/ledger/h025_event_ledger.csv (NO return column) and research/phase10/cp1/P10_CP1_audit.json
(feasibility counts, the sample gate, determinism, the digests to pin).

    PYTHONPATH=src python research/phase10/cp1/P10_CP1_audit.py
"""
import csv
import gzip
import hashlib
import io
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
import qr_h025 as H  # noqa: E402
import qr_p7_export as E  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import gitutil, p10h025 as P  # noqa: E402

SEC_LEDGER = ROOT / "research/phase10/ledger/h025_sec_ledger.csv.gz"
EXTRA = ("review_date", "security_id", "eligibility_result", "identity_status", "identity_source", "ff12",
         "mcap_quintile", "primary_event", "single_control", "exclusion_reason")


def uploaded(exp):
    from qresearch import run as RUN
    cfg = json.loads((ROOT / "experiments" / exp / "config.json").read_text())
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    bc = prov["build_commit"]
    files = RUN.assemble_files(cfg, bc, False)
    h = lambda t: hashlib.sha256(t.encode()).hexdigest()  # noqa: E731
    man = json.loads(gitutil.show_file(bc, "research/phase7/data_v2/data_freeze_v2.json"))
    rel = {"qr_x998.py": "strategies/X998_data_v2_export/main.py"}
    for f in man["files"]:
        if f.startswith("src/qresearch/lean/"):
            rel[Path(f).name] = f
    frozen = {n: h(files[n]) == man["files"][r] for n, r in rel.items() if n in files}
    pins = dict(main=h(files["main.py"]) == P.CODE_SHA256[P.HOST],
                qr_h025=h(files["qr_h025.py"]) == P.CODE_SHA256["src/qresearch/lean/qr_h025.py"],
                qr_s024=files["qr_s024.py"] == gitutil.show_file(bc, P.PARENT_HOST),
                qr_p7_pred=h(files["qr_p7_pred.py"]) == P.PRED_CODE_SHA256,
                spec=h(gitutil.show_file(bc, P.SPEC)) == P.SPEC_SHA256,
                events_payload=f"PAYLOAD_SHA256 = '{P.PAYLOAD_SHA256}'" in files["qr_h025_events.py"])
    ok = RUN.code_hash(files) == prov["code_sha256"] and all(frozen.values()) and all(pins.values())
    return ok, dict(build_commit=bc, code_sha256=prov["code_sha256"], frozen_files_equal=frozen, pins=pins,
                    files=len(files), max_file_chars=max(len(v) for v in files.values()))


def run_rows(exp):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    blob = joined(ls, "QRH")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["ledger_rows"]["blob_sha256"]
    rows = json.loads(E.unpack(blob))["rows"]
    assert H.sha(rows) == st["in_host_ledger_sha256"]
    return st, rows


def reason(r, x):
    st = x[1]
    if r["window_status"] == "before_window":
        return "trigger before 2011-02-01 (no Data v2 review before it; cooldown only)"
    if r["window_status"] == "exit_after_2017":
        return "20-session exit after 2017-12-29 (development period ends)"
    if st == "NOT_ELIGIBLE":
        return "issuer not in the Data v2 eligible universe at the review (no eligible security carries its CIK)"
    if st == "IDENTITY_UNRESOLVED":
        return "identity unresolved (an eligible security without verified identity carries the as-filed symbol)"
    if st == "NO_REVIEW":
        return "no Data v2 review before the trigger"
    if r["kind"] == "single" and int(r["near_cluster"]):
        return "single-insider control within 19 sessions of a cluster event of the issuer"
    return ""


def main(exps=P.AUDIT):
    sec = list(csv.DictReader(io.StringIO(gzip.decompress(SEC_LEDGER.read_bytes()).decode())))
    runs = {}
    for exp in exps:
        ok, up = uploaded(exp)
        st, rows = run_rows(exp)
        runs[exp] = dict(upload_ok=ok, upload=up, st=st, rows=rows)
    a, b = (runs[e] for e in exps)
    det = dict(in_host_identical=a["st"]["in_host_ledger_sha256"] == b["st"]["in_host_ledger_sha256"],
               rows_identical=a["rows"] == b["rows"], counts_identical=a["st"]["counts"] == b["st"]["counts"])
    rows = {x[0]: x for x in a["rows"]}
    assert set(rows) == {r["event_id"] for r in sec} and len(rows) == len(sec)
    out = []
    for r in sec:
        x = rows[r["event_id"]]
        prim = r["kind"] == "cluster" and r["window_status"] == "in_window" and x[1] in ("ELIGIBLE", "ELIGIBLE_MULTICLASS")
        ctrl = r["kind"] == "single" and r["window_status"] == "in_window" and x[1] in ("ELIGIBLE", "ELIGIBLE_MULTICLASS") \
            and not int(r["near_cluster"])
        out.append(dict(r, review_date=x[2] or "", security_id=x[3] or "", eligibility_result=x[1],
                        identity_status={"ELIGIBLE": "MAPPED", "ELIGIBLE_MULTICLASS": "MAPPED_MULTICLASS"}.get(
                            x[1], x[1]), identity_source=x[6] or "", ff12=x[4] or "",
                        mcap_quintile="" if x[5] is None else x[5], primary_event=int(prim), single_control=int(ctrl),
                        exclusion_reason=reason(r, x)))
    fields = list(sec[0].keys()) + list(EXTRA)
    s = io.StringIO()
    w = csv.DictWriter(s, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    for r in out:
        w.writerow(r)
    data = s.getvalue().encode()
    (ROOT / P.EVENT_LEDGER).write_bytes(data)
    cl = [r for r in out if r["kind"] == "cluster"]
    inw = [r for r in cl if r["window_status"] == "in_window"]
    prim = [r for r in cl if r["primary_event"]]
    by_year = Counter(r["trigger_date"][:4] for r in prim)
    vals = sorted(float(r["cluster_value"]) for r in prim)
    q = lambda p: round(vals[min(len(vals) - 1, int(p * (len(vals) - 1) + 0.5))], 2) if vals else None  # noqa: E731
    feas = dict(
        sec=json.loads((ROOT / P.LEDGER_MANIFEST).read_text())["feasibility"],
        clusters_in_window_before_universe=len(inw),
        in_window_status=dict(Counter(r["eligibility_result"] for r in inw)),
        identity_exclusions=dict(identity_unresolved=sum(1 for r in inw if r["eligibility_result"] == "IDENTITY_UNRESOLVED"),
                                 not_eligible=sum(1 for r in inw if r["eligibility_result"] == "NOT_ELIGIBLE"),
                                 multiclass_mapped=sum(1 for r in prim if r["eligibility_result"] == "ELIGIBLE_MULTICLASS")),
        identity_source=dict(Counter(r["identity_source"] for r in prim)),
        primary_events=len(prim), primary_issuers=len({r["issuer_cik"] for r in prim}),
        primary_by_year=dict(sorted(by_year.items())),
        insiders_per_event=dict(sorted(Counter(min(int(r["n_insiders"]), 5) for r in prim).items())),
        cluster_value_quantiles=dict(p05=q(.05), p25=q(.25), p50=q(.5), p75=q(.75), p95=q(.95)),
        cluster_value_buckets=dict(Counter("100k-250k" if v < 250e3 else "250k-1m" if v <= 1e6 else ">1m" for v in vals)),
        ceo_cfo_events=sum(int(r["ceo_cfo"]) for r in prim), director_only_events=sum(int(r["director_only"]) for r in prim),
        single_controls=sum(r["single_control"] for r in out),
        sample_gate=dict(events=len(prim), years_with_10=sum(1 for v in by_year.values() if v >= H.MIN_YEAR_EVENTS),
                         passed=H.sample_ok(dict(by_year), len(prim))))
    res = dict(experiments=list(exps), upload={e: dict(ok=runs[e]["upload_ok"], **runs[e]["upload"]) for e in exps},
               determinism=det, in_host_ledger_sha256=a["st"]["in_host_ledger_sha256"],
               event_ledger_sha256=hashlib.sha256(data).hexdigest(), event_ledger_rows=len(out),
               counts=a["st"]["counts"], calendar=a["st"]["calendar"], pit_audit=a["st"]["pit_audit"],
               feasibility=feas, wall_s={e: runs[e]["st"]["wall_s"] for e in exps})
    (HERE / "P10_CP1_audit.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(determinism=det, event_ledger_sha256=res["event_ledger_sha256"],
                          sample_gate=feas["sample_gate"], primary_by_year=feas["primary_by_year"]), indent=1))


if __name__ == "__main__":
    main()
