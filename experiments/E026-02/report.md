# E026-02 — S026 v1.0 (infrastructure)

P9-CP1 (owner D201): H024 null worlds 1-1000 of 5,000: per world the frozen identity tether (qr_p7_pred.Tether(seed), the H022 seeds) re-indexes every stock's complete feature vector with one permutation per date; all 11 features and all 415 models of the pinned library are evaluated (qr_h024.null_record): max feature t_IC (c_FEATURE), max model t_IC (c_MODEL), fold-prefix maxima, the full-procedure summary (cstar). Refused unless the H022 panel (09b1de41...), the H024 population (791a2d4c...) and the library (6af3616f...) equal the pins. No real-assignment statistic. 2011-2017 only. Infrastructure. Default build (recorded).

- **Status:** completed
- **Split:** AUDIT (2011-01-03 → 2017-12-31)
- **Commit:** `231ef45fea033f4b8cfd8351454b1b064530dbc2` · **QC backtest:** `64fd3e7c63eca9f23db8f13298c80d6b` · **LEAN:** v2.5.0.0.18178 · **run:** 2026-10-11T10:26:09Z · **runtime:** 956s
- **Parameters:** `{'mode': 'null', 'spec_sha256': 'b28e580332bd350d20d34871c85f3288795e29810638881a0bc8893813cde4a5', 'pred_code_sha256': 'bc6fd8e83e7c105e50bbd05fabb23c61ac5229216af6599320962195d83f8da5', 'feature_code_sha256': 'f9b1c87e25ea3b98bda58496fab8eee55b47661116c622de5827362ba865465c', 'seeds': [1, 1000], 'features': ['MOM', 'LOWVOL', 'GPA', 'ACC', 'BM', 'AG', 'REV1M', 'CBOP', 'HI52', 'CFP', 'EQA'], 'links': [], 'library_sha256': '6af3616f30256226b44f2612fd5e227fd0e56a47445c621b2bfd63edf7d23922', 'population_sha256': '791a2d4c8972b2d10465762d8a0a675f159d37b6cfab3ff185b2e6712c3b0bc8', 'panel_sha256': '09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': False}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

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
