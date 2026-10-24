# Owner review D296 — TT-CP1b: conditional approval and required corrections (2026-10-24)

**Context:** follows TT-CP1b (`docs/checkpoints/TT_CP1b_historical_chart_source_feasibility.md`, D295, PR #137). The message is recorded verbatim below, before any work.

---

Owner Review — TT-CP1b: Conditional Approval and Required Corrections
I have reviewed TT-CP1b and PR #137.
I agree that WIKI Prices is a potentially useful source for the hybrid technical-analysis programme.
However, I am not approving data acquisition, chart rendering, or Claude's analysis of historical charts yet.
We need to resolve several issues first.
1. WIKI Prices Licensing
The official Nasdaq Data Link WIKI Prices page does state that the dataset was released into the public domain.
However, Nasdaq Data Link's general data terms include restrictions on disclosure and redistribution of data.
Do not assume the public-domain statement automatically resolves every contractual access or AI-transmission issue.
I want a focused assessment of whether the specific proposed use is permitted:

* Downloading historical WIKI Prices for personal research.
* Rendering OHLCV data as historical candlestick charts.
* Submitting anonymized chart images to Anthropic's Claude for internal technical research.
* Using Claude to identify patterns and translate them into deterministic trading rules.

Identify any conflict or ambiguity between the WIKI dataset description and the Nasdaq Data Link terms, including the announced November 1, 2026 terms update.
If an explicit vendor confirmation is required, draft a short email to Nasdaq Data Link that I can send.
Do not contact Nasdaq on my behalf.
Also establish whether the historical WIKI Prices dataset remains accessible through a free API key in 2026. A published dataset page does not prove current download availability.
Do not attempt a download yet.
2. Reconsider the Composition Audit
The proposed 90% overall coverage and 75% delisted coverage thresholds are not sufficient by themselves.
Our existing Data v1 / QuantConnect universe has known historical completeness and survivorship limitations.
A high coverage percentage against an imperfect reference does not establish that WIKI Prices is representative.
Revise the proposed audit protocol to address:

* Independent historical universe references, where available.
* Companies that disappeared through bankruptcy, acquisition or delisting.
* Missingness by year, liquidity and security type.
* Ticker reuse and historical identity matching.
* Missing bars, suspicious price spikes, split adjustments and dividend adjustments.
* The limitations of using WIKI for chart-based hypothesis discovery.

Provide justified PASS / FAIL / INCONCLUSIVE criteria.
Clearly state which biases cannot be eliminated with our existing resources.
The purpose is to obtain a sufficiently representative exploratory chart sample, not to falsely certify the dataset as survivorship-free.
3. Historical Time Windows
I approve in principle:

* WIKI visual development limited to 2010–2017.
* No visual inspection of the proposed 1999–2009 confirmation window.
* The 2022–2026 Holdout remains sealed.
* Any future strategy validation must use separately approved, unexamined evidence.

Do not begin chart sampling yet.
4. Research Priorities
The original goal remains unchanged:
Build a deterministic technical stock-trading strategy that can outperform SPY in long-term after-tax terminal wealth.
Claude's visual role is to assist in discovering and defining technical behaviors.
The automated system will make decisions using measurable price-and-volume rules.
We are not trying to build a strategy that performs well only on WIKI Prices.
No new strategy, backtest or parameter optimization is authorized.
5. PR #137 Test Changes
The previous assignment was a desk-research task, but PR #137 modified four test files.
Please provide a concise audit of those modifications:

* Explain why each change was necessary.
* Identify whether any test expectation was weakened or changed rather than correcting a genuinely stale assertion.
* Confirm whether the complete test suite has subsequently passed.

Do not make additional test changes without separate authorization.
Do not conflate a successful subset of tests with a passing full suite.
6. Required Deliverable
Prepare one short addendum to TT-CP1b covering:

1. The remaining WIKI licensing and access uncertainties.
2. A draft Nasdaq clarification email, if required.
3. A revised historical chart-composition audit protocol.
4. A short review of the PR #137 test changes.
5. A clear recommendation on whether the owner can approve data access and chart analysis.

This is documentation and review only.
No downloads, API calls to retrieve market data, chart rendering, backtests, implementation, purchases, Holdout access, or new trading rules.
Commit the addendum through the normal workflow and STOP for review.
