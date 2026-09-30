# E011-02 — S011 v1.1 (research)

C02 H011 S011 v1.1 (pre-declared selection candidate, D069) on IS 2010-2017: 10 annual lags (pre-2010 prices as warm-up only)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `053f0b2fe3f73c8f308842b34614e5652c10105f` · **QC backtest:** `73f7b309e57ff9d00aea53e143fdb5b1` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T01:19:44Z · **runtime:** 1141s
- **Parameters:** `{'lags': 10, 'trend_filter': False, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.21% |
| Annualised volatility | 18.31% |
| Sharpe (rf = 0) | 0.67 |
| Sortino | 0.95 |
| Max drawdown | -43.05% |
| Longest drawdown (trading days) | 701 |
| Calmar | 0.26 |
| Worst year | -14.10% |
| Worst month | -20.93% |
| Closed trades | 887 |
| Win rate | 54.68% |
| Average winner | 8.70% |
| Average loser | -7.77% |
| Expectancy per trade | 1.24% |
| Profit factor | 1.25 |
| Average holding (calendar days) | 30.6 |
| Average exposure | 80.31% |
| Turnover (1-way, per year) | 9.67 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.13% | 0.97 | 0.76 |
| E901-07 | -2.72% | 0.96 | 0.81 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 26.70% |
| 2011 | 7.10% |
| 2012 | 11.14% |
| 2013 | 40.26% |
| 2014 | 21.41% |
| 2015 | -14.10% |
| 2016 | -8.79% |
| 2017 | 16.08% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97803.91 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.111798; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.209735034398567e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1795 orders vs QuantConnect Total Orders 1795 |
| fills_match_harness_count | pass | downloaded fill events 1784 vs harness-recorded fills 1784 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1784 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ca453170ef266f1ccb8e98d862bbc3ff8f017ec88e2bb5c8ccc54be4607ffbd7`
- fills_sha256: `deb7423b274f2bdc6bf9b126db48fec56b842cec07a010709d6fcbdc03c72ff9`
- trades_sha256: `9b2756c27c38fbbaad7f98163708b0d79fd4a17e93c0f82227834bc91acc8039`
