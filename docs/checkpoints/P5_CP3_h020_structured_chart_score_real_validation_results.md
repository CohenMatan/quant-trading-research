# P5-CP3 — H020 Structured Chart Score Real Validation Results (STOP)

- **Date:** 2026-10-05.
- **Owner authorisation:** "H020 — Authorise Real Structured Chart Score Validation" (D154; `docs/owner/2026-10-05_h020_real_validation_authorisation.md`).
- **Specification:** `research/phase5/H020_spec.md` v1 (SHA-256 48e6fecc…), plus addendum 1 `research/phase5/H020_spec_addendum_1.md` (c653513c…), written and pinned **before** any real computation.

## Verdict: **NO CHART SCORE QUALIFIED FOR PORTFOLIO RESEARCH**

> The frozen structured chart-analysis rubric did not demonstrate predictive information large enough and robust enough to qualify for portfolio research.

All five gates fail:

| Measure | Result | Requirement |
|---|---|---|
| Rank IC | +0.003 (t_ic = 0.27) | t_ic > c_ic = 2.33 |
| Incremental coefficient | +0.002 (t_inc = 0.22) | t_inc > c_inc = 2.26 |
| High-score group (11–20) | −0.38%/yr vs the cross-sectional average | ≥ +3.0%/yr |
| Group order | Spearman −0.3 | ≥ 0.90 |

The strongest score group (16–20) earned −1.3%/yr vs the average.

The 13-week result (NON-GATING) and the sector-adjusted result (NON-GATING) say the same. This does **not** show that chart analysis does not work, nor that no 1–2% edge exists: the design could not detect edges that small (P5-CP2 §30).

---

## 1. Execution summary

| Step | What happened |
|---|---|
| 1. E987-01 canary (X987) | 12 / 14 checks pass. The two failures were assessed as not fidelity defects (§2) |
| 2. Response accounting | Total shareholder return verified (§4) |
| 3. Sector availability | Point-in-time SEC SIC → FF12 available; NON-GATING diagnostic pre-registered (§5) |
| 4. E021-01..05 null (S021) | 5,000 / 5,000 worlds. Two runs needed a results **recovery** of the same backtest (D077, §6); no world was re-run |
| 5. c_ic, c_inc | 2.328878115 and 2.264744985 |
| 6. Pins | Commit **55bf663**: c values, null result, per-world table, chart-panel hash |
| 7. Clean tree | Verified. The E021-06 config (commit 0995ed9) references the pins; chart, stats and host code are byte-identical to the null runs |
| 8. E021-06 | ONE real evaluation (QC backtest 539d5e2f, commit 0995ed9); the chart panel equals the pinned one |
| 9. This checkpoint | — |
| 10. STOP | — |

**Programme totals (registry):**
- 18 hypotheses tested (H001–H020 with experiments);
- 57 strategy / infrastructure IDs, of which 19 are strategies;
- 310 original experiment runs (137 research runs).

**H020 runs:**
- E987-01;
- E021-01 to E021-05;
- E021-06.

## 2. E987-01 result

- **Result:** 12 / 14 checks pass (`research/phase5/H020_canary_report.json`; assessment `research/phase5/H020_canary_assessment.md`).
- **Passes:**
  - calendar;
  - weekly universe on all 417 week-ends;
  - decision dates;
  - horizon ends;
  - history rule;
  - coverage;
  - independent point-in-time recomputation (120 / 120 identical);
  - total-return recomputation (238 / 238, max difference 7e-16);
  - dividends;
  - placebo;
  - null determinism.
- **Failure 1 — 2010 industry coverage of 68.7%:** a data-coverage fact. The dated SIC starts at a company's first filing in the table. It affects only the non-gating sector diagnostic.
- **Failure 2 — a planted-signal null-world |t| < 4 criterion:** the criterion was mis-specified. Real returns share common factors, so one null world of a score that is a disguised return is ~5× wider than N(0,1). Synthetic proof: `research/phase5/h020_planted_factor_check.py`. The planted signal itself was recovered perfectly (IC = 1 on all 412 dates).
- **Consequence:** nothing in the implementation was changed.

## 3. Point-in-time universe fidelity

- **Universe:** the harness eligibility of data v1:
  - US common stock;
  - point-in-time market cap ≥ $2B;
  - ≥ $5;
  - ADV20 ≥ $5M;
  - SEC correction layer.
  It is recorded at the last session of each ISO week; all 417 research week-ends are present, with none extra.
