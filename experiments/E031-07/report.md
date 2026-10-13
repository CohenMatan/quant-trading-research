# E031-07 — S031 v1.1 (infrastructure)

P14-CP3b (owner D233, Amendment 1): S031 v1.1 sector-stratified null worlds 1-2500 (six-signal vectors tethered whole among same-FF12-sector H029-eligible stocks; H028 real). Null rows only. Infrastructure. Default build.

- **Status:** completed
- **Split:** AUDIT (2011-01-03 → 2021-12-31)
- **Commit:** `fcd06ca954d3cd529d2113e883ec38e8fbdb59f1` · **QC backtest:** `c0e73f923a22b9e8d48374b2d5ec2e7c` · **LEAN:** v2.5.0.0.18179 · **run:** 2026-10-13T05:49:02Z · **runtime:** 1764s
- **Parameters:** `{'mode': 'null', 'spec_sha256': '51121154b3efaf770ce8c82879dc56fc36a1f6b7891e2920cf67c72dba0f345a', 'amendment1_sha256': 'df620018a4359534420294758c817cdfb2dfa84cd5ebe29d15771b1d8667d4ad', 'h029_code_sha256': '9407ac0ebca1a7b95cdd8757597572e6e9bbad69df8469c9a94dc6a0f745811d', 'h028_result_sha256': '41c265e1c6b71c9fbb04c1a83a13414e1ea9a20f01fbbd341c22088f98b3639c', 'data_v3_manifest_sha256': '601d00623e97696bd81f5a18e4b604482eba2da67acf31b8085f2e455a2fefcb', 'guard_sha256': 'd4e1065baec3786d29d30397cf21fc7f8d298b52455e8b1f156b377bd680996a', 'h029_panel_digests_sha256': '5145232485a4de3c1782b7f754ea886eceb65464e4f66b0a62d0919576bc601e', 'h026_feature_panel_sha256': '10a54163c61e18662e33159f67f5dc2f6b25a1501901fbbc118d2524890d4f89', 'h026_response_panel_sha256': 'e1503f9ccbe60cfb535f46fcdced64714c03a56683dece03f0334fffd714120b', 'h028_real_wealth': 328294.90847351257, 'lv15_real_wealth': 220156.03484878788, 'h028_coefficients': {'2015': {'b0': 4.092878595657308e-06, 'beta': [0.0008861445469498317, -0.0024034881108845286, 0.0024665099528579006, 0.0021923456296783586, -0.002406947379709375, -0.0031682154231527913, -0.0020252668166985776, 0.0008241524681556861, 0.0006282037633396782, 0.00497948630466988, -0.004509086195325488]}, '2016': {'b0': 1.3893123049256875e-06, 'beta': [0.001072173331032608, -0.004002051214464988, 0.00417240155468638, 0.0011734940112191018, -0.004860350330575943, -0.0027066023990919065, -0.0013220576393204878, 0.0005672868243490726, 0.002415744475549055, 0.0018282830872167555, -0.004467564772582784]}, '2017': {'b0': 3.195287560312463e-06, 'beta': [-0.0011027088150266469, -0.0055067745620752655, 0.00216393221124931, 0.0018342351454430396, -0.0035582974649125314, -0.004257407121028683, -0.002541981614107487, 0.00096550718288309, 0.0021219668755496045, 0.003352274919731063, -0.004083736612394024]}, '2018': {'b0': 9.295183655870165e-07, 'beta': [-0.0017807407442349834, -0.0066887459038543155, 0.0027507680526347045, -0.001022515060973328, -0.004759198186000372, -0.0018466520328368472, -0.0018676515903827107, 0.0015294606982324801, 0.003297676783524045, 0.001178324790277083, -0.004224180341285307]}, '2019': {'b0': 1.6383754830289992e-06, 'beta': [-0.0020743613637853285, -0.0067618740899339815, 0.005981218208075949, 0.0018018943659367694, -0.0073005469376562215, -0.0019291325970983526, -0.00122579716238058, 0.0029505505341758725, 0.00418253697878807, -0.0015360658608032612, -0.003497930969035638]}, '2020': {'b0': 1.0818950626602085e-07, 'beta': [-0.004465642167830346, -0.007794890863802191, 0.006177399367347753, 6.793608608789593e-05, -0.008626234539534065, -0.0006883359161581475, -0.0020756827519272467, 0.0024921511727668435, 0.0029412136005714123, -0.003248275561862691, -0.0045630464778058525]}, '2021': {'b0': -3.7787905245758863e-06, 'beta': [-0.0026144842160569053, -0.004902727309099373, 0.006786677697235323, 1.6098170952901748e-05, -0.012378056949621683, 0.0018704214841266148, -0.000931817714050281, 0.002735610394948716, 0.001722429948961732, -0.008123128005813883, -0.0035575302706358806]}}, 'seeds': [1, 2500]}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per order, 0.10% slippage (the portfolio is simulated in-host; no order is placed)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': False}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

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
