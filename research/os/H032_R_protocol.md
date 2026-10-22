# H032 — R1 / R2 implementation and evaluation protocol (FROZEN before any strategy return)

- **Owner decision:** D282 (approve the trading host, R1, and R2 conditionally). **Implementation decisions:** D283.
- **Frozen text:** `research/os/H032_spec.md` (unchanged; this document only makes §9 executable). The signal, filters, Top-15 rule, 2N buffer, start review, gates and window are NOT changed.
- **Pinned in `qresearch.os1r`** with the host S033, `qr_os1_trade`, `qr_os1_books`, the pinned canary host X807, `qr_os1`, `qr_ucr` and the evaluation rule `research/os/OS1_R_eval.py` (`tests/test_os1_r.py`).
- **Status of every result:** EXPLORATORY. RR6 INCONCLUSIVE. Holdout sealed. No other variant, parameter, threshold or universe.

## 1. Runs

| Run | Experiment | Slippage | When |
|---|---|---|---|
| R1 | E033-01 (retry E033-02 only after a documented infrastructure failure) | 10 bps / side | Authorised (D282) |
| R2 | E033-03 (retry E033-04) | 20 bps / side (base 10 bps × `slippage_stress_multiple` 2, the D024 convention) | ONLY if R1 is technically valid (§4) AND passes O1–O7 and O9 |

