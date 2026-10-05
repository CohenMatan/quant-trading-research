# Owner message 2026-10-05: "H020 — Authorise Structured Chart Analysis Implementation and Canary Only"

This is a recorded summary; the full message is in the session transcript. Decision id: **D151**.

## Scope

- **Authorised:** implementation, reproducibility, leakage testing and canary validation of H020 = one pre-registered **deterministic** structured chart score.
- **Not authorised:**
  - real historical chart scoring on the 2010–2017 research universe;
  - any backtest of the chart score;
  - future returns by score;
  - 2018–2021;
  - the Holdout;
  - any portfolio.
- **No LLM / vision model in H020.**
  - Do not run the optional AI consistency study.
  - Do not send QuantConnect historical charts or OHLCV-derived images to external AI services.

## Required work

- **Deterministic pipeline:**
  - point-in-time OHLCV;
  - Daily + Weekly reconstruction;
  - confirmed swing points;
  - HH / HL / LH / LL structure;
  - support / resistance zones;
  - support and resistance trendlines;
  - base;
  - breakout;
  - volume / volatility;
  - entry risk;
  - the frozen checklist;
  - a 0–20 score plus disqualifiers.
- **Weekly role:**
  - long-term trend;
  - structure;
  - HH / HL;
  - major support / resistance;
  - major base;
  - broad relative-strength context.
- **Daily role:**
  - setup maturity;
  - breakout trigger;
  - short-term support / resistance;
  - volume;
  - contraction;
  - extension / entry risk.
- **The 4 × 5 checklist.** For every condition give:
  - the exact formula;
  - the timeframe;
  - the required history;
  - the exact threshold;
  - the source / rationale;
  - the point-in-time timing rule.
- **Threshold provenance classes:**
  - A = practitioner explicit;
  - B = derived from a practitioner rule;
  - C = academic;
  - D = engineering convention;
  - E = our design.
- **Provenance wording rules:**
  - Never write "from Weinstein / O'Neil / Minervini" unless that exact source supports the exact threshold.
  - State: "Practitioner rules are hypotheses / frameworks, not proof of predictive alpha."
- **Rules for each element:**
  - one definition only, no optimisation;
  - fully documented swing pivots with strict tests;
  - HH / HL states, keeping the P5-CP1 regression;
  - anchored S/R clustering;
  - permanent trendline invalidation;
  - one base framework;
  - one breakout architecture;
  - volume only in explicit roles;
  - one volatility-contraction measure;
  - relative strength documented as condition / diagnostic / excluded;
  - frozen hard disqualifiers, each with a reason;
  - score = 20 binary conditions, 1 point each, no weights.
- **Frozen rendering specification.**
- **Pixel / byte leakage canaries** for:
  - Daily and Weekly;
  - support / resistance;
  - trendlines;
  - swing structure;
  - base;
  - breakout;
  - score.
- **Extra canaries:**
  - future pivot confirmation;
  - future Weekly bars;
  - future volume;
  - later-listed stocks;
  - support formed after t;
  - chart scaling;
  - trendlines anchored after t;
  - base duration using future days;
  - breakout confirmation using later closes.
- **Reproducibility.** Identical features, zones, trendlines, score, disqualifiers and PNG bytes, with hashes recorded.
- **Universe:**
  - US common stock;
  - ≥ $2B;
  - ≥ $5;
  - ADV20 ≥ $5M;
  - a 2-year minimum history if technically necessary;
  - no technical pre-screen.
- **Timing and horizons:**
  - weekly scoring;
  - primary horizon 4 weeks;
  - secondary 13-week diagnostic, not evaluated now.
- **Mandatory incremental test** beyond:
  - Baseline A = medium-term momentum;
  - Baseline B = price above a long MA.
  - One method only.
- **Pre-declared score groups.**
- **Null:**
  - preserves scores, regimes, distribution, counts, return structure and dates;
  - breaks the link between a score and its own return;
  - evaluates the full procedure.
- **Gates:** economic, monotonic, significance, stability and incremental, with an economic floor.
- **Power update** only if the mechanics change materially (synthetic only).
- **Threshold-source audit table.**
- **Synthetic fixtures A–J,** each with documented expected features and score; the implementation must match exactly:
  - A clean weekly uptrend;
  - B range / choppy;
  - C healthy base;
  - D deep / failed base;
  - E valid breakout;
  - F false breakout;
  - G support break;
  - H overextended;
  - I contracting volume;
  - J expanding breakout volume.
- **Runtime / memory / capacity,** including QuantConnect runtime and output.

## Deliverable and future sequence

- **Deliverable:** P5-CP2 "H020 Structured Chart Score Implementation and Validation Readiness" (40 items). The final verdict is either "READY FOR H020 REAL SCORE VALIDATION" or "NOT READY".
- **Future sequence (design only):**
  1. PIT plumbing / fidelity check;
  2. null calibration;
  3. freeze the threshold in Git;
  4. compute the real scores once;
  5. 4-week evaluation;
  6. incremental test;
  7. 13-week diagnostic;
  8. checkpoint;
  9. STOP.
- **Interpretation rule.** If H020 later fails, never tune any of the following:
  - base depth;
  - breakout volume;
  - support distance;
  - weights;
  - trendlines;
  - cutoffs.
- **STOP after P5-CP2 is written, committed and merged.** Then do not do any of the following:
  - calculate real historical chart scores;
  - inspect 2010–2017 predictive results;
  - run the null on the real universe;
  - build a portfolio;
  - access 2018–2021 or the Holdout;
  - modify thresholds based on historical winners;
  - add AI or new indicators.
- Wait for explicit owner approval before H020 real score validation.
