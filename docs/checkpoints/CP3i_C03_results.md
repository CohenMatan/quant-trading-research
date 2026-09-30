# C03 results: H013 lottery-stock avoidance

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **STOP. Awaiting the owner.** No Validation, Walk-Forward or Holdout run was made. |
| Result | **No qualifying candidate.** All 9 H013 seed books fail the unchanged IS screen. By H013's own pre-declared test, the avoidance effect is **refuted**. |
| Runs | **All 21 committed research runs completed.** No conditional run was triggered, because no variation passed the base screen on all three seeds. Research budget used: 21 of 82. |
| Operational | 27 QuantConnect executions in C03 (21 research, 1 technical repeat, 4 canaries, 1 reproduction). Two incidents, both resolved (§6). |
| Evidence | `research/cycles/C03_results.json` (from `C03_eval.py`, written before any C03 run), the registry, `C03_budget.py`, `research/cycles/incidents/E013-06_incident.md` |
| Programme totals | 12 hypotheses tested (H001–H011, H013); H012 was withdrawn untested. 12 research strategies; 213 experiment IDs (218 registry runs of all kinds, including failed, superseded and verification runs). |

## 1. What was tested

**H013** skips stocks whose recent single-day jumps are extreme. The skipped set is the top q of eligible stocks, ranked on one of two measures over the last 21 sessions:

- **MAX:** the largest daily return;
- **MAX5:** the mean of the 5 largest daily returns.

Apart from this exclusion, H013 is exactly the no-skill random portfolio X962:

- 15 slots, each held 60 sessions;
- $100K account;
- $7 per order and 10 bps slippage;
- next-open execution, no borrowing.

**Paired design.** H013 walks the null's own random order for the same seed, so each seed is compared with its paired null (E962-22/23/24).

**Variations:**

- v1.0: top 20% by MAX;
- v1.1: top 10% by MAX;
- v1.2: top 20% by MAX5.

The exclusion worked as specified: on average 201 of about 1,007 eligible stocks were excluded at 20%, and 100 at 10%.

**Reference points, IS 2010–2017:**

- equal-weight benchmark (EW) Sharpe: 0.92;
- the screen requires Sharpe ≥ EW + 0.10 = **1.02**.

## 2. Results at $100K (IS 2010-01-04 → 2017-12-29; every seed shown)

| Book | Sharpe | Null Sharpe | Difference vs null | CAGR | Max drawdown | Trades | Profit per trade vs null | Exposure | Failed screen items |
|---|---|---|---|---|---|---|---|---|---|
| v1.0 s1 (E013-01) | 0.734 | 0.720 | +0.013 | 9.8% | −23.2% | 482 | −$28 | 84% | Sharpe vs EW; drawdown |
| v1.0 s2 (E013-02) | 0.827 | 0.820 | +0.007 | 10.9% | −19.5% | 482 | −$33 | 84% | Sharpe vs EW |
| v1.0 s3 (E013-03) | 0.835 | 0.901 | −0.065 | 11.6% | −22.4% | 481 | −$64 | 84% | Sharpe vs EW; drawdown |
| v1.1 s1 (E013-04) | 0.702 | 0.720 | −0.018 | 9.7% | −24.7% | 481 | −$32 | 84% | Sharpe vs EW; drawdown |
| v1.1 s2 (E013-05) | 0.796 | 0.820 | −0.024 | 11.0% | −23.2% | 481 | −$24 | 84% | Sharpe vs EW; drawdown |
| v1.1 s3 (E013-16) | 0.784 | 0.901 | −0.117 | 11.3% | −22.1% | 481 | −$68 | 85% | Sharpe vs EW |
| v1.2 s1 (E013-07) | 0.682 | 0.720 | −0.038 | 9.0% | −25.7% | 481 | −$44 | 84% | Sharpe vs EW; drawdown |
| v1.2 s2 (E013-08) | 0.745 | 0.820 | −0.075 | 9.7% | −20.8% | 481 | −$62 | 84% | Sharpe vs EW |
| v1.2 s3 (E013-09) | 0.944 | 0.901 | +0.043 | 13.2% | −22.3% | 481 | −$7 | 85% | Sharpe vs EW |

