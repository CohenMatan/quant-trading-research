# P5-CP2 — H020 Structured Chart Score Implementation and Validation Readiness (STOP)

- **Date:** 2026-10-05.
- **Owner authorisation:** "H020 — Authorise Structured Chart Analysis Implementation and Canary Only" (D151; summary in `docs/owner/2026-10-05_h020_implementation_authorisation.md`).
- **Scope:** implementation, reproducibility, leakage testing and canary validation only, all on **synthetic** data.
- **Frozen candidate:** `research/phase5/H020_spec.md` v1. SHA-256 pinned in `qresearch.p5h020` with every code constant and the synthetic scenario table.

## Short answer

1. **The deterministic H020 pipeline is built and tested.** Daily + Weekly reconstruction, confirmed swing points, HH / HL / LH / LL structure, anchored support / resistance zones, support and resistance trendlines with permanent invalidation, one base framework, one breakout architecture, volume in three explicit roles, one volatility-contraction measure, entry risk, the 4 × 5 checklist (0–20, no weights) and 5 hard disqualifiers.
2. **Every leakage canary passes,** including byte-identical Daily and Weekly PNGs whatever happens after t, and the twelve synthetic scenarios (A–J plus two controls) reproduce their frozen expectations exactly. Results are byte-reproducible across runs and processes.
3. **Two statistical design defects were found and fixed on synthetic data before any real data** (§27):
   - **Stratified null tether.** Stratifying the null by momentum quintile made it too narrow: 6% false significance at a nominal 1%. The frozen null is an unstratified identity tether, which is calibrated.
   - **Single critical value.** A single max(t_ic, t_inc) critical value would have crippled the incremental test. Each statistic now has its own critical value, combined as an intersection-union test.
4. **Power:** {{POWER_SHORT}}
5. **Verdict: {{VERDICT}}** — subject to your explicit approval. Nothing real has been computed:
   - no real chart scored;
   - no future return by score;
   - no null on the research universe;
   - no QuantConnect run;
   - no 2018–2021 data;
   - the Holdout is locked;
   - no AI;
   - no portfolio.

---

## 1. No real research run

| Item | Done? |
|---|---|
| Real chart scores 2010–2017 | **No** |
| Future returns by score / any backtest | **No** |
| Null calibration on the real universe | **No** |
| QuantConnect backtest of any kind for H020 | **No** (nothing uploaded; `experiments/INDEX.csv` has no E987 / E021 row — tested) |
| 2018–2021 / Holdout | **No** / locked |
| LLM or vision model; QuantConnect or OHLCV-derived images sent anywhere | **No** |
| Thresholds inspected against historical winners | **No** (no real stock was charted) |

Everything below runs on **synthetic** bars (`research/phase5/h020_fixtures.py`, `p5_synth.py`) or synthetic latent panels (`h020_synth_panel.py`).

## 2. Hypothesis

**H020.** At a weekly decision close, stocks whose point-in-time chart shows a classical long setup score high on a fixed, deterministic 20-point checklist. That setup has four parts:
- a healthy weekly trend and structure;
- a mature base;
- a fresh, confirmed breakout;
- low, well-defined entry risk.

**Claim:** these stocks earn higher 4-week returns than low-scoring and disqualified stocks, **beyond** 12-1 momentum and "price above the 40-week MA".

It is a signal-level test, not a strategy. **No LLM or vision model is part of H020.**

## 3. Checklist (4 categories × 5 binary conditions)

| Category | Timeframe | Role |
|---|---|---|
| W — Weekly trend & structure | Weekly (W5: daily highs over 52 weeks) | Is the stock worth considering? |
| B — Base quality | Weekly base; Daily contraction | Is the setup mature? |
| T — Trigger / breakout | Daily | Is there a fresh, confirmed trigger? |
| R — Entry risk & support | Daily | Is risk small and defined? |

## 4. The 20 conditions

Exact formulas, timeframes, histories, thresholds and sources are in `research/phase5/H020_threshold_provenance.md`. The full algorithms are in spec §5–14.