- **Configuration:** `strategies/S033_h032_os1`, research / DEV, official start **2012-07-31** (the frozen start review), end 2021-12-31, history-only warm-up from **2009-05-01** (the canary's stream), $100,000, $7 per order.
- **Portfolio rules:** max_positions 15, 10% weight cap, $5,000 minimum new position, 2% cash buffer, D051 settled-cash funding with a 15% gap reserve.
- **Platform:** QuantConnect's default build (recorded), the two pinned SEC objects.

## 2. Execution (identical for every traded book)

1. **Review** (frozen): the stream of month-end session t (QuantConnect stamps it the next calendar day), SEC rows filed before t.
2. **Decision:** at the **first harness close after the review data arrive** (the close of session t + 1). The harness can act only at a close and only on data already received.
   - Information used: the review of t; sizing at the decision close's prices.
   - Orders are market-on-open at the following session (t + 2).
   - This one-session implementation lag is the same for every book, uses no later information, and is disclosed.
3. **Targets:** every book applies its frozen rule (spec §7, `qr_os1.plan` / `random_step` / `beta_step`) to its **actual** holdings: held names not being sold, plus buys already placed.
   - The random and filtered-random books replace as many names as LEAN B1 enters at that review.
   - Beta-matched controls are paired to LEAN B1's target.
4. **Exits:** holdings outside the target are sold at the decision close. An exiting position keeps its slot until its sale executes (D051, harness `plan_event_targets`).
5. **Entries:** the target names not yet held, in priority order.
   - Score order for ranked books; key order for random and beta-matched books.
   - Limited to the free slots and sized by the harness order planner (equity / 15 within the 2% buffer, $5,000 minimum, 10% cap, settled cash, 15% gap reserve, $7 per order).
   - Names not bought (no free slot, no cash, below the minimum) are retried at **every close until the next review**; nothing else is resized (the S016 precedent).
6. **Corporate actions and forced exits** follow the harness and LEAN: splits, dividends, delisting at the last price with $7, and the D059 stale exit after more than 10 sessions without a real bar.

## 3. Books and benchmarks

| Name | What | Engine |
|---|---|---|
| LEAN | B1, the H032 strategy | LEAN through the harness |
| B1 (shadow) | the same decisions on the shadow engine's own holdings: the fidelity replay | `qr_os1_books` (byte copy of the E984-verified engine) |
| VB1, B0, MOM, B2 × 5, RND × 5, BETA × 5 | frozen controls (spec §7) | `qr_os1_books`, same mechanics and costs |
| SPY | total-return index from SPY closes and dividends, no costs (conservative for H032) | in-host |
| EW, EW_V | equal-weight covered pool (all / vendor-eligible) | in-host, frictionless (see below) |

**EW and EW_V construction** (frictionless; favourable to the controls):
- rebalanced at each review close using the stream's adjusted closes;
- a member without a later price counts as unchanged;
- the last period ends at the final stream session.

**Daily grid:** every book and SPY are recorded at every official close from **2012-07-31** (base $100,000; SPY level 1.0).

## 4. Validity before any verdict (STOP, no strategy verdict, if any fails)

| # | Check |
|---|---|
| I1 | Runner status `completed` and no failed runner integrity check (equity completeness, timing, fees, no leverage) |
| I2 | First traded review = 2012-07-31 (the host refuses to trade otherwise) |
| I3 | Point in time and identity: 0 SEC rows used on or after the review day; 0 duplicate identities; 0 restored securities without identity |
| I4 | Harness: 0 timing violations, 0 invalid orders, 0 negative quantities, 0 stale open orders; 0 LEAN target names without a symbol |
| I5 | Dataset consistency with the canary E807-02: for every review from 2012-07-31, the H032 denominator, covered and passing counts each differ by at most 2% (relative). Every difference is reported |
| F | **Fidelity pre-gate:** shadow-B1 terminal wealth within **1%** of LEAN's, and every calendar-month return within **0.5 points** (month-end closes from 2012-07-31). The actual maximum monthly difference and the terminal difference are reported |

## 5. Gates (spec §9; all on R1 unless stated)

**Returns:**
- Daily r = E_t / E_{t−1} − 1 on the common grid.
- Monthly returns use calendar month-end closes.
- CAGR = ∏(1 + r)^(252 / n) − 1 (Amendment 3 `wealth.cagr`).
- EW CAGR uses the same number of years as LEAN.
- Subperiod A = closes through 2015-12-31; B = after 2015-12-31.

| # | Rule |
|---|---|
| O1 | LEAN terminal wealth > SPY's **and** CAGR(LEAN) − CAGR(SPY) ≥ 1.0 point |
| O2 | g / SE ≥ 1.0. d = ln(1 + r_LEAN) − ln(1 + r_SPY) daily; g = 252 · mean(d); SE = `wealth.se_w2(d)` (max of iid and stationary bootstrap, mean block 126) |
| O3 | Monthly, up months = SPY month > 0. Up-capture = mean(LEAN \| up) / mean(SPY \| up) ≥ 1.00; capture spread = up-capture − down-capture (months SPY ≤ 0) ≥ +0.05 |
| O4 | Monthly OLS r_LEAN = α + β r_SPY: α > 0 with t ≥ 1.0 (Newey–West, Bartlett, lag 2) |
| O5 | CAGR(LEAN) > CAGR(EW), and > CAGR of ≥ 4 of 5 RND, ≥ 4 of 5 BETA and ≥ 4 of 5 B2 books |
| O6 | In each subperiod, log(LEAN growth) − log(SPY growth) > 0 and log(LEAN growth) − log(EW growth) > 0. EW periods are assigned by their end date |
| O7 | Daily d vs SPY summed in calendar blocks 2012–13, 2014–15, 2016–17, 2018–19, 2020–21: total > 0 and no block > 50% of the total |
| O8 | R2: LEAN terminal wealth > SPY's |
| O9 | VB1 terminal wealth > SPY's and CAGR(VB1) > CAGR(EW_V) |

**Decision:**
1. Validity (§4) fails → **STOP**: no verdict, no reinterpretation, no fix without the owner.
2. R1 valid, any of O1–O7 / O9 fails → **H032 NOT PROMISING**. No R2. B0 and every control stay diagnostics, never promoted.
3. All pass → R2 (same validity checks) → O8 fails: **NOT PROMISING**; passes: **EXPLORATORY PASS — UNIVERSE INCONCLUSIVE (RR6)**.
4. STOP for the owner in every case. Independent validation is proposed, never started.

## 6. Reported, never gating

- **Every book and the benchmarks:** wealth, CAGR, excess vs SPY.
- **LEAN vs SPY, monthly:**
  - captures: mean and compounded, up and down;
  - excess in strong-up months (SPY ≥ +3%) and in the bull state (SPY trailing 12-month > 0 at the previous month-end);
  - α / β.
- **LEAN, SPY and EW, daily:** maximum drawdown, volatility, Sharpe, downside capture.
- **Subperiod tables.**
- **B0 vs LEAN and MOM vs LEAN** (correlation of monthly excess): diagnostic only.
- **Turnover and costs:**
  - LEAN orders, fees and slippage from the fills;
  - every shadow book's commission, slippage and notional by month.
- **Concentration:**
  - positions, maximum position weight;
  - FF12 shares of LEAN targets by year.
- **Restored securities:** their share of LEAN targets and their P&L share in the shadow replay.
- **Integrity and fidelity diagnostics:** engine version, data checks, canary comparison, engine counts, delistings / stale exits.

**Observed performance is not predictive evidence:** 2012–2021 is exposed development data, the universe is RR6 INCONCLUSIVE, and nothing here is independent validation.
