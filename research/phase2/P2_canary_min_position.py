"""One-off verification of the $5,000 minimum new position in canary E965-02 ($60K): for every opening buy,
quantity x the price the harness planned with at the signal close (QuantConnect order record
orderSubmissionData.lastPrice, read-only) must be >= $5,000. Stores only counts, the minimum planned value and
fill/close gap ratios (no prices). Needs QC credentials.

    PYTHONPATH=src python research/phase2/P2_canary_min_position.py -> P2_canary_min_position.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from qresearch import results  # noqa: E402
from qresearch.qc_client import BacktestHandle, QCClient  # noqa: E402

EXP = Path(__file__).resolve().parents[2] / "experiments"


def main():
    prov = json.loads((EXP / "E965-02" / "result.json").read_text())["provenance"]
    orders = QCClient()._read_orders_once(BacktestHandle(int(prov["qc_project_id"]), prov["qc_backtest_id"], ""))
    by_id = {o["id"]: o for o in orders}
    fi = results.read_csv_gz(EXP / "E965-02" / "fills.csv.gz").sort_values(["date", "order_id"])
    held, opening = {}, []
    for f in fi.itertuples():
        q0 = held.get(f.symbol_id, 0)
        if q0 <= 0 and f.quantity > 0:
            opening.append(f)
        held[f.symbol_id] = q0 + f.quantity
    planned = [(f, f.quantity * by_id[f.order_id]["orderSubmissionData"]["lastPrice"]) for f in opening]
    gaps = sorted(((f.date, f.symbol, round(f.price / by_id[f.order_id]["orderSubmissionData"]["lastPrice"], 3))
                   for f, _ in planned if f.quantity * f.price < 5000), key=lambda x: x[2])[:3]
    res = dict(opening_buys=len(planned), planned_below_5000=sum(1 for _, v in planned if v < 5000),
               min_planned_value=round(min(v for _, v in planned), 2),
               fills_below_5000_at_open=sum(1 for f, _ in planned if f.quantity * f.price < 5000),
               largest_gaps_fill_over_signal_close=gaps)
    (Path(__file__).parent / "P2_canary_min_position.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(res)


if __name__ == "__main__":
    main()
