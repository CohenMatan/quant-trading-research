# H015 literature review: moving-average trend filters, diversification and stock selection

- **Purpose:** the external evidence behind the H015 pre-registration proposal (`docs/checkpoints/P2_CP2_H015_preregistration_proposal.md`).
- **Written:** 2026-10-01, before any H015 rule was implemented or tested.

**How to read the citations.**
- References are cited **from memory**. They must be checked against the originals before any number is quoted, so no specific coefficient is claimed here.
- Work published before 2010 cannot contain look-ahead about our development period.
- Later work is used only as a **caution**, never to choose a rule.
- §4 lists separately what we learned from our own H014 runs. That is **not** external evidence.

## 1. Moving-average trend rules: what the external evidence says

| Evidence | Published | What it says | Use for H015 |
|---|---|---|---|
| Brock, Lakonishok & LeBaron (1992, *J. Finance*) | pre-2010 | Simple MA rules (1/50, 1/150, 1/200-day, with and without a band) had predictive power on the Dow Jones index, 1897–1986. Returns after "buy" signals were higher and less volatile than after "sell" signals. | The 200-day average is a standard window with the longest documented history, not a value fitted by us. |
| Siegel, *Stocks for the Long Run* (1st ed. 1994; later editions) | pre-2010 | A 200-day MA timing rule on the Dow reduced volatility and the largest drawdowns. After costs, returns were similar to buy-and-hold. | The expected benefit is **risk reduction, not higher return**. |
| Faber (2007, *J. Wealth Management*) | pre-2010 | Holding an asset class only while its month-end price is above its 10-month SMA (≈ 200 days), checked monthly, kept roughly equity-like returns with much smaller drawdowns, mainly by avoiding long bear markets (1973–74, 2000–02, 2008). | Supports a **monthly check** of price vs a ≈ 200-day average, with low turnover. **Practitioner source, asset-class level.** |
| Sullivan, Timmermann & White (1999, *J. Finance*) | pre-2010 | After correcting for data snooping across thousands of rules, the best technical rules **stopped** outperforming after 1986. | Rules must be fixed before testing. Expect a small effect. |
| Park & Irwin (2007, *J. Economic Surveys*) | pre-2010 | A survey: many reported profits; much of the evidence suffers from snooping, ex-post selection and ignored costs. Profits weaken in later samples. | The same caution. |
| Moskowitz, Ooi & Pedersen (2012, *JFE*) | 2012 (data before our period) | Time-series momentum: an asset's own 12-month return predicts its next-month sign, across futures markets. | A conceptual cousin of "price above its long average". **Asset level, not single stocks. Caution only.** |
| Han, Yang & Zhou (2013, *JFQA*) | 2013 | MA timing profits on portfolios sorted by volatility were concentrated in the **high-volatility (often small)** stocks, and small for low-volatility, large stocks. | **Caution:** in a ≥ $2B universe, any MA effect should be weak. |
| Hurst, Ooi & Pedersen (2017, *J. Portfolio Management*), "A century of evidence on trend-following" | after 2017 | Trend following worked across a century of futures/asset-class data, with its value concentrated in prolonged bear markets. | **Caution only** (post-2017 publication). |
| Zakamulin (2014 onward; 2017 book *Market Timing with Moving Averages*) | after 2010 | A critical review: out-of-sample MA timing gains are much smaller than in-sample, and concentrated in a few severe bear markets. In sharp V-shaped recoveries the rule lags. | **Caution only.** Expect little or no edge in a period without a long bear market. |
| Bajgrowicz & Scaillet (2012, *JFE*) | 2012 | After false-discovery control and realistic costs, technical rules on the Dow showed no persistent value in recent decades. | **Caution only.** |

**Summary of the external evidence.**
- The 200-day average and a monthly check are standard, pre-2010, widely studied choices. They are not something we fit.
- The documented benefit is mostly **lower drawdowns at the index or asset-class level**, from moving to cash in long bear markets.
- Evidence for **single large stocks** is thinner. Han, Yang & Zhou suggest the effect is weakest in exactly the large, low-volatility stocks that make up our universe.

## 2. A structural point the literature does not settle: stock-level filtering is not market timing

