# Size-proxy evaluation — CP2 addendum

| Field | Value |
|---|---|
| Decision | **REJECTED for the primary research universe** by the owner on 2026-09-28 (D033). Kept as research history. It may only be used as the imperfect universe for an optional 1999–2009 stress test of finalists (D035). The pending v1.1 re-runs were cancelled (D038), so the numbers below remain provisional. |
| Status | **PROVISIONAL (final runs cancelled).** Based on runs E953-01 (2010–14) and E953-02 (2015–21), X953 v1.0. |
| Still pending | (1) v1.1 re-runs E953-04/05 with the corrected US-common-stock rule (D030). (2) The 1999–2009 check on the old dataset (E953-06/07); the first attempt, E953-03, failed because QuantConnect's daily log allowance ran out. |
| Why pending | The daily log allowance (about 3 MB) did not reset at 00:00 UTC as assumed; it was still 0 at 05:00 UTC on 2026-09-28. The runs start automatically when it returns. |
| Plan | Written before any result, in `size_proxy_plan.md`, including the deviations recorded before the official runs. **Caveat:** because of the `.gitignore` bug (D032), the plan file was not actually committed until 2026-09-28, after the results. Git history therefore cannot prove its timing. The commit messages `fe72067` and `2881f25` announced it before the runs, but the file itself was missing from them. |
| Data files | `size_proxy/` (per-variant agreement, yearly counts, monthly forward returns, false-positive samples, ticker classification) |

No research campaign has started. No strategy returns were computed. The forward returns below are for *universes*, over 2010–2014 (in-sample) only.

---

## 1. Exact proxy definition (the recommended candidate: "C20 + E5")

Evaluated on the first trading day of each month, using only data up to the prior close. The production universe would apply it daily in the same way.

1. **Pool.** Every security in QuantConnect's daily price universe, which includes delisted securities, with:
   - raw prior-close price ≥ $5;
   - 20-day average daily dollar volume ≥ $5M;
   - at least 63 days of price and volume history.
2. **Size rule.** 63-day average daily dollar volume (**ADV63**) ≥ **$20M** (nominal).
3. **Known-type exclusion (E1).** If Morningstar fundamentals exist for the security, keep it only if it is a US common stock:
   - common stock, not a depositary receipt;
   - primary share, **or** a US-domiciled company (D030).

   If no fundamentals exist, the security is **kept**. This is what makes the rule survivorship-free: companies that later died have no fundamentals.
4. **ETF twin filter (E5).** A security **without** fundamentals is dropped if its 63-day daily returns have |correlation| ≥ 0.95 with any other pool security. Index, leveraged, inverse and commodity ETFs have near-duplicates; individual companies almost never do.

Every input is a price, a volume, or a flag that can only *remove* a security whose type is known. Nothing depends on whether a company survived.

## 2. Why this one

- It had the best 2010–14 F1 among the three pre-registered primary rules (A-1000, B-90, C-20), under every exclusion variant. That was the single, pre-declared selection step.
- It is also the simplest rule and adapts naturally to the number of listed large companies. A fixed count (top-1000) drifts badly when the true universe grows from about 700 to 1,500 names.
- **Known weakness:** it is a *nominal* dollar-volume floor. Market-wide trading volume in 1999–2003 and 2008–09 differed from 2010–14, so its behaviour before 2010 must be checked (pending, §9).

## 3. Agreement with the reference (MarketCap ≥ $2B), 2010–2014

"Reference" means the harness's eligible set: US common stock, major exchange, MarketCap ≥ $2B, price ≥ $5, ADV20 ≥ $5M. Counts are per month, averaged over 60 months. F1 is pooled over all months.

