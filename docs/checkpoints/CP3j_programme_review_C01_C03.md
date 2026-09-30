# Research programme review: C01, C02 and C03

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **STOP. Awaiting owner decision on the future of the project.** No new cycle has started, and no backtest was run for this review. |
| Scope | All three cycles, all 40 official selection candidates, the Validation run, the diagnostics and the method studies. |
| Data | Committed, derived in-sample results only (2010-01-04 → 2017-12-29). The single Validation result (C01, E005-28) is quoted from its published report, unchanged. Benchmarks are cut to the in-sample dates before use. No Validation, Walk-Forward or Holdout data is used. |
| Evidence | `research/cycles/programme_review.py` produces `programme_review.json` (one uniform table), plus every cycle's own reports. Official verdicts are **not** recomputed or changed. |
| C03 | Closed by the owner: **No Production Candidate Found**. |

## 1. Bottom line

1. **Twelve hypotheses and 40 pre-declared selection candidates were tested with realistic trading. None survived.**
   - One hypothesis (H012) could not be evaluated reliably and was withdrawn untested.
   - Four candidates passed the in-sample screen. Three of them (H005) later failed at Validation or were not chosen for it, and one (H007 v1.1) failed robustness.
2. **Most candidates made money, but almost none beat simply holding the market** (2 of 40 on return, 6 of 40 on Sharpe).
   - Median result: Sharpe 0.58 and 7.3% a year.
   - The passive equal-weight universe (EW) earned 13.9% a year at Sharpe 0.92; SPY earned 13.3% at Sharpe 0.95.
   - The median candidate even did worse than a **random** portfolio with the same structure (Sharpe 0.72–0.90).
3. **Two causes dominate:**
   - **Trading costs.** The fixed $7 per order plus slippage cost 0.5%–14% a year. Across candidates the correlation between cost drag and Sharpe is −0.80.
   - **Portfolio structure.** With 10–15 slots, idle cash and the cash buffers, a portfolio with no skill at all already trails EW.
4. **The statistics are demanding, and that limits what more cycles can achieve.**
   - With 8 years of in-sample data, only large edges can be confirmed.
   - Every new candidate raises the bar: the Deflated Sharpe hurdle over IS + VAL rises from about 1.44 at N = 40 to about 1.57 at N = 80.
   - Our results show that no **large** edge exists among these ideas in this setting. They **cannot** exclude modest edges, which our data is too short to detect.
5. **Conclusion: continuing the same kind of research under the current constraints is not justified.** The original objective should be reconsidered (§7–§8).

## 2. What was tested

| # | Hypothesis | Cycle | Candidates | Sharpe range | Yearly return range | Cost drag per year | Outcome |
|---|---|---|---|---|---|---|---|
| H001 | Short-term oversold reversal (RSI) | C01 | 5 | −0.82 to 0.20 | −7.7% to 1.8% | 6.4–14.0% | 4 lost money; rejected |
| H002 | Price momentum | C01 | 4 | 0.38–0.56 | 5.7–9.2% | 0.7–1.3% | failed screen |
| H003 | 52-week-high proximity | C01 | 3 | 0.14–0.73 | 0.8–5.7% | 1.9–4.5% | failed screen |
| H004 | Momentum pullback | C01 | 4 | 0.03–0.46 | −1.4% to 8.2% | 4.1–7.5% | 1 lost money; failed screen |
| **H005** | **Low volatility** | C01 | 3 | **1.23–1.44** | 8.1–10.4% | 0.5–1.1% | **all 3 passed the screen**; v1.2 **failed Validation** (DSR 0.68, PBO 0.71) |
| H006 | Breakout | C02 | 3 | 0.74–0.90 | 9.8–12.3% | 1.8% | failed screen |
| H007 | Volatility squeeze | C02 | 3 | 0.50–1.12 | 5.4–6.0% | 0.9–3.5% | v1.1 **passed the screen**, then **failed robustness** (5/8) |
| H008 | Residual relative strength | C02 | 3 | 0.57–0.69 | 9.2–14.9% | 0.9–2.0% | failed screen |
| H009 | Volume shock | C02 | 3 | 0.67–1.01 | 9.1–14.4% | 1.6–3.2% | failed screen (best 1.01; the bar is 1.02) |
| H010 | Gap and hold | C02 | 3 | 0.51–0.68 | 6.1–8.6% | 1.9–3.3% | failed screen |
| H011 | Seasonality | C02 | 3 | 0.17–0.67 | 1.3–11.2% | 2.8–3.2% | failed screen |
| H012 | Volatility-managed exposure | C03 | — | — | — | — | **not evaluable** with sufficient statistical power; withdrawn untested |
| H013 | Lottery-stock avoidance | C03 | 3 (× 3 seeds) | 0.76–0.80 (seed means) | 10.6–10.7% | 1.3% | failed screen on all 9 seeds; effect refuted against its random pair |

