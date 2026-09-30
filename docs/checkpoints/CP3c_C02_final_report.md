# Research Cycle 2 (C02): final report

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **C02 complete. Outcome: No Production Candidate Found** (proposed D076, confirmed here with all tests done). STOP: awaiting owner review. |
| Supersedes | `CP3b_C02_IS_results.md` (interim, written before the last three robustness runs) |
| Period | In-sample (IS) only: 2010-01-04 → 2017-12-29. **No Validation, Walk-Forward or Holdout run was made.** |
| Next | C01–C02 review and C03 proposal: `research/cycles/C03_review_and_plan.md` (planning only) |

## 1. Executive summary

- **Six new hypotheses (H006–H011) in six families, 18 pre-declared variations, each run once.** Everything was fixed before any result:
  - the hypotheses, variations, costs and gates;
  - the trial count for the Deflated Sharpe Ratio (D069);
  - the cycle-level PBO gate (D073).
- **17 of 18 variations fail the IS screen.** Every one fails "Sharpe ≥ the equal-weight benchmark's Sharpe + 0.10" (the benchmark scored 0.92).
- **One variation passes the screen:** H007 v1.1 (E007-02), a volatility-contraction breakout. It has Sharpe 1.12 and max drawdown −5%, but is on average only 21% invested (CAGR 5.4%).
- **It fails the pre-declared robustness gate.**
  - The time-stop dimension is robust: 4 of 4 settings keep Sharpe 1.09–1.17.
  - The contraction-threshold dimension is not: 3 of 4 settings fall below the required 0.782.
  - Overall 5 of 8 pass; 7 were required.
- **Statistics:**
  - Cycle-level PBO 0.268, within the ≤ 0.30 gate.
  - The best IS Deflated Sharpe (N = 37) is 0.54, far below the 0.90 later required at Validation.
- **Outcome: No Production Candidate Found.** No rule was changed and no strategy was rescued.

## 2. The six hypotheses and why each failed

The IR figures below are information ratios. IR measures the return a strategy earns beyond what its exposure to the equal-weight benchmark explains, divided by the risk of that extra return. Passing "Sharpe ≥ EW + 0.10" needs a net IR of about 0.5 (C03 review §2.7).

| Hypothesis | Best variation (IS Sharpe) | Pre-declared falsification | Why it failed |
|---|---|---|---|
| **H006** breakout to a new N-day high on volume | v1.2, no volume: 0.90 | Not formally rejected (profit factor 1.39–1.53; expectancy CI > 0) | Real but small edge: net IR 0.07–0.33, below the ~0.5 needed. Both specific claims contradicted: volume confirmation added nothing (v1.2 ≥ v1.0), and the 52-week anchor was worse (v1.1 0.74 < v1.0 0.88). v1.1 and v1.2 also had deeper drawdowns than the benchmark. |
| **H007** volatility contraction then expansion | v1.1 ATR ratio: 1.12 (screen pass) | v1.1 passed the screen, then failed robustness | v1.0 and v1.2 (bandwidth squeeze) had profit factors of about 1.1 and no edge. v1.1's result depends on a narrow threshold: from ATR ratio 0.3 to 0.9, trades go from 30 to 897, exposure from 2% to 77%, and Sharpe from −0.10 to 0.86 (base 1.12). Its good figures come mostly from being in cash about 80% of the time and holding a few quiet stocks, 13.5% of which were takeover targets. |
| **H008** residual (market-adjusted) relative strength | v1.1 6-1: 0.69 | **Rejected** (all fail the screen) | After the score fix (D074), rankings were meaningful, but the book behaved like a high-beta market portfolio (beta 0.89–1.27, drawdown −26% to −34%) with negative net alpha. |
| **H009** high-volume return premium | v1.1 hold 40: 1.01; v1.2 weekly: 1.00 | **Rejected** (all fail the screen) | The nearest miss: v1.1 and v1.2 fail **only** the benchmark + 0.10 item, by 0.01–0.02 of Sharpe (net IR 0.42–0.45). v1.0 (hold 20) pays about double the costs and loses its edge. Per protocol, a near miss is not revisited. |
| **H010** gap-and-hold continuation | v1.1 hold 60: 0.68 | **Rejected** | The drift after accepted gaps was too weak after costs (profit factor 1.18–1.25; net IR ≤ 0). The "acceptance" condition helped a little (v1.0 0.59 > v1.2 0.51), not enough. |
| **H011** same-calendar-month seasonality | v1.1 10 years: 0.67 | **Rejected** | No reliable seasonal effect in our large-cap universe. v1.0 and v1.2 (5-year lags) were close to zero. All three suffered drawdowns of about −43% (2015–16). The 10-year look-back used pre-2010 prices only as warm-up. |