| # | Condition | Threshold |
|---|---|---|
| W1 | weekly close > MA30w | — |
| W2 | MA40w > MA40w 4 weeks ago | rising |
| W3 | MA10w > MA30w | — |
| W4 | weekly structure ∈ {strong_uptrend, uptrend} | swings k = 3 weeks, 1 ATR |
| W5 | close ≥ 0.75 × 52-week high | 25% |
| B1 | valid base (anchor = confirmed weekly swing high that is a 26-week high; length 7–65 weeks) | 7–65 w |
| B2 | base depth ≤ 33% | 0.33 |
| B3 | mean TR (t−14…t−5) / mean TR (t−64…t−15) ≤ 0.80 | 0.80 |
| B4 | mean volume, same windows ≤ 0.80 | 0.80 |
| B5 | ≥ 2 pullbacks inside the base, strictly shrinking | — |
| T1 | close > pivot P; run above P started ≤ 4 sessions ago, after the base start | 5 sessions |
| T2 | close ≤ 1.05 × P | 5% |
| T3 | first breakout-day volume ≥ 1.40 × 50-session mean | +40% |
| T4 | first breakout-day close location ≥ 0.5 | 0.5 |
| T5 | close > MA50 | — |
| R1 | risk = 1 − support / close ≤ 8% | 8% |
| R2 | risk ≤ 2.5 × ATR(20)% | 2.5 ATR |
| R3 | (close / MA20 − 1) / ATR% ≤ 2 | 2 ATR |
| R4 | ≤ 4 distribution days (≤ −0.2% on higher volume) in 25 sessions | 4 |
| R5 | daily structure ∈ {strong_uptrend, uptrend, range} | swings k = 5, 1 ATR |

## 5. Disqualifiers (frozen, each with a reason)

| # | Rule | Reason |
|---|---|---|
| D1 | weekly close < MA40w | long-term decline: not a long setup in any framework |
| D2 | weekly structure = downtrend (LH + LL) | confirmed lower highs and lower lows |
| D3 | close > 1.25 × MA50 | late, extended entry |
| D4 | no support below the close | entry risk undefined |
| D5 | an open ≤ 0.85 × the prior close in the last 10 sessions | event shock (price gap only; no news used) |

A disqualified stock gets Q = −1 (group G0); its score is never offset.

## 6. Threshold provenance

The full table is `research/phase5/H020_threshold_provenance.md`. It has one row per condition and disqualifier, plus the universe rule and the engineering conventions. **Practitioner rules are hypotheses / frameworks, not proof of predictive alpha.**

| Type | Rules |
|---|---|
| A practitioner explicit | W5 (Minervini, within 25% of the 52-week high), T2 (O'Neil, 5% above the pivot), T5 (Minervini, above the 50-day), B1 range 7–65 weeks and B2 33% (O'Neil cup-with-handle), T3 +40% (lower end of O'Neil's 40–50%), W1 30-week MA length (Weinstein) |
| B derived | W2 (Minervini's 200-day rising ≥ 1 month → 40 weeks over 4 weeks), W3 (50-day > 150-day → 10w > 30w), R1 (O'Neil 7–8% loss rule applied to support), R4 (IBD index rule applied to a stock), D1 (Minervini 200-day → 40-week), T3's 50-day average, B5's "≥ 2" (lower end of "typically 2–4") |
| C academic | concept only: nearness to the 52-week high (George & Hwang 2004) for W5. Never a threshold |
| D engineering | swing k = 5 / 3, prominence 1 ATR, tolerance 0.5 ATR, ATR 20 / 10, scan windows, zone and trendline rules, 504-session minimum history, 756-session window |
| E our design | W4 / R5 / D2 state sets, B1 anchor rule, B3 / B4 thresholds and windows, T1 freshness and pivot = anchor high, T4, R2, R3, D3, D4, D5, the support set, score groups, economic floor |

Verification: secondary summaries of the books (2026-10-05); the primary texts were not accessed. Nothing says "from Weinstein / O'Neil / Minervini" unless the cited summary gives that number for that concept.

## 7. Weekly bars

- **Construction:** ISO-week bars from the stock's **own** sessions ≤ t:
  - open = first open;
  - high = max;
  - low = min;
  - close = last close;
  - volume = sum.
- **Decision timing:** t is the last session of the ISO week, so the decision week's bar is complete.
- **Tested:**
  - at a mid-week t, the current-week bar contains only sessions ≤ t;
  - its full-week counterpart differs, which is the negative control.

## 8. Daily input

- **Prices:** split-adjusted, not dividend-adjusted, built as RAW × QuantConnect's split feed (the H019 lesson D148). Volume = RAW ÷ split factors.
- **Snapshot window:** the snapshot reads the last 756 sessions. With the full history it gives exactly the same facts (tested on 1,100-bar series).
- **Minimum history:** 504 sessions; with fewer, the snapshot raises an error, so the stock is excluded, never padded.