In-sample benchmarks (2010–2017):

| Benchmark | Sharpe | Yearly return | Max drawdown |
|---|---|---|---|
| Equal-weight ≥ $2B universe (EW) | 0.92 | 13.9% | −22.3% |
| SPY | 0.95 | 13.3% | −18.3% |
| No-skill random portfolios (15 slots, hold 60, $100K, 3 seeds) | 0.72–0.90 | 10.5–13.4% | — |

**Programme totals:**

- 12 hypotheses tested and 1 withdrawn untested; 12 research strategies.
- 40 official selection candidates; 213 experiment IDs; 218 registry runs.
- The 218 runs comprise 132 research, 63 infrastructure/verification, 14 benchmark, 6 sizing and 3 demo. Every failed, superseded and bugged run is preserved.
- About 26 hours of backtest compute.

## 3. The three kinds of outcome requested

**A. Lost money** (in-sample yearly return ≤ 0 after costs): **5 of 40.**

- H001 v1.0, v1.1, v1.3 and v1.4, and H004 v1.1.
- **All five were profitable before costs.** High turnover (28–60 times the portfolio a year) at $7 an order plus slippage cost 6–14% a year, which turned a small gross profit into a loss.

**B. Profitable, but below the passive benchmark and failing our requirements: 29 of 40.**

- These include every candidate of H002, H003, H006, H008, H010, H011 and H013, and most of H004 and H007.
- These strategies made money in a rising market (median 7.3% a year), but less money and less risk-adjusted return than simply holding the equal-weight universe or SPY.

**C. Profitable, above the passive benchmark's Sharpe, but failing a requirement: 6 of 40.**

| Candidate | Sharpe | Yearly return | What stopped it |
|---|---|---|---|
| H005 v1.2 (low volatility) | 1.44 | 8.5% | Passed the screen, then **failed Validation** (2018–2021): VAL Sharpe 0.89 was acceptable, but the Deflated Sharpe was 0.68 (< 0.90) and PBO 0.71 (> 0.30) |
| H005 v1.0 and v1.1 | 1.37, 1.23 | 8.1%, 10.4% | Passed the screen; not chosen for Validation (only the best variation goes forward) |
| H007 v1.1 (volatility squeeze) | 1.12 | 5.4% | Passed the screen; **failed robustness** (5 of 8 perturbations held up; 7 required) |
| H009 v1.1 and v1.2 (volume shock) | 1.01, 1.00 | 14.4%, 13.4% | Failed "Sharpe ≥ EW + 0.10" (1.02 required), plus other items |

**Most of the high Sharpe ratios came from holding less stock, not from earning more.**

- H005 was 68–83% invested and H007 v1.1 only 21%.
- Their returns (5–10% a year) were well below EW's 13.9%.
- A higher Sharpe from lower exposure is real risk reduction. But in a bull market it gives up return, and statistically it is hard to tell apart from luck (§5).

**D. Could not be evaluated reliably: H012** (volatility-managed exposure).

- Our simulation showed that its achievable gain over its own control (at most about +0.05 Sharpe in realistic markets) is smaller than the noise in 8 years of data (about ±0.1).
- It was withdrawn before any backtest, so it is **not** a failed trading hypothesis.

## 4. What we learned

### 4.1 Trading costs decide most outcomes