## 3. All 18 selection trials

The equal-weight ≥ $2B benchmark (E901-07) had Sharpe 0.92, CAGR 13.9% and max drawdown −22.3% over the same dates. SPY (E900-07) had Sharpe 0.95 and CAGR 13.3%.

"Gross Sharpe" adds back commissions and slippage. "Costs" are commissions plus estimated slippage, as % of average equity per year. "EW at same exposure" is the benchmark scaled to the strategy's daily invested fraction.

| Run | Variation | Sharpe | Gross Sharpe | CAGR | Max DD | Trades | Profit factor | Invested | Costs | EW at same exposure (Sharpe) | Beta to EW | Net IR | DSR (N = 37) | Screen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E006-01 | H006 v1.0 | 0.88 | 1.01 | 12.2% | −19.3% | 529 | 1.46 | 91% | 1.8% | 0.85 | 0.69 | 0.28 | 0.28 | fail |
| E006-02 | H006 v1.1 | 0.74 | 0.87 | 9.8% | −24.3% | 519 | 1.39 | 91% | 1.8% | 0.86 | 0.68 | 0.07 | 0.17 | fail |
| E006-03 | H006 v1.2 | 0.90 | 1.04 | 12.3% | −22.7% | 517 | 1.53 | 91% | 1.8% | 0.88 | 0.67 | 0.33 | 0.31 | fail |
| E007-01 | H007 v1.0 | 0.56 | 0.85 | 6.0% | −16.8% | 911 | 1.14 | 77% | 3.4% | 0.82 | 0.50 | −0.07 | 0.07 | fail |
| **E007-02** | **H007 v1.1** | **1.12** | **1.29** | **5.4%** | **−5.1%** | **223** | **2.46** | **21%** | **0.9%** | **0.64** | **0.10** | **0.88** | **0.54** | **PASS** |
| E007-03 | H007 v1.2 | 0.50 | 0.79 | 5.4% | −19.0% | 941 | 1.10 | 78% | 3.5% | 0.86 | 0.51 | −0.14 | 0.05 | fail |
| E008-01 | H008 v1.0 | 0.57 | 0.65 | 9.2% | −26.2% | 429 | 1.36 | 89% | 1.5% | 0.88 | 1.00 | −0.37 | 0.07 | fail |
| E008-02 | H008 v1.1 | 0.69 | 0.81 | 10.6% | −26.0% | 566 | 1.33 | 86% | 1.9% | 0.86 | 0.89 | −0.14 | 0.14 | fail |
| E008-03 | H008 v1.2 | 0.67 | 0.70 | 14.9% | −33.6% | 287 | 1.47 | 91% | 0.9% | 0.91 | 1.27 | −0.06 | 0.12 | fail |
| E009-04† | H009 v1.0 | 0.67 | 0.89 | 9.1% | −20.4% | 907 | 1.23 | 89% | 3.2% | 0.87 | 0.76 | −0.12 | 0.12 | fail |
| E009-02 | H009 v1.1 | 1.01 | 1.12 | 14.4% | −20.7% | 482 | 1.57 | 91% | 1.6% | 0.92 | 0.74 | 0.45 | 0.41 | fail |
| E009-03 | H009 v1.2 | 1.00 | 1.24 | 13.4% | −16.6% | 901 | 1.52 | 89% | 3.2% | 0.88 | 0.73 | 0.42 | 0.41 | fail |
| E010-01 | H010 v1.0 | 0.59 | 0.79 | 6.9% | −19.1% | 711 | 1.18 | 83% | 2.6% | 0.88 | 0.64 | −0.19 | 0.08 | fail |
| E010-02 | H010 v1.1 | 0.68 | 0.83 | 8.6% | −21.7% | 534 | 1.25 | 85% | 1.9% | 0.98 | 0.66 | −0.03 | 0.13 | fail |
| E010-03 | H010 v1.2 | 0.51 | 0.77 | 6.1% | −21.5% | 871 | 1.19 | 86% | 3.3% | 0.85 | 0.69 | −0.36 | 0.06 | fail |
| E011-01 | H011 v1.0 | 0.17 | 0.32 | 1.3% | −43.3% | 885 | 1.03 | 80% | 3.2% | 0.94 | 1.08 | −0.98 | 0.01 | fail |
| E011-02 | H011 v1.1 | 0.67 | 0.83 | 11.2% | −43.0% | 887 | 1.25 | 80% | 2.8% | 0.94 | 0.96 | −0.12 | 0.12 | fail |
| E011-03 | H011 v1.2 | 0.25 | 0.41 | 2.9% | −41.7% | 882 | 1.06 | 80% | 3.2% | 0.95 | 1.01 | −0.83 | 0.01 | fail |

