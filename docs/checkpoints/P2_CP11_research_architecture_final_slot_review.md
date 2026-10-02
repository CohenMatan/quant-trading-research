# P2-CP11 — Phase 2 research architecture and final-slot opportunity review (STOP)

- **Date:** 2026-10-02.
- **Status: RESEARCH / DESIGN ONLY.**
  - No strategy, factor or candidate backtest was run.
  - No candidate-measure returns were computed.
  - No parameter or holding period was optimised.
  - The Holdout was not accessed.
  - Phase 2 slot 3 is **unused**.
  - **STOP:** awaiting the owner.
- **Supporting files (`research/phase2/architecture/`):**
  - `P2_arch_power.py/.json`: rolling-horizon "luck" profiles and gate operating characteristics.
    - **Inputs:** only completed control books (SPY, same-universe equal weight, five random 20-stock books).
    - **Method:** joint block bootstrap, 2,000 draws per cell.
  - `sec_8k_earnings_probe.py/.json`: metadata-only probe of SEC 8-K earnings-release filings (no prices, no returns).
  - `P2_arch_literature_review.md`: event-driven, relative-strength, catalyst and fundamental families; evidence labelled by period.
- **Previous review:** `research/phase2/P2_final_slot_literature_review.md` (value, issuance, asset growth, accruals).

## Summary

1. **Objective:** finish with more money than an investor who put the same capital into S&P 500 buy-and-hold (total return) on the same date, after realistic costs, without leverage.
2. **The current methodology mixes two jobs in one Sharpe hurdle.** The +0.25 Sharpe margin over equal weight is used both as evidence of a real edge and as the definition of success.
   - It lets **essentially no** no-edge strategy through: about 0.1% of the time.
   - But it also blocks almost every **real** one: a true edge of 3% a year over SPY passes only about 5% of the time.
3. **Proposed framework:**
   - one **objective** test: terminal wealth above SPY's;
   - one **evidence** test, scaled to the strategy's own tracking error: excess CAGR ≥ 1.645 standard errors;
   - **attribution** tests: it must beat its universe and the random books;
   - simple **risk safeguards**: drawdown no worse than SPY's by more than 10 points, Sharpe at least SPY's, no single lucky period.

   With 12 years of data, its false-pass rate is about **2.5%**, and it passes a true 3% a year edge about 5 times more often than today's rules. The rolling-horizon analysis is reported, never required.
4. **Statistical power is still the binding limit.**
   - With 12 years and 20 stocks, an even chance of passing needs a true edge of about **4.8% a year** over SPY.
   - With about 22 years and 40 stocks, about **2.8%**, and an 80% chance needs about 4.2%.
   - **More history and more positions are worth more than any new idea.**
5. **Extending history to 2000 is not feasible with the data we have.**
   - QuantConnect's Morningstar has **no market cap before October 2009**, and **no fundamentals at all for companies that died before 2009** (Lehman, Enron, WorldCom, Bear Stearns…). The ≥ $2B universe cannot be rebuilt faithfully.
   - Prices, delistings, corporate actions and **SEC earnings-release timestamps** (from 2003–04) do exist.
   - A faithful extension needs **new data** (point-in-time share counts or market caps, including dead companies).
6. **Families:**
   - **Earnings-event continuation** (earnings release → strong price/volume reaction → hold 1–3 months):
     - distinct from everything tested;
     - the event dates are free and point-in-time from SEC 8-K filings;
     - but the large-cap drift is documented to have **largely disappeared after about 2005**, and costs are material.
   - **Value:** data-ready and cheap, but weak in large caps, with a known 2010s headwind.
   - **Relative-strength swing:** a re-combination of five rejected families; **not** genuinely different.
   - **Net issuance:** credible, but the data is not ready.
7. **Recommendation:**
   - **Preserve slot 3.**
   - Adopt the terminal-wealth framework (Amendment 3) now, before any hypothesis.
   - Authorise two zero-risk preparatory studies:
     - (a) a priced, licensed **data-extension option** (point-in-time market caps / share counts with dead companies, about 2000–2021) for your decision;
     - (b) a non-return **earnings-event data audit** (SEC 8-K mapping to our universe, timing, coverage).
   - Then choose **one** pre-registered hypothesis (earnings-event continuation or value) for slot 3.

## 1. Current state

