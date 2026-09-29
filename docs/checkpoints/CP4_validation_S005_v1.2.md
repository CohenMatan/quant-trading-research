# Checkpoint 4 (part 1): Validation of S005 v1.2 (H005, low volatility)

| Field | Value |
|---|---|
| Status | **Final, after the owner-requested accounting reconciliation. STOPPED, awaiting owner approval.** No Walk-Forward run. Holdout untouched (no date after 2021-12-31 was used). |
| Strategy | S005 v1.2: every month, the 15 lowest 63-day-volatility stocks among those with positive 12-1-month momentum |
| Frozen | Exactly as in C01 (E005-12), by `research/promotions/S005_v1.2.json`. The runner verified code, parameters, universe, costs, portfolio and execution rules. |
| Validation run | **E005-28**, 2018-01-02 → 2021-12-31, $100K. The one and only VAL run for this lineage (D042). All run-integrity checks passed. |
| Accounting audit | **E955-01** (X955, D058). Places no orders; not a research trial; the strategy was not re-run. |
| Benchmarks, same dates | Equal-weight ≥ $2B universe **E901-05** (same harness); **SPY** buy-and-hold **E900-06** |
| Plan written before the run | `research/validation/S005_v1.2_VAL_plan.md`; evaluation code `qresearch.validation`, committed first |

## 0. The answer in plain language

1. **Validation result: FAIL.** The approved Validation gate has **eight** checks, and all eight are required.
   - Six pass.
   - **Two fail:** Deflated Sharpe (0.68, required ≥ 0.90) and PBO (0.71, required ≤ 0.30).
   - Neither threshold was changed, reinterpreted or waived.
2. **Accounting verified exactly.** Ending equity reconciles to the cent: start + price P&L + commissions and slippage + every corporate-action cash credit (§3).
   - All $20,188.82 of non-trade cash is identified, event by event.
   - Nothing is double-counted.
3. **The accounting changes the picture of the return.**
   - Most of the 2018–2021 gain came from **two one-off corporate events**: the Dr Pepper/Keurig merger cash payout and Macquarie Infrastructure's special distribution after an asset sale.
   - Ordinary dividends were about 2% a year.
   - The trades the strategy itself closed lost money on price.
4. **Low exposure largely explains the shallow drawdown.**
   - The strategy held about 42% of equity in positions during the March 2020 crash.
   - About 30% was in live positions, because two positions had been dead since 2019 (§4).
   - Holding the benchmarks at that economic exposure cuts their crash drawdown from −38% / −33% to about −16% / −15%. S005's −6.5% is still smaller, but by far less than the raw comparison suggests.
5. **Two infrastructure defects found; nothing fixed yet:**
   - **D057:** closed-end funds and partnership units pass the common-stock filter.
   - **D059:** two acquired partnership-unit positions (OAK, BPL) were never delisted in the data. Their sell orders never filled, and they sat dead in 2 of the 15 slots from late 2019 to the end of 2021.
   - Neither affects the IS results of any C01 strategy. D059 affects this Validation run and, negligibly, the benchmark.
6. **Recommendation:**
   - Record "No Production Candidate Found" for Research Cycle 1.
   - No Walk-Forward.
   - Fix D057 and D059 before any further research.

## 1. Validation gate: every check, individually (approved D036; pre-committed code)

| # | Check | Result | Requirement | Verdict |
|---|---|---|---|---|
| 1 | VAL Sharpe | 0.89 | ≥ 0.40 | **PASS** |
| 2 | VAL Sharpe vs IS Sharpe | 0.89 = 62% of 1.44 | ≥ 50% | **PASS** |
| 3 | VAL Sharpe vs equal-weight benchmark | 0.89 vs 0.65 | above EW | **PASS** |
| 4 | VAL max drawdown | −6.5% | no worse than −35% | **PASS** |
| 5 | VAL closed trades | 174 | ≥ 50 | **PASS** |
| 6 | 2020 Feb–Mar drawdown vs EW | −6.5% vs −37.8% | ≥ EW − 5 points | **PASS** |
| 7 | Deflated Sharpe, IS + VAL combined, 77 trials | **0.68** | ≥ 0.90 | **FAIL** |
| 8 | PBO (CSCV on IS, fixed at CP3) | **0.71** | ≤ 0.30 | **FAIL** |

**Overall: FAIL (6 of 8 pass; 2 fail).**

- Check 7 fails on its own, independently of the already-known PBO failure.
- Checks 1–6 are computed on the run as it happened. §3–§4 explain how corporate-action cash and the dead positions affect what they mean.

