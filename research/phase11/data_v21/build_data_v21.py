"""Data Infrastructure v2.1 (owner D206): the frozen Data v2 reference table EXTENDED through 2021-12-31 with the SAME
rules (an extension, not a redesign). Public SEC data and our own tables only (no QuantConnect data). The builder
re-uses the frozen Data v2 builder functions unchanged (research/phase7/data_v2/build_data_v2.py: sec_v1, columnar,
guard_and_idv) and the frozen P7-CP5e filing-table logic (research/phase7/cp5e/build_x997_ref.py), with ONE parameter
changed: the cut-off END = 2021-12-31 instead of 2017-12-31 (nothing filed, reported or effective after 2021-12-31 is
kept; the programme Holdout 2022-01-01 .. 2026-08-31 is never read into any table: the cached SEC JSON snapshots also
hold later filings, which are filtered out by date before anything is used).

Components (identical definitions to Data v2, END = 2021-12-31):
  sec_v1  the data-v1 SEC correction layer (repaired securities' filings + dated SIC/CIK identity rows) up to END;
  f       every periodic filing (10-K / 10-Q / 10-KT and amendments; report date 2008-03-31 .. END; filed <= END) of
          every registrant in the dated identity table, with D111 cover-page share counts (filed from 2010-06-01);
  ext     the verified identity extension rows (unchanged, research/phase7/cp5e/identity_extension.json);
  guard   restatement-guard reference built from SEC company facts with filings up to END;
  idv     first-filed values for periods ending by 2010-12-31 (unchanged definition);
  diag    unchanged (the 2011-2017 data-v1 membership, the P7-CP5e target population, identity residual lists).
Output: src/qresearch/lean/qr_data_v21*.py, research/phase11/data_v21/data_v21_reference.json.

    PYTHONPATH=src python research/phase11/data_v21/build_data_v21.py
"""
import hashlib
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "strategies/X997_universe_repair"),
                str(ROOT / "strategies/X996_first_seen_ledger")]
