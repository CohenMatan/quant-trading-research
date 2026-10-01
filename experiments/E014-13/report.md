# E014-13 — S014 v1.0 (sizing)

P2 $200K sensitivity (12 slots) of E014-01. Diagnostic, never used for selection. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** failed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `2d0383ba6945f3d261b0a532787a443d33bbd880` · **QC backtest:** `0bd46990b0ae4084d3d32c2c70a6088b` · **LEAN:**  · **run:** 2026-10-01T03:10:58Z · **runtime:** 0s
- **Parameters:** `{'mode': 'h014', 'exit': 'A', 'limit': 63, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
QCError: backtests/read: giving up after retries (ReadTimeout) [stage: backtest]
```
