# P6-CP1 — Sector / ETF Rotation Evidence and Validation Architecture (DESIGN ONLY; STOP)

- **Date:** 2026-10-05.
- **Owner direction:** "Phase 6 — Sector / ETF Relative Strength & Rotation Research; P6-CP1 — Evidence, Data Feasibility and Signal-Validation Architecture Only" (D159; `docs/owner/2026-10-05_phase6_sector_rotation_design.md`).

**Not done:**
- no real sector signal, ranking, return, IC, portfolio, terminal wealth or SPY comparison computed;
- no lookback tuned;
- no 2018–2021 data; the Holdout is locked;
- nothing purchased.

**Done:**
- a literature review (`research/phase6/P6_CP1_references.md`);
- a QuantConnect data-**availability** probe (E988-01: bar dates, gaps, volume and corporate-action counts only, no returns; `research/phase6/p6_data_probe.json`);
- a synthetic power / null study (`research/phase6/p6_power.py` → `p6_power_result.json`);
- the cost / tracking arithmetic (`p6_costs.py` → `p6_costs_result.json`);
- the design module `research/phase6/p6_xs.py` and `tests/test_p6_design.py`.

## Short answer

1. **The evidence is real but old and weakening.**
   - Industry momentum is a strong, replicated pre-1999 US result (Moskowitz–Grinblatt 1999, Tier A for its sample).
   - It is largely a **short-horizon** effect: it disappears with a one-month skip (Grundy–Martin), and part of it is cross-serial / lead-lag (Lewellen; Hong–Torous–Valkanov).
   - The one clean post-2000 sector-ETF test found **no momentum** (iShares sector ETFs 2000–2011).
   - Later work attributes industry momentum to factor momentum (post-2017, context only).
2. **The cleanest universe is the nine original Select Sector SPDRs.**
   - All exist from 1998-12-22 in QuantConnect, with complete daily history, no gaps, no pre-launch backfill and no taxonomy change in 2000–2015.
   - XLRE (2015) and XLC (2018) are excluded.
3. **History can be extended to 2000 without buying data.**
   - That gives about 215 monthly decisions instead of 89. It needs your amendment of the "1999–2009 = stress only" rule (D035) for Phase 6.
   - The SPDRs genuinely traded from 1999, and 2000–2017 is post-publication for Moskowitz–Grinblatt.
4. **Power is the binding problem.** With 9 sectors (about 6 effectively independent), monthly decisions and a 1% test (synthetic):

   | Development window | 50% detectable top-3 edge | 80% detectable top-3 edge |
   |---|---|---|
   | 2000–2017 | about +3.3%/yr over the sector average | about +5.7%/yr |
   | 2010–2017 alone | about +5.3%/yr | above +7%/yr |

   A realistic post-2000 effect is about 0–2.5%/yr.
5. **Recommendation: NO-GO** for Phase 6 as a production-candidate search.
   - If you want the sector question settled anyway, the only defensible form is **one** pre-registered falsification test (H021-A: 6-month total-return relative momentum, monthly, 9 SPDRs, 2000–2017), knowing a fail is uninformative about edges below about 3%/yr.

---

## 1. H020 status
H020 is **rejected by its frozen test** (P5-CP3, D158: NO CHART SCORE QUALIFIED FOR PORTFOLIO RESEARCH). Formal closure is **pending your decision**: I recommended closing it as Rejected, preserved exactly as tested. Nothing in Phase 6 reuses or rescues H020.

## 2. Exact Phase 6 research question
> **Do US equity sectors with stronger medium-term relative strength (trailing total return) subsequently earn higher sector-relative total returns than weaker sectors?**

This is a cross-sectional, sector-level predictability question, tested before any portfolio. "Does a rotation portfolio beat SPY?" is a later question, asked only if the first is answered yes.

## 3. Why sector prediction is materially different
| Aspect | Individual-stock selection (H002–H020) | Sector selection (Phase 6) |
|---|---|---|
| Unit | About 1,000 stocks per date | 9 sector baskets |
| Noise | Idiosyncratic company news dominates | Diversified: about 60–70 stocks per ETF |
| Mechanism | Stock momentum, chart patterns | Industry information diffusion, slow-moving industry fundamentals, flows |
| Implementation | Many small positions, rebalancing costs | 1–4 liquid ETFs, a few orders a month |
| Statistical problem | Many cross-sectional observations, small IC | **Very few** observations per date (small-N) |

