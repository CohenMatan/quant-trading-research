# Post-2010 survivorship gap (D043) — mandatory disclosure for every research report

| Field | Value |
|---|---|
| Status | **Complete.** Counts: E953 estimate (§2) and an independent X954 measurement (§2a). Direction and size of the return bias: measured by E954-01 (§5). |
| Sources | E953-01/02 (size-proxy runs); a hand classification of 720 sampled securities (`size_proxy/fp_ticker_classification.csv`, evaluation-only); **E954-01** (X954, 2010–2021, LEAN 18131); tables in `survivorship_gap_X954_*.csv` |

## 1. The limitation in one paragraph

- QuantConnect's Morningstar dataset has **no fundamental data for securities that later stopped trading**, even for years in which they traded normally and were large. Examples are Time Warner, Heinz, Sears, JCPenney, SanDisk, Genzyme and Alcoa (before its 2016 split).
- Because the universe rule needs a point-in-time MarketCap, such companies can **never** enter our ≥ $2B universe.
- Their **prices are present**: the price data is survivorship-free. Only the *eligibility* is missing.
- So strategies can never select them, and benchmarks never contain them.

## 2. Estimated share of missing eligible companies, by year

**Method.**

- Start from securities that trade actively (price ≥ $5, 63-day average dollar volume ≥ $20M) and have **no** fundamentals, excluding ETF-like "return twins".
- Multiply by the share of them that are US common stocks (hand-classified sample of 60 per June) and by the chance that such a stock is ≥ $2B (calibrated on names whose type is known).
- Divide by that calibration's recall, to include missing names that trade less than $20M per day.

| Year | Reference universe (names/month) | Liquid no-fundamentals candidates | …of which US common stock | **Estimated missing ≥ $2B companies** | **Missing share of the true universe** |
|---|---|---|---|---|---|
| 2010 | 687 | 239 | 55% | 130 | **15.9%** |
| 2011 | 775 | 247 | 47% | 119 | **13.3%** |
| 2012 | 788 | 217 | 57% | 128 | **14.0%** |
| 2013 | 901 | 209 | 48% | 112 | **11.1%** |
| 2014 | 1,022 | 238 | 40% | 105 | **9.3%** |
| 2015 | 1,055 | 203 | 40% | 86 | **7.6%** |
| 2016 | 1,022 | 158 | 30% | 50 | **4.6%** |
| 2017 | 1,116 | 160 | 30% | 52 | **4.4%** |
| 2018 | 1,185 | 173 | 23% | 43 | **3.5%** |
| 2019 | 1,183 | 155 | 32% | 53 | **4.3%** |
| 2020 | 1,189 | 145 | 27% | 39 | **3.2%** |
| 2021 | 1,503 | 205 | 8% | 18 | **1.2%** |

By period:

| Period | Missing share of the true universe |
|---|---|
| **IS 2010–2017** | about 9–16% early, about 4–5% late; **about 10% on average** |
| **VAL 2018–2021** | about 1–4% |
| **HOLDOUT** | expected ≤ 1% (not measured; the holdout is locked) |

The gap shrinks over time because the missing securities are those that ended before QuantConnect's data snapshot, and the closer a year is to today, the fewer of its companies have ended since.

**Precision of these estimates.**

- Each year's US-common share comes from 60 sampled names, which gives about ±6 percentage points (1 s.d.). Each yearly estimate is therefore good to roughly ±15–20% of its value.
- The reference counts come from the E953 runs, which used the pre-D030 share-class rule. The current (D030) universe is larger by roughly 130–240 names per month, so the percentages above are slight **over**-estimates.
- The type classification is by hand from tickers. It is evaluation-only and never used by any rule.

## 2a. Independent measurement (X954, E954-01), using the current D030 universe rule

**Method.**

- Every month, count the securities with **no** fundamentals that trade actively (price ≥ $5, ADV20 ≥ $5M, 63 days of history) and are not ETF-like return twins, by 63-day dollar-volume bucket.
- Multiply by the share of **known** US common stocks in the same bucket that are ≥ $2B (measured the same month), then by the hand-classified US-common share.
- The reference is the harness's eligible universe under the corrected D030 rule, which is larger than E953's. That makes the percentages lower.

