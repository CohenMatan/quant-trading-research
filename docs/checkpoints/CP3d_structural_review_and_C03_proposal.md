# Structural review of C01–C02, portfolio diagnostics, and revised C03 proposal

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **STOP. Awaiting owner review.** No C03 strategy backtest has run. No Validation, Walk-Forward or Holdout data was used. |
| Evidence | IS 2010-01-04 → 2017-12-29 only: the 37 C01/C02 selection candidates (`research/cycles/C03_review.py` → `C03_review_evidence.json`) and 24 new pre-registered no-skill diagnostics (`C03_portfolio_diagnostics_plan.md`, `C03_diagnostics_eval.py` → `C03_diagnostics_results.json`) |
| New runs | E962-01..24: kind infrastructure, **not trials**; all completed without integrity failures. 24 QuantConnect backtests of the pre-registered cap of 28. |

## 1. Summary for the owner

1. **The C01/C02 strategies failed mainly because they had no real edge, not because of our method.** The screen asks for a net information ratio (IR) of about 0.5 over the equal-weight benchmark. IR is the return a strategy earns beyond what its benchmark exposure explains, divided by the risk of that extra return. The median variation delivered −0.14 net and +0.12 before costs.
2. **Our portfolio structure does handicap any strategy.** A portfolio of 10 randomly chosen stocks under our exact rules (no skill at all) earned Sharpe 0.75, against the benchmark's 0.92.
   - A C02-style strategy therefore needs about **+0.27 Sharpe of genuine skill** to reach the screen's 1.02, not +0.10.
   - The handicap comes from trading costs, about 17% idle cash, and the extra risk of holding few stocks.
3. **Holding period is the biggest structural lever.** For the same random portfolio:

   | Holding period | Costs, % of equity a year | Sharpe |
   |---|---|---|
   | 5 sessions | 8.0% | −0.13 |
   | 20 sessions | 3.6% | 0.65 |
   | 60 sessions | 1.2% | 0.81 |

   Short-horizon trading is structurally uneconomic at our costs.
4. **Account size helps through commissions only.** At 15 stocks, going from $100K to $1M cut costs from 3.6% to 2.1% a year and raised the no-skill Sharpe by +0.11.
5. **More stocks did not help at $100K.** 19 slots is not feasible: the $5,000 minimum and the approved cash rules leave only about 7 stocks held, 33% invested. 10 slots scored better than 15 (0.75 vs 0.65) because smaller positions pay proportionally more commission.
6. **Random picks alone move Sharpe by ±0.1.** Changing only the random seed moves the Sharpe of a 10–15-stock portfolio by about ±0.1. One run of a concentrated strategy therefore carries substantial luck, which is one more reason to keep the strict gates.
7. **Recommendation: keep every gate. Adopt signal-agnostic design constraints for C03, decided now before any C03 result:**
   - hold at least about 40–60 sessions or otherwise trade little;
   - 10–15 slots at $100K;
   - report a matched no-skill reference next to every result.
8. **Revised C03:**
   - two hypotheses, **B (volatility-managed exposure)** and **C (lottery-stock avoidance)**, each with 3 pre-declared variations; DSR N goes from 37 to 43;
   - **A (turn-of-the-month) is not recommended.** It is a 4-session trade, the structure the diagnostics show costs destroy. It is kept as an owner option.

## 2. What C01 and C02 taught us

Full evidence: `research/cycles/C03_review_and_plan.md` §1–2 and `C03_review_evidence.json`.

