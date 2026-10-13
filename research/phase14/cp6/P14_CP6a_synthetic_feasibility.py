"""P14-CP6a (owner D237): pre-implementation SYNTHETIC feasibility check of Null #3 (B2 Event-Copy Relay) before any
real-data Null #3 world -> P14_CP6a_synthetic_feasibility.json.

SYNTHETIC panels only (no market data, no returns, no QuantConnect run). A panel has no predictive signal, so the
'real' selection's month-to-month persistence is a purely structural property that a valid null must reproduce.
Panels are calibrated to the H029 universe (about 765 stocks, 11 sectors, ~18 exits / ~21 entries a month, quarterly
filing cycles); the frozen Null #2 (same-sector tether) on these panels reproduces its real-data turnover gap
(+0.016), which validates the calibration. Compared: Null #2, B2 as approved (rank coupling), B2 with the
exploratory continuation refinement. All through the frozen qr_h029 / qr_h026 selection code.

    PYTHONPATH=src python research/phase14/cp6/P14_CP6a_synthetic_feasibility.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean")]
import qr_h029 as Q0  # noqa: E402
import qr_h029n3 as Q  # noqa: E402

PANEL_SEEDS = (9, 10, 11)
WORLDS = tuple(range(1, 9))
SETTINGS = {
    "realistic": dict(n0=765, sectors=11, exits=18, entries=21, sector_moves=1, miss=False),
    "realistic_offcycle_missing": dict(n0=765, sectors=11, exits=18, entries=21, sector_moves=1, miss=True),
    "no_churn_control": dict(n0=765, sectors=11, exits=0, entries=0, sector_moves=0, miss=False),
}


def panel(seed=1, months=48, n0=120, exits=4, entries=5, sectors=4, sector_moves=1, miss=True):
    """SYNTHETIC panel: persistent six-signal latents updated on staggered quarterly cycles (AR 0.9), churn, sector
    moves and (optionally) off-cycle single-signal missing-value changes."""
    rng = np.random.default_rng(seed)
    nxt, lat, sec, ph = [0], {}, {}, {}

    def add():
        s = f"S{nxt[0]:05d}"
        nxt[0] += 1
        lat[s], sec[s], ph[s] = rng.normal(size=6), int(rng.integers(sectors)), int(rng.integers(3))
        return s
    alive = [add() for _ in range(n0)]
    ms, Vs = [], []
    for t in range(months):
        if t:
            out = set(rng.choice(len(alive), exits, replace=False).tolist()) if exits else set()
            alive = [s for k, s in enumerate(alive) if k not in out] + [add() for _ in range(entries)]
            if sector_moves:
                for s in rng.choice(alive, sector_moves, replace=False):
                    sec[s] = (sec[s] + 1) % sectors
        for s in alive:
            if (t + ph[s]) % 3 == 0:
                lat[s] = 0.9 * lat[s] + 0.44 * rng.normal(size=6)
        ids = sorted(alive)
        V = np.array([lat[s] for s in ids])
        if miss:
            V[(np.arange(len(ids)) * 7 + t) % 11 == 0, (t % 6)] = np.nan
        ms.append(dict(ids=ids, sector=np.array([sec[s] for s in ids]), open_ok=np.ones(len(ids), bool), day=t))
        Vs.append(V)
    return ms, Vs


def summarise(real, null):
    a = np.asarray(null, float)
    return dict(real=real, null_min=float(a.min()), null_median=float(np.median(a)), null_max=float(a.max()),
                gap_to_median=float(np.median(a) - real), real_below_all=bool(real < a.min()),
                real_above_all=bool(real > a.max()))


def main():
    out = dict(note=__doc__.split("\n\n")[0], panel_seeds=list(PANEL_SEEDS), worlds=list(WORLDS), settings=SETTINGS,
               results={})
    for name, kw in SETTINGS.items():
        for ps in PANEL_SEEDS:
            ms, Vs = panel(seed=ps, **kw)
            plan, real = Q.relay_plan(ms, Vs)
            rt = Q.selection_structure(ms, real)[0]
            r2 = Q.p2_survival(ms, plan, Q.picks(ms, real))
            res = {}
            for null in ("null2_sector_tether", "b2_approved_rank_coupling", "b2_continuation_refinement"):
                t, s2 = [], []
                for w in WORLDS:
                    if null == "null2_sector_tether":
                        sc = Q.h029_scores(Q0.tether_vectors(ms, Vs, w))
                    else:
                        sc = Q.relay(ms, Vs, plan, w, continuation=null == "b2_continuation_refinement")[1]
                    t.append(Q.selection_structure(ms, sc)[0])
                    s2.append(Q.p2_survival(ms, plan, Q.picks(ms, sc)))
                res[null] = dict(turnover=summarise(rt, t), p2_survival=summarise(r2, s2))
            out["results"][f"{name}|panel{ps}"] = res
            print(name, ps, {k: round(v["turnover"]["gap_to_median"], 4) for k, v in res.items()})
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    (HERE / "P14_CP6a_synthetic_feasibility.json").write_text(text)
    print("sha256", hashlib.sha256(text.encode()).hexdigest())


if __name__ == "__main__":
    main()