- **Bars:** 1,972 stocks; split-adjusted chart bars built from RAW × the split feed.
- **Timing:** no history row after 2017-12-29; the snapshot uses only bars up to t, confirmed by the independent recomputation from a fresh history ending at t.
- **Exclusions over 441,233 eligible stock-weeks:**

  | Reason | Stock-weeks |
  |---|---|
  | Fewer than 504 bars | 20,517 |
  | No bar at t | 77 |
  | No response | 87 |
  | No momentum | 3 |

  420,636 stock-weeks were evaluated.

## 4. Response-return accounting confirmation

**Confirmed:** the 4-week and 13-week responses are total shareholder return.
- **Start:** the open of t+1.
- **End:** the close of t+20 (or t+65).
- **Includes:**
  - price return;
  - cash dividends (QuantConnect dividend feed, reinvested at the reference price);
  - splits and reverse splits (split feed);
  - other price-factor events carried in the dividend feed.
- **Delisting:** a delisted stock is valued at its last real close (1,153 four-week windows ended in a delisting).

**Evidence:**
- An independent recomputation from RAW prices plus the event lists agrees to 7e-16.
- In all 86,571 four-week windows with an ex-date, TSR ≥ price return (mean +0.76%).

**The chart is unchanged:** split-adjusted, not dividend-adjusted.

## 5. Sector-data availability decision

- **Available:** a trustworthy point-in-time industry classification exists — the SEC SIC at filing (data v1), mapped to FF12.
- **Coverage:** 69% of evaluation observations in 2010, 94–98% in 2011–2017; 93% mean.
- **Use:** the NON-GATING SECTOR DIAGNOSTIC was pre-registered (addendum A2) before the null. It is the frozen G5 regression plus FF12 dummies, with 'Unclassified' as its own group.
- **Not used:** sector was not used in any score, screen, threshold or rule.

## 6. Null worlds completed

**5,000 / 5,000** (seeds 1–5,000; five batches of 1,000).

| Run | Backtest | Seeds | Note |
|---|---|---|---|
| E021-01 | 9d80b52b | 1–1,000 | The original was `integrity_failed`: the runner downloaded results when QuantConnect reported completed = True but status "In Progress…". The same backtest was **recovered** once final (D077). Runner fixed (D156) |
| E021-02 | 97fd22df | 1,001–2,000 | The runner was lost in a container restart; the same backtest was **recovered** once complete (D077) |
| E021-03 | 4699501a | 2,001–3,000 | Completed |
| E021-04 | 6c4c9e5d | 3,001–4,000 | Completed |
| E021-05 | eb46a966 | 4,001–5,000 | Completed |

All five runs produced the **identical chart panel** (aa5d3c51…), equal to the canary's, and an identical response panel (bd0b6792…).

## 7. Null failures / retries

**0 failed worlds, 0 re-run worlds.** Two download recoveries of already-computed backtests.

## 8. c_ic

**2.328878115.**

## 9. c_inc

**2.264744985.**

These are the 50th-largest of the 5,000 null t_ic and t_inc. Null t_ic: mean −0.41, sd 1.17. Null t_inc: mean −0.48, sd 1.17. Their correlation is 0.98.

## 10. Threshold commit hash

**55bf6634150b6cc8b068177e73a5c3b6a5d6c3ac.**

## 11. Null-output hashes

| Item | SHA-256 |
|---|---|
| `research/phase5/H020_null_result.json` | 4b26be842ce4… |
| `research/phase5/H020_null_worlds.csv` | fa936246d1af… |
| Chart panel | aa5d3c51fb12… |
| Response panel | bd0b67926352… |

## 12. Specification hash

- Spec 48e6feccbdb7…;
- addendum c653513cb9ec…;
- code: `qr_chart` c9dc5b18…, `qr_h020_stats` 426d3721…, `qr_chart_render` 3bcf1207…;
- host code hashes are recorded in the null result.

## 13. Confirmation thresholds pinned before the real run

**Confirmed.**
- Commit 55bf663 (pins) is an ancestor of 0995ed9, the clean commit E021-06 ran from.
- The run's config carries the pins, and `H020_eval.py real` refuses to run if they differ.
- The host refuses to compute if the chart panel differs from the pinned one; it was equal.

## 14. Research date range

Decisions from 2010-01-08 to 2017-11-24. Responses end at the latest on 2017-12-22 (4-week) and 2017-12-26 (13-week).

