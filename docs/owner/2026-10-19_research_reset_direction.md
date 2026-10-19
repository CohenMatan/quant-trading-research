# Owner decision D259 — Research reset following QuantConnect data and platform changes (2026-10-19)

**Context:**
- This follows D257 / D258 (SYS1-CP2, `docs/checkpoints/SYS1_CP2_object_store_migration_assessment.md`, PR #120).
- The message is recorded verbatim below, before any investigation.

---

Owner Direction — Research Reset Following QuantConnect Data and Platform Changes

I want to temporarily pause all strategy research and reassess our research framework following the September–October 2026 QuantConnect changes.

This is a research and infrastructure planning review only. Do not run backtests, implement new strategies, modify frozen experiments or access the Holdout.

1. Our investment objective remains unchanged

Our primary goal is to discover a robust, investable, long-only US equity strategy capable of outperforming SPY in long-term terminal wealth after realistic trading costs.

We prefer a 20–30-year research horizon where reliable data permits it.

Risk-adjusted performance, drawdowns, robustness and statistical evidence matter, but should support the investment objective rather than replace it.

We must not weaken validation standards, selectively change thresholds or manufacture a successful result.

The purpose of this review is to make our research process feasible, statistically credible and operationally sustainable under the current platform.

2. Audit QuantConnect's changes

Review QuantConnect's official documentation on:

- The September–October 2026 Morningstar fundamental-data migration.
- Differences in historical coverage, universe membership, market capitalization, filing dates and fundamental fields.
- Changes in fundamental availability, especially before 2013.
- Changes to financial values, definitions, reporting signs and discontinued fields.
- Historical security identifiers and symbol mapping.
- Engine version availability and reproducibility.
- Corporate actions, delistings and price-adjustment consistency.
- Updated Terms of Service, storage, uploads and permitted backtest-result exports.

Use the official Morningstar Migration Atlas where applicable.

Clearly distinguish documented platform changes from effects demonstrated by our own research.

Do not assume that all market-price data changed merely because fundamentals changed.

3. Assess the impact on our research

Review our committed research records, previous hypotheses H001–H030, frozen data versions, H028, SYS-1 and the previous platform-blocking incidents.

Classify each major research component as:

- Still valid as historical evidence.
- Not reproducible on the current platform.
- Dependent on discontinued or materially changed data.
- Potentially reusable in a new implementation.
- Unknown — requires future verification.

Do not reinterpret previous rejected strategies as successful.

Do not attempt exact recovery of H028 or reopen the original SYS-1.

Do not use prior results to retroactively optimize new hypotheses.

4. Determine what research is now feasible

Evaluate at least three approaches:

A. Price-and-volume-based strategies that require minimal fundamental data.

B. Fundamental strategies using only reliably available point-in-time fields.

C. Hybrid strategies combining technical, fundamental and market information.

For each approach determine:

- Earliest defensible historical research date.
- Expected coverage of currently listed and delisted securities.
- Whether market cap >= $2B, price >= $5 and ADV20 >= $5M can be enforced point-in-time.
- Data availability and survivorship/look-ahead risks.
- Dependence on current QuantConnect datasets.
- Whether testing over 20–30 years is credible.
- Research and implementation complexity.
- Ability to perform rigorous out-of-sample validation.
- Compliance with the current Terms of Service.

Do not assume that a longer history is automatically better if the historical observations are unreliable.

Do not arbitrarily shorten the sample merely to make a candidate appear successful.

5. Reassess the research methodology

Our historical development periods have already been examined extensively.

Account explicitly for prior research exposure and multiple testing.

Propose a credible future separation between development, validation and untouched holdout data.

Keep the existing 2022-01-01 through 2026-08-31 Holdout sealed. Any proposed change to the validation architecture requires separate owner approval.

Recommend how to reduce infrastructure complexity, unnecessary experiment counts, lengthy canaries and repeated platform-related interruptions.

Keep the approved trading-cost assumptions as the baseline unless a change is separately justified and approved.

6. Recommend an updated research roadmap

Provide two or three realistic research-programme options.

Compare them by:

- Historical depth.
- Data quality.
- Statistical credibility.
- Implementation effort.
- Expected infrastructure stability.
- Budget.
- Ability to test new strategies efficiently.

Recommend the option most likely to let us conduct meaningful research repeatedly without rebuilding our infrastructure for every experiment.

The recommendation should optimize research quality and execution feasibility, not claim any particular strategy will beat SPY.

7. Deliverables and stop conditions

Produce a concise checkpoint titled:

Research Reset — QuantConnect Migration Impact and Updated Long-Term Research Roadmap

Include:

1. Verified QuantConnect change inventory.
2. Data availability and integrity matrix by period.
3. Impact on completed research.
4. Feasible future research approaches.
5. Proposed research and validation architecture.
6. Infrastructure simplification recommendations.
7. Recommended roadmap with effort and cost estimates.
8. Remaining unknowns and the minimum future tests needed to resolve them.

Use only official platform documentation, existing repository evidence and permitted read-only metadata.

Do not export or download QuantConnect Platform Data.

No new QuantConnect runs, new research hypotheses, strategy optimizations, data purchases, subscriptions or Holdout access.

Record this owner direction, commit the documentation through the normal workflow and STOP for my review.

Do not implement or activate the new research programme without my explicit approval.
