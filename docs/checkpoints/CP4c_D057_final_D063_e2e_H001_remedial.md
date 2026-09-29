# Checkpoint 4c: D057 final, D063 end-to-end verification, H001 remedial re-test

| Field | Value |
|---|---|
| Status | **STOPPED. Awaiting owner approval.** C02 not designed. No Validation, Walk-Forward or Holdout access (IS dates only; no date after 2017-12-29 in any strategy run). |
| Outcome | **H001 is rejected on a valid test.** All five pre-registered variations fail the original C01 in-sample screen. **C01 remains: No Production Candidate Found.** |
| Tests | 276 passing |

## 1. D057 final status: complete

**What changed** (D065; sources in `docs/data/universe_overrides.md`).

- The remaining gaps are fixed with **dated** rules keyed to each security. Every date was confirmed from SEC filings or company releases:

| Security | Excluded until | Status |
|---|---|---|
| KKR | 2018-06-30 | partnership units |
| Apollo | 2019-09-04 | LLC shares |
| Ares | 2018-11-25 | partnership units |
| Blackstone | 2019-06-30 | partnership units |
| Carlyle | 2019-12-31 | partnership units |
| Texas Pacific Land | 2021-01-10 | trust sub-shares |
| KFN | its whole life | LLC shares |
| MIC | 2015-05-20 | LLC interests; a corporation from 2015-05-21 |

- Yahoo is eligible until 2017-06-15; from 2017-06-16 it is the fund Altaba.

**Survivorship-safe.** The current-status Morningstar LLC flag is never used on its own. Corporations acquired later (VMware, Sprint, BNSF and others) stay eligible.

**Tests.** Every override is tested on both sides of its boundary, using the real Morningstar fields.

**Verification (E956-03, monthly 2010–2021).**

- Each dated security appears only after its conversion: KKR from July 2018, Apollo from October 2019, MIC from June 2015, Texas Pacific Land only in 2021.
- KFN is absent.
- No partnership-flagged security remains. The fund template remains only for the four documented overrides.

**Correction.** CP4 counted MIC as a non-common holding of E005-28. MIC was a corporation from 2015-05-21, so that 2021 holding was ordinary common stock. This does not change CP4's verdict.

## 2. D063 end-to-end verification: passed

**Canary E958-01** (X958, 2012; infrastructure, not a trial):

