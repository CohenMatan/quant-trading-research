# E023-07 — S023 v1.1 (research)

H022 REAL EVALUATION, ONCE (E023-06 never started: QuantConnect refused the LEAN-version update at upload, nothing compiled or computed, D180): the frozen Conviction Score v1 on the 83 monthly decisions 2011-01-31..2017-11-30 (one-month total-shareholder-return responses demeaned by the population), judged with the pinned c_IC (gates G1-G4, all required); then the pre-registered NON-GATING diagnostics (sector-demeaned IC, regime IC, Fama-MacBeth incremental, 2- and 3-month horizons). No portfolio, no orders; refuses unless the prepared panel equals the one the null was calibrated on.

- **Status:** failed
- **Split:** IS (2011-01-03 → 2017-12-31)
- **Commit:** `516ff039564907beac607fcbf1f153b4259c2b80` · **QC backtest:** `f7d276f4a56e940f9f6b2a6394c2bbb9` · **LEAN:** v2.5.0.0.18166 · **run:** 2026-10-06T22:07:45Z · **runtime:** 445s
- **Parameters:** `{'mode': 'real', 'c_ic': 2.390976216956, 'threshold_commit': 'dbfdcc04913ddf084ed764b38bdf4dffe1024f4d', 'null_result_sha256': 'c96733d88c9a9f71127cf8a337d45543374a89ea104fd5a62aa53c25d98629b6', 'panel_sha256': 'a1e12dbfc05164e94bfd93381b64586a9addf90ca1ec5f635509961d385b5b7a', 'spec_sha256': '2c99f9623065a0d9576f35ea208733c47ce5ec3bbfe2f587ab2a9451b0061f58', 'pred_code_sha256': 'bc6fd8e83e7c105e50bbd05fabb23c61ac5229216af6599320962195d83f8da5'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
backtest ran on LEAN v2.5.0.0.18166, expected build 18131
```
