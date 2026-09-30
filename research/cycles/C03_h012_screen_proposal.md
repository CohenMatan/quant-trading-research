# H012 alternative screening items (proposal D084)

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **PROPOSED, NOT IN FORCE. Awaiting owner approval.** No H012 candidate result exists, and no C03 strategy backtest has run. |
| Owner request | "C03 — Final Prerequisites and Conditional Execution Approval", Option 2. |
| Evidence | `research/cycles/C03_h012_screen_sim.py` produces `C03_h012_screen_sim.json`. It uses synthetic data, plus a null test on real pre-C03 benchmark returns (EW E901-07, SPY E900-07, IS only) with uninformative, time-shifted signals. No C03 result and no Validation data are used. H012's actual rule is never run on real data. |
| Scope | **H012 only**: its three variations and their robustness and Validation runs. H013 and all other hypotheses keep the existing screen unchanged. |

## 1. The problem, precisely

The IS screen (D036) has four items computed from closed round-trip trades. For H012 they fail or become meaningless **for structural reasons, not because of weak evidence**:

| Item | Why it does not fit H012 |
|---|---|
| Closed trades ≥ 100 | H012 holds the 15 largest stocks and replaces only about 1–3 per quarter. A position closes only when a stock leaves the basket. The canary closed 8 trades in 2 years; expect about 30–40 over IS. |
| Profit factor ≥ 1.2 | |
| 95% bootstrap CI of expectancy > 0 | |
| Expectancy without the best 5% of trades > 0 | |

The last three items share the same faults:

1. **They measure the wrong thing.** A closed trade's profit is the return of a large-cap stock while it was held: a stock-selection outcome, which Control A has too. Timing, the thing H012 claims, changes position **sizes**, and sizes appear in no closed-trade figure.
2. **Positions still open at the end are ignored.** Stocks held for all 8 years (most of the basket) never count.
3. **With 30–40 trades the statistics are unreliable.** The trades overlap in time and all move with the same market, so they are not independent. "The best 5%" means 2 trades.

The same structural problem applies to the **Validation** item "≥ 50 closed trades" (about 15–20 expected in 4 years). See §6.

## 2. What stays unchanged for H012 (all other screening requirements)

- **IS screen, portfolio-level items:**
  - Sharpe ≥ 0.50;
  - Sharpe ≥ EW + 0.10;
  - max drawdown ≥ −35% and no worse than EW;
  - the three IS stress episodes (drawdown no more than 5 points worse than EW);
  - positive in ≥ 5 of 8 years;
  - no year above 40% of total profit;
  - Sharpe ≥ 0.40 at 2× slippage.
- **Robustness:** plateau (≥ 7 of 8 perturbations keep ≥ 70% of the base Sharpe), Sharpe > 0 at 4× costs, every IS third with Sharpe > 0.
- **DSR** ≥ 0.90 at the official and the conservative N, on IS + VAL. **PBO** stays a diagnostic. The mechanical choice of variation is unchanged.
- **Validation:** Sharpe ≥ 0.40, ≥ 0.5 × IS and above EW; max drawdown ≥ −35%; the 2020 check. The trade-count item is covered in §6.
- **H012's trading rules are unchanged.** Nothing is altered to create more trades.

## 3. The proposed replacement: five timing items (all must pass)

**Notation:**

- r_V, r_A, r_B are the aligned daily net returns over IS of:
  - V, the variation;
  - A, Control A (fully invested, E012-04);
  - B, **the variation's own** Control B (causal, exposure-matched: E012-05/06/07).
- SR(x) = mean(x) / std(x, ddof = 1) × √252.
- ΔB = SR(V) − SR(B), and ΔA = SR(V) − SR(A).