†E009-04 is the identical re-run of E009-01, whose runner was lost in a container restart (§7).

Gate-by-gate results: `research/cycles/C02_is_gates.json`. Tables: `C02_is_results.csv`. Review evidence: `C03_review_evidence.json`.

## 4. Robustness of H007 v1.1 (pre-declared, `research/cycles/C02_robustness_plan.md`)

| Test | Run | Sharpe | CAGR | Max DD | Trades | Invested | Criterion | Result |
|---|---|---|---|---|---|---|---|---|
| Base | E007-02 | 1.12 | 5.4% | −5.1% | 223 | 21% | — | — |
| 2× slippage (screen item) | E007-04 | 1.01 | 4.9% | −5.3% | 223 | 21% | ≥ 0.40 | pass |
| 4× slippage | E007-15 (repeat of E007-05) | 0.80 | 3.8% | −6.5% | 223 | 21% | > 0 | pass |
| 6× slippage | E007-06 | 0.59 | 2.8% | −8.3% | 223 | 21% | reported | — |
| ATR ratio 0.6 → 0.3 | E007-07 | −0.10 | 0.0% | −0.3% | 30 | 2% | ≥ 0.782 | **fail** |
| ATR ratio 0.48 | E007-08 | 0.41 | 0.4% | −1.0% | 51 | 4% | ≥ 0.782 | **fail** |
| ATR ratio 0.72 | E007-09 | 0.69 | 5.4% | −19.2% | 565 | 49% | ≥ 0.782 | **fail** |
| ATR ratio 0.9 | E007-10 | 0.86 | 10.1% | −20.7% | 897 | 77% | ≥ 0.782 | pass |
| Time stop 40 → 20 | E007-11 | 1.09 | 4.6% | −5.2% | 236 | 18% | ≥ 0.782 | pass |
| Time stop 32 | E007-12 (recovered, D077) | 1.17 | 5.5% | −5.0% | 224 | 20% | ≥ 0.782 | pass |
| Time stop 48 | E007-13 | 1.12 | 5.5% | −5.1% | 223 | 21% | ≥ 0.782 | pass |
| Time stop 60 | E007-14 | 1.13 | 5.5% | −5.1% | 223 | 22% | ≥ 0.782 | pass |
| Thirds of IS | E007-02 | 1.19 / 1.06 / 1.17 | | | | | each > 0 | pass |

**Plateau: 5 of 8 perturbations pass; at least 7 were required. The robustness gate fails.**

- The time stop hardly matters: most trades end on the middle-band exit (average hold about 28 calendar days), so a stop between 20 and 60 sessions rarely binds.
- The contraction threshold decides everything. The base setting sits on a peak between "almost never trades" and "an ordinary, mostly invested book with Sharpe below the benchmark". That is the pattern of a fitted, not a structural, result.
- Cost stress alone would have passed: 0.80 at 4×, because it trades rarely.

## 5. Statistics and trial accounting (all definitions frozen before C02 results)

- **Deflated Sharpe (D069):** N = 37 cumulative selection candidates (19 C01 + 18 C02).
  - With the observed Sharpe dispersion, the best of 37 skill-less strategies is expected to show an annual Sharpe of about 1.08.
  - The best IS DSR is 0.54 (E007-02). The conservative count, N = 64 (selection + robustness + Validation), gives 0.46.
- **PBO:**
  - Cycle level across all 18 (hard gate, D073): **0.268, passes** (≤ 0.30).
  - Per hypothesis (diagnostic only): H006 0.91, H007 0.12, H008 0.97, H009 0.97, H010 0.71, H011 0.06.
