"""Render the size-proxy evaluation (X953 runs) into tables and CSVs.

    python -m qresearch.proxy_eval E953-01 E953-02 E953-03
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd

from . import config, results

SECTORS = {"101": "Basic Materials", "102": "Consumer Cyclical", "103": "Financial Services",
           "104": "Real Estate", "205": "Consumer Defensive", "206": "Healthcare", "207": "Utilities",
           "308": "Communication Services", "309": "Energy", "310": "Industrials", "311": "Technology",
           "0": "Unclassified", "none": "No fundamentals"}


def parse(exp_id: str) -> dict:
    lines = (config.EXPERIMENTS_DIR / exp_id / "messages.txt").read_text().splitlines()
    y, c, s, f, x, samples, track, chk = [], [], {}, [], [], [], {}, {}
    for ln in lines:
        tag, _, rest = ln.partition("|")
        if tag == "QRPX_Y":
            yr, v, m, nP, nR, tp, fp, fn, f1lo, f1hi = rest.split("|")
            y.append(dict(year=yr, variant=v, months=int(m), nP=int(nP), nR=int(nR), TP=int(tp), FP=int(fp),
                          FN=int(fn), f1_min=float(f1lo), f1_max=float(f1hi)))
        elif tag == "QRPX_C":
            yr, p, js = rest.split("|", 2)
            c.append(dict(year=yr, primary=p, **json.loads(js)))
        elif tag == "QRPX_S":
            yr, js = rest.split("|", 1)
            s[yr] = json.loads(js)
        elif tag == "QRPX_F":
            d, js = rest.split("|", 1)
            row = {"date": d}
            for g, (ret, n, n_all) in json.loads(js).items():
                row[g] = ret
                row[g + "_n"] = n
                row[g + "_all"] = n_all
            f.append(row)
        elif tag == "QRPX_X":
            yr, v, ticks = rest.split("|", 2)
            x.append(dict(year=yr, variant=v, tickers=ticks))
        elif tag == "QRPX_SAMPLE":
            d, n, cells = rest.split("|", 2)
            for cell in cells.split(";"):
                t, sid, adv, twin, cs = cell.split(":")
                samples.append(dict(date=d, n_fp_nofund=int(n[2:]), ticker=t, sid=sid, adv_musd=float(adv),
                                    twin=float(twin), corr_spy=float(cs) if cs != "nan" else float("nan")))
        elif tag == "QRPX_T":
            track = json.loads(rest)
        elif tag == "QRPX_CHK":
            chk = json.loads(rest)
    return dict(y=pd.DataFrame(y), c=pd.DataFrame(c), s=s, f=pd.DataFrame(f), x=pd.DataFrame(x),
                samples=pd.DataFrame(samples), track=track, chk=chk)


def agreement(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("variant")[["months", "nP", "nR", "TP", "FP", "FN"]].sum()
    g["f1_min"] = df.groupby("variant")["f1_min"].min()
    return _scores(g)


def _scores(g: pd.DataFrame) -> pd.DataFrame:
    g = g.copy()
    g["precision"] = g.TP / (g.TP + g.FP)
    g["recall"] = g.TP / (g.TP + g.FN)
    g["F1"] = 2 * g.TP / (2 * g.TP + g.FP + g.FN)
    g["jaccard"] = g.TP / (g.TP + g.FP + g.FN)
    for k in ("nP", "nR", "FP", "FN", "TP"):
        g[k + "_per_month"] = g[k] / g["months"]
    return g


def by_year(df: pd.DataFrame, variants) -> pd.DataFrame:
    d = df[df.variant.isin(variants)].set_index(["year", "variant"])
    return _scores(d)


def forward_summary(f: pd.DataFrame, primaries=("A1000", "B90", "C20")) -> pd.DataFrame:
    """Monthly EW returns: annualised mean of each group and of its difference to the reference."""
    rows = []
    for g in ["R"] + [f"{p}_{k}" for p in primaries for k in ("P", "PnotR", "RnotP")]:
        if g not in f:
            continue
        r = f[g].astype(float)
        d = (f[g] - f["R"]).astype(float)
        n = int(d.notna().sum())
        rows.append(dict(group=g, months=int(r.notna().sum()), ann_mean=r.mean() * 12,
                         ann_compound=(1 + r).prod() ** (12 / max(r.notna().sum(), 1)) - 1,
                         diff_vs_R_ann=d.mean() * 12,
                         t_stat=(d.mean() / (d.std(ddof=1) / math.sqrt(n))) if n > 2 and d.std(ddof=1) > 0 else float("nan"),
                         avg_members=f.get(g + "_all", pd.Series(dtype=float)).mean(),
                         avg_missing_history=(f.get(g + "_all") - f.get(g + "_n")).mean() if g + "_all" in f else float("nan")))
    return pd.DataFrame(rows)


def sector_table(s: dict, years, primaries=("A1000", "B90", "C20")) -> pd.DataFrame:
    tot = {}
    for yr in years:
        for grp, cnt in s.get(yr, {}).items():
            for k, n in cnt.items():
                tot.setdefault(grp, {}).setdefault(k, 0)
                tot[grp][k] += n
    df = pd.DataFrame(tot).fillna(0)
    share = df / df.sum()
    share.index = [SECTORS.get(i, i) for i in share.index]
    return share


def main(argv=None) -> int:
    ids = argv or sys.argv[1:] or ["E953-01", "E953-02", "E953-03"]
    out = config.REPO_ROOT / "docs" / "data" / "size_proxy"
    out.mkdir(parents=True, exist_ok=True)
    for e in ids:
        d = parse(e)
        d["y"].to_csv(out / f"{e}_yearly_counts.csv", index=False)
        if len(d["f"]):
            d["f"].to_csv(out / f"{e}_forward_returns_monthly.csv", index=False)
        if len(d["samples"]):
            d["samples"].to_csv(out / f"{e}_fp_nofund_sample.csv", index=False)
        agreement(d["y"]).round(4).to_csv(out / f"{e}_agreement_by_variant.csv")
        print(e, "check", d["chk"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
