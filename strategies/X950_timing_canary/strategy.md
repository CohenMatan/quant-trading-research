# X950 — Execution-timing canary (infrastructure)

**Purpose:** prove that the pipeline never fills an order at the signal bar's close and that fills happen at the next session's open, at the raw price plus or minus the modelled slippage. It is re-run periodically as a data and engine change detector.

**Rules:**

- Baskets:
  - A = AAPL, XOM, KO, GE.
  - B = MSFT, JPM, PFE, WMT.
- Every 10th trading day, at the close, it targets 24% in each name of one basket and liquidates the other. Orders are market-on-open for the next session.
- The baskets include splits (AAPL 2000, 2005, 2014 and 2020), a reverse split (GE 1:8, 2021) and regular dividends.

**Checks:**

- Harness self-check on every fill: the fill date is strictly after the signal date, and the fill price equals the next session's raw open ×(1 ± slippage) within 1e-6.
- Canary check: when a fill arrives, the last processed close equals the signal date, i.e. the fill happens at the first session after the signal.
- Local integrity checks on the downloaded fills, e.g. every fill date is after the signal date encoded in its order tag.

This is not a strategy and carries no research meaning.
