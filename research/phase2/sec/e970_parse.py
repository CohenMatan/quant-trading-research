"""Parse the E970-01 identifier export (X970) into tables. Identifiers, dates and flags only (no values)."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _d(s):
    try:
        return date.fromisoformat(s[:10]) if s and s not in ("None", "") else None
    except ValueError:
        return None


def _cik(s):
    try:
        return int(str(s).strip())
    except (TypeError, ValueError):
        return None


def lines(exp):
    """All result lines of a run (the published summary-statistic chunks qr_msgs_00..; messages.txt keeps only
    the harness's own QR* lines)."""
    q = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["qc_statistics"]
    text = "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"])))
    return text.split("\n")


def load(exp="E970-01"):
    reports, native, nofund, fin, counts = [], {}, {}, [], {}
    for line in lines(exp):
        p = line.split("|")
        k = p[0]
        if k == "R":
            sid, tic, cik, pe, fd, acc, seen, flags = p[1:9]
            reports.append(dict(sid=sid, ticker=tic, cik=_cik(cik), period_end=_d(pe), file_date=_d(fd),
                                accession=acc, first_seen=_d(seen), estimated=flags[0] == "1",
                                quarantined=flags[1] == "1", amendment=flags[2] == "1"))
        elif k == "N":
            sid, cik, tics, first, last, em, ef, el = p[1:9]
            native[sid] = dict(cik=_cik(cik), tickers=tics.split(","), first=int(first), last=int(last),
                               elig_months=int(em), elig_first=None if ef == "None" else int(ef),
                               elig_last=None if el == "None" else int(el))
        elif k == "M":
            sid, tk, n, f, l, fl, ls = p[1:8]
            tickers = []
            for part in tk.split(";"):
                t, rng = part.rsplit(":", 1)
                a, b = rng.split("-")
                tickers.append((t, int(a), int(b)))
            nofund[sid] = dict(tickers=tickers, liquid_months=int(n), first_ym=int(f), last_ym=int(l),
                               first_liquid=_d(fl), last_seen=_d(ls))
        elif k == "F":
            sid, tic, cik, ym, ff, tpl, sec, ind, flags, pe = p[1:11]
            fin.append(dict(sid=sid, ticker=tic, cik=_cik(cik), ym=int(ym), fin_format=ff == "1", template=tpl,
                            sector=sec, industry=ind, rev=flags[0] == "1", gp=flags[1] == "1", cor=flags[2] == "1",
                            oi=flags[3] == "1", period_end=_d(pe)))
        elif k == "C":
            counts = json.loads(line[2:])
    return dict(reports=reports, native=native, nofund=nofund, fin=fin, counts=counts)


if __name__ == "__main__":
    t = load()
    print({k: len(v) for k, v in t.items()}, t["counts"])
