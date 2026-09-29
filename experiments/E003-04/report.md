# E003-04 — S003 v1.0 (research)

C01 H003 S003 v1.0 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E003-01 under D051 (no borrowing)

- **Status:** failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `ef1c066198982eed5b81a6f132866366e0963b51` · **QC backtest:** `` · **LEAN:**  · **run:** 2026-09-28T16:00:56Z · **runtime:** 0s
- **Parameters:** `{'rebalance': 'monthly', 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
QCError: backtests/orders/read failed: ['Error retrieving orders result, please try again later']
```
