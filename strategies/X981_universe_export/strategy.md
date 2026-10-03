# X981: universe identifier export (infrastructure; not a trial)

- **Purpose:** the P2-CP12 SEC earnings-event audit (owner 2026-10-02).
- **What it exports:** for every security in the frozen v1 harness universe (≥ $2B, price ≥ $5, ADV ≥ $5M, US common, SEC correction layer) on the first session of each month from 2010 to 2021:
  - its identifiers: QuantConnect security id, the vendor CIK (current-status), the SEC-correction CIK for repaired securities, and its dated tickers;
  - its eligible months.
- **What it does not export:** prices, returns, fundamental values or orders.
