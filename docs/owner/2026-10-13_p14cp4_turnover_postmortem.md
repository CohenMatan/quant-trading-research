# Owner message 2026-10-13: "Phase 14 — P14-CP4 H029 Structural Turnover Post-Mortem"

Decision id: **D235**.

**The owner asked for a structural diagnostic only:** why the real H029 Top-15 changes fewer names per month (0.3574) than every one of the 5,000 sector-stratified null worlds (minimum 0.3622).

**The formal status stays unchanged:**
- H029 / H030 BLOCKED — SECTOR-STRATIFIED NULL ALSO INADEQUATE;
- neither qualified nor rejected.

**Prohibited:**
- any return-based quantity (returns, CAGR, wealth, Sharpe, alpha, IC, capture, drawdown, feature-return correlation, P&L);
- E031-10 or any real-performance run;
- any Holdout access (no prices, fundamentals, returns, metadata, diagnostics or sanity checks for 2022-01-01 → 2026-08-31);
- designing, implementing, simulating, calibrating or recommending a third null, or comparing third-null designs;
- an owner exception, or weakening the adequacy rule;
- rewriting either historical null result.

**Method rules:**
- Use committed artifacts first (P14-CP1, P14-CP2, P14-CP3a, P14-CP3b; score and null rows), offline and deterministic.
- Mark anything that cannot be reconstructed "NOT AVAILABLE FROM COMMITTED ARTIFACTS".
- A structural-only run may be proposed at the end, not executed.

**Bug rule:**
- An implementation bug in the score, Top-15, sector null, turnover or donor mapping → "P14 STRUCTURAL BUG FOUND — OWNER REVIEW REQUIRED", STOP, no silent repair.
- No bug → H029 / H030 remain BLOCKED; no thresholds, no real run, no automatic Amendment 2.

**Requested analyses (owner sections 8–39):**
- turnover definition and reproduction with a plain-English magnitude;
- month-by-month real and null turnover;
- persistence concentration;
- Top-15 survival and holding spells;
- rank and raw-score persistence;
- persistence of each of F1 / F2 / F4 / F5 / F7 / F8, and of the composite;
- fundamental update cadence and filing-driven updates;
- entry / exit causes;
- sector-cap interaction;
- score margin and next-month rank depth;
- donor persistence and rematch causes;
- donor-rematch explanatory power;
- same-donor score persistence;
- stock-specific persistence;
- eligibility and missing-feature contributions;
- signal-sign stability;
- score-change, rank-change and within-sector rank-change magnitudes;
- a dominant-mechanism classification (A–F);
- a descriptive (not causal) attribution;
- whether the persistence is natural or an artifact;
- the properties any future null would need to preserve (conceptual only);
- the H030 blending explanation.

**Required output:**
- Checkpoint P14-CP4 with 50 items, Q1–Q10 at the top, and a final status of TURNOVER POST-MORTEM A / B / C / D / E.
- Then STOP: no null #3, no thresholds, no H029 / H030 run, no Holdout, no H031.

Recorded and committed with the P14-CP4 analysis. No return, Holdout value or QuantConnect run was used.
