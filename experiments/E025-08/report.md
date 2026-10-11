# E025-08 — S025 v1.0 (research)

H023 REAL DEVELOPMENT SEARCH, EXACTLY ONCE (owner D199; research/phase8/H023_spec.md): all 92 pre-registered layer weightings Score_v2 = wT*Tech/40 + wF*Fund/45 + wS*Sect/15 of the frozen Score v1 on the 83 monthly decisions 2011-01-31..2017-11-30 (TRAINING / DEVELOPMENT data for H023; one-month demeaned TSR response; Spearman IC, Newey-West lag 2), the pinned c_SEARCH = 2.9225785052912165 (5,000 optimiser-null worlds E025-02..06), development filters D1-D5, robust plateau and the frozen medoid selection rule, the walk-forward diagnostic with the pinned fold thresholds, structure counts and the NON-GATING 2- / 3-month diagnostics; monthly matrices exported for offline recomputation (research/phase8/cp1/P8_CP1_result.py, committed before the run). No portfolio, no orders (the portfolio block is the approved d051 one, required by the research-config rule and unused by this non-trading host); refused unless the panel (09b1de41...) and layer-subtotal (7652f7fc...) digests equal the pins. 2018-2021 and the Holdout sealed. Default build (recorded).

- **Status:** completed
- **Split:** IS (2011-01-03 → 2017-12-31)
- **Commit:** `504009e3a2665d5a7e40a5d24cecf52b195ea3fc` · **QC backtest:** `8df0e79984516243710fc178f8a500b5` · **LEAN:** v2.5.0.0.18178 · **run:** 2026-10-11T08:53:11Z · **runtime:** 581s
- **Parameters:** `{'mode': 'real', 'spec_sha256': '34e8e738c1df263fb726f3936b7488dc70da7f84203e20e84683a2dfbb9cf470', 'pred_code_sha256': 'bc6fd8e83e7c105e50bbd05fabb23c61ac5229216af6599320962195d83f8da5', 'grid_code_sha256': '60ac2fc67149c0a9b86dd95616b44bd154ca47d51c7fbefd389c9f6db47afce4', 'c_search': 2.9225785052912165, 'c_fold': {'2014': 3.486801872690062, '2015': 3.5098267772816225, '2016': 3.5872288855328005, '2017': 3.0235170098563535}, 'null_result_sha256': '2819cd4c803684e4f19e93d3b97bedf73feab1d105e295227f501dc1ec997190', 'threshold_commit': '8b86665dc2624910dfe68b8e8ab89903edf8ada3', 'panel_sha256': '09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0', 'components_sha256': '7652f7fca2c0bd68b9d23ba0a9eea4b2f850b1555ec3874ec9127a48b067509e'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': False}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2011-01-03 → 2017-12-29 (1761 trading days) |
| CAGR | 0.00% |
| Annualised volatility | 0.00% |
| Sharpe (rf = 0) | n/a |
| Sortino | n/a |
| Max drawdown | 0.00% |
| Longest drawdown (trading days) | 0 |
| Calmar | n/a |
| Worst year | 0.00% |
| Worst month | 0.00% |
| Closed trades | 0 |
| Win rate | n/a |
| Average winner | n/a |
| Average loser | n/a |
| Expectancy per trade | n/a |
| Profit factor | n/a |
| Average holding (calendar days) | n/a |
| Average exposure | 0.00% |
| Turnover (1-way, per year) | 0.00 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -13.19% | 0.00 | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2011 | 0.00% |
| 2012 | 0.00% |
| 2013 | 0.00% |
| 2014 | 0.00% |
| 2015 | 0.00% |
| 2016 | 0.00% |
| 2017 | 0.00% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 1761 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2011-01-03..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 1761 vs algorithm days 1761 |
| equity_matches_qc_tradeable_dates | pass | chart rows 1761 vs QuantConnect tradeableDates 1761 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 632 warm-up sessions |
| no_leverage | pass | min cash/equity 1.000000; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=0.0 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 0 orders vs QuantConnect Total Orders 0 |
| fills_match_harness_count | pass | downloaded fill events 0 vs harness-recorded fills 0 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | no fills downloaded; harness recorded 0 fills |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `fd2976e77f7ef0df9c799d33912f39ede4176238baf836e80d3fb8d9ade279b6`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
