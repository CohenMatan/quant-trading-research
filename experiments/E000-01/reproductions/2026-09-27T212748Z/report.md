# E000-01 — S000 v1.0 (demo)

PIPELINE DEMO ONLY (no hypothesis): 5-day reversal among 300 most liquid, 10 slots, 5-day hold. Starts 2010-01-04: QC's new Morningstar dataset has no MarketCap before ~2009 (E951-02/03).

- **Status:** failed
- **Split:** IS (2010-01-04 → 2014-12-31)
- **Commit:** `6de8b33989e6cf28ae49446bde39491a644c7124` · **QC backtest:** `332bc70b29bc103136134a7ea4dc2a15` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-27T21:27:48Z · **runtime:** 143s
- **Parameters:** `{'lookback': 5, 'hold_days': 5, 'slots': 10, 'pool': 300, 'weight': 0.098}`
- **Costs:** `{'slippage_bps': 10, 'commission': 'IB fixed via LEAN InteractiveBrokersFeeModel: $0.005/share, $1 min, 1% max'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02}`

## Error

```
analysis failed:
Traceback (most recent call last):
  File "/home/user/quant-trading-research/src/qresearch/run.py", line 234, in run
    an = analyse(cfg, raw)
         ^^^^^^^^^^^^^^^^^
  File "/home/user/quant-trading-research/src/qresearch/run.py", line 103, in analyse
    trades = build_trades(fills, splits)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/quant-trading-research/src/qresearch/trades.py", line 64, in build_trades
    raise LongOnlyViolation(f"sell of {sid} on {day} without an open position")
qresearch.trades.LongOnlyViolation: sell of APA R735QTJ8XC9X on 2014-12-12 without an open position

```
