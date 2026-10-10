"""P7-CP5e (D188): the packed reference table for X997 (universe repair + identity extension). PUBLIC SEC data and
our own tables only (no QuantConnect data). Complete populations, fixed before any X997 run:

  f      for every SEC registrant in the dated identity table (identity v2 rows + the v1 correction table): every
         periodic filing in EDGAR submissions (10-K / 10-Q / 10-KT and amendments; report date 2008-03-31 ..
         2017-12-31; filed <= 2017-12-31), delta-encoded [pe - previous pe, filed - pe, form, filed - cover date,
         cover shares g4]; the last two only for 10-K/10-Q filed from 2010-06-01 whose own cover page carries ONE
         unambiguous non-dimensional dei:EntityCommonStockSharesOutstanding (sec_pit.cover_shares; D111 policy),
         otherwise omitted. Report date = EDGAR reportDate (pre-XBRL filings included).
  ext    the verified identity extension rows (identity_extension.json, SAFE and BOUNDED only): sid -> [start, CIK];
  v      SEC first-filed quarterly revenue / total assets (g4) per registrant period ending by 2012-12-31 (the
         era in which identity extension rows apply), from the P7-CP5d table (identity value check ID2);
  old    the E993-02 eligible set per review (P7-CP5d table); tgt = the frozen target ids and their SHA-256.
Dates are day numbers since 2000-01-01. Output: strategies/X997_universe_repair/p5e_ref*.py,
research/phase7/cp5e/x997_ref_summary.json."""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "strategies/X996_first_seen_ledger")]
import qr_sec_data as D  # noqa: E402
from p5d_ref import load_table as load_p5d  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
from qresearch.sec_pack import pack  # noqa: E402
from qresearch.sec_pit import cover_shares, index_facts  # noqa: E402

EPOCH = date(2000, 1, 1)
STRAT = ROOT / "strategies" / "X997_universe_repair"
FORMS = {"10-Q": 1, "10-K": 2, "10-KT": 2, "10-K405": 2, "10-Q/A": 3, "10-K/A": 4, "10-KT/A": 4, "10-K405/A": 4}
SHARES_FROM = "2010-06-01"


def dn(s):
    return (date.fromisoformat(str(s)[:10]) - EPOCH).days


def g4(x):
    if not x:
        return None
    sgn = -1 if x < 0 else 1
    m, e = f"{abs(x):.3e}".split("e")
    return sgn * (int(m.replace(".", "")) * 100 + int(e))


def main():
    sec = D.load_table()
    ciks = {int(c) for rows in sec["sic_history"].values() for _e, _s, c in rows if c not in (None, "")}
    for c in sec["corrections"].values():
        ciks.update(int(x) for x in c.get("cik", []))
    client = SECClient()
    f_tab, nshares, nfil, missing = {}, 0, 0, 0
    for cik in sorted(ciks):
        sub = client.submissions(cik)
        if not sub:
            missing += 1
            continue
        rows = []
        for r in filings_table(sub):
            fm, pe, fd = r["form"], r.get("reportDate") or "", r["filingDate"]
            if fm in FORMS and "2008-03-31" <= pe <= "2017-12-31" and fd <= "2017-12-31":
                rows.append((dn(pe), dn(fd), FORMS[fm], r["accessionNumber"], pe, fd, fm))
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
                    rec += [fd_ - dn(cd), g4(sh)]
                    nshares += 1
            flat.append(rec)
            prev = pe_
            nfil += 1
        f_tab[str(cik)] = flat
    ext = json.loads((Path(__file__).parent / "identity_extension.json").read_text())["rows"]
    ext = {r["sid"]: [dn(r["start"]), int(r["cik"])] for r in ext if r["category"] in ("SAFE", "BOUNDED")}
    p5d = load_p5d()
    v_to = dn("2012-12-31")
    v = {cik: {pe: [row[0] if row else None, row[4] if len(row) > 4 else None] for pe, row in pv.items()
               if int(pe) <= v_to} for cik, pv in p5d["vint"].items()}
    tp = json.loads((Path(__file__).parent / "target_population.json").read_text())
    oi = {s: i for i, s in enumerate(p5d["old"]["sids"])}
    table = {"f": f_tab, "ext": ext, "v": v, "old": p5d["old"], "tgt": [oi[s] for s in tp["sids"]],
             "tgt_sha256": tp["sha256"], "epoch": str(EPOCH), "forms": FORMS}
    for p in STRAT.glob("p5e_ref*.py"):
        p.unlink()
    STRAT.mkdir(parents=True, exist_ok=True)
    out = pack(table, "p5e_ref")
    for name, text in out.items():
        (STRAT / name).write_text(text)
    summ = dict(registrants=len(ciks), with_filings=len(f_tab), missing_submissions=missing, filings=nfil,
                cover_counts=nshares, extension_rows=len(ext), targets=len(tp["sids"]), parts=len(out) - 1,
                chars=sum(len(x) for x in out.values()), sec_requests=client.fetched)
    (Path(__file__).parent / "x997_ref_summary.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(summ)


if __name__ == "__main__":
    main()
