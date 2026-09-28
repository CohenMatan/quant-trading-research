# RESEARCH_PLAN.md

**Status.**

- Approved at CP1: universe threshold and account size.
- CP2 infrastructure approved on 2026-09-27.
- On 2026-09-28 the owner decided the official research period is **2010 onward**, with the original MarketCap universe (D033).
- **Pending owner approval:**
  - the exact 2010+ split below (D034);
  - the standard settings and adjusted gates in `docs/checkpoints/CP2_amendment_2010_split.md`.
- **No research campaign has started.**

## 1. Objective

Identify at most one simple, explainable, robust long-only swing-trading strategy on US equities with point-in-time market cap ≥ $2B that passes every validation stage below. Otherwise, report **"No Production Candidate Found"**.

## 2. Universe (fixed across all strategies)

- **Data:** the new QuantConnect/Morningstar dataset only (LEAN build pinned per experiment), from 2010 onward.
- **US common stock:**
  - Morningstar common stock, not a depositary receipt;
  - primary share **or** a US-domiciled company (D030);
  - listed on NYSE, Nasdaq or AMEX.
  - ETFs, ADRs and OTC stocks are excluded.
- **Size:** eligible on day T if the point-in-time `MarketCap` (as of the T−1 close) is **≥ $2B nominal**. An inflation-adjusted threshold is used only as a robustness check.
- **Tradability:** raw price ≥ $5, and 20-day average daily dollar volume ≥ $5M (D023, proposed). These are fixed once and never tuned per strategy.
- **Daily rebuild:** the universe is rebuilt daily from the securities that existed on that day.
- **Size proxy:** **not used.** It was rejected for the primary universe (D033). Its evaluation is kept as research history in `docs/data/size_proxy_evaluation.md`.
- **Known residual limitation:** even from 2010, securities that later ended have no Morningstar fundamentals, so some large companies are missing from the universe while they traded. The CP2 size-proxy work estimated this at roughly 10% of true ≥ $2B names in 2010–14, and less later. It cannot be fixed without buying data, which is out of scope. Strategy reports state this.

## 3. Data split (proposed, D034)

| Segment | Dates | Years | Use |
|---|---|---|---|
| **IS** (research/training) | 2010-01-04 → 2017-12-31 | 8.0 | Exploration; choosing among a few pre-declared variations; robustness battery |
| **VAL** (validation, out-of-sample) | 2018-01-01 → 2021-12-31 | 4.0 | One frozen-parameter pass per promoted candidate |
| **Walk-forward (WF)** | 2010-01-04 → 2021-12-31 | 12.0 | Expanding training window from 2010. Annual test folds 2014, 2015, …, 2021 (8 folds, ≥ 4 training years each). Parameters are chosen in each training window by a rule declared in advance. It reuses IS and VAL years for *evaluation only*; every fold counts as a trial. |
| **HOLDOUT** | **2022-01-01 → 2026-08-31** | 4.7 | Unchanged from CP1. Used once, after CP5 approval, on frozen strategies only. |
| **STRESS** (optional) | 1999-01-04 → 2009-12-31 | 11.0 | Only for **finalists**, on an imperfect alternative universe (e.g. the size proxy). **Never** used for optimisation, parameter selection or promotion (D035). |

Rules:

- **Warm-up.** Indicators use price data before each segment's start, including before 2010. Warm-up bars never generate trades. Universe membership is reliable from October 2009 (data audit E951-03), so it is available on 2010-01-04.
- **Holdout lock (unchanged).**
  - The runner and the LEAN harness reject any end date after 2021-12-31 unless `HOLDOUT_UNLOCK.md` exists.
  - That file is created only after owner approval at CP5, and records the frozen commits.
- **Date rules enforced in code** (`config.py`, `experiment.py`):
  - Research and benchmark runs cannot start before 2010-01-04.
  - Research runs must use IS, VAL, WF or HOLDOUT.
  - The 1999–2009 window is reserved for kind `stress`, which must name a finalist and is excluded from the trial count.
  - New runs must use split scheme `2010`; CP1-scheme configs remain as history.

## 4. Execution model

- The signal uses day T's completed daily bar. The order is **market-on-open on T+1**.
- Long-only. No leverage, enforced by the harness's cash planning (D015).
- Position sizing is defined per strategy, within fixed portfolio constraints (D025, proposed):
  - at most 10% per position at entry;
  - at most 20 positions;
  - 2% cash buffer;
  - minimum position $2,000.
  - Proposed change D041: minimum $5,000 and at most 15 positions.
