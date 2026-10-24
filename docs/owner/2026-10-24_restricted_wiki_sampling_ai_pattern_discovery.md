# Owner decision D302 — Restricted WIKI sampling and AI-assisted technical pattern discovery (2026-10-24)

**Context:** follows TT-CP1c R1 (D301, PR #140). The message is recorded verbatim below, before any work.

---

Owner Decision — TT-CP1c: Restricted WIKI Sampling and AI-Assisted Technical Pattern Discovery
I have reviewed TT-CP1c R1, including the frozen audit results in PR #140.
I want to move forward with practical technical-pattern research using the historical WIKI Prices data we have already downloaded.
The objective is to stop spending time on repeated feasibility studies and begin discovering potentially valuable trading behaviors from actual historical stock charts.
This message consolidates my decisions regarding restricted WIKI sampling, chart rendering, and Claude-assisted visual analysis.
1. Accept the Existing Audit Result
I accept the frozen A1–A7 audit classification:
INSUFFICIENT
Specifically:

* A1 — PASS
* A2 — INCONCLUSIVE
* A3 — PASS
* A4 — FAIL
* A5 — FAIL
* A6 — FAIL
* A7 — PASS

Do not modify these outcomes, change the original thresholds, or retrospectively classify the full WIKI dataset as suitable.
However, I approve a documented owner exception permitting a carefully restricted subset of WIKI Prices to be used exclusively for exploratory technical-pattern discovery.
This exception does not establish that WIKI is survivorship-free, suitable for investment decisions, or independently validated.
2. Authorization for Claude Chart Analysis
I authorize using historical WIKI Prices chart images with Claude for my personal, non-commercial investment research.
The WIKI dataset is publicly described as having been released into the public domain.
I understand that the applicability of Nasdaq Data Link's contractual terms to transmitting chart images to an external AI provider has not been conclusively resolved.
I do not want to wait for an email response from Nasdaq before moving forward.
This is my authorization as the research owner, not a representation that Nasdaq has granted permission.
Before transmitting charts, check the applicable published terms. If an explicit applicable prohibition is identified, do not transmit the charts; report the precise restriction and continue with any permitted local work. Do not bypass a technical, contractual, or platform restriction.
Where permitted, use Claude to visually analyze historical candlestick charts and identify recurring price-and-volume behaviors.
For data handling:

* Disable use of these sessions for model training in the available Claude settings.
* Do not publish or redistribute the downloaded dataset.
* Keep raw OHLCV data outside Git.
* Do not transmit entire raw price tables when charts are sufficient.
* Use only the minimum data necessary for visual analysis.
* Keep full ticker/date mappings locally for reproducibility, not inside the blinded chart images.

The purpose of sending charts to Claude is to discover and describe potential trading patterns, not to train a new AI model or prove trading profitability.
3. Use Existing Resources
Continue from the already merged TT-CP1c work:

* PR #139 — acquisition and audit infrastructure.
* PR #140 — successful WIKI download and real audit results.
* Existing WIKI audit and SEC reference code.
* Existing WIKI Prices dataset and manifest.

First verify that the downloaded dataset remains accessible in the current environment and that its SHA-256 matches the recorded manifest.
If the data is no longer locally available, reacquire the same dataset through the already authorized official free route. Do not silently substitute another dataset.
Do not rebuild the existing infrastructure or introduce a new data source.
No purchases, paid subscriptions, or additional datasets.
4. Restricted Historical Research Window
For the initial visual research phase, use:
January 2011 through December 2016.
This excludes the weaker 2017 coverage during the initial stage.
The analysis must remain historically consistent:

* Use only information that would have been available as of the selected chart's decision date.
* Never display future price action beyond that date.
* Do not select chart dates based on what happened afterward.
* Do not use future returns, known winners, or later company outcomes to choose individual examples.
* Never visually inspect 1999–2009.
* Keep the 2022–2026 Holdout completely sealed.

The original 2010–2017 WIKI audit remains unchanged.
5. Construct a Restricted, Outcome-Blind Sample
Use the existing independent SEC historical reference frame as the basis for sampling, rather than sampling directly from WIKI's available ticker list.
Target approximately 300 historical stock charts, selected reproducibly.
Stratify the sample across:

* Historical years, 2011–2016.
* Company-size groups based on point-in-time SEC public-float information.
* Different historical company outcomes and market-exit categories where available.
* Different price-and-volume behaviors without selecting them using future performance.

Preserve the proportions of the historical reference population where feasible.
Apply strict quality rules:

1. Exclude unresolved or ambiguous company identities.
2. Exclude histories with material price-adjustment, split, dividend, or OHLCV problems.
3. Exclude the previously identified 21 tickers with unexplained adjustment inconsistencies unless an independently justified, pre-specified affected-period exclusion is demonstrably sufficient.
4. Require adequate historical trading data for meaningful chart analysis.
5. Prevent duplicated charts or excessive concentration in a small number of companies.
6. Preserve historical company identity and the as-of-date eligibility rules.

Do not use acquired companies as a replacement for failed or bankrupt companies.
The existing audit shows that bankrupt companies are poorly represented. This limitation must remain explicit.
If a historical sampling category cannot be filled, report it as unfilled. Do not silently replace it with companies that survived or performed better.
Do not describe the sample as statistically representative if material historical categories remain missing.
6. Create Historical Candlestick Charts
Build or reuse a minimal deterministic renderer using the existing WIKI data.
Each chart should display sufficient historical information for meaningful technical analysis, including:

* Daily candlesticks.
* Trading volume.
* Approximately 252 trading sessions of historical context, where available.
* A clearly defined decision point at the final visible session.

Charts must be blinded:

* Hide company names and tickers.
* Hide calendar dates that would reveal known historical events.
* Hide unnecessary absolute price information.
* Do not display price movement after the decision point.
* Do not attach labels indicating whether the stock subsequently gained, declined, was acquired, or failed.

Maintain the original mapping and sampling metadata locally for auditability.
The image must reflect genuine historical trading data rather than synthetic or artistically generated candlesticks.
7. Begin AI-Assisted Technical Pattern Discovery
Once the restricted sample is constructed and its limitations are documented, proceed to chart analysis where transmission is permitted.
Do not stop merely because the rendering infrastructure is ready.
Start with a small pilot batch of approximately 20–30 charts to verify the analysis workflow, then continue toward the 300-chart target if the pilot is technically sound.
For each chart, analyze the visible historical price-and-volume behavior at the decision point.
Look for potentially meaningful technical structures, such as:

* Sustained trend development.
* Consolidation and breakout behavior.
* Changes in trading volume.
* Pullback and recovery structures.
* Volatility contraction or expansion.
* Price behavior near support or resistance.
* Signs of trend acceleration or deterioration.
* Structures that may support open-ended holding periods and allowing winners to run.

These are observation categories, not authorization to reuse or optimize previously rejected trading hypotheses.
Do not force every chart into a recognizable pattern.
Record when no clear pattern exists.
The goal is to identify potentially useful behaviors and translate them into objective, deterministic trading rules.
For every proposed pattern, distinguish:

1. What is directly visible on the chart.
2. The possible economic or behavioral explanation.
3. How the pattern could be defined mathematically.
4. Why the rule could plausibly produce excess returns.
5. Whether a substantially similar rule was already tested and rejected in H001–H032.
6. What evidence would be needed to falsify it.

Do not claim a pattern is profitable simply because it looks promising.
8. Our Actual Investment Objective
Our research goal is an offensive US equity trading strategy that can generate meaningful excess returns over SPY during rising markets.
The eventual strategy should aim to outperform SPY in long-term terminal wealth after realistic transaction costs and taxes, while keeping risk explicit and controlled.
We may later investigate combining the offensive strategy with a separate defensive component.
H028 remains REJECTED. It can inform our understanding of defensive approaches but must not be treated as a validated strategy.
The immediate research objective is to discover technical behaviors that could support an offensive stock-selection and trading system.
We are particularly interested in the possibility of identifying strong stocks early enough to participate in major upward trends and allowing successful positions to develop without arbitrary premature exits.
However, previous trend, momentum, breakout, and chart-scoring tests produced negative or inconclusive results.
Do not present previously rejected concepts as new discoveries merely because their implementation or terminology has changed.
9. Research Discipline
Keep the discovery and validation stages strictly separate.
During this phase:

* No strategy backtests.
* No historical return optimization.
* No parameter searches.
* No selection of patterns based on future price outcomes.
* No new strategy registration yet.
* No QuantConnect universe repairs.
* No Holdout access.
* No changes to existing portfolio constraints.
* No purchases.

Preserve a record of all inspected charts, including charts with no interesting pattern.
Prevent selection bias by documenting how many charts were reviewed and how each proposed pattern emerged.
Do not use historical charts to manufacture an apparently successful trading strategy by trial and error.
10. Execution and Deliverables
This is an authorization to carry out a bounded exploratory chart-discovery workflow, not another design-only assignment.
Proceed in order:
Stage 1 — Restricted Sample

* Verify the existing dataset.
* Construct the restricted historically grounded sample.
* Document exclusions and missing categories.
* Determine whether approximately 300 usable charts can be produced.

Stage 2 — Chart Rendering

* Implement the minimum required renderer.
* Verify that images contain no future information.
* Preserve chart-selection reproducibility.

Stage 3 — Visual Discovery

* Analyze an initial pilot batch.
* If the workflow is valid and chart transmission is permitted, continue toward the target sample.
* Record observations consistently, including uninteresting cases.

Stage 4 — Research Findings
Produce a concise checkpoint containing:

1. The actual number of charts sampled and analyzed.
2. Historical coverage and sample limitations.
3. The most promising recurring technical behaviors observed.
4. Proposed deterministic definitions for each behavior.
5. Comparison with previously rejected hypotheses.
6. Reasons why the patterns might or might not provide an economic edge.
7. One recommended research hypothesis, if the observations genuinely support one.
8. The smallest rigorous experiment needed to test that hypothesis later.

If the observations do not support a credible new hypothesis, say so clearly.
Do not invent an investment edge to justify the work.
Commit code, metadata, research observations and concise reports through the normal GitHub workflow. Do not commit raw WIKI price data or chart images.
If a material data-integrity, licensing, or sampling blocker prevents the next stage, report the specific blocker and STOP rather than starting another infrastructure project.
Otherwise, proceed through the authorized stages without requesting separate approval after every routine step.
Our priority is to start learning from real historical stock behavior and discover promising offensive trading hypotheses — not to spend another research cycle on infrastructure, feasibility documentation, or data repair.
