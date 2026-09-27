# E900-01 — B900 v1.0 (benchmark)

Benchmark: SPY buy-and-hold, dividends reinvested monthly.

- **Status:** integrity_failed
- **Split:** FULL (1999-01-04 → 2021-12-31)
- **Commit:** `cf78b395a12cda0a7fb2187a419d0ec049ad3e12` · **QC backtest:** `7a68f26f55ff7f068c8dc8bb68e1aee4` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-27T21:14:06Z · **runtime:** 15s
- **Parameters:** `{'weight': 0.98}`
- **Costs:** `{'slippage_bps': 10, 'commission': 'IB fixed via LEAN InteractiveBrokersFeeModel: $0.005/share, $1 min, 1% max'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02}`

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
