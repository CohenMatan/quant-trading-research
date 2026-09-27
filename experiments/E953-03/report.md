# E953-03 — X953 v1.0 (infrastructure)

Size proxy vs OLD dataset (survivor-only MarketCap) 1999-2009: recall on survivors, failed-company capture, survivorship return gap. LEAN 18130 = master with old dataset (retired 2026-10-31).

- **Status:** failed
- **Split:** IS (1999-01-04 → 2009-12-31)
- **Commit:** `5bfee9d748d428d005784139128d9a682f004585` · **QC backtest:** `` · **LEAN:**  · **run:** 2026-09-27T22:22:03Z · **runtime:** 0s
- **Parameters:** `{'eval_from': '1999-04-01', 'forward_returns_until': '2009-12-31'}`
- **Costs:** `{'slippage_bps': 10, 'commission': 'IB fixed via LEAN InteractiveBrokersFeeModel: $0.005/share, $1 min, 1% max'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02}`

## Error

```
QCError: backtests/read/log failed: ['You have exceeded your daily backtest logs allocation. Please upgrade your plan to continue.']
```
