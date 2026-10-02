# P2-CP10 — Final Phase 2 hypothesis opportunity review and H017 proposal (STOP)

- **Date:** 2026-10-02.
- **Status: PROPOSAL ONLY.**
  - Nothing implemented; no H017 or factor backtest; no factor or candidate-measure return computed.
  - Phase 2 slot 3 **not consumed**; the Holdout untouched.
  - **STOP:** awaiting the owner.
- **Supporting files:**
  - `research/phase2/P2_final_slot_literature_review.md`: external evidence, labelled pre-2010 / later / practice / ours.
  - `research/phase2/P2_final_slot_power.py/.json`: how large an edge any 20-stock book needs to pass the gates.
    - **Inputs:** only completed control books (SPY, same-universe EW, five random 20-stock books), so no factor returns.
    - **Method:** joint block bootstrap, 2,000 draws.
  - `research/hypotheses/H017.md`: the exact Value hypothesis, recorded as a proposal.

## Summary

1. **H016 is closed as Rejected**, preserved exactly as tested (D118).
2. **Objective (unchanged, now explicit):** find an investable long-only strategy that **beats S&P 500 buy-and-hold after realistic costs.** Risk metrics are safeguards, not the goal.
3. **The gates need one small amendment.**
   - In development, the current gates almost never pass a strategy that trails SPY. In the bootstrap, at most 1 draw in 2,000 did.
   - Nothing **guarantees** it, and the **Holdout criteria clearly allow it**.
   - **Proposed:** add one hard return gate, "net CAGR above SPY's", to development (G1.5), the Holdout (HO4) and the forward test. Nothing is removed or loosened.
4. **Value (book-to-market) is the only remaining family** that is:
   - genuinely distinct;
   - backed by long-standing external evidence;
   - computable today from verified point-in-time data.

   H017 = Value is fully specified below.
5. **But I do not recommend spending the final slot on it now.**
   - The power analysis shows that **any** 20-stock book needs a true edge of about **7% a year over its own universe** for an even chance of passing the (unchanged) gates.
   - Credible large-cap, long-only value evidence suggests **0–3% a year** before post-publication decay.
   - **Estimated chance that H017 qualifies, even if value works as the pre-2010 literature suggests: about 1–4%.**
   - In addition, it is public knowledge that large-cap value did poorly in most of our 2010–2021 development window.
6. **Recommendation:**
   - **Preserve slot 3**, and adopt the "beat SPY" amendment now.
   - Reconsider the research architecture (§13): the limiting factor is statistical power, not a lack of ideas.
   - If you prefer to spend the slot anyway, H017 = Value is ready for approval exactly as written.

## 1. H016 formally closed as Rejected

- **Result:** H016 (GP/A top 20, quarterly) is **Rejected** (owner decision 2026-10-02; P2-CP9: G1, G2 and G3 fail; G4 not triggered).
- **Preserved exactly as tested:** spec SHA-256 pinned (`qresearch.p2h016`), code (S016), configs and results (E016-01..08).
- **Never re-run with changes:** no change to the measure, portfolio size, rebalance frequency, ranking or any parameter.
- **Phase 2 budget:** 2 of 3 slots consumed; **1 remains**.

## 2. The clarified primary objective

> Find an investable long-only strategy that outperforms S&P 500 buy-and-hold after realistic trading costs.

- **Not** the objective:
  - lower drawdown, smoother returns or lower volatility;
  - beating equal weight while earning less than SPY;
  - a defensive portfolio that merely has a higher Sharpe.
- These remain **safeguards**.

The practical question every report must answer: **would the owner have been better off running this strategy than buying and holding the S&P 500?**

## 3. Proposed exact definition of "beat SPY"

On the common development window (first portfolio date → 2021-12-31), at $100K, net of commissions and slippage:

