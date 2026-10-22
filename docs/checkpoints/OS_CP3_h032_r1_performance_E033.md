# OS-CP3 — H032 R1 performance (E033-01): NOT PROMISING

- **Decision trail:**
  - D282: owner approves the trading host, R1 and a conditional R2.
  - D283: implementation, frozen before any return.
  - D284: this result.
- **Frozen before the run:**
  - spec `research/os/H032_spec.md` (unchanged);
  - implementation / evaluation protocol `research/os/H032_R_protocol.md`;
  - evaluation rule `research/os/OS1_R_eval.py`;
  - host S033, all pinned in `qresearch.os1r` (commit e85db9f).
  - The run commit aa3c015 adds only a config-validation fix for the historical E807-01 record. No pinned file changed.
- **Status:** EXPLORATORY. 2012–2021 is exposed development data, RR6 is INCONCLUSIVE, and the Holdout is sealed.
- **Not done:** no R2, no rerun, no variant, no purchase. H031 stays parked and H028 stays REJECTED.

## 1. Result in one paragraph

R1 is **technically valid**: every validity check passed, and the shadow-book fidelity replay agrees with LEAN to the cent. **H032 failed all eight R1 gates** (O1–O7 and O9).
- **Wealth:** $100,000 grew to **$286,598** (CAGR 11.84%), against **$414,278** for SPY (16.31%). That is **−4.47 points a year**.
- **Other references:**
  - It also trailed the frictionless equal-weight pool (14.24%).
  - It trailed most of its own random and beta-matched control books.
- **Up / down markets:**
  - It captured 96% of SPY's up months.
  - It captured 121% of SPY's down months.
  - It had a beta of 1.17.
  - It fell further than SPY at the worst point (−44.0% vs −33.7%, March 2020).
- **Subperiods:** it was ahead only in 2012–2015 (subperiod A). From 2016 it fell steadily behind.

Under the frozen rule:
- the verdict is **H032 NOT PROMISING**;
- **R2 is not run**;
- B0 and every control stay diagnostics and are never promoted.

## 2. Run and validity

**Run:**

| Item | Value |
|---|---|
| Run | E033-01, the first and only R1 attempt (no retry used) |
| Code | commit aa3c015; host S033 v1.0 |
| Platform | QuantConnect default build **LEAN 18201** (the canary ran on 18200); backtest `101500a9ee43…`; 349 s |
| Window | official start 2012-07-31 (the frozen first review), end 2021-12-31 |
| Account | $100,000; 10 bps slippage per side; $7 per order |
| Portfolio rules | 15 positions, 10% initial cap, $5,000 minimum, 2% buffer, D051 settled cash |
| Activity | 113 reviews; 428 LEAN orders, 435 fills |
| Hashes | equity `24778a48…`, fills `bded437f…`, trades `88035c77…` |

**Validity checks (all PASS):**

| Check | Result |
|---|---|
| I1 runner | `completed`; no failed integrity check |
| I2 start | first traded review 2012-07-31; first recorded close 2012-07-31 |
| I3 point in time / identity | 0 SEC rows used on or after the review day (NSI and annual filters); 0 extension PIT violations; 0 duplicate identities; 0 restored securities without identity |
| I4 harness | 0 timing violations, 0 invalid orders, 0 negative quantities, 0 stale open orders, 0 LEAN target names without a symbol |
| I5 dataset vs canary E807-02 | 113 of 113 reviews: H032 denominator, covered and passing counts **identical** (0 differences) despite the build change 18200 → 18201 |

**Fidelity pre-gate F: PASS.**
- **Terminal difference:** shadow B1 $286,597.83 vs LEAN $286,597.83 → **0.000%** (limit 1%).
- **Monthly difference:** maximum **0.000 points** (limit 0.5), over 113 months.
- **Daily difference:** also 0.00 on all 2,372 closes.
- **Independence:** the two series are computed independently. LEAN's comes from its portfolio value; the shadow's comes from the shadow engine's own ledger, a byte copy of the engine verified against LEAN in E984.
- **Agreement:** the planned targets were also identical (0 LEAN-vs-shadow target differences).

