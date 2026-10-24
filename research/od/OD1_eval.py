"""OD-1 outcome-driven discovery study (owner D308; research/od/OD1_protocol.md): the frozen OFFLINE evaluation of the
X808 aggregate lines. Written and pinned (qresearch.od1) BEFORE the run. It parses the 'OD1|...' lines, builds the
report tables and applies the Stage G candidate rule (protocol section 5) exactly as frozen.

    PYTHONPATH=src python research/od/OD1_eval.py E808-01   -> research/od/OD1_result_E808-01.json (+ lines .json.gz)
"""
from __future__ import annotations

import gzip
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
DUPLICATES = {"MOM12_1": "H002 / H019 S1", "MOM6_1": "H002 / H019 S1", "HI52": "H003", "ID": "H019 S2",
              "BREAKOUT": "H006", "DROA": "OC-2 / H029 F5", "REVACCEL": "H029 F1", "AG": "H024 AG", "ACCR": "H024 ACC",
              "BM": "H024 BM", "GPA": "H016", "REPURCH": "H032", "REV1M": "H001 / H024 REV1M", "VOL63": "H024 LOWVOL",
              "OCFTA": "H024 CBOP-like", "EY": "H024 CFP-like", "GMCHG": "H029 F2"}
YEARS = list(range(2011, 2021))
NONFIN_SECTORS = [str(j) for j in range(12) if j != 10]       # FF12 index 10 = Money (financials)


STAT_KEYS = ("n", "reviews", "firms", "mean_ex", "med_ex", "trim_ex", "mean_tr", "mean_sr", "mean_ba", "p_beat", "p_w",
             "p_l", "p_s", "mae", "left")        # = qr_od1.STAT_KEYS (tests check equality)


def _unpack(tables):
    for per_h in tables.values():
        for per_p in per_h.values():
            for g, v in list(per_p.items()):
                per_p[g] = dict(zip(STAT_KEYS, v))


def parse(lines):
    out = {"feature": {}, "series": {}, "grid": {}}
    for ln in lines:
        if not ln.startswith("OD1|"):
            continue
        _, sec, key, payload = ln.split("|", 3)
        obj = json.loads(payload)
        if sec in ("feature", "series", "grid"):
            out[sec][key] = obj
        elif sec in ("meta", "reviews"):
            out[sec] = obj
        else:
            out[sec] = obj
    for f in out["feature"].values():
        _unpack(f["tables"])
    for g in out["grid"].values():
        _unpack(g["cells"])
    if "outcomes" in out:
        out["outcomes"] = {str(h): v for h, v in out["outcomes"].items()}
    return out


def _nw(x, lag):
    x = [v for v in x if v is not None and math.isfinite(v)]
    n = len(x)
    if n < 8:
        return None, n
    m = sum(x) / n
    e = [v - m for v in x]
    s = sum(v * v for v in e) / n
    for k in range(1, min(lag, n - 1) + 1):
        s += 2 * (1 - k / (lag + 1)) * sum(e[j] * e[j - k] for j in range(k, n)) / n
    return (m / math.sqrt(s / n) if s > 0 else None), n


def _period_slice(res, h, period):
    """Review indices whose h-month label lies in DISC (label end <= K1712) or STRESS (decision >= K1801)."""
    K, k1712, k1801 = res["meta"]["reviews"], res["meta"]["K1712"], res["meta"]["K1801"]
    if period == "DISC":
        return [k for k in range(K) if k + h <= k1712]
    return [k for k in range(K) if k >= k1801 and k + h <= K - 1]


def _direction(g, groups):
    """+1 for the upper half of the groups, -1 for the lower half (the partial IC sign the group implies)."""
    mid = (groups[0] + groups[-1]) / 2.0
    return 1 if g > mid else -1


def feature_rule(name, res):
    f, s = res["feature"][name], res["series"][name]
    groups = f["groups"]
    t12 = f["tables"]["12"]
    disc = t12["DISC"]
    best = max(groups, key=lambda g: (disc[str(g)].get("mean_ex") if disc[str(g)].get("n") else -9e9))
    gs = str(best)
    d = disc[gs]
    st = t12["STRESS"].get(gs, {})
    dirn = _direction(best, groups)
    pic6 = s["6"]["pic"]
    disc_k, stress_k = _period_slice(res, 6, "DISC"), _period_slice(res, 6, "STRESS")
    t_disc, n_disc = _nw([pic6[k] * dirn if pic6[k] is not None else None for k in disc_k], 5)
    st_pic = [pic6[k] for k in stress_k if pic6[k] is not None]
    st_pic_mean = sum(st_pic) / len(st_pic) if st_pic else None
    yb = f["breakdowns"]["year"]
    yrs = {y: yb[str(y)].get(gs) for y in YEARS if str(y) in yb}
    pos = [v for v in yrs.values() if v is not None and v > 0]
    sb, zb = f["breakdowns"]["sector"], f["breakdowns"]["size"]
    sec_pos = sum(1 for sct in NONFIN_SECTORS if sct in sb and sb[sct].get(gs) is not None and sb[sct][gs] > 0)
    size_pos = sum(1 for z in ("0", "1", "2") if z in zb and zb[z].get(gs) is not None and zb[z][gs] > 0)
    G = dict(
        G1=bool(d.get("n", 0) >= 1000 and d.get("reviews", 0) >= 48 and (d.get("mean_ex") or -1) >= 0.04
                and (d.get("trim_ex") or -1) >= 0.02),
        G2=bool(t_disc is not None and t_disc >= 2.0),
        G3=bool((st.get("mean_ex") or -1) >= 0.02 and st_pic_mean is not None and st_pic_mean * dirn > 0),
        G4=bool(sum(1 for v in yrs.values() if v is not None and v > 0) >= 7 and pos
                and max(pos) / sum(pos) <= 0.40),
        G5=bool(sec_pos >= 7 and size_pos == 3),
        G6=name not in DUPLICATES)
    return dict(group=best, direction=dirn, disc=d, stress=st, partial_ic_t_disc_h6=t_disc, n_reviews_disc=n_disc,
                partial_ic_mean_stress_h6=st_pic_mean, years_vs_universe=yrs, sectors_positive=sec_pos,
                size_terciles_positive=size_pos, gates=G, passes_G1_G5=all(G[x] for x in ("G1", "G2", "G3", "G4", "G5")),
                duplicate_of=DUPLICATES.get(name))