| Finding (37 variations, IS) | Evidence | Type |
|---|---|---|
| No benchmark-beating edge | Median Sharpe 0.50 net and 0.81 gross vs EW 0.92; median IR −0.14 net, +0.12 gross; about 0.5 needed | **Strategy weakness** |
| Short horizons killed by costs | H001/H004: 175–441 round trips a year, costs 4–14% a year | **Strategy weakness** at realistic costs |
| Ideas re-expressed market beta | Mean correlation with EW 0.73, beta 0.69; one factor explains 61% of all variations' returns | **Strategy weakness** (idea design) |
| The only high-IR profiles were defensive, low-exposure and fragile | H005 (later failed Validation) and H007 v1.1 (failed robustness); both tilted to takeover targets | **Strategy weakness** |
| Costs matter at every horizon | Median 2.6% a year, about 0.25 of IR | Mixed: structure (§3) plus design |
| The screen is demanding | Needs net IR ≈ 0.5; no-skill structure starts about 0.17–0.27 Sharpe below the bar (§3) | **Aligned** with the objective, but the handicap must be understood |

## 3. Controlled portfolio diagnostics (pre-registered, D079)

**Design.**

- No-skill portfolio (X962): every close it sells holdings held H sessions and refills the empty slots with *randomly* chosen eligible stocks. The seed fixes the order, and no price data is used.
- Everything else is exactly as in C02: next-open execution, $7 per order, 10 bps slippage, no borrowing, 2% buffer, 15% gap reserve, $5,000 minimum position.
- 8 settings × 3 seeds, one factor changed at a time.
- With the same seed, the $100K and $250K 15-slot runs made identical picks, so their difference is purely account size.

**Results** (mean of 3 seeds; the Sharpe range across seeds in brackets):

| Setting | CAGR | Sharpe | Max DD | Costs / yr (commission + slippage) | Invested | Avg positions | Corr. with EW | Idiosyncratic vol | Sharpe − EW |
|---|---|---|---|---|---|---|---|---|---|
| **10 slots, $100K, hold 20** (C02 setting) | 10.9% | **0.75** (0.61–0.82) | −19.8% | 3.0% (1.0 + 2.0) | 82% | 9.5 | 0.88 | 7.3% | −0.17 |
| 15 slots, $100K, hold 20 | 8.9% | 0.65 (0.57–0.71) | −19.8% | 3.6% (1.7 + 2.0) | 82% | 14.2 | 0.91 | 6.1% | −0.27 |
| 19 slots, $100K, hold 20 | 1.8% | 0.23 (0.07–0.52) | −19.0% | 1.8% | **33%** | **6.7** | 0.55 | 7.8% | −0.69 |
| 15 slots, **$250K**, hold 20 | 10.1% | 0.73 (0.64–0.78) | −19.4% | 2.6% (0.6 + 2.0) | 83% | 14.2 | 0.91 | 6.0% | −0.19 |
| 15 slots, **$1M**, hold 20 | 10.6% | 0.76 (0.68–0.81) | −19.3% | 2.1% (0.15 + 2.0) | 83% | 14.2 | 0.91 | 6.0% | −0.16 |
| **30 slots, $250K**, hold 20 | 8.2% | 0.63 (0.58–0.72) | −21.0% | 3.3% (1.3 + 2.0) | 83% | 28.4 | 0.95 | 4.6% | −0.29 |
| 15 slots, $100K, **hold 5** | −1.8% | **−0.13** (−0.25 to −0.07) | −28.6% | **8.0%** (4.4 + 3.6) | 42% | 7.0 | 0.63 | 6.9% | −1.05 |
| 15 slots, $100K, **hold 60** | 11.9% | **0.81** (0.72–0.90) | −24.5% | **1.2%** (0.5 + 0.7) | 84% | 14.6 | 0.93 | 5.8% | −0.11 |
| *EW ≥ $2B benchmark (E901-07)* | *13.9%* | *0.92* | *−22.3%* | — | *100%* | *about 1,000* | *1* | — | — |
| *SPY (E900-07)* | *13.3%* | *0.95* | — | — | — | — | — | — | — |

**Pre-registered readings:**

