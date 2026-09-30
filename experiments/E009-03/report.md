# E009-03 — S009 v1.2 (research)

C02 H009 S009 v1.2 (pre-declared selection candidate, D069) on IS 2010-2017: weekly (5-day) formation, hold 20

- **Status:** completed_with_warnings
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `6ebff2883124fd24a892174c006a15b8ae51639c` · **QC backtest:** `dc1a1bc1eacd26c14bb4456c116db319` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T00:03:20Z · **runtime:** 819s
- **Parameters:** `{'vol_mult': 2.5, 'days': 5, 'hold': 20, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.44% |
| Annualised volatility | 13.56% |
| Sharpe (rf = 0) | 1.00 |
| Sortino | 1.40 |
| Max drawdown | -16.60% |
| Longest drawdown (trading days) | 230 |
| Calmar | 0.81 |
| Worst year | -2.30% |
| Worst month | -6.58% |
| Closed trades | 901 |
| Win rate | 56.71% |
| Average winner | 5.80% |
| Average loser | -5.10% |
| Expectancy per trade | 1.08% |
| Profit factor | 1.52 |
| Average holding (calendar days) | 30.1 |
| Average exposure | 89.13% |
| Turnover (1-way, per year) | 10.88 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 0.10% | 0.75 | 0.80 |
| E901-07 | -0.48% | 0.73 | 0.84 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 13.32% |
| 2011 | -2.30% |
| 2012 | 9.92% |
| 2013 | 37.12% |
| 2014 | 13.23% |
| 2015 | 3.05% |
| 2016 | 6.96% |
| 2017 | 31.45% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 95993.22 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.031092; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 22 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.346887029444183e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1815 orders vs QuantConnect Total Orders 1815 |
| fills_match_harness_count | pass | downloaded fill events 1811 vs harness-recorded fills 1811 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | warn | 1 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 1 mirrored |
| commission_fixed_per_order | pass | 1812 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `dc930f9fb04d37a82ae75cb116f227f648e24210a1e3fb34718ef2e2834dce15`
- fills_sha256: `a1bf2b843cf3db63e53ddc2e8388e3c89e421d00b72766b2e9b7c36bb7d53101`
- trades_sha256: `a4a38fb949bf8e49882c9d284ee68edc255ee6bac7cb1609c783f37519c21279`