| Year | Reference names/month | Liquid no-fundamentals candidates | …likely ≥ $2B | US-common share | **Estimated missing ≥ $2B** | **Missing share** |
|---|---|---|---|---|---|---|
| 2010 | 765 | 447 | 229 | 55% | 126 | **14.1%** |
| 2011 | 866 | 453 | 242 | 47% | 113 | **11.5%** |
| 2012 | 885 | 393 | 222 | 57% | 126 | **12.4%** |
| 2013 | 1,021 | 436 | 248 | 48% | 120 | **10.5%** |
| 2014 | 1,165 | 461 | 263 | 40% | 105 | **8.3%** |
| 2015 | 1,208 | 406 | 218 | 40% | 87 | **6.7%** |
| 2016 | 1,168 | 345 | 177 | 30% | 53 | **4.4%** |
| 2017 | 1,274 | 392 | 216 | 30% | 65 | **4.8%** |
| 2018 | 1,347 | 401 | 220 | 23% | 51 | **3.7%** |
| 2019 | 1,326 | 344 | 193 | 32% | 61 | **4.4%** |
| 2020 | 1,312 | 337 | 168 | 27% | 45 | **3.3%** |
| 2021 | 1,649 | 438 | 243 | 8% | 20 | **1.2%** |

The two independent estimates (§2 and §2a) agree within about 2 percentage points in every year.

## 3. Examples (large US companies absent from the universe while they traded)

| Company | Missing while trading (examples of years) | How it ended |
|---|---|---|
| Time Warner (TWX) | 2010–2018 | acquired by AT&T (2018) |
| H.J. Heinz (HNZ) | 2010–2013 | acquired by Berkshire/3G (2013) |
| Precision Castparts (PCP) | 2010–2015 | acquired by Berkshire (2016) |
| Genzyme (GENZ) | 2010–2011 | acquired by Sanofi (2011) |
| SanDisk (SNDK) | 2010–2016 | acquired by Western Digital (2016) |
| DuPont (DD, old) | 2010–2017 | merged with Dow (2017) |
| Sigma-Aldrich (SIAL) | 2015 | acquired by Merck KGaA |
| BB&T (BBT) | 2010–2019 | merged into Truist (2019) |
| Alcoa (AA, old) | 2010–2016 | split into Arconic/Alcoa (2016) |
| Sears Holdings (SHLD) | 2010–2017 | bankruptcy (2018) |
| JCPenney (JCP) | 2010–2019 | bankruptcy (2020) |
| Chesapeake Energy (CHK, old) | 2010–2019 | bankruptcy (2020) |
| Frontier Communications (FTR) | 2015 | bankruptcy (2020) |
| Weatherford (WFT) | 2010–2018 | bankruptcy (2019) |
| Hertz (HTZ, old) | 2019 | bankruptcy (2020) |

Fuller lists are in `docs/data/size_proxy/E953-0*_fp_nofund_sample.csv`, with the classification in `size_proxy/fp_ticker_classification.csv`.

## 4. Do the missing securities appear in the price data?

**Yes.**

- Every name above was found *through* the survivorship-free price universe: it had daily prices and volumes in the months counted.
- E952 showed that the engine also handles their delistings. It force-sold Enron, WorldCom, Bear Stearns and Lehman positions at their final prices.
- The gap is only in **eligibility**, which depends on MarketCap.

## 5. Direction and size of the bias (measured, E954-01)

**Method.**

- Every month from 2010 to 2017 (**IS years only**; no VAL or HOLDOUT returns were computed), form equal-weight groups of the no-fundamentals candidates, split by how each security later ended.
- A security **ended** if its last price in the data is before 2021-11-01. It is **distress** if that last price was below $5, or at least 50% below its level 126 trading days earlier. Otherwise it is **other** (typically an acquisition, merger or reorganisation).
- Measure each group's next-month return and compare it with the reference universe.

| Group (2010–2017) | Average names | Annualised mean return | Difference vs universe | t-stat |
|---|---|---|---|---|
| Reference universe (MarketCap ≥ $2B) | ~1,000 | **+11.3%** | — | — |
| Later ended in **distress** | 72 | **−28.4%** | **−39.7 points** | **−6.4** |
| Later ended **otherwise** (mergers etc.) | 121 | +7.5% | −3.8 points | −2.2 |
| Still trading at the end (not interpretable: mostly ETFs and ADRs) | 224 | +2.8% | −8.4 points | −4.0 |

