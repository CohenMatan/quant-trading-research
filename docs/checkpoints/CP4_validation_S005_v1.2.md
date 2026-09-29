# Checkpoint 4 (part 1): Validation of S005 v1.2 (H005, low volatility)

| Field | Value |
|---|---|
| Status | **STOPPED. Awaiting owner approval.** No Walk-Forward run. Holdout untouched (no date after 2021-12-31 was used). |
| Strategy | S005 v1.2: every month, the 15 lowest 63-day-volatility stocks among those with positive 12-1-month momentum |
| Frozen | Exactly as in C01 (E005-12); promotion record `research/promotions/S005_v1.2.json`. The runner verified that code, parameters, universe, costs, portfolio and execution rules match it. |
| Validation run | **E005-28**, 2018-01-02 → 2021-12-31, $100K. The one and only VAL run for this lineage (D042). All integrity checks passed. |
| Benchmarks, same dates | Equal-weight ≥ $2B universe **E901-05** (same harness); **SPY** buy-and-hold **E900-06** |
| Plan written before the run | `research/validation/S005_v1.2_VAL_plan.md`; evaluation code `qresearch.validation` (committed first) |

## 0. The answer in plain language

1. **It partly generalised.**
   - Risk-adjusted return held up (Sharpe 0.89; IS 1.44).
   - Losses stayed small (worst drawdown −6.5%), including through the 2020 crash.
   - **Absolute return was weak.** 4.4% a year, against 12.3% for the equal-weight universe and 17.0% for SPY.
2. **Formal Validation result: FAIL.**
   - All six performance checks on 2018–2021 pass.
   - **Deflated Sharpe fails** (0.68 against ≥ 0.90), and the already-known **PBO fails** (0.71 against ≤ 0.30).
3. **The result weakens the case for a real, tradable edge:**
   - Its measured advantage over the benchmark, after allowing for its low market exposure, is small and statistically indistinguishable from zero in 2018–2021 (alpha +2.4% a year, t = 1.2; IS t = 3.2).
   - In 2018–2021 its entire gain came from dividends and other cash distributions. The trades themselves lost money on price.
4. **New infrastructure defect found (§6).** The universe filter lets in **closed-end funds and partnership units**, which are not US common stocks. They were **23% of S005's capital in Validation** (6% in IS).
   - The filter is shared by all C01 runs and both benchmarks.
   - Nothing was changed, per your instruction. The defect needs your decision.
5. **Recommendation:**
   - Record **"No Production Candidate Found" for C01 at the Validation stage**.
   - Do not start Walk-Forward for S005 v1.2.
   - Fix the universe defect before any further research (§8).

## 1. Validation-period performance (2018-01-02 → 2021-12-31, net of all costs)

| | S005 v1.2 | Equal-weight ≥ $2B | SPY |
|---|---|---|---|
| CAGR | **4.4%** | 12.3% | 17.0% |
| Sharpe (rf = 0) | **0.89** | 0.65 | 0.87 |
| Max drawdown | **−6.5%** | −37.8% | −33.1% |
| Drawdown in 2020 Feb–Mar | −6.5% | −37.8% | −33.1% |
| 2018 | −0.9% | −9.1% | −5.1% |
| 2019 | +8.3% | +27.0% | +30.5% |
| 2020 | +2.5% | +17.6% | +18.0% |
| 2021 | +8.1% | +16.9% | +28.0% |
| Positive years | 3 of 4 | 3 of 4 | 3 of 4 |

**Trading:**

- **Trades:** 174 closed, with a 60% win rate and an average hold of 84 days. 374 orders in total.
- **Profit factor 0.91.** Trade profit is price-only (convention D018, which excludes dividends). On price alone, the trades lost $2,818 in total.
- **Where the gain came from.** Equity grew $18,884. Dividends and other cash distributions contributed about $20,189, roughly **4.7% of equity a year**; in IS this was about 2.0% a year.

**Invested versus cash:**

- On average 72% invested and 28% cash.
- Close to 0% invested for the first 22 trading days of 2018. The universe needs about 20 days of volume history before any stock qualifies, and IS starts the same way.
- **About 41% invested during the March 2020 crash.** The March 2 rebalance sold names, and under the no-borrowing rule the freed slots stayed empty until the April rebalance.

**Turnover and costs:**

