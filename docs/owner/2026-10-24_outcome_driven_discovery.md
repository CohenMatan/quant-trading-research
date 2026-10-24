# Owner decision D308 — Outcome-driven discovery of an offensive US equity trading strategy (2026-10-24)

**Context:** follows FA-CP1 (D307, PR #143). The message is recorded verbatim below, before any work.

---

Owner Direction — Outcome-Driven Discovery of an Offensive US Equity Trading Strategy
1. Mission and Change in Research Approach
I want to begin a new phase of our quantitative investment research.
Our long-term objective remains unchanged:
Develop a systematic, long-only US equity investment strategy capable of outperforming SPY in long-term compounded terminal wealth, after realistic transaction costs and eventually taxes, without leverage.
The immediate priority is finding a credible offensive stock-selection advantage, especially one that participates strongly in rising markets.
We have already investigated many technical, fundamental, event-driven and multi-factor strategies. None has qualified as a production candidate.
I accept the previous research findings, including TT-CP2, TT-CP3 and FA-CP1, but I want to investigate the historical market from a different perspective.
Previously, much of our research began with a proposed signal, then tested whether it worked.
Now I want to reverse the process:
First investigate which stocks actually generated exceptional returns, then identify what distinguished them from comparable stocks BEFORE those returns occurred.
Those distinguishing characteristics may be:

1. Technical: candlestick patterns, price action, volume, volatility, momentum, market structure and relative strength.
2. Fundamental: business growth, profitability, cash flow, financial improvement and valuation.
3. Combined: interactions between technical market behavior and fundamental business developments.

Treat all three categories as equally legitimate research directions.
Do not assume that fundamental information is inherently more valuable than technical information, or vice versa.
A promising technical mechanism does not need an accounting-based explanation. A plausible behavioral or market-structure mechanism may be sufficient to justify further exploratory investigation.
The purpose is to discover potentially repeatable patterns that could eventually support a profitable investment strategy.
This is an explicitly outcome-driven, exploratory research programme, not independent validation.
2. Owner Authorization and Scope
I authorize the use of the already-exposed 2010–2021 development data for exploratory research, including calculations of historical future returns.
This is an explicit, narrow owner exception to the recommendation in FA-CP1 to stop further discovery on the exposed historical period.
I understand that:

* Historical outcomes can produce hindsight bias and overfitting.
* Previous research has already exposed many relationships in this period.
* A good development-period backtest does not demonstrate a durable edge.
* The same historical data cannot become independent validation simply by changing the research methodology.

Nevertheless, I want to use these historical observations to discover potentially useful relationships.
Hard constraints

* 2010-01-04 through 2021-12-31: available for exploratory analysis.
* 1999–2009: do not access or inspect.
* 2022-01-01 through 2026-08-31: sealed Holdout; do not access.
* No additional data purchases.
* No new research platform, database, backend or infrastructure project.
* Reuse existing QuantConnect data and validated SEC point-in-time data.
* Reuse the existing technical feature code and chart infrastructure where appropriate.
* Preserve previous hypothesis statuses, rejected strategies and frozen experimental results.
* Do not change historical decisions retroactively.
* Do not start live trading.

Unlike previous design-only assignments, I explicitly want empirical calculations, analysis of realised stock returns, and comparison of characteristics observed before those returns.
Do not stop after producing another feasibility report if responsible exploratory work can be performed.
If one feature or dataset is unavailable, document the limitation and continue using valid available information.
3. Central Research Question
What distinguished the stocks that generated exceptional future returns from otherwise comparable stocks that did not, and could those differences have been identified in real time?
We want to investigate whether historical winners displayed identifiable technical, fundamental or combined characteristics before their strongest advances.
Equally important, investigate stocks that:

* Underperformed SPY.
* Produced ordinary or mediocre returns.
* Looked technically strong but subsequently declined.
* Had attractive financial characteristics but subsequently disappointed.
* Experienced major drawdowns or permanent losses.
* Were acquired, delisted or failed.

Do not study successful stocks alone.
A characteristic is not useful merely because it appears frequently among successful stocks.
We need to determine whether it also appears frequently among unsuccessful stocks and whether it provides meaningful predictive information across the eligible population.
The main question is not "What did the winners look like?" but "Could we have distinguished the winners from the losers before knowing the outcomes?"
4. Stage A — Historical Outcome Analysis
Use the existing point-in-time eligible US equity universe.
Retain the existing baseline constraints wherever applicable:

* US common stocks.
* Point-in-time market capitalisation of at least $2 billion.
* Price of at least $5.
* Average daily dollar volume over 20 days of at least $5 million.
* No leverage or short selling.

At consistently defined historical decision dates, calculate subsequent stock outcomes.
Study the following forward horizons:

* 3 months.
* 6 months.
* 12 months.
* 24 months, when the full observation horizon is available within the permitted development window.

For every observation, analyse:

1. Absolute total return.
2. Total return relative to SPY over the same horizon.
3. Sector-relative return.
4. Market- and sector-adjusted returns where methodologically supportable.
5. The distribution of exceptional winners and losers.
6. Maximum adverse movement and severe drawdown, where useful.
7. Whether gains were gradual, concentrated in a few events or driven by a sustained trend.
8. The contribution of rare exceptional stocks to overall wealth creation.

Use total-return-adjusted data where appropriate, with correct corporate-action and delisting treatment.
All outcome calculations must use data available within 2010–2021.
Do not use observations whose forward-return horizons extend into the sealed Holdout.
Historical sampling
Prefer a reproducible, population-wide quantitative study rather than selecting an arbitrary collection of historically famous winners.
Include all valid eligible company-observation pairs supported by the existing data.
Avoid duplicating observations in a way that artificially inflates statistical confidence.
Account for overlapping forward-return horizons, repeated observations on the same company and common market shocks.
Report effective sample sizes and appropriate uncertainty estimates.
Clearly document missing firms, incomplete histories and the known survivorship limitations of the existing universe.
5. Stage B — Technical and Chart-Based Discovery
Technical research is a primary component of this assignment, not a secondary diagnostic.
I want to investigate how stocks behaved before their major future advances or failures.
Technical characteristics to examine
Include relevant measurable characteristics of:
Price structure

* Higher highs and higher lows.
* Persistent upward trends.
* Sideways bases and consolidation.
* Breakouts and failed breakouts.
* Pullbacks within established trends.
* Reversals after declines.
* Price compression before expansion.
* Price behavior near important historical highs and lows.

Candlestick and price-action behavior

* Large directional candles.
* Trading gaps and gap continuation.
* Price rejection and reversal structures.
* Changes in the frequency and magnitude of large moves.
* Changes in the consistency of advances versus declines.
* Close-location behavior within daily ranges.

Volume

* Unusual volume expansion.
* Volume behavior during breakouts.
* Volume contraction during consolidation.
* Price advances on relatively stronger volume.
* Price-volume divergence.
* Repeated high-volume accumulation-like events.

Volatility

* Volatility contraction and expansion.
* Changes in ATR and realised volatility.
* Volatility behavior before strong trends.
* Shallow versus deep corrections.
* Stability and persistence of upward trends.

Relative strength

* Performance relative to SPY.
* Strength relative to sector peers.
* Relative strength before major upside acceleration.
* Strength during weak market periods.
* Persistent leadership versus temporary outperformance.

Trend development

* Duration and consistency of trends.
* Rate of acceleration.
* Trend maturity.
* Distance from moving averages.
* Frequency of meaningful corrections.
* Behavior following major technical events.

These are research dimensions, not authorization for a giant parameter search.
Begin with interpretable features and existing implementations rather than generating thousands of configurations.
Historical chart inspection
Use visual analysis where it adds information beyond numerical features.
Reuse the existing WIKI chart-discovery and rendering infrastructure for the portion of the historical period it reliably covers.
WIKI's frozen audit classification remains INSUFFICIENT. Apply the documented identity and price-quality exclusions and do not treat WIKI as a fully representative historical universe.
Where the applicable terms allow external AI analysis, Claude may inspect WIKI-derived historical chart images under the previously recorded owner authorization.
Do not transmit QuantConnect-derived OHLCV data or charts to an external AI service contrary to the existing data licence and owner restrictions.
Use QuantConnect data for permitted local numerical feature analysis across the broader 2010–2021 period.
Do not substitute WIKI returns for QuantConnect returns without an explicit source-consistency assessment.
Important change from TT-CP2
TT-CP2 analysed 299 charts without looking at subsequent returns.
This research is different.
We are now explicitly allowed to connect pre-decision technical characteristics with subsequent historical outcomes, within the development period.
However, ensure that individual technical observations and feature definitions use only information available as of the historical decision date.
When feasible, record or compute features before joining them to future-return labels.
For any promising chart pattern, investigate:

1. How frequently did it occur?
2. What share of occurrences subsequently outperformed SPY?
3. What was the distribution of future returns?
4. How frequently did the same pattern precede losses?
5. Did it outperform comparable stocks without the pattern?
6. Was its apparent benefit incremental to ordinary momentum?
7. Did it remain useful across different years and sectors?
8. Could it be identified objectively and traded realistically?

Do not claim that a visually attractive chart represents a profitable trading opportunity.
6. Stage C — Fundamental and Business-Performance Discovery
In parallel with technical analysis, investigate whether information about the business itself helped distinguish future winners.
Use only existing, verified point-in-time fundamental data.
Potential explanatory characteristics include:

* Revenue growth.
* Acceleration or deceleration in revenue growth.
* Profitability levels.
* Improvement or deterioration in margins.
* Changes in return on assets or capital efficiency.
* Operating cash flow generation and improvement.
* Earnings growth and earnings stability.
* Changes in financial leverage.
* Share issuance and repurchases.
* Asset growth and capital allocation.
* Valuation measures, when historically reliable.
* Consistency of financial improvement across reporting periods.

Clearly distinguish reported financial periods from actual filing availability dates.
Do not use restated or later-published information as if it were known earlier.
Handle missing values explicitly rather than assuming missing means zero.
Important
Previous failures of individual fundamental strategies do not establish that all business-performance relationships are absent.
But they must be respected.
H016, H022–H024, H026–H028, H029/H030, OC-2 and H032 are relevant prior evidence.
Do not present a previously rejected signal as a new discovery.
If a new relationship resembles one of those hypotheses, explain whether its information content is genuinely different.
Do not repeat the previously invalidated statistical inference methodology and claim that the problem has been resolved.
7. Stage D — Combined Technical and Fundamental Relationships
I specifically want to investigate whether combinations of technical and fundamental characteristics can distinguish successful stocks better than either category alone.
Examples of questions:

* Were technically strong stocks more successful when the underlying business was also improving?
* Did accelerating revenue or profitability become more informative when accompanied by improving relative strength?
* Did technical consolidation before a breakout have different outcomes depending on fundamental performance?
* Did strong earnings growth without corresponding price strength predict future disappointment?
* Were persistent trends more reliable when accompanied by improving cash generation?
* Did deteriorating business performance help distinguish failed breakouts from successful ones?

These are research questions, not predefined winning strategies.
Do not assume that combining two weak signals automatically creates a stronger signal.
Evaluate whether any combined relationship provides meaningful additional information after accounting for the individual components.
Use economically interpretable comparisons and limit the number of combinations based on justified mechanisms.
Avoid brute-force searches across thousands of feature combinations.
8. Stage E — Separate Genuine Predictive Information From Historical Coincidence
For each potentially promising finding, compare future winners against the relevant full population.
Measure:

* Base rates of success and failure.
* Return distributions, not only average returns.
* Median returns and extreme-tail outcomes.
* False positives and false negatives.
* Incremental predictive value over simple controls.
* Differences across market regimes, sectors and size categories.
* Dependence on a handful of exceptional stocks.
* Uncertainty and sample limitations.

For example:
If 70% of the eventual exceptional winners exhibited a certain chart pattern, that is not sufficient.
We must also know how many ordinary or losing stocks exhibited that same pattern.
A useful signal must help distinguish the groups, rather than merely describe eventual winners.
Controls
Where methodologically appropriate, account for:

* Ordinary momentum.
* Market beta.
* Sector or industry.
* Company size.
* Profitability and quality.
* Market regime.

Be precise about the limits of causal interpretation and latent-factor confounding.
Do not use a statistical test already shown to produce unacceptable false approvals as evidence of validated alpha.
However, failure to establish strict causal identification should not prohibit descriptive, explicitly exploratory analysis.
Report exploratory associations honestly.
Avoid hindsight bias
The fact that we know how 2010–2021 unfolded must not become a hidden selection rule.
Do not select features because they explain a few famous historical winners.
Do not optimize arbitrary thresholds to maximize historical CAGR.
Keep a transparent record of the feature families examined, including negative results.
No cherry-picking of years, sectors, companies or market regimes.
9. Stage F — Internal Historical Stress Checks
Where feasible, use:
2010–2017: initial discovery.
2018–2021: internal stress checking.
But both periods have already been heavily exposed in earlier research.
2018–2021 must NOT be described as independent validation.
Use strict time boundaries when calculating forward-return labels so that a discovery-period observation does not obtain its future outcome from the internal stress period.
Examine whether candidate relationships persist across:

* Different calendar years.
* Bull and bear market episodes.
* Different sectors.
* Different company-size groups.
* Different return horizons.
* Different starting conditions.

Do not require every relationship to perform identically in every environment.
But investigate whether any apparent advantage is concentrated in a few extraordinary events.
Pay particular attention to the possibility that a historical result is largely explained by known dominant market winners.
10. Stage G — Identify Candidate Predictive Mechanisms
After analysing the historical evidence, determine whether any potentially useful relationships emerged.
These may be:

* Pure technical relationships.
* Pure fundamental relationships.
* Combined technical-fundamental relationships.

Do not favor a category in advance.
For every candidate, document:

1. The historical observation.
2. The measurable pre-decision signal.
3. Its relationship with subsequent relative returns.
4. Its success and failure base rates.
5. The magnitude and uncertainty of the observed effect.
6. What distinguishes it from rejected earlier research.
7. A plausible economic, behavioral or market-structure mechanism.
8. Why it might persist outside 2010–2021.
9. The main reasons it may fail.
10. The realistic implementation costs and limitations.

Rank at most three candidates using a clearly documented, exploratory assessment of plausibility, evidence quality, incremental information and tradability.
Select no more than one primary mechanism for strategy development.
If nothing credible emerges, report that result.
Do not invent a new trading edge to justify the research.
11. Stage H — Develop One Exploratory Strategy
If the historical study reveals a genuinely promising mechanism, translate it into a single deterministic strategy using existing infrastructure.
Define:

* Point-in-time stock eligibility.
* Required data and publication timing.
* Exact signal calculations.
* Stock-selection and entry rules.
* Portfolio construction.
* Position sizing.
* Exit and holding rules.
* Rebalancing frequency.
* Cash management.
* Trading costs.
* Risk and concentration limits.

Use the existing portfolio constraints unless a change is explicitly approved:

* Initial capital: $100,000.
* No leverage or short selling.
* Maximum 15 positions.
* Maximum 10% initial weight per position.
* Minimum $5,000 initial position.
* Maximum three stocks per sector where the applicable frozen strategy constraints require it.
* $7 commission per executed order.
* 0.10% slippage per side.
* Decisions at the close; execution at the next open.

Do not automatically assume that a Top-15 score or monthly rebalance is the optimal strategy construction.
Choose a simple implementation that is consistent with the observed mechanism and the frozen constraints.
Strategy evaluation
Freeze the exact specification and evaluation criteria before running the strategy backtest.
If the candidate is sufficiently credible and the existing infrastructure supports a responsible test, run one primary exploratory strategy and its necessary fixed controls.
No unrestricted parameter grid.
Compare against:

1. SPY total-return buy-and-hold.
2. An appropriate eligible-universe baseline.
3. A matched control that helps isolate the incremental selection mechanism.

Report:

* Terminal wealth.
* CAGR.
* Excess CAGR versus SPY.
* Relative terminal-wealth multiple.
* Performance in SPY-positive periods.
* Upside and downside capture.
* Market beta and risk-adjusted performance.
* Maximum drawdown.
* Volatility and Sharpe.
* Turnover.
* Realistic execution costs.
* Average and maximum holding periods.
* Sector concentration.
* Contribution of individual stocks.
* Results by calendar year and historical subperiod.

Explain whether any apparent improvement comes from genuine selection information, market exposure, sector concentration, rare exceptional winners or lower trading costs.
Any historical outperformance observed here remains exploratory, not independently validated.
If the data-quality or methodology requirements prevent a responsible backtest, preserve the discovery findings and report the specific blocker rather than building a new framework.
12. Holdout Rules
The Holdout period is:
2022-01-01 through 2026-08-31.
It must remain completely sealed during this assignment.
Do not inspect returns, select securities, tune parameters or calculate strategy performance using this period.
Only consider a future one-time Holdout test if:

1. One strategy has a clear and defensible economic or technical mechanism.
2. Its rules are completely frozen.
3. The existing exploratory evidence is meaningfully promising.
4. Apparent performance is not solely dependent on one company or market year.
5. Data-quality limitations are explicitly assessed.
6. The minimum detectable effect and test power are evaluated.
7. Exact Holdout success and failure criteria are pre-specified.

Even if these conditions are satisfied, STOP and request a separate explicit owner decision before opening the Holdout.
If the strategy later fails the Holdout, do not revise the strategy using those results and present a second attempt on the same period as independent validation.
Later modifications are possible, but they require genuinely new evidence for independent testing.
13. Execution Requirements
I do not want another research cycle dominated by theoretical arguments, infrastructure design or repeated feasibility reviews.
I want empirical discovery using the resources we already have.
Follow this sequence:
Stage A: Build the historical stock-outcome study.
Stage B: Analyse historical technical and price-action characteristics.
Stage C: Analyse historical fundamental and financial characteristics.
Stage D: Examine economically plausible combined technical-fundamental relationships.
Stage E: Measure predictive associations, false positives and robustness using appropriate controls.
Stage F: Conduct internal historical stress checks.
Stage G: Identify up to three candidate mechanisms and choose at most one.
Stage H: If justified, build and evaluate one deterministic exploratory strategy.
Reuse existing research code whenever possible.
Do not create another general-purpose engine.
Do not introduce unnecessary infrastructure.
Do not purchase additional data or services.
Do not reopen previously rejected hypotheses simply by renaming them.
Do not silently change the research scope or portfolio constraints.
If part of the analysis is blocked, document the limitation and continue with the remaining valid parts.
Do not stop after Stage A solely because perfect historical data or confirmatory statistical inference is unavailable.
However, if a material integrity problem invalidates the proposed measurements, STOP rather than producing misleading results.
Commit research specifications, reproducible aggregate results, code changes and checkpoints through the established GitHub workflow.
Keep restricted raw market data out of Git.
Do not repeatedly request approval for routine research steps already authorized here.
14. Required Final Report
The checkpoint must answer the following questions clearly:

1. How many companies and historical observations were analysed?
2. Which future-return horizons were studied?
3. What were the distributions of exceptional winners, ordinary stocks and major losers?
4. Which technical patterns preceded exceptional outperformance?
5. Which fundamental characteristics preceded exceptional outperformance?
6. Did any combination of technical and fundamental features improve the ability to distinguish winners from losers?
7. How common were the same features among unsuccessful stocks?
8. Which observations were explained by ordinary momentum, company size, sector exposure or market conditions?
9. Which relationships were stable across years and sectors?
10. What were the strongest apparent false positives?
11. Were any genuinely incremental predictive mechanisms found?
12. If a strategy was implemented, what were its actual results against SPY and the controls?
13. Which biases and data limitations remain?
14. Is there one promising strategy worth considering for a future independent Holdout test?

Provide actual numerical findings, not just descriptions of what could theoretically be analysed.
Use concise tables and clear conclusions.
Be explicit about negative findings.
If no usable relationship emerges, say so without manufacturing a strategy.
If a promising strategy emerges, record its exact specification and results, then STOP for owner review.
15. Final Research Philosophy
I want us to learn from the historical market rather than continuously guessing new indicator formulas.
The research should connect three things:
1. Historical outcomes: Which stocks actually created or destroyed wealth?
2. Information available beforehand: What technical, fundamental or combined characteristics could investors have observed before those outcomes?
3. Practical predictability: Did those characteristics distinguish successful investments from comparable failures sufficiently to justify a real trading rule?
A profitable strategy does not need to be based entirely on fundamentals.
A technical pattern may be valuable if it provides genuinely useful predictive information beyond what has already been tested.
Likewise, a financial characteristic may be useful even when its price behavior is unremarkable.
The strongest opportunity might involve a combination of market behavior and business improvement — but that must emerge from evidence, not from an assumption.
Study what worked, study what failed, identify what could have been known in advance, and determine whether those differences could support a systematic strategy capable of outperforming SPY.
Prioritize useful empirical discovery without compromising point-in-time integrity.
Do not confuse descriptive associations with validated alpha.
Do not use the sealed Holdout.
Do not force positive results.
Proceed with the actual historical analysis, not another design-only review.
