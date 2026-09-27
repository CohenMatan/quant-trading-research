# E950-01 — X950 v1.0 (infrastructure)

Execution-timing canary: verifies T+1 open fills, raw prices, slippage, on 8 large caps.

- **Status:** integrity_failed
- **Split:** FULL (1999-01-04 → 2021-12-31)
- **Commit:** `dc0e06cdc00398954c6d1325c778dd938cedf937` · **QC backtest:** `3581d568de15f70679f91e45412eea03` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-27T21:13:16Z · **runtime:** 19s
- **Parameters:** `{'weight': 0.24}`
- **Costs:** `{'slippage_bps': 10, 'commission': 'IB fixed via LEAN InteractiveBrokersFeeModel: $0.005/share, $1 min, 1% max'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.25, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | None → None (None trading days) |
| CAGR | n/a |
| Annualised volatility | n/a |
| Sharpe (rf = 0) | n/a |
| Sortino | n/a |
| Max drawdown | n/a |
| Longest drawdown (trading days) | None |
| Calmar | n/a |
| Worst year | n/a |
| Worst month | n/a |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | FAIL | 0 rows |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c08e4e3e54a2c715d78e0899b2b4235bc87bef97937fe9808da9e5e4717649d9`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
