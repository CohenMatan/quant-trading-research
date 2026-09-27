# E000-01 — S000 v1.0 (demo)

PIPELINE DEMO ONLY (no hypothesis): 5-day reversal among 300 most liquid, 10 slots, 5-day hold. Starts 2010-01-04: QC's new Morningstar dataset has no MarketCap before ~2009 (E951-02/03).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2014-12-31)
- **Commit:** `755353fe5bbb4fc334fc9b375ccc700705d314a4` · **QC backtest:** `9a857667154c9264af5d981b69e195b0` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-27T21:21:30Z · **runtime:** 175s
- **Parameters:** `{'lookback': 5, 'hold_days': 5, 'slots': 10, 'pool': 300, 'weight': 0.098}`
- **Costs:** `{'slippage_bps': 10, 'commission': 'IB fixed via LEAN InteractiveBrokersFeeModel: $0.005/share, $1 min, 1% max'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2014-12-31 (1258 trading days) |
| CAGR | 3.15% |
| Annualised volatility | 24.95% |
| Sharpe (rf = 0) | 0.25 |
| Sortino | 0.35 |
| Max drawdown | -44.98% |
| Longest drawdown (trading days) | 724 |
| Calmar | 0.07 |
| Worst year | -24.47% |
| Worst month | -14.63% |
| Closed trades | 2470 |
| Win rate | 51.38% |
| Average winner | 4.04% |
| Average loser | -4.04% |
| Expectancy per trade | 0.11% |
| Profit factor | 1.02 |
| Average holding (calendar days) | 7.2 |
| Average exposure | 96.23% |
| Turnover (1-way, per year) | 48.72 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-01 | n/a | n/a | n/a |
| E901-01 | -14.23% | 1.22 | 0.83 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 36.09% |
| 2011 | -24.47% |
| 2012 | 20.05% |
| 2013 | 19.50% |
| 2014 | -20.84% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 1258 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2014-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 83283.94 |
| equity_complete | pass | chart rows 1258 vs algorithm days 1258 |
| no_leverage | pass | min cash/equity 0.0032 |
| cash_never_negative | pass | min cash/equity 0.0032 |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.2692361674484425e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `fd8323cb5f04cb00b5f7ed6a7e773bf23a4fdd7b31bf133545a14e0b3bce65c1`
- fills_sha256: `ff174510d01744a34d31662c49057015247a4193690f70d9015f690db90501e1`
- trades_sha256: `7815e4692156456290ec71b91e52dc1293ed7907bd810de8bbae76acac2c2b57`