| Item | Rule | Type |
|---|---|---|
| **G1.5 (new, hard)** | **CAGR(H) > CAGR(SPY buy-and-hold, total return)**, both measured on the same dates. Over a common window this is the same as a higher total return | **Gate** |
| No leverage | Unchanged: the harness never borrows (integrity check "no_leverage"); long-only | Gate (existing) |
| Risk-adjusted safeguard | Unchanged G1.1(b): Sharpe(H) − Sharpe(SPY) ≥ +0.10 | Gate (existing) |
| Drawdown and concentration safeguards | Unchanged: G1.3 Calmar(H) ≥ Calmar(EW); G1.4 MaxDD(H) no more than 5 points deeper than EW's; 20 equal positions, 10% maximum weight | Gates (existing) |
| SPY report block (always shown first) | CAGR, total return, Sharpe, max drawdown and Calmar of H vs SPY; the same five at $200K and at 2× slippage; the year-by-year and two-year-block return difference vs SPY | Reported |

**Why "> 0" and not a margin:**
- the existing Sharpe margins already demand a large edge (§5);
- G1.5's role is to make it **impossible** to qualify while earning less than SPY.

A positive return margin (e.g. +1 point a year) is available as an owner option. It would cost little power for normal-risk strategies and more for defensive ones.

## 4. Are G1–G4 aligned with the objective? (review)

