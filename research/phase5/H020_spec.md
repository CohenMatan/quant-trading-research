# H020 — Structured chart score: frozen pre-registration (v1, FROZEN CANDIDATE)

**Status:** P5-CP2, 2026-10-05. **Implementation and synthetic canaries only.**
- The SHA-256 of this file is pinned in `qresearch.p5h020` (`tests/test_h020_spec.py`), together with every constant of the code it names.
- **Nothing has been computed on real data.** No real chart has been scored, no return linked to a score, no null run on the research universe, no 2018+ data, no Holdout.
- Any change before the owner's approval means a new version with a new hash. **Nothing may change after any real chart score is computed.**

**Code (frozen with this file):**

| File | Role |
|---|---|
| `src/qresearch/lean/qr_chart.py` | Snapshot, checklist, score |
| `src/qresearch/lean/qr_chart_render.py` | Frozen rendering, audit only |
| `src/qresearch/lean/qr_h020_stats.py` | Statistics, null, gates |

**Threshold provenance:** `research/phase5/H020_threshold_provenance.md`.

> **Practitioner rules are hypotheses / frameworks, not proof of predictive alpha.**

---

## 1. Hypothesis H020

At a weekly decision close, US stocks whose point-in-time chart shows a classical long setup score high on a fixed, deterministic 20-point checklist. The checklist covers four areas:
- a healthy weekly trend and structure;
- a mature base;
- a fresh, confirmed breakout;
- a well-defined, low entry risk.

**Claim:** these stocks earn higher returns over the next 4 weeks than lower-scoring and disqualified stocks, **and** the score carries information beyond plain medium-term momentum and "price above a long moving average".

**This is a signal-level test, not a strategy.** There is no portfolio, no costs model and no position sizing.

**No LLM or vision model is part of H020.** No chart image is an input to the score. The score is computed from numbers.

## 2. Data and point-in-time contract

| Item | Rule |
|---|---|
| Engine / data | QuantConnect Cloud LEAN, build pinned per experiment; data infrastructure v1 (`research/phase2/data_freeze_v1.json`), unchanged |
| Chart inputs (OHLCV) | Each stock's own daily bars, **split-adjusted, not dividend-adjusted** (a practitioner's price chart), built as RAW bars × QuantConnect's split feed (the H019 lesson, D148); volume = RAW volume ÷ the same split factors |
| Response / momentum | Total-return prices = RAW × split and dividend feeds (as H019) |
| Snapshot at t | `qr_chart.snapshot_at(bars, t)`: only bars 0 … t; the snapshot itself reads only the last `HIST_SESSIONS` = 756 sessions (tested: identical facts with the full history) |
| Look-back history | Pre-2010 bars are **look-back inputs only** (≥ 504 sessions needed). No pre-2010 decision or response |
| Hard limits | Every run ends on or before 2017-12-31; no 2018-01-01 → 2021-12-31 data in any form; Holdout locked |

## 3. Universe (each weekly decision close t)

Eligibility:
- harness eligibility of data v1: US common stock, point-in-time market cap ≥ $2B, close ≥ $5, ADV20 ≥ $5M, SEC correction layer on, financials included;
- **and** a bar at session t;
- **and** ≥ 504 sessions of the stock's own bars (`MIN_SESSIONS`, type D: every condition computable).

**No technical pre-screen.** Every eligible stock is scored. No present-day list is used.

## 4. Decision schedule and horizons

