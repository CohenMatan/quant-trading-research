# E003-11 — S003 v1.1 (research)

C01 H003 S003 v1.1 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E003-02 under D051 with the D054 harness fix (replaces E003-08)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `638a1166d4632d63363b5bacca982ac205ee2768` · **QC backtest:** `74ee3291ef540cda96f04f094618455b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T08:53:48Z · **runtime:** 383s
- **Parameters:** `{'rebalance': 'days', 'every_days': 10, 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 0.82% |
| Annualised volatility | 7.78% |
| Sharpe (rf = 0) | 0.14 |
| Sortino | 0.20 |
| Max drawdown | -16.97% |
| Longest drawdown (trading days) | 1219 |
| Calmar | 0.05 |
| Worst year | -9.97% |
| Worst month | -4.01% |
| Closed trades | 1370 |
| Win rate | 47.52% |
| Average winner | 3.51% |
| Average loser | -3.29% |
| Expectancy per trade | -0.06% |
| Profit factor | 0.97 |
| Average holding (calendar days) | 17.1 |
| Average exposure | 48.37% |
| Turnover (1-way, per year) | 10.26 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -12.52% | 0.39 | 0.71 |
| E901-05 | -12.93% | 0.37 | 0.73 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 0.86% |
| 2011 | -9.97% |
| 2012 | 0.50% |
| 2013 | 7.96% |
| 2014 | 1.45% |
| 2015 | -1.41% |
| 2016 | 1.05% |
| 2017 | 7.17% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 86846.63 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.146960; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 18 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2749 orders vs QuantConnect Total Orders 2749 |
| fills_match_harness_count | pass | downloaded fill events 2747 vs harness-recorded fills 2747 |
| commission_fixed_per_order | pass | 2747 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `186cf1e27e2b16f1702013b6c9be813c2eb243aa1639300c43d7bb68497a1729`
- fills_sha256: `9c67249be4422b2059046725ffcf78b50593876796c976eaa717bacbd642a872`
- trades_sha256: `8037d016acf940c82f7c6eb00ac04abd4faaec299abd4af3e1e3dc922d82c48e`