| Item | Definition | Pass if | Replaces |
|---|---|---|---|
| **T1: timing decisions** | Number of applied exposure changes during IS (changes beyond the 0.10 band). The first close is not counted. | **≥ 8** (on average one per IS year) | Closed trades ≥ 100 |
| **T2: statistical evidence of timing value** | Paired **stationary block bootstrap** (Politis–Romano): 10,000 resamples of the IS days, mean block length 63 sessions, seed 20260930. The same days are drawn for V and B. Take the **2.5% quantile** of the bootstrap distribution of ΔB. | **> 0** | 95% bootstrap CI of expectancy > 0 (same confidence level) |
| **T3: better than fully invested** | ΔA, the point estimate | **> 0.05** (the materiality margin already in H012.md) | Profit factor ≥ 1.2 |
| **T4: not one year** | ΔB recomputed with each IS calendar year removed in turn (8 samples) | **Every sample > 0** | Expectancy without the best 5% of trades |
| **T5: subperiod consistency** | ΔB in each third of IS (the same thirds as the robustness item) | **> 0 in at least 2 of 3** | Added (no counterpart) |

The exact code is `h012_timing_items` and `boot_sharpe_diff` in `C03_h012_screen_sim.py`. After approval it moves unchanged into `src/qresearch` with tests.

## 4. Why these items separate timing from lower exposure and good markets

- **Lower exposure alone cannot pass.** Cash earns 0%, so holding a constant fraction of the basket leaves the Sharpe ratio unchanged. Control B has about the same average exposure, but it does not respond to current volatility.
  - A book that is merely less invested has ΔB ≈ 0, so it fails T2 (which needs a positive lower bound) and usually T3.
- **Favourable markets cancel out.** V, A and B hold the same basket on the same days. The bootstrap draws the **same days** for V and B, so the market's direction is shared and drops out of ΔB. Only differences in **when** exposure was high or low remain.
- **One lucky episode is not enough.**
  - T4 removes each year in turn, including 2011, the largest volatility episode in IS.
  - T5 requires consistency across subperiods.
- **Degenerate timing is excluded.** A variation that almost never changes exposure has nothing to test, and fails T1.

## 5. Statistical calibration (no C03 data)

### 5.1 Setup

**Synthetic data** (300 repetitions per scenario):

- 2,012 daily returns, the IS length;
- a GARCH(1,1) market with Student-t shocks, i.e. volatility clustering;
- a 15-stock basket = market + idiosyncratic noise;
- the H012 v1.0 rule (monthly, RV21, band 0.10, next-day application) with realistic costs, together with Controls A and B.

**Semi-real null:** the real IS returns of the equal-weight benchmark, traded with exposure paths computed from SPY returns shifted in time by at least one year. These paths are realistic but carry no information about the traded days (72 overlapping shifts). **The unshifted rule, which would preview H012, is never computed.**

### 5.2 Results: probability that all five items pass

| True situation | ΔB (mean ± sd) | T2 | All five | All five at q = 0.05 | All five at q = 0.10 |
|---|---|---|---|---|---|
| **N1** no timing value: expected return ∝ variance, so constant exposure is optimal | −0.055 ± 0.077 | 0.7% | **0.7%** | 1.0% | 2.7% |
| **N2** uninformative timing: the exposure path comes from an unrelated volatility path | −0.044 ± 0.056 | 0.7% | **0.3%** | 1.3% | 1.7% |
| **Semi-real null** (real EW returns, shifted SPY signal) | median −0.037 | 0/72 | **0/72** | | |
| **A1** genuine timing value: constant expected return (Moreira–Muir) | +0.000 ± 0.069 | 2.3% | **2.3%** | 4.3% | 7.0% |
| **A2** constant conditional Sharpe | −0.012 ± 0.078 | 0.7% | **0.7%** | 3.7% | 7.0% |
| **A3** as A1, with stronger volatility clustering | +0.042 ± 0.108 | 4.3% | **4.3%** | 8.0% | 16.7% |

**Block-length check.** Under the nulls, T2 passes 0.7–1.3% of the time for mean block lengths of 5, 21, 63 and 126 days. It is not sensitive to that choice, and it is below its nominal 2.5%. Costs and the cap make the no-edge difference negative on average, so the test errs strict.

