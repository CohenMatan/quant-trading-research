"""OD-1 report tables (descriptive; owner D308). Reads the committed E808-01 aggregate lines and the frozen evaluation,
writes research/od/OD1_tables_E808-01.json. No new statistic is used for any decision: the Stage G rule is OD1_eval.

    python research/od/OD1_tables.py E808-01
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import OD1_eval as EV  # noqa: E402

QS = (0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99)


def r(x, d=4):
    return None if x is None else round(x, d)


def outcomes(res):
    out = {}
    for h, d in res["outcomes"].items():
        row = {}
        for p in ("DISC", "STRESS", "ALL"):
            x = d.get(p, {})
            if not x.get("n"):
                continue
            q = dict(zip(QS, x["tr_q"]))
            qe = dict(zip(QS, x["ex_q"]))
            row[p] = dict(n=x["n"], reviews=x["reviews"], firms=x["firms"],
                          independent_windows=r(x["reviews"] / int(h), 1),
                          mean_tr=x["mean_tr"], median_tr=q[0.5], mean_ex=x["mean_ex"], median_ex=qe[0.5],
                          p_beat_spy=x["p_beat"], p_severe_loss=x["p_s"], p_double=x["p_big"],
                          tr_p01=q[0.01], tr_p10=q[0.1], tr_p90=q[0.9], tr_p99=q[0.99],
                          left_universe=x["left"], left_winners=x["left_w"], left_losers=x["left_l"],
                          mae_winners=x["mae_w"], mae_losers=x["mae_l"], mae_all=x["mae_all"])
        row["concentration"] = d.get("concentration")
        row["winner_path"] = d.get("winner_path")
        row["years"] = d.get("years")
        out[h] = row
    return out


def features(res, ev):
    out = {}
    disc6 = EV._period_slice(res, 6, "DISC")
    disc12 = EV._period_slice(res, 12, "DISC")
    st12 = EV._period_slice(res, 12, "STRESS")
    for name, f in res["feature"].items():
        gl = f["groups"]
        t12 = f["tables"]["12"]
        lo, hi = str(gl[0]), str(gl[-1])
        D, S = t12["DISC"], t12["STRESS"]
        s12 = res["series"][name]["12"]
        s6 = res["series"][name]["6"]
        spread_d = [s12["spread"][k] for k in disc12]
        t_spread, _ = EV._nw(spread_d, 11)
        t_ic6, _ = EV._nw([s6["ic"][k] for k in disc6], 5)
        t_pic6, _ = EV._nw([s6["pic"][k] for k in disc6], 5)
        st6 = EV._period_slice(res, 6, "STRESS")
        pst = [s6["pic"][k] for k in st6 if s6["pic"][k] is not None]
        sp_st = [s12["spread"][k] for k in st12 if s12["spread"][k] is not None]
        prof = f["profiles"]["12"]["DISC"]
        yb = f["breakdowns"]["year"]
        yrs_pos = sum(1 for y in EV.YEARS if str(y) in yb and yb[str(y)].get(hi) is not None
                      and yb[str(y)].get(lo) is not None and yb[str(y)][hi] - yb[str(y)][lo] > 0)
        sb = f["breakdowns"]["sector"]
        sec_pos = sum(1 for s in EV.NONFIN_SECTORS if s in sb and sb[s].get(hi) is not None
                      and sb[s].get(lo) is not None and sb[s][hi] - sb[s][lo] > 0)
        e = ev["features"][name]
        out[name] = dict(
            groups=len(gl), duplicate_of=EV.DUPLICATES.get(name),
            top=dict(n=D[hi].get("n"), mean_ex=D[hi].get("mean_ex"), med_ex=D[hi].get("med_ex"),
                     p_w=D[hi].get("p_w"), p_l=D[hi].get("p_l"), p_s=D[hi].get("p_s")),
            bottom=dict(n=D[lo].get("n"), mean_ex=D[lo].get("mean_ex"), med_ex=D[lo].get("med_ex"),
                        p_w=D[lo].get("p_w"), p_l=D[lo].get("p_l"), p_s=D[lo].get("p_s")),
            univ_disc=dict(mean_ex=D["univ"].get("mean_ex"), p_w=D["univ"].get("p_w"), p_l=D["univ"].get("p_l")),
            top_minus_bottom_disc_h12=r((D[hi].get("mean_ex") or 0) - (D[lo].get("mean_ex") or 0)),
            top_minus_bottom_stress_h12=r((S.get(hi, {}).get("mean_ex") or 0) - (S.get(lo, {}).get("mean_ex") or 0)),
            spread_nw_t_disc_h12=r(t_spread, 2), raw_ic_nw_t_disc_h6=r(t_ic6, 2),
            partial_ic_nw_t_disc_h6=r(t_pic6, 2),
            partial_ic_mean_stress_h6=r(sum(pst) / len(pst)) if pst else None,
            partial_ic_t_disc_h6_best_group_dir=r(e["partial_ic_t_disc_h6"], 2),
            stress_spread_mean_h12=r(sum(sp_st) / len(sp_st)) if sp_st else None,
            winners_in_top_quintile=prof["W"]["top_q"], losers_in_top_quintile=prof["L"]["top_q"],
            ordinary_in_top_quintile=prof["M"]["top_q"],
            winners_in_bottom_quintile=prof["W"]["bot_q"], losers_in_bottom_quintile=prof["L"]["bot_q"],
            years_top_beats_bottom=yrs_pos, sectors_top_beats_bottom=sec_pos,
            coverage=f["coverage"], rule_best_group=e["group"], gates=e["gates"])
    return out


def grids(res, ev):
    out = {}
    for name, g in res["grid"].items():
        D = g["cells"]["12"]["DISC"]
        S = g["cells"]["12"]["STRESS"]
        cells = {c: dict(n=v.get("n"), mean_ex=v.get("mean_ex"), med_ex=v.get("med_ex"), p_w=v.get("p_w"),
                         p_l=v.get("p_l"), stress_mean_ex=S.get(c, {}).get("mean_ex"))
                 for c, v in D.items()}
        e = ev["grids"][name]
        out[name] = dict(rows=g["rows"], cols=g["cols"], cells=cells, best=e["cell"], incremental=e["incremental"],
                         t_disc_h6=e["cmu_t_disc_h6"], gates=e["gates"])
    return out


def main(eid):
    res = EV.parse(json.load(gzip.open(HERE / f"{eid}_od1_lines.json.gz", "rt")))
    ev = json.loads((HERE / f"OD1_result_{eid}.json").read_text())["evaluation"]
    out = dict(run=eid, meta=res["meta"], outcomes=outcomes(res), features=features(res, ev), grids=grids(res, ev),
               reviews=res["reviews"])
    (HERE / f"OD1_tables_{eid}.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "E808-01")
