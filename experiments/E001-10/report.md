# E001-10 — S001 v1.4 (research)

C01 H001 S001 v1.4 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E001-05 under D051 (no borrowing)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `0f2fac48af92b2fc61d8a421fffd6d94956ddcd4` · **QC backtest:** `94c8b34eeddb05d8aee070873817f130` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T15:22:06Z · **runtime:** 374s
- **Parameters:** `{'entry': 'ret3', 'ret3_max': -0.06, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.55% |
| Annualised volatility | 21.89% |
| Sharpe (rf = 0) | 0.69 |
| Sortino | 1.02 |
| Max drawdown | -30.43% |
| Longest drawdown (trading days) | 606 |
| Calmar | 0.45 |
| Worst year | -19.00% |
| Worst month | -15.01% |
| Closed trades | 316 |
| Win rate | 56.33% |
| Average winner | 5.15% |
| Average loser | -3.58% |
| Expectancy per trade | 1.34% |
| Profit factor | 1.89 |
| Average holding (calendar days) | 28.0 |
| Average exposure | 92.72% |
| Turnover (1-way, per year) | 1.39 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-05 | 0.21% | 1.17 | 0.77 |
| E901-04 | -0.19% | 1.14 | 0.80 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 27.39% |
| 2011 | -3.49% |
| 2012 | 23.99% |
| 2013 | 44.12% |
| 2014 | 29.04% |
| 2015 | 10.85% |
| 2016 | -19.00% |
| 2017 | 8.33% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97041.97 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.022132; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 648 orders vs QuantConnect Total Orders 648 |
| fills_match_harness_count | pass | downloaded fill events 647 vs harness-recorded fills 647 |
| commission_fixed_per_order | pass | 647 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `a12abc7922655a098871cde6d6615d27bc968da945f85327e94fcf9c5ca7b583`
- fills_sha256: `87555f92e0dbbe0870cd73ab7e6bef8bafdfed1c2289615897944ad5563a3164`
- trades_sha256: `d01e73a11175222173f90616511e601d13ddbc8cf3228e1b71fcc7aa145bdfb7`
