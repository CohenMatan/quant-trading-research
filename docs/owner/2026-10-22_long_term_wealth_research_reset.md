# Owner direction D288 — Long-term wealth research reset (2026-10-22)

**Context:** follows SA-CP1 (`docs/checkpoints/SA_CP1_post_h032_architecture_review.md`, D287, PR #133). The message is recorded verbatim below, before any work.

---

Owner Direction — Strategic Research Reset: Finding a Credible Path to Outperform SPY
1. Our Primary Objective
After 31 registered hypotheses, 588 logged experiments, and no validated production candidate, I want to reconsider our overall research direction.
Our primary investment objective is:
Maximize long-term terminal wealth over a 20–30-year investment horizon, with the goal of outperforming SPY after realistic transaction costs.
This objective takes priority over minimizing volatility, improving Sharpe ratio, or reducing maximum drawdown.
I am willing to consider substantial temporary drawdowns if the strategy has a credible, evidence-supported prospect of producing higher long-term terminal wealth.
However, this does not mean ignoring permanent capital loss, extreme concentration, liquidity problems, or risks of ruin.
A defensive strategy that merely reduces drawdowns while sacrificing terminal wealth is not what I am looking for.
Do not propose defensive research unless there is a credible economic mechanism through which it could improve long-term terminal wealth.
2. Reassess Our Existing Constraints
Our research has operated under several restrictions:

* US equities only.
* Long-only, no leverage.
* Market capitalization ≥ $2 billion.
* Stock price ≥ $5.
* ADV20 ≥ $5 million.
* Maximum 15 positions.
* Minimum $5,000 per position.
* Maximum 10% initial allocation per position.
* $100,000 starting portfolio.
* Realistic commissions and slippage.
* Point-in-time data and next-session execution.

I want you to critically evaluate which of these restrictions are economically justified and which may unnecessarily limit our ability to discover meaningful excess returns.
For each potentially restrictive rule, explain:

1. Why it was originally useful.
2. How it may limit the opportunity set or portfolio construction.
3. What economic advantage relaxing it might make accessible.
4. What new risks, transaction costs, liquidity requirements or data problems would result.
5. Whether changing it could plausibly improve terminal wealth rather than merely improving a backtest.
6. Whether the required data and testing infrastructure are available within our existing resources.

Do not automatically recommend removing constraints.
Distinguish constraints that protect research integrity from constraints that limit investment opportunities.
3. Understand What Our Previous Research Actually Established
Review the completed H001–H032 programme, especially:

* Momentum and technical strategies.
* Quality and profitability.
* Earnings-related signals.
* Insider buying.
* Multi-factor and learned scoring models.
* H026–H028.
* H032 and its Top-15 portfolio.
* RR1–RR7 universe and data limitations.
* SA-CP1 architecture review.

Identify which economic mechanisms were genuinely tested and rejected, which were inconclusive, and which were never successfully evaluated.
Do not interpret a failure to discover alpha as proof that alpha cannot exist.
At the same time, do not recycle previously rejected hypotheses under new names.
Explain whether the main limitations appear to come from:

* The economic weakness of the signals.
* The large-cap and liquidity restrictions.
* Concentrated portfolio construction.
* Benchmark-relative market exposure.
* Insufficient statistical power.
* Data quality or survivorship issues.
* Excessive prior searching and overfitting.

Separate demonstrated findings from hypotheses or interpretation.
4. Identify Genuinely Different Sources of Potential Outperformance
Explore at most THREE materially different research directions that could plausibly outperform SPY over long horizons.
I am interested in genuine economic mechanisms, not another arbitrary combination of indicators.
Potential areas to examine, only if justified, include:

* Different equity market-cap segments or investment universes.
* Structural or behavioral market inefficiencies.
* Long-term return premia and their associated risks.
* Portfolio construction approaches that differ fundamentally from our existing equal-weight Top-15 architecture.
* Other simple, economically motivated approaches consistent with long-term wealth accumulation.

You are not required to recommend any of these categories.
For each direction, explain:

1. The economic source of expected excess return.
2. Why it might persist despite competition.
3. What credible academic or empirical evidence supports it.
4. Whether the advantage remains plausible after publication and transaction costs.
5. Whether it is genuinely distinct from our previous tests.
6. Whether it can work without leverage.
7. Expected risks and potential long-term drawdowns.
8. Data requirements and point-in-time limitations.
9. Whether we can investigate it with our existing QuantConnect subscription and public data.
10. How it could eventually be validated without relying on already-exposed development data.

Do not recommend a direction merely because its historical returns were higher than SPY during 2010–2021.
5. Research Integrity and Independent Validation
Our 2010–2021 development data has already been heavily explored.
The 2022–2026 Holdout remains sealed and is reserved for at most one programme candidate under the existing rules.
Pre-2010 QuantConnect universe data is not currently reliable for our prior stock-selection framework.
Therefore:

* Do not use the existing Holdout.
* Do not mine previous strategy results to select promising variations.
* Do not assume changing the universe automatically solves statistical overfitting.
* Clearly explain how a new direction could generate genuinely independent evidence.
* Assess whether forward testing, independent public data or additional historical data would be necessary.

Any proposal to buy data must be presented as a separate future decision, not an authorized expense.
6. Budget and Practicality
For now, use only the resources we already have.
No new purchases, subscriptions or paid datasets.
Avoid another extensive infrastructure project unless there is a compelling, clearly explained reason.
The goal is not to conduct another 500 experiments.
I want a small number of well-founded, falsifiable research ideas with a realistic path to testing.
7. Required Deliverable
Produce a concise strategic checkpoint titled:
Long-Term Wealth Research Reset — Constraints, Opportunity Set and Next Direction
It must contain:

1. A clear assessment of why the existing research programme has not produced an offensive strategy that beats SPY.
2. A table evaluating our current constraints and recommending which should remain, which should be reconsidered, and why.
3. A comparison of no more than three genuinely different economic directions.
4. An assessment of expected economic advantage, risk, transaction costs, data requirements and independent validation feasibility for each.
5. A concrete recommendation for ONE direction to investigate next, if a credible one exists.
6. The minimum work and owner decisions needed to investigate that direction.
7. A clear alternative recommendation to pause the programme if no direction is sufficiently credible.

Do not invent an opportunity simply to keep the research project going.
8. Execution Boundaries
This phase is DESIGN AND RESEARCH REVIEW ONLY.
Do not:

* Register a new hypothesis.
* Run any backtests or strategy-return calculations.
* Optimize parameters or portfolio weights.
* Change our investment constraints.
* Purchase data or services.
* Implement new infrastructure.
* Reopen rejected hypotheses.
* Access or modify the Holdout.

H032 and H028 remain REJECTED. H031 remains parked. RR6 remains INCONCLUSIVE.
Use our existing research records and credible independent literature where appropriate.
Commit one decision-oriented checkpoint through the normal workflow, then STOP for my review.
Final Question
Given everything we have learned, what is the most economically credible and practically testable path toward building a long-only, unleveraged portfolio that can outperform SPY in terminal wealth over 20–30 years?
If our current restrictions are preventing us from investigating the most promising opportunities, identify them.
If the evidence does not support a credible path, explain that clearly instead of proposing another weak strategy.
