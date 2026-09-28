# CP2 AMENDMENT — Official research period from 2010

| Field | Value |
|---|---|
| Date | 2026-09-28 |
| Status | **Awaiting owner approval. STOPPED.** No strategy research has started. |
| Owner decision implemented | D033: MarketCap ≥ $2B universe on the new dataset, from 2010 only; the size proxy is rejected; 1999–2009 is only an optional stress test for finalists (D035); no data purchase |
| Proposed for approval | D034 (the split), D036 (the adjusted gates), plus D023–D025 (standard settings), which are still open from CP2 |

## 1. Proposed split

| Segment | Dates | Length | Role |
|---|---|---|---|
| **Research / In-Sample (IS)** | 2010-01-04 → 2017-12-31 | 8 years | Discovery, variation choice, robustness |
| **Validation / Out-of-Sample (VAL)** | 2018-01-01 → 2021-12-31 | 4 years | One frozen pass per promoted candidate |
| **Walk-forward (WF)** | 2010 → 2021, expanding window, 8 annual test folds 2014 … 2021 | 12 years | Tests the *selection process*. Each fold has ≥ 4 training years; parameters are picked by a rule fixed in advance. Evaluation only; every fold counts as a trial. |
| **Final Holdout** | **2022-01-01 → 2026-08-31** (unchanged, still locked) | 4.7 years | Once, after CP5 approval |
| Optional STRESS | 1999-01-04 → 2009-12-31 | 11 years | Finalists only, imperfect universe, report only; never used for selection (D035) |

**Enforced in code:**

- Research and benchmark runs cannot start before 2010-01-04.
- Research must use IS, VAL, WF or HOLDOUT.
- The 1999–2009 window accepts only kind `stress`, which must name a finalist and is excluded from the trial count.
- The holdout lock (no end date after 2021-12-31 without `HOLDOUT_UNLOCK.md`) is unchanged, in both the runner and the QuantConnect-side harness.
- New tests cover all of this: 92 of 92 pass.

## 2. Why this split

- **The holdout stays exactly as approved at CP1.** It is the most recent 4.7 years and has never been touched: no run has ever used a date after 2021-12-31. Moving it would waste its untouched status.
- **The universe is reliable from October 2009.** In the audit (E951-03), MarketCap coverage jumps from about 40 names to about 650 in July–October 2009 and is stable afterwards. 2010-01-04 leaves a three-month margin; indicator warm-up can still use earlier prices.
- **8 years of IS versus 4 of VAL.**
  - Discovery needs the longer piece.
  - 8 years is the minimum for a Sharpe estimate with an error of about ±0.4.
  - VAL gets two genuine stress episodes, the 2018 Q4 sell-off and the 2020 crash, which IS lacks. Validation therefore tests exactly what IS could not show.
- **Alternatives considered:**
  - IS 2010–16 / VAL 2017–21: VAL gains a calm year (2017) but IS loses a year of discovery. Rejected.
  - IS 2010–18 / VAL 2019–21: VAL of 3 years is too short (Sharpe error about ±0.6). Rejected.
  - Moving 2022 into VAL: shortens and "uses up" the holdout. Rejected.

## 3. What we lose by dropping 1999–2009

- **Two full bear markets and a crash regime:**
  - the 2000–02 dot-com bust;
  - the 2007–09 financial crisis (SPY −54% peak to trough over 1999–2009, with a CAGR of only 0.8%).
- **A friendly in-sample period.**
  - SPY in 2010–2017 had **no losing calendar year** (worst +1.3%), a maximum drawdown of −18%, and a Sharpe of 0.94.
  - That period was also near-zero interest rates and QE almost throughout.
  - Long-only strategies will tend to look good in IS. That is why every gate is measured **relative to the equal-weight benchmark**, which returned 14.6%/year with a Sharpe of 0.95 in IS.
- **Statistical power:**
  - 12 years of IS + VAL instead of 23.
  - The standard error of an annual Sharpe estimate rises from about 0.27 (16 IS years) to about 0.38 (8 IS years).
  - Fewer strategies can be tested before multiple-testing penalties dominate.
- **No rising-rate regime** anywhere before the holdout (2022). The holdout will be the first test in that environment. That makes it an honest test, but also a harder one.
- Ideas can still be stress-tested on 1999–2009 later (finalists only, imperfect universe), but that evidence cannot promote anything.

## 4. What we gain

- **Faithful universe definition.** Point-in-time Morningstar MarketCap ≥ $2B exactly as you specified, not a liquidity approximation (no high-turnover tilt, no 9% ETF/ADR contamination).
- **Much better coverage.**
  - About 650–1,500 eligible names per month, on data that QuantConnect will support after the 2026-10-31 retirement of the old dataset.
  - MarketCap values now use filing dates, which removes a look-ahead in the old feed.