**Engine activity, all 19 shadow books together:** 6,554 dividends, 60 split adjustments, 116 delisting exits, 4 stale exits.
- **LEAN:** 7 forced liquidations, each charged the $7 commission (D049); 0 stale exits; 6 held splits.

## 3. Gates (R1)

| Gate | Rule | Result | Verdict |
|---|---|---|---|
| O1 | Wealth > SPY and CAGR excess ≥ 1 point | $286,598 vs $414,278; 11.84% vs 16.31% (**−4.47 points**) | **FAIL** |
| O2 | g / SE ≥ 1 | g −3.92% a year, SE 3.22% → **−1.21** | **FAIL** |
| O3 | Up-capture ≥ 1.00 and spread ≥ +0.05 | Up 0.96 (82 months), down 1.21 (31 months), spread **−0.25** | **FAIL** |
| O4 | NW-2 alpha > 0 with t ≥ 1 | α −0.49% a month (−5.8% a year), t −1.57; β 1.17 | **FAIL** |
| O5 | Beat EW and ≥ 4 / 5 of RND, BETA, B2 | EW 14.24% (not beaten); beat 1 / 5 RND, 1 / 5 BETA, 3 / 5 B2 | **FAIL** |
| O6 | Both subperiods beat SPY and EW (log growth) | A 2012-07 → 2015-12: +3.2 vs SPY, +0.8 vs EW; **B 2016 → 2021: −40.1 vs SPY, −20.7 vs EW** | **FAIL** |
| O7 | Positive total, no two-year block > 50% | Total **−0.368** (log). Blocks: 2012–13 +0.160, 2014–15 −0.128, 2016–17 −0.113, 2018–19 −0.083, 2020–21 −0.205 | **FAIL** |
| O9 | VB1 > SPY and CAGR(VB1) > EW_V | VB1 $290,642 (12.01%) vs SPY; EW_V 14.74% | **FAIL** |
| O8 | R2 wealth > SPY | **Not run** (R1 failed required gates) | — |

## 4. Required report

### 4.1 Wealth and returns, 2012-07-31 → 2021-12-31 (9.4 years)

| Book | Role | Wealth | CAGR | Excess vs SPY | Max DD | Vol | Sharpe |
|---|---|---|---|---|---|---|---|
| **LEAN (H032 B1)** | **strategy** | **$286,598** | **11.84%** | **−4.47** | **−44.0%** | 18.6% | 0.70 |
| SPY (total return, no costs) | benchmark | $414,278 | 16.31% | — | −33.7% | 16.3% | 1.01 |
| EW pool (frictionless) | benchmark | $349,843 | 14.24% | −2.07 | n/a (monthly) | — | — |
| EW_V vendor pool (frictionless) | benchmark | $364,494 | 14.74% | −1.57 | n/a | — | — |
| VB1 (vendor universe) | control | $290,642 | 12.01% | −4.30 | −43.8% | 18.5% | 0.71 |
| B2 random from the filtered pool (5 seeds) | control | — | 9.29 – 13.80% | — | — | — | — |
| RND random from the covered pool (5 seeds) | control | — | 9.59 – 13.41% | — | — | — | — |
| BETA beta-matched (5 seeds) | control | — | 11.65 – 16.37% | — | — | — | — |
| B0 unfiltered NSI rank | **diagnostic only** | $371,387 | 14.96% | −1.34 | −42.0% | 19.5% | 0.81 |
| MOM 12-1 momentum | **diagnostic only** | $536,492 | 19.55% | +3.24 | −44.2% | 31.0% | 0.73 |

- **CAGR convention:** CAGRs use the frozen 252-day convention. The runner's calendar-day CAGR for LEAN is 11.83%.
- **B0 and MOM are not candidates.** They are diagnostics from the frozen spec. B0 did better than B1 here, which says the filters did not help in this sample. **Neither is promoted, and neither is tested further.**

**Calendar years (LEAN vs SPY):**

| | 2012 (from 31 Jul) | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|---|---|---|---|
| LEAN | +10.8% | +46.7% | +9.4% | −7.5% | +7.8% | +13.0% | +0.8% | +14.3% | −0.4% | +24.6% |
| SPY | +4.8% | +32.2% | +13.5% | +1.3% | +12.0% | +21.7% | −4.6% | +31.2% | +18.4% | +28.8% |

