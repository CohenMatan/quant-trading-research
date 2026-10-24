"""WIKI Prices data-quality and composition audit (D298; frozen protocol WIKI_AUDIT_protocol.md).

Usage:  python research/tt/wiki_audit/wiki_audit.py data/wiki/WIKI_PRICES.csv

- Refuses to run unless the file's SHA-256 equals WIKI_MANIFEST.json (written when the file is acquired).
- Reads only 2010-01-04 .. 2017-12-29 rows. Every other row is dropped while the file is read; only the total row
  count is kept for the manifest.
- Prints and writes aggregates only (WIKI_AUDIT_result.json). No row, per-ticker price series or chart is ever
  printed.
- The SEC reference frame comes from sec_reference.py (run it first).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
MANIFEST = HERE / "WIKI_MANIFEST.json"
RESULT = HERE / "WIKI_AUDIT_result.json"
FRAME = ROOT / "data" / "wiki_audit" / "sec_frame.json.gz"
COMPANYFACTS = ROOT / "data" / "sec_cache" / "data.sec.gov" / "api" / "xbrl" / "companyfacts"

START, END = "2010-01-04", "2017-12-29"
COLUMNS = ["ticker", "date", "open", "high", "low", "close", "volume", "ex-dividend", "split_ratio",
           "adj_open", "adj_high", "adj_low", "adj_close", "adj_volume"]
NYSE_SESSIONS = {2010: 252, 2011: 252, 2012: 250, 2013: 252, 2014: 252, 2015: 252, 2016: 252, 2017: 251}
SPLIT_SEED = 20261024
EXIT_TYPES = ("FAILED", "ACQUIRED", "DELISTED-OTHER", "UNKNOWN")


# ---------------------------------------------------------------- loading
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_wiki(path: Path, chunksize: int = 2_000_000) -> tuple[pd.DataFrame, int]:
    """Window rows only, plus the file's total row count."""
    head = pd.read_csv(path, nrows=0).columns.tolist()
    if head != COLUMNS:
        raise SystemExit(f"unexpected schema: {head}")
    parts, total = [], 0
    for ch in pd.read_csv(path, chunksize=chunksize, dtype={"ticker": str, "date": str}):
        total += len(ch)
        ch = ch[(ch["date"] >= START) & (ch["date"] <= END)]
        if len(ch):
            parts.append(ch)
    df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=COLUMNS)
    df["ticker"] = df["ticker"].str.upper()
    df = df.sort_values(["ticker", "date"], kind="mergesort").reset_index(drop=True)
    return df, total


# ---------------------------------------------------------------- calendar and inventory
def reference_sessions(df: pd.DataFrame) -> list[str]:
    """Dates on which >= 50% of the tickers with any bar in that calendar year have a bar (protocol 4)."""
    y = df["date"].str[:4]
    active = df.groupby(y)["ticker"].nunique()
    per_day = df.groupby("date")["ticker"].nunique()
    return sorted(d for d, n in per_day.items() if n >= 0.5 * active[d[:4]])


def calendar_check(sessions: list[str]) -> dict:
    c = Counter(int(d[:4]) for d in sessions)
    diff = {y: c.get(y, 0) - n for y, n in NYSE_SESSIONS.items()}
    return {"sessions_by_year": dict(sorted(c.items())), "diff_vs_nyse": diff,
            "ok": all(abs(v) <= 2 for v in diff.values())}


def inventory(df: pd.DataFrame) -> dict:
    y = df["date"].str[:4]
    g = df.groupby(y)
    return {"tickers_by_year": g["ticker"].nunique().to_dict(), "rows_by_year": g.size().to_dict(),
            "tickers_total": int(df["ticker"].nunique()), "rows_total": int(len(df)),
            "rows_any_nan_share": float(df[COLUMNS[2:]].isna().any(axis=1).mean()) if len(df) else 0.0}


