# Owner message 2026-10-06: "Phase 7 — Multi-Factor Stock Conviction Score; P7-CP1 — Data Availability, Point-in-Time Integrity and Fidelity Audit Only"

This is a recorded summary; the full message is in the session transcript. Decision id: **D165**.

## Closure of Phase 6

- **H021-A:** Rejected / Did Not Qualify, preserved exactly as tested (P6-CP2).
- **Phase 6 is closed.**
- Phase 7 must not be used to rescue H021-A.

## Phase 7 concept (not to be designed or tested yet)

**Individual stock conviction score** = technical quality + fundamental quality + sector context. The **market regime** controls total portfolio exposure; it does not add points to every stock.

**Intended portfolio philosophy:**
- difficult entry and a high entry threshold;
- few, high-conviction holdings with long holding periods;
- a lower exit threshold (hysteresis) and a replacement buffer;
- low churn;
- cash is acceptable.

## P7-CP1 scope: data availability, data quality, point-in-time fidelity and implementation feasibility ONLY

Requested:
- a complete data inventory (price/technical, fundamentals, market cap/liquidity, sector/industry, market/breadth, corporate actions, delistings, calendar);
- a technical price-data audit, with independent recomputations;
- the fundamental field inventory and point-in-time chronology;
- fundamental leakage canaries: future-filing invariance, truncation, amendment timing, restatement protection;
- fundamental coverage and staleness by year, including field combinations;
- missingness characteristics;
- a sector-classification audit and sector-context feasibility;
- a market-regime and breadth audit, including breadth survivorship (point-in-time denominator);
- cross-domain timing alignment;
- candidate-universe fidelity;
- the earliest clean date per layer and the common development window, chosen mechanically;
- a data-error hunt, a reusable canary suite and a deterministic random-sample verification;
- data lineage, runtime / resource estimates and a component readiness matrix (A–D);
- an information-overlap map and hard-disqualifier feasibility;
- designs, not runs, for the availability-only threshold study, the portfolio-size study and the hysteresis / churn study;
- data gaps and the value of any purchase;
- answers to questions A–J;
- the deliverable P7-CP1 with 40 items.

## Constraints

- **No future returns** of any kind and **no test of whether any factor predicts returns**.
- **No score:** no weights, entry/exit thresholds, tiers, position sizes or maximum positions; no relaxation ladder; no portfolio backtest.
- **No 2018-01-01 → 2021-12-31** for feature inspection, coverage, design, thresholds or diagnostics.
- **The Holdout (2022-01-01 → 2026-08-31) stays locked.**
- **Do not modify the universe.** A material data defect: document it, assess its effect on earlier frozen research, and STOP for approval if a repair could change earlier conclusions.
- **STOP** after P7-CP1. The next step, P7-CP2 Actual Score Architecture Design, needs owner approval.