- **R1 Diversification, 19 vs 10 slots at $100K.** Δ Sharpe = −0.51: *not* a diversification result. The 19-slot structure is infeasible at $100K.
  - At about $5,160 per position, the no-borrowing planner shrinks buys below the $5,000 minimum. 27,452 buys were skipped in seed 1.
  - The portfolio held about 7 stocks and was 33% invested.
  - **The practical ceiling at $100K is about 15 positions.**
- **R2 Account size, 15 slots.**
  - Commission falls from 1.66% a year at $100K to 0.63% at $250K and 0.15% at $1M.
  - Total cost falls from 3.6% to 2.6% to 2.1%.
  - Sharpe rises by +0.07 at $250K and +0.11 at $1M.
  - Slippage (2.0% a year) is proportional and does not change.
- **R3 Structural handicap, C02 setting.** No-skill Sharpe is 0.75 against EW's 0.92, a **handicap of 0.17**. The screen bar (EW + 0.10 = 1.02) is **0.27 above no-skill**.
- **R4 Holding period.** Costs are 8.0%, 3.6% and 1.2% a year for holds of 5, 20 and 60 sessions; Sharpe is −0.13, 0.65 and 0.81.
  - At hold 5 the portfolio was also only 42% invested. Each sale's cash is reusable only the next day (D051), and 2,444 buys were skipped at the minimum.
- **R5 Breadth with a larger account, 30 vs 15 slots at $250K.** Idiosyncratic volatility falls from 6.0% to 4.6%, but Sharpe falls by 0.10.
  - Positions of $8.2K pay double the commission share (1.3% vs 0.6% a year).
  - The difference lies within the seed range.
  - Diversification beyond about 15 names buys little at our cost structure.

**Other findings:**

- **Idle cash:** about 17% even at normal turnover, from the 2% buffer, the 15% gap reserve and the one-day lag between a sale and its reinvestment. That is 58% at hold 5. It lowers CAGR but barely changes Sharpe.
- **Luck:** within any setting, the seed alone moves Sharpe by 0.13–0.46. A concentrated 10–15-stock book has large selection luck.

## 4. Conclusions on the research method

| Question | Conclusion | Genuine weakness or limitation? |
|---|---|---|
| Concentration / 10–15 stocks | A no-skill 10–15-stock book loses 0.1–0.3 Sharpe to the benchmark, mostly through costs and idle cash; more names helps little at our costs | **Structural limitation**; not a cause of C01/C02 failure (their net IR was −0.14) |
| $5,000 minimum position | Caps a $100K book at about 15 positions; 19 is infeasible | **Constraint of the real account** (D041, D044) |
| Trading costs and holding period | The dominant structural factor: 5-session holding is uneconomic, 60-session costs 1.2% a year | **Structural**; C03 should be designed around it |
| Exposure and idle cash | About 17% idle at normal turnover; Sharpe-neutral, lowers CAGR | **Small structural cost**; no change proposed (gap reserve M3 optional, later) |
| Strategy correlation | C01/C02 variations correlated 0.58 across hypotheses; no-skill books correlate 0.9 with EW | **Strategy weakness**: tilts, not independent return sources |
| Benchmark comparison for concentrated portfolios | "EW + 0.10" sits 0.27 above what our structure achieves without skill; demanding but not wrong | **Aligned**, with a known handicap; keep, and report the matched null |
| Screen vs swing-trading objective | The screen rewards net, risk-adjusted, robust outperformance of simply holding the universe; that is the right bar for a strategy worth trading | **Aligned; no relaxation** |

**Recommendations. None changes a gate. Each needs approval before any C03 result.**

1. **Keep all gates and statistics unchanged:** D036 screen, D069 DSR count, D073 cycle-level PBO, costs, universe.
2. **Design constraints for C03** (signal-agnostic, fixed before any C03 result):
   - holding period at least about 40 sessions, or turnover at most about 12× a year;
   - 10–15 slots at $100K;
   - expected cost at most about 1.5% a year.
   - *Multiple testing:* these come from no-skill diagnostics and select no signal, so they add no trial to N. They are recorded as a decision and disclosed in every C03 report.
