# OD-CP1 — Outcome-driven discovery of offensive stock characteristics (owner D308)

**Status:** STOP. Exploratory research, completed. **No candidate passed the frozen Stage G rule, so no strategy was built (Stage H not triggered).**
**Decisions:** D308 (owner direction), D309 (implementation), D310 (result).
**Data windows:**
- 2010-01-04 → 2021-12-31 only.
- 1999–2009 was not read: the run starts in 2010 without warm-up, and filings before 2010 are dropped on load.
- The Holdout (2022-01-01 → 2026-08-31) stayed sealed: labels end at the 2021-11 review.

Nothing was purchased and nothing was built beyond plain-JSON research code.

**Artefacts:**

| Item | File |
|---|---|
| Frozen protocol | `research/od/OD1_protocol.md` (pinned in `qresearch.od1`) |
| Host and module | `strategies/X808_od1_outcomes/main.py`, `src/qresearch/lean/qr_od1.py` |
| SEC object | `rr/od1_sec_v1.json` (manifest in `research/od/`) |
| Run | E808-01 (backtest b486d51a…, LEAN 18203 default build, 337 s) |
| Aggregate lines | `research/od/E808-01_od1_lines.json.gz` |
| Frozen evaluation | `research/od/OD1_result_E808-01.json` |
| Descriptive tables | `research/od/OD1_tables_E808-01.json` |
| WIKI numeric study | `research/od/OD1_wiki_numeric.json` |
| WIKI consistency | `research/od/OD1_wiki_consistency.json` |
| Visual test | `research/od/OD1_visual_{manifest,predictions,result}.*` |

**Reading guide:**
- **EX** = 12-month total return minus SPY total return over the same dates, unless stated otherwise.
- **DISC** = decisions 2011-01 → 2016-12, with labels ending by the 2017-12 review.
- **STRESS** = decisions 2018-01 onward, with labels ending by 2021-11. STRESS is a later, already-exposed period, **not** independent validation.
- **W** = top 10% of EX within a review; **L** = bottom 10%; **M** = 40th–60th percentile.

---

## Summary

1. **Exceptional winners existed but were rare.** 1.1% of stock-months doubled within 12 months in DISC (4.8% in STRESS). About half the 12-month gain came from the top 10% of stocks.
2. **No feature or combination separated future winners from future losers in a way that was large, persistent and new.**
   - 47 features and 6 grids were scored against a candidate rule fixed before any forward return was seen. **0 passed.** No previously rejected feature passed either.
3. **The strongest effects are not usable.**
   - Volatility-type features predicted **both** tails (more winners *and* more losers), and their sign flipped between DISC and STRESS.
   - **Momentum did not work** in this universe and period: the 12-1 top decile minus bottom decile was +1.5 points over 12 months, t = 0.6.
4. **The best non-duplicate pattern was leverage change (DLEV).**
   - Statistically it was the most consistent: raw IC t = 3.5; positive in 8 of 10 years and 9 of 11 sectors; STRESS also positive.
   - Economically it is too small: the top decile beat SPY by only +2.8 points in 12 months, with a median of +0.65 points. It fails the size gate G1.
5. **Charts carried no detectable information.**
   - In the blinded test of 120 WIKI charts, winner-vs-loser calls were 29 of 45 = 64.4% (p = 0.036). The three-way accuracy of 35.8% is at chance.
   - Under the frozen rule (≥ 65% and p < 0.01) this means **visual information not present**.
6. **The candlestick features computed from WIKI showed nothing usable.**
   - All 8 have 12-month top-minus-bottom spreads below 2.5 points.
   - WIKI agrees with the QuantConnect universe returns (correlation 0.993), so this is not a data-source artefact.
7. **Answer to Q14: no.** There is no strategy worth considering for a Holdout test. This is consistent with FA-CP1 and with every earlier phase.

---

## Q1. How many companies and observations?

