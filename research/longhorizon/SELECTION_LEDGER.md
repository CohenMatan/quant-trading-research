# Long-horizon programme — hypothesis and selection ledger

Created by D241 (2026-10-18; `docs/checkpoints/RM2_h028_defensive_reference_offensive_companion_design.md` §22).

**Rule:** every hypothesis, signal variant, construction, weight policy and selection decision of the long-horizon
(defensive reference + offensive companion) programme is entered here **before** its result exists, with its
decision ID, stage, motivation label and outcome. Entries are never deleted or rewritten; outcomes are appended.
Current status of every hypothesis remains in `research/hypotheses/STATUS.md`; experiments in `experiments/INDEX.csv`.

**Motivation labels:** `literature` (design source independent of observed programme results), `development-motivated`
(influenced by observed 2011–2021 results, e.g. H028's profile), `H029-related` (overlaps H029 features).

**Budget (PROPOSED in RM2 §22, not yet approved):** Stage D ≤ 2 signal hypotheses (Holm), Stage E ≤ 1 portfolio,
Stage F ≤ 1 combination with one weight policy, Stage G ≤ 1 Holdout candidate.

**Context — prior looks at 2011–2021:** H001–H030 (`research/hypotheses/STATUS.md`); none qualified (D240).

| # | Date | Decision | Stage | Item | Motivation label | Pre-registered in | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | 2026-10-18 | D242 | C (data audit) | OF-A candidate families C1–C6: input coverage, timing and PIT feasibility only (no returns, no surprise values, no selection) | literature (family); C4 H029-related | `research/longhorizon/stage_c/LH_StageC_protocol.md` (ff97789b…) | Frozen classification C — NOT FEASIBLE (chain criterion mis-specified, disclosed); no candidate selected; awaiting owner |
| 2 | 2026-10-18 | D243 | C (data audit, follow-up) | Fiscal-calendar anomaly investigation of the Stage C chain criterion (metadata only; no candidate, no values combined) | — | `research/longhorizon/cp2/LH_CP2_protocol.md` (f7cbac94…) | C — INSUFFICIENT EVIDENCE; rule P proposed (not applied); Stage C unchanged; awaiting owner |
| 3 | 2026-10-18 | D244 | C (data audit, follow-up) | Missing fiscal-label recovery and validation (metadata only; reconstruction rules R* = M-SEQ ∧ M-CMP; no candidate, no values combined) | — | `research/longhorizon/cp3/LH_CP3_protocol.md` (38d790e5…), rules 9a72c5c8…, manifest ce09012e… | B — PARTIAL RECOVERY; verified-only histories meet the 70% floor 2015–2021; Stage C unchanged; awaiting owner |
| 4 | 2026-10-18 | D245 | Analytical feasibility (design only) | OF-A statistical power over the verified 2015–2021 population under the narrow Stage C exception (equations on assumed parameters; no candidate, no values) | — | `research/longhorizon/STAGE_C_EXCEPTION_D245.json`; `research/longhorizon/cp4/lh_cp4_power.py` | B — UNDERPOWERED FOR MODEST EFFECTS; no candidate selected; awaiting owner |
| 5 | 2026-10-18 | D246 | Candidate selection (design only) | H028 offensive complement: families A (leadership), B (quality growth), C (fundamental improvement), D (high beta, EW, announcement premium), OC-1 (SPY / QQQ); preferred OC-1 SPY, backup OC-B; proposed system test SYS-1 (not run) | development-motivated (H028 weakness map; disclosed) | `docs/checkpoints/OC_CP1_h028_offensive_complement_candidate_selection_test_design.md` | No stock-selection candidate selected; SYS-1 awaiting owner approval |
| 6 | 2026-10-18 | D247 | Candidate selection (design only) | Independent offensive stock selection: families A (business improvement), B (price leadership), D (earnings-announcement premium, net issuance); C folded into A / rejected levels; preferred **OC-2 = ΔROA (Data v3 F5) single-signal Fama–MacBeth test**, window 2012-02 → 2021-11 (coverage rule), Stage B-OC2 calibration first; OC-2 would supersede OF-A; no backup | literature (mechanism and signal choice); H029-related (F5 definition reused; disclosed); window rule from a committed non-return aggregate | `docs/checkpoints/OC_CP2_independent_offensive_stock_selection_candidate_review.md` §10 | Not registered, not run; awaiting owner |
| 7 | 2026-10-18 | D248 | Data integrity (Stage 1) + synthetic calibration (Stage 2) | OC-2 exact Data v3 F5: PIT / fiscal-period audit (metadata only); universe-wide Fama–MacBeth test calibration on synthetic worlds (no real signal or return) | literature (signal); H029-related (F5 definition reused, disclosed) | `research/longhorizon/oc2/stage1/OC2_S1_protocol.md` (91da6f27…); `research/longhorizon/oc2/stage2/OC2_S2_protocol.md` (447b4860… + Addendum 1 bcb872ad…) | Stage 1 PASS; Stage 2 D — INSUFFICIENT EVIDENCE (method not validated: leakage bias in 9 of 14 gating nulls); no real-data test; awaiting owner |
