# X951 — Data audit (infrastructure)

A read-only algorithm that places no orders. It measures the Morningstar fundamental universe over the backtest window and writes monthly counts to the chart `AUDIT`, plus snapshot and delisting lines to the logs.

The runner stores the counts in `experiments/E951-01/audit_monthly.csv`. `python -m qresearch.audit` renders them into `docs/data/data_audit.md`.

**What it answers:**

1. How many US common stocks are ≥ $2B each year, and how many survive the tradability filters?
2. How often is MarketCap missing (zero) for actively traded stocks, and are large companies affected?
3. Does MarketCap agree with an independent recomputation (price × shares outstanding)?
4. Do known companies show plausible market caps on known dates?
5. Do known failed or acquired companies (Enron, WorldCom, Lehman, Bear Stearns) appear and then disappear at the right time?
6. How many ≥ $2B names are excluded as ADRs or as listings on other exchanges?
