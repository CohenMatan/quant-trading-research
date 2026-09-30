# Phase 2 methodology amendment (P2-CP0c): forward testing, hypothesis budget, G1

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **PROPOSAL. STOP, awaiting owner approval.** Nothing implemented; no H014 candidate or control has run; the Holdout was not accessed. |
| Amends | `P2_CP0b_revised_evaluation_methodology.md` §3 (forward period), §5 G1, §8 (hypothesis budget). Everything else in P2-CP0b, as approved in principle by the owner, is unchanged. |
| Evidence | `research/phase2/P2_amendment_sim.py/.json` (simulations only; seed 20261003). Part A compares budget schedules under sequential screening. Part B tests the G1 return-risk rule on 12-year daily paths with realistic crash regimes. |

## 1. Historical Holdout versus true forward testing

There are four kinds of data, each defined by **when it can be seen**, not only by calendar dates:

| Name | Period | Status and use |
|---|---|---|
| **D: Development** | 2010-01-04 → 2021-12-31 | Used to discover and evaluate. Not untouched: programme 1 learned from it. |
| **H: Historical Holdout** | 2022-01-01 → 2026-08-31 | Locked. Opened once, after the freeze and with written owner approval, for one frozen candidate. |
| **U: Additional historical unseen data** | 2026-09-01 → the freeze timestamp FZ | Locked from now. Historical, **not** forward. At a freeze in the coming weeks or months it will be only a few months long, so it is **reported next to H as a supplementary historical check, not gated**. It is opened together with H, under the same single unlock. |
| **F: True forward data** | Sessions opening **after FZ** | Did not exist when the candidate was frozen, so it cannot have influenced it. This is the only genuine forward test. |

**The freeze timestamp FZ** is the UTC time of the commit that hash-pins the frozen candidate specification (rules, parameters, construction, costs, benchmarks, criteria), together with the owner's written freeze approval (`FREEZE.md`).

- The forward clock starts at the first market open after FZ.
- Forward evaluations are pre-declared at freeze: after about 12 months and about 24 months of F. Each is a single backtest of the frozen strategy over F.
- Its criteria are written into the freeze (the same form as HO1–HO3, with the forward period in place of the Holdout).

**Order of events:**

1. The candidate passes the development gates.
2. It is frozen at FZ.
3. The owner approves unlocking H and U together.
4. H and U are evaluated once.
5. If the Holdout criteria pass, the forward test on F follows.

**The code lock already enforces this.** Every run whose end date is after 2021-12-31 is refused (`LAST_UNLOCKED_DATE`, tested by `tests/test_holdout_lock.py`), so both H and U are locked by code today. No change is needed.

## 2. Hypothesis-budget schedules

**Question.** At most 3 Phase 2 hypotheses may be screened on D before the one-time Holdout is used. Which development margin (the Sharpe improvement over EW required at gate G1) should each hypothesis face?

**Process modelled (realistic).** Hypotheses are screened one at a time. The first to clear its margin is frozen and uses the Holdout, whether it passes there or not, and the search then stops.

**Model.** Unchanged from P2-CP0b. The development noise in the Sharpe difference is ±0.20 over 12 years, and the Holdout noise ±0.32. The correlation with EW is 0.76, calibrated on committed programme-1 books; sensitivity to 0.70 and 0.85 is shown. The Holdout gate is +0.10.

- **"No-edge accepted"** is the probability that some hypothesis with no real edge ends up accepted.
- **"Power"** is the probability that a genuinely better hypothesis is accepted when it is screened first, second or third.
- Gates G2–G4 are not modelled, so all no-edge rates are **upper bounds**.

**Results at correlation 0.76:**

