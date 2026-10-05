# Owner message 2026-10-05: "H020 — Authorise Real Structured Chart Score Validation"

This is a recorded summary; the full message is in the session transcript. Decision id: **D154**.

## What was approved

- **Scope:** the real H020 validation under the frozen specification (`research/phase5/H020_spec.md` v1), for **H020 only**. Do not broaden the experiment.
- **Hypothesis:** a deterministic structured chart score, combining Weekly trend / structure, base quality, breakout / trigger quality and entry risk / support quality, may predict subsequent stock returns beyond simple momentum and broad trend.
  - 20 binary conditions, 1 point each, 0–20, plus frozen disqualifiers.
  - No learned weights, no threshold optimisation, no AI.

## What stays frozen

- **Immutable throughout:**
  - Weekly / Daily construction;
  - swing points and HH / HL / LH / LL states;
  - support / resistance zones, trendlines, base and breakout;
  - the volume rules, the contraction rule and support / risk;
  - the 20 conditions, the 5 disqualifiers and groups G0–G4;
  - the universe, the weekly frequency and the 4-week primary horizon;
  - the 13-week diagnostic;
  - G1–G5 and the +3% floor;
  - the null architecture and the 5,000 null worlds.
- **After the null thresholds are committed, also immutable:**
  - c_ic and c_inc;
  - the monotonicity and subperiod rules;
  - the incremental model and both baselines.

## Clarifications to apply before the real run

- **Sector:** if trustworthy point-in-time sector / industry data exists, add a pre-registered NON-GATING sector diagnostic (one simple method, e.g. Fama-MacBeth with point-in-time sector fixed effects).
  - If it does not exist, record it as a limitation and do not block H020.
  - Sector is never used inside the score, for screening, or for thresholds.
- **Response:** use total shareholder return (price, cash dividends, splits / corporate actions, delisting proceeds), while the chart keeps the split-adjusted, non-dividend-adjusted prices. If dividends are not handled correctly, STOP and fix the accounting only.

## Execution

**Sequence (only this order):**
1. E987-01 canary;
2. verify the response accounting;
3. verify sector availability / the diagnostic plan;
4. E021-01..05: 5,000 null worlds;
5. compute c_ic and c_inc;
6. commit / hash / pin;
7. clean tree;
8. E021-06: ONE real evaluation;
9. P5-CP3;
10. STOP.

**Canary must verify:**
- PIT universe membership;
- score-table coverage;
- exact weekly decision dates;
- the history requirement;
- independent slow recomputation;
- chart-feature digests;
- planted-signal recovery;
- placebo behaviour;
- no look-ahead;
- response alignment;
- horizon end ≤ 2017-12-29;
- runtime / memory;
- split / dividend / delisting accounting.

A technical defect means STOP and fix the implementation only.

**Null:** 5,000 worlds of the frozen identity-tethered chart-side permutation.
- **Preserved:** dates, returns, momentum, trend, the per-date score distribution, group counts, persistence and overlapping returns.
- **Broken:** only score ↔ own return.
- **Rules:** no self-matches, no momentum-stratified re-matching, the full procedure in every world.
- **Critical values:** two separate ones (c_ic, c_inc; the 50th-largest equivalent); no shared max-statistic.

**Pins before the real result:**
- c_ic and c_inc;
- the null method version;
- the RNG / world identifiers;
- worlds completed and retries / failures;
- the result hashes and the score-panel hash;
- the spec hash and the code hash.

The real config references the pins; the tree must be clean.

**Real evaluation:**
- exactly once over 2010–2017, with no reruns with alternate parameters;
- the 13-week result is NON-GATING;
- no post-result component mining.

## Required report and interpretation

**Report (P5-CP3, with the owner's full item list):**
- group sizes by date;
- G0–G4 means;
- High / Low;
- High vs the average and High − Low;
- IC and t_ic;
- monotonicity and stability;
- G5;
- the sector diagnostic;
- score distribution by year;
- condition / disqualifier frequencies;
- descriptive correlations;
- every confirmation.

**Interpretation wording:**
- **Fail:** "The frozen structured chart-analysis rubric did not demonstrate predictive information large enough and robust enough to qualify for portfolio research." Never "chart analysis does not work" or "no 1–2% edge exists".
- **Pass:** "The frozen structured chart score demonstrates credible cross-sectional predictive information in the 2010–2017 development period and qualifies for portfolio-design research." Never "production-ready", "out-of-sample validated", "SPY-beating" or "investable".

**Final verdict:** one of:
- "NO CHART SCORE QUALIFIED FOR PORTFOLIO RESEARCH";
- "H020 CHART SCORE QUALIFIED FOR PORTFOLIO RESEARCH".

## Not authorised

- any portfolio (no stock count, sizing, exits, stops, commissions, terminal wealth or SPY comparison);
- 2018-01-01 → 2021-12-31;
- the Holdout 2022-01-01 → 2026-08-31;
- AI;
- data purchase;
- new indicators or chart rules.

## STOP

After P5-CP3 is written, committed and merged.
