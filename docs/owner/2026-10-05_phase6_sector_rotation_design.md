# Owner message 2026-10-05: "Phase 6 — Sector / ETF Relative Strength & Rotation Research; P6-CP1 — Evidence, Data Feasibility and Signal-Validation Architecture Only"

This is a recorded summary; the full message is in the session transcript. Decision id: **D159**.

## Direction

- **Objective (unchanged):** terminal wealth above SPY buy-and-hold after realistic costs; long-only, no leverage, same capital and dates.
- **New unit of prediction:** sectors / broad equity groups instead of individual stocks.
- **Research question:** do sectors with stronger medium-term relative strength subsequently outperform weaker ones? This comes before any portfolio question.
- **Hypothesis set:** a tiny set (1–3 explicit hypotheses: H021-A pure relative momentum; H021-B with an absolute trend), not an optimizer.

## Required design work

- **Evidence review:**
  - an A–D evidence hierarchy;
  - the distinction between stock, industry / sector, asset-class, time-series and ETF momentum;
  - original sample, post-publication evidence, large / liquid relevance, costs.
- **Universe:**
  - universe first (SPDR sector ETFs vs index series vs synthetic PIT sectors);
  - ETF inception / backfill;
  - a stable taxonomy;
  - XLC / XLRE.
- **Signal design:**
  - one primary lookback from external evidence;
  - absolute trend as a separate role;
  - no indicator soup;
  - monthly vs weekly decided on evidence.
- **Holding count:** at design level, including tracking error, turnover, $7 per order and 10 bps.
- **Validation:**
  - signal validation is cross-sectional first; SPY is not the primary statistical response;
  - small-N and effective sample analysis;
  - synthetic power (50% / 80% detectable edge, false-positive rate);
  - a full null preserving co-movement and persistence, with a full-search null if more than one lookback is used.
- **Accounting:** total return for signals and responses.
- **Other:**
  - a longer history (e.g. 2000+), feasibility only;
  - cash option as a design question;
  - breadth excluded.
- **No purchase.**

## Deliverable

P6-CP1 with 39 items plus answers to questions A–J.

## STOP conditions

**Not allowed:**
- a real sector signal test, sector future-return IC or rankings;
- portfolios, terminal wealth or SPY comparison;
- tuning;
- 2018–2021 for validation, or the Holdout;
- purchases.

**Allowed:**
- literature;
- QuantConnect data metadata / availability;
- infrastructure inspection;
- synthetic power studies;
- cost arithmetic;
- null design.

Then STOP and wait for the owner.
