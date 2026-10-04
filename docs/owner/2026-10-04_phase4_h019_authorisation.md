# Owner message 2026-10-04: "H019 — Authorise Final Cross-Sectional Signal Validation Run"

This is a recorded summary; the full message is in the session transcript. Decision id: **D145**.

## Authorisation
- H019 only, under the frozen specification v2 (`research/phase4/P4_xs_spec.md`, SHA-256 15fb0451…).
- **Signals, exactly three:**
  - S1 plain 12-1 momentum (reference / replication);
  - S2 smooth momentum: ID = sign(PRET) × (% negative days − % positive days); momentum quintiles first, then ID;
  - S3 the Han-Zhou-Zhu trend factor per the Chen-Zimmermann reproduction (11 MA horizons, rolling monthly cross-sectional regressions, previous 12 averaged, ≥ $2B point-in-time universe adaptation, partial-history behaviour as frozen). No 50/100/200 score.
- **Frozen:** monthly ranking; next-1-month primary; 3-month diagnostic only (cannot promote, rescue, veto or alter interpretation); universe US common stock, ≥ $2B, ≥ $5, ADV20 ≥ $5M; window 2011-01 → 2017-11 (83 monthly evaluation periods); 1% threshold; +3% economic floor; monotonicity; subperiod stability; incremental value for S2 / S3; family max-statistic null. Nothing may change after results.
- **Wording:** never "all 83 months are independent". Say: "83 non-overlapping monthly evaluation periods; synthetic calibration indicates effective sample size is close to the full 83 months."

## Exact sequence
1. QuantConnect plumbing / fidelity check (PIT universe and decision dates; signal availability and response alignment; S2 grouping and ID; S3 chronology and partial history; no leakage; determinism). If it fails: STOP, fix technical defects only.
2. 5,000 null worlds (S2 keeps PRET, ID and the two-stage relation; S3 re-fits the complete trend-factor pipeline per world).
3. Family null threshold.
4. Commit, hash and pin it (null method version, seeds, completed / failed / retried worlds, max-stat distribution, 99th percentile, empirical calibration, result-file hashes, threshold commit, null-result hash, spec hash).
5. Verify a clean tree.
6. ONE real evaluation of S1 / S2 / S3 (it records that it started from exactly the pinned state). No reruns or alternatives.
7. P4-CP4 checkpoint (36 items).
8. STOP.

## Interpretation rules
- S1 passing = replication / confirmation, not discovery.
- S2 / S3 must pass their incremental tests: "Among stocks with similar Plain Momentum, does Information Discreteness add predictive information?"; distinguish "Trend Factor predicts returns" from "merely repackages momentum".
- Failure wording: "No technical stock-selection signal large enough to satisfy the project's detection and economic-significance requirements was found."
- Success wording: "The signal shows credible cross-sectional predictive information on the frozen 2011–2017 development sample and is eligible for portfolio-design research." Not production-ready, validated, SPY-beating or investable.

## Forbidden
- New hypotheses from the result; any portfolio (holdings, rebalancing, Weekly exits, commissions, terminal wealth, SPY comparison); 2018–2021; the Holdout; paid data.
