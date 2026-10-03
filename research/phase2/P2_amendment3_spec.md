# Phase 2 Methodology Amendment 3: terminal-wealth evaluation framework (FROZEN)

- **Status:** FROZEN 2026-10-03 (D121), before any new hypothesis is selected or run.
  - The SHA-256 of this file is pinned in `qresearch.wealth.AMENDMENT3_SHA256` and checked by `tests/test_wealth.py`.
  - Any later change means: STOP and obtain owner approval.
- **Authority:** the owner's approval of Amendment 3 with two refinements (2026-10-02; `docs/owner/2026-10-02_amendment3_refinements_preparatory_studies.md`).
- **Implementation:** `src/qresearch/wealth.py`; the constants equal those below.
- **Calibration:** `research/phase2/architecture/P2_amend3_calibration.py/.json`.
  - It uses completed CONTROL books only: SPY, the same-universe EW, and five random 20-stock books, 2010-03 → 2021-12.
  - No candidate or factor returns were used.
- **What it replaces for every future Phase 2 hypothesis:**
  - development gates G1–G3;
  - the P2-CP10 G1.5 / HO4 proposal;
  - the Holdout criteria HO1–HO3.
- **Unchanged:**
  - the hypothesis budget (3; 2 consumed);
  - one Holdout use;
  - the forward test;
  - DSR and PBO as diagnostics;
  - data infrastructure v1;
  - every closed result (H014, H016).

## 1. Objective

**Starting with the same capital on the same date, the strategy's terminal wealth must exceed S&P 500 buy-and-hold total return (SPY with dividends reinvested), after realistic costs and without leverage.**

- **Primary account:** $100,000. $200,000 is a sensitivity only; it never selects, decides or rescues.
- **Not required:** beating SPY in every year or rolling window.

## 2. Primary economic table (first item of every candidate report)

Starting capital; Final strategy value; Final SPY value; Strategy total return; SPY total return; Strategy CAGR; SPY CAGR; Excess CAGR; **Terminal wealth ratio = final strategy value / final SPY value** (`wealth.wealth_table`).

## 3. Development gates (all must pass; common development window; $100K base run)

The window runs from the first portfolio date to the end of development.

| Gate | Exact rule |
|---|---|
| **W1 objective** | CAGR(H) > CAGR(SPY), equivalently terminal wealth above SPY's over the same dates |
| **W2 evidence** | g ≥ **2.15** × SE. Here d_t = ln(1 + r_H,t) − ln(1 + r_SPY,t) (daily), and g = 252 × mean(d) is the annualised growth of the log wealth ratio. SE = **max**(SE_iid, SE_SB). SE_iid = 252 × sd(d) / √n. SE_SB is the exact stationary-bootstrap standard error of the mean (Politis & Romano 1994, Lemma 1): 252 × √{[C(0) + 2 Σ_{k=1}^{n−1} b(k) C(k)] / n}, with b(k) = (1 − k/n) q^k + (k/n) q^{n−k}, q = 1 − 1/126, and C the ordinary (1/n) sample autocovariances. Deterministic (no Monte Carlo) |
| **W3 attribution** | CAGR(H) > CAGR(EW of the exact same universe) **and** CAGR(H) > the median CAGR of the five matched random books (same universe, positions, schedule, costs and mechanics; only the selection is random; seeds fixed before any run). Fewer than five completed random books means W3 fails |
| **R1 drawdown** | MaxDD(H) ≥ MaxDD(SPY) − 0.10, i.e. at most 10 percentage points deeper |
| **R2 risk-adjusted** | Sharpe(H) ≥ Sharpe(SPY) − **0.15** (Sharpe = mean / sd of daily returns × √252) |
| **R3 no single lucky period** | The total log excess Σ d_t > 0, and no calendar two-year block (2010–11, 2012–13, …; a partial first block counts as a block) contributes more than half of it |
| **R4 implementation** | Realised costs ≤ 1.5% a year at base costs (commissions + traded notional × slippage); no leverage (harness integrity check); the account and concentration limits of the hypothesis's frozen spec |
| **G4′ robustness** (run only if W1–W3 and R1–R4 pass) | At least 5 of the 6 pre-declared perturbations keep W1; at 2× slippage W1 still holds |