- With 15 positions of about $6.5K, one round trip costs about $14 in commission (0.2%) plus about 0.2% slippage: **about 0.4% per round trip.**
- A strategy holding positions for 1–4 weeks makes 10–60 portfolio turnovers a year, which costs 2–14% a year.
- Median cost drag across candidates is 2.0% a year; 17 of 40 candidates paid ≥ 3%.
- Before costs, 6 candidates would have matched or beaten EW's return; after costs, only 2 did.
- **The fixed $7 per order at a $100K account is itself a major handicap for swing trading.**
  - The $200K sensitivity in C03 halved the commission drag and lifted Sharpe by about +0.02 for random and H013 portfolios alike.
  - It did not create an edge.

### 4.2 Portfolio structure costs return before any signal

The C03 diagnostics measured this with random, no-skill portfolios:

- 10–15 slots, a 2% cash buffer, a 15% gap reserve, a $5K minimum position and settled-cash buying leave about 15% of the account idle.
- Sampling only 10–15 stocks from about 1,000 adds noise.
- Result: a skill-less portfolio reaches **Sharpe 0.72–0.90 against EW's 0.92**.
- The screen asks for EW + 0.10 (1.02). A strategy therefore needs genuine skill worth roughly **+0.2 to +0.3 Sharpe over random selection** just to reach the screen.
- None of the 40 candidates showed that. Most were **below** random selection with the same structure.

### 4.3 Statistical limits

- **8 years of in-sample data is short.** Differences between random seeds of the same portfolio alone are about ±0.1–0.2 Sharpe.
- **The multiple-testing correction (DSR) grows with every candidate tried.** The observed Sharpe needed over IS + VAL, at the current dispersion:

  | N (candidates tried) | Sharpe needed |
  |---|---|
  | 40 | 1.44 |
  | 50 | 1.48 |
  | 60 | 1.52 |
  | 80 | 1.57 |
  | 100 | 1.61 |

  **Each additional cycle makes success harder.**
- **Power is low for modest edges.** A genuine improvement of +0.10 Sharpe would be detected only about 15–25% of the time (H012 study). Needing 80% power would take about 50 years of data.
- **What the null result means:**
  - It **does** rule out large, robust edges (about Sharpe ≥ 1.4 over IS + VAL) among these 12 ideas in this universe.
  - It does **not** prove that no modest edge exists. Such edges are simply not detectable with our data.
- **The false-acceptance protection worked as designed.**
  - H005's strong in-sample result was stopped by the multiple-testing checks at Validation.
  - H007's by robustness.
  - Nothing was relaxed to pass anything.

### 4.4 The process and infrastructure proved reliable

- Execution was realistic: next-open fills, $7 per order plus slippage, no borrowing, point-in-time universe, delisting handling.
- Every run is reproducible (exact re-runs match by hash) and preserved in the registry.
- Canaries and tests caught real defects before results were relied on: the D063 price windows, the H008 estimation defect, and the S012 warm-up basket.
- **This machinery is the project's durable asset**, whatever is decided about strategy research.

## 5. Economic viability of the current approach

- **What success would look like.** Suppose a strategy just cleared every gate. It would earn perhaps a few percentage points a year above the market, on a $100K account: a **few thousand dollars a year**. It would carry model risk, and its evidence would stay statistically fragile.
- **The passive alternative.** Holding the market (EW or SPY) earned 13–14% a year in-sample, at almost no cost and effort. **38 of 40 candidates earned less than EW** (the exceptions: H008 v1.2 at 14.9% with a Sharpe of 0.67, i.e. more risk; and H009 v1.1 at 14.4% with a Sharpe of 1.01, just short of the 1.02 bar. Both failed the screen).
- **Research cost.**
  - Money is small: QuantConnect costs **$24 a month** ($10 seat + $14 backtest node), about one month so far, well inside the $100 target.
  - The larger costs are owner attention, decision time and the growing multiple-testing burden, which lowers the chance of any future success.
- **Judgement.** For a single $100K, long-only, large-cap, technical-signal, swing-horizon strategy paying $7 per order, **the expected value of further searching is low.** The structure and costs take away most of the room an edge would need, and the data cannot confirm a modest edge.

## 6. Options for the future