| Variant | Reference names | Proxy names | False positives | False negatives | Precision | Recall | F1 | Worst month F1 |
|---|---|---|---|---|---|---|---|---|
| **C20 + E5 (twin 0.95)** | 835 | 1,010 | 318 | 143 | 0.685 | 0.829 | **0.750** | 0.714 |
| C20 + E1 (no ETF filter) | 835 | 1,148 | 456 | 143 | 0.603 | 0.829 | 0.698 | 0.657 |
| C20 + E0 (no type filter at all) | 835 | 1,342 | 650 | 143 | 0.516 | 0.829 | 0.636 | 0.596 |
| C20, known-type names only (E3, diagnostic) | 835 | 789 | 97 | 143 | 0.877 | 0.829 | **0.852** | 0.832 |
| A1000 + E5 | 835 | 1,000 | 317 | 152 | 0.683 | 0.818 | 0.744 | 0.711 |
| B90 + E5 | 835 | 803 | 211 | 243 | 0.737 | 0.709 | 0.723 | 0.698 |

- Every one of the 144 evaluated months had the reference set identical to the harness's own eligible set (a built-in check).
- **Important:** F1 against this reference is a *lower bound*. The reference itself is survivorship-biased: see §6.

## 4. Agreement by year (C20 + E5)

| Year | Reference names | Proxy names | Precision | Recall | F1 | F1, known-type only |
|---|---|---|---|---|---|---|
| 2010 | 687 | 926 | 0.631 | 0.850 | 0.724 | 0.845 |
| 2011 | 775 | 983 | 0.665 | 0.843 | 0.744 | 0.857 |
| 2012 | 788 | 965 | 0.688 | 0.843 | 0.758 | 0.859 |
| 2013 | 901 | 1,020 | 0.713 | 0.807 | 0.757 | 0.850 |
| 2014 | 1,022 | 1,155 | 0.719 | 0.813 | 0.763 | 0.851 |
| *2015* | 1,055 | 1,181 | 0.747 | 0.837 | 0.790 | 0.863 |
| *2016* | 1,022 | 1,124 | 0.774 | 0.851 | 0.811 | 0.870 |
| *2017* | 1,116 | 1,206 | 0.770 | 0.833 | 0.800 | 0.863 |
| *2018* | 1,185 | 1,293 | 0.774 | 0.844 | 0.807 | 0.872 |
| *2019* | 1,183 | 1,247 | 0.796 | 0.839 | 0.817 | 0.874 |
| *2020* | 1,189 | 1,315 | 0.782 | 0.864 | 0.821 | 0.872 |
| *2021* | 1,503 | 1,580 | 0.783 | 0.824 | 0.803 | 0.856 |

Italic years are the out-of-period check: membership only, nothing tuned. Agreement **does not degrade** out of period. It improves slightly, because ETFs, ADRs and later-disappeared companies make up a smaller share of liquid securities there.

## 5. Stability across thresholds and variants (2010–14 F1; 2015–21 in brackets)

| Rule family | Values tested → F1 (E1 exclusion) |
|---|---|
| C. ADV63 floor | $5M 0.600 · $10M 0.668 · **$20M 0.698** · $40M 0.641 |
| A. Top-N | 500 0.520 · 750 0.630 · **1000 0.684** · 1250 0.693 · 1500 0.671 (2021: top-1000 drops to 0.68 as the universe grows) |
| B. Dollar-volume coverage | 80% 0.507 · 85% 0.578 · **90% 0.650** · 95% 0.699 |
| ETF twin filter on C20 | corr ≥ 0.90 0.763 [0.819] · **0.95 0.750 [0.807]** · 0.98 0.738 [0.790] |
| Exchange filter (E2) on C20 | 0.700 vs 0.698 without it: **no material effect** |
| SPY-correlation ETF filter (E4) on C20 | 0.709: small effect |

- The C floor has a reasonable plateau between $10M and $40M: F1 is within about 0.06 of the peak. $20M sits in the middle; it was chosen before the results.
- The twin-filter threshold barely matters (±0.013).
- Families A and B are clearly worse or less stable.

## 6. What the disagreements are made of (C20, 2010–14, per month)

**False positives (318/month under E5; 456 under E1):**

