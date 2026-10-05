"""P5-CP1 plumbing demo: renders SYNTHETIC snapshots only (no market data, no returns, no historical winners or losers).

python research/phase5/p5_demo.py  ->  research/phase5/demo/{base,random}_{daily,weekly}.png + demo_snapshots.json
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p5_chart as C  # noqa: E402
import p5_render as R  # noqa: E402
import p5_synth as S  # noqa: E402

OUT = HERE / "demo"


def jsonable(x):
    if isinstance(x, dict):
        return {k: jsonable(v) for k, v in x.items() if k not in ("pivots_daily", "pivots_weekly")}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else round(float(x), 6)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def main():
    OUT.mkdir(exist_ok=True)
    rec = {}
    for name, kind, seed in (("base", "base", 7), ("random", "random", 11)):
        b = S.make_bars(seed=seed, n=600, kind=kind)
        snap = C.snapshot(b["o"], b["h"], b["l"], b["c"], b["v"], b["week_id"])
        chk = C.checklist(snap)
        d = R.render(b["o"], b["h"], b["l"], b["c"], b["v"], 126, R.daily_overlays(snap, C.sma, b["c"], len(b["c"])))
        Wb = C.weekly_bars(b["o"], b["h"], b["l"], b["c"], b["v"], b["week_id"])
        w = R.render(Wb["o"], Wb["h"], Wb["l"], Wb["c"], Wb["v"], 104, R.weekly_overlays(Wb["c"], C.sma))
        files = {}
        for tag, cv in (("daily", d), ("weekly", w)):
            png = cv.png()
            (OUT / f"{name}_{tag}.png").write_bytes(png)
            files[tag] = hashlib.sha256(png).hexdigest()
        rec[name] = dict(kind=kind, seed=seed, bars=len(b["c"]), png_sha256=files, checklist=chk,
                         snapshot=jsonable({k: v for k, v in snap.items()}),
                         n_pivots_daily=len(snap["pivots_daily"]), n_pivots_weekly=len(snap["pivots_weekly"]))
    (OUT / "demo_snapshots.json").write_text(json.dumps(rec, indent=1, default=str) + "\n")
    for k, v in rec.items():
        print(k, v["checklist"], v["snapshot"]["weekly_state"], v["snapshot"]["daily_state"])


if __name__ == "__main__":
    main()