- **Index-level rules move the whole portfolio to cash.** Faber and Siegel describe this.
- **A stock-level rule with 15 slots does something different.** It **selects** among roughly 700 qualifying stocks (on a typical 2010–2021 day, most of a ≈ 1,000-stock universe is above its 200-day average).
  - It holds cash only if fewer than 15 stocks qualify, which is rare even in sell-offs.
  - So the book stays ≈ 93% invested. It is a **cross-sectional** bet ("stocks above their long average beat those below") plus a **trend-failure exit**, not a timing bet.
- **The nearest external evidence for that cross-sectional claim** is the momentum literature (Jegadeesh & Titman 1993; Grinblatt & Moskowitz 2004 on trend consistency; George & Hwang 2004, "52-week high"). Price above a long average is a crude, binary form of intermediate-horizon momentum.
- **That evidence is about ranking.** The extremes (top-decile winners) earn the premium. A binary filter that keeps about 70% of the universe should capture only a small part of it.
- **Expectation: a small effect.**

## 3. Stock selection and diversification

| Evidence | Published | What it says | Use for H015 |
|---|---|---|---|
| Evans & Archer (1968, *J. Finance*); Statman (1987, *JFQA*) | pre-2010 | Most diversifiable risk is removed with about 10–20 stocks (Evans & Archer). Statman argued at least 30–40 are needed for a borrowing investor. | At 15 stocks, idiosyncratic noise remains material. This motivates the seed replicates and a seed-averaged estimate. |
| DeMiguel, Garlappi & Uppal (2009, *RFS*) | pre-2010 | Naive 1/N weighting is hard to beat out of sample. | Supports **equal slot weights**, not optimised weights. |
| Plyakha, Uppal & Vilkov (working paper from 2012) | after 2010 | Equal-weighted portfolios of index stocks earn higher returns than value-weighted ones (size and rebalancing effects). | **Caution:** selecting by market cap tilts away from EW. We also already know that large caps (SPY) beat EW over 2010–2021 (our own benchmarks E900-07 and E901-07), so a cap-based selection would load on an **observed** outcome. |
| Jegadeesh & Titman (1993); Novy-Marx (2012) | pre-2010 / 2012 | Ranking by past returns carries the momentum premium. | The momentum-ranking route is **not** reused: H014 used 12-1 ranking (owner caution), and ranking is not the hypothesis here. |

## 4. What we learned from H014 (our own development data, not external evidence)

These are facts from already-observed 2010–2021 books (`research/phase2/P2_h015_feasibility.json`). They inform **feasibility and disclosure only**. No H015 rule is chosen to match them.

- **Random choice among uptrend stocks did not beat EW by much.** The H014 random-uptrend controls (12 slots, Close > MA200 and MA50 > MA200, exits on Close < MA200) had Sharpe differences to EW of:
  - −0.12, +0.20 and −0.07 with the MA200 exit plus horizon roll;
  - +0.01, +0.04 and +0.12 with a 126-session cap.
  - The median is well below the +0.25 margin.
- **Momentum-ranked uptrend books were the worst** (−0.21 and −0.42 vs EW).
- **Costs were low:** 0.5–0.9% a year for the random-uptrend books, with average holds of 70–110 sessions.
- **The 12-stock books track EW with only ≈ 0.78 daily correlation,** and seed-to-seed dispersion of Sharpe was large (≈ 0.06–0.18 across 3 seeds). Both make a 12-year test noisy.

## 5. Implications for the H015 design

1. **Trend rule:** one condition, price above its 200-day average. This is the longest-documented, most standard form (Brock et al.; Siegel; Faber's 10-month equivalent).
   - The MA50 > MA200 "golden cross" state is a convention without separate evidence, so it is not included.
2. **Review cadence:** monthly (Faber), to cut whipsaw and turnover. Signals use the same calendar as the EW benchmark (first close of the month).
3. **Selection:** must avoid known tilts.
   - Momentum ranking is excluded (not the hypothesis; owner caution).
   - Market-cap ranking is excluded (it loads on an outcome we have already observed).
   - **Seeded random selection among qualifying stocks** is the factor-neutral way to fill 15 slots from the trend population.
4. **Expected effect:** small. The external evidence (Han, Yang & Zhou; Zakamulin; Bajgrowicz & Scaillet) and our own observed books point the same way. The proposal must say so plainly and size the test accordingly.