| Requirement | Result |
|---|---|
| Stock selected at the close, next-open buy queued | 24 picks (the last on 2012-12-31, the final day, so it had no next open) |
| Stock leaves the universe overnight while the buy is pending | **23 of 23** removed while pending |
| Price history survives the removal | **23 of 23** |
| The next-open buy still fills | **23 of 23**, history present at every fill |
| The normal exit rule (a time exit that reads the history, as H001's does) executes | **23 of 23** exits submitted at age 3 and filled |
| Safety net: history deliberately deleted after the fill | 4 deleted, **4 restored**, exits still fired |
| Positions without history at a close; positions stuck at the end | **0; 0** |

**Confirmed again in the real H001 runs below:**

- no position held longer than 18 calendar days (the rule allows 10 trading days);
- nothing stuck at the end;
- no history restores needed.

## 3. H001 remedial re-test: the five corrected results

**Setup.**

- Runs E001-16..20 are identical to the pre-registered E001-11..15 (checked field by field). Only the ID, the label "H001 remedial re-test after infrastructure correction", the benchmark references and the corrected harness (D057 + D059 + D063) differ.
- All five were run. Nothing was selected.
- The plan was fixed in advance in `research/cycles/C01_H001_remedial_plan.md`.
- The benchmark is the equal-weight ≥ $2B universe E901-07 on the same harness: IS Sharpe 0.92, max drawdown −22.3%.
- All integrity checks pass on all five runs.

| Run | Variation | CAGR | Sharpe | Max DD | Closed trades | Profit factor | Positive years | Avg positions | Costs per year (commission + slippage) | Before the fix (bugged): CAGR / Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| E001-16 | v1.0 RSI(2) ≤ 10, exit above 5-day mean | −7.7% | −0.82 | −49.2% | 3,262 | 0.72 | 0/8 | 5.4 | 8.0% + 6.0% | 1.7% / 0.19 |
| E001-17 | v1.1 RSI(2) ≤ 5 | −3.8% | −0.47 | −29.3% | 2,432 | 0.77 | 2/8 | 4.0 | 5.2% + 4.0% | 1.7% / 0.19 |
| E001-18 | v1.2 10-day time exit | +1.8% | 0.20 | −30.0% | 2,705 | 0.99 | 5/8 | 13.5 | 4.1% + 4.2% | 4.3% / 0.36 |
| E001-19 | v1.3 + market regime filter | −3.7% | −0.67 | −29.0% | 1,679 | 0.69 | 2/8 | 2.8 | 3.6% + 2.8% | −4.7% / −0.45 |
| E001-20 | v1.4 3-day drop ≥ 6% | −5.6% | −0.27 | −50.6% | 3,521 | 0.90 | 2/8 | 7.8 | 6.7% + 5.8% | 13.5% / 0.69 |

**Exact gate results** (original C01 IS screen, D036; ✅ pass, ❌ fail). Every variation passes the same four gates (trade count, flash crash, downgrade, and China-oil except v1.2) and fails the rest:

| Gate | Requirement | v1.0 | v1.1 | v1.2 | v1.3 | v1.4 |
|---|---|---|---|---|---|---|
| Closed trades | ≥ 100 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Sharpe | ≥ 0.50 | ❌ | ❌ | ❌ | ❌ | ❌ |
| Sharpe vs EW + 0.1 | ≥ +0.10 | ❌ | ❌ | ❌ | ❌ | ❌ |
| Max drawdown | ≥ −35% and ≥ EW | ❌ | ❌ | ❌ | ❌ | ❌ |
| Episode: 2010 flash crash | ≥ EW − 5 points | ✅ | ✅ | ✅ | ✅ | ✅ |
| Episode: 2011 downgrade | ≥ EW − 5 points | ✅ | ✅ | ✅ | ✅ | ✅ |
| Episode: 2015–16 China/oil | ≥ EW − 5 points | ✅ | ✅ | ❌ | ✅ | ✅ |
| Profit factor | ≥ 1.20 | ❌ | ❌ | ❌ | ❌ | ❌ |
| Expectancy CI lower bound | > 0 | ❌ | ❌ | ❌ | ❌ | ❌ |
| Positive years | ≥ 5 of 8 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Largest year's share of profit | ≤ 40% | ❌ (total loss) | ❌ (loss) | ❌ (144%) | ❌ (loss) | ❌ (loss) |
| Expectancy without the best 5% | > 0 | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Passed** | | **4/12** | **4/12** | **4/12** | **4/12** | **4/12** |

**Screen: all five FAIL.**

- Per the pre-declared plan, no 2× slippage and no robustness runs follow.
- No new parameters or variations were created.
- PBO across the five variations: 0.07, reported only. Every variation fails, so there is nothing to select.

## 4. Does H001 remain rejected?

**Yes, now on a valid test.**

- Correctly implemented, the short-term reversal rules trade far more often than before: 1,700–3,500 trades, instead of stuck slots.
- They lose 7–14% of equity a year to the fixed $7 commission and 10 bps slippage.
- Their raw edge before costs is small or negative: profit factor at most 0.99.
- The bugged runs looked better (v1.4: 13.5% CAGR) only because stuck positions turned them into accidental buy-and-hold portfolios in a rising market.
- **There is no legitimate H001 candidate.** Nothing is proposed for Validation.

## 5. Confirmations

- **No hypothesis tuning occurred.** Signals, parameters, exits, sizing, costs, timing and the no-borrowing rule are unchanged from pre-registration. All five variations were run and reported. The only change is the corrected infrastructure.
- **No Validation, Walk-Forward or Holdout data were used.** Strategy runs covered 2010-01-04 → 2017-12-29 only. The verification probe E956-03 scans 2010–2021 only to check classification; it trades nothing.
- **All history is preserved.** The original H001 runs E001-01..15 remain in the registry, annotated bugged/inconclusive. Nothing was overwritten.

## 6. Trial accounting (D066; `registry.trial_accounting`)

| Category | Count | Counts toward DSR/PBO? |
|---|---|---|
| **Genuine strategy trials** (distinct configurations: 19 C01 variations + 15 robustness + 1 Validation) | **35** | yes |
| Technical repeats (re-runs of an identical configuration after D051/D054 fixes, operational retries, and the 5 H001 remedial runs) | 46 | no |
| Attempts that never started | 7 | no |
| Verification, canary, probe and benchmark runs (incl. E956-03, E958-01, E901-07) | 37 | no |
| All research runs that started (conservative figure used so far) | 81 | reported |

## 7. Decision needed

- Approve this checkpoint.
- Decide whether to design Research Cycle 2. Nothing has been started.
