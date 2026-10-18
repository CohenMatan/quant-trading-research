# Owner message — 2026-10-18 (D241)

**Scope recorded by Claude:** DESIGN ONLY.
- Approved: a design checkpoint (`docs/checkpoints/RM2_h028_defensive_reference_offensive_companion_design.md`), recording this instruction, roadmap updates, a documentation-only PR.
- Not approved: H031, any backtest, synthetic experiment, null world, real-data H028 recalculation, Ridge retraining, H028 change, OF-A training or implementation, combined-portfolio implementation, Holdout access, data purchase, changes to frozen gates or results, reopening Phase 13 or 14.
- H028 stays REJECTED. "Frozen Defensive Research Reference" is a descriptive designation only.

The message follows verbatim.

---

# New Research Programme — H028 Defensive Reference + Offensive Companion

## Owner Approval: Design-Only Phase

I approve a new **design-only research checkpoint** exploring an investment architecture built around:

1. The frozen H028 learned-score portfolio as a defensive research reference.
2. A potential independently motivated offensive stock-selection strategy.
3. A future combined portfolio designed to outperform SPY over a long investment horizon.

**This is not approval to run experiments, build new strategies, change H028, or access the Holdout.**

The purpose is to design a credible research path without discarding the economically interesting findings from H028.

---

# 1. Verify the Current Project State

Before making changes, inspect:

- Current `main` branch.
- D240 and the research-cycle closure.
- `research/hypotheses/STATUS.md`.
- H028's original specification and checkpoints.
- P13-CP4, P13-CP5 and P13-CP6.
- The current 30-year research roadmap.
- Relevant Phase 14 / H029 / H030 materials.
- Existing owner decisions and research-governance rules.

Confirm:

- Phases 13–14 are CLOSED.
- H028 remains REJECTED.
- H029/H030 are NOT EVALUABLE.
- No production candidate exists.
- No new hypothesis is active.
- The 2022–2026 Holdout is sealed.

Do not assume anything beyond the repository records.

---

# 2. Our Actual Investment Objective

The objective is to build an autonomous long-only US-stock investment system that:

**Accumulates more terminal wealth than SPY Buy & Hold over approximately 30 years, after realistic costs, without leverage and with acceptable risk.**

We do not require outperformance every calendar year.

We do not necessarily require outperformance in the majority of calendar years.

A strategy may lag SPY for extended periods and still be economically successful over 30 years.

However, we must understand:

- How often it underperforms.
- How deep relative underperformance becomes.
- How long it may remain behind.
- How it performs in extended bull markets.
- How much of its final return depends on a few exceptional periods.
- Whether the investor could realistically tolerate the drawdowns and relative underperformance.

The primary long-horizon statistic is:

S = ln(W_strategy / W_SPY)

where both portfolios use identical starting capital, dates and realistic costs.

Annual win rate should be a diagnostic rather than a universal qualification requirement for future hypotheses.

Do not retroactively relax H028's failed B4 gate.

---

# 3. H028 Must Be Preserved

The historical H028 development result for 2015–2021 was approximately:

| Metric | H028 | SPY |
|---|---:|---:|
| Starting wealth | $100,000 | $100,000 |
| Terminal wealth | $328,295 | $262,325 |
| CAGR | 18.5% | 14.8% |
| Volatility | 16.2% | 17.7% |
| Maximum drawdown | -26.1% | -33.7% |
| Beta | 0.76 | 1.00 |
| Up capture | 0.97 | 1.00 |
| Down capture | 0.69 | 1.00 |

These are historical development results, NOT independently confirmed future performance.

H028:

- Failed B4.
- Has unreliable original conditional-null significance.
- Could not be validated using the attempted repaired-null methods.
- Remains formally REJECTED.
- Must not be used in production.

However, its observed economic profile is relevant to architecture design.

**For the new design phase, call H028 the "Frozen Defensive Research Reference".**

This is a descriptive research designation, not a change in qualification status.

Preserve exactly:

- All 11 feature definitions.
- Learned-score methodology.
- Fixed Ridge penalty λ = 100.
- Existing training and portfolio rules.
- Top-15 construction.
- Sector and position caps.
- Rebalance schedule.
- Costs.
- Existing numerical results.

No tuning, rescue or new H028 version.

---

# 4. Why We Are Exploring a Complement

H028 historically combined:

- Lower market beta.
- Relatively strong upside participation.
- Lower downside participation.
- Attractive terminal wealth versus SPY.

But its excess wealth was concentrated in a small number of historical market episodes, particularly 2018 and 2020.

We do NOT know that this behavior will persist.

The research question is:

**Could an independently justified offensive strategy add a different source of long-term return and improve the wealth accumulation of a portfolio that includes a defensive exposure like H028?**

Do not interpret this as an instruction to find a model that happens to win in the specific years when H028 lost.

