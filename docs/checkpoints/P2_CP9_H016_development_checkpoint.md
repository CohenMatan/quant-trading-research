# P2-CP9 — H016 (gross profitability) development checkpoint (STOP)

- **Date:** 2026-10-02.
- **Programme:** Phase 2, hypothesis 2 of 3. **Slot 2 is consumed** by E016-01.
- **Spec:** frozen `research/phase2/H016_spec.md` (SHA-256 pinned, verified unchanged).
- **Evaluation:** `research/phase2/H016_eval.py` (committed before any candidate result), output in `research/phase2/H016_results.json`.
- **Holdout:** locked. Not opened, not requested.

## Verdict

**H016 is NOT development-qualified.**
- The GP/A top-20 portfolio fails **G1, G2 and G3**.
- **G4** fails by rule: its perturbation and 2× slippage items are "not run", because the candidate already failed G1–G3 (spec §9).
- The conditional robustness runs E016-09 … E016-17 were therefore **not run**.

H016 is **profitable** (12.8% a year), but it did **not** beat the equal-weight portfolio of its own universe, did **not** beat SPY, and did **not** beat the median random 20-stock portfolio drawn from the same universe.

**No Holdout request.** This is the honest outcome, and the pre-registered rules are applied as written.

| Class | Result |
|---|---|
| Profitable (CAGR > 0 after costs) | **Yes** |
| Benchmark-beating (G1) | **No** |
| Random-control-beating (G2) | **No** |
| Development-qualified (G1–G4) | **No** |

## What was run (all on 2010-03-01 → 2021-12-31, the common window for every book)

| Run | Book | Status |
|---|---|---|
| E980-01 | Canary (random seed 0, not a control); infrastructure, not a trial | Completed; all 20 checks pass (`research/phase2/H016_canary_check.json`) |
| E016-01 | **Candidate**: top 20 by GP/A, quarterly, $100K | Completed |
| E016-02 | EW-H016: equal weight of the same universe | Completed with warnings (see the note below) |
| E016-03 … 07 | Random controls, seeds 1–5 | Completed |
| E016-08 | Candidate at $200K (sensitivity) | Completed |
| E016-09 … 17 | Conditional robustness | **Not run** (trigger not met) |

**Note on E016-02:** three holdings were closed at their last real close after more than 10 sessions without data. This is the standard D059 fallback, a warning and not a failure.

**Run totals:**
- **This stage:** 1 canary + 8 committed development runs.
- **Phase 2 so far:** 2 hypotheses tested (H014 rejected, H016 now failed); 3 selection candidates (H014 A, H014 B, H016).
- **Programme since C01:** 43 selection candidates in total.

## The 23 checkpoint items

### Candidate performance (items 1–7)

| Item | E016-01 (H016, $100K) |
|---|---|
| 1. CAGR | **12.8%** |
| 2. Sharpe | **0.69** |
| 3. Max drawdown | **−40.5%** |
| 4. Calmar | 0.32 |
| 5. Annualised costs | **0.30% a year** (commissions + slippage) |
| 6. Turnover | 149% of equity a year |
| 7. Exposure / cash | 95.3% invested on average (4.7% cash), lowest cash 1.9%; 19.7 positions on average (98.6% of slots) |

**Position-sizing rule in practice (owner request, reported separately):**

| | E016-01 ($100K) | E016-08 ($200K) |
|---|---|---|
| Initial buys | 217 | 221 |
| Top-up orders | 182 | 200 |
| Top-up commissions | $1,274 | $1,400 |
| Top-up slippage | $265 | $994 |
| **Incremental cost of top-ups** | **0.06% a year** | **0.04% a year** |
| Smallest top-up fill | $283 | $252 |

- Every top-up was at least $250 at the decision price, and every position was topped up at most once (verified on the canary).
- No negative cash and no leverage in any run.
- The cost gate (≤ 1.5% a year) is comfortably met.

### Benchmarks and controls (items 8–12)

| Book | Sharpe | CAGR | Max DD | Calmar |
|---|---|---|---|---|
| **H016 (E016-01)** | **0.69** | **12.8%** | **−40.5%** | **0.32** |
| 8. EW-H016, same universe (E016-02), *primary benchmark* | 0.85 | 14.4% | −36.0% | 0.40 |
| 9. SPY (E900-07) | 0.92 | 14.9% | −33.1% | 0.45 |
| 10. Broad EW ≥ $2B (E901-07), *reference only* | 0.79 | 13.4% | −37.7% | 0.35 |
| 11. Random seed 1 (E016-03) | 0.85 | 15.4% | −33.8% | 0.46 |
| Random seed 2 (E016-04) | 0.62 | 10.6% | −38.0% | 0.28 |
| Random seed 3 (E016-05) | 0.67 | 13.3% | −40.4% | 0.33 |
| Random seed 4 (E016-06) | 0.75 | 13.4% | −40.6% | 0.33 |
| Random seed 5 (E016-07) | 0.98 | 18.5% | −36.4% | 0.51 |

**12. Median random comparison:**
- The median random Sharpe is **0.75** (seed 4); the range is 0.62 to 0.98.
- H016's 0.69 is **below** the median and beats only 2 of the 5 random portfolios.

### Gates (items 13–16)