The mathematics (past returns) is shared; the unit of prediction is not.

## 4. Academic evidence for industry / sector momentum

| Study | Finding | Tier |
|---|---|---|
| **Moskowitz & Grinblatt (1999)** | Industry momentum is strong, explains much of stock momentum and survives standard controls (US, 1963–1995) | **A** for that sample |
| **Grundy & Martin (2001)** | Industry momentum needs **no skip month**; with a 1-month gap it is insignificant | B (critical qualification) |
| **Lewellen (2002)** | Momentum exists in industry portfolios but is driven by cross-serial covariance, not own autocorrelation | B |
| **Hong, Torous & Valkanov (2007)** | Some industries lead the market by up to two months | B (context for the null) |

**Answer to A:** yes. Industry momentum is documented as distinct from, and partly the source of, stock momentum (Moskowitz–Grinblatt). It is mostly a short-horizon, no-skip effect, and its mechanism is debated.

## 5. Practitioner evidence

| Source | Finding | Tier |
|---|---|---|
| Faber (2010) | Relative strength on Fama-French sector data back to the 1920s; outperformed buy-and-hold in about 70% of years; a trend filter cut volatility and drawdown | C |
| O'Neal (2000) | Sector mutual funds over 10 years to the late 1990s; momentum was strong | B/C |
| Antonacci, Dual Momentum | Relative + absolute momentum; claims drawdown reduction | C |
| Stangl et al. | Even perfect-foresight business-cycle rotation adds at most about 2.3% a year since 1948 | B (upper-bound context) |

## 6. Post-publication evidence

| Evidence | Finding |
|---|---|
| Moskowitz–Grinblatt sample | Ended 1995; published 1999. **2000–2017 is a genuine post-publication window for it** |
| Sector ETFs (iShares, 2000–2011, Journal of Asset Management 2014) | **No momentum** for formation 1–12 months and holding 1 / 6 months |
| Andreu et al. (2013), ETFs | About 5% a year combined country + industry momentum over the ETF periods. Mixed evidence: the headline mixes in country momentum |
| Stock-level momentum | Declined sharply after the early 2000s |
| † Arnott et al. (post-2017) | Industry momentum is subsumed by factor momentum |

**Answer to B:** the effect is **not** shown to be large and persistent in modern liquid US markets. The best post-2000 evidence on sector ETFs is null or weak.

## 7. Large / liquid-market relevance

- **Sector size:** sectors are large-cap aggregates by construction. The SPDRs hold S&P 500 constituents only, so the question concerns large, liquid companies.
- **Liquidity history** (E988-01 median daily dollar volume):
  - 1999: $0.2–3.5M for most SPDRs; XLK $19M;
  - 2002: $1.4–42M;
  - 2005 onward: ≥ $15M for all nine;
  - 2017: $0.2–1.4B.
- **Implication:** early-period prices may be slightly stale, but no day had zero volume and no session is missing. With monthly decisions and returns, the effect is small; it is disclosed and checked with a 2005+ sub-period diagnostic.

## 8. Proposed sector universe alternatives

| Option | Data | Quality | Problems |
|---|---|---|---|
| **A. 9 original Select Sector SPDRs** | QuantConnect daily from **1998-12-22**, complete | Tradable; one issuer, one index family (S&P sector indexes); constant 9 for 1999–2015 | XLF real-estate removal (2016); 2018 GICS reshuffle (XLC) in the OOS period; thin trading in 1999–2002 |
| A+. SPDRs + XLRE (+ XLC) | XLRE from 2015-10-08; XLC from 2018 | — | Changing N; XLRE 2 years in development, XLC none |
| B1. iShares US sector ETFs (10–11) | From mid-2000, **gappy** (up to 54 missing sessions), thin | Worse than A | Gaps, later start |
| B2. Vanguard sector ETFs | From 2004 | Liquid later | Shorter |
| B3. Fama-French / Ken French industry portfolios (free, from 1926) | **Host blocked** by the network policy; analytical only | Long history | Not tradable; all CRSP stocks (small caps); the very data on which the effect was discovered and backtested (Moskowitz–Grinblatt, Faber), so no out-of-sample value before 2000; annual revisions |
| C. Synthetic PIT sectors from our ≥ $2B stock universe (dated SEC SIC → FF12) | From 2010 only (market cap from Oct 2009; SIC coverage about 69% in 2010) | PIT-clean in principle | No longer history; complex; not tradable without stocks; overlaps the stock project |

