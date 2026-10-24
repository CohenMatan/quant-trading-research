# H006X — Exit-policy comparison on the fixed H006 reference (owner D304)

**Status:** FROZEN before any run (commit recorded in `DECISIONS.md` D305 and pinned in `qresearch.h006x`). H006 stays **REJECTED** (C02, D076 / D078). It is used here only as a fixed historical reference, not revived or validated. **EXPLORATORY**: 2010–2021 is exposed development data and cannot provide independent validation (D261, D285).

## 1. The one question

Does removing the arbitrary 60-session time exit materially improve H006 by letting winners run? Everything else is held fixed.

| Run | What | Experiment |
|---|---|---|
| Control A | H006 v1.0 exactly: entry, ranking, chandelier exit K = 3.0 × ATR20, **60-session time stop**, 10 slots | **E006-04** |
| Experiment B | Identical, **without the time stop** (chandelier exit only) | **E006-05** |
| SPY benchmark | B900 SPY buy-and-hold (98% SPY, dividends reinvested monthly, $7 / order, 10 bps), same build and dates | **E900-08** |

Labels: A = S006 v1.0 (unchanged rules), B = S006 v1.3 (v1.0 without the time stop). No other run, no parameter grid, no variants, no tuning after results. A documented infrastructure failure allows **one** retry per run (E006-06 / E006-07 / E900-09); any other failure → STOP.

## 2. Feasibility verification (done before freezing)

| Check | Finding | Consequence |
|---|---|---|
| Existing code | S006 (`strategies/S006_breakout`) on the shared harness. Uploads only plain-text modules: harness, indicators, fundamentals, SEC-corrections logic, industry. No packed table, because the SEC layer is off (D254 compliant). 5 + 2 files, far below the 50-file limit. | Runs as is |
| Engine / dataset | Build 18131 and the old Morningstar dataset can no longer be selected (D180 / D254). The run uses QuantConnect's **default build**, recorded per run (`default_build_digest_verified`, as H032 did). | E006-01 (old dataset, 2010–2017) **cannot be reproduced exactly**. Control A is rerun on the current build. E006-01 is compared as a drift diagnostic only. |
| Universe | The harness universe: vendor point-in-time `market_cap` ≥ $2B, price ≥ $5, ADV20 ≥ $5M, US common primary listing on NYSE / Nasdaq / AMEX, daily. The ≥ $2B rule is unchanged. RR5 (E805) found this vendor universe **misses** confirmed ≥ $2B names: 3.5–6.1% a year in 2010–2015 (survivorship bias up to 0.78 points a year on an equal-weight universe) and 0.8–2.9% in 2016–2021 (INCONCLUSIVE). The SEC-repaired universe (UCR-1, RR6 INCONCLUSIVE) exists only at month-ends inside the X806 / X807 hosts. Daily H006 eligibility on it would be a new infrastructure build, which D304 forbids. | **FLAG 2** below |
| Holding-period scope | CLAUDE.md: several days to several weeks; Phase 2 (D094) weeks to months; D115 (H016 only) months to over a year. Experiment B has **no maximum holding period**. | **FLAG 1** below |
| Trailing-stop fidelity | S006 keeps a 260-bar window. For holds beyond 259 sessions the original code took the highest close of the last 260 bars, not since entry, which would quietly loosen the stop. | **Fidelity fix, no rule change.** Beyond the window the highest close since entry is carried forward (§3). Control A never holds that long (60-session cap), so A's behaviour is unchanged by construction (tested). |
| Holdout / 1999–2009 / purchases | The window ends 2021-12-31. No pre-2010 bar, no Holdout bar, nothing bought. | — |

### Scope flags (stated before any run; D304: "Explicitly flag any required scope amendment before running")

- **FLAG 1 — holding-period scope amendment, this comparison only.** Experiment B lets positions run without a time limit, beyond the "weeks to months" scope (D094). D304 itself defines Experiment B as "without the 60-session time exit", so this is read as the owner granting the amendment for E006-05 only. No general scope change.
- **FLAG 2 — universe (D261).** D261 forbids a survivorship-biased universe *without approval*. The only daily universe available without new infrastructure is the vendor universe above, with its measured gap.
  - D304 asks for "sensitivity to the known universe-quality limitations". That is read as approving this universe, with the limitation disclosed, **for this single exploratory comparison only**.
  - Mitigation: the primary A-vs-B question is a **paired, same-universe** comparison (§5), so a universe gap common to both arms largely cancels.
  - The SPY comparison does not cancel. It is judged with the bias bounds in §5.4.
- If the owner reads either flag differently, the results stay recorded and are used for nothing else.

## 3. Exact rules (unchanged from `research/hypotheses/H006.md` v1.0 except the time stop in B)

- **Entry:** at the close of day T, all three must hold:
  - close_T > the highest high of T−55 … T−1;
  - volume_T ≥ 1.5 × the mean volume of T−50 … T−1;
  - close_T > SMA200.
