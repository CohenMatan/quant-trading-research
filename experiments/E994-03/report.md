# E994-03 — X994 v1.1 (infrastructure)

H022 DIAGNOSTIC CANARY ON QUANTCONNECT'S DEFAULT BUILD (owner option B, P7-CP5a, D182; X994 v1.1, infrastructure, non-trading): identical to E994-02 except that it runs on whatever LEAN build QuantConnect now uses by default (recorded). Reports whether the prepared panel (scores and responses) equals the pinned one the null was calibrated on, and which side differs if not. Computes NO IC of the real assignment, NO gate, NO null statistic; nothing after 2017-12-31.

- **Status:** failed
- **Split:** AUDIT (2011-01-03 → 2017-12-31)
- **Commit:** `df9d6f849b06e947732fe5b04b94e0678fc1aec2` · **QC backtest:** `aa5df53058ae5ccac2f7d1edb60826b3` · **LEAN:** v2.5.0.0.18178 · **run:** 2026-10-10T10:56:11Z · **runtime:** 558s
- **Parameters:** `{'mode': 'canary', 'spec_sha256': '2c99f9623065a0d9576f35ea208733c47ce5ec3bbfe2f587ab2a9451b0061f58', 'pred_code_sha256': 'bc6fd8e83e7c105e50bbd05fabb23c61ac5229216af6599320962195d83f8da5'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
2017-12-30 00:00:00 Runtime Error: float division by zero
  at nw_tstat
    lrv = float(e @ e) / T
          ~~~~~~~~~~~~~^~~
 in qr_xs.py: line 248
  at summarise
    m_ic, se_ic, t_ic = X.nw_tstat(ic, lag)
                        ^^^^^^^^^^^^^^^^^^^
 in qr_p7_pred.py: line 142
  at run_world
    out = summarise(series, years, regimes, lag, ann)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 in qr_p7_pred.py: line 211
  at 
    dg = [self._world_digest(R.run_world(prep, seed=900001 + i)) for i in range(TIMING_WORLDS)]
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 in main.py: line 882
  at _canary
    dg = [self._world_digest(R.run_world(prep, seed=900001 + i)) for i in range(TIMING_WORLDS)]
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 in main.py: line 882
  at qr_on_end
    self._canary(dates, reviews, rows_k)
 in main.py: line 590
  at on_end_of_algorithm
    self.qr_on_end()
 in qr_harness.py: line 873

float division by zero
  at nw_tstat
    lrv = float(e @ e) / T
          ~~~~~~~~~~~~~^~~
 in qr_xs.py: line 248
  at summarise
    m_ic, se_ic, t_ic = X.nw_tstat(ic, lag)
                        ^^^^^^^^^^^^^^^^^^^
 in qr_p7_pred.py: line 142
  at run_world
    out = summarise(series, years, regimes, lag, ann)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 in qr_p7_pred.py: line 211
  at <listcomp>
    dg = [self._world_digest(R.run_world(prep, seed=900001 + i)) for i in range(TIMING_WORLDS)]
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 in main.py: line 882
  at _canary
    dg = [self._world_digest(R.run_world(prep, seed=900001 + i)) for i in range(TIMING_WORLDS)]
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 in main.py: line 882
  at qr_on_end
    self._canary(dates, reviews, rows_k)
 in main.py: line 590
  at on_end_of_algorithm
    self.qr_on_end()
 in qr_harness.py: line 873

```
