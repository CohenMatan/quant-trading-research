"""H020 synthetic scenario table (P5-CP2 section 33): builds every fixture of h020_fixtures, computes the frozen snapshot at
the last bar and renders the Daily / Weekly panels. SYNTHETIC ONLY (no market data, no returns).

  python research/phase5/h020_scenarios.py            # print the table
  python research/phase5/h020_scenarios.py --write    # (re)write h020_scenarios_expected.json  (frozen: written ONCE
                                                      #  before the spec pin; tests/test_h020_scenarios.py compares)
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / "src" / "qresearch" / "lean")]
import h020_fixtures as F  # noqa: E402
import qr_chart as C  # noqa: E402
import qr_chart_render as R  # noqa: E402

OUT = HERE / "h020_scenarios_expected.json"


def scenario(name):
    b = F.build(name)
    t = b["c"].size - 1
    s = C.snapshot_at(b, t)
    W = C.weekly_bars(b["o"], b["h"], b["l"], b["c"], b["v"], b["week_id"])
    cd = R.render(b["o"], b["h"], b["l"], b["c"], b["v"], 126, R.daily_overlays(s, C.sma, b["c"], len(b["c"])))
    cw = R.render(W["o"], W["h"], W["l"], W["c"], W["v"], 104, R.weekly_overlays(s, W, C.sma))
    bs, bo = s["base"], s["breakout"]
    return dict(
        score=s["score"], categories=s["categories"], quality_level=C.quality_level(s), group=C.score_group(s),
        conditions=s["conditions"], disqualifiers=s["disqualifiers"],
        weekly_state=s["weekly_state"], daily_state=s["daily_state"],
        features=C.canonical(dict(
            base_valid=bool(bs is not None and bs["valid"]), base_length_w=None if bs is None else bs["length"],
            base_depth=None if bs is None else bs["depth"], base_pullbacks=None if bs is None else bs["pullbacks"],
            breakout_age=None if bo is None else bo["age"], breakout_ext=None if bo is None else bo["ext"],
            breakout_relvol=None if bo is None else bo["relvol"], breakout_clv=None if bo is None else bo["clv"],
            atr_pct=s["atr_pct"], atr_ratio=s["atr_ratio"], vol_ratio=s["vol_ratio"], risk=s["risk"],
            distribution_days=s["distribution_days"], n_pivots_daily=len(s["pivots_daily"]),
            n_pivots_weekly=len(s["pivots_weekly"]), n_zones_daily=len(s["zones_daily"]),
            support_trendline=s["trend_support"] is not None, resistance_trendline=s["trend_resistance"] is not None,
            close_over_ma50=float(b["c"][-1] / s["ma"]["ma50"]), close_over_hi52=float(b["c"][-1] / s["hi52"]))),
        snapshot_digest=C.digest(s),
        daily_raster_sha256=hashlib.sha256(cd.a.tobytes()).hexdigest(),
        weekly_raster_sha256=hashlib.sha256(cw.a.tobytes()).hexdigest(),
        daily_png_sha256=hashlib.sha256(cd.png()).hexdigest(),
        weekly_png_sha256=hashlib.sha256(cw.png()).hexdigest(),
        target=F.TARGET[name])


def table():
    return {n: scenario(n) for n in F.SCENARIOS}


if __name__ == "__main__":
    T = table()
    for n, r in T.items():
        dq = [k for k, v in r["disqualifiers"].items() if v]
        print("%-28s score %2d  W/B/T/R %s  group G%d  DQ %-8s weekly %-15s daily %-14s" % (
            n, r["score"], "/".join(str(r["categories"][k]) for k in "WBTR"), r["group"], ",".join(dq) or "-",
            r["weekly_state"], r["daily_state"]))
    if "--write" in sys.argv:
        OUT.write_text(json.dumps(dict(
            note="H020 frozen synthetic scenario expectations (P5-CP2). Synthetic fixtures only; written once before "
                 "the spec pin; never rewritten to match a code change without a recorded decision.",
            scenarios=T), indent=1, sort_keys=True) + "\n")
        print("wrote", OUT)
