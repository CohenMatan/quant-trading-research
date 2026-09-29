# E003-05 — S003 v1.1 (research)

C01 H003 S003 v1.1 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E003-02 under D051 (no borrowing)

- **Status:** failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `712dd0573553a4efec518022a55ca636478dac78` · **QC backtest:** `` · **LEAN:**  · **run:** 2026-09-28T16:46:24Z · **runtime:** 0s
- **Parameters:** `{'rebalance': 'days', 'every_days': 10, 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
QCError: backtests/orders/read: giving up after retries (HTTP 500)
```
