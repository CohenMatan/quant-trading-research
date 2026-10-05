"""H020 runtime / memory / capacity measurement on SYNTHETIC data (P5-CP2 sections 34-36). No market data.

  python research/phase5/h020_runtime.py      -> research/phase5/h020_runtime.json
"""
import json
import platform
import resource
import sys
import time
import tracemalloc
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / "src" / "qresearch" / "lean")]
import h020_synth_panel as P  # noqa: E402
import p5_synth as S  # noqa: E402
import qr_chart as C  # noqa: E402
import qr_chart_render as R  # noqa: E402
import qr_h020_stats as H  # noqa: E402

# capacity assumptions for the real run (documented in P5-CP2 section 35)
WEEKS = 417                 # weekly decisions 2010-01 .. 2017-12 (scoring starts once 504 sessions exist per stock)
ELIGIBLE_PER_WEEK = 1000    # >= $2B, >= $5, ADV20 >= $5M, >= 504 sessions (H019 universe: ~900-1,300 a month)
UNIQUE_STOCKS = 1800        # distinct stocks ever eligible 2010-2017 (+ warm-up history)
SESSIONS = 2770             # 2007-01 .. 2017-12 daily bars held (504-session warm-up before 2010 + response window)
QC_SLOWDOWN = 2.0           # assumed LEAN cloud node vs this container (conservative)
R_NULL = 5000


def timeit(f, reps):
    t = []
    for _ in range(reps):
        t0 = time.perf_counter()
        f()
        t.append(time.perf_counter() - t0)
    return float(np.median(t))


def main():
    out = dict(platform=platform.platform(), python=platform.python_version(), numpy=np.__version__)
    bars = [S.make_bars(seed=s, n=1100, kind="random") for s in (1, 2, 3)] + [S.make_bars(seed=7, n=700, kind="base")]
    snaps = []
    for b in bars:
        for t in (650, 699) if b["c"].size == 700 else (800, 950, 1099):
            snaps.append(timeit(lambda: C.snapshot_at(b, t), 10))
    out["snapshot_ms_median"] = round(1e3 * float(np.median(snaps)), 2)
    out["snapshot_ms_max"] = round(1e3 * float(np.max(snaps)), 2)
    b = bars[0]
    out["weekly_bars_ms"] = round(1e3 * timeit(lambda: C.weekly_bars(*(b[k][-756:] for k in "ohlcv"),
                                                                       b["week_id"][-756:]), 20), 3)
    s = C.snapshot_at(b, 1099)
    out["render_daily_plus_weekly_ms"] = round(1e3 * timeit(lambda: R.render_snapshot(
        b["o"], b["h"], b["l"], b["c"], b["v"], b["week_id"], s, C.sma, C.weekly_bars), 5), 1)
    d, w = R.render_snapshot(b["o"], b["h"], b["l"], b["c"], b["v"], b["week_id"], s, C.sma, C.weekly_bars)
    out["png_bytes_daily_weekly"] = [len(d), len(w)]
    tracemalloc.start()
    C.snapshot_at(b, 1099)
    out["snapshot_peak_kb"] = round(tracemalloc.get_traced_memory()[1] / 1024, 1)
    tracemalloc.stop()
    # null world at the real scale
    dates = P.make_dates(WEEKS, ELIGIBLE_PER_WEEK, seed=1)
    t0 = time.perf_counter()
    prep = H.prepare(dates)
    out["null_prepare_s"] = round(time.perf_counter() - t0, 2)
    out["real_world_s"] = round(timeit(lambda: H.run_world(prep), 2), 3)
    out["null_world_s"] = round(timeit(lambda: H.run_world(prep, seed=3), 3), 3)
    out["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    # capacity estimates
    n_snap = WEEKS * ELIGIBLE_PER_WEEK
    est = dict(
        snapshots=n_snap,
        snapshot_compute_min_local=round(n_snap * out["snapshot_ms_median"] / 1e3 / 60, 1),
        snapshot_compute_min_qc=round(QC_SLOWDOWN * n_snap * out["snapshot_ms_median"] / 1e3 / 60, 1),
        daily_panel_mb_float64=round(UNIQUE_STOCKS * SESSIONS * 5 * 8 / 2 ** 20, 1),
        score_table_mb=round(n_snap * (4 + 2 + 1 + 1 + 8 + 8 + 8 + 8) / 2 ** 20, 1),
        null_hours_local=round(R_NULL * out["null_world_s"] / 3600, 2),
        null_hours_qc=round(QC_SLOWDOWN * R_NULL * out["null_world_s"] / 3600, 2),
        null_output_kb=round(R_NULL * 2 * 12 / 1024, 1),
        rendering_all_snapshots_hours_local=round(n_snap * out["render_daily_plus_weekly_ms"] / 1e3 / 3600, 1),
    )
    out["capacity"] = est
    out["assumptions"] = dict(weeks=WEEKS, eligible_per_week=ELIGIBLE_PER_WEEK, unique_stocks=UNIQUE_STOCKS,
                              sessions=SESSIONS, qc_slowdown=QC_SLOWDOWN, r_null=R_NULL)
    (HERE / "h020_runtime.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