| Item | Value |
|---|---|
| Reviews (month-ends) | 131 (2011-01-31 → 2021-11-30) |
| Stock-month observations | **162,920** |
| Distinct firms (security identities) | **3,315** |
| Eligible per review (mean) | 944 (2011) → 1,675 (2021) |
| … of which SEC-repaired (UCR-1) | 95 (2011) → 21 (2021) a month; 7,566 repaired rows |
| … of which financials (fundamental features masked) | 166 → 304 a month |
| Technical features available | 98% of observations |
| Fundamental features available | 63% (2011) → 66–71% (2014–2021) |
| PIT / structural checks | pit_violations 0 (fundamental and external), identity duplicates 0, observations without a price row 0 |
| Identity refusals (SEC fundamentals not attached) | ambiguous QC ticker 1,683, contested prefix 899, multi-class 307 observation-months |

**Effective sample size.** Overlapping horizons and shared market shocks make independent evidence far smaller than the observation count:

| Horizon | DISC reviews | Independent windows (reviews ÷ h) |
|---|---|---|
| 3 months | 81 | ≈ 27 |
| 6 months | 78 | ≈ 13 |
| 12 months | 72 | ≈ 6 |
| 24 months | 60 | ≈ 2.5 |

All t-statistics below are Newey–West with lag h − 1 on per-review series. They are **descriptive**: 47 features × 4 horizons were examined.

## Q2. Horizons studied

3, 6, 12 and 24 months, for all valid observations, with labels ending by the 2021-11 review.
- DISC labels never use 2018+ prices.
- The 24-month DISC results rest on about 2.5 independent windows. Treat them as anecdotal.

## Q3. Distributions of exceptional winners, ordinary stocks and major losers

**12-month outcomes (equal weight per stock-month):**

| | DISC | STRESS |
|---|---|---|
| Observations / reviews / firms | 80,361 / 72 / 2,176 | 46,953 / 35 / 2,035 |
| Mean / median TR | +12.9% / +12.1% | +17.3% / +11.0% |
| Mean / median EX (vs SPY) | **+1.5% / +0.6%** | +1.2% / −3.8% |
| Share beating SPY | 51.1% | 45.2% |
| TR 1st / 10th / 90th / 99th percentile | −60% / −22% / +47% / +102% | −66% / −31% / +70% / +181% |
| Doubled (TR ≥ +100%) | **1.08%** | 4.78% |
| Severe loss (TR ≤ −30%) | 6.7% | 10.5% |
| Left the stream before 12 months (mostly acquisitions) | 3.4% (winners 5.5%, losers 0.8%) | 3.1% |
| Worst month-end drawdown within horizon: W / L / all | −3.2% / −40.2% / −11.7% | −5.9% / −47.1% / −17.6% |

**Wealth concentration (12 months, median over reviews, one dollar per stock).**
- The top 1% of stocks produced 8.7% of the summed TR; the top 5%, 29%; the top 10%, **47%**.
- 73% of stocks had a positive TR.
- At 24 months: top 10% = 48%, top 1% = 10.8%.

**Gain path of 12-month winners (W).**
- The single best month supplied a median 36% of the log gain (75th percentile: 47%).
- Winners rose in a median 9 of 12 months, and 80% rose in at least 8.
- **Winners were mostly gradual trends, not single jumps** — but the trend is only visible after the fact.

**Universe EX by decision year (12 months, mean / median):**

| Year | Mean EX | Median EX |
|---|---|---|
| 2011 | −1.6 | −1.7 |
| 2012 | +7.6 | +4.8 |
| 2013 | +1.9 | −0.4 |
| 2014 | +0.8 | +1.4 |
| 2015 | −1.3 | −0.3 |
| 2016 | +2.4 | +0.4 |
| 2017 | +0.4 | −3.4 |
| 2018 | −1.2 | −2.0 |
| 2019 | −5.9 | −11.3 |
| 2020 | +11.8 | +3.3 |

