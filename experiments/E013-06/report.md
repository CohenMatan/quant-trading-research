# E013-06 — S013 v1.1 (research)

C03 H013 S013 v1.1 seed 3 (one candidate per variation; seeds are replicates, D082) on IS, paired with null E962-24. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `83df3331adfe68d1a47e19ae09e387ab18c2d3c7` · **QC backtest:** `5c1afc8e56c21718609f6f98bd781082` · **LEAN:**  · **run:** 2026-09-30T16:11:10Z · **runtime:** 0s
- **Parameters:** `{'q': 0.1, 'stat': 'max', 'seed': 3, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
QCError: backtests/read: giving up after retries (ReadTimeout) [stage: backtest]
```