## 15. Number of weekly decisions

**412** primary (4-week); 403 for the 13-week diagnostic.

## 16. Eligible-stock counts over time

- **Per decision:** evaluated stocks min 727, max 1,258, mean 1,021.
- **Mean by year:**

  | Year | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
  |---|---|---|---|---|---|---|---|---|
  | Mean evaluated | 792 | 884 | 892 | 1,014 | 1,117 | 1,145 | 1,121 | 1,217 |

## 17. Score distribution

**Pooled distribution** (420,636 stock-weeks):

| Q | −1 (disqualified) | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n | 141,390 | 7 | 59 | 299 | 1,810 | 6,402 | 17,853 | 33,322 | 47,681 | 47,516 | 47,916 | 39,614 | 18,828 | 9,333 | 5,142 | 2,604 | 750 | 105 | 5 |

No stock-week scored 0–2.

**Groups (share of stock-weeks):**

| Group | Scores | Share |
|---|---|---|
| G0 | disqualified | 33.6% |
| G1 | 0–5 | **0.09%** |
| G2 | 6–10 | 25.5% |
| G3 | 11–15 | 38.8% |
| G4 | 16–20 | **2.0%** |

**By year (G0 / G1 / G2 / G3 / G4, % of stock-weeks):**

| Year | G0 | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|
| 2010 | 30 | 0.1 | 25 | 43 | 2.4 |
| 2011 | 39 | 0.1 | 25 | 35 | 1.8 |
| 2012 | 33 | 0.2 | 27 | 39 | 1.9 |
| 2013 | 19 | 0.1 | 29 | 49 | 2.9 |
| 2014 | 31 | 0.1 | 25 | 42 | 2.3 |
| 2015 | 45 | 0.1 | 22 | 31 | 1.5 |
| 2016 | 40 | 0.1 | 27 | 32 | 1.5 |
| 2017 | 31 | 0.1 | 25 | 42 | 2.2 |

**Sparse groups:**
- **G1 is practically empty:** 0.9 stocks per date on average, empty on 226 of 412 dates. Its mean return rests on about one stock and is noise.
- **G4 is sparse:** median 18 stocks per date, empty on 9 dates.

The definition of High was **not** changed after seeing this.

## 18. Group sizes

**Mean stocks per date:** G0 343, G1 0.9, G2 260, G3 396, G4 21.

| Group | G0 | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|
| Minimum per date | 63 | 0 | 49 | 15 | 0 |
| Median per date | 336 | 0 | 257 | 420 | 18 |

Per-date sizes for every decision are in `research/phase5/H020_real_result.json` (`diagnostics.score_distribution.group_sizes_by_date`).

## 19. Disqualifier frequencies

| Disqualifier | Share of stock-weeks |
|---|---|
| D1 weekly close < MA40w | 31.2% |
| D2 weekly downtrend | 9.7% |
| D3 > 1.25 × MA50 | 0.5% |
| D4 no support | 3.2% |
| D5 ≥ 15% gap | 0.2% |

**Any disqualifier:** 33.6% of stock-weeks. Number of disqualifiers per stock-week:

| Disqualifiers | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| Stock-weeks | 279,246 | 98,363 | 38,738 | 4,233 | 56 | 0 |

## 20. 20-condition frequencies

Share of all evaluated stock-weeks; in brackets, among non-disqualified stock-weeks. Descriptive only.

| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **W** | W1 67% (94) | W2 72% (90) | W3 67% (90) | W4 58% (78) | W5 87% (98) |
| **B** | B1 78% (72) | B2 64% (67) | B3 17% (14) | B4 22% (21) | B5 13% (12) |
| **T** | T1 3.8% (5.6) | T2 3.4% (5.1) | T3 1.2% (1.7) | T4 3.4% (5.0) | T5 61% (76) |
| **R** | R1 91% (94) | R2 85% (87) | R3 84% (80) | R4 38% (45) | R5 78% (88) |

**Reading:**
- The **trigger** conditions are rare: a fresh breakout occurs in 3.8% of stock-weeks.
- **Contraction** (B3–B5) occurs in 13–22%.
- The **weekly-trend** and **risk** conditions are common.

## 21. G0–G4 4-week results

Mean demeaned 4-week total shareholder return, annualised (× 13); "weeks" = number of decisions with that group present.

