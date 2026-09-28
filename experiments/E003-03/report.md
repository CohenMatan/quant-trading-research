# E003-03 — S003 v1.2 (research)

C01 H003 S003 v1.2 (pre-declared variation) on IS 2010-2017

- **Status:** failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `782d3a6413dc2ea0fb319aa1f78d9f50187e177b` · **QC backtest:** `` · **LEAN:**  · **run:** 2026-09-28T13:18:06Z · **runtime:** 0s
- **Parameters:** `{'rebalance': 'monthly', 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Error

```
QCError: backtests/create failed: ['Compile id not found: "e21bc1f599178f218db8f17f26dfed35-b9d0a5f612900a3db5aad52b79f505ed"']
```
