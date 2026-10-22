# E033-01 — S033 v1.0 (research)

H032 R1 (owner D282; research/os/H032_spec.md section 9 and research/os/H032_R_protocol.md): S033 on QuantConnect's default build; B1 traded in LEAN, controls and a shadow replay of B1 in the shadow engine; official start 2012-07-31 (frozen start review), history-only warm-up from 2009-05-01; $100,000, 10 bps slippage per side, $7 per order. EXPLORATORY.

- **Status:** completed
- **Split:** DEV (2012-07-31 → 2021-12-31)
- **Commit:** `aa3c015fda20ea513cf09dc346e85d9a436d3f24` · **QC backtest:** `101500a9ee437d19137d3743162b7098` · **LEAN:** v2.5.0.0.18201 · **run:** 2026-10-22T18:19:58Z · **runtime:** 349s
- **Parameters:** `{'h032_spec_sha256': '979af2e3944cfc75af617d959ed2e4354fe9f79e7cf48f6d608627cbc8db66aa', 'h032_r_protocol_sha256': 'dbe40049f3be7b0b562e95901050ffacde614f64945af2e97bf0b58b7c8d05fe', 'h032_r_code_sha256': {'main.py': '7c654a335c4c13e3c668f2504ebc5a7b0b073fc7f3faf0943e5d8d80d3f38728', 'qr_os1.py': '07d6b03c92ad3b4741fcb32e3e3029bcfbbcc0fba091f3ca45f3de8c6dc9592a', 'qr_os1_books.py': '788a4d410f3e8a98b56fe869ab2c84c69d5c91e14017fc12ecb46902bb5aa8a4', 'qr_os1_trade.py': 'e1c1a898045363964065b8bbf4e44a9e0e3c5257f3a9f166c7662f554145c967', 'qr_ucr.py': '77135cd38a1edfa8e6b295cf00255c34adb36780328bdd135cc3309e4a85e9d5', 'qr_x807.py': '877e265430bd90014cf2b60e4c3f2df7670fe55c88b89ff298ea3944f62fa7a2'}, 'start_review': '2012-07-31', 'ucr_object_key': 'rr/ucr_sec_v1.json', 'ucr_reference_sha256': 'ba3ab515f6fad602f8638279927c4b5b3c417577851f7748891ff23be52a4a82', 'os1_object_key': 'rr/os1_sec_v1.json', 'os1_reference_sha256': '32bb0a666503e333ed20001074da687a12c557f28c85fa4b090b8b1983645b17'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (harness and shadow engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2012-07-31 → 2021-12-31 (2372 trading days) |
| CAGR | 11.83% |
| Annualised volatility | 18.56% |
| Sharpe (rf = 0) | 0.70 |
| Sortino | 0.95 |
| Max drawdown | -43.98% |
| Longest drawdown (trading days) | 391 |
| Calmar | 0.27 |
| Worst year | -7.53% |
| Worst month | -25.86% |
| Closed trades | 210 |
| Win rate | 60.48% |
| Average winner | 26.91% |
| Average loser | -18.69% |
| Expectancy per trade | 8.89% |
| Profit factor | 1.72 |
| Average holding (calendar days) | 228.5 |
| Average exposure | 92.87% |
| Turnover (1-way, per year) | 1.39 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2012 | 10.81% |
| 2013 | 46.67% |
| 2014 | 9.40% |
| 2015 | -7.53% |
| 2016 | 7.79% |
| 2017 | 12.99% |
| 2018 | 0.80% |
| 2019 | 14.34% |
| 2020 | -0.37% |
| 2021 | 24.64% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2372 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2012-07-31..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 2372 vs algorithm days 2372 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2372 vs QuantConnect tradeableDates 2372 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 819 warm-up sessions |
| no_leverage | pass | min cash/equity 0.027065; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.0818751887864673e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 435 orders vs QuantConnect Total Orders 435 |
| fills_match_harness_count | pass | downloaded fill events 435 vs harness-recorded fills 435 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 435 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `24778a4897ae34e81e548ef567893c329f5c91785e6a75636ed0c27776f3784c`
- fills_sha256: `bded437f2fd7e5663498a91555c341eb62ef3a4b0af70da2a19f59600aeeca71`
- trades_sha256: `88035c772ba6c7f667035147a59b2fc3c69c91a0c8af29d13df90ca9eb263a99`
