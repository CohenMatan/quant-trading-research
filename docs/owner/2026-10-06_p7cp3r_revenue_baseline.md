# Owner message 2026-10-06: "P7-CP3R — Revenue-Baseline Correction and Final Mechanics Confirmation. MECHANICS ONLY — NO FUTURE RETURNS"

This is a recorded summary; the full message is in the session transcript. Decision id: **D173**.

## Decision: revenue baseline (P7-CP3 decision 9, Option B approved)

**Principle:** fundamental history belongs to the company, not to the strategy universe.

- The YoY revenue-growth baseline is the company's PIT revenue True TTM available at the corresponding prior-year review.
- It is taken from the full trustworthy PIT fundamental store, whether or not the company was in the strategy's eligible universe then.
- It must still satisfy every existing PIT rule:
  - it existed in the PIT store and was public by that date (filing-availability chronology of P7-CP1);
  - no restatement leaked backwards;
  - stale-data rules apply;
  - it belongs to the same corporate / security life.
- No interpolation and no look-forward: without a valid value at that date, the stock is H2.

**Everything else is unchanged:**
- Score v1 (40 / 45 / 15): features, bands, weights, lookbacks, sector and volatility definitions.
- Every other H2 condition.

## Required before the mechanics rerun

- **PIT safety tests:**
  - A. future-filing invariance;
  - B. truncation;
  - C. eligibility independence;
  - D. same-company continuity (re-used ticker / security lives, unrelated companies, CIK-successor mistakes);
  - E. determinism.
- **Audit of the rescued rows:** counts by year, share of non-financial rows, the reason each was outside the old ledger (below $2B, illiquid, newly listed, other), and an independently verified deterministic sample.

## Rerun

- Same period, 2011-01 → 2017-12.
- Non-trading QuantConnect export (0 orders), then the same offline mechanics.
- **CP3 vs CP3R comparisons:** funnel, availability at 75 / 80 / 85 / 90, distribution, correlations, composition, persistence, churn H1 / H2 / H3, orders, costs, sector concentration, capacity, and the market regime (which should be unchanged).

## Owner's PROVISIONAL mechanics (report only; not optimised, not compared by returns)

| Item | Provisional choice |
|---|---|
| Entry / exit / buffer | 80 / 70 / 5 (H2 Balanced) |
| Maximum positions | 10 |
| Initial position cap | 10% |
| Relaxation ladder | None; cash allowed |
| Regime position limits | STRONG 10, NORMAL 8, WEAK 5, RISK_OFF 2. When holdings exceed the limit, keep the highest current scores and exit the lowest-scoring excess at the next monthly review. Hard-disqualifier exits stay weekly. The regime never alters scores or ordering |
| Grown-winner hard ceiling | 20% of equity; trim back to 20% at the next monthly review. A future risk rule only, not tested |
| Sector cap | At most 3 holdings per FF12 sector (PIT). Skip extra candidates from a full sector and take the next-ranked; otherwise cash. Never lower the threshold |
| Share class | New positions take the highest PIT ADV20 class (deterministic tie-break). A held class is kept while it remains eligible and trustworthy; switch only if the held class becomes ineligible or disqualified |
| Weekly check | Hard disqualifiers of holdings only. A freed slot stays in cash until the next monthly review |
| Tie-break | Total, then Fundamental, then Technical, then PIT ADV20, then stable id. The frozen P7-CP2 planner used total, ADV20, id; the difference is documented before the change |
| Whipsaw | Re-entry within 3 monthly reviews of a sale (unchanged) |
| Costs | $7 per buy and per sell, 10 bps per side; $100K primary, $200K sensitivity; no leverage |

## Stop rules

- If the corrected ledger materially changes the 80+ population, or causes a major structural shift (80+ becoming common, a large churn, concentration or cost increase, an unexpected distribution shift): **STOP and request owner review.** Do not modify the score.
- **Not authorised:** returns of any kind, IC, buckets, a portfolio backtest, CAGR, terminal wealth, Sharpe, drawdown, SPY comparison, 2018–2021, the Holdout, purchases.
- **STOP after P7-CP3R.**

## Implementation readings recorded by Claude before the run (D173)

1. **Store-wide revenue ledger.** At every month-end review session t (from 2010-01), the host records, for EVERY company in the PIT store, the revenue True TTM the store returns on the universe-selection day reflecting t. The store is the frozen `qr_fundamentals` layer: availability = filing date + 1, estimated dates + 90, quarantine, restatement blocks, SEC timing holds, field releases and the 200-day freshness rule. Values are recorded live, so nothing later can alter them.
2. **SEC-repaired securities** are fed into the store from the SEC table on every day a new filing of theirs becomes usable, not only while eligible. This is idempotent: the same filings with the same availability dates, so the values at any date are unchanged.
3. **Baseline for a review at t** = the ledger value at the review session 12 calendar months earlier (same calendar month, prior year). If that value is absent (no four visible consecutive quarters, failed reconciliation, or stale), the stock is H2. No other date is searched.
4. **Same security life:** the security's current price life at t must have started on or before the baseline review session (`qr_p7.LIFE_GAP` rule, D167). Otherwise there is no baseline (H2).
5. **Same registrant:** if the SEC CIK carried by the security's filings (PIT SIC table) is known at both dates and differs, there is no baseline (H2). The store is keyed by QuantConnect security id, never by Morningstar's current-status CIK.
6. **Weekly checks** use the baseline of the score in force (the latest monthly review), validated by the same rules.
7. **Alternate share class:** for companies with more than one eligible class, the non-chosen class is also scored (the same review with that class substituted). This is used only to keep a held class under the owner's no-switch rule. The chosen class's score and the ranking population are unchanged.
8. **Rescued-row audit:** at every month-end, the reason each store company was outside the eligible universe is recorded:
   - not in QuantConnect's universe list that day;
   - below $2B;
   - price < $5;
   - ADV20 < $5M or fewer than 20 days of ADV history;
   - not US common / exchange;
   - plus whether it was first seen less than 365 days earlier.
   All rescued baselines are checked in-host (every quarter usable on or before the baseline date). A deterministic sample is checked against SEC EDGAR filing dates offline.
9. **Provisional mechanics** are implemented in a separate planner `qr_p7_mech.py`; the frozen `qr_p7_score.plan_review` is unchanged. It adds the owner's tie-break, regime limits, sector cap, share-class stickiness and cash-until-monthly after weekly exits. The 20% grown-winner trim needs prices and is recorded as a rule only (not simulated).