## 9. Swing points

- **Swing high at i:**
  - h[i] > max of the 5 bars before (strict);
  - and ≥ the max of the 5 bars after (equal highs → the left-most);
  - and prominence h[i] − min(l[i−10…i]) ≥ 1 ATR(20).
  - Lows are the mirror image. A bar that qualifies as both counts as a high.
- **Weekly:** k = 3 with ATR(10w).
- **Confirmation** at i + k exactly (delay k).
- **Missing sessions:** none are synthesised.
- **Spacing:** implicit.
- **Prominence window:** local (2k bars), so the swing set does not depend on where history starts.
- **Tests:**
  - absent at t = i + k − 1, present at t = i + k;
  - prefix property: no repainting;
  - identical after dropping old history.

## 10. HH / HL structure

- **Labels:**
  - HH / LH / EH for the last two swing highs, and HL / LL / EL for the lows, with a tolerance of 0.5 ATR;
  - "equal" is within the tolerance.
- **State** (spec §6):
  - break down below L2 → downtrend if LH + LL, otherwise deteriorating;
  - break up above H2 → strong_uptrend if HL, otherwise uptrend;
  - otherwise HH + HL → strong_uptrend, LH + LL → downtrend, HH + EL or EH + HL → uptrend, else range;
  - fewer than 2 + 2 swings → undefined.
- **P5-CP1 regression kept as a test:** a close above H2 after a lower high is never "downtrend".

## 11. Support / resistance

- **Members:** confirmed swing highs and lows (roles flip). Daily: last 252 sessions. Weekly: last 104 weeks.
- **Anchored clustering:** a pivot joins a zone if it lies within 2·tol of the zone's lowest member. Zone = members ± tol. ≥ 2 touches. **No chaining** (a price ladder test).
- **Nearest resistance** = the nearest zone fully above the close; **nearest support** = the nearest zone fully below it.

## 12. Trendlines

- **Support line:** two rising confirmed swing lows. **Resistance line:** two falling confirmed swing highs.
- **Anchors:** ≥ 10 sessions apart, inside 252 sessions.
- **Selection:** most touches → most recent second anchor → earliest first anchor.
- **Permanent invalidation:** any close beyond the line by more than tol after the first anchor kills it. A later recovery never revives it (tested).
- **Anchors after t are impossible:** anchors are confirmed pivots, so ≤ t − 5 (tested).

## 13. Base

One framework (Weekly):
- **Anchor:** the most recent confirmed weekly swing high that is the highest high of the prior 26 weeks.
- **Validity:** length 7–65 weeks.
- **Depth:** from the lowest weekly low since the anchor.
- **Pullbacks:** swing high → next swing low.
- **Contracting:** ≥ 2 pullbacks, strictly shrinking.
- **Pivot:** P = the anchor high.
- **Test:** the base length at t counts only weeks ≤ t, and the same anchor ages week by week.

## 14. Breakout

One architecture:
- **Fresh breakout:**
  - the close at t is above P;
  - the run of closes above P started ≤ 4 sessions ago;
  - and after the base start.
- **Measured at t:**
  - extension;
  - first-day close location;
  - first-day volume / 50-session mean.
- **Test:** a breakout that fails after t is unchanged at t, and gone at t + 10.

## 15. Volume

Volume enters in exactly three roles and nowhere else:
- **B4:** dry-up in the base;
- **T3:** breakout confirmation;
- **R4:** distribution days.

A future-volume-only perturbation changes nothing (tested). The two controlled fixture pairs isolate B4 (I vs I-control) and T3 (J vs J-control).

## 16. Volatility

One contraction measure (B3): mean true range of t−14 … t−5 over that of t−64 … t−15, ≤ 0.80. The last 4 sessions are excluded so the trigger day does not cancel the contraction.

## 17. Extension / risk

- **Extension:**
  - R3: (close / MA20 − 1) / ATR% ≤ 2;
  - D3: close > 1.25 × MA50 disqualifies.
- **Support** = the highest of:
  - the nearest support-zone top;
  - the support trendline (if below the close);
  - P (if broken upward);
  - the last confirmed swing low below the close.
- **Risk** = 1 − support / close. R1: ≤ 8%. R2: ≤ 2.5 ATR%. D4: no support.

## 18. Relative strength role