def grid_rule(name, res):
    g = res["grid"][name]
    disc = g["cells"]["12"]["DISC"]
    cells = [c for c in disc if c != "univ"]
    best = max(cells, key=lambda c: (disc[c].get("mean_ex") if disc[c].get("n") else -9e9))
    d = disc[best]
    st = g["cells"]["12"]["STRESS"].get(best, {})
    ser = g["series"][best]["cmu"]
    disc_k, stress_k = _period_slice(res, 6, "DISC"), _period_slice(res, 6, "STRESS")
    t_disc, n_disc = _nw([ser[k] for k in disc_k], 5)
    st_s = [ser[k] for k in stress_k if ser[k] is not None]
    st_mean = sum(st_s) / len(st_s) if st_s else None
    # incremental: the cell vs its row and column marginals (n-weighted DISC means of the same row / column)

    def marg(pred):
        cs = [c for c in cells if pred(c) and disc[c].get("n")]
        n = sum(disc[c]["n"] for c in cs)
        return sum(disc[c]["mean_ex"] * disc[c]["n"] for c in cs) / n if n else None
    row_m, col_m = marg(lambda c: c[0] == best[0]), marg(lambda c: c[1] == best[1])
    incr = (d.get("mean_ex") or -1) - max(v for v in (row_m, col_m) if v is not None) if d.get("n") else None
    yb, sb, zb = g["breakdowns"]["year"], g["breakdowns"]["sector"], g["breakdowns"]["size"]
    yrs = {y: yb[str(y)].get(best) for y in YEARS if str(y) in yb}
    pos = [v for v in yrs.values() if v is not None and v > 0]
    sec_pos = sum(1 for sct in NONFIN_SECTORS if sct in sb and sb[sct].get(best) is not None and sb[sct][best] > 0)
    size_pos = sum(1 for z in ("0", "1", "2") if z in zb and zb[z].get(best) is not None and zb[z][best] > 0)
    G = dict(
        G1=bool(d.get("n", 0) >= 1000 and d.get("reviews", 0) >= 48 and (d.get("mean_ex") or -1) >= 0.04
                and (d.get("trim_ex") or -1) >= 0.02),
        G2=bool(t_disc is not None and t_disc >= 2.0),
        G3=bool((st.get("mean_ex") or -1) >= 0.02 and st_mean is not None and st_mean > 0),
        G4=bool(sum(1 for v in yrs.values() if v is not None and v > 0) >= 7 and pos and max(pos) / sum(pos) <= 0.40),
        G5=bool(sec_pos >= 7 and size_pos == 3),
        G6=bool(incr is not None and incr >= 0.02))
    return dict(cell=best, disc=d, stress=st, cmu_t_disc_h6=t_disc, n_reviews_disc=n_disc, cmu_mean_stress_h6=st_mean,
                row_marginal=row_m, col_marginal=col_m, incremental=incr, years_vs_universe=yrs,
                sectors_positive=sec_pos, size_terciles_positive=size_pos, gates=G,
                passes_G1_G5=all(G[x] for x in ("G1", "G2", "G3", "G4", "G5")))


def evaluate(res):
    feats = {n: feature_rule(n, res) for n in res["feature"]}
    grids = {n: grid_rule(n, res) for n in res["grid"]}
    cands = [("feature", n, v) for n, v in feats.items() if v["passes_G1_G5"] and v["gates"]["G6"]] + \
            [("grid", n, v) for n, v in grids.items() if v["passes_G1_G5"] and v["gates"]["G6"]]
    reobs = [("feature", n, v["duplicate_of"]) for n, v in feats.items() if v["passes_G1_G5"] and not v["gates"]["G6"]]
    cands.sort(key=lambda c: -((c[2].get("partial_ic_t_disc_h6") or c[2].get("cmu_t_disc_h6") or 0)))
    return dict(features=feats, grids=grids,
                candidates=[dict(kind=a, name=b, group=v.get("group", v.get("cell"))) for a, b, v in cands[:3]],
                re_observations=[dict(kind=a, name=b, parent=p) for a, b, p in reobs],
                stage_h=bool(cands))


def main(eid):
    sys.path.insert(0, str(ROOT / "src"))
    from qresearch import results
    st = json.loads((ROOT / "experiments" / eid / "result.json").read_text())
    lines = results.lines_from_statistics(st["qc_statistics"])
    od = [ln for ln in lines if ln.startswith("OD1|")]
    with gzip.open(HERE / f"{eid}_od1_lines.json.gz", "wt") as fh:
        json.dump(od, fh)
    res = parse(od)
    ev = evaluate(res)
    (HERE / f"OD1_result_{eid}.json").write_text(json.dumps(dict(meta=res["meta"], evaluation=ev), indent=1) + "\n")
    print(json.dumps(dict(candidates=ev["candidates"], re_observations=ev["re_observations"], stage_h=ev["stage_h"]),
                     indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "E808-01")
