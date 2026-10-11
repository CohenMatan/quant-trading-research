# E026-08 — S026 v1.0 (research)

H024 REAL DEVELOPMENT SEARCH, EXACTLY ONCE (owner D201; research/phase9/H024_spec.md): the 11 frozen features and all 415 equal-weight 2-4 feature models on the 83 monthly decisions 2011-01-31..2017-11-30 (DEVELOPMENT / TRAINING data; one-month demeaned TSR; Spearman IC, Newey-West lag 2), the pinned c_MODEL = 4.3673 and c_FEATURE = 3.4533 (5,000 null worlds E026-02..06), gates D1-D6 + robust neighbourhood, the frozen selection rule, the walk-forward diagnostic with the pinned fold thresholds, feature stability, the Score v1 / H023 80/10/10 controls and the NON-GATING 2- / 3-month diagnostics; monthly matrices exported for offline recomputation (research/phase9/cp1/P9_CP1_result.py, committed before the run). No portfolio, no orders (the portfolio block is the approved d051 one, required by the research-config rule and unused by this non-trading host); refused unless the panel, population and library digests equal the pins. 2018-2021 and the Holdout sealed. Default build (recorded).

- **Status:** completed
- **Split:** IS (2011-01-03 → 2017-12-31)
- **Commit:** `047910138f509abdb7a7072be0f9299e7944f432` · **QC backtest:** `17612205d416a1604d2ca7f9ad8d4b8d` · **LEAN:** v2.5.0.0.18178 · **run:** 2026-10-11T12:06:56Z · **runtime:** 653s
- **Parameters:** `{'mode': 'real', 'spec_sha256': 'b28e580332bd350d20d34871c85f3288795e29810638881a0bc8893813cde4a5', 'pred_code_sha256': 'bc6fd8e83e7c105e50bbd05fabb23c61ac5229216af6599320962195d83f8da5', 'feature_code_sha256': 'f9b1c87e25ea3b98bda58496fab8eee55b47661116c622de5827362ba865465c', 'features': ['MOM', 'LOWVOL', 'GPA', 'ACC', 'BM', 'AG', 'REV1M', 'CBOP', 'HI52', 'CFP', 'EQA'], 'links': [], 'library_sha256': '6af3616f30256226b44f2612fd5e227fd0e56a47445c621b2bfd63edf7d23922', 'population_sha256': '791a2d4c8972b2d10465762d8a0a675f159d37b6cfab3ff185b2e6712c3b0bc8', 'panel_sha256': '09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0', 'c_model': 4.3672788679087295, 'c_feature': 3.4533403374111082, 'c_fold': {'2014': 5.226474685869657, '2015': 5.0028522952177354, '2016': 4.778611975498576, '2017': 4.4241903365718285}, 'null_result_sha256': 'db1cb1923b9aa0580a9c62fbd1238db8827033128239a7fa7530802404d2fc89', 'threshold_commit': '75117b03bac33ff652fde4cc7fcdd8f76d81919c'}`
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