# ---------------------------------------------------------------- bar integrity (protocol 5.2)
def integrity(df: pd.DataFrame, sessions: list[str]) -> dict:
    sess = pd.Index(sessions)
    pos = pd.Series(np.arange(len(sess)), index=sess)
    d = df[df["date"].isin(sess)].copy()
    d["p"] = pos.reindex(d["date"]).to_numpy()
    life = (d.groupby("ticker")["p"].max() - d.groupby("ticker")["p"].min() + 1).sum()
    missing = 1 - len(d) / life if life else 0.0
    t = d["ticker"]
    same = t.eq(t.shift(1))
    split = d["split_ratio"].fillna(1.0)
    div = d["ex-dividend"].fillna(0.0)
    event = (split != 1.0) | (div > 0)
    r = np.log(d["adj_close"] / d["adj_close"].shift(1)).where(same)
    rn = r.shift(-1).where(t.eq(t.shift(-1)))
    ev_next = event.shift(-1, fill_value=False)
    spike = (r.abs() > 0.40) & (rn.abs() > 0.30) & (np.sign(r) == -np.sign(rn)) & ~event & ~ev_next
    inval = pd.Series(False, index=d.index)
    for pre in ("", "adj_"):
        o, h, lo, c = (d[pre + k] for k in ("open", "high", "low", "close"))
        inval |= (h < np.maximum(o, c)) | (lo > np.minimum(o, c)) | (h < lo) | (o <= 0) | (h <= 0) | (lo <= 0) | (c <= 0)
    inval |= d["volume"] < 0
    ratio = d["adj_close"] / d["close"]
    chg = ((ratio / ratio.shift(1) - 1).abs() > 1e-4) & same
    explained = chg & event
    no_change_events = event & same & ~chg
    divonly = (div > 0) & (split == 1.0) & same
    implied = 1 - div / d["close"].shift(1)
    observed = ratio.shift(1) / ratio
    div_ok = (observed - implied).abs() <= 0.002
    n = len(d)
    return {
        "ticker_sessions": int(n),
        "missing_share": float(missing),
        "spike_share": float(spike.sum() / n) if n else 0.0,
        "invalid_ohlc_share": float(inval.sum() / n) if n else 0.0,
        "ratio_changes": int(chg.sum()), "ratio_changes_explained_share": float(explained.sum() / chg.sum()) if chg.sum() else 1.0,
        "events_without_ratio_change": int(no_change_events.sum()),
        "dividend_events": int(divonly.sum()),
        "dividend_factor_agree_share": float((div_ok & divonly).sum() / divonly.sum()) if divonly.sum() else 1.0,
        "split_events": int(((split != 1.0) & same).sum()),
        "spike_share_by_year": spike.groupby(d["date"].str[:4]).mean().to_dict(),
    }


# ---------------------------------------------------------------- linking to the SEC frame (protocol 3)
def month_bars(df: pd.DataFrame, sessions: list[str]) -> tuple[dict, dict]:
    """(ticker, ym) -> bars on reference sessions; ym -> number of reference sessions."""
    per_m = Counter(int(x[:4]) * 100 + int(x[5:7]) for x in sessions)
    d = df[df["date"].isin(set(sessions))]
    k = d["date"].str[:4].astype(int) * 100 + d["date"].str[5:7].astype(int)
    bars = d.groupby([d["ticker"], k]).size().to_dict()
    return bars, dict(per_m)


def classify(frame_rows: list[dict], prefix_ciks: dict, wiki_tickers: set, bars: dict, per_m: dict) -> list[dict]:
    out = []
    for r in frame_rows:
        p, m = r["prefix"], r["ym"]
        reuse = len(prefix_ciks.get(p, [])) > 1
        if r["prefix_shared"] or (p in wiki_tickers and reuse):
            cls = "AMBIGUOUS"
        elif p not in wiki_tickers:
            cls = "UNRESOLVED-IDENTITY"
        else:
            b = bars.get((p, m), 0)
            need = per_m.get(m, 0)
            cls = "MATCHED" if need and b >= 0.9 * need else ("MISSING-OUT-OF-LIFE" if b == 0 else "MISSING-PARTIAL")
        out.append({**r, "cls": cls})
    return out


def cov(rows) -> dict:
    c = Counter(r["cls"] for r in rows)
    nonamb = len(rows) - c["AMBIGUOUS"]
    resolved = c["MATCHED"] + c["MISSING-OUT-OF-LIFE"] + c["MISSING-PARTIAL"]
    return {"n": len(rows), "registrants": len({r["cik"] for r in rows}), "classes": dict(c),
            "strict": c["MATCHED"] / nonamb if nonamb else None,
            "resolved": c["MATCHED"] / resolved if resolved else None}