| Group | Return vs the average (%/yr) | Weeks |
|---|---|---|
| G0 disqualified | −1.18 | 412 |
| G1 0–5 | +5.93 (≈ 1 stock per date; noise) | 186 |
| G2 6–10 | −0.58 | 412 |
| G3 11–15 | −0.32 | 412 |
| G4 16–20 | **−1.27** | 403 |

## 22. High-group excess over average

**High (G3 + G4) = −0.38%/yr.** The requirement is ≥ +3.0%/yr.

## 23. High-minus-Low result

Low (G0 + G1) = −1.16%/yr, so **High − Low = +0.78%/yr**. High > Low holds, but the economic floor fails.

## 24. Rank IC

- **Mean:** +0.0029 per date (NW se 0.0109).
- **Mean by year:**

  | Year | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
  |---|---|---|---|---|---|---|---|---|
  | Mean IC | −0.008 | +0.011 | −0.009 | +0.019 | +0.016 | +0.038 | −0.051 | +0.007 |

## 25. t_ic

- **t_ic = 0.27** against c_ic = 2.33.
- Reporting-only p vs the null: 0.28.

## 26. Monotonicity result

**Spearman(group 0–4, group mean) = −0.30**, against ≥ 0.90. **Fail.** The order is G1 > G3 > G2 > G0 > G4, so the top group is the worst.

## 27. Stability result

- **Halves:** mean IC in the first half +0.0041, second half +0.0018. Both positive.
- **Concentration:** the largest 2-year block's share of the IC sum is 2.35, against ≤ 0.5. The total IC sum is tiny, so 2014–15 alone exceeds it.
- **G4 fails.**

## 28. Incremental regression result

- **Model:** the frozen Fama-MacBeth regression on each date, rank(demeaned y) on rank(Q), rank(12-1 momentum) and the trend dummy, with an intercept.
- **Result:** mean coefficient on rank(Q) = **+0.0019** (NW se 0.0086).

## 29. t_inc

- **t_inc = 0.22** against c_inc = 2.26.
- Reporting-only p vs the null: 0.28.

## 30. Momentum / trend-control result

- **Score vs the baselines:** the score correlates with momentum (mean per-date Spearman 0.36, sd 0.14) and strongly with trend (0.75). D1 is the complement of the trend baseline.
- **Not just momentum:** the score is not merely momentum, but it carries **no** detectable information beyond momentum and trend (t_inc 0.22).
- **Raw score either:** neither the raw nor the incremental relationship is detectable.

## 31. PIT sector diagnostic — NON-GATING SECTOR DIAGNOSTIC

- **Model:** the G5 regression plus FF12 industry dummies (point-in-time SEC SIC).
- **Result:** coefficient on rank(Q) = +0.0014 (NW se 0.0070), **t = 0.20**.
- **Coverage:** classified share 93% mean, 49% minimum (early 2010).
- **Effect of the controls:** sector controls change nothing. It is not a gate, and it was not chosen after the primary result was seen.

## 32. G1–G5 pass / fail

| Gate | Rule | Result | Pass |
|---|---|---|---|
| G1 economic | High ≥ +3.0%/yr over the average **and** High > Low | High −0.38%/yr; High − Low +0.78%/yr | **FAIL** |
| G2 monotonic | Spearman ≥ 0.90 | −0.30 | **FAIL** |
| G3 significant | t_ic > c_ic | 0.27 vs 2.33 | **FAIL** |
| G4 stable | Both halves > 0 **and** no 2-year block > 50% | halves +0.004 / +0.002; block share 2.35 | **FAIL** |
| G5 incremental | t_inc > c_inc **and** inc > 0 | 0.22 vs 2.26 | **FAIL** |

The gates were recomputed locally from the published summary with the pinned c values; they are identical to the host's.

## 33. Overall qualification result

**NOT QUALIFIED.** 0 of 5 gates pass. For reference, 0 of the 5,000 null worlds passed all five gates either.

## 34. 13-week diagnostic — NON-GATING DIAGNOSTIC

This is reported only. It cannot rescue, veto, change promotion or motivate tuning.

| Measure | Value |
|---|---|
| IC | 0.0052 (t 0.33) |
| Incremental | 0.019 (t 1.80) |
| High | +0.05%/yr |
| Low | −0.85%/yr |
| Monotonicity | 0.2 |
| Halves | −0.003 / +0.014 |

**Group means (%/yr):**

| G0 | G1 | G2 | G3 | G4 |
|---|---|---|---|---|
| −0.86 | +3.61 | −1.33 | +0.05 | +0.56 |

It is no different in substance from the 4-week result.