| Option | What it means | Money | Research effort | Advantages | Limitations |
|---|---|---|---|---|---|
| **1. Close and archive** | End Phase 1 as "No Production Candidate Found". Cancel QuantConnect. Keep the repository as a reproducible record. | $0 a month | None | Honest, cheap, final. All knowledge preserved. | No further chance of a strategy from this project. |
| **2. Pause** | As option 1, but keep the seat or cancel only the backtest node; revisit only if new information arrives (a better cost structure, new data, a well-founded idea). | $0–10 a month | None until resumed; about 1 day to restart | Keeps the door open at low cost. | Risk of drifting back into more of the same search; the multiple-testing burden remains. |
| **3. One more cycle under current rules** | New hypotheses in the same setting (swing horizon, $100K, $7 per order, technical only). | $24 a month for 1–2 months | About 1–2 weeks of cycles plus reviews | Uses existing infrastructure unchanged. | **Not recommended.** Structural and cost handicaps remain, the DSR bar rises (about 1.5 at N ≈ 50), and power is low. The likely outcome is another "No Candidate". |
| **4. Reconsider the objective: lower-turnover, longer-horizon systematic investing** | Change the scope: monthly or quarterly rebalancing, broader diversification (e.g. 30–100 names or ETFs), longer holding. Possibly a risk-management goal (reconsidering H012-type overlays) instead of beating the market. | $24 a month while active. Possibly $0 extra, if QuantConnect's included US equity and ETF daily data (from 1998) suffices. | New plan and pre-registration (about 1 week), then 1–2 cycles | Costs and structure matter far less; goals such as reducing drawdowns are measurable; builds on the infrastructure. | Needs new owner decisions on scope and universe rules. Pre-2010 data has the known universe limits (D033/D035). Still statistically hard for small effects, and still no guarantee. |
| **5. Change the cost basis first** | If you actually move to a lower-cost broker (for example no per-order commission), re-plan with the real costs before any new hypothesis. | Depends on the broker; research $24 a month | About 1 week to re-plan | Removes the largest measured handicap. | **Earlier candidates cannot simply be re-run at lower cost and picked:** their results are known, so that would be data snooping. Only new, pre-registered tests would be valid. |
| **6. Forward (paper) evaluation** | Freeze one well-motivated rule set (none currently qualifies) and track it forward, in real time, without trading. | $0 to minimal | Low, but slow: years | Truly out-of-sample; no multiple-testing growth. | Very slow; needs a rule worth tracking, and none has earned that under our standards. |

## 7. Is continuing strategy research justified under the current constraints?

**No.**

- Under the current combination of constraints, the evidence says further cycles are unlikely to find a candidate that passes our standards:
  - swing-trading horizon;
  - $100K account;
  - fixed $7 per order;
  - large-cap universe;
  - technical signals only;
  - long-only, with the approved portfolio rules.
- Each extra attempt raises the statistical bar. Lowering the standards is not an option we should consider.

## 8. Should the original objectives be reconsidered?

**Yes, if the project is to continue at all.** The objective "one simple long-only swing-trading strategy that beats the market after costs" meets two structural obstacles:

- **Costs at the swing horizon:** each round trip costs about 0.4%.
- **Portfolio structure:** a few concentrated slots with idle cash.

These obstacles would stay the same whichever new signals we try.

The most defensible reframings are:

- **Option 4:** a lower-turnover, diversified, possibly risk-management-oriented objective;
- **Option 5:** re-planning with a genuinely lower cost basis.

Each would be a **new, pre-registered research phase**, with the same integrity rules.

**My recommendation: Option 1 or Option 2 now** (close, or pause with the backtest node cancelled). Consider Option 4 only if you actively want to pursue a changed objective. I do not recommend Option 3.

## 9. Decisions requested

1. The future of the project: Option 1, 2, 4, 5 or 6 (Option 3 is not recommended).
2. Whether to cancel the QuantConnect backtest node ($14 a month) and/or the seat ($10 a month). **No change is made without your approval.**
3. If you choose Option 4 or 5: permission to draft a new, pre-registered research plan for your review. No experiments would be run before your approval.
