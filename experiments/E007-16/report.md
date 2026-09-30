# E007-16 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): plateau: time stop 40 -> 32 (pre-declared in research/cycles/C02_robustness_plan.md) | TECHNICAL REPEAT of E007-12 (runner lost in a container restart; identical configuration; D069)

- **Status:** failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `568ff471fd7cd1fbe44fbfd6d60431e2f592940a` · **QC backtest:** `eddea030ec6e7842417b28de32c1d7fc` · **LEAN:**  · **run:** 2026-09-30T06:19:09Z · **runtime:** 0s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.6, 'use_trend': True, 'time_stop': 32, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
QCError: backtests/read: giving up after retries (ReadTimeout) [stage: backtest]
```
