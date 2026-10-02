"""Authoritative SEC TTM reference for the True-TTM validation (X975, D113).

For each sample company (the E971 sample, 406 companies), from SEC XBRL company facts AS FIRST FILED:
  * quarterly values per fiscal quarter from each filing's own facts (Q4 = fiscal-year total from the 10-K minus the
    nine-month YTD known on the 10-K's filing date; never from a later filing);
  * TTM for each period end P = sum of the four consecutive quarters ending at P, each in the version public on the
    date the newest of them was filed (amendments only from their own filing date); available from the day after
    that filing date; no interpolation, no filling;
  * 'fy_check' at fiscal-year ends: the 10-K's own annual total (authoritative) for the same window.
Output: strategies/X975_true_ttm_validation/ttm_ref*.py (packed) and research/phase2/sec/x975_inputs.json."""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pack import pack, unpack  # noqa: E402
from qresearch.sec_pit import build_company  # noqa: E402
import rss_index  # noqa: E402

STRAT = ROOT / "strategies" / "X975_true_ttm_validation"
BASES = ("revenue", "gross_profit", "operating_income", "net_income", "operating_cash_flow", "free_cash_flow")


def sec_ttm(recs):
    """{period_end: {base: [ttm, available, [quarter ends], fy_total or None]}} from SEC records (list of dicts)."""
    by_pe = {}
    for r in sorted(recs, key=lambda r: (r["period_end"], r["filed"])):
        by_pe.setdefault(r["period_end"], []).append(r)
    pes = sorted(by_pe)
    out = {}
    for i in range(3, len(pes)):
        win = pes[i - 3:i + 1]
        ds = [date.fromisoformat(p) for p in win]
        if not all(80 <= (b - a).days <= 100 for a, b in zip(ds, ds[1:])):
            continue
        newest = min(by_pe[win[-1]], key=lambda r: r["filed"])["filed"]       # first filing of the newest quarter
        vers = [max((r for r in by_pe[p] if r["filed"] <= newest), key=lambda r: r["filed"], default=None) for p in win]
        if any(v is None for v in vers):
            continue
        avail = (date.fromisoformat(max(v["filed"] for v in vers)) + timedelta(days=1)).isoformat()
        row = {}
        for b in BASES:
            qs = [v["values"].get(b + "_q") for v in vers]
            if any(q is None for q in qs):
                continue
            fy = vers[-1]["values"].get(b + "_ttm") if vers[-1]["form"].startswith("10-K") else None
            row[b] = [sum(qs), avail, win, fy]
        if row:
            out[win[-1]] = row
    return out


def main():
    src = ROOT / "strategies" / "X971_sec_verification"
    sample = unpack({p.name: p.read_text() for p in src.glob("sec_ref*.py")}, "sec_ref")["sample"]
    client = SECClient()
    fye = {}
    for r in rss_index.load():
        if r["form"] in ("10-K", "10-Q") and r["fye"]:
            fye.setdefault(r["cik"], set()).add(r["fye"])
    ref, cats = {}, {}
    for cik, c in sample.items():
        cf, sub = client.companyfacts(int(cik)), client.submissions(int(cik))
        if not cf:
            continue
        recs = [r for r in build_company(cf, sub) if "2008-06-30" <= r["period_end"] <= "2021-12-31"
                and r["filed"] <= "2021-12-31"]
        ref[cik] = {"sids": c["sids"], "ttm": sec_ttm(recs)}
        f = fye.get(int(cik), set())
        cats[cik] = {"why": c["why"], "fiscal_year_ends": sorted(f), "non_calendar": any(x != "1231" for x in f),
                     "changed_fiscal_year": len(f) > 1,
                     "amended": any(r["form"].endswith("/A") for r in recs)}
    STRAT.mkdir(parents=True, exist_ok=True)
    for p in STRAT.glob("ttm_ref*.py"):
        p.unlink()
    for name, text in pack(ref, "ttm_ref").items():
        (STRAT / name).write_text(text)
    (Path(__file__).parent / "x975_inputs.json").write_text(json.dumps(cats, indent=1, sort_keys=True) + "\n")
    print(len(ref), "companies;", sum(len(v["ttm"]) for v in ref.values()), "SEC TTM periods;",
          len(list(STRAT.glob("ttm_ref*.py"))), "files")


if __name__ == "__main__":
    main()