| Gate | Requirement | Result | Pass |
|---|---|---|---|
| **G1.1** | Sharpe − EW-H016 ≥ +0.25 **and** Sharpe − SPY ≥ +0.10 | **−0.16** and **−0.23** | ✗ |
| G1.2 | CAGR ≥ EW-H016 − 2 pts | 12.8% vs 14.4% − 2 | ✓ |
| G1.3 | Calmar ≥ EW-H016 | 0.32 vs 0.40 | ✗ |
| G1.4 | Max DD ≥ EW-H016 − 5 pts | −40.5% vs −36.0% − 5 | ✓ |
| **13. G1** | all of the above | | **✗ FAIL** |
| **14. G2** | Sharpe > median of 5 random controls | 0.69 vs 0.75 | **✗ FAIL** |
| **15. G3** | beat EW-H016 in ≥ 4 of 6 two-year blocks, total excess > 0 | 2 of 6 blocks (see below); total excess −11 pts | **✗ FAIL** |
| **16. G4** | (a) perturbations, (b) 2× slippage, (c) cost ≤ 1.5% a year | (a), (b) not run (§9); (c) 0.30% ✓ | **✗ FAIL** (a gate that is not run fails) |

**G3 blocks** (Sharpe(H016) − Sharpe(EW-H016)):

| 2010–11 | 2012–13 | 2014–15 | 2016–17 | 2018–19 | 2020–21 |
|---|---|---|---|---|---|
| +0.26 | −0.59 | −0.12 | −0.71 | +0.06 | −0.22 |

### Diagnostics (items 17–22; never gates)

**17. Survivorship sensitivity** (pre-declared):

| View | Sharpe(H016) − Sharpe(EW-H016) |
|---|---|
| Base | −0.16 |
| S1: frozen yearly penalty applied | −0.21 |
| S2: from 2012-01-01 (low-coverage years excluded) | −0.26 |

The failure does not depend on the residual survivorship gap or on the 2010–2011 low-coverage years. The candidate is **worse** relative to EW once they are excluded.

**18. Yearly coverage** (mean H016-universe size at the year's rebalances):

| 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 539 | 535 | 623 | 698 | 813 | 820 | 801 | 848 | 913 | 884 | 917 | 1,097 |

Calendar-year returns (2010 from March):

| | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H016 | 15.8% | 15.8% | 2.4% | 45.0% | 2.3% | 2.2% | −2.6% | 21.0% | 5.4% | 18.7% | 35.0% | 0.1% |
| EW-H016 | 18.5% | 0.7% | 17.5% | 36.1% | 10.5% | −2.6% | 13.4% | 20.1% | −6.5% | 27.8% | 24.5% | 18.4% |
| SPY | 14.3% | 1.8% | 15.7% | 31.4% | 13.2% | 1.3% | 11.7% | 21.2% | −4.5% | 30.5% | 18.0% | 28.0% |

**19. $200K sensitivity** (E016-08; sensitivity only):
- Sharpe 0.71, CAGR 13.3%, Sharpe − EW-H016 = −0.14, costs 0.23% a year.
- It does not change the conclusion, and by rule it could not rescue it.

**20. DSR** (frozen formula; diagnostic):
- P2 candidates (N = 3): **0.83**;
- P2 broad (N = 3; no robustness runs): 0.83;
- cumulative (N = 43): **0.09**.

All three are below the 0.90 warning level. The PSR against zero is 0.99, which only says the strategy's own return was positive.

**21. PBO:** not computable, as there is a single candidate and no perturbation runs (spec §10).

**22. Does the ranking add value?** **No evidence that it does.**
- H016's Sharpe is 0.06 below the median random portfolio drawn from the same universe with identical mechanics, and it beats only 2 of the 5 seeds.
- By two-year block, it beats most random seeds only in 2010–11 and loses to most of them in 2012–13, 2016–17 and 2020–21.
- Paired block-bootstrap 95% intervals for Sharpe(H016) − Sharpe(X):

  | X | Point estimate | 95% interval |
  |---|---|---|
  | EW-H016 | −0.16 | [−0.51, +0.14] |
  | SPY | −0.23 | [−0.68, +0.14] |

  Against every random seed, the interval contains zero.
- The candidate also turns over about twice as much as the random books (149% vs 48–80% a year), for no gain.

### 23. Holdout access

**H016 does not qualify. No Holdout request is made.** The Holdout (2022-01-01 → 2026-08-31) and all later data remain locked and unread.

## What this means

On 2010–2021 large US non-financial stocks with point-in-time fundamentals, buying the 20 most gross-profitable companies (relative to assets) each quarter did not do better than simply holding the whole universe equally weighted, or than holding 20 random names from it.

- The literature's profitability premium is mostly measured on broad, long-short, value-weighted portfolios, often including small stocks and earlier decades. It did not show up in this long-only, $2B+, concentrated, 2010–2021 implementation.
- The weakness is broad, not one bad episode: H016 lagged EW-H016 in 4 of 6 blocks.
- The data infrastructure (v1, frozen) and the position-sizing rule behaved as designed. The canary passes, top-up costs are negligible (about 0.06% a year), and exposure is about 95%. The result is not an artefact of the new mechanics.

## Programme status and the decision for the owner

- **Phase 2 budget:**
  - 2 of 3 hypothesis slots consumed (H014 rejected; H016 not development-qualified);
  - **1 slot remains**;
  - Holdout locked.
- **Prohibitions in force:** no change to GP/A, the universe, the schedule, the sizing rule, the controls or the gates after this result (spec §12). H016 must not be re-run with changes.
- **Options:**
  1. Close H016 as rejected and stop Phase 2 here: "No Production Candidate Found". This is a defensible, honest outcome after two well-specified hypotheses.
  2. Close H016 as rejected, and ask for a written proposal for hypothesis 3 (pre-registration only, no implementation). It must be motivated without hindsight from these results.

  **Recommendation:** option 1 unless you specifically want to spend the last slot. If you choose option 2, hypothesis 3 should be economically distinct from GP/A (not a re-weighting or another profitability metric, which the H016 approval excludes), and it should be judged under the same gates.

**STOP. Awaiting the owner.**