- **Return correlations:**
  - Within hypotheses 0.72–0.92, except H007 v1.1 at 0.34–0.37.
  - Across all 37 C01+C02 variations: mean 0.58 between hypotheses, and one common factor explains 61% of variance.
- **Trial accounting (registry, D069):**

| Category | C01 and earlier | C02 | Total |
|---|---|---|---|
| Selection candidates (DSR N) | 19 | 18 | **37** |
| Robustness runs | 15 | 11 (E007-04 … E007-14) | 26 |
| Validation runs | 1 | 0 | 1 |
| Technical repeats (same configuration) | 46 | 3 (E009-04, E007-15, E007-16) | 49 |
| Not started | 7 | 0 | 7 |
| Verification / canary / benchmark | 37 | 6 (E959-01..03, E960-01, E961-01..02) | 43 |
| Recoveries of a lost runner's completed backtest (D077; not trials) | 0 | 1 (E007-12) | 1 |

- **Registry totals:** 167 runs (annotation rows excluded) over 163 experiment IDs (research 121, infrastructure 29, benchmark 14, demo 3). **Hypotheses 11, research strategies 11.**
- **C02 QuantConnect backtests started:** 18 selection + 1 lost (E009-01) + 11 robustness + 1 repeat (E007-15) = 31, within the 56 cap. E007-16 never ran and was deleted with owner approval, after its metadata was preserved.

## 6. Costs and benchmark comparisons

- **Costs:** commissions ($7 per order) plus slippage (10 bps per side) cost C02 variations 0.9–3.5% of equity a year. That is about 0.1–0.3 of Sharpe (gross versus net).
- **Before costs, only 4 of 18** would beat EW + 0.10: E006-03, E007-02, E009-02, E009-03.
- **Exposure-aware comparison:** against the equal-weight benchmark held at each strategy's own daily exposure, five variations beat it on Sharpe: E006-01 and E006-03 (by 0.03), E009-02 and E009-03 (by 0.09 and 0.12), and E007-02 (by 0.48). The other 13 do not.
- **Market exposure:** beta to equal-weight was 0.64–1.27 for the fully invested variations, so most of the return is market return.

## 7. Operational incidents (no recorded result is affected)

- **Three container restarts** killed the local runner during E009-01, E007-05 and E007-12. All three are recorded as operational failures with their QuantConnect backtest IDs kept.
  - Identical re-runs: E009-04 and E007-15.
  - **E007-12's completed backtest was recovered and verified** instead of re-running (D077, owner instruction). It uses the same download and integrity checks, and the strategy code is proven unchanged since the original commit.
- **E007-16** (the first repeat of E007-12) was stuck "In Queue" at 0% on QuantConnect and never ran. Its metadata and runner output were preserved (`research/cycles/incidents/E007-16_*`), then it was deleted with owner approval. Its registry record is kept.
- **QuantConnect published fill data late** on E007-01 and E007-07 (71–77 minutes). The runner waited; the downloads were complete.
- **E009-02 and E009-03** ended `completed_with_warnings`: holdings without data for 10 sessions were closed at their last real price under D062, a general rule applied to all strategies.

## 8. What we learned from C02

Details and the C01+C02 evidence are in `research/cycles/C03_review_and_plan.md`.

1. **The ideas lacked a benchmark-beating edge; costs made it worse but were not the cause.** Median net IR −0.14, gross +0.12, against about 0.5 needed.
2. **Most variations re-expressed market beta.** A concentrated, fully invested long-only book is dominated by the market. Its entry signal mostly changes *which* 10 large stocks are held, not the risk that drives returns.
3. **The only attractive profiles were defensive and low-exposure, and fragile.** They were tilted towards takeover targets and sensitive to thresholds (H005 in C01, H007 v1.1 here).
4. **Volume-based ideas came closest.** H009's longer-hold variants missed by 0.01–0.02 of Sharpe. That is recorded, and per protocol it is not pursued as a rescue.
5. **Process lessons.**
   - The signal-equivalence canary caught a mathematically empty score (H008) before any run.
   - Freezing the DSR and PBO definitions in advance removed any room for after-the-fact interpretation.
   - Container restarts are the main operational risk; the recovery tool (D077) now limits their cost.

## 9. Decision requested

Confirm the C02 outcome, **No Production Candidate Found**, and review the C03 proposal. No C03 experiment will run without approval.