**Excluded** from the score; it is the **control** instead.
- Cross-sectional RS is Baseline A (12-1 momentum). Including it would make the score partly the baseline it must beat.
- W5 measures the stock's distance to its own high, not RS versus the market.
- **Diagnostic:** the per-date Spearman(score, momentum).

## 19. Scoring formula

- **Score** = number of true conditions, 0–20, **1 point each, no weights.**
- **Nesting:** B2–B5 require a valid base (B1); T2–T4 require a fresh breakout (T1).
- **Q** = −1 if any disqualifier, otherwise the score.

## 20. Score groups (pre-declared)

| Group | Members |
|---|---|
| G0 | Disqualified |
| G1 | 0–5 |
| G2 | 6–10 |
| G3 | 11–15 |
| G4 | 16–20 |

**High = G3 + G4; Low = G0 + G1.**

## 21. Universe

At each weekly decision close, a stock is eligible if all of these hold:
- US common stock;
- point-in-time market cap ≥ $2B;
- close ≥ $5;
- ADV20 ≥ $5M;
- SEC correction layer on (data infrastructure v1, as H019);
- a bar at t;
- **≥ 504 sessions of history** — technically necessary, because the 40-week MA and its 4-week slope, the 52-week high and the weekly swing scan must exist.

**No technical pre-screen.**

## 22. Frequency

- **Weekly:** the last session of each ISO week, about 410 primary decisions in 2010–2017.
- **Timing:** the score uses the close at t; the response starts at the next open.

## 23. 4-week horizon (primary)

- **Response:** y = total return from the open of t+1 to the close of t+20. A delisted stock is valued at its last real close.
- **Window:** the last decision's t+20 is on or before 2017-12-29.
- **Inference:** responses overlap by 3 weeks, so Newey-West uses lag 3; the null absorbs any residual misspecification.

## 24. 13-week diagnostic

- **Response:** open t+1 → close t+65 (NW lag 12).
- **When:** computed in the same real run and reported only. **Never a gate. Not evaluated now.**

## 25. Baselines

| Baseline | Definition |
|---|---|
| A — medium-term momentum | TR close t−21 / TR close t−252 − 1 |
| B — price above a long MA | 1{weekly close > MA40w} |

Both stay with the stock in every null world.

**Note:** B is the exact complement of D1, so the incremental test necessarily measures the score beyond "above the 40-week MA".

## 26. Incremental test (one method)

- **Regression:** a Fama-MacBeth cross-sectional OLS on each date, rank(demeaned y) on [rank(Q), rank(momentum), trend dummy] with an intercept.
- **Statistic:** inc = the mean slope on rank(Q); t_inc = its Newey-West t (lag 3).
- **Gate G5:** t_inc > c_inc and inc > 0.

## 27. Null