## 2. Validation-period performance (2018-01-02 → 2021-12-31, net of all costs)

| | S005 v1.2 | Equal-weight ≥ $2B | SPY |
|---|---|---|---|
| CAGR | 4.4% | 12.3% | 17.0% |
| Sharpe (rf = 0) | 0.89 | 0.65 | 0.87 |
| Max drawdown | −6.5% | −37.8% | −33.1% |
| Drawdown in 2020 Feb–Mar | −6.5% | −37.8% | −33.1% |
| 2018 | −0.9% | −9.1% | −5.1% |
| 2019 | +8.3% | +27.0% | +30.5% |
| 2020 | +2.5% | +17.6% | +18.0% |
| 2021 | +8.1% | +16.9% | +28.0% |
| Positive years | 3 of 4 | 3 of 4 | 3 of 4 |

**Trades:** 174 closed, 60% winners, average hold 84 days, 374 orders in total.

- **47 of the 174 (27%) ended because the company was taken over** and LEAN cashed the position out ("forced liquidation"). These won 83% of the time and made **+$3,018**.
- The **127 trades the strategy closed itself lost −$5,836**.

**Invested versus cash:**

| | Reported (positions / equity) | Economic (dead OAK/BPL positions counted as cash) |
|---|---|---|
| Average | 72% | 65% |
| March 2020 crash | about 42% | **about 30%** |

The crash exposure was low because the March 2 rebalance sold names, and the no-borrowing rule (D051) kept those slots empty until April. The first 22 trading days of 2018 were almost entirely cash, because the universe needs about 20 days of volume history (IS starts the same way).

**Turnover and costs:**

- Buy + sell value was 5.2× equity a year (about 2.6× one-way).
- Commissions: $2,618, 0.61% a year.
- Estimated slippage: $2,243, 0.52% a year, already inside fill prices.

**IS → VAL:**

| | IS | VAL |
|---|---|---|
| Sharpe | 1.44 | 0.89 |
| CAGR | 8.5% | 4.4% |
| Max drawdown | −5.3% | −6.5% |

## 3. Accounting reconciliation (exact)

**Method.**

- E005-28 did not record cash events per security. The audit E955-01 therefore subscribed to the 131 securities E005-28 held, by their exact identifiers.
- For every dividend, split, ticker change and delisting during E005-28's holding periods, it recorded the cash E005-28's holdings should receive.
- That was then matched, trading day by trading day, against E005-28's cash movements not explained by its fills.

**Result.**

- Unexplained cash in E005-28: **$20,188.82**.
- Cash owed by the audit: **$20,188.82**.
- Residual over the whole period: $0.003. There is **no day with a residual above $0.01**.
- Every non-trade cash credit is a dividend or distribution on a held position. There are no unexplained credits and no debits.

**Classification of non-trade cash** (per event: `research/validation/E005-28_cash_events.csv`):

| Category | Events | Cash | Detail |
|---|---|---|---|
| Ordinary dividends | 179 | **$8,410.33** | Median 0.5% of price per payment (about 2.0% of equity a year). Of this, $2,293 came from closed-end funds. |
| Special distributions | 3 | **$6,383.49** | MIC 2021-10-08 $5,645.89 ($37.39 per unit after the Atlantic Aviation sale; MIC is an LLC-unit holding, see D057); EQC 2020-09-30 $686.00 ($3.50 special); NVG 2020-12-14 $51.60 (closed-end-fund year-end supplemental) |
| Merger / acquisition cash consideration | 1 | **$5,395.00** | Dr Pepper Snapple (DPS→KDP) 2018-07-10: $103.75 per share paid to holders in the Keurig merger |
| Spin-off or other corporate-action cash | 0 | **$0.00** | See 21st Century Fox below |
| **Total** | **183** | **$20,188.82** | |

**Forced liquidation proceeds** are fills, not non-trade cash: 47 takeover or delisting cash-outs, $303,221 of proceeds, each charged $7 (D049). Their price result (+$3,018) is inside trade P&L.

**No double counting.**

- Positions are valued and filled at raw prices; adjusted prices are used only for signals (D016). A cash distribution therefore coincides with an equal fall in the raw price.
- Checked on each large event day:

| Date | Event | Cash change | Equity change that day |
|---|---|---|---|
| 2018-07-10 | KDP merger payout | +$5,395 | +$217 |
| 2021-10-08 | MIC special distribution | +$5,646 | +$188 |
| 2020-09-30 | EQC special distribution | +$686 | +$564 |

