# B901 — Equal-weight ≥ $2B universe (benchmark)

- Every eligible stock gets the same weight.
  - Eligible means passing the harness universe: US common stock, primary share, NYSE/Nasdaq/AMEX, point-in-time MarketCap ≥ $2B, plus the tradability filters.
- It rebalances on the first trading day of each month. Stocks that left the universe are sold.
- This is the "harder, more honest" benchmark for a stock picker in this universe. It also measures what the universe itself earned, including delisted names.
- It runs with a larger notional account (see the experiment config) so that per-order minimum commissions and whole-share rounding across about 500–1,500 names do not distort it. Slippage and per-share commissions are the same as for strategies.
