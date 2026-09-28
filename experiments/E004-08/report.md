# E004-08 — S004 v1.3 (research)

C01 H004 S004 v1.3 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E004-04 under D051 (no borrowing); S004 WINDOW_BARS bug fixed

- **Status:** failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `f0979cdf455b47cdbe44b01cd9b1ac5438c6eb6b` · **QC backtest:** `` · **LEAN:**  · **run:** 2026-09-28T23:06:30Z · **runtime:** 0s
- **Parameters:** `{'leader_frac': 0.2, 'drop': 0.05, 'hold_days': 10, 'slots': 15, 'regime_filter': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
QCError: backtests/create failed: ['There are no spare nodes available in your cluster. To launch a new backtest please stop an existing running backtest or add more compute nodes to your organization.']
```
