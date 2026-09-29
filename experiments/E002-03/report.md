# E002-03 — S002 v1.2 (research)

C01 H002 S002 v1.2 (pre-declared variation) on IS 2010-2017

- **Status:** failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `dd829bfadab4588ce1457258d59af953cf2fada4` · **QC backtest:** `` · **LEAN:**  · **run:** 2026-09-28T12:22:45Z · **runtime:** 0s
- **Parameters:** `{'lookback': 252, 'skip': 21, 'every_months': 1, 'slots': 15, 'band': 0.25, 'regime_filter': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Error

```
QCError: orders incomplete after 1800s: downloaded 1076 of 1076 orders, 1020 lack fill events
```
