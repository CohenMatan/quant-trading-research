# Owner decision D276 — Revisit OS-1 before freezing H032 (2026-10-21)

**Context:**
- This follows OS-CP1 (D275, `docs/checkpoints/OS_CP1_offensive_score_candidate_selection_first_experiment_design.md`, PR #128).
- The message is recorded verbatim below, before any work.

---

Owner Direction — Revisit OS-1 Before Freezing H032
I have reviewed the OS-1 design and want to improve the stock-selection quality before approving H032.
I believe ranking stocks solely by their reduction in shares outstanding is too narrow for our offensive investment objective.
I want to evaluate adding two complementary fundamental filters:

1. Free Cash Flow: Prefer companies generating positive trailing-12-month free cash flow, defined consistently as operating cash flow minus capital expenditures.
2. Revenue Growth: Prefer companies with positive trailing-12-month revenue growth versus the preceding 12 months.

The existing 12-month net share-count reduction remains the primary ranking signal.
The proposed structure is:
Eligible universe → Financial quality filters → Rank by net share-count reduction → Top 15.
These are preliminary design choices, not yet frozen thresholds.
What I want you to evaluate

1. Are these two filters economically justified for identifying higher-quality offensive stock candidates?
2. Can both be computed reliably with point-in-time data already available in our project, particularly the cached public SEC filings?
3. What is their historical coverage by year and company type, including delisted companies and securities restored by the SEC universe repair?
4. Are these metrics comparable across industries, especially banks, insurers and other financial firms?
5. Would the filters introduce additional survivorship bias, sector concentration or an unacceptable loss of eligible companies?
6. Would another pair of financially motivated filters be more appropriate for our goal? If so, propose one alternative and explain why.
7. Can this be implemented with minimal additional infrastructure and no purchases?
8. How should we distinguish the incremental economic contribution of the filters from the net-share-reduction signal without conducting parameter searches or treating previously exposed data as independent confirmation?

Do not optimize filter thresholds against historical stock returns.
Prefer a single, transparent, pre-registered specification rather than learned weights or a search across multiple combinations.
Preserve the existing account constraints, realistic costs, PIT requirements and exploratory-only status of the repaired universe.
Scope
This is DESIGN ONLY.
Do not register or freeze H032 yet.
Do not upload a new SEC object, build a new data layer, run backtests, calculate new strategy returns, or access the Holdout.
Review the feasibility and recommend one final scoring/filtering architecture with the minimum data requirements and a clear coverage gate.
Update the OS-1 design checkpoint and STOP for my review.
Our goal is to identify strong businesses with credible potential to outperform SPY, not simply companies that repurchased the most shares.
