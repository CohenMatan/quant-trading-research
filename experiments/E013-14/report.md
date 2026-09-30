# E013-14 — S013 v1.0 (sizing)

C03 S2 ($200K, 20 positions) of E013-02. Diagnostic, not a trial. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `2a10d333d2246a9c1ddcc95d11bba21e2d8e24e8` · **QC backtest:** `81a6146b058619a4a49d315830a50cdf` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T18:26:27Z · **runtime:** 430s
- **Parameters:** `{'q': 0.2, 'stat': 'max', 'seed': 2, 'slots': 20, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.98% |
| Annualised volatility | 13.46% |
| Sharpe (rf = 0) | 0.84 |
| Sortino | 1.18 |
| Max drawdown | -18.00% |
| Longest drawdown (trading days) | 332 |
| Calmar | 0.61 |
| Worst year | 2.56% |
| Worst month | -8.19% |
| Closed trades | 642 |
| Win rate | 62.77% |
| Average winner | 9.83% |
| Average loser | -9.70% |
| Expectancy per trade | 2.56% |
| Profit factor | 1.61 |
| Average holding (calendar days) | 87.9 |
| Average exposure | 83.77% |
| Turnover (1-way, per year) | 3.55 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.36% | 0.86 | 0.91 |
| E901-07 | -2.95% | 0.81 | 0.94 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.51% |
| 2011 | 3.57% |
| 2012 | 17.37% |
| 2013 | 26.01% |
| 2014 | 9.39% |
| 2015 | 2.56% |
| 2016 | 8.34% |
| 2017 | 6.84% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 189509.70 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.102779; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1304 orders vs QuantConnect Total Orders 1304 |
| fills_match_harness_count | pass | downloaded fill events 1304 vs harness-recorded fills 1304 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1304 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `90b6bfeff3333187e636cf051edcca20e8e62be18fb872edcddbbe42397acd34`
- fills_sha256: `9c03e2fad5c3ba105e2e418555002e7987ad6b08af92d063d69853ffb1a7ce60`
- trades_sha256: `02a9adaa5c0ceb5f1f01a6cf578d45e5704e358b960bbd93dcfbb97b96d608eb`