- **One consistent dataset** for IS, VAL, walk-forward and holdout, so strategies behave the same way in every segment.
- **Remaining limitation, disclosed.**
  - Even from 2010, securities that later ended (Time Warner, Heinz, Sears, Alcoa before its 2016 split, …) have no fundamentals, so they are missing while they traded.
  - Estimated at about 10% of true ≥ $2B names in 2010–14, less later.
  - This is a residual survivorship bias in our favour. It cannot be removed without buying data.
  - Every strategy report will state it, and gates are relative to a benchmark built on the same universe, which partly cancels it.

## 5. Gate adjustments for the shorter history (proposed, D036; replaces D026)

| Gate | CP2 proposal | Adjusted proposal | Why |
|---|---|---|---|
| IS: trades | ≥ 100 closed trades | unchanged | Enough for a swing strategy in 8 years |
| IS: Sharpe | ≥ 0.5 and ≥ EW Sharpe + 0.1 | **≥ EW benchmark Sharpe + 0.1**, plus the absolute floor of 0.5 | EW's IS Sharpe is 0.95, so the relative condition is the one that binds in a bull period |
| IS: drawdown | ≤ 35% and no worse than EW | unchanged, **plus** in each IS episode (2010 May–Jun, 2011 Jul–Oct, 2015 Aug–2016 Feb): drawdown no more than 5 points worse than EW's | IS has no deep bear market, so check the three stress windows it does have |
| IS: consistency | positive in ≥ 60% of years; each IS third positive | positive in **≥ 5 of 8** years; each third (about 2.7 years) positive | Same rule, stated for 8 years |
| Robustness | plateau ±20–50%; Sharpe > 0 at 4× costs | unchanged | |
| VAL | Sharpe ≥ 0.4 and ≥ 50% of IS Sharpe; beats EW; max DD ≤ 35% | unchanged, **plus ≥ 50 closed trades in VAL**, and VAL max drawdown no worse than EW's in 2020 Feb–Mar + 5 points | 4 years is short; require a minimum sample and test the crash explicitly |
| Deflated Sharpe | ≥ 0.90 | ≥ 0.90, computed on **IS + VAL combined (12 years)** with the full trial count | More power than VAL alone; the penalty for trials is kept |
| PBO | ≤ 0.30 | unchanged (CSCV on IS) | |
| **Walk-forward** (new, explicit) | — | aggregate out-of-sample Sharpe across the 8 folds ≥ 0.3, **and** ≥ 5 of 8 folds positive | Tests the process, not one parameter set |
| Holdout | defined before CP5 | unchanged | |
| Research budget | "a few hundred" experiments | **≤ about 200** before a checkpoint review | A shorter history makes each extra trial more costly |

## 6. Throughput

- Measured at CP2: about 33 s of backtest time per year of history for a full ≥ $2B universe backtest (E901-01: 12 years in 391 s).
- So an IS run takes about 4–5 minutes, a VAL run about 2–3 minutes, and a walk-forward fold 1–3 minutes.
- Only one backtest runs at a time. That gives **about 12–20 research backtests per hour, 150–300 per day**, far above a budget of about 200 experiments. **Sufficient**, and no extra node is needed (D002 stands).
- **New constraint discovered:** QuantConnect's **daily log allowance (about 3 MB)**.
  - The heavy size-proxy runs exhausted it, and it did not reset at midnight UTC.
  - Research runs log only a few KB each (the harness summary and held-position splits), so about 300 or more per day fit easily.
  - I will keep diagnostic logging small. The runner will check the remaining allowance before starting a run, so a run is not lost the way E953-03 was.

## 7. Housekeeping done in this amendment

- **Code:**
  - Split schemes (`cp1` kept for history, `2010` current).
  - Date rules; the `stress` kind; new tests.
  - The holdout lock is unchanged.
- **Benchmarks** re-configured for 2010-01-04 → 2021-12-31: E900-03 (SPY) and E901-02 (EW, with the D029/D030 fixes). They are **not yet run**: the log allowance was still exhausted. They run first when the campaign is approved.
- **Size proxy.** Kept in GitHub as history and marked **REJECTED for the primary universe** (`docs/data/size_proxy_evaluation.md`). Its unrun v1.1 re-runs were cancelled (D038).
- **Documents updated:** `RESEARCH_PLAN.md`, `DECISIONS.md` (D033–D038; D004, D026, D027 and D031 re-statused), `CLAUDE.md`, and a pointer in the CP2 report.

## 8. Confirmation

- **No strategy research has started.**
  - The registry contains 0 hypotheses, 0 research strategies and 0 research experiments.
  - All 16 registered runs are infrastructure (11), benchmark (3) or pipeline-demo (2) runs.
- No data has been purchased.
- No date after 2021-12-31 has ever been run.

## 9. Decisions requested

| # | Decision | Recommendation |
|---|---|---|
| 1 | Approve the split in §1 (D034) | **Approve** |
| 2 | Approve the adjusted gates in §5 (D036) | **Approve**, or amend |
| 3 | Approve the standard settings still open from CP2 (D023–D025): price ≥ $5, 20-day ADV ≥ $5M, 10 bps slippage per side, ≤ 10% per position, ≤ 20 positions | **Approve** |
| 4 | Then authorise the first research cycle (CP3), starting with the two benchmark runs | Your call |
