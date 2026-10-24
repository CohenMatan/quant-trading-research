"""TT chart discovery (D302) — Stage 1: restricted, outcome-blind WIKI chart sample, 2011-2016.

Rules (fixed in this file before it was first run; committed before any chart exists):
  Frame      the independent SEC reference frame (sec_reference.py), registrant-months 2011-01 .. 2016-12, with the
             frozen audit's identity classes (wiki_audit.classify, computed exactly as in the audit on 2010-2017).
  Eligible   class MATCHED only (AMBIGUOUS / UNRESOLVED-IDENTITY / MISSING excluded), ticker not among the tickers with
             an unexplained adjustment-ratio change anywhere in 2010-2017 (frozen definition 5.2 iv; the audit found 21),
             bars on all 252 reference sessions before the month's first session (decision date = the last of them), and
             a clean window: no invalid OHLC (raw or adjusted), no spike (5.2 ii), no split row, no dividend row whose
             adjustment factor disagrees by > 0.002, no missing field, in those 252 sessions.
  Strata     year (2011..2016) x public-float size tercile (frame, per month) x exit group of the registrant-month:
             ACQUIRED / FAILED / DELISTED-OTHER / STOPPED-FILING-ONLY (within 24 months before the last SEC filing) or
             CONTINUING (all other months).
  Targets    300 charts allocated to the strata in proportion to the SEC frame's registrant-months (all identity classes),
             largest remainder. Within a stratum the target is split as evenly as possible across terciles of the trailing
             252-session log return to the decision date (computed per year over eligible candidates; uses only data up to
             the decision date; behaviour coverage, not outcome selection).
  Draw       seeded (SEED) shuffle of each sub-stratum's candidates; at most ONE chart per registrant; strata processed
             smallest pool first. Shortfalls are reported as unfilled and never back-filled from another stratum.
  Output     data/chart_discovery/sample_mapping.json (local only: chart id -> cik, ticker, decision date, strata);
             research/tt/chart_discovery/SAMPLE_summary.json (committed: counts only + mapping SHA-256).
             Chart ids are assigned after a separate seeded shuffle so their order carries no stratum information.
No future price, return or outcome is used to choose a chart; exit groups only keep the frame's proportions.
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
sys.path.insert(0, str(ROOT / "research" / "tt" / "wiki_audit"))
import wiki_audit as wa  # noqa: E402

SEED = 20261024
TARGET = 300
N_BARS = 252
YEARS = range(2011, 2017)
LOCAL = ROOT / "data" / "chart_discovery"
MAPPING = LOCAL / "sample_mapping.json"
SUMMARY = HERE / "SAMPLE_summary.json"
EXIT_GROUPS = ("CONTINUING", "ACQUIRED", "FAILED", "DELISTED-OTHER", "STOPPED-FILING-ONLY")


def exit_group(r) -> str:
    if not r["leaver_month"]:
        return "CONTINUING"
    return {"UNKNOWN": "STOPPED-FILING-ONLY"}.get(r["exit_type"], r["exit_type"])


def bad_flags(d: pd.DataFrame) -> pd.Series:
    """Per-row defects (frozen audit definitions) on a ticker-sorted frame."""
    t = d["ticker"]
    same = t.eq(t.shift(1))
    split = d["split_ratio"].fillna(1.0)
    div = d["ex-dividend"].fillna(0.0)
    event = (split != 1.0) | (div > 0)
    r = np.log(d["adj_close"] / d["adj_close"].shift(1)).where(same)
    rn = r.shift(-1).where(t.eq(t.shift(-1)))
    spike = (r.abs() > 0.40) & (rn.abs() > 0.30) & (np.sign(r) == -np.sign(rn)) & ~event & ~event.shift(-1, fill_value=False)
    inval = d["volume"] < 0
    for pre in ("", "adj_"):
        o, h, lo, c = (d[pre + k] for k in ("open", "high", "low", "close"))
        inval |= (h < np.maximum(o, c)) | (lo > np.minimum(o, c)) | (h < lo) | (o <= 0) | (h <= 0) | (lo <= 0) | (c <= 0)
    ratio = d["adj_close"] / d["close"]
    divonly = (div > 0) & (split == 1.0) & same
    div_bad = divonly & ((ratio.shift(1) / ratio - (1 - div / d["close"].shift(1))).abs() > 0.002)
    nan = d[wa.COLUMNS[2:]].isna().any(axis=1)
    return (spike | inval | (split != 1.0) | div_bad | nan).fillna(True)


def unexplained_tickers(d: pd.DataFrame) -> set:
    t = d["ticker"]
    same = t.eq(t.shift(1))
    ev = (d["split_ratio"].fillna(1.0) != 1.0) | (d["ex-dividend"].fillna(0.0) > 0)
    ratio = d["adj_close"] / d["close"]
    unexp = ((ratio / ratio.shift(1) - 1).abs() > 1e-4) & same & ~ev
    return set(t[unexp])


def largest_remainder(weights: dict, total: int) -> dict:
    s = sum(weights.values())
    raw = {k: total * w / s for k, w in weights.items()}
    out = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: (-(raw[k] - out[k]), str(k)))[: total - sum(out.values())]:
        out[k] += 1
    return out


def build(path: Path):
    man = json.loads(wa.MANIFEST.read_text())
    if wa.sha256(path) != man["sha256"]:
        raise SystemExit("file SHA-256 does not match WIKI_MANIFEST.json")
    df, _ = wa.load_wiki(path)                                   # 2010-2017, as in the frozen audit
    sessions = wa.reference_sessions(df)
    fr = json.load(gzip.open(wa.FRAME, "rt"))
    bars, per_m = wa.month_bars(df, sessions)
    cl = wa.classify(fr["rows"], fr["prefix_ciks"], set(df["ticker"].unique()), bars, per_m)
    cl = [r for r in cl if r["ym"] // 100 in YEARS]
    excluded_adj = unexplained_tickers(df)
    # per-ticker session-position arrays (2010 .. 2016 only: nothing after 2016-12 is read below)
    d = df[(df["date"] <= "2016-12-31") & df["date"].isin(set(sessions))].reset_index(drop=True)
    d["bad"] = bad_flags(d).to_numpy()
    pos = {s: i for i, s in enumerate(sessions)}
    d["p"] = d["date"].map(pos)
    first_of = {}
    for s in sessions:
        first_of.setdefault(int(s[:4]) * 100 + int(s[5:7]), pos[s])
    per_t = {}
    for tk, g in d.groupby("ticker", sort=False):
        n = len(sessions)
        have = np.zeros(n + 1, np.int64)
        bad = np.zeros(n + 1, np.int64)
        adj = np.full(n, np.nan)
        have[g["p"].to_numpy() + 1] = 1
        bad[g["p"].to_numpy() + 1] = g["bad"].to_numpy().astype(int)
        adj[g["p"].to_numpy()] = g["adj_close"].to_numpy()
        per_t[tk] = (np.cumsum(have), np.cumsum(bad), adj)
    reasons = Counter()
    cands = []
    for r in cl:
        if r["cls"] != "MATCHED":
            reasons[f"identity:{r['cls']}"] += 1
            continue
        if r["prefix"] in excluded_adj:
            reasons["adjustment_defect_ticker"] += 1
            continue
        f = first_of.get(r["ym"])
        h, b, adj = per_t[r["prefix"]]
        if f is None or f < N_BARS or h[f] - h[f - N_BARS] < N_BARS:
            reasons["history_<252_bars"] += 1
            continue
        if b[f] - b[f - N_BARS] > 0:
            reasons["window_defect"] += 1
            continue
        cands.append({"cik": r["cik"], "ticker": r["prefix"], "ym": r["ym"], "year": r["ym"] // 100,
                      "size": r["size_tercile"], "exit": exit_group(r), "decision_date": sessions[f - 1],
                      "trail": float(np.log(adj[f - 1] / adj[f - N_BARS]))})
    # trailing-return terciles per year (eligible candidates only)
    for y in YEARS:
        vals = np.array([c["trail"] for c in cands if c["year"] == y])
        q1, q2 = np.quantile(vals, [1 / 3, 2 / 3])
        for c in cands:
            if c["year"] == y:
                c["trail_t"] = 1 if c["trail"] <= q1 else (2 if c["trail"] <= q2 else 3)
    # targets from the SEC frame (all identity classes)
    pop = Counter((r["ym"] // 100, r["size_tercile"], exit_group(r)) for r in cl)
    targets = largest_remainder(dict(pop), TARGET)
    pool = defaultdict(list)
    for c in cands:
        pool[(c["year"], c["size"], c["exit"], c["trail_t"])].append(c)
    rng = random.Random(SEED)
    used, chosen, cells = set(), [], {}
    order = sorted(targets, key=lambda k: (sum(len(pool[k + (t,)]) for t in (1, 2, 3)), k))
    for k in order:
        tg = targets[k]
        sub = {t: tg // 3 for t in (1, 2, 3)}
        extra = [1, 2, 3]
        rng.shuffle(extra)
        for t in extra[: tg % 3]:
            sub[t] += 1
        got = 0
        for t in (1, 2, 3):
            lst = sorted(pool[k + (t,)], key=lambda c: (c["cik"], c["ym"]))
            rng.shuffle(lst)
            n = 0
            for c in lst:
                if n >= sub[t]:
                    break
                if c["cik"] in used:
                    continue
                used.add(c["cik"])
                chosen.append(c)
                n += 1
            got += n
        cells["|".join(map(str, k))] = {"target": tg, "filled": got,
                                         "candidates": sum(len(pool[k + (t,)]) for t in (1, 2, 3))}
    rng2 = random.Random(SEED + 1)
    rng2.shuffle(chosen)
    for i, c in enumerate(chosen, 1):
        c["chart_id"] = f"C{i:03d}"
    LOCAL.mkdir(parents=True, exist_ok=True)
    MAPPING.write_text(json.dumps(chosen, indent=1))
    by = lambda key: dict(sorted(Counter(str(c[key]) for c in chosen).items()))
    tgt_exit = Counter()
    for k, v in targets.items():
        tgt_exit[k[2]] += v
    summary = {
        "decision": "D302", "seed": SEED, "target": TARGET, "sampled": len(chosen),
        "frame_registrant_months_2011_2016": len(cl), "eligible_candidates": len(cands),
        "eligible_registrants": len({c["cik"] for c in cands}),
        "exclusions": dict(reasons), "adjustment_defect_tickers": len(excluded_adj),
        "by_year": by("year"), "by_size_tercile": by("size"), "by_exit_group": by("exit"),
        "by_trailing_return_tercile": by("trail_t"),
        "target_by_exit_group": dict(tgt_exit),
        "unfilled_cells": {k: v for k, v in cells.items() if v["filled"] < v["target"]},
        "cells": cells, "mapping_sha256": hashlib.sha256(MAPPING.read_bytes()).hexdigest(),
        "note": "Counts only. The chart id -> company/date mapping stays local (data/chart_discovery, git-ignored).",
    }
    SUMMARY.write_text(json.dumps(summary, indent=1) + "\n")
    out = {k: summary[k] for k in ("sampled", "eligible_candidates", "eligible_registrants", "exclusions",
                                   "adjustment_defect_tickers", "by_year", "by_size_tercile", "by_exit_group",
                                   "target_by_exit_group", "unfilled_cells")}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    build(Path(sys.argv[1]))
