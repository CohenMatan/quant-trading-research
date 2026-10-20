# E805-02 — X805 v1.0 (infrastructure)

SCA-1 SEC classification audit (owner D267; research/rr/sec_classification/SCA_protocol.md): X805 on QuantConnect's default build, 2009-11-02 .. 2021-12-31, month-end points 2010-01 .. 2021-11. Public SEC registrants (plain JSON, Object Store) matched in-cloud by dated ticker evidence / share fingerprint to the vendor universe: matched / confirmed missing / possible missing / unresolved, gaps, survivorship bounds, frozen verdict. Aggregates only, 0 orders, no returns, no identifiers. Infrastructure.

- **Status:** completed
- **Split:** AUDIT (2009-11-02 → 2021-12-31)
- **Commit:** `bd0c83d8c441dd2d95becb7144fa345a1bad083b` · **QC backtest:** `53453716678265853dbccb043caded39` · **LEAN:** v2.5.0.0.18194 · **run:** 2026-10-20T10:42:42Z · **runtime:** 155s
- **Parameters:** `{'sca_protocol_sha256': 'a4cec4f5111adad28fe653f708fc1fd6264700f26538065ac16d5b8692e21b36', 'sca_code_sha256': {'main.py': 'eb88c69e9299c80b416bab339ee2786ac53d5cd3919c67fad072b98367d722ad', 'qr_sca.py': '38045153a769367b41f42c9fb858c9064deaf53fc11558ea5a07fcc14672dba5'}, 'sec_object_key': 'rr/sca_sec_v1.json', 'sec_reference_sha256': '67bc9260f3c5bed6ac723a0ed4b177dee9f9be5814f482200438687b0984a747'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (no order is placed in this run)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2009-11-02 → 2021-12-31 (3063 trading days) |
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
| equity_nonempty | pass | 3063 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2009-11-02..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 3063 vs algorithm days 3063 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3063 vs QuantConnect tradeableDates 3063 |
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

- equity_sha256: `529b170b31ff0d052f0dfbe2d2723d8dca2c866f5c5873614c2e079fd6235379`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
