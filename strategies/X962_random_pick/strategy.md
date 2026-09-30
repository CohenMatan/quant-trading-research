# X962: no-skill random-pick portfolio (portfolio-structure diagnostic)

**Purpose:** measure what portfolio size, account size and holding period do to a portfolio **with no stock-picking skill at all**, under exactly the rules C01 and C02 strategies faced:

- the approved universe;
- next-open execution;
- $7 per order and 10 bps slippage;
- no borrowing, with the 2% cash buffer and 15% gap reserve.

**Rules:**

- Every trading day, sell each holding once it has been held `hold` sessions.
- Refill empty slots with randomly chosen eligible stocks. The order is fixed by a seed.
- Selection uses no price or volume information.

It is a verification diagnostic (kind `infrastructure`): not a strategy and not a trial. Configurations, seeds and evaluation rules are pre-registered in `research/cycles/C03_portfolio_diagnostics_plan.md`.