The median stock lagged SPY in 2017–2019: the mega-cap regime noted in LW-CP1.

## Q4. Technical patterns before exceptional outperformance

12-month EX in DISC.

| Feature (T) | Top decile EX | Bottom decile EX | Spread | Spread NW t | Partial IC t (h = 6) | STRESS spread | Duplicate of |
|---|---|---|---|---|---|---|---|
| MOM12_1 (12-1 momentum) | −0.6 | −2.1 | +1.5 | 0.6 | 0.5 | +4.9 | H002 / H019 |
| HI52 (near 52-week high) | +0.1 | −3.5 | +3.7 | 0.9 | 1.5 | **−11.3** | H003 |
| TREND200 | −1.0 | −2.3 | +1.3 | 0.4 | −0.3 | +1.1 | — |
| MA50_200 | −1.2 | −2.1 | +0.9 | 0.3 | −1.2 | +1.6 | — |
| MAXDD252 (shallow drawdown) | +2.0 | −3.2 | +5.2 | 0.9 | 1.9 | **−17.7** | — |
| VOL63 (high volatility) | −3.5 | +2.0 | −5.5 | −0.9 | **−3.2** | **+26.0** | H024 LOWVOL |
| BIGUP (many +5% days) | −2.2 | +2.7 | −4.9 | −0.8 | **−3.5** | +25.9 | — |
| BIGDN (many −5% days) | −2.6 | +2.7 | −5.3 | −1.0 | **−3.0** | +26.8 | — |
| DOWNMKT (strength on SPY-down days) | +0.2 | −2.1 | +2.3 | 0.4 | 1.1 | **−22.3** | — |
| BREAKOUT (new high on volume; flag) | +0.8 vs +1.6 | | −0.8 | −1.1 | 0.0 | +0.1 | H006 |
| BASE (tight base; flag) | +1.9 vs +1.5 | | +0.4 | 0.0 | 0.4 | −4.1 | — |
| RANGECOMP | +0.9 | +1.3 | −0.3 | −0.5 | 2.1 | −1.2 | — |
| ID (smooth momentum) | +1.8 | +0.7 | +1.1 | 0.6 | 2.5 | −2.9 | H019 S2 |
| UPDV63 / ACCUM63 / TRENDAGE / EXT50 / RS6 / SECREL6 | all within ±1.5 | | | \|t\| ≤ 0.9 | \|t\| ≤ 0.9 | | — |

The remaining technical features are in the JSON tables, with spreads within ±2.6 points and \|spread t\| ≤ 1.3 (excluding the degenerate MONTHSUP decile).

**Answer:**
- No technical pattern preceded exceptional outperformance in a way that was large, positive and stable.
- The trend / leadership features favoured by technical practice (momentum, 52-week high, trend age, 50 / 200 cross, relative strength) produced **1–4-point 12-month spreads with t below 1**.
- The only partial-IC |t| ≥ 3 belong to the **volatility family** (VOL63, BIGUP, BIGDN). In DISC their sign is *negative* (calm stocks did better). In STRESS the sign reversed with +26-point spreads (2020–2021 speculative rally).

## Q5. Fundamental characteristics before exceptional outperformance

All values are as filed in the original 10-K / 10-Q, known before the decision date. Financials are excluded.

