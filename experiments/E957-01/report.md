# E957-01 — X957 v1.0 (infrastructure)

D059 canary: holdings whose data stops without a delisting event must be taken out at their last real close; no order may stay open.

- **Status:** completed_with_warnings
- **Split:** AUDIT (2013-01-01 → 2021-12-31)
- **Commit:** `ec280f805ee16acc07a970431a2d870a0123edb3` · **QC backtest:** `362a86c601969c19059a8bdec725fa5a` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T13:19:27Z · **runtime:** 35s
- **Parameters:** `{'buys': {'CPNO T3JPOU4QFQZP': {'ticker': 'CPNO', 'buy_on': '2013-03-01'}, 'SEP TTSYULARW12D': {'ticker': 'SEP', 'buy_on': '2018-10-01'}, 'VLP VMBQF57YDSO5': {'ticker': 'VLP', 'buy_on': '2018-11-01'}, 'ELLI UVRNCD1237TX': {'ticker': 'ELLI', 'buy_on': '2019-03-01'}, 'APU R735QTJ8XC9X': {'ticker': 'APU', 'buy_on': '2019-07-01'}, 'OAK V5P2MATBV339': {'ticker': 'OAK', 'buy_on': '2019-08-01'}, 'BPL R735QTJ8XC9X': {'ticker': 'BPL', 'buy_on': '2019-09-03'}, 'EQM V7RWLEM5OFAD': {'ticker': 'EQM', 'buy_on': '2020-05-01'}, 'HOME WCRVPJY6DCV9': {'ticker': 'HOME', 'buy_on': '2021-06-01'}, 'TIF R735QTJ8XC9X': {'ticker': 'TIF', 'buy_on': '2020-11-02'}, 'KO R735QTJ8XC9X': {'ticker': 'KO', 'buy_on': '2013-01-02'}}, 'oak_sid': 'OAK V5P2MATBV339', 'oak_sell_on': '2019-10-01'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2013-01-02 → 2021-12-31 (2267 trading days) |
| CAGR | 0.46% |
| Annualised volatility | 1.01% |
| Sharpe (rf = 0) | 0.47 |
| Sortino | 0.64 |
| Max drawdown | -2.28% |
| Longest drawdown (trading days) | 298 |
| Calmar | 0.20 |
| Worst year | -0.01% |
| Worst month | -0.92% |
| Closed trades | 10 |
| Win rate | 60.00% |
| Average winner | 3.87% |
| Average loser | -3.80% |
| Expectancy per trade | 0.80% |
| Profit factor | 1.45 |
| Average holding (calendar days) | 70.7 |
| Average exposure | 5.62% |
| Turnover (1-way, per year) | 0.05 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2013 | 0.79% |
| 2014 | 0.23% |
| 2015 | 0.22% |
| 2016 | -0.01% |
| 2017 | 0.62% |
| 2018 | 0.27% |
| 2019 | 0.75% |
| 2020 | 0.69% |
| 2021 | 0.62% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2267 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2013-01-02..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 999304.76 |
| equity_complete | pass | chart rows 2267 vs algorithm days 2267 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2267 vs QuantConnect tradeableDates 2267 |
| no_leverage | pass | min cash/equity 0.825161; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 10 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=1.9200240813017123e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 13 orders vs QuantConnect Total Orders 13 |
| fills_match_harness_count | pass | downloaded fill events 12 vs harness-recorded fills 12 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| stale_exits | warn | 9 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 9 mirrored |
| commission_fixed_per_order | pass | 21 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ccdb28a97cd94cb34a582891090301dd42d5badcb83c0e82dbeeae5363ce3091`
- fills_sha256: `0b507fc454d67ae51d8ae01b0c40c7ccb3d2b33d20a55d587fcdb01613e008cc`
- trades_sha256: `9dffc88b16b977e7187afc61d0889e8fda2c14babdd4bebc90104259bfea81bb`
