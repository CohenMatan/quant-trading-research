# E028-05 — S028 v1.0 (research)

P11-CP1 (owner D206): the ONE real H026 development run 2015-2021 (S028 real mode) with the pinned c_WEALTH, null result, threshold commit, feature- and response-panel digests: D1-D5, metrics, coefficients and the pre-registered diagnostics; final 2011-2021 model only if D1-D5 all pass. Research. Default build (recorded).

- **Status:** completed
- **Split:** DEV (2011-01-03 → 2021-12-31)
- **Commit:** `7ac01465c81b5d5a4c5325901463778b3da01793` · **QC backtest:** `613cee9d5df4812e5696cb3193362b0e` · **LEAN:** v2.5.0.0.18178 · **run:** 2026-10-11T20:22:19Z · **runtime:** 1261s
- **Parameters:** `{'mode': 'real', 'spec_sha256': '3c29288506bacb4be8ba8379e9e831c9779d2ff0c29e2adbefe47ffe709edc89', 'h026_code_sha256': '3b6249d48e338510f64d8eed92461469ad252d0170bf0e88ad00af414693eab6', 'data_v21_manifest_sha256': 'ef0a7a66f5ff1e746447cccdab3d812059192d474c6778ad307b946f4974a7bf', 'feature_panel_sha256': '10a54163c61e18662e33159f67f5dc2f6b25a1501901fbbc118d2524890d4f89', 'c_wealth': 0.22454658263960384, 'null_result_sha256': '3706b60525a0b98b6ad6f7dba2f115b3b712e982b8f7699e81c7334cfdc65b85', 'threshold_commit': '8024d90fcc3fcf9182b0177cb11efeb36de5b932', 'response_panel_sha256': 'e1503f9ccbe60cfb535f46fcdced64714c03a56683dece03f0334fffd714120b'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': False}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2011-01-03 → 2021-12-31 (2769 trading days) |
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
| E900-07 | -14.61% | 0.00 | n/a |

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
| 2018 | 0.00% |
| 2019 | 0.00% |
| 2020 | 0.00% |
| 2021 | 0.00% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2769 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2011-01-03..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 2769 vs algorithm days 2769 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2769 vs QuantConnect tradeableDates 2769 |
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

- equity_sha256: `181cd94e5e887eff9a05c10246c2e57ef3f74d4686d0536f79a8a777787cb70a`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
