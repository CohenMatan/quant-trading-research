# E004-02 — S004 v1.1 (research)

C01 H004 S004 v1.1 (pre-declared variation) on IS 2010-2017

- **Status:** integrity_failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `17b5efb55828dc17ece947d8bcce4e8f61996e44` · **QC backtest:** `28382110f7259b8796e4ed37491ea1a9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T13:24:09Z · **runtime:** 316s
- **Parameters:** `{'leader_frac': 0.2, 'drop': 0.08, 'hold_days': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -1.81% |
| Annualised volatility | 22.80% |
| Sharpe (rf = 0) | 0.03 |
| Sortino | 0.05 |
| Max drawdown | -51.29% |
| Longest drawdown (trading days) | 1053 |
| Calmar | -0.04 |
| Worst year | -24.44% |
| Worst month | -15.75% |
| Closed trades | 2201 |
| Win rate | 49.80% |
| Average winner | 6.52% |
| Average loser | -6.58% |
| Expectancy per trade | -0.06% |
| Profit factor | 0.95 |
| Average holding (calendar days) | 14.5 |
| Average exposure | 71.45% |
| Turnover (1-way, per year) | 17.87 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -15.09% | 1.13 | 0.71 |
| E901-03 | -15.96% | 1.11 | 0.77 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 24.72% |
| 2011 | -16.81% |
| 2012 | 16.35% |
| 2013 | 21.19% |
| 2014 | -24.44% |
| 2015 | -19.21% |
| 2016 | -9.31% |
| 2017 | 6.75% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 72638.63 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | FAIL | min cash/equity -0.0151 |
| cash_never_negative | warn | min cash/equity -0.0151 |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 4420 orders vs QuantConnect Total Orders 4420 |
| fills_match_harness_count | pass | downloaded fill events 4415 vs harness-recorded fills 4415 |
| commission_fixed_per_order | pass | 4415 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `775bb6b0086b30e8093e026cd476e59ae23804df9987088a4dd859490ab7f35e`
- fills_sha256: `3fec8bcf7193c8e0bcf106d04b00d8ac9a19dd9698ac5b5d0edddbb4a173ade1`
- trades_sha256: `e7b68bab11621b1592fd66fd2ede44b571dc30b718a6c172e734672162a4eebe`