- In each case the position's value fell by the distribution. Equity did not jump.
- The audit found 47 delistings on held positions, matching the 47 forced liquidations one for one, and 2 ticker changes (DPS→KDP; FOX→TFCF), neither of which carried a double credit.

**Possible under-count (not double count): 21st Century Fox.**

- E005-28 held 120 shares when New Fox was distributed and 21CF was acquired by Disney (March 2019).
- The data shows no distribution credit and no price drop. The position was cashed out at $51.04, in line with the Disney consideration.
- If holders were additionally due New Fox shares, the backtest leaves them out and *understates* S005 by at most the value of those shares. The QuantConnect data cannot settle this.

**Reconciliation of equity** (all figures from committed run files; open positions valued at E005-28's final marks):

| Line | Amount |
|---|---|
| Starting equity | $100,000.00 |
| Price P&L of closed trades, before commissions (fills include 10 bps slippage) | −$297.80 |
| Price P&L of the 14 open positions, before commissions | +$1,610.64 |
| Commissions ($7 × 374 orders, including 47 forced liquidations) | −$2,618.00 |
| Ordinary dividends | +$8,410.33 |
| Special distributions | +$6,383.49 |
| Merger cash consideration (paid as dividend) | +$5,395.00 |
| Spin-off / other corporate-action cash | $0.00 |
| **Computed ending equity** | **$118,883.66** |
| **Reported ending equity (E005-28)** | **$118,883.66** |
| Difference | $0.003 |

- Slippage (estimated $2,243) is already inside the fill prices, so it is part of the price P&L lines, not a separate cash line.
- Closed trades net of their $2,520 commissions: −$2,817.80. Open positions net of their $98: +$1,512.64.

**What the reconciliation means:**

- Of the $18,884 gain, **$11,040.89 (58%) came from two one-off corporate events**: the KDP merger payout and the MIC special distribution.
- Without them the gain is about $7,843, roughly 1.9% a year.
- The trades together lost $1,305 after commissions. The rest is ordinary dividends plus two small specials.

## 4. Dead positions, and what low exposure explains

**D059, new: dead positions.**

- **OAK** (Oaktree Capital Group units): acquired by Brookfield on 2019-09-30.
- **BPL** (Buckeye Partners units): acquired by IFM on 2019-11-01.
- The data never delivered a delisting for either, so LEAN never cashed them out. S005's sells (2019-10-01 and 2019-12-02) stayed "submitted" for more than two years.
- Both positions sat at their last price until the end of 2021: 11% of equity, 2 of the 15 slots.
- Effects:
  - They earned 0%, like cash, so they did not inflate returns.
  - They made reported exposure overstate economic exposure.
  - **The run is not a faithful implementation from late 2019 onward.** The strategy would have used those slots, and this cannot be corrected without a new run, which is not allowed.
- Across all C01 runs, the benchmark and E005-28, only E005-28 (2 positions) and the equal-weight benchmark (9 positions of about 0.1% each, mostly partnership units) were affected. **No IS run was affected.** Evidence: `research/validation/C01_VAL_unfilled_orders_audit.txt`.

**Exposure-aware comparison.** Each benchmark is held at S005's day-by-day exposure, with the rest in cash at 0%. This method was declared before the run; the economic-exposure version was added in this reconciliation.

| 2018–2021 | S005 v1.2 | EW at reported exposure | EW at economic exposure | SPY at reported exposure | SPY at economic exposure |
|---|---|---|---|---|---|
| CAGR | 4.4% | 10.7% | 9.5% | 13.4% | 11.7% |
| Sharpe | 0.89 | 0.80 | 0.80 | 1.02 | 1.02 |
| Max drawdown | −6.5% | −20.8% | −16.4% | −18.1% | −14.8% |
| 2020 Feb–Mar drawdown | −6.5% | −20.8% | −16.1% | −18.1% | −14.0% |

**Regression of daily returns on each benchmark:**

| | Beta | Alpha per year | t-stat |
|---|---|---|---|
| vs EW | 0.15 | +2.4% | 1.2 |
| vs SPY | 0.16 | +1.6% | 0.8 |
| IS, vs EW (context) | 0.28 | +4.4% | 3.2 |

**Reading:**

- **Most of the shallow drawdown is low exposure.** Cash alone takes the benchmarks' crash losses from −38% / −33% to about −16% / −15%.
- The holdings account for the smaller remaining gap (−6.5% vs about −15%). They were low-beta, income and takeover-pinned names.
- **The Sharpe advantage is not an edge in 2018–2021.**
  - It beats exposure-matched EW (0.89 vs 0.80), but not exposure-matched SPY (1.02).
  - Alpha is statistically indistinguishable from zero.
  - Much of the return is the two one-off distributions in §3.

## 5. What the holdings reveal

- **Closed-end funds and partnership/LLC units:** 23% of capital-days (D057).
- **Pending takeover targets:** 47 of 174 trades ended in a buyout. Price-pinned targets look "low volatility", so part of the return is merger-arbitrage exposure (small, capped gains).
- **Mortgage REITs and business development companies (BDCs).**
- **Classic defensive stocks** (PG, KO, PEP, JNJ, KMB, CL, WMT, MCD, VZ, utilities), which are what the hypothesis was about. They were a minority.

## 6. The PBO concern, kept separate

- PBO for H005 is **0.71** against the pre-declared **≤ 0.30**. It was known at CP3, is not changed, reinterpreted or waived, and is check 8 above: **FAIL**.
- It means the approved process judges the in-sample choice among H005's variations likely to be overfit.
- The Validation performance does not remove that concern. It adds a second, independent multiple-testing failure: Deflated Sharpe 0.68 on the full 12 years, with 77 trials.

## 7. Infrastructure defects (recorded, not fixed; your decision)

| ID | Defect | Affects | Proposed fix |
|---|---|---|---|
| D057 | The common-stock filter trusts Morningstar's security type, which labels some closed-end funds (NEA, NVG, NZF, DSL, BCAT, UTG) and partnership/LLC units (BPL, OAK, MMP, PAA, WPZ, KMR, OKS, KKR, MIC) as common stock | All C01 universes and the EW benchmark. S005: 23% of VAL capital, about 6% in IS. | Exclude funds, trusts and partnership units using Morningstar classification fields; audit run and tests |
| D059 | Acquired securities with no delisting event in the data leave sell orders unfilled forever and positions frozen | E005-28 (OAK, BPL), E901-05 (9 small positions); no IS run | A new integrity check (any harness order still open after 5 trading days fails the run), plus a harness rule to treat a security that stops delivering data as delisted |

All affected runs carry `flagged` registry annotations. Nothing is deleted or retired.

## 8. Does this strengthen or weaken the case that H005 has a real edge?

**It weakens it.**

- **Supports:**
  - Low beta and small drawdowns held out of sample, partly beyond what cash explains.
  - Checks 1–6 pass.
- **Against:**
  - Two of eight Validation checks fail (Deflated Sharpe, PBO).
  - Alpha is not significant.
  - It loses to SPY held at the same exposure.
  - The strategy's own trades lost money.
  - 58% of the gain came from two one-off corporate payouts, one of them from a non-common-stock unit.
  - 27% of trades were takeover cash-outs, and two positions sat dead for two years.
- **Honest summary.** As implemented, H005 is a low-exposure, income- and takeover-heavy portfolio. It protects in falls because it holds little market risk. It is not shown to be a robust source of excess return.

## 9. Recommendation and decisions for you

1. **Accept the Validation FAIL** and record **"No Production Candidate Found" for Research Cycle 1**. No Walk-Forward for S005 v1.2. The Holdout stays locked.
2. **Approve fixing D057 and D059** before any further research.
   - After the fixes, S005 cannot get a second clean Validation on 2018–2021 (D042).
   - A corrected low-volatility idea would be a new, post-Validation hypothesis, and its reports must say so.
3. **Decide whether to start Research Cycle 2** after the fixes. Nothing has been started.

## 10. Records

- **Registry:**
  - 83 research runs, all kept; trial count 77.
  - E955-01 is registered as infrastructure (not a trial).
  - `flagged` annotations cover D057 (19 final C01 runs, E005-28, E901-05) and D059 (E005-28, E901-05).
- **Files:**
  - `research/validation/E005-28_validation.json`: all gate and performance numbers.
  - `research/validation/E005-28_cash_events.csv`: 183 classified cash events, portfolio amounts only.
  - `research/validation/C01_VAL_unfilled_orders_audit.txt`.
  - Plan: `research/validation/S005_v1.2_VAL_plan.md`.
  - Freeze record: `research/promotions/S005_v1.2.json`.
- **Decisions:** D056 (promotion and evaluation), D057 (universe defect), D058 (cash-event audit), D059 (dead positions).
- **Not done, as instructed:**
  - no change to the frozen strategy;
  - no second Validation run;
  - no new variations;
  - no H001–H004 work;
  - no Walk-Forward;
  - no date after 2021-12-31.