**Design:**
- **Permutation:** an identity-tethered within-date permutation of the chart side (Q, G).
- **Partners:** each stock receives another stock's scores and keeps that partner while both stay in the cross-section. Entrants and orphans are re-matched at random. **No self-matches.**
- **Preserved:**
  - dates and cross-sections;
  - every stock's returns, momentum and trend;
  - the exact score distribution and group counts on every date;
  - score persistence (a null score history is a real stock's history);
  - the overlapping-return structure.
- **Broken:** only the link between a stock's score and its own return.
- **Full procedure:** every world re-runs it all — IC, groups, the incremental regression, monotonicity, stability and the gates.
- **Worlds:** R = 5,000.
- **Critical values:** c_ic and c_inc = the 50th-largest null t_ic and t_inc (α = 1% each). Promotion needs both: an **intersection-union test**, so the false-promotion probability is ≤ 1%.

**Two defects found and fixed on synthetic data (D152), before any real data:**

| Problem | Evidence (`research/phase5/h020_null_design_check.json`, 417 dates × 300 stocks, 300 null worlds, 120 no-edge panels) | Fix |
|---|---|---|
| H019's tether + momentum-quintile × trend strata: a stock changing stratum alone is re-matched **to itself**, and self-matches persist | 31% of receivers self-matched; a planted chart edge leaked into the null | `ChartTether`: no self-matching (swap / splice) |
| Even without self-matches, dynamic strata break partners almost weekly | Week-to-week persistence 0.56; null sd of t_ic 0.87 vs 1.14 across real no-edge panels; **size 5.8% at a nominal 1%** | **Unstratified** tether: persistence 0.98, null sd 1.10 vs 1.14, size t_ic 0.8% / t_inc 2.5% at 1% (3 / 120) |
| One critical value from max(t_ic, t_inc) | If the score correlates with momentum and momentum predicts returns, the null t_ic is centred away from 0 (≈ 5 in a synthetic momentum world), so the shared critical value is dominated by t_ic and G5 becomes nearly impossible | **Per-statistic critical values, intersection-union test** |

Momentum and trend are controlled by G5's regression, not by null strata.

**Full-scale check (1,000 stocks):** {{SIZE_TEXT}}

## 28. Gates (all five required; outcome "qualified" / "not qualified")

| Gate | Rule |
|---|---|
| G1 economic | High-group mean ≥ +3.0%/yr over the cross-sectional average, and High > Low |
| G2 monotonic | Spearman(group 0–4, group mean) ≥ 0.90 |
| G3 significant | t_ic > c_ic |
| G4 stable | Mean IC > 0 in both halves; no 2-year block > 50% of the IC sum |
| G5 incremental | t_inc > c_inc and inc > 0 |

## 29. Economic floor

**+3.0%/yr** for the High group (scores 11–20, not disqualified) over the equal-weight cross-sectional average (4-week demeaned return × 13). This is the same floor as H019; it is our design (type E). Below it, a real edge would not survive costs and turnover in a weekly-rebalanced book.

## 30. Power (synthetic, mechanics changed: weekly, 4-week horizon, 0–20 score)

`research/phase5/h020_power_result.json`, from `h020_power.py`. The design is 417 weekly dates × 1,000 stocks, with latent chart quality persistence 0.85 a week, correlation 0.5 with momentum, and weekly idiosyncratic volatility 4.5%.

{{POWER_TABLE}}

## 31. Leakage results

All pass. 95 H020 tests (+1 skipped for a short fixture); `tests/test_h020_*.py`.

| Canary | Result |
|---|---|
| Future perturbation (prices ×, highs / lows, volume after t): **every** feature, swing, zone, trendline, base, breakout, condition, disqualifier, score **and both PNGs byte-identical** | Pass (3 series × 3–5 week-end t each) |
| Mid-week t | Pass |
| Future pivot confirmation: absent at i + k − 1, present at i + k; no repainting; scan-start independent | Pass |
| Future Weekly bars (partial current week; negative control) | Pass |
| Future volume only | Pass |
| Later-listed / short history (< 504 sessions raises; 504 computes) | Pass |
| Support formed after t (a double bottom after t invisible at t, visible once confirmed) | Pass |
| Levels / trendline anchors ≤ t − k | Pass |
| Trendline permanent invalidation; resistance lines need falling highs | Pass |
| Base duration uses only weeks ≤ t | Pass |
| Breakout at t unchanged by a later failure | Pass |
| Chart scaling: a future-driven axis changes the bytes (negative control); scale invariance (×3.7) | Pass |
| Sensitivity: a snapshot one bar late differs (negative control) | Pass |
| History window 756 = full history | Pass |

## 32. Reproducibility results

- **Repeated runs:** identical snapshot digests and PNG bytes for all 12 scenarios.
- **Fresh process:** identical (subprocess test).
- **Frozen table:** `h020_scenarios_expected.json` pins, per scenario:
  - all 20 conditions, 5 disqualifiers, score, categories, groups and states;
  - key features (12-significant-digit strings);
  - snapshot digest;
  - Daily / Weekly raster SHA-256.
- **Across environments:** PNG SHA-256 is recorded but checked only within one environment, because the zlib version may change compression bytes; the raster hashes are environment-independent.

## 33. Scenario table (synthetic; frozen; matched exactly)

| Scenario | Score | W/B/T/R | Group | DQ | Weekly | Daily | Shows |
|---|---|---|---|---|---|---|---|
| A clean weekly uptrend | 12 | 5/2/1/4 | G3 | – | strong_uptrend | strong_uptrend | W1–W5 all true, no DQ |
| B range / choppy | 8 | 1/3/0/4 | G0 | D1 | range | downtrend | W4 false, no trigger |
| C healthy base | 16 | 5/5/1/5 | G4 | – | uptrend | range | B1–B5 all true, no breakout yet |
| D deep / failed base | 9 | 2/2/0/5 | G2 | – | range | range | base valid, depth 46% → B2 false |
| E valid breakout | 18 | 5/5/5/3 | G4 | – | strong_uptrend | uptrend | T1–T5 all true (ext 3.2%, relvol 2.34); R2 / R3 false (breakout-day jump) |
| F false breakout | 13 | 4/4/0/5 | G3 | – | uptrend | range | closed back inside the base → T1–T4 false |
| G support break | 7 | 3/0/0/4 | G0 | D1 | deteriorating | deteriorating | R5 false, D1 |
| H overextended | 6 | 4/0/1/1 | G0 | D3, D4 | undefined | undefined | D3 (> 1.25 × MA50), R3 false |
| I contracting volume | 15 | 5/4/1/5 | G3 | – | uptrend | range | B4 true (volume ratio 0.60) |
| I-control (flat volume) | 14 | 5/3/1/5 | G3 | – | uptrend | range | **differs from I only in B4** |
| J expanding breakout volume | 18 | 5/5/5/3 | G4 | – | strong_uptrend | uptrend | T3 true (relvol 2.34) |
| J-control (quiet breakout) | 17 | 5/5/4/3 | G4 | – | strong_uptrend | uptrend | **differs from J only in T3** (relvol 1.29) |

**Notes:**
- J is the same construction as E, with the volume role made explicit.
- These are fixtures built to exercise the definitions, not evidence of any edge.

Example renders (synthetic) are in `research/phase5/h020_demo/`.

## 34. Runtime / memory (measured, synthetic, this container)

{{RUNTIME_TABLE}}

## 35. Expected real runtime (QuantConnect B2-8 node; assumptions: 2× slower than this container, ≈ 1,000 eligible stocks × ≈ 410 weeks)

{{QC_RUNTIME}}

## 36. Expected cost

- **$0 extra.** The runs use the existing QuantConnect subscription (Researcher seat plus one B2-8 node, $24/month).
- No AI calls. No data purchase.
- The research budget counts H020 as one hypothesis.

## 37. Files / hashes

{{FILES}}

## 38. Risks

1. **Overlap with failed ideas.** W1–W5 and T5 re-test trend / 52-week-high ideas that failed here (H002, H003, H018, H019); D1 equals Baseline B. G5 exists for this reason; a pass driven only by W would fail G5.
2. **Sparse High group.** Breakout conditions (T1–T4) fire rarely, so G4 may be thin on many dates. Group means then rest on few stocks (G1 and G2 use pooled weekly means; per-date group sizes are reported).
3. **Low power for small edges.** Edges of 1–3%/yr are not detectable (§30). A "not qualified" result does not prove there is no chart information.
4. **Definitions are ours where practitioners are vague** (type E: the pivot = anchor high, freshness, the support set, D3–D5). They are frozen and never tuned.
5. **QuantConnect runtime.** The score table is recomputed per null batch unless an in-project ObjectStore cache is verified in the canary (export stays blocked). The step-1 canary measures it.
6. **Vendor data defects** (H019: spin-offs, a split / price-factor inconsistency). The same RAW × feed construction is used; the canary's independent slow recomputation is the guard.
7. **Synthetic calibration ≠ real calibration.** That is why the real null (5,000 worlds on the real panel) sets c, not the synthetic study.

## 39. Future run sequence (design only; each step needs your explicit approval)

1. **E987-01 (X987):** PIT plumbing / fidelity canary. Checks:
   - in-cloud digest equality against an independent slow recomputation;
   - placebo IC ≈ 0;
   - planted IC recovered;
   - coverage counts;
   - horizon end ≤ 2017-12-29;
   - runtime.
   - No response-linked statistic of a real score is published.
2. **E021-01..05 (S021 = byte copy of X987):** null worlds 1–5,000.
3. **Freeze:** commit and pin c_ic, c_inc and the null hashes in `qresearch.p5h020`; clean tree.
4. **E021-06, once:** the real scores and the real evaluation:
   - 4-week gates G1–G4 (step 5);
   - incremental G5 (step 6);
   - 13-week diagnostic (step 7).
5. **P5-CP3 checkpoint** (step 8).
6. **STOP** (step 9).

**Interpretation rule (frozen):** if H020 fails, never tune base depth, breakout volume, support distance, weights, trendlines, cut-offs or anything else; never run a variant.

## 40. Final verdict

**{{VERDICT}}**

{{VERDICT_TEXT}}

**STOP.** Nothing further is done until your explicit approval of H020 real score validation. In particular:
- no real historical chart scores;
- no 2010–2017 predictive results;
- no null on the real universe;
- no portfolio;
- no 2018–2021 data and no Holdout;
- no threshold changes;
- no AI;
- no new indicators.