| Item | State |
|---|---|
| H014 | Rejected (D101) |
| H016 | **Rejected** (D118), preserved exactly as tested |
| Phase 2 hypothesis slots | **2 of 3 consumed; slot 3 unused** |
| H017 (Value) | Proposed in P2-CP10, **not approved**, not implemented, never run |
| Holdout 2022-01-01 → 2026-08-31 | **Locked**, never accessed |
| Data infrastructure | v1 frozen (unchanged) |
| Runs in this step | None on QuantConnect. One SEC metadata probe (free public data, cached) |

## 2. The investment objective (exact restatement)

> **Starting with the same capital on the same date, find an investable long-only strategy whose terminal wealth exceeds S&P 500 buy-and-hold after realistic costs.**

- **Benchmark:** S&P 500 total return, using SPY with dividends reinvested (the E900 benchmark series). SPY's expense ratio is included, which slightly favours neither side.
- **Comparison terms:** same initial capital ($100,000 primary), same start date, same end date, no external cash flows, no leverage. The strategy pays $7 per order plus slippage.
- **Equivalence:** over the same window, higher terminal wealth means higher CAGR, and vice versa.
- **Not the objective:**
  - beating SPY every year or in every regime;
  - minimum drawdown or maximum Sharpe;
  - a defensive portfolio;
  - merely beating same-universe equal weight.
- **Horizon:** not fixed. Holding periods follow the economic source of the edge (days to years). The investor may judge over 1, 3, 5, 10 years or the whole history; the rolling analysis in §4 serves that view.

## 3. Proposed evaluation framework: terminal wealth first (Amendment 3, for approval)

### 3.1 Primary economic table (always first in every report)

| Line | Content |
|---|---|
| Initial capital | $100,000 (and $200,000 sensitivity) |
| Final value | strategy, SPY (total return), same-universe equal weight, median random book |
| Total return | strategy vs SPY |
| CAGR | strategy vs SPY |
| **Excess CAGR** | strategy − SPY, with its standard error = TE / √years |
| Terminal-wealth ratio | final strategy ÷ final SPY |

### 3.2 Development gates (all must pass; frozen before any hypothesis is pre-registered)

| Gate | Rule | Purpose |
|---|---|---|
| **W1, objective** | CAGR(H) > CAGR(SPY): terminal wealth above SPY's, net, $100K, whole development window | The goal itself |
| **W2, evidence** | Excess CAGR ≥ **1.645** × TE(H vs SPY) / √years, using the strategy's own annualised tracking error. One-sided 5% | False-positive protection that adapts to how far the strategy strays from SPY |
| **W3, attribution** | CAGR(H) > CAGR(same-universe EW) **and** CAGR(H) > median CAGR of the 5 random books (same universe and mechanics) | The edge must come from **selection**, not from the universe or luck |
| **R1, drawdown** | MaxDD(H) no more than **10 points** deeper than SPY's | No catastrophic extra risk |
| **R2, risk-adjusted** | Sharpe(H) ≥ Sharpe(SPY) | Extra wealth must not be just extra risk. Passes the owner's example (13% vs 10.5% CAGR, Sharpe 0.93 vs 0.80) |
| **R3, no single lucky period** | Total excess over SPY > 0 and no two-year block contributes more than half of it | Guards against one-episode luck |
| **R4, costs and concentration** | Realised costs ≤ 1.5% a year; maximum position 10%; the structural limits of the account | Implementability |
| **G4′, robustness** (conditional, as before) | ≥ 5 of 6 pre-declared perturbations keep W1; at 2× slippage W1 still holds | Not a knife-edge |

### 3.3 Holdout and forward test (frozen now, applied only to a qualified candidate)

- **HO-W:** CAGR(H) > CAGR(SPY) over 2022-01-01 → 2026-08-31.
- **HO-R:** R1 over the Holdout.
- The 2022 / 2023–26 split is **reported**. The old HO3 "both sub-periods" rule is kept only for strategies with a market-timing or defensive component, where the known 2022 bear market could flatter them.
- The **forward test** inherits HO-W and HO-R.

## 4. Rolling 1/3/5/10-year evaluation (reported, never a hard gate)

For every start date, and each horizon of 1, 3, 5 and 10 years:
- the share of start dates on which the strategy ended with more wealth than SPY;
- the median and mean excess CAGR;
- the 10th and 90th percentiles;
- the worst and best windows.