That would be hindsight optimization.

We seek a genuinely distinct economic mechanism.

---

# 5. Separate Three Research Questions

We need to avoid combining multiple unproven ideas into one backtest.

## Question A — Defensive reference

What economic exposures does H028 appear to represent, and how could those exposures be replicated or benchmarked transparently?

## Question B — Offensive signal

Is there an independently justified predictive stock-selection signal that could generate long-term appreciation after realistic implementation costs?

## Question C — Portfolio combination

Would combining a defensively oriented portfolio with an independently useful offensive strategy plausibly improve long-term wealth and risk characteristics relative to SPY and simpler alternatives?

These questions must be evaluated separately before considering a combined system.

A strong result on C cannot retroactively validate A or B.

---

# 6. Design the Offensive Companion

Our initial preferred research family is:

**OF-A — Fundamental Surprise and Acceleration.**

Investigate this as a candidate offensive signal, not as a predetermined winning strategy.

Potential information includes:

- Accounting earnings surprise.
- Revenue surprise.
- Earnings acceleration.
- Revenue growth acceleration.
- Operating-profit improvement.
- Changes in fundamental expectations inferred from reported results.

However, distinguish genuine surprises from simple historical growth rates.

A company reporting 20% revenue growth is not necessarily surprising investors.

Explain possible definitions that use only information available at the time of each filing.

For example, compare newly reported results with an expectation formed from earlier public financial statements.

If using accounting data, investigate:

- Same-quarter year-over-year comparison.
- Seasonal adjustments.
- Historical forecast baselines.
- Fiscal-calendar irregularities.
- Restatements.
- SEC filing acceptance time.
- Missing quarters.
- Non-comparable accounting items.
- Outliers and negative earnings.
- Changes in reporting standards.

Do not settle on a formula yet.

Do not build the signal.

---

# 7. Independent Economic Justification

Review the existing literature and committed research references supporting fundamental surprises and post-announcement drift.

Explain:

- Why the information might be underpriced.
- Why any advantage might persist in modern large-cap equities.
- Why it might have weakened over time.
- Why it could provide something different from momentum and profitability levels already tested.
- Whether it is plausibly relevant to long-term compounding rather than only short-lived trading reactions.

Specifically contrast OF-A with:

- H017 earnings-event price reaction.
- H016 profitability levels.
- H022–H024 financial factors.
- H026–H028 learned scores.
- H029 business-improvement features.

Avoid presenting already-tested factors under new names.

If OF-A lacks a sufficiently distinct economic justification, recommend against pursuing it.

---

# 8. Offensive Means Growth Potential, Not Excessive Risk

The offensive strategy should aim to participate effectively in sustained rising markets and identify businesses with meaningful appreciation potential.

But "offensive" does not mean:

- Leverage.
- Options.
- Microcap speculation.
- Unlimited concentration.
- Excessive turnover.
- Ignoring valuation or risk.
- High beta for its own sake.

Preserve the baseline universe:

- NYSE/Nasdaq US common stocks.
- Market cap >= $2B.
- Price >= $5.
- ADV20 >= $5M.
- Long-only.
- No leverage.
- No intraday trading.

Preserve realistic transaction costs.

The offensive candidate should be assessed on standalone long-term economics, not merely on whether it has negative correlation with H028 during already-seen periods.

---

# 9. First Test the Signal, Not a Top-15 Portfolio

One of the major lessons from D238 and P13-CP6 is that attempting to validate stock-picking skill only after constructing a concentrated portfolio is problematic.

Therefore propose a signal-first process.

The initial real-data evaluation, if later approved, should cover the eligible stock universe rather than immediately selecting a Top-15 book.

Investigate:

- Cross-sectional rank information.
- Forward excess-return relationships.
- Sector-controlled results.
- Size-controlled results.
- LOWVOL-controlled results.
- Growth/value and profitability controls.
- Persistence across filing events.
- Signal decay across different holding horizons.

A signal-level test may use a Fama–MacBeth-type procedure or another defensible cross-sectional method.

But no method is approved merely because it is statistically standard.

It must pass an independently frozen synthetic-validation protocol first.

Synthetic scenarios must include:

- No true signal.
- Priced LOWVOL.
- Priced growth.
- Priced profitability.
- Sector correlation.
- Stock entries and exits.
- Time-varying factor premia.
- Overlapping forward returns.
- Persistent characteristics.
- A genuinely planted signal.

The previous false-positive problems must not recur.

Do not perform synthetic or real-data tests during this design checkpoint.

---

# 10. Standalone Offensive Evaluation

If a future offensive signal passes its signal-level evaluation, a separate approval may allow portfolio construction.

That portfolio would need a pre-registered specification for:

- Selection count.
- Score construction.
- Position sizing.
- Sector concentration.
- Rebalancing.
- Holding periods.
- Risk control.
- Cash handling.
- Trade execution.
- Commissions and slippage.

Evaluate standalone performance against:

1. SPY Buy & Hold.
2. An eligible-universe benchmark.
3. A transparent benchmark that reflects the strategy's main style exposures.

This is essential.

We do not want an offensive model whose apparent skill is explained entirely by holding high-beta growth stocks during a favorable historical period.

---

# 11. Defensive Benchmarks Must Be Included

H028 is not the only conceivable defensive portfolio.

Future research should compare it with transparent alternatives:

- SPY.
- Frozen LV15.
- USMV.
- SPLV.
- A quality ETF such as QUAL.
- A pre-specified SPY + defensive ETF mix.
- A beta-matched defensive benchmark.

Verify actual instrument availability and historical inception dates before any future test.

Do not optimize benchmark weights retrospectively.

The economic question is not merely:

**Does H028 look good?**

It is also:

**Does H028 justify its additional complexity, turnover and stock-specific risk compared with simple investable defensive alternatives?**

If not, the eventual architecture might use a transparent defensive ETF instead.

Do not presume H028 must be included in the final system.

---

# 12. Future Combined Portfolio

If the offensive strategy demonstrates useful independent evidence, a future hypothesis may combine it with a defensive reference.

Conceptually:

Combined = w_D × Defensive + w_O × Offensive

where:

w_D + w_O = 1

and neither component uses leverage.

Do not select the weights yet.

Do not assume 50/50.

Do not optimize allocations against H028's 2015–2021 performance.

Investigate possible prospective allocation policies:

- Fixed strategic allocations.
- Independently justified risk-budget allocations.
- Other transparent rules, if appropriate.

Distinguish a fixed allocation from dynamic regime switching.

Do not propose a 2018/2020-inspired crash filter.

The final portfolio must respect aggregate constraints, including:

- Overlapping positions between components.
- Total single-stock weight.
- Sector exposure.
- Total market beta.
- Cash usage.
- Rebalance interactions.
- Net trading costs.
- Portfolio-level drawdown.

It must be simulated as one investable portfolio rather than combining two independently computed equity curves without accounting for trading interactions.

---

# 13. Combined Portfolio Benchmarks

A future combined strategy must be compared with at least:

1. SPY Buy & Hold.
2. Its defensive component alone.
3. Its offensive component alone.
4. A simple pre-specified SPY + defensive ETF portfolio.
5. A sensible exposure-matched benchmark where valid.

Why?

Because combining two models only adds value if the combination improves the investment outcome relative to simpler viable alternatives.

A combination that beats SPY but fails to outperform a simple SPY + defensive ETF mix may not justify its added complexity.

Define how incremental economic value should be evaluated without repeating invalid conditional-null procedures.

---

# 14. The 30-Year Horizon

Our intended real-world investment horizon is approximately 30 years.

This is an investment objective, not a claim that 30 years of valid historical data are currently available.

Prospective primary objective:

**Greater terminal wealth than SPY after costs.**

Supporting metrics:

- CAGR.
- Excess CAGR.
- Relative terminal wealth.
- Rolling 3-, 5-, 10-, 15- and 20-year results where available.
- Maximum drawdown.
- Relative drawdown.
- Time underwater.
- Recovery time.
- Up capture.
- Down capture.
- Return concentration.
- Trading costs.
- Risk and style concentration.

Calendar-year outperformance should be reported but should not universally determine qualification.

Do not choose an arbitrary annual win-rate requirement as a substitute for long-term economic performance.

However, do not allow one extraordinary episode to masquerade as a robust 30-year edge.

Propose a balance between long-horizon wealth and protection against fragile results.

---

# 15. Historical Evidence Limitations

The existing stock-selection development history is heavily used:

2011–2021.

The Holdout is:

2022-01-01 to 2026-08-31.

It remains sealed.

Pre-2010 stock-selection data could potentially provide additional evidence, but historically accurate point-in-time market capitalization, fundamentals and delisted-firm coverage require further feasibility work and potentially a paid dataset.

No purchases are authorized.

Do not treat earlier historical periods as clean confirmation until an audit establishes this.

Do not extrapolate seven years of CAGR into a 30-year backtest.

Do not open the Holdout merely to improve statistical power or select an allocation.

---

# 16. Critical Research-Governance Rule

We are allowed to learn from H028's descriptive results.

We are NOT allowed to pretend we did not see them.

Any new strategy formulated partly in response to H028's historical weaknesses must be labelled as development-motivated.

A truly independent offensive hypothesis must have an economic justification and a design source separate from those observed weaknesses.

Maintain a complete hypothesis and selection ledger.

Do not repeatedly test different offensive models until one complements H028 by chance.