| Type | Per month | How identified |
|---|---|---|
| No fundamentals (type unknown) | about 221 (E5) / 359 (E1) | see the sample below |
| US common stock with MarketCap $1–2B | 68 | fundamentals |
| US common stock with MarketCap $0.5–1B | 11.5 | fundamentals |
| US common stock with MarketCap < $0.5B | 1.8 | fundamentals |
| MarketCap missing (0) | 11 | fundamentals |
| Non-major exchange | 4.7 | fundamentals |

**Sample of the no-fundamentals false positives.** 300 names were drawn deterministically, 60 each June from 2010 to 2014, and classified by hand from the tickers. The classification is evaluation-only (`size_proxy/fp_ticker_classification.csv`).

| Type | Share |
|---|---|
| **US common stocks whose security later ended** (Alcoa pre-2016, Time Warner, DuPont, Precision Castparts, SanDisk, Genzyme, JCPenney, Heinz, Sears, Chesapeake, BB&T, …) | **49%** |
| ADRs | 22% |
| ETFs/ETNs (bond, country, sector, commodity) | 19% |
| Foreign-domiciled ordinary shares on US exchanges | 8% |
| MLPs/LLCs | 1% |

**The reference is survivorship-biased even in 2010–14.**

- In **both** QuantConnect datasets, these companies have no fundamentals at all while they traded. I verified this for Alcoa, DuPont, Time Warner, Chesapeake, JCPenney, BB&T, SanDisk, Genzyme and Weatherford on 2010-03-01.
- The proxy *correctly* includes such companies: Heinz 42 of 42 months, Time Warner 60 of 60, Sears 60 of 60. The reference includes none of them.

**Estimated agreement against a survivorship-complete reference.**

- Assume the US common stocks among the unknown-type false positives are ≥ $2B at the same rate as the known-type proxy names (precision 0.877).
- Then about 95 of the 318 monthly false positives are really true positives. The estimated F1 becomes **about 0.80**: precision about 0.78, recall about 0.83.
- With a perfect type filter it would be about 0.85, the known-type figure.

**Remaining contamination.** ETFs, ADRs and MLPs still in the proxy universe number about 95 per month, **about 9% of the proxy universe**. The owner's spec excludes them.

**False negatives (143/month).** These are mostly companies just above the threshold, with low trading activity:

| MarketCap | Share of false negatives |
|---|---|
| $2–3B | 62% |
| $3–5B | 30% |
| $5–10B | 7% |
| > $10B | 1% |

Their median annual turnover (ADV × 252 / MarketCap) is 1.2×, against 2.2× for correctly included names.

## 7. Does the proxy include or exclude particular kinds of companies?

| Dimension | Reference | Proxy (C20) | Reading |
|---|---|---|---|
| **Turnover** | median 2.2×/year among true positives | false positives with a known cap < $2B: 5.5×/year; false negatives: 1.2×/year | **Main bias.** The proxy swaps quiet mid-caps for heavily traded smaller caps. |
| Volatility (median absolute daily move) | 1.0% (true positives) | 1.1% (false positives); 0.9% (false negatives) | Slight tilt to more volatile stocks |
| Nasdaq share | 30% of true positives; 29% of false negatives | **43%** of known-type false positives | False positives lean to Nasdaq (high-turnover tech, biotech) |
| Sector (known-type names) | Industrials 14.3%, Financials 12.4%, Utilities 5.1%, Consumer Cyclical 12.5%, Technology 12.4% | Industrials 13.2%, Financials 11.2%, Utilities 4.0%, Consumer Cyclical 13.7%, Technology 13.3% | Low-turnover sectors under-weighted by about 1 percentage point; high-turnover sectors over-weighted by about 1 point. Small. |
| Type | US common only | + about 9% ETFs, ADRs, MLPs | Contamination |
| Survivorship | Misses later-disappeared companies | Includes them | **The proxy is better here** |

## 8. Evidence of a different bias: universe forward returns (2010–14 only)