3. **Matched no-skill reference** next to every C03 result: same slots, holding and costs. It is reported as "Sharpe over the matched null", **not a gate**. For C it is the core falsification test (§5).
4. **Account size (owner decision, informational):** $1M would add about +0.1 Sharpe to any strategy through commissions. It does not change the research standard, because the product must work at the owner's real $100K. **No change proposed.**

## 5. Revised C03 proposal

### 5.1 Market indicator definitions (owner item 4)

- **SPY is an indicator only, never traded.** The indicator values are computed from SPY's split- and dividend-adjusted daily closes, already kept by the harness, using data up to and including the decision close T. Orders execute at the T+1 open or later.
- **Realised volatility RV(n)** = sample standard deviation of SPY's last n daily simple returns ending at T, × √252.
- **Calendar:** the exchange calendar (`qr_is_last_session_of_month`), plus a session counter within the month.
- **Traded instruments:** only the approved ≥ $2B US-common universe.

### 5.2 Family B: volatility-managed exposure (recommended) — H012 / S012

- **Hypothesis.** Stock-market volatility is persistent, so high recent volatility predicts high near-term volatility. Expected returns do not rise proportionally, so the reward per unit of risk is lower when volatility is high. Investors bear more risk exactly when it is least rewarded; some are leverage-constrained or slow to rebalance.
- **Literature (pre-2018):**
  - Fleming, Kirby & Ostdiek (2001), *J. Finance*;
  - Barroso & Santa-Clara (2015), *J. Financial Economics* (momentum);
  - Moreira & Muir (2017), *J. Finance*;
  - on volatility persistence: Engle (1982), Bollerslev (1986).
- **How it differs from C01/C02:**
  - It changes *how much* is held, not *which* stocks.
  - No C01/C02 strategy timed total exposure; the one "cash-heavy" profile (H005) was a stock-selection side effect.
- **Trading logic:**
  - **Basket:** the 15 largest eligible stocks by point-in-time market cap, reconstituted quarterly.
    - *Justification:* the literature scales the *market* portfolio. Within our stock-only universe and the 15-position limit, the largest names track the cap-weighted market most closely, at the lowest cost and turnover.
    - The traded basket's correlation with SPY is reported. This is a design choice for the traded basket only; the indicator is SPY itself.
  - **Exposure:** at the last session of each month, exposure = min(1, RV(252) / RV(21)), with no leverage (the long-run average volatility of the last 252 days is the target).
    - Positions are scaled to exposure × equal weight at the next open.
    - The change is applied only if exposure moves by more than 0.10, to limit trading.
- **Variations (3):**
  - v1.0: as above;
  - v1.1: RV(63) instead of RV(21) (slower signal);
  - v1.2: weekly instead of monthly rescaling.
- **Holding period:** the basket is held indefinitely, rescaled monthly (weekly for v1.2), and reconstituted quarterly.
- **Costs:** basket turnover plus monthly partial rescales, about 0.3–0.8% a year.
- **Timing vs holding cash (owner requirement):**
  - We measure Sharpe with a zero cash rate, so a *constant* cash share cannot change Sharpe. Any Sharpe gain over the same basket held unscaled can only come from timing.
  - A pre-declared **control run** (the same basket, always 100% target) is a benchmark, not a trial.
  - Drawdown and CAGR are compared with the control **scaled to B's average exposure** (constant, computed after the run), so less drawdown from simply holding more cash is not credited.
- **Falsification:**
  - Reject H012 if every variation fails the unchanged IS screen.
  - Also reject if Sharpe(B) − Sharpe(control) ≤ 0.05 for all variations, meaning no timing value.
  - Also reject if its drawdown is not smaller than the exposure-matched control's.
- **Limitations:**
  - IS 2010–2017 has few volatility spikes (2010, 2011, 2015–16), so the test has limited power.
  - The benefit is concentrated in crashes that IS barely contains.
  - We may learn little either way. This is stated in advance.