- **Decision t** = the last trading session of each ISO week (market calendar). The score uses the close of t.
- **Primary response (4 weeks):** y = total return from the **open of t+1** to the **close of t+20** (20 sessions; a signal at T is never filled at T's close).
  - A stock delisted inside the window is valued at its last real close.
  - A stock with no bar at t+1 has no response and is excluded on that date.
- **Primary decisions:** from the first week-end on or after 2010-01-04, up to the last week-end whose t+20 close is on or before 2017-12-29.
  - That is about 410 decisions, fixed mechanically by the session calendar.
  - Responses overlap by 3 weeks.
- **13-week diagnostic (§20):** y13 = open t+1 → close t+65, for decisions whose t+65 close is on or before 2017-12-29. **Diagnostic only; never a gate.**

## 5. Swing points (`swing_points`)

- **Confirmation:**
  - k = 5 sessions on Daily (`D_K`), k = 3 weeks on Weekly (`W_K`);
  - a swing at bar i is **confirmed only at bar i + k**;
  - the delay is exactly k bars.
- **Swing high at i:**
  - h[i] > max(h[i−k … i−1]) (strict on the left);
  - **and** h[i] ≥ max(h[i+1 … i+k]) (equal highs on the right: the left-most bar is the swing);
  - **and** h[i] − min(l[i−2k … i]) ≥ 1 × ATR_i (prominence, `PROM_ATR`, local window `PROM_WIN`·k).
  - Swing low: the mirror image.
  - A bar that qualifies as both counts as a high.
- **ATR:** simple mean of true range over 20 sessions / 10 weeks (`D_ATR`, `W_ATR`).
- **Scan:** confirmed swings in the last 300 sessions / 104 weeks (`D_SCAN`, `W_SCAN`). Bars with undefined ATR are skipped.
- **Missing sessions:** the stock's own bars are used in sequence. A trading halt is simply absent; no bars are synthesised.
- **Spacing:** implicit (a swing high needs k bars on each side).
- **No repainting:** the prominence window is local, so the swing set does not depend on where the history starts (tested).

## 6. Market structure (`classify`, `structure_state`)

- **Inputs:** the last two confirmed swing highs (H1, H2) and lows (L1, L2), in log price. Tolerance tol = 0.5 × ATR% (`TOL_ATR`).
- **Labels:**
  - HH if H2 − H1 > tol, LH if H1 − H2 > tol, otherwise EH;
  - HL / LL / EL for the lows, the same way.
- **State at the close of t:**
  - **undefined:** fewer than two swing highs or two swing lows;
  - **close < L2 − tol (break down):** downtrend if LH + LL, otherwise deteriorating;
  - **close > H2 + tol (break up):** strong_uptrend if HL, otherwise uptrend (P5-CP1 regression fixed: a break above H2 is never "downtrend");
  - **otherwise:**
    - HH + HL → strong_uptrend;
    - LH + LL → downtrend;
    - HH + EL or EH + HL → uptrend;
    - anything else → range.
- **Timeframes:** Weekly uses weekly swings and weekly ATR; Daily uses daily swings and daily ATR.

## 7. Support / resistance zones (`zones`, `nearest`)

- **Members:** confirmed swing highs **and** lows (roles flip). Daily: pivots of the last 252 sessions. Weekly: pivots of the last 104 weeks.
- **Anchored clustering** in sorted log price:
  - a pivot joins the current zone if it lies within 2·tol of the zone's lowest member;
  - zone = [min − tol, max + tol];
  - ≥ 2 touches (`ZONE_MIN_TOUCHES`);
  - **no chaining.**
- **Nearest resistance** = the nearest zone entirely above the close. **Nearest support** = the nearest zone entirely below it. A zone that contains the close is neither.

## 8. Trendlines (`trendline`)

- **Support line:** two confirmed swing lows L1 < L2 (rising), both within the last 252 sessions, anchors ≥ 10 sessions apart (`TL_MIN_SPACING`).
- **Resistance line:** two confirmed swing highs, falling, same rules.
- **Permanent invalidation:** the line is invalid if **any** close after the first anchor lies beyond it by more than tol (below for support, above for resistance). A broken line never revives.
- **Selection:** most touches (same-type pivots within tol of the line), then the most recent second anchor, then the earliest first anchor.
- **Value at t** = the line extrapolated to t.

## 9. Base (`base`, Weekly)

- **Anchor:** the most recent confirmed weekly swing high whose high is the highest weekly high of the prior 26 weeks inclusive (`BASE_ANCHOR_W`). Earlier anchors are not searched.
- **Length:** L = weeks since the anchor. **Valid iff 7 ≤ L ≤ 65** (`BASE_MIN_W`, `BASE_MAX_W`).
- **Depth** = 1 − (lowest weekly low since the anchor) / (anchor high).
- **Pullbacks:**
  - each confirmed weekly swing high (the anchor first) followed by a confirmed weekly swing low gives 1 − low/high;
  - **contracting** = ≥ 2 pullbacks, each strictly smaller than the previous.
- **Pivot level P** = the anchor high (one definition; no handle detection).
- **Base start day** = the last session of the anchor week.

## 10. Breakout (`breakout`, Daily)

- **Run start:** the current run of closes > P began at session j0.
- **Fresh breakout iff all hold:**
  - the close at t > P;
  - age = t − j0 < 5 (`BO_FRESH`);
  - j0 > base start day;
  - j0 ≥ 50 (volume reference available).
- **Measured at the decision:**
  - ext = close_t / P − 1;
  - clv = close location of day j0 = (c − l)/(h − l);
  - relvol = v[j0] / mean(v[j0−50 … j0−1]).
- **No later close is used.** A breakout that fails after t is still a breakout at t (tested).

## 11. Volume (explicit roles only)

| Role | Condition | Definition |
|---|---|---|
| Dry-up in the base | B4 | mean volume t−14 … t−5 / mean volume t−64 … t−15 ≤ 0.80 |
| Breakout confirmation | T3 | relvol ≥ 1.40 |
| Distribution | R4 | ≤ 4 sessions in the last 25 with return ≤ −0.2% on higher volume than the prior session |

Volume enters nowhere else.

## 12. Volatility contraction, extension and entry risk

- **One volatility-contraction measure (B3):**
  - mean true range t−14 … t−5 / mean true range t−64 … t−15 ≤ 0.80;
  - the last 4 sessions are excluded so the trigger day does not cancel the contraction.
- **Extension:**
  - R3: (close/SMA20 − 1) / ATR% ≤ 2.0;
  - D3: close > 1.25 × SMA50 disqualifies.
- **Support** = the highest of:
  - the nearest daily support-zone top;
  - the support trendline value at t if below the close;
  - the pivot P if the close is above it (role flip);
  - the most recent confirmed daily swing low if below the close.
  - If none exist, D4 applies.
- **Entry risk:**
  - risk = 1 − support / close;
  - R1: risk ≤ 8%;
  - R2: risk ≤ 2.5 × ATR%.

## 13. Frozen rendering (audit only, `qr_chart_render`)

**Format:**
- 1000 × 640 px, white background;
- price area = top 74%, **log scale**, range = min low / max high of the drawn bars, widened only to keep the active levels known at t (P, defined support) on screen, plus 4% padding;
- the decision bar t is the last drawn bar, then a margin of 6 empty slots;
- volume panel = bottom 20%;
- overlays are clipped to their panel;
- **no text** (no ticker, date, price or score).

**Daily panel:** last 126 sessions, with:
- MA20 / 50 / 200;
- the nearest daily resistance and support zones;
- the support line (solid) and resistance line (dashed);
- P (dashed);
- the 52-week high (dotted);
- the base strip.

**Weekly panel:** last 104 weeks, with:
- MA10 / 30 / 40 weeks;
- the nearest weekly zones;
- P.

**Encoding:** pure numpy raster plus a stdlib PNG encoder (zlib level 9). The output is byte-deterministic in one environment. Raster hashes are pinned for the synthetic scenarios.

**Licence:** images of QuantConnect data never leave QuantConnect and are never sent to any AI service. Rendering is not part of the score and is not run on real data in the validation.

## 14. Checklist, disqualifiers, score and groups

**Exact formulas, timeframes, histories, thresholds and sources:** `H020_threshold_provenance.md`.

**Weekly vs Daily:**
- **Weekly** gives trend and structure (W1–W4), the major base (B1, B2, B5) and the major zones (overlay).
- **Daily** gives setup maturity and trigger (B3, B4, T1–T5), short-term support, volume, contraction and extension / risk (R1–R5).

| Category | Conditions (1 point each) |
|---|---|
| W — Weekly trend & structure | W1 weekly close > MA30w · W2 MA40w rising over 4 weeks · W3 MA10w > MA30w · W4 weekly state ∈ {strong_uptrend, uptrend} · W5 close ≥ 0.75 × 52-week high |
| B — Base quality | B1 valid base · B2 depth ≤ 33% · B3 volatility contraction ≤ 0.80 · B4 volume dry-up ≤ 0.80 · B5 contracting pullbacks |
| T — Trigger / breakout | T1 fresh breakout · T2 ext ≤ 5% · T3 relvol ≥ 1.40 · T4 clv ≥ 0.5 · T5 close > MA50 |
| R — Entry risk & support | R1 risk ≤ 8% · R2 risk ≤ 2.5 ATR · R3 MA20 extension ≤ 2 ATR · R4 ≤ 4 distribution days / 25 · R5 daily state ∈ {strong_uptrend, uptrend, range} |

**Hard disqualifiers (any one → disqualified):**
- D1 weekly close < MA40w;
- D2 weekly state = downtrend;
- D3 close > 1.25 × MA50;
- D4 no support;
- D5 an open ≤ 0.85 × the prior close within 10 sessions.

**Score and groups:**
- **Score** = number of true conditions (0–20). **No weights.** B2–B5 require B1; T2–T4 require T1.
- **Q** (quality level) = −1 if disqualified, otherwise the score.
- **Groups (pre-declared):**
  - G0 = disqualified;
  - G1 = 0–5;
  - G2 = 6–10;
  - G3 = 11–15;
  - G4 = 16–20.
  - **High = G3 ∪ G4; Low = G0 ∪ G1.**

## 15. Baselines (stay with the stock in every world)

- **Baseline A — medium-term momentum:** mom = TR close at t−21 sessions / TR close at t−252 sessions − 1 (12-1 momentum, as H019 S1 in sessions).
- **Baseline B — price above a long MA:** trend = 1{weekly close > MA40w}.
  - **Note:** this is the complement of D1.
  - The incremental test therefore necessarily measures the score's information **beyond** "above the 40-week MA".

## 16. Per-date statistics (`date_stats` ≡ `fast_date_stats`)

These are computed on each decision date over the eligible stocks with a response (≥ 20 stocks), with yd = y − the cross-sectional mean (equal weight):
- **IC** = Spearman(Q, yd), average ranks;
- **group means** of yd for G0 … G4, plus the High and Low means;
- **Incremental (one method only):** a Fama-MacBeth cross-sectional OLS of rank(yd) on [rank(Q), rank(mom), trend] with an intercept, ranks scaled to (0, 1). inc = the coefficient on rank(Q).

## 17. Time-series inference

- IC and inc series: mean, Newey-West (Bartlett) standard error with **lag 3** (`NW_LAG`; responses overlap by 3 weeks), t = mean / se.
- The permutation null (§18) absorbs any residual misspecification of the standard error, because the whole procedure is re-run in every world.
- Annualisation: weekly-decision 4-week mean × 13.

## 18. Null (`run_world(prep, seed)`, `ChartTether`)

**Construction:** an identity-tethered within-date permutation of the **chart side** (Q, G) across stocks.
- Each receiving stock gets the chart side of a partner stock and keeps that partner while both stay in the cross-section. New or orphaned stocks are re-matched at random.
- **No self-matching:** fixed points are swapped out.
- **One stratum** (`NULL_STRATIFIED = False`).
- **Preserved:**
  - the dates;
  - the cross-section;
  - every stock's returns, momentum and trend;
  - the exact distribution and group counts of the scores on every date;
  - each null score history's persistence (it is a real stock's history);
  - the overlapping-return structure.
