"""Turn raw QC API payloads (orders, chart, logs) into canonical tables, files and hashes.

Canonical CSV text (fixed column order, fixed number formats, sorted rows, "\\n" line endings) is
what gets hashed, so a hash identifies the result independent of pandas versions or gzip metadata.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from .trades import FILL_COLUMNS, SPLIT_COLUMNS

NY = ZoneInfo("America/New_York")
EQUITY_COLUMNS = ["date", "equity", "cash", "npos", "nelig"]


def _ny_date(ts: float) -> str:
    return datetime.fromtimestamp(float(ts), tz=timezone.utc).astimezone(NY).strftime("%Y-%m-%d")


# ---------------------------------------------------------------- parsing
def parse_equity(series: dict[str, list]) -> pd.DataFrame:
    """Chart 'QR' series -> one row per trading day."""
    cols = {}
    for name in ("equity", "cash", "npos", "nelig"):
        pts = series.get(name, [])
        d: dict[str, float] = {}
        for p in pts:
            ts, val = (p["x"], p["y"]) if isinstance(p, dict) else (p[0], p[-1])
            if val is None:
                continue
            d[_ny_date(ts)] = float(val)   # last value of the day wins (one plot per day expected)
        cols[name] = pd.Series(d, dtype=float)
    df = pd.DataFrame(cols).sort_index()
    df.index.name = "date"
    df = df.reset_index()
    for c in ("npos", "nelig"):
        df[c] = df[c].fillna(0).round().astype(int)
    return df[EQUITY_COLUMNS]


def chart_table(series: dict[str, list]) -> pd.DataFrame:
    """Any custom chart -> one row per date, one column per series (last value of the day)."""
    cols = {}
    for name, pts in series.items():
        d = {}
        for p in pts:
            ts, val = (p["x"], p["y"]) if isinstance(p, dict) else (p[0], p[-1])
            if val is not None:
                d[_ny_date(ts)] = float(val)
        cols[name] = pd.Series(d, dtype=float)
    df = pd.DataFrame(cols).sort_index()
    df.index.name = "date"
    return df.reset_index()


def parse_fills(orders: list[dict]) -> pd.DataFrame:
    rows = []
    for o in orders:
        sym = o.get("symbol") or {}
        for ev in o.get("events") or []:
            if ev.get("status") not in ("filled", "partiallyFilled"):
                continue
            q = float(ev.get("fillQuantity") or 0)
            if q == 0:
                continue
            rows.append(dict(order_id=int(o["id"]), symbol_id=str(sym.get("id")),
                             symbol=str(sym.get("value")), date=_ny_date(ev["time"]), quantity=q,
                             price=float(ev.get("fillPrice") or 0.0),
                             fee=float(ev.get("orderFeeAmount") or 0.0), tag=str(o.get("tag") or "")))
    df = pd.DataFrame(rows, columns=FILL_COLUMNS)
    return df.sort_values(["date", "order_id"], kind="mergesort").reset_index(drop=True)


def parse_logs(lines: list[str]) -> tuple[pd.DataFrame, dict, list[str]]:
    """Returns (split events of held symbols, QRSUMMARY dict, other QR* lines)."""
    splits, other, summary = [], [], {}
    for ln in lines:
        i = ln.find("QR")
        if i < 0:
            continue
        body = ln[i:]
        if body.startswith("QRSUMMARY|"):
            summary = json.loads(body.split("|", 1)[1])
        elif body.startswith("QRSPLIT|"):
            _, sid, day, factor = body.split("|")
            splits.append(dict(symbol_id=sid, date=day, factor=float(factor)))
        elif body.startswith("QR"):
            other.append(body)
    return pd.DataFrame(splits, columns=SPLIT_COLUMNS), summary, other


def apply_forced_fees(fills: pd.DataFrame, qr_lines: list[str]) -> tuple[pd.DataFrame, int]:
    """Mirror the harness's cash debits for LEAN-generated orders (delisting liquidations), which the
    Orders API reports with a $0 fee (D049). Each QRFORCEDFEE|order_id|amount line sets the fee of that
    order's first fill row. Returns (fills, number of debits applied)."""
    debits = {}
    for ln in qr_lines:
        if ln.startswith("QRFORCEDFEE|"):
            _, oid, amt = ln.split("|")
            debits[int(oid)] = float(amt)
    if not debits or fills.empty:
        return fills, 0
    fills = fills.copy()
    applied = 0
    for oid, amt in debits.items():
        idx = fills.index[fills["order_id"] == oid]
        if len(idx) and float(fills.loc[idx, "fee"].sum()) == 0.0:
            fills.loc[idx[0], "fee"] = amt
            applied += 1
    return fills, applied


def lines_from_statistics(st: dict) -> list[str]:
    """Rebuild the harness's result lines from summary statistics (D046): the qr_summary JSON as a
    QRSUMMARY line, followed by the message chunks qr_msgs_00.. in order."""
    lines = ["QRSUMMARY|" + st["qr_summary"]]
    n = int(st.get("qr_msgs_n", "0") or 0)
    text = "".join(st.get(f"qr_msgs_{i:02d}", "") for i in range(n))
    if n and any(f"qr_msgs_{i:02d}" not in st for i in range(n)):
        raise ValueError("incomplete qr_msgs chunks in summary statistics")
    lines += [ln for ln in text.split("\n") if ln]
    return lines


# ---------------------------------------------------------------- canonical text + hashes
_FMT = {"equity": "{:.2f}", "cash": "{:.2f}", "price": "{:.6f}", "fee": "{:.4f}", "quantity": "{:.4f}",
        "factor": "{:.10f}", "cost": "{:.4f}", "proceeds": "{:.4f}", "fees": "{:.4f}",
        "pnl": "{:.4f}", "ret": "{:.8f}", "max_qty": "{:.4f}"}


def canonical_csv(df: pd.DataFrame) -> str:
    out = io.StringIO()
    out.write(",".join(df.columns) + "\n")
    for row in df.itertuples(index=False):
        cells = []
        for col, v in zip(df.columns, row):
            if isinstance(v, float) and v != v:
                cells.append("")
            elif col in _FMT and v != "":
                cells.append(_FMT[col].format(float(v)))
            else:
                s = str(v)
                cells.append('"' + s.replace('"', '""') + '"' if ("," in s or '"' in s) else s)
        out.write(",".join(cells) + "\n")
    return out.getvalue()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_gz(path: Path, text: str) -> None:
    """Deterministic gzip (mtime=0, no filename) so identical content gives identical bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(text.encode("utf-8"))


def read_csv_gz(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, compression="gzip", keep_default_na=False, na_values=[""])
