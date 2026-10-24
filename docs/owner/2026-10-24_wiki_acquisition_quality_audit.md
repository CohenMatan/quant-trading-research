# Owner direction D298 — WIKI Prices: practical acquisition and data-quality audit (2026-10-24)

**Context:** follows TT-CP1b Addendum 1 (D297, PR #138). The message is recorded verbatim below, before any work.

---

Owner Direction — WIKI Prices: Practical Acquisition and Data Quality Audit

I reviewed TT-CP1b and its addendum.

I do not want another design-only review or to wait for an email response from Nasdaq before investigating whether the data is usable.

Your next task is to obtain the historical WIKI Prices dataset at no additional cost, if legally and technically accessible, and perform a practical data-quality and historical-composition audit.

1. Acquire the Dataset

Try the following sources in order:

1. Official Nasdaq Data Link WIKI/PRICES dataset:
   https://data.nasdaq.com/databases/WIKIP

2. If the official source is inaccessible, investigate the historical public archive:
   https://www.kaggle.com/datasets/marketneutral/quandl-wiki-prices-us-equites

Use only a legitimate, free download route. Check the applicable access and reuse terms for the actual source used.

Do not purchase data, bypass authentication, circumvent network restrictions, or treat an unknown mirror licence as automatically permissive.

If credentials or network access are unavailable, report the exact blocker and the smallest action I need to take. Do not replace the dataset with synthetic data.

If acquisition succeeds:

- Record source URL, acquisition date, file size, format, row count and SHA-256.
- Store the raw dataset outside Git.
- Do not commit API keys or credentials.
- Keep raw market-data rows and charts out of AI model context while transmission rights remain unclear. Perform the audit programmatically and report aggregates.

2. Audit Historical Coverage

Restrict the research window to 2010–2017.

Measure:

- Unique securities and daily rows by year.
- Historical trading-session coverage.
- Missing bars, invalid OHLC values, suspicious price spikes and adjustment inconsistencies.
- Split and dividend data quality.
- Ticker reuse and ambiguous historical identities.
- Representation of companies that later delisted, failed or were acquired.
- Coverage differences by year, company size and available security categories.

Compare against the independent SEC reference information already available in our repository.

Do not substitute public float for trading liquidity.

Distinguish actual missing price histories from unresolved historical identity mappings.

Avoid point-in-time look-ahead when defining historically eligible companies.

Use the existing TT-CP1b audit framework, incorporating the corrections already identified. Fix the criteria and definitions before inspecting the audit outcomes; do not tune thresholds to obtain a PASS.

3. Determine Whether the Data Is Sufficient

Our immediate purpose is to build approximately 300 historically representative candlestick charts for exploratory technical-pattern discovery.

Determine whether the acquired dataset supports this.

Evaluate:

- Enough eligible stocks across 2010–2017.
- Adequate representation of failed, acquired and delisted companies.
- Sufficient continuous trading history for useful price-and-volume charts.
- Reliable adjusted and unadjusted OHLCV information.
- A reproducible sampling method that avoids selecting only historical winners.

Be explicit about biases and gaps that cannot be eliminated.

4. Restrictions

Do not:

- Render or send raw historical charts to Claude yet.
- Start a new strategy or backtest.
- Open or inspect 1999–2009 visually.
- Access the sealed 2022–2026 Holdout.
- Purchase data or subscriptions.
- Begin another QuantConnect universe-repair project.
- Modify previously frozen experiment results.

5. Deliverable

Produce a concise factual report answering:

1. Was the dataset successfully downloaded? From where?
2. How many stocks and daily observations are available for 2010–2017?
3. What quality and composition issues were actually measured?
4. Is the data sufficient to build approximately 300 representative historical charts?
5. What specific limitations remain?
6. What is the smallest next step needed to begin chart-based hypothesis discovery?

Classify the result as:

- SUFFICIENT FOR EXPLORATORY CHART RESEARCH
- INSUFFICIENT
- INCONCLUSIVE / ACCESS BLOCKED

Do not describe the dataset as survivorship-free without supporting evidence.

Commit only the audit code, metadata and concise report through the normal workflow. Do not commit raw market data.

STOP after the audit and report the findings.

The goal is a real answer based on actual downloaded data — not another feasibility proposal.