Annual detail (per cent per year):

| Year | Universe | Later distress | Later other |
|---|---|---|---|
| 2010 | 6.2 | −16.4 | 2.8 |
| 2011 | 11.9 | −15.5 | 5.1 |
| 2012 | 11.5 | −27.0 | 11.2 |
| 2013 | 23.9 | 3.0 | 26.7 |
| 2014 | 11.6 | −41.3 | 3.2 |
| 2015 | −5.5 | −78.4 | −3.7 |
| 2016 | 19.0 | −0.1 | 6.6 |
| 2017 | 11.6 | −51.4 | 8.0 |

**Conclusion: the bias is OPTIMISTIC (upward).**

- The missing companies underperformed the universe. The takeover premium of the later-acquired ones did not offset the losses of the later-distressed ones.
- **Implied effect on the equal-weight universe return, IS 2010–2017:** each year's missing share × (universe return − the missing names' ended-group return).
  - **+0.6 to +2.3 percentage points per year, average +1.4.**
  - This is the amount by which our universe *overstates* a survivorship-complete ≥ $2B universe.
  - Per-year detail: `survivorship_gap_X954_implied_bias.csv`.
- **VAL 2018–2021:** the missing share is 1–4% and the distressed share falls to 0–7%, so the effect should be well under 1 point per year. It was not measured with returns, because VAL is out-of-sample.

**Who is affected most.**

- Strategies that **buy stocks after declines** (short-term reversal H001, pullbacks H004) are the most exposed. The missing distressed companies are exactly the falling stocks such rules would have bought.
- Strategies that hold strong or stable names (momentum H002, 52-week high H003, low volatility H005) are less exposed.
- **The gates partly cancel the bias.** Every gate compares a strategy with the equal-weight benchmark built on the same universe, so the benchmark is flattered by roughly the same +1.4 points.
- The residual risk is that a dip-buying strategy is flattered *more* than the benchmark.

**Caveats.**

- **"Distress" is defined by the final price.** A few collapsed leveraged or volatility ETNs (e.g. XIV, UGAZ) fall into that group despite the twin filter (see `survivorship_gap_X954_examples.txt`). That makes the distress figure somewhat more negative than for companies alone.
- **The US-common share comes from 60-name samples per year**, about ±6 points.
- **The "still trading" group mixes ETFs, ADRs and some surviving companies without fundamentals**, and is not used in the bias estimate.

## 6. What every research report must state

- The universe omits about **5–14% of eligible companies in IS** (about 1–4% in VAL), mostly companies that later ended.
- This flatters universe-level returns by about **+1.4 points per year in IS** (range 0.6–2.3), and **flatters dip-buying rules the most**.
- Gates are relative to an equal-weight benchmark built on the same universe, which cancels much, but not all, of the effect.
## Update 2026-10-01 (D111): partial repair from SEC data

- A dated, **opt-in** SEC correction layer (`universe.sec_corrections`) repairs 163 securities that QuantConnect prices without fundamentals.
- It uses SEC cover-page share counts × raw price, with live split handling, and statement totals as first filed.
- 108 of them are eligible in at least one month.
- **Estimated missing share, before → after the repair:**

  | Year | Before | After |
  |---|---|---|
  | 2010 | 14.1% | 11.4% |
  | 2011 | 11.5% | 5.9% |
  | 2012 | 12.4% | 8.0% |
  | 2013 | 10.5% | 6.8% |
  | 2014 | 8.3% | 5.1% |
  | 2015 | 6.7% | 4.2% |
  | 2016 | 4.4% | 2.7% |
  | 2017 | 4.8% | 3.3% |
  | 2018 | 3.7% | 2.2% |
  | 2019 | 4.4% | 3.3% |
  | 2020 | 3.3% | 2.4% |
  | 2021 | 1.2% | 0.5% |

- **Earlier runs are unchanged.** The layer applies only to configs that opt in.
- **Details:** `docs/checkpoints/P2_CP6_sec_verification_survivorship_remediation.md`.