| Feature (F) | Top decile EX | Bottom decile EX | Spread | Spread NW t | Raw IC t (h = 6) | Partial IC t (h = 6) | STRESS spread | Duplicate of |
|---|---|---|---|---|---|---|---|---|
| REVYOY (revenue growth) | −1.9 | +0.1 | −2.0 | −0.8 | −0.9 | −0.3 | +9.2 | — |
| REVACCEL | −0.4 | −1.1 | +0.7 | 0.9 | 2.6 | 2.9 | −1.1 | H029 F1 |
| NICHG (net income change) | −1.2 | +2.5 | −3.7 | −3.0 | −0.5 | 0.2 | −6.8 | — |
| ROA | +1.3 | −1.0 | +2.3 | 0.3 | 0.9 | 0.1 | −3.6 | — |
| DROA | −0.9 | −1.1 | +0.3 | −0.2 | −1.3 | −1.3 | +0.7 | OC-2 / H029 F5 |
| GPA | −1.4 | +0.5 | −1.9 | −0.3 | 0.3 | 0.6 | +3.7 | H016 |
| AG (asset growth) | −0.7 | +0.6 | −1.3 | −0.5 | −1.2 | −1.0 | +12.5 | H024 AG |
| ACCR (accruals) | −0.2 | −2.9 | +2.7 | 1.2 | 1.9 | −0.2 | −6.0 | H024 ACC |
| **DLEV (leverage change)** | **+2.8** | −1.1 | **+3.9** | **3.1** | **3.5** | **2.2** | **+1.9** | — |
| REPURCH (net buyback) | +3.8 | −1.5 | +5.3 | 3.0 | 5.1 | 2.5 | **−8.2** | H032 |
| EY / SP / BM (valuation) | +0.7 / +1.3 / −1.7 | −1.4 / +4.0 / +4.0 | +2.1 / −2.8 / −5.7 | \|t\| ≤ 1.6 | \|t\| ≤ 1.5 | \|t\| ≤ 0.7 | −10.0 / −13.3 / −16.0 | H024 |
| OCFTA, GMCHG, REVCONS, NICONS | within ±2.2 | | | ≤ 1.2 | | | | |

**Answer:**
- Profitability, growth and valuation levels did not precede outperformance in this universe (2011–2017).
- Two features show consistent small positive ranks: **REPURCH** (H032: already rejected as a portfolio; it reverses in STRESS) and **DLEV**.
- DLEV (rising liabilities / assets in the latest 10-K) is the most persistent pattern in the study:
  - spread t = 3.1;
  - top beats bottom in 8 of 10 years and 9 of 11 sectors;
  - STRESS spread +1.9;
  - partial IC t = 2.2 after momentum, size, beta, volatility, sector and ROA.
- But DLEV's top decile beat SPY by only +2.8 points in 12 months (99%-trimmed +0.9, median +0.65). Most of its mean comes from a few large winners.
- DLEV has no prior economic rationale in our record (the literature associates leverage *increases* with *lower* returns). Its result was not anticipated. It is a single data-mined feature among 47.

## Q6. Did combinations improve discrimination?

Six pre-registered tercile × tercile grids (12-month EX, DISC):

| Grid | Best cell | n | EX | STRESS EX | Increment vs marginals | Cell NW t (h = 6) | Gates passed |
|---|---|---|---|---|---|---|---|
| D1 MOM12_1 × REVACCEL | mid × mid | 6,391 | +4.4 | +0.4 | +1.0 | 2.9 | G1, G2 |
| D2 TREND200 × DROA | mid × mid | 6,875 | +3.8 | −1.1 | +0.8 | 2.3 | G2 |
| D3 MOM6_1 × NICHG | mid × mid | 7,350 | +3.1 | −0.5 | +0.5 | 1.6 | — |
| D4 HI52 × OCFTA | mid × mid | 6,531 | +3.7 | −0.4 | +1.1 | 2.7 | G2 |
| D5 BREAKOUT × REVYOY | yes × mid | 626 | +3.5 | +0.7 | +0.0 | 0.6 | — |
| D6 RS6 × REVCONS | high × 2 quarters | 1,426 | +4.4 | +2.4 | +1.0 | 1.3 | G1 |

