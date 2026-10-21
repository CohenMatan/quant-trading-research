# E807-02 — X807 v1.0 (infrastructure)

H032 canary C-OS1 (owner D278; research/os/H032_spec.md): X807 on QuantConnect's default build, 2009-05-01 .. 2021-12-31, month-end reviews 2010-01 .. 2021-11. UCR-1 repaired universe; point-in-time identity, SIC, split-adjusted net share issuance and fiscal-year OCF / same-filing revenue-growth filters from two public SEC objects; coverage gates G-COV1-3, mechanical start, subperiod lengths; H032 books by name only and their in-run recomputation. Aggregates only, 0 orders, no returns, no identifiers.

- **Status:** completed
- **Split:** AUDIT (2009-05-01 → 2021-12-31)
- **Commit:** `8623b4f5f36653c72d22f4185b3033f3cf1de8c2` · **QC backtest:** `fae482142b5ea14d3f8cfe88bad23704` · **LEAN:** v2.5.0.0.18200 · **run:** 2026-10-21T15:07:31Z · **runtime:** 272s
- **Parameters:** `{'h032_spec_sha256': '979af2e3944cfc75af617d959ed2e4354fe9f79e7cf48f6d608627cbc8db66aa', 'h032_code_sha256': {'main.py': '877e265430bd90014cf2b60e4c3f2df7670fe55c88b89ff298ea3944f62fa7a2', 'qr_os1.py': '07d6b03c92ad3b4741fcb32e3e3029bcfbbcc0fba091f3ca45f3de8c6dc9592a', 'qr_ucr.py': '77135cd38a1edfa8e6b295cf00255c34adb36780328bdd135cc3309e4a85e9d5'}, 'ucr_object_key': 'rr/ucr_sec_v1.json', 'ucr_reference_sha256': 'ba3ab515f6fad602f8638279927c4b5b3c417577851f7748891ff23be52a4a82', 'os1_object_key': 'rr/os1_sec_v1.json', 'os1_reference_sha256': '32bb0a666503e333ed20001074da687a12c557f28c85fa4b090b8b1983645b17'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (no order is placed in this run)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2009-05-01 → 2021-12-31 (3191 trading days) |
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
| 2009 | 0.00% |
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
| equity_nonempty | pass | 3191 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2009-05-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 3191 vs algorithm days 3191 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3191 vs QuantConnect tradeableDates 3191 |
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

- equity_sha256: `7427a8d8bf873531c72d6ad9c1d3677e768ee9e18b965d23a0aff088be7eb5a5`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