spec = importlib.util.spec_from_file_location("build_data_v2", ROOT / "research/phase7/data_v2/build_data_v2.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
import qr_sec_data as D  # noqa: E402
from p5d_ref import load_table as load_p5d  # noqa: E402
from p5e_ref import load_table as load_p5e  # noqa: E402
from qresearch import v2pack  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
from qresearch.sec_pit import cover_shares, index_facts  # noqa: E402

END = "2021-12-31"
B.END = END                                # the ONE changed parameter of the frozen Data v2 builder functions
LEAN = ROOT / "src" / "qresearch" / "lean"
PREFIX = "qr_data_v21"
FORMS = {"10-Q": 1, "10-K": 2, "10-KT": 2, "10-K405": 2, "10-Q/A": 3, "10-K/A": 4, "10-KT/A": 4, "10-K405/A": 4}
SHARES_FROM = "2010-06-01"


def filing_table(ciks, client):
    """The P7-CP5e f table (build_x997_ref.py logic, unchanged) with the END cut-off."""
    f_tab, nshares, nfil, missing = {}, 0, 0, 0
    for cik in sorted(ciks):
        sub = client.submissions(cik)
        if not sub:
            missing += 1
            continue
        rows = []
        for r in filings_table(sub):
            fm, pe, fd = r["form"], r.get("reportDate") or "", r["filingDate"]
            if fm in FORMS and "2008-03-31" <= pe <= END and fd <= END:
                rows.append((B.dn(pe), B.dn(fd), FORMS[fm], r["accessionNumber"], pe, fd, fm))
        if not rows:
            continue
        cf = None
        if any(fd >= SHARES_FROM and fm in ("10-K", "10-Q") for _a, _b, _c, _acc, _pe, fd, fm in rows):
            cf = client.companyfacts(cik)
        facts = index_facts(cf) if cf else {}
        flat, prev = [], 0
        for pe_, fd_, code, acc, pe, fd, fm in sorted(rows):
            rec = [pe_ - prev, fd_ - pe_, code]
            if facts and fm in ("10-K", "10-Q") and fd >= SHARES_FROM:
                cd, sh = cover_shares(facts, {"accn": acc, "period_end": pe, "filed": fd})
                if sh and cd:
                    rec += [fd_ - B.dn(cd), B.g4(sh)]
                    nshares += 1
            flat.append(rec)
            prev = pe_
            nfil += 1
        f_tab[str(cik)] = flat
    return f_tab, dict(registrants=len(ciks), with_filings=len(f_tab), missing_submissions=missing, filings=nfil,
                       cover_counts=nshares)


def main():
    sec = D.load_table()
    p5e, p5d = load_p5e(), load_p5d()
    tp = json.loads((ROOT / "research/phase7/cp5e/target_population.json").read_text())
    ide = json.loads((ROOT / "research/phase7/cp5e/identity_extension.json").read_text())["rows"]
    client = SECClient()
    ciks = {int(c) for rows in sec["sic_history"].values() for _e, _s, c in rows if c not in (None, "")}
    for c in sec["corrections"].values():
        ciks.update(int(x) for x in c.get("cik", []))
    flat, fstats = filing_table(ciks, client)
    # 2011-2017 consistency: every Data v2 (P7-CP5e) filing row must be a prefix of the v2.1 row list of its registrant
    pref = dict(registrants=0, identical_prefix=0, differing=[])
    for cik, rows in p5e["f"].items():
        pref["registrants"] += 1
        new = flat.get(cik, [])
        if new[:len(rows)] == rows:
            pref["identical_prefix"] += 1
        else:
            pref["differing"].append(cik)
    f = {cik: B.columnar(r) for cik, r in sorted(flat.items())}
    guard, idv, n_periods, n_later = B.guard_and_idv(f.keys(), client)
    o = p5d["old"]
    revs = sorted(o["reviews"])
    bits = {}
    for j, r in enumerate(revs):
        for i in o["reviews"][r]:
            bits.setdefault(o["sids"][i], ["0"] * len(revs))[j] = "1"
    old = dict(reviews=revs, bits={s: format(int("".join(b), 2), "x") for s, b in sorted(bits.items())})
    extciks = {str(v[1]) for v in p5e["ext"].values()}
    idv = {k: v for k, v in idv.items() if k in extciks}
    diag = dict(old=old, tgt=sorted(tp["sids"]), tgt_sha256=tp["sha256"],
                id_reject=sorted(r["sid"] for r in ide if r["category"] == "REJECT"),
                id_none=sorted(r["sid"] for r in ide if r["category"] == "NO_IDENTITY_ROW"))
    table = dict(version="data_v2.1", epoch=str(B.EPOCH), end=END, sec_v1=B.sec_v1(sec), f=f, ext=p5e["ext"],
                 guard=guard, idv=idv, diag=diag)
    for p in LEAN.glob(f"{PREFIX}*.py"):
        p.unlink()
    files = v2pack.pack(table, PREFIX)
    for name, text in files.items():
        (LEAN / name).write_text(text)
    comp = {k: dict(sha256=hashlib.sha256(v2pack.raw_bytes(v)).hexdigest(), raw_bytes=len(v2pack.raw_bytes(v)))
            for k, v in table.items()}
    summ = dict(loader_version=v2pack.LOADER_VERSION, end=END,
                table_sha256=hashlib.sha256(v2pack.raw_bytes(table)).hexdigest(), parts=len(files) - 1,
                project_files_of_table=len(files), chars=sum(len(t) for t in files.values()),
                file_sha256={n: hashlib.sha256(t.encode()).hexdigest() for n, t in sorted(files.items())},
                components=comp, filings=fstats, data_v2_filing_rows_prefix=dict(
                    registrants=pref["registrants"], identical_prefix=pref["identical_prefix"],
                    differing=len(pref["differing"]), differing_sample=pref["differing"][:20]),
                counts=dict(repaired_securities=len(table["sec_v1"]["corrections"]),
                            sic_history_securities=len(table["sec_v1"]["sic_history"]),
                            registrants_with_filings=len(f), extension_rows=len(p5e["ext"]),
                            guard_registrants=len(guard), guard_periods=n_later, guard_periods_scanned=n_periods,
                            idv_registrants=len(idv), id_reject=len(diag["id_reject"]), id_none=len(diag["id_none"])),
                sec_requests=client.fetched)
    (OUT / "data_v21_reference.json").write_text(json.dumps(summ, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in summ.items() if k != "file_sha256"}, indent=1))


if __name__ == "__main__":
    main()