def composition(cl: list[dict]) -> dict:
    by_year = defaultdict(list)
    for r in cl:
        by_year[r["ym"] // 100].append(r)
    leavers = [r for r in cl if r["leaver_month"]]
    stayers = [r for r in cl if not r["left"]]
    by_type = defaultdict(list)
    for r in leavers:
        by_type[r["exit_type"]].append(r)
    strata = defaultdict(list)
    for r in cl:
        strata[f"{r['ym'] // 100}|size{r['size_tercile']}"].append(r)
        if r["fin"]:
            strata["category|financial_reit"].append(r)
        if r["foreign_name"]:
            strata["category|foreign_style_name"].append(r)
    return {"overall": cov(cl), "by_year": {y: cov(v) for y, v in sorted(by_year.items())},
            "leavers": cov(leavers), "non_leavers": cov(stayers),
            "leavers_by_exit_type": {k: cov(v) for k, v in by_type.items()},
            "strata": {k: cov(v) for k, v in sorted(strata.items())}}


# ---------------------------------------------------------------- liquidity (WIKI only) and chart readiness
def liquidity_terciles(df: pd.DataFrame) -> dict:
    """Per year: tercile cut points of the median 63-session raw dollar volume (raw close x raw volume)."""
    dv = (df["close"] * df["volume"]).rename("dv")
    med = dv.groupby([df["ticker"], df["date"].str[:4]]).median()
    out = {}
    for y, s in med.groupby(level=1):
        q = s.quantile([1 / 3, 2 / 3]).to_list()
        out[y] = {"n_tickers": int(s.size), "cut_1_3": float(q[0]), "cut_2_3": float(q[1])}
    return out


def chart_ready(cl: list[dict], df: pd.DataFrame, sessions: list[str]) -> list[dict]:
    """MATCHED registrant-months with bars on all 252 reference sessions before m's first session (protocol 5.5)."""
    pos = {d: i for i, d in enumerate(sessions)}
    first_of = {}
    for d in sessions:
        k = int(d[:4]) * 100 + int(d[5:7])
        first_of.setdefault(k, pos[d])
    have = defaultdict(set)
    for tk, d in zip(df["ticker"], df["date"]):
        if d in pos:
            have[tk].add(pos[d])
    out = []
    for r in cl:
        if r["cls"] != "MATCHED":
            continue
        f = first_of.get(r["ym"])
        if f is None or f < 252:
            continue
        s = have[r["prefix"]]
        if all(i in s for i in range(f - 252, f)):
            out.append(r)
    return out


# ---------------------------------------------------------------- split cross-check (protocol 5.3)
def cover_shares(cik: int) -> list[tuple[str, float]]:
    p = COMPANYFACTS / f"CIK{cik:010d}.json.gz"
    if not p.exists():
        return []
    d = json.load(gzip.open(p, "rt"))
    f = d.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {}).get("units", {}).get("shares", [])
    return sorted({(x["end"], float(x["val"])) for x in f if x.get("val")})


def split_check(df: pd.DataFrame, cl: list[dict], shares_of=cover_shares) -> dict:
    tick_cik = {}
    for r in cl:
        if r["cls"] == "MATCHED":
            tick_cik.setdefault(r["prefix"], r["cik"])
    s = df[(df["split_ratio"].fillna(1.0) != 1.0) & df["ticker"].isin(tick_cik)][["ticker", "date", "split_ratio"]]
    ev = sorted(map(tuple, s.to_numpy().tolist()))
    random.Random(SPLIT_SEED).shuffle(ev)
    by_t = defaultdict(list)
    for tk, d, _ in ev:
        by_t[tk].append(d)
    agree = tested = 0
    for tk, d, ratio in ev:
        if tested >= 100:
            break
        sh = shares_of(tick_cik[tk])
        before = [x for x in sh if x[0] < d and (pd.Timestamp(d) - pd.Timestamp(x[0])).days <= 400]
        after = [x for x in sh if x[0] >= d and (pd.Timestamp(x[0]) - pd.Timestamp(d)).days <= 400]
        if not before or not after:
            continue
        b, a = before[-1], after[0]
        if any(b[0] < o < a[0] and o != d for o in by_t[tk]):
            continue
        tested += 1
        agree += abs((a[1] / b[1]) / float(ratio) - 1) <= 0.15
    return {"events_in_window": len(ev), "tested": tested, "agree": agree,
            "agree_share": agree / tested if tested else None}


# ---------------------------------------------------------------- gates (protocol 6)
def g(pass_, fail_):
    return "FAIL" if fail_ else ("PASS" if pass_ else "INCONCLUSIVE")