## 9. ETF inception dates

| ETF | Launch | First QuantConnect bar | Index predecessor / backfill |
|---|---|---|---|
| XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY | 1998-12-16 (prospectus); trading 1998-12-22 | 1998-12-22 | S&P Select Sector indexes; **no backfill in QuantConnect** |
| XLRE | 2015-10-08 | 2015-10-08 | Real-estate index; no backfill |
| XLC | 2018-06-18 | none up to 2017-12-29 | Communication-services index; no backfill |
| iShares US sector ETFs | 2000-05 → 2000-06 | 2000-05-19 → 2000-07-14 | Dow Jones US sector indexes |
| Vanguard sector ETFs | 2004-01-26 / 2004-09 | 2004-01-30 / 2004-09-29 | MSCI US IMI sector indexes |

## 10. Data-history availability (E988-01, 1998-01-01 → 2017-12-31, availability facts only)
- **9 SPDRs:** 4,787 bars each (XLI 4,786); 0 sessions missing against SPY from the first bar (XLI 1); 0 zero-volume days.
- **Corporate actions:** 50–78 distribution events each; no splits. **XLF has one large distribution:** 2016-09-19, 18.8% of the reference price — the XLRE spin-off.
- **XLRE:** 559 bars from 2015-10-08. **XLC:** none.
- **QuantConnect does not backfill** ETF history before launch.

## 11. Problems caused by XLC / XLRE and other late ETFs
- **XLRE:** real estate sat inside XLF (financials) until **2016-09-16**, then was removed. Adding XLRE in 2015 changes N from 9 to 10 mid-sample and double-counts real estate for 11 months. Keeping 9 means XLF's composition changes in 2016. The total-return series handles the spin-off value (the distribution is in QuantConnect's dividend feed), but XLF's exposure changes; this is disclosed.
- **XLC (2018):** the 2018 GICS change moved Alphabet, Facebook and others out of XLK and XLY into XLC. This falls in the internal OOS period (2018–2021), so the 9-ETF universe changes character there. It is handled at that stage (owner decision), not in development.
- **Not done:** no ETF is used before its launch.

## 12. Do historical sector indexes solve it?
- **Partly, and not usefully for us.**
  - S&P sector index history before 1999 is not in our QuantConnect subscription.
  - Fama-French industry portfolios are free but blocked here, not tradable, broader than large caps, and are the in-sample data of the original studies.
- **Decision:** signal research on indexes would be separated from tradable implementation, so they could at most be a non-gating diagnostic. **I do not recommend using them.**

## 13. Are synthetic PIT sectors feasible?
- **Technically yes from 2010:** dated SEC SIC → FF12 groups of our ≥ $2B universe, value- or equal-weighted.
- **Not recommended as primary:**
  - no longer history than the ETFs;
  - 2010 classification coverage is about 69% (E987-01);
  - weaker investability;
  - more code, more failure modes.
- **Possible later use:** a robustness check only.

## 14. Recommended primary universe
**The 9 original Select Sector SPDRs (XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY), fixed for the whole development period.** XLRE and XLC are excluded. The constant N avoids the 9 → 10 → 11 structural change.

## 15. Earliest reliable date
- **Data:** from **1998-12-22**.
- **First decision:** a 6-month lookback allows decisions from **1999-06-30**.
- **Recommended development decisions: 2000-01 → 2017-11**, about 215 monthly decisions with 1-month responses ending ≤ 2017-12-29. This skips the thinnest-trading first year.

## 16. Is a pre-2010 extension feasible?
- **Yes, technically:** genuinely traded ETFs, no backfill, no taxonomy change, current subscription, no purchase.
- **Owner decision needed:** CLAUDE.md / D035 reserve 1999–2009 as an optional stress test of finalists only. Using 2000–2009 as development data for Phase 6 is a methodology change. It is justified because these instruments were tradable, the period is post-publication for Moskowitz–Grinblatt, and power more than doubles.
- **Answer to D:** yes. It is the single most important power lever.