**These are compared with the same statistics for the 5 random books and the equal-weight universe (the "luck band").**

**What luck alone looks like** (actual completed controls, 2010-03 → 2021-12; share of windows beating SPY):

| Book | 1 year | 3 years | 5 years | 10 years |
|---|---|---|---|---|
| Same-universe EW | 47% | 36% | 28% | 13% |
| Random seed 1 | 48% | 30% | 26% | 56% |
| Random seed 2 | 28% | 25% | 10% | 0% |
| Random seed 3 | 39% | 27% | 21% | 0% |
| Random seed 4 | 45% | 53% | 55% | 12% |
| Random seed 5 | 70% | 64% | 63% | 100% |

**Reading:**
- Pure luck spans **0% to 100%** of 10-year windows.
- With 12 years of data the 10-year windows overlap almost entirely (≈ 2 independent observations), so **10-year win rates from a 12-year sample are not evidence**.
- They become informative only with ≥ 20 years.
- Win rates must always be read against the luck band, never alone.

## 5. Risk safeguards: summary of intent

The economic goal is wealth. Risk enters only as **bounds** (R1–R4), plus full reporting of:
- volatility, Sharpe, max drawdown, Calmar;
- worst calendar year vs SPY;
- longest time under the previous peak (recovery);
- turnover and costs;
- largest position and sector weights.

**The two owner examples:**
- 13% vs 10.5% CAGR with Sharpe 0.93 vs 0.80 passes R1/R2 (and W2 if the tracking error is moderate; see §7).
- +0.5% CAGR with a catastrophic drawdown fails R1, and almost certainly W2.

## 6. Assessment of the existing "+0.25 Sharpe over same-universe EW" gate