For the new research programme, propose a small fixed hypothesis budget before the first real-data test.

Do not authorize the final Holdout automatically.

A combined-portfolio test is a distinct selection decision and must account for multiple testing across the standalone and combined candidates.

---

# 17. Requested Architecture Comparison

Include a comparison of these potential long-term architectures:

**Architecture A — H028 alone**

Frozen H028, kept only as an unqualified research reference.

**Architecture B — Transparent defensive exposure**

SPY plus a low-volatility or quality ETF.

**Architecture C — Offensive alone**

A future independently qualified stock-selection strategy.

**Architecture D — H028 + Offensive**

A possible future combined portfolio.

**Architecture E — Transparent Defensive + Offensive**

A future stock-selection offensive component combined with an ETF-based defensive component.

For each explain:

- Expected source of returns.
- Expected risk exposures.
- Complexity.
- Data requirements.
- Trading costs.
- Need for independent evidence.
- Principal weaknesses.
- What would make it preferable to SPY.
- What evidence could disqualify it.

Do not rank architectures by fitting their historical returns.

Instead recommend which architecture is most practical to investigate first, and why.

---

# 18. Required Roadmap

Create a staged roadmap that minimizes research waste.

I expect something along these lines:

**Stage A — Design**

Specify the offensive hypothesis, defensive benchmarks and statistical methodology.

**Stage B — Synthetic validation**

Validate the inference machinery without using real stock returns.

**Stage C — PIT data feasibility**

Verify that the fundamental information and timestamps are accurate.

**Stage D — Signal research**

Test the offensive signal across the eligible universe.

**Stage E — Standalone portfolio research**

Only if the signal qualifies, evaluate a frozen offensive portfolio.

**Stage F — Portfolio architecture research**

Assess a pre-registered combination against SPY, the components and simple ETF-based alternatives.

**Stage G — Independent confirmation**

Only after separate owner approval, evaluate a frozen candidate on independent data.

**Stage H — Forward monitoring**

If justified, paper-trade prospectively before making any live investment decision.

For each stage specify:

- Research question.
- Required input.
- Deliverable.
- Objective stop condition.
- Required owner decision before continuing.

No automatic advancement.

---

# 19. Current Approval Scope

This approval is **DESIGN ONLY**.

You may:

- Inspect existing committed documentation and prior results.
- Review relevant economic and statistical research.
- Record this owner instruction.
- Update a forward-looking roadmap.
- Create a design checkpoint.
- Commit and open/merge a documentation-only PR under repository conventions.

You may NOT:

- Start H031.
- Run any backtest.
- Run synthetic experiments.
- Run new null worlds.
- Recalculate H028 from real market data.
- Retrain Ridge.
- Modify H028.
- Train OF-A.
- Implement an offensive strategy.
- Implement a combined portfolio.
- Access the Holdout.
- Purchase datasets.
- Change frozen historical gates or results.
- Reopen Phase 13 or Phase 14.

If source material is missing, report the gap rather than filling it with invented findings.

---

# 20. Deliverable

Create a checkpoint titled:

**H028 Defensive Reference + Offensive Companion — Long-Horizon Architecture Design**

Include:

1. Verified current project status.
2. Owner approval and exact scope.
3. Frozen H028 specification and formal status.
4. Summary of H028's historical economic behavior.
5. Reasons it is not validated.
6. What would establish genuine defensive value.
7. Transparent defensive alternatives.
8. OF-A economic hypothesis.
9. Distinction from prior failed hypotheses.
10. Required OF-A data and PIT constraints.
11. Candidate surprise/acceleration signal definitions, without implementing them.
12. Proposed universe-wide signal evaluation method.
13. Synthetic validation requirements.
14. False-positive calibration and power requirements.
15. Standalone offensive portfolio design principles.
16. Future combined-portfolio mechanics.
17. Portfolio overlap and trading-cost treatment.
18. Five-architecture comparison (A–E).
19. SPY and simple defensive benchmark requirements.
20. Long-horizon 30-year objective and metrics.
21. Evidence limitations and independent-data constraints.
22. Multiple-testing and selection governance.
23. Staged roadmap with STOP gates.
24. One recommended next checkpoint.
25. Exact next owner approval required.

Keep all repository-specific statements linked to their existing decisions, checkpoints or experiment IDs.

**STOP after the design checkpoint is committed and reported.**

Do not advance to synthetic validation or real-data research without another explicit owner approval.

---

# Final Principle

We are not trying to rescue H028's failed hypothesis.

We are trying to preserve a potentially useful historical observation while identifying a genuinely independent return source that might complement defensive investing.

The final measure of success is the complete investable system's long-term after-cost terminal wealth relative to SPY, not the attractiveness of a single historical backtest.

H028 remains REJECTED.

No new candidate exists.

The Holdout remains sealed.