## 35. Score-vs-momentum correlation

Mean per-date Spearman(Q, 12-1 momentum) = **0.36** (sd 0.14).

## 36. Score-vs-trend relationship

**Correlations:**
- Spearman(Q, trend dummy) = 0.75.
- Among stocks above the 40-week MA, 58% are High; among stocks below it, 0.002%, because D1 disqualifies them.
- The mean score of non-disqualified stocks is 11.2 above the MA and 12.0 below it (very few observations below).

**The raw 0–20 score vs its category counts** (Spearman, descriptive):

| Category | W | B | T | R |
|---|---|---|---|---|
| Spearman | 0.66 | 0.47 | 0.58 | 0.52 |

## 37. Confirmation: no component mining or tuning occurred

**Confirmed.**
- No per-condition return test was computed or looked at.
- No condition, weight, threshold, group or cut-off was changed.
- The condition frequencies above are descriptive only.

## 38. Confirmation: no rerun with alternate parameters

**Confirmed.** One real evaluation (E021-06) with the frozen parameters. No other real evaluation exists.

## 39. Confirmation: 2018–2021 untouched

**Confirmed.** Every run ends on 2017-12-31 (enforced by config validation and the host). There is no history after 2017-12-29.

## 40. Confirmation: Holdout untouched

**Confirmed.** 2022-01-01 → 2026-08-31 is never requested; `HOLDOUT_UNLOCK.md` is unchanged.

## 41. Confirmation: no portfolio built

**Confirmed.** No stock count, sizing, exits, stops, commissions, terminal wealth or SPY comparison.

## 42. Confirmation: no AI / data purchase

**Confirmed.**
- No LLM or vision model was used in any score.
- No chart image of QuantConnect data was made or sent anywhere; the renderer was not even uploaded.
- No data was purchased.

**Cost:** QuantConnect node time ≈ 4.8 hours in total (canary 0.56 h, five null runs 3.65 h, real run 0.63 h; plus a 6-minute unregistered scratch plumbing run on 60 stocks), within the existing $24/month subscription.

## 43. Interpretation under the frozen wording

> **The frozen structured chart-analysis rubric did not demonstrate predictive information large enough and robust enough to qualify for portfolio research.**

**What this does not mean:**
- It does **not** mean "chart analysis does not work".
- It does **not** mean "no 1–2% edge exists". The power study (P5-CP2 §30) put the realistic 50% detectable edge at ≈ 3–5%/yr for the High group, so smaller edges were not testable by design.

**What can be said:**
- In ≥ $2B US stocks over 2010–2017, at weekly decisions and 4-week horizons, higher scores on this deterministic checklist did not go with higher total shareholder returns.
- The top group (16–20 points) did slightly worse than average.
- Controlling for momentum, trend and sector does not change that.

## 44. Exact next action requiring owner approval

The owner decides on H020 after reviewing this report. My recommendation is to **close H020 as Rejected: No Production Candidate Found** (H020 preserved exactly as tested).

This is the third consecutive technical stock-selection programme without a qualifying signal (H018 systematic search, H019 cross-sectional signals, H020 chart structure; H002 / H003 / H008 failed earlier). Any further technical stock-selection research would need a genuinely different source of information, as a new phase with its own pre-registration.

**Not done and not proposed now:**
- no portfolio;
- no 2018–2021 data;
- no Holdout;
- no threshold or rule changes;
- no new indicators;
- no use of the 13-week diagnostic;
- no new technical hypothesis.

## 45. Final verdict

# NO CHART SCORE QUALIFIED FOR PORTFOLIO RESEARCH

**STOP.** Awaiting the owner's explicit decision after reviewing H020.

---

### Files

| File | Content |
|---|---|
| `research/phase5/H020_real_result.json` | Real summary, gates, per-date series, diagnostics, 13-week |
| `research/phase5/H020_null_result.json` | Null distributions, c values, hashes |
| `research/phase5/H020_null_worlds.csv` | Per-world null statistics |
| `research/phase5/H020_canary_report.json` | Canary checks |
| `research/phase5/H020_canary_assessment.md` | Assessment of the two canary failures |
| `experiments/E987-01`, `E021-01..06` | Configs, run records, recoveries |
| `strategies/X987_h020_chart`, `S021_h020_chart` | Host (byte-identical) |
| `src/qresearch/lean/qr_h020_panel.py`, `qr_h020_diag.py` | Real-run plumbing and descriptives |