### 5.3 Family C: lottery-stock avoidance (recommended) — H013 / S013

- **Hypothesis (independent of H005).** Investors with a preference for lottery-like payoffs overpay for stocks that recently had extreme positive one-day returns. Those stocks subsequently underperform. A long-only investor captures the effect by **avoiding** them.
- **Literature (pre-2018):**
  - Barberis & Huang (2008), *AER*, stocks as lotteries;
  - Kumar (2009), *J. Finance*;
  - Boyer, Mitton & Vorkink (2010), *RFS*;
  - Bali, Cakici & Whitelaw (2011), *J. Financial Economics*, the MAX effect. It persists after controlling for idiosyncratic volatility, so it is not a low-volatility effect.
- **How it differs:**
  - It never *selects* low-volatility or quiet stocks (unlike H005 or H007 v1.1).
  - It only *excludes* the upper tail of recent one-day jumps and picks among the rest without any other signal.
  - It is not motivated by, and contains no filter for, the H005 Validation outcome.
- **Trading logic:**
  - Identical to the no-skill null X962 at the structure the diagnostics favour (15 slots, $100K, hold 60), except that at each buy decision the candidate set excludes the top fraction of eligible stocks by **MAX**.
  - MAX = the stock's largest daily simple return over the last 21 sessions ending T, from adjusted closes.
  - Seeds 1, 2 and 3, **paired** with the already-run null E962-22..24 (same seeds, same structure). The paired difference isolates the avoidance effect, and seed luck largely cancels.