- **Broken:** only the link between a stock's chart score and its own future return.
- **Full procedure per world:** every statistic, group, regression and gate is recomputed.
- **Worlds:** R = 5,000 (seeds 1 … 5,000).
- **Critical values:** c_ic and c_inc = the 50th-largest null t_ic and t_inc (α = 1% each).
- **Decision rule:** promotion needs **both** (an intersection-union test), so P(false promotion) ≤ 1% without a multiplicity correction.
- **Why not stratified (rejected in P5-CP2, synthetic evidence `research/phase5/h020_null_design_check.json`):**
  - stratifying by momentum quintile × trend makes partners change almost weekly (persistence about 56%);
  - the null loses the real scores' persistence and becomes too narrow (size about 6% at a nominal 1%);
  - the flat tether keeps about 98% of partners and is calibrated.
  - Momentum and trend are controlled by G5 instead.

## 19. Gates (all required for "H020 qualified for portfolio research")

| Gate | Rule |
|---|---|
| G1 economic | High-group mean ≥ **+3.0%/yr** over the cross-sectional average (the economic-significance floor), **and** High > Low |
| G2 monotonic | Spearman(group index 0–4, group mean) ≥ 0.90 over groups with data |
| G3 significant | t_ic > c_ic |
| G4 stable | Mean IC > 0 in both halves of the decisions **and** no 2-year block (2010–11, 12–13, 14–15, 16–17) contributes > 50% of the IC sum |
| G5 incremental | t_inc > c_inc **and** inc > 0 |

