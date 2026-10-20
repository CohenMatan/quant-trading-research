# Owner decision D274 — Next research phase: Offensive Stock Selection Score (2026-10-20)

**Context:**
- This follows RR7 (D273, `docs/checkpoints/RR7_research_path_design_review.md`, PR #127).
- The message is recorded verbatim below, before any work.

---

Owner Direction — Next Research Phase: Offensive Stock Selection Score

I want to redirect our research toward developing an offensive US equity stock-selection strategy, potentially using a scoring and Top-N portfolio construction approach similar in architecture to H028.

This is a new research direction, not a continuation or optimization of H028.

1. Long-Term Investment Objective

Our long-term objective is to build a portfolio with two complementary components:

Offensive component — our immediate priority

- Identify stocks expected to outperform SPY during rising markets.
- Generate meaningful upside participation and ideally upside capture above 1.0.
- Seek genuine excess returns, rather than simply increasing market beta or concentrating in high-volatility stocks.
- Aim for robust performance across different bullish regimes and long investment horizons.

Defensive component — future research

- Protect capital during significant market declines.
- Potentially draw on ideas from H028 or other defensive approaches.
- H028 remains formally REJECTED and is not authorized for reuse as a validated strategy.

Ultimate portfolio

- Eventually investigate whether combining offensive and defensive components produces higher terminal wealth than SPY over full market cycles, after realistic costs.
- Portfolio combination and allocation optimization are NOT part of the current phase.

For now, focus exclusively on the offensive component.

2. Preferred Research Architecture

I want to seriously investigate the following approach:

Stock characteristics → Offensive Score → Rank eligible stocks → Select Top N → Construct and rebalance portfolio.

H028 used a learned multi-factor score and selected the Top 15 stocks.

We may reuse that general portfolio architecture, but NOT its rejected predictive model, coefficients, or historical conclusions.

Evaluate whether a transparent offensive scoring model can identify stocks with stronger expected upside relative to SPY.

Consider both:

- A simple, economically motivated scoring formula with fixed, pre-registered rules.
- A learned score, only if there is a credible way to fit and evaluate it without excessive overfitting or reproducing the failed H026–H028 research.

Do not assume machine learning is superior to simpler ranking models.

Top 15 is a preferred starting architecture, not permission to optimize the number of holdings.

Preserve the existing long-only, no-leverage, market-cap, price, liquidity, position-size, execution and transaction-cost constraints.

3. Learn From Previous Research

Review the completed H001–H030 research, especially:

- H019 — momentum and trend-related signals.
- H024 — feature selection.
- H026 — learned stock score.
- H027 — exposure-controlled score.
- H028 — fixed-shrinkage learned score.
- OC-2 — independent offensive candidate investigation.
- RR1–RR7 — current platform and universe limitations.

Identify exactly why previous scoring and offensive strategies failed their research gates.

Do not propose another combination of previously rejected features or a new weighting scheme unless there is a genuinely different, independently motivated economic hypothesis.

Distinguish a new source of predictive information from a repackaging of momentum, quality, low volatility, growth or market beta.

Previous development results must not be used to choose parameters that merely maximize historical performance.

4. Identify a Credible Offensive Signal

Investigate 2–3 specific economic mechanisms that could plausibly produce stock-level outperformance during rising markets.

For each mechanism, assess:

- The economic reason it might create persistent excess returns.
- Whether it is supported by credible published research available before the development period, rather than hindsight from our own results.
- How it differs from H001–H030.
- Which indicators and data fields would be required.
- Whether those fields are genuinely point-in-time.
- Whether they are available through our existing QuantConnect subscription or existing independently sourced SEC data.
- Potential exposure to the unresolved stock-universe bias.
- Expected turnover, transaction costs and capacity.
- How to distinguish genuine selection alpha from market beta and known factor exposures.
- The simplest experiment capable of falsifying the hypothesis.

Recommend ONE specific mechanism to pursue first.

Do not produce a broad catalogue of speculative indicators.

If no sufficiently distinct and credible scoring hypothesis exists, report that explicitly rather than inventing one.

5. Define the Offensive Score

For the recommended mechanism, prepare a concrete, freeze-ready scoring specification.

Include:

1. Exact input fields and point-in-time availability rules.
2. Mathematical scoring or ranking formula.
3. Any required normalization.
4. Handling of missing values, corporate actions and security identity.
5. Stock ranking and Top-N selection rules.
6. Portfolio sizing, sector concentration, rebalancing and execution timing.
7. How the score is expected to identify potential outperformers rather than simply high-beta stocks.
8. The minimum implementation required using existing research modules.

If learned coefficients are proposed, explain exactly how they would be estimated without information leakage or unapproved parameter searches.

Prefer simple, explainable rules and a single primary specification.

6. Evaluation Framework

Propose a pre-registered exploratory evaluation framework that specifically measures offensive performance.

The evaluation should include:

- Upside capture relative to SPY.
- Excess performance during SPY-positive months and bullish market regimes.
- Terminal wealth relative to SPY after costs.
- Performance across the fixed 2010–2015 and 2016–2021 development subperiods.
- Market beta and a suitable beta-matched comparison.
- Comparison with relevant simple factor and same-universe controls.
- Downside capture, maximum drawdown and volatility as risk diagnostics.
- Robustness to higher trading costs.
- Concentration of excess performance in individual years or market events.

Define bullish-market periods in advance. Historical regime labels used only for evaluation must not leak future information into trading decisions.

The offensive component does not need to be defensive, but its upside advantage must not be explained solely by taking greater market risk.

Preserve the distinction between exploratory candidate discovery and independent validation.

7. Current Data Restrictions

RR6 remains INCONCLUSIVE.

RR7 is a design checkpoint, not permission to trade the SEC-repaired universe.

Any eventual exploratory strategy test must first have an explicitly approved protocol addressing the unresolved universe bias, including appropriate comparisons between the repaired and original vendor universes.

The 2010–2021 development period has already been extensively researched and cannot provide independent confirmation.

The Holdout covering 2022-01-01 through 2026-08-31 remains sealed.

Do not reinterpret old rejected strategies as validated.

8. Budget and Simplicity

Use only our existing QuantConnect subscription, existing SEC data and existing code.

No additional purchases, subscriptions or paid datasets.

No new SEC identity-repair cycle.

No substantial infrastructure redesign.

Favor reusing the current research harness, scoring utilities, portfolio simulator and evaluation modules where technically and legally appropriate.

The priority is to get back to testing meaningful investment hypotheses, not to build another complex research system.

9. Scope and Deliverable

This phase is DESIGN ONLY.

Produce a concise checkpoint titled:

Offensive Score Research — Candidate Selection and First Experiment Design

The report must contain:

- Lessons from H026–H028 and OC-2.
- Comparison of 2–3 genuinely distinct offensive mechanisms.
- One recommended hypothesis.
- A concrete scoring and Top-N portfolio specification.
- Point-in-time data feasibility assessment.
- Proposed exploratory evaluation criteria and stopping rules.
- Minimum implementation and canary requirements.
- Estimated work required to reach the first legitimate strategy backtest.
- Specific owner decisions needed to authorize that test.

Do not register or run a new hypothesis yet.

Do not perform backtests, analyze new strategy returns, optimize weights, alter the existing universe, reopen H028, access the Holdout or purchase anything.

Commit the checkpoint through the normal workflow and STOP for my review.

The objective of this phase is to produce ONE actionable offensive stock-selection hypothesis, not another open-ended research roadmap.