- **Variations (3):**
  - v1.0: exclude the top 20% by MAX;
  - v1.1: exclude the top 10%;
  - v1.2: exclude the top 20% by MAX5 (the average of the 5 largest daily returns in 21 sessions, Bali et al.'s robustness measure).
- **Holding period:** 60 sessions. **Costs:** about 1.2% a year (measured, R4).
- **Evaluation (pre-declared):**
  - A variation passes the IS screen only if **all three seeds pass**; no best-seed picking.
  - DSR and PBO use the equal-weighted average of its three seed return series.
  - Seeds are replicates of one candidate, not extra trials: they count once in N and are counted in the conservative count.
- **Falsification:**
  - Reject H013 if no variation passes.
  - Also reject if mean Sharpe(C) − mean Sharpe(paired null) ≤ 0.05 for all variations.
  - Also reject if its average profit per trade is not above the null's.
- **Limitations:**
  - The selection within the allowed set is random. A passing result supports *avoidance*, and deployment would use a fixed seed, which is honest but unusual.
  - The MAX effect is documented most strongly in small stocks; our ≥ $2B universe may dilute it.
  - Excluding high-MAX stocks leaves a basket with somewhat lower volatility. We report its volatility and correlation to the H005 variations as a distinctness check.

### 5.4 Family A: turn-of-the-month timing (not recommended; owner option) — H014

- **Hypothesis:** month-end cash flows (payrolls, pension contributions) are invested around the turn of the month, and stock returns concentrate in the window from the last trading day to the third trading day.
- **Literature (pre-2018):** Ariel (1987, *JFE*); Lakonishok & Smidt (1988, *RFS*); Ogden (1990, *J. Finance*); McConnell & Xu (2008, *FAJ*).
- **Logic:**
  - Buy the 15-largest basket at the open of the last trading day of the month (the signal is the calendar, known at the prior close).
  - Sell at the open of the 4th trading day.
  - About 4 sessions held, 12 times a year.
- **Why not recommended:** it is exactly the short-hold structure the diagnostics show costs destroy (R4: hold 5, costs 8% a year, no-skill Sharpe −0.13).
  - Each cycle costs about 0.4% of equity: 12 round trips at $6.5K positions, about 0.22% commission and 0.2% slippage per cycle, so about 5% a year.
  - The published premium, of the order of 0.5% a month before costs, would be almost fully consumed.
- **Falsification (if run):** net profit per cycle ≤ 0, or a failed screen.
- If the owner wants it, it adds 3 trials (N 46).

### 5.5 Alternative directions considered

- **Longer-horizon selection tilts in general** (hold about 60 sessions). The diagnostics show this is where costs stop dominating. Both B and C are built this way, so no separate family is added.
- **Industry momentum:** needs point-in-time industry classifications, which Morningstar does not provide reliably (D061). Not proposed.
- **Continuing C01/C02 families, e.g. H009 with longer holds:** would be a rescue. Not proposed.

### 5.6 Statistics, budget, stopping

- **Trial count (D069):** B 3 + C 3 = 6 new selection candidates, so **N = 43** (46 with A). At the current dispersion the DSR bar is about 1.11 (1.13 with A).
  - Diagnostics, controls and seed replicates are not selection candidates.
  - The conservative count includes robustness runs and C's seed runs.
- **PBO (D073, frozen):** cycle-level CSCV over the C03 selection set: 6 columns (C as seed-averaged series). With 6 columns the statistic is coarser than C02's 18; this is disclosed. Per-hypothesis PBO is a diagnostic.
- **Screen and robustness:** the unchanged D036 screen, including 2× slippage. Robustness for at most 2 hypotheses, perturbations pre-declared in each hypothesis file:
  - B: RV windows 15/30 and 42/84, rescale band 0.05/0.20, plus 4×/6× costs;
  - C: exclusion 15%/25%, hold 45/75, plus 4×/6× costs; each on 3 seeds.
- **Budget (QuantConnect backtests):**

  | Block | Runs |
  |---|---|
  | B selection + 1 control | 4 |
  | C selection (3 variations × 3 seeds; nulls reused) | 9 |
  | 2× slippage for screen passes | ≤ 12 |
  | Robustness (B ≤ 10; C ≤ 18) | ≤ 28 |
  | **Cap** | **≤ 53** (+ technical retries/recoveries, reported separately) |

  - **Runtime:** about 6–8 minutes per run (measured on X962), so **about 6–8 hours of node time** at the cap.
  - Wall-clock time is longer with QuantConnect delays and restarts; the resumable queue and D077 limit the loss.
  - **Cost:** within the $24/month subscription; no purchase.
- **Infrastructure needed (verification, not trials; tests plus a canary):**
  - SPY realised-volatility indicator;
  - quarterly largest-15 basket;
  - exposure scaling with a band;
  - MAX/MAX5 exclusion reusing X962;
  - a session-of-month counter (only if A is approved).
- **Stopping rule (approved by the owner):** if C03 produces no qualifying candidate, no further strategy cycle is launched automatically. Instead, a final review of the whole research programme (findings, limitations, costs, alternative directions) is written for a separate owner decision.

## 6. Timeline

1. On approval: build and test the infrastructure, run a canary (about ½ day), then an owner-free check that the canary passes.
2. The 13 selection-and-control runs (about 2 hours of node time), then the screen and robustness (≤ about 5 hours).
3. C03 results checkpoint, then stop. No Validation without approval.

## 7. Decisions needed

1. **Accept the structural conclusions and the C03 design constraints** (§4, recommendation 2): holding period at least about 40 sessions or turnover at most about 12× a year, 10–15 slots at $100K, expected cost at most about 1.5% a year. Gates unchanged.
2. **Approve the matched no-skill reference** as a reported diagnostic (not a gate), and as the core falsification test for C.
3. **Approve the C03 hypotheses:** B (H012) and C (H013), with their variations, evaluation rules and budget cap of 53. Or add A (H014) despite the cost evidence.
4. **Approve the traded basket for B/A:** the 15 largest eligible stocks by point-in-time market cap, reconstituted quarterly, with SPY as the indicator only (§5.2).
5. **Account size:** keep $100K as the only research account (recommended), or ask for a larger-account track.
