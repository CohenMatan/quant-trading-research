# Owner message 2026-10-06: "Phase 7 — P7-CP4: Freeze Score/Mechanics and Design the Predictive Test — DESIGN ONLY, NO REAL RETURNS"

This is a recorded summary; the full message is in the session transcript. Decision id: **D175**.

## Decisions

1. **P7-CP3R approved:** "MECHANICS CONFIRMED — READY TO FREEZE FOR PREDICTIVE TEST DESIGN". No further correction or tuning.
2. **Revenue baseline frozen** exactly as implemented in P7-CP3R:
   - The baseline for a review in month M, year Y is the company's revenue True TTM recorded live at the month-end review of month M, year Y − 1, from the frozen PIT store as it existed then.
   - Prior eligibility is not required.
   - No recomputation, no nearby-date search, no interpolation, no later filing.
   - No valid recorded value means H2.
   - All other baseline protections are kept.
3. **CIK: Option A.**
   - Reject the baseline only when a registrant change is known (CIK known at both dates and different).
   - An unknown CIK alone never rejects.
   - The security-life rule still applies.
   - The stricter "known and identical at both dates" option is not adopted.
4. **Score v1 frozen exactly as pinned** (40 / 45 / 15; features, weights, bands, lookbacks, sector and volatility definitions, H2–H7 except the approved baseline correction). No score optimisation.
5. **Primary portfolio mechanics frozen** (`qr_p7_mech`):
   - entry 80, exit 70, buffer 5;
   - K = 10, 10% initial weight;
   - no relaxation ladder;
   - no search over entry thresholds or K.
6. **Regime limits frozen:** STRONG 10, NORMAL 8, WEAK 5, RISK_OFF 2. The lowest-ranked holdings exit first at the monthly review.
7. **Sector cap frozen:** at most 3 holdings per PIT FF12 sector. Skip the candidate and evaluate the next. No 2 / 3 / 4 tests.
8. **Ranking / tie-break frozen:** total, then Fundamental subtotal, then Technical subtotal, then ADV20, then security id. No reversion and no return comparison.
9. **Share classes:**
   - one company, one held exposure;
   - no second class of a held company;
   - a held class is evaluated on its own score;
   - no switching for liquidity.
10. **Weekly hard-disqualifier checks:** sell only, then cash until the next monthly review. Entries only at monthly reviews.
11. **Grown-winner 20% cap:** a pre-registered future risk rule. Define its exact implementation and where it applies. No historical impact, no tuning, no comparison.
12. **Costs:** $7 per buy, $7 per sell, 0.10% slippage per side; $100K primary, $200K sensitivity. Mechanical estimates 0.80% / 0.64% a year.

## Instructions for P7-CP4 (design only)

- Design a **signal-level predictive test of the frozen Score v1** before any portfolio:
  - Does a higher score rank higher subsequent total shareholder return among eligible stocks?
  - Do not refit, reweight, mine components or create Score v2.
  - The 80 threshold is not a search parameter.
- **Freeze before any real return:**
  - one primary horizon (diagnostic horizons pre-registered);
  - the overlap and inference method;
  - the response definition and benchmark;
  - the PIT timing (no same-close look-ahead);
  - total-shareholder-return accounting with a deterministic delisting rule (nothing silently dropped);
  - one primary statistic;
  - one economic statistic (relevant to ≈ 0.8% / yr costs);
  - a monotonicity check;
  - a stability gate;
  - non-gating regime diagnostics;
  - a sector diagnostic;
  - at most one secondary incremental-information test.
- **Null:**
  - a primary null that preserves the dependence structure but breaks the link between a stock's own score and its own future return;
  - the full procedure (every gate) run inside every null world;
  - a conservative family-level threshold;
  - the number of null worlds stated.
- **Synthetic power study:** preserve universe size, score distribution and persistence, sectors and common factors; report the false-positive rate, the 50% / 80% detectable effects and their economic translation.
- **Recommendation:** GO / NO-GO for the one real predictive evaluation.
- **Frozen artefacts:**
  - spec;
  - response module;
  - null module;
  - power module;
  - gate evaluator;
  - integrity tests (canaries A–G);
  - result template;
  - hashes and seeds.
- **Not authorised:**
  - any real future return, real IC, real 80+ or score-band return;
  - any portfolio run, CAGR, Sharpe, drawdown, terminal wealth, SPY comparison, win rate or alpha;
  - any tuning;
  - 2018-01-01 → 2021-12-31;
  - the Holdout (2022-01-01 → 2026-08-31);
  - purchases.
- **STOP** after committing P7-CP4.
