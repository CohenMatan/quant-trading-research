# Owner direction D292 — New technical trading research programme, Phase 1 only (2026-10-23)

**Context:** follows SO-CP0 (`docs/checkpoints/SO_CP0_spinoff_stage0_desk_review.md`, D291, PR #135). The message is recorded verbatim below, before any work.

---

Owner Direction — New Technical Trading Research Programme
1. Primary Objective
I want to refocus our quantitative trading research exclusively on technical analysis of stock price charts.
Our objective is to develop a systematic US equity trading strategy that can generate higher long-term terminal wealth than SPY, after realistic transaction costs and applicable capital-gains taxes.
The intended investment horizon is 20–30 years, but individual positions may be held for days, weeks, months, or years, depending on the technical conditions.
Maximizing terminal wealth is the primary objective.
Reducing volatility, drawdowns, or improving Sharpe ratio is useful only when it supports long-term wealth accumulation or protects against unacceptable risks such as permanent capital loss or ruin.
I am not interested in a defensive strategy that simply reduces drawdowns while consistently sacrificing terminal wealth.
There is no assumption that technical analysis can outperform SPY. The purpose of the research is to determine whether a credible, reproducible technical trading edge exists.
2. Research Philosophy — Hybrid Visual and Quantitative Approach
I want to combine Claude's chart-analysis capabilities with a fully systematic trading engine.
Claude's role during research:

* Examine historical stock price charts.
* Identify potentially meaningful price-action behaviors.
* Investigate market structures, trends, breakouts, consolidations, reversals and volatility changes.
* Help translate these observations into clear, measurable and falsifiable hypotheses.
* Critically evaluate whether a pattern has an economic or behavioral explanation.
* Avoid identifying patterns merely because they look profitable in hindsight.

The algorithm's role:

* Apply deterministic technical rules.
* Identify entry, hold and exit signals.
* Manage portfolio exposure and position sizing.
* Generate trade recommendations automatically.
* Evaluate the frozen strategy through rigorous historical tests and subsequent forward paper trading.

The final trading strategy must not depend on Claude subjectively interpreting charts during live execution.
Visual analysis is a research and explanation tool. Actual trading decisions must be determined by reproducible numerical rules.
Use blind historical chart analysis when appropriate: show only information available at the historical decision date, not future candles or later outcomes.
Chart samples must be selected by a pre-specified procedure and include strong stocks, weak stocks, unsuccessful setups, delisted stocks and multiple market conditions.
Visual inspection of already-exposed data is exploratory and cannot serve as independent validation.
3. Allowed Trading Information
All trading signals must be derived exclusively from:

* Open, high, low and close prices.
* Trading volume.
* Historical price and volume behavior.
* Technical indicators derived from price and volume.
* Relative price strength versus SPY or other market benchmarks.
* Historical market-price information available at the decision time.

Do not use financial statements, valuation ratios, earnings announcements, analyst forecasts, news sentiment, insider transactions or other fundamental information as trading signals.
Market capitalization and liquidity data may be used for universe eligibility, but not for ranking securities or determining entry and exit signals.
All data must be point-in-time correct.
4. Trading Style — Swing and Long-Term Trend Participation
I am open to both swing trading and long-term position holding.
I do not want a strategy that automatically exits after a fixed number of days merely because the historical research framework used that holding period.
A position should be able to remain open while its objectively defined holding conditions remain satisfied.
I want to investigate whether a complete technical entry-and-exit system can:

1. Identify stocks beginning or continuing meaningful upward moves.
2. Enter under defined technical conditions.
3. Avoid unnecessary exits during healthy trends.
4. Allow unusually successful positions to generate substantial gains.
5. Exit when objective technical conditions indicate deterioration or invalidation.
6. Reallocate available capital efficiently.

Possible technical concepts include trend structure, higher highs and higher lows, relative strength, breakouts, volatility-adjusted trailing stops, support violations and volume confirmation.
These are examples to investigate, not approved trading rules or an invitation to optimize indicator combinations.
An economic explanation is required for any proposed signal.
The specific mechanism of dynamic exits versus fixed holding periods is of interest because our earlier H018 research used a fixed 63-session holding period and did not proceed to its planned dynamic-exit stage.
However, do not assume changing the exit rules will rescue rejected entry signals or create alpha.
5. Investment Universe
The current research universe is:

* US-listed common stocks.
* Market capitalization >= $2 billion.
* Share price >= $5.
* ADV20 >= $5 million.

The $2 billion market-capitalization floor was originally selected to avoid relatively small, potentially volatile companies.
I am willing to reconsider the universe if there is a compelling economic and technical justification.
However:

* Market capitalization alone is not a sufficient volatility or risk filter.
* Do not relax the size or liquidity requirements solely to improve historical returns.
* Any change requires an assessment of spreads, liquidity, delistings, survivorship bias and point-in-time data availability.
* Any proposed universe change requires separate owner approval before implementation or testing.

Use the existing universe as the initial reference, not as an unquestionable permanent requirement.
6. Portfolio Construction — Open for Research
Unlike our previous research, the following portfolio rules are not fixed requirements:

* Maximum 15 positions.
* Minimum $5,000 per position.
* Maximum 10% initial allocation per position.
* Equal-weight allocation.

You are authorized to evaluate and recommend the portfolio construction rules that best support our objective of outperforming SPY in long-term terminal wealth.
Specifically, investigate:
Number of positions

* What level of diversification makes economic sense for a technical trend-following stock portfolio?
* When does concentration help or hurt terminal wealth?
* Should the number of positions be fixed or depend on the number of valid technical opportunities?

Position sizing

* Equal-weight, volatility-aware, risk-budgeted or another deterministic method.
* Appropriate minimum and maximum position sizes.
* Whether a position should be allowed to grow beyond its initial allocation as its price rises.
* When, if ever, rebalancing an existing winner is justified.
* How portfolio-level concentration and correlated stock exposure should be controlled.

Capital allocation

* How to prioritize valid signals when available capital is insufficient.
* Whether new positions should be funded only from cash or by selling existing holdings.
* Whether a stronger technical opportunity should replace a weaker position.
* How uninvested capital should be managed.
* Whether SPY should eventually be permitted as a holding for otherwise idle capital.

Portfolio risk

* Exposure to individual securities.
* Industry and sector concentration.
* Correlated positions.
* Portfolio drawdowns.
* Gap risk.
* Liquidity and execution risk.

Important: Do not choose portfolio parameters based on which configuration produced the highest returns in previously exposed historical data.
Recommend a defensible portfolio structure based on economic reasoning, implementation constraints and risk considerations.
All final rules must be deterministic and frozen before strategy-performance evaluation.
No actual portfolio-rule changes are authorized in this phase.
7. Fixed Investment and Execution Constraints
Unless separately approved, retain:

* Initial research capital: $100,000.
* US equities.
* Long-only.
* No leverage.
* No short selling.
* No borrowing to fund trades.
* Realistic execution and settlement rules.
* Point-in-time information only.
* Trades executed no earlier than the next available trading session after a signal.

The strategy must account for stock splits, dividends, acquisitions, delistings, trading suspensions and opening-price gaps.
Stops must not assume execution at an unavailable stop price when the market gaps beyond it.
Do not silently assume fractional shares, unlimited liquidity or instant execution.
8. Commissions, Slippage and Taxes
My brokerage commission is:

* $7 per purchase.
* $7 per sale.

Retain realistic slippage and spread assumptions. The previous 10 bps per side model may be used as a starting reference, subject to assessment.
For taxation, assume a preliminary Israeli capital-gains tax rate of 25%, with applicable capital-loss offsets or tax shields.
However, the actual tax model must be confirmed before it is finalized.
Important requirements:

* Model realized gains and losses separately from unrealized gains.
* Recognize loss offsets only when legally applicable.
* Do not treat losses as automatic immediate tax refunds.
* Consider the timing of taxable events and loss carryforwards where applicable.
* Treat dividends consistently.
* Compare the strategy and SPY using equivalent tax assumptions.
* Include a consistent terminal-liquidation assumption when comparing final wealth.

Eventually report:

1. Terminal wealth before taxes.
2. Terminal wealth after taxes.
3. CAGR before and after taxes.
4. Total trading costs.
5. Tax drag.
6. Turnover.
7. Results against SPY under the same assumptions.

The primary economic objective is after-tax terminal wealth, subject to a validated tax model.
Do not implement the final taxation model before the necessary account-specific assumptions are confirmed.
9. Market Exposure and Idle Capital
I want you to examine the implications of two approaches:
A. Cash when there are no valid stock signals.
B. Holding SPY with capital not currently allocated to individual technical trades.
The objective is to avoid unnecessary long-term cash drag while preserving the strategy's ability to take technical opportunities.
However, SPY as an actual holding would require changes to our existing stocks-only and portfolio concentration rules.
Do not make those changes automatically.
Do not choose the better-performing approach using already-exposed historical results.
Provide an economically justified recommendation and identify the necessary owner decisions.
10. Human Approval of Real Trades
The eventual system should identify opportunities and generate recommendations automatically.
Real trades must be explicitly approved by me.
The planned workflow is:

1. Run the technical analysis.
2. Identify eligible buy, sell and hold signals.
3. Calculate proposed trade sizes and capital requirements.
4. Produce recommendations with the technical reasons.
5. Send the recommendations to me for review.
6. Execute only approved real orders through an explicitly authorized brokerage integration.

Every recommendation should include:

* Stock symbol.
* BUY, SELL or HOLD decision.
* Signal date and time.
* Technical explanation.
* Relevant chart and indicator values.
* Proposed order details and sizing.
* Expected commissions and execution risks.
* The technical conditions that would invalidate the trade.
* Effect on available cash and portfolio exposure.

If my approval is delayed or missing, the system must not pretend the trade executed at an earlier historical price.
A separate and deterministic expiration or reassessment policy will be needed for delayed approvals.
Historical research must evaluate the automatic strategy independently of human discretionary approvals.
In forward operation, maintain separate records for the systematic model and the actually approved trades.
No live-order execution or broker integration is authorized now.
11. Mandatory Audit of Previous Technical Research
Before proposing a new technical strategy, review our repository and prior experiments thoroughly.
Focus especially on:

* H001–H014.
* H018, including its 1,533-configuration technical search.
* H019 and H020.
* Prior trend, breakout, pullback and reversal experiments.
* Existing trailing-stop or dynamic-exit experiments, if any.
* The Phase 3 null-world analysis.
* The prior ranking, holding, portfolio and exit mechanics.

I want precise answers to:

1. Which technical entry rules were actually tested?
2. Which holding-period and exit mechanisms were used?
3. Which technical exits were never tested?
4. Which hypotheses were rejected versus inconclusive?
5. Which previously tested configurations were particularly vulnerable to overfitting?
6. What does the H018 null-world research tell us about the risk of discovering fake winners?
7. Which fundamentally different technical trading questions remain open?

Distinguish clearly between:

* A genuinely new research architecture.
* A new exit mechanism paired with a previously tested entry.
* A parameter variation of a previously rejected strategy.
* Repeating the same hypothesis under a different name.

Do not reopen rejected hypotheses or reuse historically successful diagnostic portfolios as candidates without explicit owner approval.
The purpose is to identify a legitimate new question, not to rescue previous failures.
12. Research Design — Entry, Holding and Exit as One System
Our new research should consider three distinct components.
Entry
What objective price-and-volume behavior is supposed to identify a worthwhile opportunity?
Holding
What objective conditions justify continuing to hold a position, especially one that has already appreciated significantly?
Exit
What objective technical development indicates the position should be reduced or closed?
These components must be evaluated within a complete portfolio, not independently optimized until the historical results look attractive.
Where methodologically possible, distinguish:

* Whether entry signals identify favorable future returns.
* Whether exit rules add value over an appropriate pre-specified reference exit.
* Whether position sizing and portfolio allocation add value beyond simple benchmarks.
* Whether overall excess returns come primarily from market beta, sector exposure, concentration or genuine signal quality.

Any such decomposition must use pre-defined comparisons, not searches over multiple exit or sizing variants.
Do not optimize entries, exits and sizing jointly across a large grid.
13. Research Integrity and Validation
Our 2010–2021 development period has already been heavily explored.
The 2022-01-01 through 2026-08-31 Holdout remains sealed and reserved under existing programme governance.
QuantConnect has historical price data before 2010, including some delisted securities, but point-in-time market-cap data and historical universe completeness remain unresolved for that period.
Therefore:

* Do not treat 2010–2021 as independent validation.
* Do not use the sealed Holdout to discover rules.
* Do not assume pre-2010 prices alone establish a reliable investable universe.
* Audit the historical universe before any proposed pre-2010 confirmatory test.
* Include delisted and acquired securities where applicable.
* Avoid survivorship bias, look-ahead bias, indicator warm-up leakage and corporate-action errors.
* Account for the full history of prior strategy searches when interpreting new results.
* Pre-register one primary specification and its evaluation protocol before testing returns.

Historical chart illustrations viewed during strategy development cannot later be counted as independent test observations for that same strategy.
No strategy should be declared validated simply because a Backtest beats SPY.
If there is no credible independent evidence path, identify that blocker before authorizing performance experiments.
14. Proposed Research Phases
I want the programme organized into the following phases, with an owner approval gate between them.
Phase 1 — Previous Research Audit and Feasibility
Review prior technical work, available data and independent-validation constraints.
Phase 2 — Blind Chart Analysis
Use a balanced historical sample to investigate technical behaviors and express them in measurable language.
Phase 3 — Single Strategy Design
Select at most one economically justified entry/holding/exit architecture.
Recommend portfolio construction, exposure and sizing rules.
Phase 4 — Specification Freeze and Mechanical Verification
Freeze strategy rules, costs, data definitions, execution model and evaluation protocol.
Run synthetic tests and limited integrity checks only with separate approval.
Phase 5 — Controlled Strategy Evaluation
Run the approved backtest and frozen comparison suite.
Require meaningful excess wealth after costs, robustness to execution assumptions, and evidence beyond market exposure or selection luck.
Phase 6 — Forward Paper Trading
If justified by independent evidence, operate a forward signal-generation system with explicit human approval.
Track the automatic model separately from approved trade outcomes.
No phase may begin without the required owner decision.
15. Immediate Assignment — Phase 1 Only
For now, I authorize Phase 1: research audit and design assessment only.
Prepare one checkpoint titled:
Technical Trading Research — Phase 1: Prior Research Audit and New System Architecture
The document should include:

1. Prior technical research audit: an exact account of previously tested entry, holding and exit mechanics, with repository references.
2. Remaining research opportunities: identify technical trading questions that are genuinely different from the rejected approaches.
3. Chart analysis methodology: explain how Claude should inspect historical charts without future leakage, biased sample selection or cherry-picking.
4. Technical vocabulary: propose measurable descriptions of market structure, trend continuation, relative strength, volatility, breakouts, invalidation and exits.
5. Portfolio construction: recommend how to determine position count, sizing, concentration limits, winner management and capital allocation before any return-based optimization.
6. Universe feasibility: assess whether the current $2B large-cap universe is suitable and what would be needed to change it responsibly.
7. Market exposure: evaluate the design implications of holding cash versus SPY with idle capital, without historical performance selection.
8. Cost and tax framework: identify requirements and unresolved assumptions for realistic after-tax comparison against SPY.
9. Validation architecture: propose a credible way to test a future strategy despite our heavily explored development sample, including blockers and stop conditions.
10. One preliminary research direction: recommend at most ONE genuinely distinct, economically motivated technical architecture worth designing next, if one exists.
11. Owner decisions: clearly list the minimum decisions required before Phase 2.

The checkpoint should distinguish:

* Facts demonstrated by our prior research.
* Assumptions.
* External literature.
* Proposed rules that are not yet approved.

If the evidence does not support a genuinely new, testable direction, recommend stopping rather than inventing another technical configuration.
16. Execution Boundaries
This task is DESIGN ONLY.
Do not:

* Register H033 or another new hypothesis.
* Implement a strategy.
* Run Backtests or performance calculations.
* Run an indicator or parameter search.
* Optimize position counts, sizing, stop distances or holding periods.
* Start chart sampling or view historical future-return outcomes.
* Access the sealed Holdout.
* Modify existing investment constraints.
* Purchase data or services.
* Begin paper or real trading.
* Create a brokerage integration.
* Reopen H018, H028, H032 or other rejected hypotheses.

H031 remains parked. RR6 remains INCONCLUSIVE.
Use the existing repository, research records and infrastructure wherever possible.
Keep the document practical and decision-oriented rather than creating another large speculative research roadmap.
Record the owner direction, commit the checkpoint through the normal repository workflow, and STOP for my review.
Final Research Question
Can we design a disciplined, price-and-volume-based stock trading system—with objectively defined entries, potentially long holding periods, intelligent technical exits and economically justified portfolio construction—that has a credible and independently testable opportunity to outperform SPY in long-term after-tax terminal wealth?
I want a rigorous answer and a realistic research path, not a strategy that merely looks profitable in historical charts.
