# E804-01 — X804 v1.0 (infrastructure)

UB-1 universe baseline audit (owner D263; research/rr/universe_baseline/UB_protocol.md): X804 on QuantConnect's default build, 1999-01-04 .. 2021-12-31, month-end audit points 1999-02 .. 2021-11. U-A (vendor market cap) and U-B (shares x raw price x split factor) coverage, survivorship (later exits, censored), U-B validity tests and pre-2010 coverage. Aggregates only, 0 orders, no returns, no identifiers. Infrastructure.

- **Status:** completed
- **Split:** AUDIT (1999-01-04 → 2021-12-31)
- **Commit:** `0f11c81cfe6f90f6f0e35436fea4cbf69512a305` · **QC backtest:** `8d6d47e3d9256bba8b1a095d6da00001` · **LEAN:** v2.5.0.0.18194 · **run:** 2026-10-20T07:05:16Z · **runtime:** 257s
- **Parameters:** `{'ub_protocol_sha256': 'd5ce14e251cb910b463e05c8d5a611f00ee981eec5a586cb73de65d1fb7137ef', 'ub_code_sha256': {'main.py': 'feeaf55afa563faf11200b571500216ae06b471f8aaa437def44edbe727e76b6', 'qr_ub.py': 'dbb8eb671c153941d90a9aa023b305eadcf36cd9d4c8e8435a0632af024661ed'}}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (no order is placed in this run)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 1999-01-04 → 2021-12-31 (5788 trading days) |
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
| 1999 | 0.00% |
| 2000 | 0.00% |
| 2001 | 0.00% |
| 2002 | 0.00% |
| 2003 | 0.00% |
| 2004 | 0.00% |
| 2005 | 0.00% |
| 2006 | 0.00% |
| 2007 | 0.00% |
| 2008 | 0.00% |
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
| equity_nonempty | pass | 5788 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 1999-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 5788 vs algorithm days 5788 |
| equity_matches_qc_tradeable_dates | pass | chart rows 5788 vs QuantConnect tradeableDates 5788 |
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

- equity_sha256: `c0934c7bc401a8d7ab655ee5a10e5383122aa7012864e7743a072aca1a594f6b`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