Equal-weight next-month return of each group, formed monthly; 59 months.

| Group | Annualised mean | Difference vs the reference | t-stat |
|---|---|---|---|
| Reference (MarketCap ≥ $2B) | 13.4% | — | — |
| Proxy (C20, E1) | 13.3% | −0.2%/year | −0.13 |
| In proxy, not in reference | 12.7% | −0.7%/year | −0.22 |
| In reference, not in proxy | 13.6% | +0.1%/year | +0.08 |
| Proxy (A1000) | 13.1% | −0.4%/year | −0.27 |
| Proxy (B90) | 12.9% | −0.5%/year | −0.41 |

- No return difference between the proxy universe and the reference universe is distinguishable from noise.
- Every gap is well inside the pre-registered ±2%/year.
- Caveat: 2010–14 was a calm, rising market, so the high-turnover tilt could matter more in stressed periods. The 1999–2009 check is meant to test this and is pending.

## 9. Still missing before a final verdict

1. **v1.1 re-runs (E953-04/05).**
   - The D030 fix brings US companies wrongly flagged "non-primary" (GE, Bank of America, Visa, Comcast, …) into both the reference and the known-type exclusion.
   - Expected effect: the reference grows by roughly 130–240 names per month, and most of them are highly liquid. Recall and F1 should *rise*, but this has to be measured.
2. **1999–2009 on the old dataset (E953-06/07).**
   - How recall behaves on surviving large companies, given very different market-wide volume.
   - Whether the proxy includes Enron, WorldCom, Lehman, Bear Stearns, Merrill Lynch, Countrywide, Lucent and old GM while they were large.
   - The survivorship return gap: proxy vs a survivors-only universe.
   - The nominal $20M floor may be too strict in 1999–2003 and too loose in 2008–09. That is the largest open risk.

## 10. Pre-registered thresholds vs the evidence so far (C20 + E5)

| Condition for APPROVE | Status |
|---|---|
| 2010–14 F1 ≥ 0.85 | ❌ 0.750 as measured; about 0.80 estimated against a complete reference; 0.852 on known-type names |
| Every year F1 ≥ 0.80 | ❌ 0.72–0.76 as measured |
| 2015–21 F1 within 0.05 of 2010–14 | ≈ +0.057, an *improvement*, not a degradation |
| Neighbouring thresholds within 0.05 | ≈ within 0.06 ($10M, $40M); the twin threshold is within 0.013 |
| Forward-return gap ≤ 2%/year | ✅ −0.2%/year, not significant |
| Captures known failed companies | ✅ for 2010–14 (Heinz, Sears, Time Warner); 1999–2009 pending |

## 11. Provisional recommendation

**APPROVE WITH LIMITATIONS (provisional).** Final after the v1.1 and 1999–2009 runs.

- **Why not APPROVE:** measured F1 is 0.75, and even the survivorship-corrected estimate (about 0.80) is below the pre-registered 0.85. About 9% of the proxy universe is ETFs, ADRs or MLPs. It tilts toward high-turnover stocks.
- **Why not REJECT:**
  - It agrees with the reference on about 83% of the reference's names.
  - Its errors are explainable, stable across years and thresholds, and do not show up in universe returns.
  - It fixes the bigger problem: the MarketCap reference itself drops every company that later disappeared.
- **Limitations that would come with approval:**
  1. The universe definition changes from "MarketCap ≥ $2B" to "most-traded US-listed stocks (ADV63 ≥ $20M)", about 800–1,500 names. It is a liquidity universe, not a size universe.
  2. Residual ETF, ADR and MLP contamination of about 9%. Every strategy report will list the non-common names it traded.
  3. A tilt toward high-turnover stocks. Hypotheses about volume or attention must account for it.
  4. The nominal $20M floor must be confirmed for 1999–2009. If recall collapses there, an adjustment (e.g. a floor scaled to market-wide volume) would come back to you for approval before use.

STOPPED. No research campaign will start without your approval.