**Answer: no.**
- In every grid the best cell was the **middle** of both characteristics, not "strong technicals + improving business".
- The pattern is the same as in Q7: extreme values on either axis hold more losers as well as more winners, so the middle avoids both tails.
- The increment over the row / column marginals is at most +1.1 points, against the +2-point requirement (G6).
- The middle-cell advantage disappears in STRESS.
- The theory-driven corners also failed:
  - strong momentum + accelerating revenue (D1 cell 22): +2.0 DISC;
  - near-high + strong cash flow (D4 22): +1.5;
  - breakout + revenue growth (D5 12): +1.5.

## Q7. How common were the same features among unsuccessful stocks?

Each cell gives the share of each 12-month outcome group (DISC) whose feature value sat in the cross-section's **top quintile**. Without information, all three would be 20%.

| Feature | Winners (W) | Ordinary (M) | Losers (L) | Reading |
|---|---|---|---|---|
| VOL63 high | 30.9% | 12.1% | **46.6%** | marks *both* tails; losers more |
| BIGUP / BIGDN high | 30.4 / 29.7% | 12.4 / 12.3% | 44.8 / 45.9% | same |
| BETA high | 25.6% | 15.3% | 33.8% | same |
| REVYOY high | 24.2% | 15.5% | 35.9% | fast growers: more losers than winners |
| AG high | 25.5% | 16.5% | 32.3% | same |
| MOM12_1 high | 22.9% | 17.7% | 26.0% | leaders: slightly more losers than winners |
| HI52 high (near high) | 14.3% | 23.7% | 13.6% | marks the calm middle |
| MAXDD252 high (shallow drawdown) | 12.2% | 25.9% | 7.8% | calm middle; fewer losers |
| SIZE high | 13.6% | 24.1% | 11.2% | large caps cluster in the middle |
| REPURCH high | 21.5% | 21.0% | 14.1% | fewer losers, not more winners |
| DLEV high | 25.4% | 19.0% | 23.2% | barely different |

**Answer:** almost every characteristic that is frequent among eventual winners is **as frequent or more frequent among eventual losers**.
- High volatility, fast revenue growth, high asset growth, high beta and strong momentum all mark *dispersion*, not direction.
- Measured on its own top-decile members, such a feature yields more losers than winners. For example:
  - VOL63 top decile: 16.6% end up W and 28.3% end up L;
  - REVYOY top decile: 14.9% W and 21.3% L.

## Q8. What was explained by momentum, size, sector or market conditions?

- **Momentum** explained nothing, because it did not work here (MOM12_1, MOM6_1, RS6, SECREL6 and the trend features all have |spread t| < 0.7).
- **Volatility and beta** explain the tail features: BIGUP, BIGDN, MAXDD252, DOWNMKT, REVYOY and AG are largely volatility in other forms. After controls, their direction in DISC is low-risk-better, which is the H024 / H027 / H028 LOWVOL finding again.
- **Market regime** reverses them: STRESS 2018–2021 spreads are
  - VOL63 +26.0, BETA +26.2, LO52 +16.0;
  - BM −16.0 and SP −13.3 (value lost);
  - DOWNMKT −22.3, MAXDD252 −17.7.
  The sign of most risk-related features is decided by the regime, not by the stock.
- **Size:** the largest-cap decile beat SPY by +2.6 points with a bottom decile of +1.8. Large caps held fewer of both winners and losers.
- **Sector:** controlled in every partial IC by FF12 dummies. Valuation and accrual features lose most of their raw signal after controls (EY raw t 1.5 → partial 0.7; ACCR 1.9 → −0.2).
- **Survivors:** see Q13.

## Q9. Stable across years and sectors?

Counting the years (of 10, 2011–2020 decision years) and non-financial sectors (of 11) in which the top decile beat the bottom decile:

| Feature | Years | Sectors |
|---|---|---|
| **DLEV** | 8 | 9 |
| ACCUM63 | 8 | 7 |
| REPURCH | 7 | 5 |
| MOM12_1 | 7 | 6 |
| TREND200 | 7 | 8 |
| SIZE | 7 | 5 |
| NICHG | 0 (reliably negative) | 1 |
| BM | 3 | 2 |
| HI52 | 6 | 1 |
| DOWNMKT | 4 | 1 |
| MONTHSUP | 0 | 0 (degenerate; see Q10) |

