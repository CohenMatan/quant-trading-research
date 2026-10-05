# H020 specification — Addendum 1 (pre-run clarifications; written before any real chart score exists)

- **Date:** 2026-10-05.
- **Owner authorisation:** "H020 — Authorise Real Structured Chart Score Validation" (D154; `docs/owner/2026-10-05_h020_real_validation_authorisation.md`).
- **What this addendum is:** an addition to `research/phase5/H020_spec.md` v1, which stays unchanged (its hash pin stands). This addendum is pinned separately in `qresearch.p5h020`.
- **What it does not change.** It changes **nothing** in:
  - the chart score: the 20 conditions, the 5 disqualifiers, the score groups and every algorithm;
  - the universe, frequency or horizons;
  - the baselines, the incremental model, the null, the gates or the economic floor.
- **What it does.** It records owner-requested clarifications and implementation details fixed before the first real computation.

## A1. Response = total shareholder return (owner item 5)

The chart keeps the frozen **split-adjusted, non-dividend-adjusted** bars. The response that judges the signal is the **total shareholder return**:

- **Formula.** y = TRC[end] / TRO[t+1] − 1, where:
  - TRO[t+1] = the open of the first session after the decision;
  - end = the close of session t+20 (4 weeks), or t+65 for the 13-week diagnostic.
- **TR price construction** (H019 construction, D148): TRC / TRO = RAW close / open × the split-feed multiplier × the dividend-feed multiplier. Every row before an event's first session is multiplied:
  - by the split factor, for a split;
  - by (1 − distribution / reference price), for a dividend-feed event — QuantConnect's own price-factor convention, i.e. dividends reinvested at the reference price.
- **What the response therefore includes:**
  - **price return;**
  - **cash dividends** (dividend feed);
  - **splits and reverse splits** (split feed);
  - **other price-factor events** that QuantConnect carries in its dividend feed (spin-offs and special distributions).
- **Delisting.** A stock delisted inside the window is valued at its **last real close**, which is LEAN's delisting / terminal value. Nothing after the last bar is invented.
- **Exclusion.** A stock without a bar at t+1 has no response and is excluded on that date (spec §4).
- **Verified in the E987-01 canary:**
  - an independent recomputation from RAW prices and the event lists (a fresh history request per sampled stock, no multiplier arrays: `qr_h020_panel.response_slow`);
  - a panel-wide check that TSR ≥ price return in every window containing a dividend;
  - delisting counts.
- If dividends were not included correctly, H020 would STOP before the real evaluation and fix the accounting only.

## A2. Point-in-time sector / industry (owner items 3, 4, 16)

- **Data.** The project has a trustworthy point-in-time industry classification: the **SEC-assigned SIC code at each filing**, dated (D113, data infrastructure v1, `qr_industry.SICHistory`).
  - It is never a present-day label.
  - It is never inferred from current Morningstar metadata.
  - It is mapped to the **Fama-French 12 industries** with H019's frozen mapping (`qr_xs_diag.ff12`).
  - A stock without a SIC on the date is its own group, 'Unclassified' (H019: about 3% of observations).
- **The diagnostic, fixed before any real score: NON-GATING SECTOR DIAGNOSTIC.**
  - On each primary decision date, the frozen G5 regression, rank(yd) on [rank(Q), rank(mom), trend] with an intercept, **plus one dummy per FF12 group present on that date**.
  - A collinear dummy is omitted by the same in-order rule as `qr_xs.ols_slopes`.
  - Reported: the mean coefficient on rank(Q), its Newey-West t (lag 3), and the classified share. It is computed in the same real run, after the primary result.
- **It is not a gate:**
  - it cannot promote, rescue or veto anything;
  - it is reported side by side with the G5 result;
  - neither is chosen after seeing which looks better.
- **Sector is used only for this diagnostic.** It is never used to screen candidates, alter scores, change thresholds, prefer sectors or create sector-specific chart rules.

## A3. Implementation details fixed before the first real computation (clarifications, not changes)

| Item | Rule |
|---|---|
| Decision universe | The harness eligibility recorded at the **last official session of each ISO week** (eligibility as of the previous close, the H019 / harness convention), with market cap and the point-in-time SIC |
| Look-back history | Daily bars from 2006-11-01 (≥ 756 sessions before the first decision, so every long-listed stock has the full snapshot window). Pre-2010 bars are look-back only |
| Stock's own bars | Rows where the split-adjusted open, high, low and close are finite and > 0; a missing volume is 0 |
| History rule | ≥ 504 own bars up to and including t; a bar at t is required |
| Baseline B | trend = 1{close at t > MA40w}, where the close at t is the decision week's weekly close |
| Baseline A | Market-calendar sessions t−21 and t−252, each the stock's last valid TR close at or before that session within 5 sessions (H019 S1 rule). A stock without defined momentum is excluded on that date (count reported) |
| 13-week decisions | Primary decisions whose t+65 is on or before 2017-12-29 |
| Null batches | E021-01..05 = seeds 1–1,000, …, 4,001–5,000 (1,000 worlds per run); every world runs the complete procedure; per-world statistics are published, so each world's G1–G5 outcome can be evaluated with the final critical values |
| Critical values | c_ic, c_inc = the 50th-largest of the 5,000 null t_ic and t_inc. They are committed and pinned in `qresearch.p5h020` with the null result hash, the spec, addendum and code hashes and the **chart-panel hash**, before E021-06 |
| Real run guard | E021-06 refuses to compute anything if its chart-panel hash differs from the pinned one |
| Descriptives (no return, non-gating) | Score distribution (Q −1 … 20, G0–G4) overall and by year; group sizes by date; frequencies of the 20 conditions and the 5 disqualifiers (overall, by year, and among non-disqualified); Spearman(score, momentum); score vs trend; score vs category counts |
| Not done | Component mining: no per-condition return test, no condition selection or reweighting |

## A4. Run sequence

1. E987-01 canary (X987).
2. Verify the response accounting (A1) and sector availability (A2).
3. E021-01..05 null (S021 = byte copy of X987).
4. Compute c_ic and c_inc.
5. Commit and pin.
6. Verify a clean tree.
7. E021-06, once.
8. P5-CP3.
9. STOP.