| Schedule (hypotheses 1 / 2 / 3) | No-edge accepted, after 1 / 2 / 3 hypotheses | Power, true +0.3 (as #1 / #2 / #3) | Power, true +0.5 (as #1 / #2 / #3) |
|---|---|---|---|
| Fixed +0.20 | 8.3% / 14.7% / **19.8%** | 57 / 45 / 35% | 86 / 67 / 52% |
| +0.20 / +0.25 / +0.30 | 8.3% / 12.7% / 15.3% | 57 / 40 / 29% | 86 / 66 / 54% |
| +0.20 / +0.30 / +0.40 (the earlier proposal) | 8.3% / 11.2% / 12.1% | 57 / 35 / **21%** | 86 / 63 / 49% |
| Equal error budget (+0.20 / +0.29 / +0.33) | 8.3% / 11.6% / 13.4% | 57 / 36 / 28% | 86 / 64 / 54% |
| **Fixed +0.25** | **5.7% / 10.5% / 14.7%** | **51 / 43 / 37%** | **84 / 71 / 61%** |
| Fixed +0.30 | 3.7% / 7.1% / 10.1% | 44 / 40 / 36% | 81 / 73 / 66% |

Sensitivity: at correlation 0.70 every no-edge rate is about 2–3 points higher; at 0.85 it is about 5–7 points lower (`P2_amendment_sim.json`).

**Why +0.10 per step?** It was **not** statistically derived; it was a round-number heuristic. The principled version is the **equal error budget**: each later hypothesis gets 1/k of the first one's false-pass chance, Bonferroni-style, which gives +0.20 / +0.29 / +0.33. The +0.40 step was stricter than needed.

**Do rising margins mainly improve false-positive control, or mainly reduce power?** Mainly reduce power.

- Rising from +0.20 to +0.40 cuts no-edge acceptance after 3 hypotheses from 19.8% to 12.1%.
- But it cuts the third hypothesis's power for a real +0.3 edge from 35% to 21%. That is the "punishing later ideas" effect you asked about.
- Much of the loss for later ideas is structural anyway. With one Holdout, an earlier no-edge idea that passes by luck uses it up before a better later idea is tested. Rising margins do not fix that.

**A fixed margin treats every hypothesis equally, and the budget of 3 does the controlling.** Fixed +0.25 compared with the rising schedule:

- **Lower** no-edge acceptance for the first and second hypotheses (5.7% vs 8.3%; 10.5% vs 11.2%);
- **slightly higher** after the third (14.7% vs 12.1%);
- **much better** power for later ideas (37% vs 21% at +0.3; 61% vs 49% at +0.5);
- a little less power for the first idea (51% vs 57% at +0.3).

## 3. Recommended rule

**Hypothesis budget: at most 3 Phase 2 hypotheses, each screened against a fixed development margin of Sharpe(H) − Sharpe(EW) ≥ +0.25**, one at a time. The first to pass all development gates is frozen and uses the Holdout. After that, no more hypotheses are screened against this Holdout.

**Why this rule:**

- It is the simplest rule, with one number and equal treatment of every idea.
- It controls repeated searching: no-edge acceptance stays at or below about 15% after the full budget. That is an upper bound; with gates G2–G4 and the 2-year forward test (which about halves it) the real figure is lower.
- It keeps reasonable effects detectable: a real +0.5 edge is accepted 61–84% of the time, and a real +0.3 edge 37–51%.

**The stricter alternative is fixed +0.30:** at most 10% no-edge acceptance, but power for a +0.3 edge of 36–44%.

**Consequence for H014.** Its G1 margin becomes **+0.25** (previously proposed +0.20).

## 4. Revised G1: combined return-risk rule

**All four constraints must hold on 2010–2021 at $100K.** Each is transparent, none is weighted, and none is fitted to data.

| # | Constraint | Purpose |
|---|---|---|
| G1.1 | Sharpe(H) − Sharpe(EW) ≥ +0.25 (the budget margin), **and** Sharpe(H) − Sharpe(SPY) ≥ +0.10 | Better risk-adjusted return than passive investing |
| G1.2 | CAGR(H) ≥ CAGR(EW) − 2.0 percentage points a year | Rules out a "better Sharpe" that only comes from holding much less stock |
| G1.3 | Calmar(H) ≥ Calmar(EW), where Calmar = CAGR ÷ \|maximum drawdown\| | Return per unit of worst loss must be at least as good as the benchmark's. A deeper drawdown is allowed **only if paid for by proportionally higher return**. |
| G1.4 | Maximum drawdown(H) no more than **5 percentage points deeper** than EW's | A plain upper limit so that no amount of return can buy a dramatically worse drawdown |

**How your examples resolve:**

| Candidate vs EW | G1.1 | G1.2 | G1.3 | G1.4 | Result |
|---|---|---|---|---|---|
| Sharpe +0.3; CAGR +2 pts; drawdown 3 pts deeper | ✔ | ✔ | ✔ (higher return per unit of drawdown) | ✔ | **Qualifies.** A slightly worse drawdown is no longer a veto. |
| CAGR +3 pts; drawdown 15 pts deeper | — | ✔ | depends | ✘ | **Fails**: dramatically worse drawdown |
| Sharpe +0.3; CAGR −1.5 pts; drawdown 10 pts shallower | ✔ | ✔ | ✔ | ✔ | **Qualifies**: better risk, a practical return |
| Sharpe +0.3; CAGR −4 pts (mostly cash) | ✔ | ✘ | — | — | **Fails**: the owner could simply hold less stock |

**Why no absolute drawdown cap such as −35%?** 2010–2021 includes the 2020 crash, so the equal-weight benchmark's own drawdown over this period is much deeper than its 2010–2017 value. An absolute cap would reject the benchmark itself. Relative constraints G1.3 and G1.4 compare like with like.

**Simulation (Part B)**, 12-year paths with crash regimes. Each figure is the probability of passing G1 at a +0.20 margin; the relative comparison is the same at +0.25.

| Candidate type | True Sharpe edge | Sharpe only | Old G1 (drawdown ≤ EW) | **Revised G1** |
|---|---|---|---|---|
| Same risk as EW | 0 | 18.7% | 17.3% | 18.5% |
| Same risk as EW | +0.3 | 69% | 65% | **69%** |
| Same risk as EW | +0.5 | 92% | 87% | **91%** |
| 30% more risk | 0 | 19.2% | 11.2% | 16.3% |
| 30% more risk | +0.3 | 69% | **40%** | **60%** |
| 30% more risk | +0.5 | 92% | 56% | **82%** |
| 30% less exposure | +0.3 | 68% | 60% | 60% |

**Reading:**

- The old drawdown veto rejected many genuinely better, slightly riskier strategies, as you suspected: 40% vs 60% at +0.3.
- The revised rule recovers most of that while still filtering high-risk candidates with no edge: 16% vs 19% for Sharpe alone.
- For low-exposure candidates G1.2 behaves as intended.

## 5. Updated false-positive and power estimates (whole pipeline)

Under the recommended rule (fixed +0.25, budget of 3, Holdout gate +0.10, correlation 0.76):

- **No-edge acceptance: at most about 5.7% (1 hypothesis) up to at most about 14.7% (3 hypotheses).** Gates G2–G4 are not modelled, so these are upper bounds.
- With the 2-year forward test, roughly half those figures (P2-CP0b's forward modelling).
- **Power:**

  | True edge | Screened as #1 | Screened as #3 |
  |---|---|---|
  | +0.3 | 51% | 37% |
  | +0.5 | 84% | 61% |

## 6. Important downsides of the revised practical framework

1. **The Holdout remains weak evidence on its own.** A no-edge strategy passes its +0.10 gate about 38% of the time over 4.7 years. It is one additional piece of evidence, never proof. The forward test is required before any real-money decision.
2. **A one-shot Holdout plus sequential screening means a lucky early idea can use it up.** At correlation 0.76, a no-edge first idea passes development and consumes the Holdout about 15% of the time before a later good idea is tested.
3. **DSR as a diagnostic removes protection against the research history outside Phase 2.** Programme 1's 40 candidates on the same years influenced our thinking, and no budget or margin can measure that. It is reported (the cumulative-N DSR), not controlled.
4. **The drawdown measures are noisy.** Maximum drawdown and Calmar depend on one path and one worst episode. The 5-point tolerance is a convention, not a derived value.
5. **U will be tiny.** A few months of extra historical data adds little evidence. It is reported, not gated.
6. **Forward testing is slow**, taking 1–2 years, and the forward period can itself be unusual.
7. **The calibration is uncertain.** At a correlation of 0.70 every no-edge figure is about 2–3 points higher.

## 7. Decisions still requiring owner approval

1. The four data categories and the **freeze-timestamp definition of the forward test** (§1): U locked, opened with H, reported but not gated.
2. **Hypothesis budget: at most 3 hypotheses, with a fixed +0.25 development margin** (§3). The stricter alternative is fixed +0.30; the previous proposal 0.20 / 0.30 / 0.40 is not recommended.
3. **Revised G1** (G1.1–G1.4, §4), replacing the drawdown veto.
4. Confirmation that H014's margin is **+0.25**, and that Holdout criteria HO1–HO3, G2–G4 and all other approved items are unchanged.
5. A CLAUDE.md update for Phase 2 once the above is approved.

After approval I will:

1. write the frozen, hash-pinned Phase 2 specification, with its tests;
2. implement S014 and the controls, with tests and canaries;
3. run the committed development runs;
4. stop at the development checkpoint.
