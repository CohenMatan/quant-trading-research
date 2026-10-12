# E030-05 — S030 v1.0 (research)

P13-CP1 (owner D217): the ONE real H028 development run 2015-2021 (S030 real mode): lambda = 100 for every fit; H027 reproduction, 2016-2021 equality vs H027 (pinned tolerance), LV15_CONTROL, gates B1-B6 against the pinned c_WEALTH_H028, diagnostics; final score only if B1-B6 all pass. Research. Default build.

- **Status:** completed
- **Split:** DEV (2011-01-03 → 2021-12-31)
- **Commit:** `c1cfe245c6cba17de160894aa059b7429fd385aa` · **QC backtest:** `f03e3bdb7f780d5d3b54fed9cdc4a616` · **LEAN:** v2.5.0.0.18178 · **run:** 2026-10-12T10:44:59Z · **runtime:** 1189s
- **Parameters:** `{'mode': 'real', 'spec_sha256': '39b205c2b50172b8d7f89a013e08423e5cec8cfd632b574c0b90cc8aba6b7d18', 'h028_code_sha256': 'f92eb5f6e6cadb23c6542052d4149ddc35c787649992a4f7795adf4ca1b3f0be', 'data_v21_manifest_sha256': 'ef0a7a66f5ff1e746447cccdab3d812059192d474c6778ad307b946f4974a7bf', 'h026_feature_panel_sha256': '10a54163c61e18662e33159f67f5dc2f6b25a1501901fbbc118d2524890d4f89', 'h026_response_panel_sha256': 'e1503f9ccbe60cfb535f46fcdced64714c03a56683dece03f0334fffd714120b', 'h027_real_wealth': 311396.7708031718, 'h027_real_s_wealth': 0.17148195882657039, 'h027_lambda_schedule': [0.01, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0], 'c_wealth_h028': 0.056125732120069, 'null_result_sha256': 'f5c1401ba7faa4d37f86662ff409d028df7870343b61e06ff30b25d614be4ffe', 'threshold_commit': '76f172e13ba0985650a7389208d8edc17fb026af', 'tolerance': {'2016': {'ret': 0.009007340054033253, 'turnover': 0.18431948944490628}, '2017': {'ret': 0.004244822721305108, 'turnover': 0.07091525372131358}, '2018': {'ret': 0.0038521977289630582, 'turnover': 0.025}, '2019': {'ret': 0.0030989247820020216, 'turnover': 0.025}, '2020': {'ret': 0.0032547503506195063, 'turnover': 0.025}, '2021': {'ret': 0.00268444125519518, 'turnover': 0.025}}, 'tolerance_sha256': 'a754d355ae96b77d9a5c2d0c8a5a80ecda8e2ac24b5075c25f25645a7c0c0128'}`
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