- Buy + sell value was 5.2× equity a year (about 2.6× one-way).
- Commissions: $2,618, 0.61% a year.
- Estimated slippage: $2,243, 0.52% a year.
- Total cost: about 1.1% a year.

**IS → VAL degradation:**

| | IS | VAL |
|---|---|---|
| Sharpe | 1.44 | 0.89 (62% retained) |
| CAGR | 8.5% | 4.4% |
| Max drawdown | −5.3% | −6.5% |

## 2. Validation gate (approved D036; computed by pre-committed code)

| Check | Result | Requirement | |
|---|---|---|---|
| VAL Sharpe | 0.89 | ≥ 0.40 | ✅ |
| VAL Sharpe vs IS | 62% of 1.44 | ≥ 50% | ✅ |
| VAL Sharpe vs equal-weight | 0.89 vs 0.65 | above EW | ✅ |
| VAL max drawdown | −6.5% | no worse than −35% | ✅ |
| VAL closed trades | 174 | ≥ 50 | ✅ |
| 2020 Feb–Mar drawdown | −6.5% vs EW −37.8% | ≥ EW − 5 points | ✅ |
| **Deflated Sharpe, IS + VAL combined, 77 trials** | **0.68** | ≥ 0.90 | ❌ |
| **PBO (CSCV on IS, fixed at CP3)** | **0.71** | ≤ 0.30 | ❌ |

**Verdict: FAIL (6 of 8).** Deflated Sharpe fails on its own, independently of PBO.

## 3. Exposure-aware comparison: is the low drawdown and higher Sharpe just the cash?

**Method (declared before the run).** Each benchmark is held with S005's own day-by-day invested percentage, with the rest in cash at 0%. Separately, S005's daily returns are regressed on each benchmark's.

| 2018–2021 | S005 v1.2 | EW at S005's exposure | SPY at S005's exposure |
|---|---|---|---|
| CAGR | 4.4% | 10.7% | 13.4% |
| Sharpe | **0.89** | 0.80 | **1.02** |
| Max drawdown | **−6.5%** | −20.8% | −18.1% |

| Regression on daily returns | vs EW | vs SPY |
|---|---|---|
| Beta | 0.15 | 0.16 |
| Annual alpha | +2.4% | +1.6% |
| t-statistic of alpha | 1.2 | 0.8 |
| Correlation with EW | 0.63 | |

**For context, IS 2010–2017, same method:**

| | S005 v1.2 | EW at S005's exposure |
|---|---|---|
| Sharpe | 1.44 | 1.01 |
| CAGR | 8.5% | 10.8% |
| Max drawdown | −5.3% | −14.2% |

In IS, versus EW: beta 0.28, alpha +4.4% a year, t = 3.2.

**Reading:**

- **The low drawdown is not just cash.** Even with identical cash, the benchmarks fell about three times further in 2020 (−21% / −18% versus −6.5%). The holdings themselves were much less exposed to market falls: beta about 0.15.
- **The higher Sharpe is mostly not an edge in 2018–2021.**
  - It beats exposure-matched EW (0.89 vs 0.80) but loses to exposure-matched SPY (0.89 vs 1.02).
  - Its alpha shrank from +4.4% a year (t = 3.2, IS) to +2.4% (t = 1.2, VAL). In VAL that cannot be told apart from zero.
- **It earns far less in rising markets.** It gave up about 6 points a year against even the exposure-matched EW, and about 9 against SPY.

## 4. What the holdings reveal (descriptive)

- **Closed-end funds and partnership units:** 23% of capital in VAL (see §6).
- **Mortgage REITs and business development companies (BDCs):** BXMT, STWD, ARI, CIM, AGNC, MAIN, GBDC and others. BDCs alone were 2.8%.
- **Pending takeover targets.** Once a deal is announced the price is pinned, so the volatility screen picks them up. Examples: ADSW, CBPO, ACIA, WBC, USG, KS, RHT, MGLN, CHNG, PPD, NUAN, WORK, TIF, and in IS MON, NXPI, COL, WGL and STRP. This is legitimate under the rules (a pure price signal), but it means part of the "low-volatility" return is really merger-arbitrage exposure: small, capped gains and occasional deal-break risk.
- **Classic defensive stocks:** PG, KO, PEP, JNJ, KMB, CL, WMT, MCD, VZ and utilities. These are what the hypothesis was about, and they were a minority in VAL.

## 5. The PBO concern, kept separate