- **Any gate that cannot be evaluated fails.**
- **The old "Sharpe(H) ≥ Sharpe(EW) + 0.25" is retired as a gate** and reported as a diagnostic, together with Sharpe(H) − Sharpe(SPY), DSR (frozen formula and counts) and PBO where computable.

## 4. Holdout and forward confirmation (only for a candidate that passed §3, with written owner approval)

- **Window:** 2022-01-01 → 2026-08-31, used once.
- **HO-W:** CAGR(H) > CAGR(SPY) over the Holdout.
- **HO-R:** R1 over the Holdout.
- **Reported, not gated:** 2022 and 2023-01-01 → 2026-08-31 separately (the hindsight split); every §2/§5 statistic.
- **Exception, frozen now:** for a hypothesis with a market-timing or defensive (cash-raising) component, CAGR(H) > CAGR(SPY) must also hold in 2023-01-01 → 2026-08-31 alone.
- **The forward test** (data after the freeze, only after owner approval) uses HO-W and HO-R.

## 5. Rolling-horizon reporting (never a gate)

For 1, 3, 5 and 10 years, over every start date (`wealth.rolling_report`), report:
- the share of start dates on which the strategy ended with more wealth than SPY;
- the mean and median excess CAGR;
- the 10th and 90th percentiles;
- the worst and best windows;
- the number of independent windows (years / horizon).

**Always shown beside:**
- the same-universe EW;
- each of the five random books, as the luck band.

Win rates are never converted into gates. Windows from a sample shorter than twice the horizon (e.g. 10-year windows on 12 years) are labelled **not evidence**.

## 6. Other required reporting

- Volatility; Sharpe; max drawdown; Calmar; worst calendar year (absolute and vs SPY); longest recovery period (sessions below the previous peak).
- Turnover; costs (commissions and slippage separately); largest position and sector weights; mean, minimum and invested cash.
- The $200K sensitivity; 4× and 6× slippage (reported); yearly and two-year-block tables vs SPY, EW and each random book.

## 7. Calibration summary

Completed control books only (`P2_amend3_calibration.json`).

**Dependence:** the excess returns of 20-stock books over SPY mean-revert at long horizons. The one-year variance ratio is 0.58–1.08 (mean 0.76).

**W2 false-pass rates at zero true edge:**

| Relative-performance process | iid SE, z 1.645 | Frozen W2 |
|---|---|---|
| Control-like (resampled; mean blocks 21–504 sessions) | 1.9–4.9% | 0.4–1.4% |
| Persistent drift: one-year variance ratio 1.25, half-life ≈ 1 year | 11.4% | **4.6%** |
| Persistent drift: one-year variance ratio 1.5 | 10.7–15% | 3.3–7.0% |
| Persistent drift: one-year variance ratio 2.0 | 15.8–21.5% | 5.1–10.4% |

The critical value 2.15 is the 95th percentile of the W2 statistic under the most persistent process inside the declared envelope (variance ratio ≤ 1.25, half-life ≤ about 1 year), rounded up. Stronger persistence is left to G4′, the Holdout and the forward test.

**R2 tolerance:**
- The standard deviation of Sharpe(book) − Sharpe(SPY) for no-edge 20-stock books over 12 years is **0.137**.
- 0.15 ≈ 1 SE: the midpoint between "no deficit" and a material true deficit of 0.30 (about one-third of SPY's Sharpe).
- Error rates are ≈ 14% each way: wrongly rejecting a candidate whose true Sharpe equals SPY's, and wrongly passing one 0.30 worse.
- At +3% a year excess return, R2 allows at most ≈ 1.43× SPY's volatility.

**Full framework, 12 years, 20 positions** (W1–W3, R1–R3; R4 and G4′ not modelled, so these are upper bounds):

| True edge over SPY | 0% (false pass) | 1% | 2% | 3% | 4% | Edge for 50% | Edge for 80% |
|---|---|---|---|---|---|---|---|
| Pass probability | 0.3% | 1.1% | 2.6% | 7.1% | 16.3% | ≈ 6.3% | ≈ 8.6% |

With 40 positions the edges for 50% / 80% are ≈ 5.1% / 6.9%.

## 8. Prohibitions

- No change to any rule, constant or definition here after any candidate result.
- No gate is added, removed or re-weighted per hypothesis.
- The random seeds, perturbations and costs of a hypothesis are fixed in its own frozen spec before its first run.
