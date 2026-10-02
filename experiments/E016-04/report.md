# E016-04 — S016 v1.0 (benchmark)

P2 H016 random control seed 2: same universe, 20 slots, schedule, costs and position rules as E016-01; only the ranking differs. Pre-declared in research/phase2/H016_spec.md (frozen, D116).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `7738614033ee543e0b80eec299a95da20d312dbd` · **QC backtest:** `689a63e3c06f530c4319c86c00c5ea40` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-02T17:07:37Z · **runtime:** 736s
- **Parameters:** `{'slots': 20, 'months': [3, 6, 9, 12], 'book': 'random', 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 10.59% |
| Annualised volatility | 19.40% |
| Sharpe (rf = 0) | 0.62 |
| Sortino | 0.86 |
| Max drawdown | -38.01% |
| Longest drawdown (trading days) | 688 |
| Calmar | 0.28 |
| Worst year | -11.12% |
| Worst month | -15.48% |
| Closed trades | 81 |
| Win rate | 44.44% |
| Average winner | 67.25% |
| Average loser | -20.02% |
| Expectancy per trade | 18.76% |
| Profit factor | 1.91 |
| Average holding (calendar days) | 659.8 |
| Average exposure | 94.67% |
| Turnover (1-way, per year) | 0.31 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.30% | 1.05 | 0.90 |
| E901-07 | -2.80% | 1.02 | 0.94 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 22.47% |
| 2011 | -5.17% |
| 2012 | 20.79% |
| 2013 | 36.44% |
| 2014 | 17.12% |
| 2015 | -11.12% |
| 2016 | 4.36% |
| 2017 | 14.10% |
| 2018 | -6.56% |
| 2019 | 18.26% |
| 2020 | 7.39% |
| 2021 | 16.85% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 92534.80 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 418 warm-up sessions |
| no_leverage | pass | min cash/equity 0.018396; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.826330491169592e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 266 orders vs QuantConnect Total Orders 266 |
| fills_match_harness_count | pass | downloaded fill events 266 vs harness-recorded fills 266 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 266 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `1f4bd8fc332f536bc49ecb664c2ca41137dcc2211f2cb015d883116227b93a70`
- fills_sha256: `fb45fea0670681469c51e86ccbc58166f51d14d3bcf829dc66cfa5f2928e168d`
- trades_sha256: `d43cad2e1e9381cdd5076f7007db83d0215f4a22186f6976c7df5724e6b44567`