- **Ranking:** (close_T − prior 55-day high) / ATR20, highest first; ties go by security id.
- **Exit (signal at a close, sell at the next open):**
  - **chandelier:** close_T < (highest close since entry) − 3.0 × ATR20;
  - **A only:** sessions held ≥ 60.
- **Highest close since entry:**
  - while sessions held + 1 ≤ the 260-bar window: read from the window, as the original code did;
  - beyond the window: carried, as max(previous peak re-expressed in today's adjusted price units, close_T).
  - The re-expression uses the ratio of the stored peak to the close at the time it was stored, so splits and dividend re-adjustments of the window carry over exactly.
- **Portfolio and execution:** 10 slots, equal weight, D051 execution model:
  - 10% cap, $5,000 minimum, 2% cash buffer, 15% gap reserve, settled cash only;
  - $100,000 start;
  - $7 per order plus 10 bps slippage per side;
  - T+1 open fills, raw prices for fills and adjusted prices for signals;
  - general delisting, D054 and D062 rules.
- **Window:** `DEV` 2010-01-04 → 2021-12-31, no warm-up. That is H006's original start, run to the end of development data. Eligibility needs 20 sessions of ADV, so the first trade is in February 2010, as in E006-01.
- **Params:**
  - A = `{n: 55, vol_mult: 1.5, use_volume: true, k: 3.0, time_stop: 60, slots: 10}`;
  - B = the same with `time_stop: null`.

## 4. Metrics (computed by the frozen `research/tt/h006_exit/H006X_eval.py` from the three runs' equity, fills and trades)

All results are after costs, on the same dates; SPY = E900-08.

1. **Wealth:** terminal wealth, CAGR, and B / A, B / SPY, A / SPY.
2. **Paired difference B − A:** monthly log-return difference; mean, Newey–West (lag 6) t-statistic; per year; for each half (2010–2015, 2016–2021).
3. **Capture:** monthly upside capture (SPY-positive months) and downside capture (SPY-negative months), as the ratio of mean returns.
4. **Beta-adjusted:** OLS of monthly excess returns over cash (0) on SPY's. Report beta, annualised alpha and its Newey–West t-statistic, and the information ratio vs SPY.
5. **Risk:** maximum drawdown, annualised volatility, Sharpe (rf 0).
6. **Holding:** mean, median, 90th percentile and maximum sessions held per closed trade, plus positions still open at the end. Also the share of B trades exceeding 60 / 126 / 252 sessions.
7. **Turnover and costs:** traded value / average equity per year; commissions ($7 × orders); slippage (10 bps × traded value); total cost as % of average equity per year.
8. **Concentration:**
   - net P&L share of the top 1 / 5 / 10 stocks (trades summed by security);
   - P&L by calendar year;
   - share of the largest single year in the positive annual log-differences B − A.
9. **Universe sensitivity:**
   - halves 2010–2015 (confirmed vendor gap 3.5–6.1%) vs 2016–2021 (0.8–2.9%);
   - P&L from trades ending by delisting / dead-position close;
   - the excess over SPY compared with RR5 / RR6 bias bounds.
10. **Taxes (descriptive):** share of realised gains on trades held > 365 calendar days. Illustrative only; no tax model.
11. **Drift diagnostic:** A's 2010-01-04 → 2017-12-29 sub-path vs E006-01 (old dataset); CAGR, trades, Sharpe. Not a gate.

## 5. Pre-declared answers (fixed now; no thresholds change after results)

### 5.1 Does removing the time limit add meaningful value? **YES** only if all of:
- **V1:** W_B / W_A ≥ 1.10 (about +0.8 points a year over 12 years).
- **V2:** B − A cumulative log-wealth difference > 0 in **both** halves.
- **V3:** no single calendar year supplies more than 50% of the sum of positive annual B − A log-differences.

Otherwise: **NO** (if W_B ≤ W_A) or **NOT MEANINGFUL** (if W_B > W_A but V1–V3 not all met).

### 5.2 Does B beat SPY?
**YES** if W_B > W_SPY (terminal wealth, same dates, after costs). Same for A, reported.

### 5.3 Robust enough to justify seeking independent evidence? **YES** only if all of:
- **R1:** 5.1 = YES and 5.2 = YES.
- **R2:** CAGR_B − CAGR_SPY ≥ +1.0 point a year. This is the EDP-1 E4 margin. It exceeds the largest confirmed RR5 universe bias (0.78) and sits within RR6's upper bounds of 0.56–1.26.
- **R3:** B ahead of SPY in log-wealth in **both** halves.
- **R4:** beta-adjusted alpha of B > 0.
- **R5:** B's top 5 stocks supply < 50% of its net P&L.

Otherwise **NO**, and the recommendation is **closure** (no parameter variations).

### 5.4 Universe caveat
Every SPY comparison is labelled exploratory and vendor-universe-biased. The A − B difference is reported as the primary, universe-robust result.