| Rule | Still useful? | Could it let a strategy qualify while materially trailing SPY? |
|---|---|---|
| G1.1(a): Sharpe − EW(same universe) ≥ +0.25 | **Yes, keep.** It is the overfitting/quality screen: the selection rule must add a large risk-adjusted edge within its own universe. The budget margin was fixed for false-positive control and must not be lowered | Not by itself, but it is Sharpe-based: a low-volatility book can satisfy it with a low return |
| G1.1(b): Sharpe − SPY ≥ +0.10 | Yes, keep (safeguard) | Same: it is Sharpe-based |
| G1.2: CAGR ≥ CAGR(EW) − 2 points | Weak relative to the objective | **Yes, in principle.** It explicitly tolerates a CAGR 2 points below EW, and EW itself can trail SPY (it did by 0.46 point a year in H016's universe) |
| G1.3 / G1.4 (Calmar, drawdown vs EW) | Yes (safeguards) | Not return gates |
| G2: > median random | **Yes:** separates selection skill from luck | No return requirement vs SPY |
| G3: ≥ 4 of 6 blocks vs EW, positive total excess | Yes (consistency) | Only vs EW; a candidate beating a lagging universe can still trail SPY |
| G4: perturbations, 2× slippage, costs ≤ 1.5% | Yes | No return requirement vs SPY |
| **Holdout HO1–HO3 (D094)** | Yes | **Yes, clearly.** HO1 needs only Sharpe(H) ≥ Sharpe(SPY); HO2 allows a CAGR 3 points below EW. A defensive candidate could pass the Holdout while trailing SPY |

**Measured in practice** (`P2_final_slot_power.json`; three risk profiles, true edges 0–8% a year over the universe):
- The current development gates passed a book with CAGR below SPY's in **at most 1 draw in 2,000**.
- The large Sharpe margin plus G3's positive-excess rule already imply a high return.
- So **G1.5 costs essentially no power** and only closes the gap by rule.

**Recommended smallest amendment (Amendment 2 to the Phase 2 methodology):**
1. Add **G1.5: CAGR(H) > CAGR(SPY)** (net, common development window, $100K base run).
2. Add **HO4: CAGR(H) > CAGR(SPY)** over the Holdout.
   - On 4.7 years this is noisy: a book with a true 3% a year edge over SPY and about 9% tracking error fails it about 20–25% of the time.
   - That is the honest price of the objective.
3. The forward-test criteria inherit HO4.
4. **Nothing else changes:** +0.25 margin, G1.1–G1.4, G2, G3, G4, HO1–HO3, the budget of 3, DSR and PBO as diagnostics.

**Not proposed** (it would weaken safeguards): replacing the Sharpe margins by a return-only test. Under the current rules, a strategy with a higher return than SPY but much higher volatility still fails G1.1(b). I consider that a correct safeguard ("no clearly unreasonable risk"). It is recorded here so the consequence is understood.

## 5. Statistical power: the binding constraint (applies to every family)

Same mechanics as H016: 20 positions, 2010-03 → 2021-12. The noise is taken from the five completed random books (no factor returns):

| Observed noise of a 20-stock book | Value |
|---|---|
| Tracking error vs SPY | 8.1–11.0% a year |
| Tracking error vs same-universe EW | 6.6–8.9% a year |
| Spread of CAGR across 5 random books (pure luck) | ± 2.9 points a year (sd) |
| Spread of Sharpe across random books | ± 0.145 |
| Universe (EW) minus SPY, CAGR | −0.46 point a year |

**Probability of passing G1–G3 (plus G1.5).** G4 is not modelled, so these are upper bounds. "Edge" = true excess return over the same-universe EW, net:

| True edge (a year) | Random-like book | Concentrated tilt (1.4× tracking) | Defensive book (0.75 beta) |
|---|---|---|---|
| 0% | 0.2% | 0.4% | 0.2% |
| 1% | 0.4% | 0.7% | 0.4% |
| 2% | 1.5% | 1.3% | 1.3% |
| 3% | 3.8% | 3.3% | 3.2% |
| 4% | 9.3% | 6.4% | 7.2% |
| 5% | 19.5% | 10.5% | 13.8% |
| 6% | 35.9% | 17.3% | 24.5% |
| 8% | 66.9% | 38.1% | 52.8% |

**Reading:**
- A 50% chance needs about **7% a year** of true edge over the universe; an 80% chance needs more than 8%.
- The binding gate is G1.1(a), the +0.25 Sharpe margin over EW: +0.25 Sharpe is about 4.75% a year at a 19% volatility, before any noise.
- **Published long-only, large-cap factor edges are a fraction of that.**
- This helps explain why every hypothesis tested so far (H001–H016) failed, and why the next will very likely fail too, whatever its quality. The margin protects against false positives; it also makes modest **true** edges invisible on 12 years with 20 stocks.

## 6. Remaining genuinely distinct families (evidence, data, costs, plausibility)

Details and citations are in the literature review.

| Family | Distinct? | External evidence for large-cap long-only | Point-in-time data today | Turnover / cost | Plausible edge over universe | Chance of qualifying (§5) |
|---|---|---|---|---|---|---|
| **Value: B/M** | Yes | Oldest premium; **weakest in large caps** (Loughran 1997; Israel & Moskowitz 2013); post-publication decay; long drawdowns | **Yes:** equity and market cap approved, SEC-verified (96.4% within 0.5%) | Very low (≈ 0.5–1× a year; ≈ 0.1–0.3% a year) | 0–3% | **≈ 1–4%** |
| Net issuance / net payout | Yes | Robust in all size groups (Fama & French 2008), mainly the short leg | **No:** share counts unsafe; a market-value-based construction is unaudited | Very low | 0–2% long-only | Not testable yet |
| Asset growth / investment | Partly (overlaps value) | Weak among big stocks (Fama & French 2008) | Yes | Low | 0–1% | < 1% |
| Accruals | Overlaps profitability | Decayed in the 2000s (Green, Hand & Soliman 2011) | Yes | Low | ≈ 0 | < 1% |
| Analyst revisions, PEAD | Yes | Weakened in large caps | **No** (data) | Moderate | — | — |

I am not forcing three alternatives: **only Value is credible and ready.**

## 7. Detailed evaluation of Value

| Question | Assessment |
|---|---|
| Historical premium in large US stocks | Present but **much smaller** than in small stocks, and statistically weak in the largest stocks in several studies (Loughran 1997; Fama & French 2006/2012; Israel & Moskowitz 2013) |
| Weakened after publication? | Yes. The anomaly average falls about 58% after publication (McLean & Pontiff 2016). Fama & French (2021) find the 1991–2019 US premium lower than 1963–1991 and statistically weak (later evidence, overlapping our window) |
| Can it beat SPY after costs? | Costs are not the problem (very low turnover). Return is: a concentrated value book must beat the **cap-weighted** index, whose large-growth tilt historically was value's opposite. Pre-2010 evidence supports a modest edge over a broad universe, not a reliable edge over SPY |
| Long underperformance | Standard: 1998–2000, 2007–2009, and (public knowledge) most of 2010–2020. Multi-year lags of 10+ points are normal for value |
| Sector concentration | High: raw B/M among non-financials concentrates in energy, materials, utilities, industrials, autos and retail. Industry-relative B/M reduces this (Asness, Porter & Stevens 2000), but it would add a choice, so it is not proposed |
| Value traps | Severe in a 20-name book: most high-B/M firms disappoint; a few winners carry the premium (Piotroski 2000) |
| Accounting comparability | Book equity omits internally created intangibles (Lev & Sougiannis 1996). Buybacks depress book equity. Book is understated for asset-light, intangible-rich firms, which value will systematically avoid |
| Statistical power | §5: needs about 7% a year to have an even chance; the plausible edge is 0–3% |
| Data errors | Value ranks the **extremes**, where data errors concentrate (1.8% of equity values differ from SEC by > 10%; possible dual-class market-cap mismatches). A pre-run top-of-ranking audit is required (§8) |
| Contamination | Large-cap value's weak 2010–2020 is public knowledge. It points against value, so it is not hindsight in value's favour, but a failure would be largely predictable |

**Verdict on Value:**
- It is the **strongest remaining family**, and the only one that clears every owner criterion except the decisive one: a **credible path to qualifying and beating SPY** under our constraints.
- On the evidence, that path is **weak**.

## 8. H017 = Value, exactly specified (for approval only if the slot is spent)

The full text is in `research/hypotheses/H017.md`.

- **Measure:** B/M = latest point-in-time stockholders' equity / point-in-time market cap on T. Book equity ≤ 0 is not ranked. One measure, no alternatives.
- **Universe:**
  - eligible (≥ $2B, price ≥ $5, ADV ≥ $5M, SEC correction layer);
  - non-financial / non-REIT (SEC SIC at filing);
  - B/M computable.
- **Portfolio:**
  - top 20 by B/M, equal weight;
  - quarterly (first session of March, June, September and December; next-open execution); first decision 2010-03-01;
  - the H016 mechanics exactly: $4,000 minimum, 15% reserve, one-time top-up ≥ $250, D051, $7 and 10 bps;
  - $100K primary, $200K sensitivity only.
- **Window:** 2010-03-01 → 2021-12-31, warm-up from 2008-07; the Holdout locked.
- **Gates:** G1 (with G1.5), G2, G3, G4, as amended (§4); the SPY block reported first; DSR (N = 4 Phase 2 candidates, 44 cumulative) and PBO as diagnostics; the frozen survivorship sensitivity.
- **Prerequisites before the candidate run:**
  1. a frozen spec, hash-pinned;
  2. S017 = the S016 code path with a "bm" ranking (unit tests incl. truncation);
  3. canary X981 (random seed 0, shadow B/M ranking: counts and hash only);
  4. **top-of-ranking data audit:** for the shadow top 20 at every rebalance, compare equity with the SEC filing and check market cap for dual-class consistency. Identifiers only, no returns. Any systematic error means STOP.

## 9. Proposed controls (fixed before any run)

| Control | Separates | Role |
|---|---|---|
| SPY buy-and-hold (E900-07) | **The objective** | G1.1(b), G1.5, SPY block |
| EW-H017: equal weight of the exact H017 universe | **Universe effect** (EW-H017 vs SPY) and **selection effect** (H vs EW-H017) | G1.1(a), G1.2–G1.4, G3 |
| Random 20-stock books, seeds 1–5, identical mechanics | **Random-selection luck** | G2 (median), each reported |
| Low-B/M book ("growth": the 20 lowest B/M), identical mechanics | **Factor effect** (does the measure sort returns monotonically?) | Diagnostic only, never a candidate |
| Broad EW ≥ $2B (E901-07) | Context | Reference |

## 10. Turnover and costs

- **Value:** quarterly re-selection on a slow-moving ratio. Expected turnover is well under H016's 149% a year: roughly 50–100% a year, so roughly 0.1–0.3% a year of costs at $100K (about 60–120 orders a year).
- **G4(c) cap:** 1.5% a year, so no concern.

## 11. Estimated QuantConnect runs and runtime (only if approved)

| Runs | Count | Time |
|---|---|---|
| Canary X981 | 1 | ≈ 20 min + result download |
| Committed: candidate, EW-H017, 5 random, $200K, low-B/M control | 9 | ≈ 15 min each + 0–75 min result download ≈ 3–6 h |
| Conditional robustness (only if G1, G2, G3 and G1.5 pass): 2×/4×/6× slippage, P1–P6 | ≤ 9 | ≈ 3–6 h |

- **No extra spending** (within the existing $24 a month).
- **Implementation:** about 1 day (reusing S016).

## 12. Recommendation

1. **Approve Amendment 2** (G1.5, HO4, forward test), whatever you decide about H017. It aligns the methodology with the objective without weakening anything.
2. **Do not spend slot 3 on H017 now.**
   - With an estimated 1–4% chance of qualifying even if value works as the older evidence suggests, the slot would almost certainly be consumed for a predictable "not qualified".
   - The slot is the last Holdout use in the hypothesis budget, and has more value preserved.
3. If you nevertheless want the final attempt, **H017 = Value (B/M)**, exactly as in §8 and `research/hypotheses/H017.md`. It is the only justified family; I would not substitute anything weaker.

## 13. If the slot is preserved: what would change the odds (each needs your decision)

These are not ways to make a strategy pass. They are ways to make a **true** edge detectable without lowering any safeguard.

1. **More history.**
   - Extend development back to 1999 (fundamentals exist from about 1998).
   - That doubles the sample, which cuts the sampling noise in Sharpe differences by about 30%. A smaller margin could then give the same false-positive protection. That would be a separately justified, owner-approved recalibration, not a loosening on the current data.
   - **Needs:** a re-audit of the pre-2010 dataset and survivorship (D033 currently limits official research to 2010+).
2. **More positions.**
   - 50–100 names cut selection noise roughly in half.
   - **Needs:** more capital or fractional-share execution (the $4,000 minimum), and an owner decision on the account model.
3. **New data.**
   - An audited issuance/payout construction, or point-in-time analyst data (spending approval).
   - This would open a second credible family.
4. **Accept the passive conclusion.** For a $100K–$200K account, SPY buy-and-hold remains the rational default until a candidate clears the bar.

## 14. Exact decisions for the owner

1. **Confirm H016 closed as Rejected,** preserved exactly as tested (recorded as D118).
2. **Approve or amend the definition of "beat SPY"** (§3): G1.5 CAGR(H) > CAGR(SPY), net, common window; no margin (or name a margin).
3. **Approve Methodology Amendment 2** (§4): add G1.5, HO4 and the forward-test equivalent; everything else unchanged.
4. **Decide the final slot:**
   - **(a) preserve it** (recommended), and choose which of §13's architecture options, if any, to study next (design only, no backtests); or
   - **(b) spend it on H017 = Value (B/M)** exactly as specified, authorising implementation, the canary, the top-of-ranking audit and the 9 committed runs (+ ≤ 9 conditional), with STOP at the development checkpoint; or
   - **(c) close Phase 2: No Production Candidate Found.**
5. **If (b):** approve the low-B/M diagnostic control (adds 1 run), and confirm that no alternative value measure, composite, industry adjustment or sector cap will be added.

**STOP.** No H017 implementation, no run, no factor-return calculation, slot 3 unused, Holdout locked.
