# E808-01 — X808 v1.0 (infrastructure)

OD-1 outcome-driven discovery study (owner D308; research/od/OD1_protocol.md): X808 on QuantConnect's default build, 2010-01-04 .. 2021-12-31 without warm-up; UCR-1 repaired universe, month-end reviews 2011-01 .. 2021-11; technical features from the Fundamental stream, as-filed SEC fundamentals (rr/od1_sec_v1.json); forward outcomes 3/6/12/24 months never past 2021-11; aggregates only, 0 orders. EXPLORATORY.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2021-12-31)
- **Commit:** `ee9b1fa5f888b953c3e839996796d7c16e71dc3d` · **QC backtest:** `b486d51a4878de428927bb16f3da5069` · **LEAN:** v2.5.0.0.18203 · **run:** 2026-10-24T22:10:18Z · **runtime:** 337s
- **Parameters:** `{'od1_protocol_sha256': 'cc6b1d2cdff3b0aeaa6d3fe59d40e1a8595b841edcadcf93b5a567f3595f8bc6', 'od1_code_sha256': {'main.py': 'f7778bacafde1672dc4766695b44615c766cda3727967554c6dc238843880311', 'qr_od1.py': '679aee8f51c4b340d519e48c8b57ac586a9bf5616e002f01f2cf62f6167eed82', 'qr_os1.py': '07d6b03c92ad3b4741fcb32e3e3029bcfbbcc0fba091f3ca45f3de8c6dc9592a', 'qr_ucr.py': '77135cd38a1edfa8e6b295cf00255c34adb36780328bdd135cc3309e4a85e9d5'}, 'ucr_object_key': 'rr/ucr_sec_v1.json', 'ucr_reference_sha256': 'ba3ab515f6fad602f8638279927c4b5b3c417577851f7748891ff23be52a4a82', 'os1_object_key': 'rr/os1_sec_v1.json', 'os1_reference_sha256': '32bb0a666503e333ed20001074da687a12c557f28c85fa4b090b8b1983645b17', 'od1_object_key': 'rr/od1_sec_v1.json', 'od1_reference_sha256': '8bafcedea8a3b0f377f2b8642d9988ebd353e644e0e4964e95e3403b9dfa3d4d'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; no order is placed in this run'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
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

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 0.00% |
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
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
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

- equity_sha256: `e7d58685f65d2fea293c8dbc719045c30ba45694d2161652e9f5b591ef50c88b`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