### 5.3 What the calibration shows

1. **The standard does not fall.** With no genuine edge, all five items pass together 0.3–0.7% of the time (0 of 72 on real returns). The main protection is T2.
   - T3, T4 and T5 are consistency checks. They are **not** independent statistical evidence: under the nulls they pass individually 3–22% of the time.
   - T1 never binds for this rule. It only excludes degenerate cases.
2. **Power is very low, and this is a finding about H012 itself.**
   - Even when volatility timing has genuine value in the market, H012's no-leverage rule (exposure between 0 and 1) raises the Sharpe ratio over Control B by only about 0 to +0.04 on average.
   - Over 8 years the noise in that difference (standard deviation 0.06–0.11) is larger than the effect.
   - So the rule passes 2–4% of the time at the proposed level, and 7–17% at a looser one-sided 90% level.
   - The large gains reported in the literature come from **leveraged** volatility-managed portfolios over many decades. H012 is capped at full investment and has only 8 years of IS.
3. **Loosening T2 would buy little.** Moving from q = 0.025 to q = 0.10 roughly triples the false pass rate (0.3–0.7% → 1.7–2.7%) and still leaves power below 17%. H012 must also pass the unchanged items, including Sharpe ≥ EW + 0.10 and, much later, the DSR at N = 43 (about 1.48 Sharpe over IS + VAL). The binding constraint is therefore unlikely to be T2.

## 6. Validation (replacement for "≥ 50 closed trades", H012 only)

Proposed, and applied only if Validation is later approved:

- **V1:** ≥ 4 applied exposure changes in VAL (the same one-per-year rule as T1).
- **V2:** SR(V) − SR(B) > 0 in VAL (point estimate). This needs **one extra Validation backtest**, the variation's Control B in VAL, which would count in the research budget when Validation is authorised.

All other Validation gates and the DSR stay unchanged.

## 7. Limitations

- **Dependence.**
  - Daily returns are not independent: volatility clusters. The block bootstrap keeps dependence up to roughly a quarter, and the calibration shows the result is insensitive to the block length. It still assumes the IS period is one stationary process.
  - IS 2010–2017 contains only about three volatility episodes (2010, 2011, 2015–16). The effective number of independent timing "events" is therefore small whatever the number of days.
- **T3–T5 reuse the same data as T2.** They add consistency, not new evidence. Passing all five is not five independent confirmations.
- **Control B is an imperfect counterfactual.** It follows past volatility slowly, so part of any genuine timing effect may also show up in B. That makes ΔB conservative.
- **The three H012 variations share data and are highly correlated.** Each is judged separately. Their joint multiplicity is handled by the DSR N (unchanged).
- **The synthetic models are simplifications.** Real crises (e.g. 2008) have stronger volatility regimes than GARCH, which would favour timing. None occurs in IS.
- **The calibration uses H012 v1.0's form (monthly, RV21).** v1.1 (RV63) and v1.2 (weekly) differ in speed but not in the logic of the test.

## 8. Decision requested (D084)

Approve for **H012 only**, before any H012 result:

1. Replace the four trade-level IS items with **T1–T5**, with exactly the definitions and thresholds of §3: T2 at the 2.5% quantile, block 63, 10,000 resamples, seed 20260930.
2. Replace the Validation trade-count item with **V1 and V2** (§6). V2 includes one extra Control B Validation backtest if H012 ever reaches Validation.
3. Leave everything else unchanged (§2).

**Recommendation: approve at the 2.5% level as proposed.**

- It keeps the confidence level of the item it replaces, and it holds false acceptance below 1%.
- Loosening it would not materially change H012's prospects, because the unchanged Sharpe and DSR requirements are the binding ones.
- **H012 is expected to be rejected with high probability.** If so, it will now be for lack of statistical evidence, which is a legitimate reason, not for a trade count it could never reach.
