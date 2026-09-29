# E003-06 — S003 v1.2 (research)

C01 H003 S003 v1.2 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E003-03 under D051 (no borrowing)

- **Status:** failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `93b56c46cbe30d98e9b8dc6b37637ea8478065f2` · **QC backtest:** `` · **LEAN:**  · **run:** 2026-09-28T17:05:26Z · **runtime:** 0s
- **Parameters:** `{'rebalance': 'monthly', 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
QCError: Backtest 3ec1dd8c0ae39b72ddf9acfa2350cbbd timed out
```
