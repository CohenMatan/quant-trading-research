# E989-01 — X989 v1.0 (infrastructure)

H021-A FIDELITY CANARY (infrastructure): the 9 Select Sector SPDRs + SPY, history 1998-12-01..2017-12-31 only; histories / launch / calendar / independent day-by-day recomputation of every signal and response / ADJUSTED cross-check / XLF 2016 XLRE distribution / future perturbation / truncation / placebo / planted / null determinism. Publishes NO real IC and no other signal-response statistic.

- **Status:** failed
- **Split:** AUDIT (2017-12-01 → 2017-12-31)
- **Commit:** `47101cb07e37c5891e83dd83a13158b102f0b3b3` · **QC backtest:** `1c619fa52bf742073477b42006c32d08` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-06T04:53:47Z · **runtime:** 174s
- **Parameters:** `{'mode': 'canary'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
2017-12-29 16:00:00 Runtime Error: The key &#039;No key found for either mapped or original key. Mapped Key: [&#039;distribution&#039;]; Original Key: [&#039;distribution&#039;]&#039; was not found in the collection, which raises a KeyError exception. To prevent the exception, use collection.get(key), which returns None when the key is not found, or guard the access with &#039;if key in collection:&#039;.
  at wrapped_function
    raise KeyError(f&quot;No key found for either mapped or original key. Mapped Key: {mKey}; Original Key: {oKey}&quot;)
 in PandasMapper.py: line 93
  at _events
    for e, amt, ref in zip(ed, dv[&quot;distribution&quot;].tolist(), dv[&quot;referenceprice&quot;].tolist()):
                               ~~^^^^^^^^^^^^^^^^
 in main.py: line 114
  at _canary
    sp, dv, _, _ = self._events(self.h_sym[j], cal, d0 - timedelta(days=5), d1, upto=t_day)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 in main.py: line 370
  at qr_on_end
    self._canary()
 in main.py: line 197
  at on_end_of_algorithm
    self.qr_on_end()
 in qr_harness.py: line 873

The key 'No key found for either mapped or original key. Mapped Key: ['distribution']; Original Key: ['distribution']' was not found in the collection, which raises a KeyError exception. To prevent the exception, use collection.get(key), which returns None when the key is not found, or guard the access with 'if key in collection:'.
  at wrapped_function
    raise KeyError(f"No key found for either mapped or original key. Mapped Key: {mKey}; Original Key: {oKey}")
 in PandasMapper.py: line 93
  at _events
    for e, amt, ref in zip(ed, dv["distribution"].tolist(), dv["referenceprice"].tolist()):
                               ~~^^^^^^^^^^^^^^^^
 in main.py: line 114
  at _canary
    sp, dv, _, _ = self._events(self.h_sym[j], cal, d0 - timedelta(days=5), d1, upto=t_day)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 in main.py: line 370
  at qr_on_end
    self._canary()
 in main.py: line 197
  at on_end_of_algorithm
    self.qr_on_end()
 in qr_harness.py: line 873

```
