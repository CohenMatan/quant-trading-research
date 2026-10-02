# E980-01 — X980 v1.0 (infrastructure)

H016 non-candidate technical canary: byte copy of S016, random book seed 0 (not a control seed), full common window. Checks PIT timing, universe exclusions, quarterly dates, 20 positions, the $4,000 minimum, the 15% reserve, at most one top-up >= $250 per new position, no leverage, cash/commission reconciliation, the 2010-03-01 start. The GP/A ranking is shadow-computed only (counts and a hash). Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-03-01 → 2021-12-31)
- **Commit:** `5c2b25eb66e4e12eeed66739087410ecbed7ab26` · **QC backtest:** `44542af4edb42f81a96efddc084b80f9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-02T14:58:29Z · **runtime:** 1048s
- **Parameters:** `{'slots': 20, 'months': [3, 6, 9, 12], 'book': 'random', 'seed': 0, 'canary': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 14.21% |
| Annualised volatility | 18.21% |
| Sharpe (rf = 0) | 0.82 |
| Sortino | 1.15 |
| Max drawdown | -35.97% |
| Longest drawdown (trading days) | 429 |
| Calmar | 0.40 |
| Worst year | -8.32% |
| Worst month | -14.12% |
| Closed trades | 69 |
| Win rate | 52.17% |
| Average winner | 49.41% |
| Average loser | -17.93% |
| Expectancy per trade | 17.20% |
| Profit factor | 2.50 |
| Average holding (calendar days) | 597.0 |
| Average exposure | 96.40% |
| Turnover (1-way, per year) | 0.24 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -0.67% | 1.00 | 0.91 |
| E901-07 | 0.83% | 0.95 | 0.94 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 28.10% |
| 2011 | -8.32% |
| 2012 | 12.79% |
| 2013 | 34.21% |
| 2014 | 12.89% |
| 2015 | 6.07% |
| 2016 | 14.86% |
| 2017 | 18.22% |
| 2018 | -7.80% |
| 2019 | 27.01% |
| 2020 | 20.28% |
| 2021 | 18.42% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97593.12 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 418 warm-up sessions |
| no_leverage | pass | min cash/equity 0.019840; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 9 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.017355591316655e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 240 orders vs QuantConnect Total Orders 240 |
| fills_match_harness_count | pass | downloaded fill events 240 vs harness-recorded fills 240 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 240 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `a59e98d974f0f84a79371dd6de151257b56465ae9b8fb1f289119dcae2092064`
- fills_sha256: `d6fdb9be0e84c43841528685f027b170ef1d1de2c9f517f3d9481bc58479f7d1`
- trades_sha256: `b05318023fdcd483c00b1dc61a7dedf600204df1c73b6e969528fb41d85b6143`
