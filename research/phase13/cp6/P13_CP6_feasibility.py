"""P13-CP6 (owner D239) DEVELOPMENT FIXTURE — matching feasibility for R1 (owner section 5). NOT statistical
validation: no rejection rate or p-value is computed here; only matching support and exposure balance, which decide
the matching method that is then frozen in P13_CP6_protocol.json before the final synthetic evaluation.

Seeds 900001-900008 (development range, never reused by the final evaluation). SYNTHETIC panels only.

    PYTHONPATH=src python research/phase13/cp6/P13_CP6_feasibility.py
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from qresearch import r1synth as G  # noqa: E402
from qresearch import r1twin as T  # noqa: E402

SEEDS = tuple(range(900001, 900009))
PROCS = ("P1", "P1L", "P2", "P3")
V1 = ("LV", "SIZE")
V2 = ("LV", "SIZE", "BM", "PROF", "MOM", "BETA")
CALIPERS = (0.05, 0.10, 0.15, 0.20, 0.30)
KNN = (5, 10, 20)
MMIN = (3, 5)


def events(months, real):
    """(t, row) of every real buy and of every continuing real holding (possible replacement draw)."""
    ev = []
    for t, (m, rec) in enumerate(zip(months, real["trace"])):
        pos = {int(s): i for i, s in enumerate(m["ids"])}
        ev += [(t, pos[sid], "buy") for _, sid in rec["buys"]]
        ev += [(t, pos[sid], "keep") for _, sid in rec["keeps"]]
    return ev


GROUPS = {0: 0, 1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 0, 7: 0, 8: 0, 9: 0, 10: 1}   # defensive / cyclical / technology


def m3_stats(months, ev, dims, k, cal, mmin, cal2=None, sector_mode="exact"):
    """Support and balance; SMD is reported over ALL events (unmatched = self, zero difference) and over MATCHED
    events only (smd_matched), plus the share of matched events whose twin has a different sector (cross_sector)."""
    lvls, size, diff, dm, cross = [], [], {d: [] for d in V2}, {d: [] for d in V2}, []
    for t, i, _ in ev:
        m = months[t]
        p, lvl = T.m3_pool(m, i, dims, k, cal, mmin, cal2, sector_mode)
        lvls.append(lvl)
        size.append(p.size)
        for d in V2:
            x = m["pct"][d][i] - (m["pct"][d][p].mean() if p.size else m["pct"][d][i])
            diff[d].append(x)
            if p.size:
                dm[d].append(x)
        if p.size:
            cross.append(float(np.mean(m["sector"][p] != m["sector"][i])))
    lv = np.array(lvls)
    return dict(primary=float(np.mean(lv == 1)), fallback=float(np.mean(lv == 2)), unmatched=float(np.mean(lv == 0)),
                pool_median=float(np.median(size)), pool_q10=float(np.quantile(size, 0.1)),
                smd={d: float(np.mean(diff[d]) / T.U_SD) for d in V2},
                smd_matched={d: (float(np.mean(dm[d]) / T.U_SD) if dm[d] else float("nan")) for d in V2},
                cross_sector=float(np.mean(cross)) if cross else float("nan"))


def m1_stats(months, ev, dims_bins):
    occ, alone, sing = [], [], []
    for t, i, _ in ev:
        m = months[t]
        cells = T.m1_cell(m, dims_bins)
        c = cells[i]
        n_same = sum(1 for x in cells if x == c) - 1
        alone.append(n_same == 0)
        occ.append(n_same)
    # cell-level occupancy over all months
    for m in months[::12]:
        cells = T.m1_cell(m, dims_bins)
        u, cnt = np.unique(np.array([hash(c) for c in cells]), return_counts=True)
        sing.append(float(np.mean(cnt == 1)))
    n_cells = 11 * int(np.prod([nb for _, nb in dims_bins]))
    return dict(n_cells=n_cells, mean_occupancy=475 / n_cells, selected_no_alternative=float(np.mean(alone)),
                selected_alternatives_median=float(np.median(occ)), share_singleton_cells=float(np.mean(sing)))


def m2_stats(months, ev):
    """M2 hierarchy: L1 sector x LV quintile x SIZE tercile; L2 sector x LV quintile; L3 sector x LV tercile; else
    unmatched (each level needs >= 3 alternatives)."""
    levels = ([("LV", 5), ("SIZE", 3)], [("LV", 5)], [("LV", 3)])
    got, diff = [], {d: [] for d in V2}
    for t, i, _ in ev:
        m = months[t]
        lvl, pool = 0, None
        for L, db in enumerate(levels, 1):
            cells = T.m1_cell(m, db)
            p = np.array([j for j, c in enumerate(cells) if c == cells[i] and j != i])
            if p.size >= 3:
                lvl, pool = L, p
                break
        got.append(lvl)
        for d in V2:
            diff[d].append(m["pct"][d][i] - (m["pct"][d][pool].mean() if pool is not None else m["pct"][d][i]))
    g = np.array(got)
    return dict(level_shares={f"L{L}": float(np.mean(g == L)) for L in (1, 2, 3)}, unmatched=float(np.mean(g == 0)),
                smd={d: float(np.mean(diff[d]) / T.U_SD) for d in V2})


def m4_stats(months, real, dims, tol, rng):
    acc = []
    for t in range(0, len(months), 12):
        m = months[t]
        pos = {int(s): i for i, s in enumerate(m["ids"])}
        rows = np.array([pos[s] for _, s in real["trace"][t]["held"]])
        if rows.size:
            acc.append(T.m4_acceptance(m, rows, dims, tol, 2000, rng))
    return dict(acceptance_mean=float(np.mean(acc)), acceptance_min=float(np.min(acc)))


def main():
    t0 = time.time()
    out = dict(checkpoint="P13-CP6", decision="D239", kind="DEVELOPMENT FIXTURE — matching feasibility only",
               seeds=list(SEEDS), synthetic_only=True, rejection_rates_computed=False, results={})
    rng = np.random.default_rng(7)
    for proc in PROCS:
        res = dict(M1={}, M2=None, M3={}, M4={})
        allev, panels = [], []
        for seed in SEEDS:
            ms = G.panel(seed, G.config())
            real = T.real_sim(ms, T.scores(ms, proc))
            panels.append((ms, real))
            allev.append(events(ms, real))
        pick = lambda f: [f(ms, ev) for (ms, _), ev in zip(panels, allev)]  # noqa: E731

        def avg(lst):
            if isinstance(lst[0], dict):
                return {k: avg([x[k] for x in lst]) for k in lst[0]}
            return float(np.mean(lst))
        res["M1"]["V1_LVq5_SIZEt3"] = avg(pick(lambda ms, ev: m1_stats(ms, ev, [("LV", 5), ("SIZE", 3)])))
        res["M1"]["V1_plus_BMt3"] = avg(pick(lambda ms, ev: m1_stats(ms, ev, [("LV", 5), ("SIZE", 3), ("BM", 3)])))
        res["M2"] = avg(pick(m2_stats))
        for vname, dims in (("V1", V1), ("V2", V2)):
            for cal in CALIPERS:
                for k in KNN:
                    for mmin in MMIN:
                        if mmin > k:
                            continue
                        key = f"{vname}_cal{cal}_k{k}_min{mmin}"
                        res["M3"][key] = avg(pick(lambda ms, ev: m3_stats(ms, ev, dims, k, cal, mmin)))
        for vname, dims in (("V1", V1), ("V2", V2)):
            for smode, sname in (("none", "nosector"), (GROUPS, "groups")):
                for cal in (0.10, 0.15, 0.20, 0.25):
                    key = f"{vname}_{sname}_cal{cal}_k10_min3"
                    res["M3"][key] = avg(pick(lambda ms, ev: m3_stats(ms, ev, dims, 10, cal, 3, None, smode)))
        for vname, dims in (("V1", V1), ("V2", V2)):
            for tol in (0.03, 0.05):
                res["M4"][f"{vname}_tol{tol}"] = avg([m4_stats(ms, real, dims, tol, rng) for ms, real in panels])
        out["results"][proc] = res
        print(proc, f"{time.time() - t0:.0f}s", flush=True)
    # universe-size sensitivity (is "at current universe size" the binding qualifier?): P1 / P1L, 3 seeds
    sizes = {}
    for n in (475, 950, 1900):
        for proc in ("P1", "P1L"):
            acc = {}
            for seed in SEEDS[:3]:
                ms = G.panel(seed, G.config(n_target=n))
                real = T.real_sim(ms, T.scores(ms, proc))
                ev = events(ms, real)
                for vname, dims, smode, cal in (("V1", V1, "exact", 0.15), ("V1", V1, "exact", 0.20),
                                                ("V2", V2, "exact", 0.20), ("V2", V2, "exact", 0.25),
                                                ("V2", V2, "exact", 0.30)):
                    key = f"{vname}_exact_cal{cal}_k10_min3"
                    acc.setdefault(key, []).append(m3_stats(ms, ev, dims, 10, cal, 3, None, smode))
            sizes[f"n{n}_{proc}"] = {k: {"matched": float(np.mean([1 - x["unmatched"] for x in v])),
                                         "smd_matched": {d: float(np.mean([x["smd_matched"][d] for x in v]))
                                                         for d in V2}} for k, v in acc.items()}
            print("size", n, proc, f"{time.time() - t0:.0f}s", flush=True)
    out["universe_size_sensitivity"] = sizes
    txt = json.dumps(out, indent=1, sort_keys=True)
    (HERE / "P13_CP6_feasibility.json").write_text(txt + "\n")
    print(hashlib.sha256(txt.encode()).hexdigest()[:16])


if __name__ == "__main__":
    main()
