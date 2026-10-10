"""Data Infrastructure v2 (owner D190): the ONE consolidated reference table uploaded to QuantConnect
(src/qresearch/lean/qr_data_v2*.py, lzma + base85, qresearch.v2pack). Public SEC data and our own tables only; no
QuantConnect data. Every date is a day number since 2000-01-01; nothing filed or effective after 2017-12-31 is kept
(2018+ is sealed). Components:

  sec_v1   the data-v1 SEC correction layer, unchanged in substance (D111/D113/D114): the 'repaired' securities'
           periodic filings (form, filed, period end, cover date, cover shares, statement totals AS FIRST FILED -- exact
           values) and the dated SIC/CIK identity rows. Compacted losslessly for the fields Score v1 reads (revenue,
           gross profit, net income, operating cash flow: quarter + fiscal year; total assets; equity); the five unused
           fields (cost of revenue, operating income, free cash flow) and every row filed / effective after 2017-12-31
           are dropped. Accession numbers are replaced by their rank (the D111 sort order (filed, accession) is kept).
           The data-v1 vendor-report-keyed lists (timing holds, quarantine releases, restatement blocks, field
           releases) are not part of v2 (they refer to data-v1 vendor reports; v2 timing is M2).
  f        every periodic filing (10-K / 10-Q / 10-KT and amendments; report date 2008-03-31 .. 2017-12-31; filed by
           2017-12-31) of every registrant in the dated identity table (EDGAR submissions; pre-XBRL included), columnar
           [period-end deltas, filed - period end, form, filed - cover date, cover shares (g4)]: the M2 filing reference
           and the D111 cover-page share counts (single unambiguous count, filed from 2010-06-01) -- the P7-CP5e table.
  ext      the verified identity extension rows (SAFE / BOUNDED only; research/phase7/cp5e/identity_extension.json).
  guard    restatement guard reference (P7-CP5d methodology): for every registrant period whose SEC quarterly revenue
           or total assets was later re-reported (> 0.5% different), per field [first g4, later g4, later filed - period
           end] (None where the field has no later value); periods without any later value can never trigger the guard
           and are omitted.
  idv      SEC first-filed quarterly revenue / total assets per period ending by 2010-12-31, for the registrants that
           have identity extension rows (the in-cloud identity continuity check of extension-mapped reports).
  diag     diagnostics only (never used by a rule): the E993-02 data-v1 membership (per security, a hex bitset over the
           84 reviews), the frozen P7-CP5e target population, and the identity REJECT / no-identity-row security lists
           (owner sanity check, D190 item 7).
Output: src/qresearch/lean/qr_data_v2*.py, research/phase7/data_v2/data_v2_reference.json (component hashes, sizes)."""
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "strategies/X997_universe_repair"),
                str(ROOT / "strategies/X996_first_seen_ledger")]
import qr_sec_data as D  # noqa: E402
from p5d_ref import load_table as load_p5d  # noqa: E402
from p5e_ref import load_table as load_p5e  # noqa: E402
from qresearch import v2pack  # noqa: E402
from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pit import index_facts, period_versions  # noqa: E402

EPOCH = date(2000, 1, 1)
END = "2017-12-31"
LEAN = ROOT / "src" / "qresearch" / "lean"
OUT = Path(__file__).parent
KEYS = ("revenue_q", "revenue_ttm", "gross_profit_q", "gross_profit_ttm", "net_income_q", "net_income_ttm",
        "operating_cash_flow_q", "operating_cash_flow_ttm", "total_assets", "stockholders_equity")
FORMS = ("10-K", "10-K/A", "10-KT", "10-Q", "10-Q/A")
GFIELDS = ("revenue_q", "total_assets")
IDV_TO = "2010-12-31"


def dn(s):
    return None if not s else (date.fromisoformat(str(s)[:10]) - EPOCH).days


def num(x):
    if x is None:
        return None
    x = float(x)
    return int(x) if x.is_integer() and abs(x) < 2 ** 53 else x


def g4(x):
    if not x:
        return None
    sgn = -1 if x < 0 else 1
    m, e = f"{abs(x):.3e}".split("e")
    return sgn * (int(m.replace(".", "")) * 100 + int(e))


def sec_v1(sec):
    corr = {}
    for sid, c in sorted(sec["corrections"].items()):
        if c.get("status") != "repaired":
            continue
        rows = sorted((r for r in c["filings"] if r[2] <= END), key=lambda r: (r[2], r[0]))
        out = []
        for r in rows:
            accn, form, filed, pe, cd, sh, vals = r
            v = [[KEYS.index(k), num(x)] for k, x in sorted((vals or {}).items()) if k in KEYS and x is not None]
            out.append([FORMS.index(form), dn(filed), dn(pe), dn(cd), num(sh), v])
        corr[sid] = dict(cik=c["cik"], rows=out)
    sic = {sid: [[dn(e), s, c] for e, s, c in rows if e <= END] for sid, rows in sorted(sec["sic_history"].items())}
    sic = {k: v for k, v in sic.items() if v}
    return dict(keys=list(KEYS), forms=list(FORMS), corrections=corr, sic_history=sic)


