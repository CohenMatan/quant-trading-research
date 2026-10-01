# E967-01 — X967 v1.0 (infrastructure)

Fundamental-data point-in-time integrity audit (D106): timing/look-ahead, accession years, revisions, coverage and missingness, market cap vs shares, staleness, fiscal-year changes, sample companies. No orders, no rankings, no returns. Logs counts, dates and ratios only (no raw values). Verification; not a trial.

- **Status:** failed
- **Split:** AUDIT (2010-01-04 → 2021-12-31)
- **Commit:** `a888d05856c47245bbdda2cf14eed36958eb3ddf` · **QC backtest:** `2cb2061341f42ccaf6201747b79c00ac` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T17:25:06Z · **runtime:** 239s
- **Parameters:** `{}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Error

```
2016-06-01 00:00:00 Runtime Error: float division by zero
  at _sample
    if r is not None and (st is None or st.get(&quot;r&quot;) is None or abs(r / st[&quot;r&quot;] - 1) &gt; 0.02
                                                                   ~~^~~~~~~~~
 in main.py: line 341
  at _qr_select
    self._sample(t, f, today, f.symbol in elig)
 in main.py: line 105

float division by zero
  at _sample
    if r is not None and (st is None or st.get("r") is None or abs(r / st["r"] - 1) > 0.02
                                                                   ~~^~~~~~~~~
 in main.py: line 341
  at _qr_select
    self._sample(t, f, today, f.symbol in elig)
 in main.py: line 105

```