## 17. Recommended primary relative-strength definition
- **Definition:** S_i(t) = sector i's **total return** (dividends reinvested) over the 6 months ending at the month-end close t.
- **No skip month.** Grundy–Martin show industry momentum needs no gap, and a 12-1 convention exists to avoid **stock-level** short-term reversal, which industries do not show.
- **Total return, not price:** dividend yields differ persistently across sectors (e.g. utilities vs technology), so price-return ranks would be biased.

## 18. Recommended lookback
**6 months, one lookback only.** It is Moskowitz–Grinblatt's headline formation period and is in the middle of the 3–12-month range used in the literature. It is not selected from our data.
- A 12-month lookback is the obvious alternative. If both are wanted, the null must include the max over both (§27). Synthetic: the max over {6, 12} has c = 2.50 instead of 2.27, with similar power, so nothing is gained.
- **Recommendation:** 6 months alone.

## 19. Recommended decision frequency
**Monthly** (last session of each month), responses non-overlapping.
- The effect is medium-term and the signal persistent.
- Weekly decisions with a 1-month response create overlapping responses: no new information, only autocorrelation.
- Weekly also multiplies turnover; there is no evidence of a weekly-specific effect.
- **Answer to F:** monthly.

## 20. Absolute-trend filter evidence
- **Time-series momentum** (Moskowitz–Ooi–Pedersen 2012): Tier A for liquid futures and indexes; its main documented benefit is crash / drawdown reduction.
- **For sector rotation:** practitioner evidence (Faber, Antonacci; Tier C) shows lower drawdown and volatility; terminal-wealth evidence against buy-and-hold is mixed and backtest-based.
- **Role:** the filter decides **whether to hold equities at all**. It is a market-timing overlay, not a sector-selection signal, and it cannot be tested cross-sectionally.

## 21. Does absolute trend belong in the first experiment?
**No.**
- The first experiment is a cross-sectional signal test; an absolute filter does not change the ranking.
- Its cash periods trade terminal wealth against drawdown, so it is a portfolio-stage design question (§27 of the brief).
- It would be tested only if H021-A qualifies, as a separately pre-registered H021-B overlay judged by terminal wealth vs SPY.
- **Answer to E:** pure relative momentum first.

## 22. Proposed number of explicit hypotheses
**One for the signal stage: H021-A**, 6-month total-return relative momentum. H021-B (absolute-trend overlay) is deferred to the portfolio stage and exists only if H021-A qualifies. **No optimizer, no grid.**