### 4.2 Up and down markets (monthly, vs SPY)

- **SPY-up months (82):**
  - mean-ratio up-capture 0.96;
  - compounded up-capture 0.88.
- **SPY-down months (31):**
  - mean-ratio down-capture **1.21**;
  - compounded down-capture 1.13.
  - The book lost more than the market when it fell.
- **Strong-up months** (SPY ≥ +3%, 32 months): mean excess **+0.38%** a month.
- **Bull state** (SPY trailing 12 months > 0, 95 months): mean excess **−0.46%** a month.
  - Outside the bull state (18 months): +0.76% a month.
- **Regression:** α −0.49% a month (t −1.57, NW lag 2); β 1.17 (t 11.3).

### 4.3 Turnover, costs, concentration

**Turnover and costs:**
- 428 orders (about 45 a year).
- Traded notional $4.93M, about **139% one-way turnover a year** on average equity of $188K.
- Commissions $3,045; slippage about $4,923.
- Together about **0.45% a year** of average equity. Costs explain only about a tenth of the 4.5-point shortfall.
- The shadow B1 replay records the same commissions and slippage ($3,045 / $4,840 from the open-price base).

**Positions and weights:**
- Mean 14.9 positions, maximum 15.
- Largest single position weight 12.0%: a winner that grew past the 10% initial cap, which by rule is not trimmed.

**Sectors:**
- Targets clustered in Shops (retail) and Business Equipment / Other.
- Shops held 43% of target slots in 2016 and 37% in 2017, the years the book fell behind.
- H032 has no sector cap by design.

### 4.4 Restored securities (the SEC-repaired part of the universe)

- **In targets:** restored securities averaged 1.0 of the 15 targets per review (maximum 3).
- **Contribution in the shadow B1 replay:**
  - restored positions (44 holdings) contributed **−$1,978**;
  - vendor-universe positions (661 holdings) contributed **+$188,576**.
- **Universe check:** the vendor-universe-only book VB1 performs almost exactly like B1 (12.01% vs 11.84%; correlation of monthly excess 0.97).
- **Conclusion:** the universe repair does not explain the failure.

### 4.5 Diagnostics (non-gating)

- **Correlation of monthly excess returns with LEAN:**
  - B0: 0.57;
  - VB1: 0.97;
  - MOM: 0.04.
- **Beta matching:** 1,234 of 1,234 beta-matched draws found a match.
- **EW benchmark:** members without a later price were treated as unchanged (37 cases across all reviews), as the frozen construction specifies.

## 5. Observed performance versus evidence of predictive ability

- **What was observed:** over 2012–2021 on QuantConnect data, the frozen H032 book underperformed SPY, the equal-weight pool and most matched random books.
  - The underperformance lasted from 2014 onward, with 2018 the only year ahead; it was not one bad episode.
  - It came with higher beta and worse down-market capture.
- **What it does not show:**
  - This is one exposed development sample.
  - The universe is RR6 INCONCLUSIVE.
  - 15 of the 18 control books are random draws, so each one is noisy.
  - The result neither proves that net share repurchases carry no premium in general, nor that any other variant would work.
  - It does show that **this pre-registered strategy did not have the hoped-for edge in this sample**, under the frozen rules.

## 6. Decision under the frozen protocol and next step

1. Validity passed → gates applied → O1–O7 and O9 fail → **H032 NOT PROMISING (EXPLORATORY)**.
2. **R2 is not run** (D282: no R2 when R1 fails a required gate).
3. **Preserved exactly as tested:**
   - the result in `research/os/OS1_R_result_E033-01.json`;
   - the host's aggregate lines in `research/os/E033-01_os1r_lines.txt`;
   - run records in `experiments/E033-01/`.
4. **Closed lines:**
   - no rerun, variant, filter change, sector cap, other N or other start date;
   - B0, MOM and every control stay diagnostics and are not promoted.
5. **STOP.** The next step is the owner's.
   - The recommendation is to **close H032 as REJECTED — NOT PROMISING**.
   - There is no automatic successor: H031 stays parked and no new hypothesis is proposed here.
