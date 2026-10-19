# Hypothesis status index (H001–H030)

**Maintained index (D240, 2026-10-18).** This file is the current-status source for every hypothesis.

**Why it exists:** the hypothesis files H022–H028 are hash-pinned (`qresearch.p7pred`, `p8h023`, `p9h024`, `p10h025`, `p11h026`, `p12h027`, `p13h028`). Their "Status: pre-registered" headers are the frozen pre-registration text and are **deliberately not edited**. Where a hypothesis file and this index differ on *current* status, this index and `DECISIONS.md` govern. The frozen definitions and results in the files never change.

**Vocabulary:**

| Status | Meaning |
|---|---|
| REJECTED | A real result failed its own pre-registered gates |
| BLOCKED | Could not be tested validly |
| NOT EVALUABLE | Final administrative closure of a BLOCKED hypothesis without any valid real-data evaluation |
| NOT ADOPTED / REMOVED / WITHDRAWN | Never run |
| CLOSED | An owner closure decision exists |

| ID | Hypothesis | Phase | Current status | Records |
|---|---|---|---|---|
| H001 | Short-term reversal in uptrends | 1 (C01) | REJECTED (remedial re-test, all variations fail) | D067 |
| H002 | 12-1 momentum | 1 (C01) | REJECTED (C01 screen); C01 closed: No Production Candidate Found | D060 |
| H003 | 52-week high | 1 (C01) | REJECTED (C01 screen) | D060 |
| H004 | Pullbacks in momentum leaders | 1 (C01) | REJECTED (C01 screen) | D060 |
| H005 | Low-volatility anomaly | 1 (C01) | REJECTED: S005 v1.2 failed Validation 2018–2021 (E005-28); never re-validated on 2018–2021 | D056, D060 |
| H006–H011 | Breakout, squeeze, residual momentum, volume, gap, seasonality | 1 (C02) | REJECTED; C02 complete: No Production Candidate Found | D076, D078 |
| H012 | Volatility-managed exposure | 1 (C03) | REMOVED before any backtest (not evaluable with sufficient power; not a failed hypothesis) | D087 |
| H013 | Lottery-stock avoidance | 1 (C03) | REJECTED; C03 closed | CP3i, D090 |
| H014 | Trend + pullback + recovery | 2 | REJECTED and CLOSED | D100, D101 |
| H015 | Diversified low-turnover trend | 2 | NOT ADOPTED (never run) | D104 |
| H016 | Gross profitability GP/A | 2 | REJECTED and CLOSED | D117, D118 |
| H017 | Earnings-event continuation (8-K reaction) | 2 | REJECTED (Case A); Phase 2 closed. The H017 = Value draft was never approved (WITHDRAWN) | D120, D128, D129 |
| H018 | Systematic technical search (1,533 configs) | 3 | CLOSED: No Production Candidate Found | D139 |
| H019 | Cross-sectional technical signals (momentum, smooth momentum, trend factor) | 4 | NO SIGNAL QUALIFIED. No separate owner closure decision is on record; the owner moved to Phase 5. Spec: `research/phase4/P4_xs_spec.md` (no H019.md file) | D149, D150 |
| H020 | Structured chart score | 5 | REJECTED and CLOSED | D158, D160 |
| H021 (H021-A) | Sector-ETF relative momentum | 6 | REJECTED / Did Not Qualify; Phase 6 closed | D164, D165 |
| H022 | Conviction Score v1 | 7 | REJECTED / NOT QUALIFIED (E024-07). The pinned file still reads "pre-registered … Not run" | D198, D199 |
| H023 | Score v2 layer weights | 8 | CLOSED: no robust Score v2 candidate | D200, D201 |
| H024 | Feature redesign and selection | 9 | CLOSED: no robust feature model | D203, D204 |
| H025 | Insider cluster buying | 10 | REJECTED and CLOSED | D205, D206 |
| H026 | Learned score portfolio | 11 | REJECTED (permanent) | D210, D211, D213 |
| H027 | Exposure-controlled learned score | 12 | REJECTED and CLOSED. Its conditional-null p 0.0006 shares the D238 mechanism and should be read with the same caution | D216, D217 |
| H028 | Fixed strong shrinkage (λ = 100) | 13 | REJECTED (B4 failed). Conditional-null p ≈ 0.0004 structurally suspect (D238); repaired-null attempt **B — METHOD NOT VALIDATED** (D239); **Phase 13 CLOSED**. Descriptive designation (D241): **Frozen Defensive Research Reference** — not a status change, never a production component | D220, D238, D239, D240, D241 |
| H029 | Standalone business-improvement score | 14 | Historical: BLOCKED (two nulls inadequate; Null #3 failed synthetic feasibility). **Final: NOT EVALUABLE — NO VALID REAL-DATA EVALUATION** (never REJECTED on performance); **Phase 14 CLOSED** | D232, D234, D237, D240 |
| H030 | Fixed 50/50 blend of frozen H028 and H029 | 14 | Same as H029: historical BLOCKED; **final NOT EVALUABLE**; Phase 14 CLOSED | D232, D234, D237, D240 |

**Programme state (D240):**
- Research cycle completed: **No Production Candidate Found**.
- No active hypothesis and no active experiment.
- Holdout 2022-01-01 → 2026-08-31 sealed and never accessed.
- Any further research needs a new owner approval.

**Update (D241, 2026-10-18):** a long-horizon defensive-reference + offensive-companion programme is approved for DESIGN ONLY (`docs/checkpoints/RM2_h028_defensive_reference_offensive_companion_design.md`; ledger `research/longhorizon/SELECTION_LEDGER.md`). No hypothesis is active; OF-A is a candidate family, not a hypothesis.

**Update (D242, 2026-10-18):** Stage C OF-A data / PIT feasibility audit: frozen result **C — NOT FEASIBLE** (mis-specified chain criterion disclosed; `docs/checkpoints/LH_CP1_stage_c_ofa_data_pit_feasibility_audit.md`). Still no active hypothesis.

**Update (D243, 2026-10-18):** LH-CP2 fiscal-calendar anomaly investigation: frozen result **C — INSUFFICIENT EVIDENCE** (`docs/checkpoints/LH_CP2_fiscal_calendar_anomaly_resolution.md`); Stage C unchanged (C). Still no active hypothesis.

**Update (D244, 2026-10-18):** LH-CP3 missing fiscal labels recovery & validation (metadata only; 120 EDGAR header requests): frozen result **B — PARTIAL RECOVERY** (`docs/checkpoints/LH_CP3_missing_fiscal_labels_recovery_validation.md`); Stage C (C) and LH-CP2 (C) unchanged. Still no active hypothesis.

**Update (D245, 2026-10-18):** LH-CP3 accepted (B). Narrow prospective Stage C exception (2015–2021, verified L0 / L1 labels, rule V; `research/longhorizon/STAGE_C_EXCEPTION_D245.json`). LH-CP4 analytical feasibility: **B — UNDERPOWERED FOR MODEST EFFECTS** (`docs/checkpoints/LH_CP4_ofa_statistical_feasibility_research_horizon.md`). Still no active hypothesis.

**Update (D246, 2026-10-18):** research priority = offensive complement to H028 (design only; `docs/checkpoints/OC_CP1_h028_offensive_complement_candidate_selection_test_design.md`). Preferred complement OC-1 = SPY; proposed account-level system test SYS-1 not run. No new hypothesis registered. Still no active hypothesis.

**Update (D247, 2026-10-18):** independent offensive stock-selection candidate review (design only; `docs/checkpoints/OC_CP2_independent_offensive_stock_selection_candidate_review.md`). Proposed candidate OC-2 (profitability improvement ΔROA, Data v3 F5, single-signal test) — NOT registered as a hypothesis, not built, not run; it would receive the next hypothesis ID only on owner approval. H029 / H030 remain NOT EVALUABLE. Still no active hypothesis.

**Update (D248, 2026-10-18):** OC-2 (profitability improvement, exact Data v3 F5) approved as the single offensive candidate; not registered as a hypothesis, no real-data test run. Stage 1 data integrity PASS (`docs/checkpoints/OC_CP3_oc2_stage1_data_integrity.md`); Stage 2 synthetic calibration D — INSUFFICIENT EVIDENCE, method as specified not validated (`docs/checkpoints/OC_CP4_oc2_stage2_synthetic_calibration.md`). Still no active hypothesis.

**Update (D249, 2026-10-18):** OC-2 synthetic calibration v2 (one repair attempt) built and engineering-validated, then STOPPED before the confirmatory run for an owner decision on the identification family (noisy controls / latent factor; `docs/checkpoints/OC_CP5a_oc2_synthetic_calibration_v2_prerun_stop.md`). No v2 classification; v1 remains D. Still no active hypothesis.

**Update (D250, 2026-10-18):** OC-2 synthetic calibration v2 (one frozen confirmatory run): **C — NOT VALIDATED** (Tier 1 30 / 30 pass; severe hidden-factor world N2L5 at IC sd 0.12 full-rule false approval 4.40% > 2%; complete-rule power at +3% 43.5%) — `docs/checkpoints/OC_CP5_oc2_synthetic_calibration_v2.md`. Recommendation: close OC-2; SPY remains the offensive baseline. No real-data test. Still no active hypothesis.

**Update (D251, 2026-10-19):** **OC-2 — CLOSED — STATISTICAL METHOD NOT VALIDATED UNDER CURRENT RESEARCH CONSTRAINTS** (Stage 1 PASS; synthetic v1 D; v2 C; never evaluated on real returns; economic hypothesis not disproven; no further calibration). H029 / H030 remain NOT EVALUABLE. SPY = preferred simple offensive baseline. Corrected SYS-1 (H028 + SPY) design only (`docs/checkpoints/OC_CP6_oc2_closure_corrected_sys1_design.md`): original 50 / 50 infeasible under the frozen account rules; not registered, not run. Still no active hypothesis.