## 23. Cross-sectional signal-validation methodology (design; `research/phase6/p6_xs.py`)
- **Each month-end t:**
  - rank the 9 sectors by S_i(t);
  - response Y_i(t) = total return of sector i over month t+1 minus the 9-sector equal-weight average (execution convention: from t+1's open, later spec detail; the synthetic design uses month-to-month returns).
- **Statistics:**
  - **primary:** the mean monthly **Spearman rank IC**, with a Newey-West t (lag 0, non-overlapping);
  - **economic:** **top-3 minus the sector average**, annualised;
  - top-3 minus bottom-3;
  - **tercile monotonicity:** top 3 > middle 3 > bottom 3;
  - **stability:** both halves positive, and no 6-year block (2000–05, 2006–11, 2012–17) contributing more than 50% of the IC sum.
- **Proposed gates:**

  | Gate | Rule |
  |---|---|
  | P1 | t_IC > c (1% null) |
  | P2 | top-3 vs average ≥ **+3%/yr** (covers about 0.7%/yr costs, §35, with margin for the equal-weight-vs-SPY gap) |
  | P3 | Terciles monotonic |
  | P4 | Stability (as above) |

- **Diagnostics only:**
  - the 2010–2017 and 2005–2017 sub-periods;
  - 3- and 6-month responses;
  - the sector-average-vs-SPY difference.

## 24. Primary future-return horizon
**Next 1 month (sector-relative total return).** Industry predictability is strongest at short horizons (Moskowitz–Grinblatt; also later work). It matches monthly decisions and gives non-overlapping observations. 3 and 6 months are diagnostics only.

## 25. Effective-sample-size analysis
- **Cross-section:**
  - after removing the common market move, 9 sectors leave 8 degrees of freedom;
  - correlated clusters (cyclical vs defensive, beta differences) reduce that to an **effective about 6.1 independent sectors** (synthetic covariance);
  - per-date IC noise under no edge: sd 0.376, vs 0.354 if iid.
- **Time:**
  - monthly non-overlapping responses; null IC lag-1 autocorrelation about 0.006, so the effective T is about T: **215 (2000–2017) or 89 (2010–2017)**;
  - not 215 × 9 independent observations.
- **Per-month noise:** each month's IC is extremely noisy (sd 0.38). Detecting a mean IC of about 0.06 needs about 215 months at 1%.

## 26. Null-world methodology (primary)
- **Identity-tethered derangement:**
  - each null world draws one fixed permutation of the 9 sector labels with no fixed point;
  - each sector receives **another sector's entire signal history**.
- **Preserved:**
  - every return, the market and cross-sector co-movement and the volatility differences (returns untouched);
  - each signal's persistence, distribution and time-series structure (whole histories move);
  - universe composition and dates.
- **Broken:** only "own signal ↔ own future relative return".
- **Lead-lag effects:** cross-sector effects (Lewellen, Hong–Torous–Valkanov) can appear in null worlds and widen the null. That is conservative.
- **Procedure:** the complete procedure (every declared lookback, every gate) runs in every world. R = 5,000; c = the 50th-largest null statistic.
- **Synthetic calibration:** size 0.7% at a 1% nominal (600 no-edge panels).

## 27. Multiple-testing rule
- **One hypothesis, one primary statistic (t_IC of the 6-month signal), α = 1%.**
- If more than one lookback is ever declared, the world statistic is the **max over all of them** inside the null: full-search null.
- The prior stock-level technical looks (H002/H003/H008/H018/H019/H020) are a different unit of prediction; α = 1% stays as the conservative programme level.

## 28. Synthetic power study (`p6_power_result.json`; 300 panels per cell, 10,000 null worlds per case)

| Case | c (1%) | top-3 vs average +1.3%/yr | +2.5%/yr | +3.5%/yr | +7.1%/yr |
|---|---|---|---|---|---|
| 9 sectors, 2000–2017, 6-month | 2.27 | 8% | 29% | 56% | 95% |
| 9 sectors, **2010–2017 only**, 6-month | 2.26 | 7% | 13% | 30% | 70% |
| 9 sectors, 2000–2017, max(6, 12) | 2.50 | 14% | 34% | 68% | 100% |
| 11 sectors, 2000–2017, 6-month | 2.25 | 8% | 33% | 69% | 100% |
| 9 sectors, 2000–2017, 12-month | 2.31 | 12% | 34% | 64% | 99% |

Column headings are the realised top-3 excess of the primary case for the four planted drift sizes. The other cases' realised excess for the same drift differs by at most about ±0.6 points (full rows in the JSON).

**Answer to H:**
- 9 vs 11 sectors changes little.
- The **sample length** dominates: 2010–2017 alone needs edges about 1.6× larger.

## 29. 50% detectable edge
- **2000–2017:** about **+3.3%/yr** top-3 over the sector average (mean IC ≈ 0.057).
- **2010–2017:** about +5.3%/yr.

## 30. 80% detectable edge
- **2000–2017:** about **+5.7%/yr**.
- **2010–2017:** above +7%/yr.

## 31. Expected false-positive rate
**About 1%** with the tethered null (synthetic: 0.7%). If the economic, monotonicity and stability gates are also required, a false promotion is lower still.

## 32. Random / control design
- **Signal stage (canary):**
  - placebo signals (seeded random ranks), which should give IC ≈ 0;
  - a planted signal (Y itself), which should give IC = 1;
  - an independent slow recomputation of the total returns;
  - the truncation test.
- **Portfolio stage (only if H021-A qualifies):**
  - the equal-weight 9-sector book;
  - random top-3 books (seeded);
  - SPY buy-and-hold as the economic benchmark.

## 33. Total-return accounting (pre-registered distinction)

| Use | Price series |
|---|---|
| Ranking signal S (6-month return) | **Total return** (RAW × split × dividend feeds) |
| Response Y | **Total shareholder return** (same construction; XLF's 2016 XLRE distribution included as reinvested value) |
| Absolute-trend filter (later H021-B only) | Total-return price vs its moving average (one series, no price / total mixing) |
| Execution (later) | RAW prices, fill at the T+1 open |

**No split-adjusted-only series is needed:** ETFs have no splits in 1999–2017 (probe), but the construction handles them anyway.

## 34. Potential holding-count analysis (design level, synthetic model; not optimised)

| Top-k (equal weight) | Tracking error vs the 9-sector equal-weight average | Membership changes per month | Orders per year | Cost at $100K | Cost at $200K |
|---|---|---|---|---|---|
| 1 | 13.8%/yr | 0.40 | 9.6 | 1.03%/yr | 1.00%/yr |
| 2 | 9.1%/yr | 0.63 | 15.1 | 0.86%/yr | 0.81%/yr |
| **3** | **6.9%/yr** | 0.76 | 18.1 | **0.73%/yr** | 0.67%/yr |
| 4 | 5.4%/yr | 0.86 | 20.6 | 0.66%/yr | 0.59%/yr |

**Recommendation: top-3**, one third of the sectors.
- Concentrated enough that a real ranking edge shows up in wealth.
- Diversified enough to avoid single-sector risk: top-1 tracking error of 14%/yr would dominate any edge.
- About $33K per position at $100K, far above the $4,000 minimum position.
- **SPY gap:** to beat SPY, the top-3 book must also overcome the gap between the equal-weight sector average and cap-weighted SPY, a separate tracking component.

## 35. Expected future turnover / costs
- **Top-3, 6-month signal:** about 0.76 replacements a month, about 18 orders a year.
- **Cost:** $7 per order plus 10 bps per side, about **0.7%/yr at $100K** (0.67% at $200K), before optional re-equal-weighting.
- **Consequence:** the economic gate (+3%/yr) leaves about 2.3%/yr after costs.

## 36. Major methodological risks
1. **Low power.** A realistic edge (0–2.5%/yr) is below the 50% detectable edge (3.3%/yr even with 2000–2017). A fail would be weakly informative.
2. **Post-publication decay.** The best post-2000 sector-ETF evidence is null.
3. **Mechanism.** Industry momentum may be short-horizon autocorrelation or lead-lag (Grundy–Martin, Lewellen) or factor momentum (post-2017 context), not persistent sector leadership.
4. **Small N.** With 9 sectors (about 6 effective), each month's evidence is tiny; one or two regimes (e.g. 2000–02, 2008) can dominate. Hence the stability gate.
5. **Structural breaks:** XLF in 2016; XLC in 2018 (OOS).
6. **Thin trading in 1999–2002:** stale-price risk is small for monthly data; a 2005+ diagnostic is planned.
7. **Practitioner data snooping.** Sector-rotation rules (e.g. Faber, 2010) were designed on data through about 2009, which overlaps 2000–2009. We pre-register one textbook signal and do no search.
8. **The SPY hurdle:** equal-weight sectors vs cap-weighted SPY is an extra source of tracking difference at the portfolio stage.
9. **Absolute-trend cash drag:** H021-B could cut drawdowns but lose terminal wealth to SPY in long bull markets.

## 37. Comparison with H001–H020

| Hypothesis | Unit / signal | Phase 6 distinct? |
|---|---|---|
| H002, H003, H008 | Stock momentum / 52-week high / trend, stock level | Yes (different unit) |
| H004 | Stock-level variant | Yes |
| H014 | Stock-level trend portfolio (Phase 2) | Yes |
| H018 | Systematic search over stock technical configurations | Yes (no search; sector unit) |
| H019 | Cross-sectional stock signals (12-1, smooth momentum, trend factor) | Shares the IC methodology; **different unit (sectors)** |
| H020 | Stock chart structure | Yes |

**Overlap:** past returns are the input again. The predicted object, sector-group persistence, and the instrument (9 ETFs) are new. If H021-A fails, that is a different finding from H019's "no stock-level momentum".

## 38. GO / NO-GO recommendation
**NO-GO for Phase 6 as a production-candidate search (recommended).**
- The prior evidence for **post-2000** sector momentum in liquid US ETFs is null or weak.
- The detectable edge (+3.3%/yr at 50% power, even with the 2000–2017 extension) exceeds a realistic effect.
- After costs and the SPY hurdle, even a detected edge leaves little.

**Alternative (only if you want the sector question settled):** **one** pre-registered falsification test **H021-A**.
- **Universe and signal:** 9 SPDRs, 6-month total-return relative momentum, monthly, 1-month total-return response.
- **Period:** development 2000–2017 (requires amending D035 for Phase 6).
- **Null and gates:** tethered-derangement null (R = 5,000), the gates in §23.
- **Steps:** canary → null → pin c → one real evaluation → checkpoint → STOP.
- **Cost:** QuantConnect node time under an hour.
- **Caveat:** a pass would be meaningful; a fail would not exclude 1–3% edges.

**Answer to I:** only plausibly-large edges (≥ 3–5%/yr) can be detected before a portfolio is built. Realistic edges probably cannot.

## 39. Exact next owner decisions required
1. **Close H020** as Rejected (pending from P5-CP3).
2. **GO / NO-GO** for Phase 6 (recommendation: NO-GO).
3. **If GO** (H021-A falsification test only), approve:
   - **a.** The development period **2000-01 → 2017-11** for Phase 6, i.e. amend D035 for these ETFs. Otherwise 2010–2017 only (50% detectable edge about 5.3%/yr; not recommended).
   - **b.** The **9-SPDR fixed universe** (XLRE and XLC excluded; XLF 2016 break disclosed).
   - **c.** The **single signal:** 6-month total return, no skip; monthly decisions; 1-month total-return response.
   - **d.** **Gates P1–P4**, including the **+3%/yr** floor; α = 1%; tethered-derangement null with R = 5,000.
   - **e.** H021-B (absolute trend) **deferred** to a portfolio stage that exists only if H021-A qualifies.
   - **f.** No Ken French / index history (or allow the host for a non-gating diagnostic only; not recommended).
4. **Budget:** no data purchase needed in either case.

## Answers to the owner's explicit questions (A–J)

| Q | Answer |
|---|---|
| **A** | **Yes, historically.** Industry momentum is documented as distinct from, and a large source of, stock momentum (Moskowitz–Grinblatt, Tier A for 1963–1995). It is mostly a no-skip, short-horizon effect, and its mechanism is debated (cross-serial; factor momentum, post-2017) |
| **B** | **Not shown for modern liquid US markets.** The best post-2000 sector-ETF test is null (2000–2011). ETF studies mixing in country momentum are more positive. Momentum broadly decayed after 2000 |
| **C** | **The 9 original Select Sector SPDRs**, fixed, from 1998-12-22 (complete QuantConnect history, no backfill), with XLRE and XLC excluded |
| **D** | **Yes.** About 215 monthly decisions (2000–2017) on genuinely traded ETFs, at no cost. It needs your amendment of the D035 stress-only rule |
| **E** | **Pure relative momentum first.** The absolute trend is a portfolio-level overlay (cash vs equity) to test later, only if the signal qualifies |
| **F** | **Monthly** |
| **G** | **The next 1 month (sector-relative total return)**; 3 and 6 months as diagnostics |
| **H** | 9 sectors are about **6 effective**. Per-month IC noise is about 0.38. Power comes almost entirely from the **number of months**: 50% detectable top-3 edge about 3.3%/yr (2000–2017) vs about 5.3%/yr (2010–2017); 11 sectors add little |
| **I** | **Only large edges** (≥ 3–5%/yr top-3 over the average). A realistic 0–2.5%/yr edge would usually be missed |
| **J** | If H021-A qualified, a separate pre-registration (spec below) would be judged by Amendment-3 wealth gates vs SPY buy-and-hold, with the equal-weight-9 and random top-3 books as controls. The 2018–2021 internal OOS would follow only with separate approval (XLC break handled there) |

**J — the portfolio-stage pre-registration:**
- monthly ranking;
- hold the **top 3 equal-weight**;
- trade at the next session's open;
- 100% invested; no cash in the base case;
- costs $7 per order plus 10 bps per side;
- optionally H021-B: hold cash instead of a top-3 sector whose own 6-month total return is below T-bills.

**STOP.** Awaiting your decisions. No sector signal, return, IC, portfolio or SPY comparison has been computed.