**Answer:**
- Only DLEV is consistent across both years and sectors, and it is economically small.
- NICHG is consistently *negative*: the largest earnings increases had the worst subsequent EX (−3.7-point spread, t −3.0, 0 of 10 years positive). This fits post-surge mean reversion. The bottom decile beat SPY by +2.5 points, too little for G1 even read in reverse.

## Q10. Strongest apparent false positives

| Pattern | In discovery (DISC) | Later (STRESS) / caveat |
|---|---|---|
| Shallow 12-month drawdown (MAXDD252 top decile) | +2.0 EX; spread +5.2 | −17.7 spread |
| Near 52-week high (HI52) | spread +3.7 | −11.3 |
| Strength on SPY-down days (DOWNMKT) | +2.3 | −22.3 |
| Net repurchase (REPURCH) | +3.8 EX, raw IC t 5.1, the strongest raw statistic of the study | −8.2; H032 already rejected as a Top-15 portfolio |
| Low volatility (VOL63 bottom decile) | +2.0, partial t 3.2 | +26-point reversal |
| Best grid cell D1 (mid momentum × mid revenue acceleration) | +4.4, t 2.9 | +0.4 |
| MONTHSUP decile 1 | +13.1% EX | n = 18 (degenerate decile); the frozen rule's "best group" picked it; gates reject it |
| Visual "likely outperform" calls (46 of 120) | 18 eventual W | 18 ordinary, 10 eventual losers |

## Q11. Genuinely incremental predictive mechanisms?

**No.**
- The frozen rule G1–G6 (large, positive, robust and persistent; not a prior duplicate; incremental) passed **0 of 47 features and 0 of 6 grids**.
- No duplicate passed G1–G5 either, so nothing was even re-observed.

Closest misses:

| Candidate | Gates passed | Failed |
|---|---|---|
| DLEV | G2–G6 | G1: top decile +2.8 < +4; trimmed +0.9 < +2 |
| GPA (H016 duplicate) | G1, G3, G4, G5 | G2: t 0.6; also G6 (duplicate) |
| SP | G3–G6 | G1, G2 |
| REPURCH (duplicate) | G1, G2, G4 | G3, G5, G6 |

**WIKI candlestick study** (2011–2016 decisions; 43,693 stock-months; 1,049 registrants; source consistency with QuantConnect: **CONSISTENT**, 12-month correlation 0.993, mean |difference| 0.96 points):

| Feature | 12-month top − bottom EX | Partial IC NW t |
|---|---|---|
| K1 CLV21 (close location) | −1.6 | −0.7 |
| K2 GAPUP63 | −0.8 | 0.3 |
| K3 GAPDN63 | −1.2 | 0.2 |
| K4 BIGBODY63 | −1.6 | 0.3 |
| K5 UPWICK21 | +1.5 | 1.0 |
| K6 LOWICK21 | −2.2 | **−3.4** |
| K7 ATRPCT21 | −1.5 | −1.6 |
| K8 ATRCHG | −1.3 | 1.0 |

- LOWICK21 (long lower wicks → slightly worse returns) is the only |t| > 2.
- Its spread is −2.2 points. It is one of 8 features on overlapping 12-month windows (≈ 6 independent years) and has no frozen hypothesis behind it. It is not a candidate.

**Blinded visual test:**
- 120 charts (40 W, 40 L, 40 M), predictions committed (101bf58) before unblinding.
- W-vs-L hit rate: 29 / 45 = 64.4%, binomial p = 0.036.
- Three-way accuracy: 35.8% (chance 33.3%, p = 0.31).
- Frozen rule result: **visual information not present**.
- The weak tilt that exists follows "near highs, above both moving averages" (tagged on 45% of W, 27.5% of L, 40% of M), i.e. momentum, which Q4 shows did not pay at population level.