| Question | Answer |
|---|---|
| Is it aligned with the objective? | **No.** It measures risk-adjusted superiority over equal weight, not wealth relative to SPY. A strategy can satisfy it while trailing SPY (low volatility), or fail it while compounding materially more than SPY (the owner's example: +0.13 Sharpe) |
| Is it good false-positive protection? | **Too good to be useful.** It lets a no-edge strategy through ≈ 0.05–0.1% of the time, but a true +3% a year edge passes only ≈ 4–5% of the time (12 years, 20 or 40 positions). It rejects real edges almost as reliably as false ones |
| Recommendation | **Retire it as a hard gate**, and report Sharpe(H) − Sharpe(EW) as a diagnostic. Replace its two jobs explicitly: evidence by W2 (calibrated, adaptive) and selection attribution by W3 |
| Is that a weakening? | Development false-pass rises from ≈ 0.1% to ≈ 2.5% per hypothesis (z = 1.645). Through the pipeline (development → Holdout W1, which luck passes ≈ 40% of the time → forward test), the false-acceptance probability per hypothesis is ≈ 1% or less, **well below** the ≤ 5.7–14.7% pipeline bound you approved in D093. The protection is redistributed to where it is informative, not removed |
| Would it re-qualify past failures? | **No.** Under W1–R3: H014 A (CAGR 12.1% vs SPY 14.6%) fails W1; H016 (12.8% vs 14.9%) fails W1; H014 B (+0.24 point) fails W2 and R2 (Sharpe 0.72 vs 0.91). The framework is not reverse-engineered to rescue anything |

## 7. Statistical power under the revised framework

These are pass probabilities. The **0% row is the false-pass rate**. "Edge" = true excess return over SPY a year. G4′ is not modelled, so these are upper bounds.

| History | Positions | Current (G1–G3 + G1.5) false / at 3% | W1 alone (wealth > SPY) false | **Proposed (z = 1.645): false / at 2% / at 3% / at 4%** | Edge for 50% / 80% chance (proposed) |
|---|---|---|---|---|---|
| 12 years (2010–21) | 20 | 0.05% / 4.8% | **39%** | **2.6% / 12% / 23% / 38%** | 4.8% / > 5% |
| 12 years | 40 | 0.0% / 4.3% | 41% | 2.6% / 18% / 34% / 53% | 3.8% / > 5% |
| ~22 years (2000–21) | 20 | 0.0% / 1.7% | 38% | 2.2% / 19% / 36% / 58% | 3.7% / > 5% |
| ~22 years | 40 | 0.0% / 1.5% | 39% | 2.6% / 30% / 55% / 78% | **2.8% / 4.2%** |

**What this says:**
1. **"Beat SPY" alone is not evidence.** A no-edge 20-stock book ends above SPY about 39% of the time. That is why W2 is needed.
2. **The proposed framework is about 5× more powerful** than today's rules at a 3% edge with 12 years of data, and far more with longer history, while keeping development false passes at about 2–3%.
3. **Power comes from history and breadth, not from the gates.**
   - Going from 12 years and 20 positions to 22 years and 40 positions roughly **halves** the edge needed for an even chance (4.8% → 2.8%).
   - The 22-year rows resample 2010–2021 noise. 2000–2009 was probably noisier, so they are optimistic.
4. **Realistic targets.** Published large-cap long-only edges, after decay, are about 0–3% a year. Even with the new framework and 12 years of data, a **real 2% edge would pass only about 12% of the time**.
5. **Selection noise is the larger part of the tracking error.**
   - Tracking error of a 20-stock book vs SPY ≈ 9.2% a year: selection noise 7.6% and the universe's own 5.2%, combined in quadrature.
   - Going to 40 positions cuts the selection part by √2.
   - A universe closer to the S&P 500 (e.g. the largest 500 by point-in-time market cap) would cut the universe part.

**Account-model constraint (identified, not changed):**
- The $4,000 minimum new position (H016 rule) caps a $100K book at about 20–24 positions.
- 40 positions need either about $160K+ at the same minimum, or a lower minimum.
- A lower minimum is only sensible for **low-turnover** strategies. At $2,500 a round trip costs $14, i.e. 0.56%, plus 0.20% slippage.
- This is an account-model decision for you; it is not assumed.

## 8. Feasibility of extending development history toward 2000

**Measured facts** (CP2 audits E951-01/-03; tracked-company tables; the new SEC probe):

| Data | 2000–2009 availability | Point-in-time / survivorship | Verdict |
|---|---|---|---|
| Daily prices (AlgoSeek on QuantConnect) | From 1998, including delisted securities (Lehman, Enron, WorldCom seen trading until their end) | Yes | **Usable** |
| Corporate actions (Security Master: splits, dividends, mergers, delistings) | From 1998 | Yes; audited for 2010+ only | **Usable after a pre-2010 audit** |
| Benchmark (SPY total return) | From 1998 | Yes | **Usable** |
| Market cap, new dataset (the official one) | **Absent before Oct 2009** (4–27 names ≥ $2B a year vs about 700 from 2010) | — | **Not usable** |
| Market cap, old dataset | About 350–600 names ≥ $2B a year | **Dead companies have no fundamentals** (WorldCom, Enron, Lehman, Bear Stearns: none). The dataset is also **retired by QuantConnect on 2026-10-31** | **Not usable** (survivorship-biased; disappearing) |
| Morningstar fundamentals (statements) | Objects exist for about 2,500–3,600 securities a year | **Missing for companies that failed before 2009** | **Not usable for research** (survivorship) |
| SEC structured financials (XBRL) | Only from 2009–2011 (phase-in) | — | **Not available** pre-2009; pre-2009 statements exist only as unstructured text filings |
| SEC share counts (for market-cap reconstruction) | Pre-2009 only as text on 10-K/10-Q cover pages; no structured data; no historical ticker ↔ CIK map for dead firms | Point-in-time in principle | **Possible but a large, error-prone project** |
| Earnings-release timestamps (SEC 8-K Item 12/2.02, acceptance time) | **From 2003-03 / 2004-08**; 37–39 of 40 large survivors each year at about 4.3 a year; failed firms included until their end | **Yes**, survivorship-safe | **Usable from about 2004** |
| Consensus estimates | EODHD on QuantConnect from 1998 (paid; point-in-time status of the estimate unverified); Estimize 2011+ (paid); I/B/E/S institutional only | Unverified | **Requires purchase + audit** |
| Point-in-time index membership (S&P 500) | QuantConnect ETF constituents only from June 2009 | — | **Not available** pre-2009 |

**By family:**

| Family | Can it go back to about 2000 safely? |
|---|---|
| Any family that needs the **≥ $2B point-in-time universe** (all of them) | **Not with current data.** The universe itself cannot be rebuilt. It needs point-in-time market caps or share counts **including dead companies**: purchased data, or a large EDGAR text-extraction project |
| Earnings-event continuation | Events: from **about 2004** (SEC 8-K). Prices: yes. Universe: **no** (as above). So at most about 2004–2021, and only after universe data is acquired |
| Value / fundamentals | **No.** Fundamentals are survivorship-biased before 2009 in both QuantConnect datasets; SEC XBRL starts in 2009 |
| Price-only families (relative strength) | Prices yes; universe no (D033 rejected the liquidity-proxy universe) |

**Realistic extension routes (each needs your approval; nothing bought):**
- **(i) A licensed point-in-time US equity dataset with delisted companies and historical shares / market caps**, ideally usable inside QuantConnect.
  - Example: a fundamentals-and-prices bundle available through QuantConnect's Nasdaq Data Link connector, or an equivalent vendor.
  - Price, licence terms and engine integration must be quoted and verified before any decision.
  - QuantConnect's own **EODHD earnings calendar** (from 1998) would add announcement dates and estimates for 1998–2003, but not the universe.
- **(ii) Free:** reconstruct share counts from EDGAR cover pages (about 2000–2009), plus an identity map for dead registrants. Weeks of work with real error risk; it would need its own audit and freeze.

The CP2 decision (D033) explicitly preferred "a shorter, faithful period" to a longer approximate one. **Neither route should be taken without your decision**, and either must be audited to the same standard as data v1 before use.

## 9. Comparison of genuinely distinct families

| Family | Distinct from H001–H016? | Source of edge | Evidence in large US caps after publication | Point-in-time data today (2010–2021) | Holding period | Turnover / cost ($100K) | Credible path to beat SPY wealth |
|---|---|---|---|---|---|---|---|
| **A/C. Earnings-event continuation** (release → strong reaction → continuation) | **Yes** (H009/H010 were price-only; event conditioning is the point, per Chan 2003; Savor 2012) | Under-reaction to verified news | **Weak:** large-cap drift largely gone since about 2005 (Chordia et al. 2009; Martineau 2022) | **Yes:** 8-K timestamps (free) + prices; audit needed | 1–3 months (≈ 60 sessions in the literature) | ≈ 3–4× a year; ≈ 1.5–2.5% a year at 20 positions (~80 round trips) | Low–moderate; per-trade edge must exceed ≈ 0.5% just to cover costs |
| A2. Earnings-announcement premium | Yes | Compensation for event risk | Modest, international (Barber et al. 2013) | Yes (dates) | ≈ 1 month around each event | High (every stock every quarter) | Low |
| B. Relative-strength swing (vs SPY + sector + consolidation) | **No** (re-combination of H002/H003/H004/H008/H014) | Momentum / continuation | Weakened; crash-prone (Daniel & Moskowitz 2016) | Yes | Weeks–months | Moderate–high | Low; repackaging |
| D1. Value (B/M) | Yes | Mis-extrapolation / distress premium | Weak in large caps; lower 1991–2019 premium (Fama & French 2021); 2010s headwind public | **Yes, ready** | 6–24 months | ≈ 0.5–1× a year; ≈ 0.1–0.3% a year | Low (P2-CP10: ≈ 1–4% chance under the old gates) |
| D2. Net issuance / payout | Yes | Managers time issuance; repurchases signal under-pricing | Robust in all sizes, mainly the short leg | **No** (needs an audit) | ≈ 12 months | Very low | Low–moderate; not testable yet |
| D3. Asset growth | Partly (overlaps value) | Over-investment | Weak in big stocks | Yes | ≈ 12 months | Low | Very low |
| D4. Accruals / F-score | Overlaps profitability | Earnings quality | Decayed; F-score needs unapproved fields | Partly | ≈ 12 months | Low | Very low |

## 10. Detailed assessment: event-driven / earnings swing

- **Source of edge:**
  - investors under-react to earnings news, especially when attention is scarce;
  - news-driven moves continue, while no-news moves reverse.
- **Why it might persist:**
  - limited attention;
  - institutional constraints on chasing post-event moves;
  - event risk that keeps capital away.

  **Why it might not:** algorithmic news processing. The documented large-cap decay since about 2005 is exactly this.
- **What creates the opportunity:** a scheduled earnings release (SEC 8-K Item 2.02, acceptance timestamp), followed by a large abnormal price reaction (and volume) over the event window.
- **Expected gross edge per trade (large caps):**
  - historically about 1–3% over about 60 days for the strongest-reaction decile (long side, pre-2005 samples);
  - plausibly about 0–1% after 2005 (Martineau 2022).

  **[ours: a range, not an estimate from our data]**
- **Duration:** the literature's drift horizon is about 60 trading days, up to the next announcement. **Not optimised:** if pre-registered, the horizon is fixed from the literature before any run.
- **Frequency:**
  - ≈ 4 events per stock a year, about 4,000 a year in a 1,000-stock universe;
  - a strong-reaction filter (e.g. top decile) leaves about 400 a year.

  With 20 slots and about 60-day holds, the book can take about 80 a year, so the selection among qualifying events must be pre-declared.
- **Turnover and cost:**
  - about 80 round trips a year at about $5,000 each, i.e. $14 commission + 0.20% slippage ≈ 0.48% per round trip;
  - that is **≈ 1.9% a year** of a $100K account;
  - at $200K, about 1%.

  The gross edge per trade must exceed about 0.5% just to break even. That is high relative to the post-2005 large-cap evidence.
- **Data feasibility:**
  - **event dates:** free and point-in-time from SEC (verified coverage); this needs a non-return audit mapping 8-Ks to our universe (2010–2021): coverage, before-open vs after-close timing, multiple filings per quarter, amended filings, and companies that release earnings without an 8-K;
  - **surprise:** the price reaction (QuantConnect prices); no estimates are needed;
  - **SUE from Morningstar:** **not** point-in-time safe (the 10-Q file date lags the release).
- **Statistical aspects:**
  - the portfolio-level tests (§3) apply unchanged;
  - an event-level diagnostic is also available: the average post-event excess return over thousands of events. That gives **much more evidence about the mechanism** than a 12-year portfolio curve, but it is not the objective.
- **Overall:** the most genuinely new and best-motivated family we have not tested, with free point-in-time data. Its main weakness is published evidence that the large-cap effect decayed exactly in our period, plus material costs. **A credible but low-probability path.**

## 11. Detailed assessment: relative-strength swing

- **Proposed shape:** strength vs SPY + strength vs sector + a pause/consolidation + re-entry.
- **What we already tested:**
  - momentum (H002), 52-week high (H003), pullback in leaders (H004), breakout (H006), squeeze (H007);
  - residual (market-relative) strength (H008);
  - trend + pullback + recovery (H014).

  Every element except sector-relative strength has been tested and rejected.
- **Independent evidence:**
  - for industry/sector momentum: Moskowitz & Grinblatt 1999;
  - for the consolidation/re-entry filter: **none rigorous** (practitioner lore).
- **Conclusion:** this would be a combination of rejected components with one new feature. It fails your item 7/8 test of genuine difference. **Not recommended** for the final slot.

## 12. Detailed assessment: medium-term fundamental strategies

- **Value (B/M):**
  - **for:** the most implementable (data verified, very low cost, holds for months to years);
  - **against:** weak large-cap evidence, publication decay, value traps, sector concentration and intangibles bias.

  Its well-known 2010–2020 weakness makes a development failure likely, and largely uninformative.
- **Net issuance / payout:** independent and robust in big stocks, but our share data is unsafe as levels. A market-cap-based construction would need an audit first.
- **Asset growth and accruals:** weak in large caps or decayed. Not recommended.
- **Combinations:** none has evidence strong enough that "the combination is the hypothesis"; profitability re-use is excluded.

## 13. Data requirements

| Family | Required data | Status |
|---|---|---|
| Earnings-event continuation | 8-K Item 2.02 timestamps; daily prices and volume; point-in-time ≥ $2B universe | Timestamps: free, verified coverage (audit pending). Prices/universe: ready for 2010–2021 |
| Value | Point-in-time equity, market cap | Ready (data v1) |
| Net issuance | Point-in-time share-count change (or market-cap growth minus price return) | Audit needed |
| Earnings with analyst surprise | Point-in-time consensus estimates | Purchase (EODHD / Estimize) + audit |
| Any family on about 2000–2021 | Point-in-time market cap / shares **with dead companies**; pre-2010 corporate-action audit | Purchase or a large EDGAR project + audit |

## 14–15. Turnover, costs and holding periods

| Family | Holding period | Turnover | Cost a year at $100K (≈ 20 positions) |
|---|---|---|---|
| Earnings-event continuation | 1–3 months | ≈ 3–4× | ≈ 1.5–2.5% (≈ 1% at $200K) |
| Announcement premium | ≈ 1 month | ≈ 10× | > 4% (not viable) |
| Relative-strength swing | Weeks–months | ≈ 4–8× | ≈ 2–4% |
| Value | 6–24 months | ≈ 0.5–1× | ≈ 0.1–0.3% |
| Net issuance | ≈ 12 months | ≈ 0.5–1× | ≈ 0.1–0.3% |

## 16–17. Feasible now vs requires new data

| Feasible with current data (2010–2021) | Requires acquisition or new infrastructure |
|---|---|
| **Value (B/M)**: ready now | Any extension to about 2000 (point-in-time market caps / shares with dead companies) |
| **Earnings-event continuation**: free SEC timestamps; needs only a non-return audit | Analyst-surprise PEAD (consensus estimates) |
| Asset growth, accruals (not recommended) | Net issuance (audit of a market-cap-based construction; Smart Insider only 2015+) |

## 18. Which family has the strongest credible path to beating SPY's terminal wealth?

Honestly, **none has a strong path under our constraints.** Ranked:

1. **Earnings-event continuation:**
   - the best-motivated untested source of edge;
   - genuinely event-conditioned;
   - point-in-time-safe free data;
   - the edge is per event, so its mechanism can be evidenced at event level.

   Its weakness is documented large-cap decay since about 2005 and about 2% a year of costs at $100K.
2. **Value (B/M):** the cheapest and most implementable, but the weakest large-cap evidence and a known 2010s headwind.
3. Net issuance: promising, but not testable yet.

## 19. Use the final slot now, or preserve it?

**Preserve it.** Reasons:
- **Power.** On today's 12 years and 20 positions, even the improved framework gives a real 2–3% a year edge only a **12–23% chance** of qualifying. The slot is the last use of the Holdout budget, so it should be spent when evidence can actually be strong.
- **Two cheap, return-free steps can change the odds or the choice:**
  - (a) price the data that would extend history to about 2000–2004 with dead companies (power improves materially, §7);
  - (b) audit the earnings-event data, so that the leading new family can be pre-registered on a verified footing.
- **Order of work.** The framework must be frozen **before** any hypothesis is chosen, so the choice cannot be fitted to the gates.

## 20. Exact owner decisions required before any implementation

1. **Confirm the objective** (§2): terminal wealth above SPY total return, same capital, start and end, net, no leverage.
2. **Approve Amendment 3**, the terminal-wealth framework (§3):
   - W1 objective, W2 evidence (z = **1.645**; or choose 1.28), W3 attribution, R1–R4, G4′ robustness;
   - HO-W/HO-R for the Holdout and forward test;
   - rolling 1/3/5/10-year reporting (§4);
   - **retire the +0.25 Sharpe-over-EW hard gate** to a diagnostic (§6).

   This supersedes the P2-CP10 Amendment 2 proposal, whose G1.5 becomes W1.
3. **Approve the data-extension study:** obtain quotes, licence terms and integration options for point-in-time US equity data with delisted companies and historical shares / market caps (about 2000–2021). No purchase without a separate approval. Alternatively, decline and stay with 2010–2021.
4. **Approve a non-return earnings-event data audit:** map SEC 8-K Item 2.02 filings to our universe for 2010–2021 (and 2004–2009 if data is extended). It covers coverage, timing classes, duplicates, amendments and missing releases. It is an infrastructure run with no slot.
5. **Decide the account model for future hypotheses** (§7): keep the $4,000 minimum (≈ 20–24 positions at $100K), or allow more positions for low-turnover strategies. Unchanged until you decide.
6. **Confirm that relative-strength swing is dropped**, as not genuinely different.
7. **Keep slot 3 unused** until 2–4 are complete. Then I will return with **one** pre-registered hypothesis (earnings-event continuation or value), its frozen parameters and controls, for your approval.

**STOP.** Nothing was implemented or run, no candidate returns were computed, slot 3 is unused, and the Holdout is locked.
