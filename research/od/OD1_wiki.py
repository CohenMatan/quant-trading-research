"""OD-1 WIKI candlestick and blinded visual study (owner D308; research/od/OD1_protocol.md section 6). LOCAL ONLY:
WIKI rows, labels per stock and chart images stay under data/ (git-ignored); only aggregates are committed.

Fixed before any WIKI forward return was computed (this file is committed before `numeric` / `sample` run):
  Frame        the TT chart-discovery frame: SEC reference-frame registrant-months of the decision month with identity
               class MATCHED (wiki_audit.classify), ticker not among the adjustment-defect tickers
               (sample.unexplained_tickers), 252 clean bars (sample.bad_flags) ending at the decision session.
  Decisions    the last reference session of each month 2011-01 .. 2016-12 (72 reviews); nothing before 2010 is read.
  Labels       h = 3 / 12 months: adjusted close at the decision session of month m + h over the decision close - 1;
               a ticker without a bar there takes its last adjusted close before it (left = 1). Labels end <= 2017-12.
               SPY = E900-08 equity (98% SPY) on the same sessions; EX = TR - SPY.
  Features     K1..K8 (protocol table) on adjusted OHLC; controls MOM12_1, VOL63, BETA (252 sessions vs E900-08),
               SIZE = SEC public float; FF12 dummies by SEC SIC.
  Statistics   per feature, h = 12 (and 3): decile mean / median EX, p(EX > 0), shares of W / L; per-review partial rank
               IC (feature and EX ranks residualised on control ranks + FF12 dummies, qr_od1.partial_ic), NW t with
               lag h - 1 (descriptive).
  Consistency  per-review universe mean TR (h = 3 / 12) vs the QuantConnect aggregate (E808 'consistency' section);
               NOT CONSISTENT if the h = 12 correlation < 0.8 or mean |difference| > 0.03.
  Visual test  seed 20261025: 40 W, 40 L, 40 M (h = 12 EX groups within review: top 10% / bottom 10% / 40-60%), at most
               one per registrant per group; shuffled with seed + 1 into ids V001..V120; rendered with the frozen
               chart-discovery renderer; predictions recorded and COMMITTED before `unblind` (which refuses otherwise).

    python research/od/OD1_wiki.py numeric data/wiki/<file>.csv
    python research/od/OD1_wiki.py sample  data/wiki/<file>.csv
    python research/od/OD1_wiki.py record  < lines "V001|OUT|tag,tag"     (OUT / NEU / UND)
    python research/od/OD1_wiki.py consistency E808-01
    python research/od/OD1_wiki.py unblind
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "tt" / "wiki_audit"))
sys.path.insert(0, str(ROOT / "research" / "tt" / "chart_discovery"))
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
import wiki_audit as wa  # noqa: E402
import sample as cds  # noqa: E402
import qr_od1 as O  # noqa: E402
import qr_os1 as OS  # noqa: E402

SEED = 20261025
N_PER = 40
L = 252
MONTHS = [y * 100 + m for y in range(2011, 2017) for m in range(1, 13)]
KFEAT = ("CLV21", "GAPUP63", "GAPDN63", "BIGBODY63", "UPWICK21", "LOWICK21", "ATRPCT21", "ATRCHG")
CONTROLS = ("MOM12_1", "VOL63", "BETA", "SIZE")
LOCAL = ROOT / "data" / "od1_wiki"
PANEL = LOCAL / "panel.npz"
MAPPING = LOCAL / "visual_mapping.json"
CHARTS = LOCAL / "charts"
NUMERIC = HERE / "OD1_wiki_numeric.json"
VIS_MANIFEST = HERE / "OD1_visual_manifest.json"
PRED = HERE / "OD1_visual_predictions.jsonl"
VIS_RESULT = HERE / "OD1_visual_result.json"
CONSIST = HERE / "OD1_wiki_consistency.json"
TAGS = {"UPTREND", "DOWNTREND", "SIDEWAYS", "NEAR_HIGH", "NEAR_LOW", "ABOVE_MAS", "BELOW_MAS", "BREAKOUT", "BREAKDOWN",
        "PULLBACK", "BASE", "EXTENDED", "V_RECOVERY", "GAP_UP", "GAP_DOWN", "HIGH_VOL", "LOW_VOL", "VOL_SPIKE",
        "TIGHT", "CHOPPY", "NONE"}


def _check_file(path: Path):
    man = json.loads(wa.MANIFEST.read_text())
    if wa.sha256(path) != man["sha256"]:
        raise SystemExit("file SHA-256 does not match WIKI_MANIFEST.json")


def spy_series(sessions):
    eq = pd.read_csv(ROOT / "experiments" / "E900-08" / "equity.csv.gz", usecols=["date", "equity"])
    s = eq.set_index("date")["equity"].reindex(sessions).ffill()
    return s.to_numpy(float)


def k_features(o, h, lo, c):
    """K1..K8 for arrays (n, >= 127) of adjusted OHLC ending at the decision session (last column)."""
    with np.errstate(all="ignore"):
        rng = h - lo
        ok = rng > 0
        clv = np.where(ok, (c - lo) / rng, np.nan)
        upw = np.where(ok, (h - np.maximum(o, c)) / rng, np.nan)
        low = np.where(ok, (np.minimum(o, c) - lo) / rng, np.nan)
        pc = c[:, :-1]
        gap = o[:, 1:] / pc
        up = c[:, 1:] > pc
        tr = np.maximum(rng[:, 1:], np.maximum(np.abs(h[:, 1:] - pc), np.abs(lo[:, 1:] - pc)))
        body = np.abs(c - o) / o
        atr21 = np.nanmean(tr[:, -21:], axis=1)
        atr126 = np.nanmean(tr[:, -126:], axis=1)
        return dict(
            CLV21=np.nanmean(clv[:, -21:], axis=1),
            GAPUP63=((gap[:, -63:] >= 1.03) & up[:, -63:]).sum(axis=1).astype(float),
            GAPDN63=(gap[:, -63:] <= 0.97).sum(axis=1).astype(float),
            BIGBODY63=(body[:, -63:] >= 0.04).sum(axis=1).astype(float),
            UPWICK21=np.nanmean(upw[:, -21:], axis=1),
            LOWICK21=np.nanmean(low[:, -21:], axis=1),
            ATRPCT21=atr21 / c[:, -1],
            ATRCHG=atr21 / atr126)


def controls(c, spy):
    with np.errstate(all="ignore"):
        r = np.diff(np.log(c), axis=1)
        sr = np.diff(np.log(spy))
        mom = c[:, -22] / c[:, -L] - 1
        vol = np.std(r[:, -63:], axis=1, ddof=1)
        sc = sr - sr.mean()
        beta = ((r - r.mean(axis=1, keepdims=True)) @ sc) / (sc @ sc)
        return mom, vol, beta


def build(path: Path):
    """Frame, features and labels (local panel)."""
    _check_file(path)
    df, _ = wa.load_wiki(path)
    sessions = wa.reference_sessions(df)
    pos = {s: i for i, s in enumerate(sessions)}
    last_of = {}
    for i, s in enumerate(sessions):
        last_of[int(s[:4]) * 100 + int(s[5:7])] = i
    fr = json.load(gzip.open(wa.FRAME, "rt"))
    bars, per_m = wa.month_bars(df, sessions)
    cl = wa.classify(fr["rows"], fr["prefix_ciks"], set(df["ticker"].unique()), bars, per_m)
    excluded = cds.unexplained_tickers(df)
    d = df[df["date"].isin(set(sessions))].reset_index(drop=True)
    d["bad"] = cds.bad_flags(d).to_numpy()
    tick = sorted(d["ticker"].unique())
    ti = {t: j for j, t in enumerate(tick)}
    n, S = len(tick), len(sessions)
    A = {k: np.full((n, S), np.nan) for k in ("adj_open", "adj_high", "adj_low", "adj_close")}
    BAD = np.ones((n, S), bool)
    rr, cc = d["ticker"].map(ti).to_numpy(), d["date"].map(pos).to_numpy()
    for k in A:
        A[k][rr, cc] = d[k].to_numpy(float)
    BAD[rr, cc] = d["bad"].to_numpy(bool)
    spy = spy_series(sessions)
    rows = []
    for ym in MONTHS:
        dd = last_of[ym]
        cand = [r for r in cl if r["ym"] == ym and r["cls"] == "MATCHED" and r["prefix"] not in excluded]
        if dd < L - 1 or not cand:
            continue
        idx = np.array([ti[r["prefix"]] for r in cand if r["prefix"] in ti])
        cand = [r for r in cand if r["prefix"] in ti]
        w = slice(dd - L + 1, dd + 1)
        clean = (~BAD[idx, w]).all(axis=1) & np.isfinite(A["adj_close"][idx, w]).all(axis=1)
        idx = idx[clean]
        cand = [r for r, k in zip(cand, clean) if k]
        o, h, lo, c = (A[k][idx, w] for k in ("adj_open", "adj_high", "adj_low", "adj_close"))
        kf = k_features(o, h, lo, c)
        mom, vol, beta = controls(c, spy[w])
        lab = {}
        for hz in (3, 12):
            q = (ym // 100) * 12 + ym % 100 - 1 + hz
            e = last_of[(q // 12) * 100 + q % 12 + 1]
            seg = A["adj_close"][idx, dd:e + 1]
            have = np.isfinite(seg)
            lastj = np.where(have.any(axis=1), seg.shape[1] - 1 - np.argmax(have[:, ::-1], axis=1), 0)
            endp = seg[np.arange(idx.size), lastj]
            tr = endp / c[:, -1] - 1
            lab[hz] = (tr, tr - (spy[e] / spy[dd] - 1), (lastj < seg.shape[1] - 1).astype(float))
        for j, r in enumerate(cand):
            rows.append(dict(ym=ym, k=MONTHS.index(ym), cik=r["cik"], ticker=r["prefix"],
                             decision=sessions[dd], sec=ff12_index(r["sic"]), size=r["float"],
                             **{f: float(kf[f][j]) for f in KFEAT}, MOM12_1=float(mom[j]), VOL63=float(vol[j]),
                             BETA=float(beta[j]),
                             **{f"{nm}{hz}": float(lab[hz][q][j]) for hz in (3, 12)
                                for q, nm in enumerate(("tr", "ex", "left"))}))
    return pd.DataFrame(rows)


def ff12_index(sic):
    name = OS.ff12(sic)
    return O.FF12_NAMES.index(name) if name in O.FF12_NAMES else len(O.FF12_NAMES) - 1


def r6(x):
    return O.r6(x)


def numeric(path: Path):
    P = build(path)
    LOCAL.mkdir(parents=True, exist_ok=True)
    P.to_pickle(LOCAL / "panel.pkl")
    k = P["k"].to_numpy()
    out = {"decision": "D308", "protocol": "research/od/OD1_protocol.md section 6", "observations": int(len(P)),
           "reviews": int(P["k"].nunique()), "registrants": int(P["cik"].nunique()),
           "per_review_median": float(P.groupby("k").size().median()),
           "status": "PENDING SOURCE-CONSISTENCY ASSESSMENT (WIKI returns; see OD1_wiki_consistency.json)",
           "features": {}, "universe": {}}
    pr = {c: O.pct_rank(P[c if c != "SIZE" else "size"].to_numpy(float), k) for c in CONTROLS}
    D = np.column_stack([(P["sec"].to_numpy() == j) for j in range(len(O.FF12_NAMES) - 1)]).astype(float)
    Z = np.column_stack([pr[c] for c in CONTROLS] + [D])
    for hz in (3, 12):
        ex = P[f"ex{hz}"].to_numpy()
        out["universe"][hz] = dict(mean_tr=r6(P[f"tr{hz}"].mean()), mean_ex=r6(ex.mean()),
                                   med_ex=r6(np.median(ex)), p_beat=r6((ex > 0).mean()),
                                   left=r6(P[f"left{hz}"].mean()))
    exr = {hz: O.pct_rank(P[f"ex{hz}"].to_numpy(), k) for hz in (3, 12)}
    grp12 = O.deciles(P["ex12"].to_numpy(), k)
    W, Lg = grp12 == 9, grp12 == 0
    for f in KFEAT:
        x = P[f].to_numpy(float)
        dec = O.deciles(x, k)
        xr = O.pct_rank(x, k)
        res = {"coverage": r6(np.isfinite(x).mean())}
        for hz in (3, 12):
            ex = P[f"ex{hz}"].to_numpy()
            tab = {}
            for g in range(10):
                m = dec == g
                tab[g] = dict(n=int(m.sum()), mean_ex=r6(ex[m].mean()), med_ex=r6(np.median(ex[m])),
                              p_beat=r6((ex[m] > 0).mean()),
                              **({"p_w": r6(W[m].mean()), "p_l": r6(Lg[m].mean())} if hz == 12 else {}))
            ser, ic = [], []
            for g, (a, b) in O.bounds(k).items():
                ser.append(O.partial_ic(xr[a:b], exr[hz][a:b], Z[a:b]))
                ic.append(O.spearman(x[a:b], ex[a:b]))
            t, nn = O.nw_t(ser, hz - 1)
            t2, _ = O.nw_t(ic, hz - 1)
            vals = [v for v in ser if v is not None]
            res[hz] = dict(deciles=tab, top_minus_bottom=r6(tab[9]["mean_ex"] - tab[0]["mean_ex"]),
                           partial_ic_mean=r6(np.mean(vals)) if vals else None, partial_ic_nw_t=t,
                           raw_ic_mean=r6(np.nanmean([v for v in ic if v is not None])), raw_ic_nw_t=t2, reviews=nn)
        out["features"][f] = res
    NUMERIC.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({f: {hz: (v[hz]["top_minus_bottom"], v[hz]["partial_ic_nw_t"]) for hz in (3, 12)}
                      for f, v in out["features"].items()}, indent=1))


def consistency(eid):
    P = pd.read_pickle(LOCAL / "panel.pkl")
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(HERE))
    import OD1_eval as EV
    from qresearch import results
    st = json.loads((ROOT / "experiments" / eid / "result.json").read_text())
    res = EV.parse(results.lines_from_statistics(st["qc_statistics"]))
    T = res["meta"]["review_dates"] if "review_dates" in res["meta"] else None
    qc = res["consistency"]
    out = {"decision": "D308", "run": eid}
    ok = True
    for hz in (3, 12):
        rows = qc[str(hz)]
        # QC review index 0 = 2011-01 month-end (the host's first review); WIKI k = months since 2011-01
        w = P.groupby("k")[f"tr{hz}"].mean()
        pairs = [(w[kk], rows[kk][1]) for kk in w.index if kk < len(rows) and rows[kk][1] is not None]
        a, b = np.array([p[0] for p in pairs]), np.array([p[1] for p in pairs])
        corr = float(np.corrcoef(a, b)[0, 1])
        mad = float(np.mean(np.abs(a - b)))
        out[hz] = dict(reviews=len(pairs), corr=r6(corr), mean_abs_diff=r6(mad), mean_diff=r6(float(np.mean(a - b))))
        if hz == 12:
            ok = corr >= 0.8 and mad <= 0.03
    out["review_dates_checked"] = T is not None
    out["label"] = "CONSISTENT" if ok else "NOT CONSISTENT"
    CONSIST.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def sample(path: Path):
    """Draw the blinded visual sample and render the charts (needs `numeric` first)."""
    _check_file(path)
    P = pd.read_pickle(LOCAL / "panel.pkl")
    k = P["k"].to_numpy()
    g = O.deciles(P["ex12"].to_numpy(), k)
    pct = O.pct_rank(P["ex12"].to_numpy(), k)
    P["grp"] = np.where(g == 9, "W", np.where(g == 0, "L", np.where((pct >= 0.4) & (pct < 0.6), "M", "")))
    rng = random.Random(SEED)
    chosen = []
    for grp in ("W", "L", "M"):
        lst = P[P["grp"] == grp].sort_values(["cik", "ym"], kind="mergesort").to_dict("records")
        rng.shuffle(lst)
        seen = set()
        for r in lst:
            if r["cik"] in seen:
                continue
            seen.add(r["cik"])
            chosen.append(dict(cik=int(r["cik"]), ticker=r["ticker"], decision_date=r["decision"], ym=int(r["ym"]),
                               group=grp, ex12=r["ex12"]))
            if sum(1 for c in chosen if c["group"] == grp) == N_PER:
                break
    random.Random(SEED + 1).shuffle(chosen)
    for i, c in enumerate(chosen, 1):
        c["chart_id"] = f"V{i:03d}"
    LOCAL.mkdir(parents=True, exist_ok=True)
    MAPPING.write_text(json.dumps(chosen, indent=1))
    import render as R
    df, _ = wa.load_wiki(path)
    sessions = set(wa.reference_sessions(df))
    df = df[df["ticker"].isin({c["ticker"] for c in chosen}) & df["date"].isin(sessions)]
    groups = dict(tuple(df.groupby("ticker", sort=False)))
    CHARTS.mkdir(parents=True, exist_ok=True)
    pngs = {}
    for c in sorted(chosen, key=lambda c: c["chart_id"]):
        png, last = R.chart_png(groups[c["ticker"]], c["decision_date"])
        if last != c["decision_date"]:
            raise SystemExit(f"{c['chart_id']}: last drawn bar is not the decision date")
        (CHARTS / f"{c['chart_id']}.png").write_bytes(png)
        pngs[c["chart_id"]] = hashlib.sha256(png).hexdigest()
    VIS_MANIFEST.write_text(json.dumps({"decision": "D308", "seed": SEED, "charts": len(pngs),
                                        "per_group_target": N_PER,
                                        "mapping_sha256": hashlib.sha256(MAPPING.read_bytes()).hexdigest(),
                                        "png_sha256": pngs}, indent=1) + "\n")
    print(f"rendered {len(pngs)} charts (groups hidden)")


def record():
    seen = {json.loads(x)["chart_id"] for x in PRED.read_text().splitlines()} if PRED.exists() else set()
    recs = []
    for line in sys.stdin.read().splitlines():
        if not line.strip():
            continue
        cid, pred, tags = [x.strip() for x in line.split("|", 2)]
        tg = [t.strip() for t in tags.split(",") if t.strip()]
        if not (cid.startswith("V") and cid[1:].isdigit()) or pred not in ("OUT", "NEU", "UND") or \
                any(t not in TAGS for t in tg) or cid in seen:
            raise SystemExit(f"bad or duplicate line: {line!r}")
        seen.add(cid)
        recs.append(dict(chart_id=cid, prediction=pred, tags=tg))
    with PRED.open("a") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"recorded {len(recs)}; total {len(seen)}")


def binom_sf(k, n, p):
    """P(X >= k), X ~ Binomial(n, p)."""
    return float(sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1)))


def unblind():
    preds = [json.loads(x) for x in PRED.read_text().splitlines()]
    man = json.loads(VIS_MANIFEST.read_text())
    if len(preds) != man["charts"]:
        raise SystemExit("not every chart has a prediction")
    st = subprocess.run(["git", "status", "--porcelain", "--", str(PRED)], capture_output=True, text=True, cwd=ROOT)
    lg = subprocess.run(["git", "log", "--format=%H", "-1", "--", str(PRED)], capture_output=True, text=True, cwd=ROOT)
    if st.stdout.strip() or not lg.stdout.strip():
        raise SystemExit("predictions must be committed before unblinding")
    if hashlib.sha256(MAPPING.read_bytes()).hexdigest() != man["mapping_sha256"]:
        raise SystemExit("mapping changed since rendering")
    truth = {c["chart_id"]: c["group"] for c in json.loads(MAPPING.read_text())}
    want = {"W": "OUT", "L": "UND", "M": "NEU"}
    conf = Counter((truth[p["chart_id"]], p["prediction"]) for p in preds)
    acc = sum(1 for p in preds if want[truth[p["chart_id"]]] == p["prediction"])
    wl = [p for p in preds if truth[p["chart_id"]] in ("W", "L") and p["prediction"] in ("OUT", "UND")]
    wl_hit = sum(1 for p in wl if want[truth[p["chart_id"]]] == p["prediction"])
    tag_rates = {}
    for t in sorted(TAGS):
        tag_rates[t] = {g: r6(np.mean([t in p["tags"] for p in preds if truth[p["chart_id"]] == g])) for g in "WLM"}
    out = dict(decision="D308", predictions_commit=lg.stdout.strip(), charts=len(preds),
               confusion={f"{a}->{b}": v for (a, b), v in sorted(conf.items())},
               accuracy_3class=r6(acc / len(preds)), p_3class=r6(binom_sf(acc, len(preds), 1 / 3)),
               wl_called=len(wl), wl_hits=wl_hit, wl_accuracy=r6(wl_hit / len(wl)) if wl else None,
               p_wl=r6(binom_sf(wl_hit, len(wl), 0.5)) if wl else None,
               visual_information="present" if wl and wl_hit / len(wl) >= 0.65 and binom_sf(wl_hit, len(wl), 0.5) < 0.01
               else "not present",
               tag_rate_by_group=tag_rates)
    VIS_RESULT.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "tag_rate_by_group"}, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "numeric":
        numeric(Path(sys.argv[2]))
    elif cmd == "sample":
        sample(Path(sys.argv[2]))
    elif cmd == "record":
        record()
    elif cmd == "consistency":
        consistency(sys.argv[2])
    elif cmd == "unblind":
        unblind()
    else:
        raise SystemExit(__doc__)