## Q12. Strategy results

**No strategy was implemented.** Stage H runs only if a non-duplicate candidate passes G1–G5 (protocol §7). None did, so no portfolio was built and no return is reported against SPY, the universe baseline or a matched control.

## Q13. Remaining biases and data limitations

1. **Universe gap:** RR6 INCONCLUSIVE.
   - The repaired universe may still miss up to about 3–4% of ≥ $2B stock-months a year, mostly later-disappearing names.
   - The DISC loss rates are therefore slightly optimistic, and loser-heavy features slightly understated.
2. **Exposed data:** 2010–2021 was used by every earlier phase. STRESS is a later window of the same exposed data, **not independent validation**. No 1999–2009 window exists on QuantConnect (RR3).
3. **Multiple comparisons:**
   - 47 features + 6 grids + 8 WIKI features + 1 visual test, each at 4 horizons.
   - About 2–3 nominal |t| > 2 would be expected by chance per horizon. We observed 8 partial-IC |t| ≥ 2 at h = 6, five of them in two families (volatility; buyback / leverage).
   - Effective sample: ≈ 6 independent 12-month windows in DISC.
4. **Labels:**
   - Monthly checkpoints, so the MAE misses intramonth lows.
   - Delisted securities take their last real close; cash or acquisition proceeds after that are not tracked, which understates acquired winners by their deal premium if paid after the last bar.
   - SPY = harness total-return index.
5. **Fundamentals:**
   - As-filed 10-K / 10-Q values only; SEC tag coverage 63–71% of observations; financials excluded.
   - Identity refusals (2,889 observation-months) drop ambiguous tickers.
   - 2011 coverage is lower because the as-filed history starts in 2010.
6. **No OHLC on QuantConnect's Fundamental stream:** candlestick features come only from WIKI (2011–2016, MATCHED identities; adjustment-defect tickers and windows excluded; composition audit INSUFFICIENT, TT-CP1c R1). The source-consistency check passed, but WIKI covers a narrower frame (median 616 names a month vs ~1,250).
7. **The visual test** was one rater (Claude) on 120 charts, with the rater's prior shaped by earlier phases. A 64% hit rate on 45 calls has a wide interval (≈ 49–78%).
8. **Equal-weighted statistics:** a cap-weighted SPY benchmark against equal-weight stock-months overweights small large-caps. The 2017–2019 mega-cap regime depresses median EX.

## Q14. One promising strategy worth a future Holdout test?

**No.**
- Nothing passed the frozen discovery rule.
- The best non-duplicate pattern (DLEV) is economically too small: about +2.8 points in 12 months for the top decile, less than SPY tracking costs plus trading costs for a 15-name book (≈ 3–4 points a year, H032 / SA-CP1). It also has no prior mechanism.
- The Holdout remains sealed. Opening it would need a separate owner decision. I do not recommend it: there is no candidate to test.

**What this study adds to earlier phases:**
- It looked at outcomes first, as the owner asked. Its main empirical lesson is that, in US ≥ $2B stocks during 2011–2021, the visible markers of future big winners (volatility, growth, momentum, leadership) were **shared with future big losers**.
- The parts of the cross-section that did slightly better were the *calm, middle* parts: low volatility, shallow drawdowns, buybacks. This is the defensive LOWVOL pattern already captured (and rejected for robustness) in H026–H028, and it reversed in 2020–2021.
- An offensive stock-selection rule that reliably picks winners did not emerge from this data.

**Recommendation:**
- Close OD-1 as **NO CANDIDATE — NO INCREMENTAL PREDICTIVE MECHANISM FOUND**.
- Keep SPY as the offensive baseline.
- Further stock-selection research needs independent evidence first (licensed pre-2010 point-in-time data, or a frozen forward record). Each would be a separate owner decision.

**STOPPED awaiting the owner.**