**Paired nulls:**

| Null | Sharpe | CAGR | Max drawdown | Exposure |
|---|---|---|---|---|
| s1 (E962-22) | 0.720 | 10.5% | −25.9% | 85% |
| s2 (E962-23) | 0.820 | 11.8% | −25.8% | 84% |
| s3 (E962-24) | 0.901 | 13.4% | −21.7% | 84% |

**Costs** are almost identical across all books:

- about 977 orders ($6.8K commissions over 8 years);
- commission drag 0.5–0.6% a year;
- slippage drag 0.7% a year;
- turnover about 7.1× a year.

**Per variation (mean over its three seeds):**

| Variation | Mean Sharpe | Mean difference vs null | Mean profit per trade vs null | Screen |
|---|---|---|---|---|
| v1.0 | 0.799 | −0.015 | −$42 | fail (0 of 3 seeds pass) |
| v1.1 | 0.760 | −0.053 | −$41 | fail (0 of 3) |
| v1.2 | 0.790 | −0.024 | −$38 | fail (0 of 3) |

## 3. Screening, robustness and conditional runs

**Screen.**

- Every seed fails "Sharpe ≥ EW + 0.10". The best seed reaches 0.944 against the 1.02 required.
- Five of the nine also fail the drawdown item (drawdown worse than EW's).
- All pass the trade-count, profit-factor, positive-years and stress-episode items.

**Conditional runs.** No variation passed the base screen on all three seeds. So, by the pre-declared procedure, **no** 2× slippage run and **no** robustness battery was run, and no variation was chosen.

**Every IS third has a positive Sharpe** for every seed (thirds from 0.39 to 1.83). This is reported for completeness; there is no robustness stage.

## 4. Did H013 show a consistent advantage? No.

- **Against its paired random selection:**
  - the Sharpe difference is positive for 3 of 9 seed books and negative for 6;
  - the mean per variation is between −0.015 and −0.053;
  - the average profit per trade is lower than the null's **in all 9 books**.
- **H013.md's pre-declared falsification:** the effect is refuted if, for every variation, the mean seed Sharpe difference is ≤ 0.05 or profit per trade does not exceed the null's. **Both conditions are met for all three variations.**
- **Overlap with the null.** 70–88% of H013's entries are the same (stock, date) entries the null made. The differences arise only where excluded names were skipped, and on those trades H013 did worse, not better.
- **Seed noise dominates.**
  - The nulls alone range from 0.72 to 0.90 Sharpe across seeds.
  - The seed-to-seed spread (about 0.2) is far larger than any H013 effect.
  - The three seeds share the market and most holdings, so they are not three independent confirmations. Here they are consistent only in showing **no** benefit.

**Conclusion.** Within IS 2010–2017, avoiding recent lottery-like stocks did not improve on random selection of the same portfolio structure. No H013 variation is a candidate.

## 5. $200K capital sensitivity (diagnostic; never used for selection)

| Seed | S1 ($200K, 15 positions) | S1 paired null | S2 ($200K, 20 positions) | S2 paired null |
|---|---|---|---|---|
| 1 | 0.754 | 0.739 | 0.860 | 0.666 |
| 2 | 0.848 | 0.838 | 0.842 | 0.917 |
| 3 | 0.856 | 0.918 | 0.855 | 0.902 |

Values are Sharpe ratios.

- **S1** (the same books at $200K) raises every H013 seed's Sharpe by about +0.02, and each paired null's by +0.02 too.
  - The cause is lower commission drag: 0.26–0.28% a year instead of 0.53–0.56%.
  - H013's standing against its null is unchanged: mean difference −0.012.
- **S2** (20 positions) gives a mean difference vs null of **+0.024**.
  - This is driven entirely by seed 1, whose null happens to be weak (0.666). The other two seeds are negative (−0.076 and −0.047).
  - This illustrates the size of seed noise. It is not evidence of an effect, and it would not change any decision.

## 6. Statistics and trial accounting

**Trial counts** (Amendment 1), from the registry after C03 (SHA-256 `d9143643…`):

- **official N = 40** (37 before C03 + the 3 H013 variations);
- **conservative N = 73** (40 selection + 6 H013 replicate seeds + 26 robustness + 1 Validation);
- **sensitivity N = 43**, reported only.
- **Not counted:** technical repeats (50 cumulative, including E013-16), not-started runs (7), and verification, benchmark, null and sizing runs (83).
- **Sharpe dispersion** V[SR] is now 0.000946 (40 candidates).

**DSR.** The frozen gate (IS + VAL) applies only after Validation, so it does not apply here. **IS-only diagnostic** DSR per seed book, which is far below the 0.90 bar:

- N = 40: 0.14–0.36;
- N = 73: 0.08–0.25;
- N = 43: 0.13–0.35.

**PBO (diagnostic only)** over the 3 seed-averaged variations is 0.93.

- Three near-identical, highly correlated variations make PBO close to meaningless (see CP3f).
- It is consistent with "no variation is reliably better than another".

**Research budget:** 21 of 82 used (21 committed, 0 conditional).

**Operational usage in C03:** 27 QuantConnect executions:

- 21 research runs, one of which (E013-06) failed;
- 1 technical repeat (E013-16);
- 4 infrastructure canaries (E963-01/02/03, E964-01);
- 1 reproduction (E013-03).

**Incidents** (`research/cycles/incidents/E013-06_incident.md`):

1. **E013-06** was stuck "In Queue" on QuantConnect for over an hour and never ran.
   - Its metadata was committed, and it was then deleted with the owner's approval.
   - The identical configuration ran as **E013-16**, a technical repeat. It is not a new selection candidate, and the original failed row is kept.
2. **E013-03** was labelled "Runtime Error" by QuantConnect's own infrastructure (websocat) after it had completed.
   - A reproduction run gave **identical equity, fills and trades**: all three hashes match, and the fills hash covers every order's date, quantity, price and fee.
   - So the label affected no order, fill, fee or result. **E013-03 is retained.**

Runtimes of the completed runs were 3.9–11.4 minutes (typically about 7), within the normal range.

## 7. Limitations

- **One period.** IS 2010–2017 is a single, mostly calm bull market. A lottery-avoidance effect documented elsewhere may exist in other periods or universes. This test only shows it did not appear here, in our ≥ $2B universe, with random selection among the remaining names.
- **Limited design.**
  - There are only 3 variations of one idea, so selection bias can hardly be measured (hence the weak PBO).
  - The seeds are correlated (about 0.86 between seeds), so they carry little more information than one portfolio.
- **Precision.** The paired design removes shared market effects, but H013 and its null share 70–88% of their entries. The measured effect therefore rests on the few hundred differing trades, over 8 years.
- **Nothing was done to rescue a result.** No Validation was run, and no rule, parameter, threshold or seed was changed after results were seen.

## 8. Stopping rule and next step

- **C03 produced no qualifying candidate.** Under the owner-approved stopping rule (CP3e §8, D087): **no further research cycle is started.**
- The next deliverable is a **comprehensive review of the research programme**:
  - findings from C01–C03 (12 hypotheses tested, none qualifying);
  - what the structural diagnostics taught;
  - limitations, costs and time;
  - alternative directions, including whether to continue at all.

  It will be written as a separate document for your decision before any further experiment is proposed.
- **Decision requested:**
  1. Accept these C03 results and close C03 as **No Production Candidate Found**.
  2. Confirm that I should now prepare the programme review.