def columnar(flat):
    cols = [[], [], [], [], []]
    for r in flat:
        r = list(r) + [None] * (5 - len(r))
        for i in range(5):
            cols[i].append(r[i])
    return cols


def guard_and_idv(ciks, client):
    guard, idv, n_periods, n_later = {}, {}, 0, 0
    for cik in sorted(ciks, key=int):
        cf = client.companyfacts(int(cik))
        if not cf:
            continue
        facts = index_facts(cf)
        pes = sorted({f["end"] for tag in ("Assets", "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                                            "SalesRevenueNet") for f in facts.get(tag, ())
                      if f.get("form") in FORMS and "2008-03-31" <= f["end"] <= END})
        g, iv = {}, {}
        for pe in pes:
            vers = [v for v in period_versions(facts, pe) if v["filed"] <= END]
            row, has_later, first = [], False, []
            for fld in GFIELDS:
                vals = [(v["filed"], v["values"][fld]) for v in vers if v["values"].get(fld)]
                if not vals:
                    row += [None, None, None, None]
                    first.append(None)
                    continue
                fi, fv = vals[0]
                lat = next(((d_, x) for d_, x in vals[1:] if abs(x / fv - 1) > 0.005), None)
                row += [g4(fv), dn(fi) - dn(pe), g4(lat[1]) if lat else None, (dn(lat[0]) - dn(fi)) if lat else None]
                first.append(g4(fv))
                has_later |= lat is not None
            n_periods += 1
            if has_later:
                g[str(dn(pe))] = [row[0], row[2], None if row[2] is None else row[1] + row[3],
                                  row[4], row[6], None if row[6] is None else row[5] + row[7]]
                n_later += 1
            if pe <= IDV_TO and any(x is not None for x in first):
                iv[str(dn(pe))] = first
        if g:
            guard[str(cik)] = g
        if iv:
            idv[str(cik)] = iv
    return guard, idv, n_periods, n_later


def main():
    sec = D.load_table()
    p5e, p5d = load_p5e(), load_p5d()
    tp = json.loads((ROOT / "research/phase7/cp5e/target_population.json").read_text())
    ide = json.loads((ROOT / "research/phase7/cp5e/identity_extension.json").read_text())["rows"]
    client = SECClient()
    f = {cik: columnar(flat) for cik, flat in sorted(p5e["f"].items())}
    guard, idv, n_periods, n_later = guard_and_idv(f.keys(), client)
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
    table = dict(version="data_v2", epoch=str(EPOCH), end=END, sec_v1=sec_v1(sec), f=f, ext=p5e["ext"], guard=guard,
                 idv=idv, diag=diag)
    for p in LEAN.glob("qr_data_v2*.py"):
        p.unlink()
    files = v2pack.pack(table, "qr_data_v2")
    for name, text in files.items():
        (LEAN / name).write_text(text)
    comp = {k: dict(sha256=hashlib.sha256(v2pack.raw_bytes(v)).hexdigest(), raw_bytes=len(v2pack.raw_bytes(v)))
            for k, v in table.items()}
    summ = dict(loader_version=v2pack.LOADER_VERSION, packing="lzma preset 9|extreme + base85, chunks of 63,000",
                table_sha256=hashlib.sha256(v2pack.raw_bytes(table)).hexdigest(), parts=len(files) - 1,
                project_files_of_table=len(files), chars=sum(len(t) for t in files.values()),
                file_sha256={n: hashlib.sha256(t.encode()).hexdigest() for n, t in sorted(files.items())},
                components=comp,
                counts=dict(repaired_securities=len(table["sec_v1"]["corrections"]),
                            sic_history_securities=len(table["sec_v1"]["sic_history"]),
                            registrants_with_filings=len(f), extension_rows=len(p5e["ext"]),
                            guard_registrants=len(guard), guard_periods=n_later, guard_periods_scanned=n_periods,
                            idv_registrants=len(idv), id_reject=len(diag["id_reject"]), id_none=len(diag["id_none"])),
                sources=dict(target_population_sha256=tp["sha256"],
                             identity_extension_json_sha256=hashlib.sha256(
                                 (ROOT / "research/phase7/cp5e/identity_extension.json").read_bytes()).hexdigest(),
                             p5e_ref_sha256=hashlib.sha256(v2pack.raw_bytes(p5e)).hexdigest(),
                             qr_sec_data_v1_sha256=hashlib.sha256(v2pack.raw_bytes(sec)).hexdigest()),
                sec_requests=client.fetched)
    (OUT / "data_v2_reference.json").write_text(json.dumps(summ, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in summ.items() if k not in ("file_sha256",)}, indent=1))


if __name__ == "__main__":
    main()