- **Costs (D039).** Every reported metric is net of both commission and slippage.
  - **Commission: $7 per executed order, buy or sell** ($14 per normal round trip).
    - An order filled in pieces is charged once.
    - Entering or exiting with several separate orders is charged per order.
  - **Slippage (separate):** 10 bps per side (D024, proposed). Stress runs at 2×, 4× and 6×.
  - Commission sensitivity: a stress run at $10 per order is also reported for finalists.
- Corporate actions: fills use raw prices, dividends are credited as cash, signals use point-in-time adjusted history. Delistings liquidate at the last price.
- Assumed account size: $100,000 (approved at CP1).

## 5. Research loop

```
Hypothesis (H###) → Strategy (S###) → Exploration on IS 2010–2017 (3–10 variations)
  → Analysis → Reject / Continue
  → Robustness on IS (parameter plateau, sub-periods, regimes, costs, trade distribution)
  → Validation (VAL 2018–2021, frozen) → Walk-forward (2010–2021, pre-declared selection rule)
  → Realistic LEAN checks → CP4 → Freeze
  → [optional STRESS 1999–2009, report only] → CP5 approval → HOLDOUT once
  → Production Candidate / Reject
```

## 6. Metrics (computed locally from the equity curve and trades)

- CAGR, annualized return, and annualized volatility.
- Max drawdown and its duration.
- Sharpe, Sortino and Calmar ratios.
- Profit factor, win rate, average winner, average loser and expectancy.
- Number of trades, average holding period, exposure and turnover.
- Worst year, worst month, and performance by year.
- Benchmark-relative figures: excess CAGR, beta and correlation.
- Multiple-testing indicators:
  - **Deflated Sharpe Ratio**, using the registry's trial count.
  - **Probability of Backtest Overfitting**, using CSCV across a hypothesis's variations.
  - IS→VAL degradation.

Benchmarks, both over 2010-01-04 → 2021-12-31 and reported per segment:

- **B900** SPY buy-and-hold, total return, on a $100K account with the same costs as strategies (E900-03).
- **B901** equal-weight ≥ $2B universe, monthly rebalance (E901-02). It replaces E901-01, which used the pre-D030 universe rule.
  - Same cost model, but on a **$10M notional** account.
  - Holding about 1,000 names on $100K with a $7 fixed fee per order is not a meaningful portfolio (commissions alone would be several percent a year).
  - B901 therefore measures the universe's own return, with costs immaterial.

## 7. Robustness battery

- **Parameter stability:** ±20–50% perturbations around the chosen parameters. We need a plateau, not a single peak.
- **Time stability:** sub-period (thirds of IS) and per-year results.
- **Regimes:**
  - Bull and bear markets, defined by SPY relative to its 200-day moving average and by drawdown periods.
  - High and low volatility, defined by realized-volatility terciles.
  - Named episodes:
    - IS: 2010 May–Jun (flash crash), 2011 Jul–Oct (US downgrade), 2015 Aug–2016 Feb (China and oil).
    - VAL: 2018 Q4, 2020 Feb–Mar (COVID).
    - HOLDOUT only: 2022.
- **Costs:** slippage stress at 2×, 4× and 6× the base; also a higher commission assumption.
- **Trade distribution:**
  - Share of profit from the top 1%, 5% and 10% of trades.
  - Performance with the best N trades removed.
  - A bootstrap confidence interval on expectancy.

## 8. Promotion gates

- The proposed values are in `docs/checkpoints/CP2_amendment_2010_split.md` §5, adjusted for the shorter history. They await owner approval.
- Gates are fixed *before* the data they apply to is examined.
- STRESS results never enter any gate.

## 9. Research budget (first campaign)

- Tens of hypotheses, 3–10 variations each, and **at most about 200 experiments** before a checkpoint review.
- The limit is tighter than at CP1 because the shorter history makes multiple testing more costly.
- Any expansion must be justified to the owner first.

## 10. Hindsight control

- Every hypothesis must cite a rationale that does not depend on knowledge of market events **after 2017**, the end of IS.
- Validation-era (2018–2021) and holdout-era (2022+) events may not motivate hypotheses, e.g. the 2018 Q4 sell-off, the 2020 crash, the 2021 mania, 2022, or the 2023–24 AI rally.
- **Disclosed prior exposure** (from CP2 infrastructure runs; no strategy results):
  - SPY and equal-weight benchmark returns for 2010–2021.
  - The S000 demo on 2010–2014 (short-term reversal).
  - Universe-level forward returns for 2010–2014 (size-proxy evaluation).
  - Universe membership statistics for 2015–2021.