- PBO for H005 is **0.71** against the pre-declared ≤ 0.30. This was known at CP3. It was not changed, reinterpreted or waived, and it counts as a failed gate item above.
- **Implication:** the approved process says the in-sample choice among H005's variations has a high chance of being overfit.
- The Validation performance does not remove that concern. It adds one: Deflated Sharpe, which penalises the 77 trials, is also below its threshold on the full 12 years.
- Two independent multiple-testing measures now point the same way.

## 6. New finding: a universe defect (D057, not fixed)

**What.**

- The harness's "US common stock" filter trusts Morningstar's security type. Morningstar labels some **closed-end funds** and **partnership/LLC units** as common stock, so they entered the ≥ $2B universe.
  - Closed-end funds: NEA, NVG, NZF (Nuveen municipal bond funds), DSL (DoubleLine), BCAT (BlackRock), UTG (Reaves).
  - Partnership/LLC units: BPL, OAK, MMP, PAA, WPZ, KMR, OKS, KKR (pre-2018), MIC.
- The approved universe is **US common stocks** (CP1 and CLAUDE.md), so these should have been excluded.

**How much** (hand classification, used for evaluation only; share of capital-days):

| Run | Closed-end funds | Partnership units | (BDCs, borderline) |
|---|---|---|---|
| E005-28 (VAL) | 12.7% | 10.6% | 2.8% |
| E005-12 (IS) | 5.1% | 1.0% | 4.6% |
| E005-10 / E005-11 (IS) | 5.1% / 9.3% | 0.9% / 0.1% | 4.4% / 0.3% |

- The same filter builds the **equal-weight benchmark** and every other C01 universe, so all C01 comparisons share the defect.
- The price profit or loss on these holdings was small or negative, but their distributions probably make up a meaningful part of S005's cash income in VAL.
- All affected runs carry a `flagged` annotation in the registry. None is deleted or retired.

**Why it matters.** Low-volatility selection is the rule most attracted to bond-like funds. S005's Validation portfolio is therefore partly not the strategy you approved.

**Options:**

- (a) Fix the filter now, as an infrastructure bug fix (D-level): exclude funds, trusts and partnership units using Morningstar's classification fields, verified by an audit run and tests. Then decide what to re-run.
- (b) Leave it and note it.

I recommend **(a)**. It is required before any further research, whatever you decide about H005.

## 7. Does this strengthen or weaken the case that H005 has a real edge?

**It weakens it.**

- **Supports:**
  - The risk profile held out of sample: low beta, small drawdowns, a good crash outcome even after adjusting for cash.
  - All six performance checks passed.
- **Against:**
  - The return advantage per unit of market exposure shrank to statistical noise (t = 1.2).
  - It lost to SPY held at the same exposure.
  - The trades lost money on price, and returns relied on distributions, partly from securities outside the approved universe.
  - Two multiple-testing checks (Deflated Sharpe, PBO) fail.
- **Honest summary.** H005 as implemented is a low-beta, income-heavy portfolio that protects well in falls and lags badly in rises. It is not shown to be a robust source of excess return.

## 8. Recommendation and decisions for you

1. **Accept the formal Validation FAIL.** Record **"No Production Candidate Found" for Research Cycle 1**. Do not run Walk-Forward for S005 v1.2. The Holdout stays locked.
2. **Approve fixing the universe defect (§6)** as an infrastructure fix before any new research.
   - After the fix, S005 cannot get a second clean Validation on 2018–2021 (one VAL per lineage, D042).
   - Any corrected low-volatility idea would be a new, post-VAL hypothesis, and its report must say so.
3. **Decide whether to start Research Cycle 2** (new, pre-2018-motivated hypotheses) after the fix. It needs your approval; nothing has been started.

## 9. Accounting and records

- **Registry:** 83 research runs (82 + E005-28); all kept.
  - Trial count at evaluation: 77.
  - New annotations flag the universe defect on the 19 final C01 runs, E005-28 and the benchmark E901-05.
- **Files:**
  - Evaluation: `research/validation/E005-28_validation.json` (all numbers above).
  - Plan: `research/validation/S005_v1.2_VAL_plan.md`.
  - Freeze record: `research/promotions/S005_v1.2.json`.
- **Decisions:** D056 (promotion and evaluation), D057 (universe defect).
- **Not done, as instructed:**
  - no parameter, rule or code change after Validation;
  - no new variations;
  - no H001–H004 work;
  - no Walk-Forward;
  - no date after 2021-12-31.
