"""TT chart discovery (D302) — Stage 2: blinded daily candlestick charts for the Stage 1 sample.

Format (fixed before any chart was rendered or viewed):
  - the frozen H020 renderer qr_chart_render.render: 1000 x 640 PNG, white background, log price scale, volume panel,
    no text of any kind (no ticker, date, price axis or label); the decision bar is the last drawn bar, followed by a
    blank margin of 6 slots;
  - 252 reference sessions ending at the decision date (the last session before the sampled month), adjusted OHLC and
    adjusted volume (signals use adjusted prices; the absolute level is not shown);
  - overlays: 50- and 200-session simple moving averages of the adjusted close (ma_fast blue, ma_slow purple), each
    computed only from bars <= the decision date and drawn only where the full window lies on 2010+ bars (nothing
    before 2010 is read).
Every bar is selected with date <= decision date BEFORE any computation, so later bars cannot reach an image
(tests/test_chart_discovery.py checks this byte for byte).
Images are written to data/chart_discovery/charts/<chart id>.png (local, git-ignored). The committed
CHARTS_manifest.json holds only chart id -> PNG SHA-256 and the mapping SHA-256.

Usage:  python research/tt/chart_discovery/render.py data/wiki/<file>.csv
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "tt" / "wiki_audit"))
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
import qr_chart_render as cr  # noqa: E402
import wiki_audit as wa  # noqa: E402

N_BARS = 252
MAS = ((50, "ma_fast"), (200, "ma_slow"))
CHARTS = ROOT / "data" / "chart_discovery" / "charts"
MAPPING = ROOT / "data" / "chart_discovery" / "sample_mapping.json"
OUT = HERE / "CHARTS_manifest.json"


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    if x.size >= n:
        cs = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def chart_png(g: pd.DataFrame, decision_date: str) -> tuple[bytes, str]:
    """g: one ticker's rows on reference sessions (any dates). Returns the PNG bytes and the last drawn date."""
    g = g[g["date"] <= decision_date].sort_values("date", kind="mergesort")      # truncation first
    if len(g) < N_BARS:
        raise ValueError("fewer than 252 bars up to the decision date")
    o, h, l, c, v = (g[k].to_numpy(float) for k in ("adj_open", "adj_high", "adj_low", "adj_close", "adj_volume"))
    mas = [(sma(c, n), key) for n, key in MAS]
    cv = cr.render(o, h, l, c, v, N_BARS, {"mas": mas, "n_input": c.size})
    return cv.png(), g["date"].iloc[-1]


def main(path: str):
    man = json.loads(wa.MANIFEST.read_text())
    if wa.sha256(Path(path)) != man["sha256"]:
        raise SystemExit("file SHA-256 does not match WIKI_MANIFEST.json")
    sample = json.loads(MAPPING.read_text())
    df, _ = wa.load_wiki(Path(path))
    sessions = set(wa.reference_sessions(df))
    df = df[df["ticker"].isin({s["ticker"] for s in sample}) & df["date"].isin(sessions)]
    groups = dict(tuple(df.groupby("ticker", sort=False)))
    CHARTS.mkdir(parents=True, exist_ok=True)
    out = {}
    for s in sorted(sample, key=lambda s: s["chart_id"]):
        png, last = chart_png(groups[s["ticker"]], s["decision_date"])
        if last != s["decision_date"]:
            raise SystemExit(f"{s['chart_id']}: last drawn bar is not the decision date")
        (CHARTS / f"{s['chart_id']}.png").write_bytes(png)
        out[s["chart_id"]] = hashlib.sha256(png).hexdigest()
    OUT.write_text(json.dumps({"decision": "D302", "charts": len(out), "bars": N_BARS,
                               "mapping_sha256": hashlib.sha256(MAPPING.read_bytes()).hexdigest(),
                               "png_sha256": out}, indent=1) + "\n")
    print(f"rendered {len(out)} charts")


if __name__ == "__main__":
    main(sys.argv[1])