**Outcomes:**
- **qualified** (all five gates pass);
- **not qualified** (any gate fails).

Diagnostics (never gates):
- the 13-week results;
- per-year IC;
- group means per year;
- category-level ICs (W, B, T, R sums);
- Spearman(Q, mom);
- group sizes.

## 20. 13-week diagnostic

The same statistics on y13 (NW lag 12, ×4 annualisation), computed in the same real run. Diagnostic only.

## 21. Relative strength (RS)

- **Excluded from the score.** Cross-sectional RS is Baseline A (momentum). Putting it inside the score would make the score partly the baseline it must beat.
- W5 (nearness to the stock's own 52-week high) is an absolute-strength condition, not RS versus the market.
- **Diagnostic:** the mean per-date Spearman(Q, mom).

## 22. Leakage canaries and reproducibility (synthetic, all passing in P5-CP2)

These are tests in `tests/test_h020_chart.py`, `tests/test_h020_scenarios.py` and `tests/test_h020_stats.py`.

**Leakage:**
- future perturbation (all features, score and both PNGs byte-identical);
- swing confirmation exactly at i + k;
- no repainting;
- scan-start independence;
- history-window sufficiency;
- the current partial week;
- future volume only;
- short / later-listed history;
- levels from pivots confirmed by t;
- support formed after t;
- trendline invalidation;
- base length;
- breakout followed by a later failure;
- an axis negative control;
- scale invariance.

**Reproducibility:**
- repeated runs and a fresh process give identical digests and PNG bytes;
- 12 synthetic scenarios match `h020_scenarios_expected.json` exactly.

## 23. Future run sequence (each step only after explicit owner approval; configs carry `owner_approval_required`)

| Step | Run | Publishes |
|---|---|---|
| 1 | **E987-01 (X987) PIT plumbing / fidelity canary** | Canary statistics only, **no response-linked statistic of a real score** (see the list after this table) |
| 2 | **E021-01..05 (S021 = byte copy of X987)**: null worlds 1–5,000 (1,000 per run), full procedure per world | Null t_ic / t_inc per world only |
| 3 | Commit and pin c_ic, c_inc and the null result hashes in `qresearch.p5h020`; verify a clean tree | — |
| 4–7 | **E021-06** the real scores and the real evaluation, **once** | 4-week statistics and gates (5), incremental test (G5), 13-week diagnostic (7) |
| 8 | P5-CP3 checkpoint | — |
| 9 | STOP | — |

**What E987-01 (step 1) checks:**
- an in-cloud snapshot digest equality against an independent slow recomputation for a fixed stock sample;
- leakage guards;
- placebo (seeded random) Q gives IC ≈ 0;
- a planted response-based Q gives its known IC;
- universe / history coverage counts;
- the last horizon ends ≤ 2017-12-29;
- runtime, memory and output size.

## 24. Interpretation rule (frozen)

**If H020 fails:**
- **never** tune base depth, breakout volume, support distance, weights, trendlines, cut-offs or any other number;
- **never** re-run a variant;
- **never** look for the stocks or periods where it "worked".

**Meaning of each outcome:**
- **Not qualified:** *"A pre-registered deterministic chart-structure checklist did not show predictive information large enough to meet the project's requirements in ≥ $2B US stocks, 2010–2017."* It is not proof that no chart information exists.
- **Qualified:** credible signal-level information on 2010–2017 only. It is not a strategy, not "beats SPY", and not 2018–2021 validation. The next step would be one separate portfolio pre-registration (owner approval).

## 25. Pinned constants

`qresearch.p5h020.CONSTANTS` lists every constant of `qr_chart` and `qr_h020_stats`. `tests/test_h020_spec.py` checks that the code carries exactly those values and that this file's hash is unchanged.