def gates(comp: dict, integ: dict, cal: dict, splits: dict, ready: list[dict]) -> dict:
    out = {}
    yr = {y: v["strict"] for y, v in comp["by_year"].items() if v["strict"] is not None}
    ov = comp["overall"]["strict"] or 0.0
    out["A1"] = g(ov >= 0.90 and all(v >= 0.85 for v in yr.values()), ov < 0.75 or any(v < 0.70 for v in yr.values()))
    big = {k: v for k, v in comp["leavers_by_exit_type"].items() if v["registrants"] >= 20}
    lv, st = comp["leavers"]["strict"], comp["non_leavers"]["strict"]
    gap = (st - lv) if (lv is not None and st is not None) else None
    if not big:
        out["A2"] = "INCONCLUSIVE"
    else:
        out["A2"] = g(all(v["strict"] >= 0.80 for v in big.values()) and gap is not None and gap <= 0.10,
                      any(v["strict"] < 0.65 for v in big.values()) or (gap is not None and gap > 0.20))
    st_big = [v["strict"] for v in comp["strata"].values() if v["registrants"] >= 50 and v["strict"] is not None]
    out["A3"] = g(all(v >= 0.70 for v in st_big), any(v < 0.50 for v in st_big))
    c = comp["overall"]["classes"]
    n = comp["overall"]["n"]
    amb = c.get("AMBIGUOUS", 0) / n if n else 1.0
    unres = c.get("UNRESOLVED-IDENTITY", 0) / (n - c.get("AMBIGUOUS", 0)) if n - c.get("AMBIGUOUS", 0) else 1.0
    out["A4"] = g(amb <= 0.02 and unres <= 0.10, amb > 0.05 or unres > 0.20)
    if not cal["ok"] or (splits["tested"] or 0) < 30:
        out["A5"] = "INCONCLUSIVE"
    else:
        sa = splits["agree_share"]
        pass5 = (integ["missing_share"] <= 0.005 and integ["spike_share"] <= 0.001 and integ["invalid_ohlc_share"] <= 0.0001
                 and integ["ratio_changes_explained_share"] >= 0.995 and integ["dividend_factor_agree_share"] >= 0.95 and sa >= 0.95)
        fail5 = (integ["missing_share"] > 0.025 or integ["spike_share"] > 0.005 or integ["invalid_ohlc_share"] > 0.0005
                 or (1 - integ["ratio_changes_explained_share"]) > 0.025 or (1 - integ["dividend_factor_agree_share"]) > 0.25
                 or sa < 0.85)
        out["A5"] = g(pass5, fail5)
    base = [yr[y] for y in ("2014", "2015", "2016") if y in yr] or [yr[y] for y in (2014, 2015, 2016) if y in yr]
    y17 = yr.get("2017", yr.get(2017))
    if base and y17 is not None:
        drop = sum(base) / len(base) - y17
        out["A6"] = g(drop <= 0.02, drop > 0.05)
    else:
        out["A6"] = "INCONCLUSIVE"
    cells = defaultdict(set)
    for r in ready:
        cells[(r["ym"] // 100, r["size_tercile"])].add(r["cik"])
    lv_ready = {r["cik"] for r in ready if r["leaver_month"]}
    need = [(y, t) for y in range(2011, 2018) for t in (1, 2, 3)]
    sizes = [len(cells[k]) for k in need]
    out["A7"] = g(all(s >= 20 for s in sizes) and len(lv_ready) >= 30, any(s < 10 for s in sizes) or len(lv_ready) < 10)
    vals = list(out.values())
    out["overall"] = ("INSUFFICIENT" if "FAIL" in vals else
                      "SUFFICIENT FOR EXPLORATORY CHART RESEARCH" if all(v == "PASS" for v in vals) else "INCONCLUSIVE")
    out["_a7_cells_min"] = min(sizes) if sizes else 0
    out["_a7_leaver_registrants"] = len(lv_ready)
    return out


def main(path: str):
    p = Path(path)
    man = json.loads(MANIFEST.read_text())
    if sha256(p) != man["sha256"]:
        raise SystemExit("file SHA-256 does not match WIKI_MANIFEST.json")
    pin = json.loads((HERE / "PROTOCOL_PIN.json").read_text())
    if hashlib.sha256((ROOT / pin["protocol"]).read_bytes()).hexdigest() != pin["sha256"]:
        raise SystemExit("protocol changed since it was frozen")
    df, total = load_wiki(p)
    if total != man.get("row_count", total):
        raise SystemExit("row count differs from the manifest")
    sessions = reference_sessions(df)
    cal = calendar_check(sessions)
    fr = json.load(gzip.open(FRAME, "rt"))
    bars, per_m = month_bars(df, sessions)
    cl = classify(fr["rows"], fr["prefix_ciks"], set(df["ticker"].unique()), bars, per_m)
    comp = composition(cl)
    matched = {r["prefix"] for r in cl if r["cls"] == "MATCHED"}
    integ = integrity(df[df["ticker"].isin(matched)], sessions)      # protocol 6 A5: MATCHED tickers
    splits = split_check(df, cl)
    ready = chart_ready(cl, df, sessions)
    res = {"protocol_sha256": pin["sha256"], "file_sha256": man["sha256"], "window": [START, END],
           "inventory": inventory(df), "calendar": cal, "integrity": integ, "liquidity_terciles": liquidity_terciles(df),
           "composition": comp, "split_check": splits,
           "chart_ready": {"registrant_months": len(ready), "registrants": len({r['cik'] for r in ready})},
           "gates": gates(comp, integ, cal, splits, ready)}
    RESULT.write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res["gates"], indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
