# Post-2010 survivorship gap (D043) — mandatory disclosure for every research report

| Field | Value |
|---|---|
| Status | Counts and examples: **measured and estimated** (below). Direction of the return bias: **measurement E954-01 pending** (queued on QuantConnect; §5). |
| Sources | E953-01 and E953-02 (size-proxy runs, which contain the needed counts); a hand classification of 720 sampled securities (`size_proxy/fp_ticker_classification.csv`, evaluation-only); E954-01 (pending) |

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

## 5. Direction of the bias

**Reasoning (before measurement).** The missing names are a mix of two kinds.

- **Later acquired or merged** (Time Warner, Heinz, Precision Castparts, SanDisk, DuPont, …).
  - Before a deal is announced they are ordinary large caps.
  - At announcement they jump by the takeover premium.
  - Leaving them out removes these jumps from the universe, a **downward** bias on strategy and benchmark returns.
- **Later distressed or bankrupt** (Sears, JCPenney, Chesapeake, Weatherford, Frontier, Hertz).
  - They decline for years before ending.
  - Leaving them out removes losers, an **upward (optimistic)** bias.
  - This matters most for strategies that **buy weakness**: reversal and pullback strategies such as H001 and H004. The missing distressed names are exactly the "cheap after a drop" stocks such rules would have bought.

**Measurement (pending, E954-01).**

- Equal-weight forward one-month returns of the missing candidates, split by how they later ended: distress-type vs other.
- Compared with the reference universe, for **IS years 2010–2017 only**.
- It runs on QuantConnect when the log allowance returns. This section will be updated with the numbers.

**What every report must say until then.** Strategies are measured on a universe that lacks about 10% of eligible companies in IS (about 3% in VAL), mostly companies that later ended.

- The net effect on returns is likely small at the universe level: in the size-proxy work, proxy-only names returned −0.7%/year versus the reference in 2010–14, not significant.
- It may be **optimistic for strategies that buy losers**, and **conservative for strategies that hold large stable names**.
- Gates are relative to an equal-weight benchmark built on the **same** universe, which cancels much of the effect.
