# H017 (WITHDRAWN DRAFT): Value (book-to-market). Never approved (owner D120); superseded by H017 = earnings-event continuation (P2-CP13). Kept for the record only.

- **Status:** PROPOSAL ONLY (P2-CP10, 2026-10-02).
  - Not approved, not implemented, never run.
  - Phase 2 slot 3 is not consumed.
  - The recommendation in P2-CP10 is to **preserve** the slot rather than spend it on this hypothesis (§7 there). This file records the exact hypothesis in case the owner chooses to spend it.
- **Chosen before any return was computed.** No 2010–2021 or later performance of any value measure was calculated or compared. The choice rests on literature, economic rationale, point-in-time data reliability and implementation feasibility (`research/phase2/P2_final_slot_literature_review.md`).

## Hypothesis

Among the large US non-financial stocks of our universe, the 20 with the highest **book-to-market ratio**, re-selected quarterly from point-in-time data and held equally weighted, earn a **higher net return than S&P 500 buy-and-hold** (SPY), and a higher risk-adjusted return than the equal-weight portfolio of the same universe, after realistic costs.

## Rationale

- **Behavioural:** investors extrapolate past growth and over-price glamour firms. Cheap firms are under-priced relative to their mean-reverting fundamentals (Lakonishok, Shleifer & Vishny 1994).
- **Risk-based:** cheap firms carry distress risk that is compensated (Fama & French 1993, 1995).
- **Distinctness:**
  - independent of every family tested (all technical families; H016's profitability, which is negatively correlated with value);
  - one measure, chosen for its canonical status, not its performance.

## Measure (one, fixed)

**B/M(T) = stockholders' equity / market capitalisation**, evaluated on decision date T.

- **Stockholders' equity:** the latest point-in-time balance-sheet snapshot visible on T (frozen fundamentals layer v1: filing-date availability, +90 days for estimated dates, quarantine, restatement guard, SEC correction layer v3.2, freshness 200 days). It is an approved field, matching SEC filings within 0.5% in 96.4% of reports (X971).
- **Market cap:** the point-in-time market cap on T (approved; the "timely" form of Asness & Frazzini 2013).
- **Book equity ≤ 0:** the measure is undefined and the stock is not ranked (standard practice).
- **Preferred stock:** not subtracted, because the item is not in the approved set. This is immaterial for non-financials and is disclosed.

**Why B/M and not earnings, sales or cash-flow yields, EV/EBIT, or a composite:**
- it is the canonical academic value measure, with the longest independent record;
- it is a balance-sheet stock, so it is stable, and not a profitability ratio in disguise (E/P and CF/P are partly profitability, a family H016 has just covered);
- both inputs are approved and SEC-verified;
- a composite would multiply choices.

**No alternative value measure will be run.**

## Portfolio (identical mechanics to the frozen, canary-verified H016 implementation; only the ranking differs)

| Item | Rule |
|---|---|
| Universe on T | Harness-eligible (US common, NYSE/Nasdaq/AMEX, point-in-time market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, SEC correction layer) ∩ not financial/REIT (SEC SIC at filing) ∩ B/M computable |
| Selection | Top 20 by B/M, highest first; ties by security id |
| Rebalance | Close of the first session of March, June, September and December; executed at the next open. First decision 2010-03-01 |
| Sizing | Equal slot weight; D051 settled cash, 2% buffer, 15% gap reserve; $4,000 minimum new position; one-time top-up (≥ $250); no other resizing |
| Exits | Only at rebalances, for names that left the selection; normal forced exits (delistings, data loss) |
| Costs | $7 per order; 10 bps slippage per side |
| Accounts | $100K primary; $200K sensitivity only |
| Window | 2010-03-01 → 2021-12-31; warm-up from 2008-07-01; the Holdout is untouched |

## Known risks (disclosed in advance)

- **Large-cap weakness:** the premium is weakest in large caps (Loughran 1997; Israel & Moskowitz 2013).
- **Decay:** the effect weakens after publication (McLean & Pontiff 2016).
- **Value traps:** a concentrated top-B/M book holds many deteriorating firms (Piotroski 2000).
- **Sector concentration:** expected tilts towards energy, materials, utilities, industrials and autos. Reported, not constrained.
- **Intangibles bias:** book equity omits internally created intangibles (Lev & Sougiannis 1996).
- **Data errors cluster at the top of the ranking:** a too-high equity or too-low market cap pushes a stock to the top. Hence the pre-run top-of-ranking audit (P2-CP10 §8).
- **Contamination:** it is public knowledge that US large-cap value did poorly over most of 2010–2020. This was disclosed and not used to choose.
