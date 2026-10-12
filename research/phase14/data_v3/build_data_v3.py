"""Data v3 builder (owner D229; research/phase14/data_v3/DATA_V3_spec.md, committed before this builder ran).
Public SEC company facts (cached under data/sec_cache; filings <= 2021-12-31 only) and the frozen Data v2.1 table; no
QuantConnect data. Outputs:
  * src/qresearch/lean/qr_data_v3_NN.py   the guard-v3 reference table (spec 3; at most four parts, no loader file);
  * src/qresearch/lean/qr_v3val_NN.py     the SEC validation reference of the stratified sample (spec 7.1-7.2);
  * research/phase14/data_v3/data_v3_reference.json   hashes, sizes, counts, the sample, and the descriptive SEC-only
    restatement-materiality study (spec 7.6).

    PYTHONPATH=src python research/phase14/data_v3/build_data_v3.py
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
LEAN = ROOT / "src" / "qresearch" / "lean"
sys.path[:0] = [str(ROOT / "src"), str(LEAN)]
from qr_data_v21 import load_table  # noqa: E402
from qr_xs_diag import FF12_NAMES, ff12  # noqa: E402
from qresearch import data_v3 as V3  # noqa: E402
from qresearch.sec_edgar import SECClient  # noqa: E402

GUARD_PREFIX, VAL_PREFIX = "qr_data_v3", "qr_v3val"
PER_SECTOR = 25
SIZE_MIN = 1e9
SECTORS = tuple(n for n in FF12_NAMES if n not in ("Money", "Unclassified"))
PERIODS = (("2011-2014", 2011, 2014), ("2015-2017", 2015, 2017), ("2018-2021", 2018, 2021))


def sig6(x):
    return None if x is None else float(f"{x:.6g}")


def size_proxy(cf):
    best = 0.0
    for tax, tag in (("us-gaap", "Assets"), ("dei", "EntityPublicFloat")):
        for f in (((cf.get("facts") or {}).get(tax) or {}).get(tag) or {}).get("units", {}).get("USD", ()):
            if "2010-01-01" <= f["end"] <= V3.END and f.get("filed", "9999") <= V3.END:
                best = max(best, float(f["val"]))
    return best


def latest_sic(sic_history):
    """CIK -> SIC of its latest identity row dated <= 2021-12-31 (any security of the registrant)."""
    best = {}
    for rows in sic_history.values():
        for day, sic, cik in rows:
            if cik in (None, "") or sic in (None, "") or day > V3.dn(V3.END):
                continue
            k = str(int(cik))
            if k not in best or day > best[k][0]:
                best[k] = (day, int(sic))
    return {k: v[1] for k, v in best.items()}


def centred(x):
    x = np.asarray(x, float)
    out = np.full(x.size, np.nan)
    ok = np.isfinite(x)
    n = int(ok.sum())
    if n > 1:
        from scipy.stats import rankdata
        out[ok] = 2.0 * (rankdata(x[ok]) - 1.0) / (n - 1) - 1.0
    return out


def main():
    t = load_table()
    f = t["f"]
    sic = latest_sic(t["sec_v1"]["sic_history"])
    client = SECClient()
    rows, sizes, stats = {}, {}, Counter()
    facts_keep = {}
    for n, cik in enumerate(sorted(f, key=int)):
        cf = client.companyfacts(int(cik))
        if not cf:
            stats["no_companyfacts"] += 1
            continue
        fx = V3.Facts(cf)
        cols = f[cik]
        pes, pe = [], 0
        for i in range(len(cols[0])):
            pe += cols[0][i]
            pes.append(pe)
        r = V3.guard_rows(fx, set(pes))
        stats["periods"] += len(set(pes))
        if r:
            rows[cik] = r
        sizes[cik] = size_proxy(cf)
        s = sic.get(cik)
        if s is not None and ff12(s) in SECTORS and sizes[cik] >= SIZE_MIN:
            facts_keep[cik] = None          # candidates; facts re-read for the sample below
        if n % 500 == 0:
            print("guard", n, len(rows), flush=True)
    C = V3.columnar(rows)
    gfiles, gsha = V3.pack_parts(C, GUARD_PREFIX)
    if len(gfiles) > V3.MAX_PARTS:
        raise SystemExit(f"STOP: the guard table needs {len(gfiles)} parts (> {V3.MAX_PARTS}); spec 3.7")
    for p in LEAN.glob(f"{GUARD_PREFIX}_*.py"):
        p.unlink()
    for name, text in gfiles.items():
        (LEAN / name).write_text(text)
    per_field = Counter(C[2])
    # ---------------------------------------------------------------------------------------- the sample (7.1)
    by_sector = {s: [] for s in SECTORS}
    for cik in facts_keep:
        by_sector[ff12(sic[cik])].append(cik)
    sample = {}
    for s in SECTORS:
        for cik in sorted(by_sector[s], key=V3.sample_key)[:PER_SECTOR]:
            sample[cik] = s
    revs = V3.review_days()
    days = [V3.dn(str(sel)) for _t, sel in revs]
    ref = {}
    asof_end = V3.dn(V3.END)
    known_mat = {}
    for cik in sorted(sample, key=int):
        fx = V3.Facts(client.companyfacts(int(cik)))
        orig = V3.originals(f[cik])
        out, prev = [], None
        for j, D in enumerate(days):
            a, sg, raw = V3.sec_signals(fx, orig, D)
            row = [a] + [sig6(sg[k]) for k in V3.SIGNALS] + [V3.g4(raw[k]) if raw[k] is not None else None for k in V3.RAW]
            if row != prev:
                out.append([j] + row)
                prev = row
            _a2, sg2, _r2 = V3.sec_signals(fx, orig, D, values_asof=asof_end)
            known_mat[(cik, j)] = (sg, sg2)
        ref[cik] = out
    vfiles, vsha = V3.pack_parts(dict(days=days, signals=list(V3.SIGNALS), raw=list(V3.RAW), ref=ref,
                                      sector={k: v for k, v in sample.items()}), VAL_PREFIX)
    for p in LEAN.glob(f"{VAL_PREFIX}_*.py"):
        p.unlink()
    for name, text in vfiles.items():
        (LEAN / name).write_text(text)
    # ---------------------------------------------------------------------------------------- 7.6 descriptive
    mat = {}
    for sg in V3.SIGNALS:
        res = {p[0]: [] for p in PERIODS}
        for j, (tt, _sel) in enumerate(revs):
            ids = sorted(sample, key=int)
            a = np.array([np.nan if known_mat[(c, j)][0][sg] is None else known_mat[(c, j)][0][sg] for c in ids])
            b = np.array([np.nan if known_mat[(c, j)][1][sg] is None else known_mat[(c, j)][1][sg] for c in ids])
            ok = np.isfinite(a) & np.isfinite(b)
            if ok.sum() < 10:
                continue
            pa, pb = centred(a[ok]), centred(b[ok])
            per = next(p[0] for p in PERIODS if p[1] <= tt.year <= p[2])
            res[per].extend((np.abs(pa - pb) / 2.0).tolist())     # percentile units (0..1)
        mat[sg] = {k: dict(n=len(v), share_gt_0_20=float(np.mean(np.asarray(v) > 0.20)) if v else None,
                           median=float(np.median(v)) if v else None,
                           share_changed=float(np.mean(np.asarray(v) > 0)) if v else None) for k, v in res.items()}
    summ = dict(
        spec_sha256=hashlib.sha256((OUT / "DATA_V3_spec.md").read_bytes()).hexdigest(),
        data_v21_table_sha256=hashlib.sha256(json.dumps(t, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        guard=dict(prefix=GUARD_PREFIX, raw_sha256=gsha, parts=len(gfiles), chars=sum(len(x) for x in gfiles.values()),
                   file_sha256={k: hashlib.sha256(v.encode()).hexdigest() for k, v in sorted(gfiles.items())},
                   registrants=len(f), registrants_with_restatements=len(rows), periods=stats["periods"],
                   restated_values=len(C[0]), by_field={V3.FIELDS[k]: v for k, v in sorted(per_field.items())},
                   no_companyfacts=stats["no_companyfacts"], store_tol=V3.STORE_TOL),
        validation=dict(prefix=VAL_PREFIX, raw_sha256=vsha, parts=len(vfiles),
                        chars=sum(len(x) for x in vfiles.values()),
                        file_sha256={k: hashlib.sha256(v.encode()).hexdigest() for k, v in sorted(vfiles.items())},
                        sample=dict(sorted(sample.items(), key=lambda kv: int(kv[0]))),
                        candidates_by_sector={s: len(v) for s, v in by_sector.items()},
                        per_sector=PER_SECTOR, size_min=SIZE_MIN,
                        review_days=[[str(tt), str(sel)] for tt, sel in revs]),
        restatement_materiality_descriptive=mat,
        sec_requests=client.fetched)
    (OUT / "data_v3_reference.json").write_text(json.dumps(summ, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in summ.items() if k not in ("validation",)}, indent=1)[:4000])
    print("validation parts", len(vfiles), "sample", len(sample))


if __name__ == "__main__":
    main()
