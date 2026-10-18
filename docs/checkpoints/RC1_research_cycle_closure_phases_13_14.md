# Research Cycle Closure — Phases 13 and 14

**Owner decision D240, 2026-10-18.** The message is recorded verbatim in `docs/owner/2026-10-18_close_phases_13_14_roadmap.md`.

**Nature:** administrative closure and documentation only. Nothing was run:
- no backtest;
- no null-world or synthetic experiment;
- no QuantConnect research run;
- no data purchase;
- no Holdout access.

No historical strategy implementation, frozen result, data manifest, threshold, gate or decision ID was changed.

## 1. Repository state verified before any edit

| Item | State |
|---|---|
| `main` | `ebf8579` (PR #104, P13-CP6), identical to the working branch |
| Working tree | Clean |
| Decisions | Last D239 |
| Experiments | Last E031-09 |
| `HOLDOUT_UNLOCK.md` | Absent |

No material change since P13-CP6. The QuantConnect session checks pass (credentials present, never printed; site reachable).

## 2. Owner approvals recorded (D240)

**Approved:**

- **A. Accept P13-CP6.**
  - Classification **B — METHOD NOT VALIDATED**.
  - The H028 null-repair workstream is closed: no R1-V1, no R1b, no further repair variants.
  - Every synthetic artifact and failure is preserved.
  - This is **not** a claim that no valid method could ever exist.
- **B. Close Phase 13:** **PHASE 13 — CLOSED — NO QUALIFIED PRODUCTION CANDIDATE.**
- **C. Close Phase 14:** **PHASE 14 — CLOSED — H029/H030 NOT EVALUABLE.**
- **D. Close the research cycle:** **Research cycle completed — No Production Candidate Found.**
  - This is not a decision to abandon systematic investing.
  - None of the evaluated hypotheses met its own qualification criteria.
- **A design-only roadmap:** `docs/checkpoints/RM1_long_term_defensive_offensive_equity_roadmap.md`.

**Not approved:** any further research execution, H031, or the third null.

## 3. H028: history preserved, status unchanged

1. **Approval.** H028 was explicitly approved as a post-hoc, single-λ experiment (D217).
2. **Development backtest** E030-05 (2015–2021, $100,000 start):

   | | H028 | SPY |
   |---|---|---|
   | Final wealth | $328,295 | $262,325 |
   | CAGR | 18.5% | 14.8% |
   | Max drawdown | −26.1% | −33.7% |

   (`research/phase13/cp1/P13_CP1_result.json`)
3. **Gates.**
   - **B1** passed against its conditional null (S 0.224, p ≈ 0.0004).
   - **B4 failed:** over 2015–2017 H028 trailed the LOWVOL-only comparator by −0.006 in log wealth (D220).
4. **D238 (P13-CP5).** The conditional null's persistent donor pairing re-forms about 17.6% of pairs a month under universe churn. This penalises null worlds structurally, so **the p ≈ 0.0004 is not reliable evidence of stock-selection alpha**.
5. **D239 (P13-CP6).** A repaired, exposure-matched null (R1) proved infeasible: an H028-like Top-15 sits in the joint tail of the controlled exposures. The secondary factor regression (R3) was miscalibrated under priced growth and profitability factors. **B — METHOD NOT VALIDATED.**
6. **Status:** **H028 REJECTED** (unchanged, permanent).
   - It may be cited as a historical, defensive-style observation.
   - It is never a validated strategy, proven alpha or approved production component.

## 4. H029 / H030: BLOCKED history, final NOT EVALUABLE

| Step | Record |
|---|---|
| Approved for development | D229 |
| Data v3 built and frozen | D230 |
| Pre-registration frozen | D231 |
| Original single-stratum null inadequate (sector concentration) | D232 / P14-CP3a |
| Owner-approved sector-stratified null also inadequate (name turnover) | D233, D234 / P14-CP3b |
| Post-mortem: the failure is the null's own pairing mechanics | D235 / P14-CP4 |
| Third-null design approved in principle | D236, D237 |
| That design failed its synthetic feasibility before any real-data world | P14-CP6a |
| Valid final null calibration completed | **Never** |
| Threshold pinned | **Never** (`qresearch.p14h029`: thresholds `None`) |
| E031-10 (the real evaluation) | **Never executed** |
| Real H029 or H030 return, wealth or performance computed | **None** |

**Historical status (kept in the record):** BLOCKED.

**Final administrative classification: NOT EVALUABLE — NO VALID REAL-DATA EVALUATION.**
- Neither hypothesis is REJECTED.
- Neither is called profitable, unprofitable or statistically insignificant.
- No third or new null will be launched.
- Data v3 and every Phase 14 artifact are retained.

## 5. Data versions retained (unchanged)

| Version | Manifest | Pin | Status |
|---|---|---|---|
| Data v1 | `research/phase2/data_freeze_v1.json` | `qresearch.datafreeze` 17fffa03… | Frozen; does not reproduce on QuantConnect's current default build (D183) |
| Data v2 | `research/phase7/data_v2/data_freeze_v2.json` | `qresearch.datafreeze_v2` cf833f6f… | Frozen with the owner-approved Gate K exception (D192 / D193) |
| Data v2.1 | `research/phase11/data_v21/data_freeze_v21.json` | `qresearch.datafreeze_v21` ef0a7a66… | Frozen (D207); NEW_YEARS_MAPPING failed as written, owner-approved exception (D213); ends 2021-12-31 |
| Data v3 | `research/phase14/data_v3/data_freeze_v3.json` | `qresearch.datafreeze_v3` 601d0062… | Frozen (D230); H029-only guard layer on Data v2.1 |

## 6. Experiments preserved

- `experiments/INDEX.csv` is unchanged: 580 rows, 413 distinct experiment IDs.
- Research-kind originals: 147, covering hypotheses H001–H011, H013, H014, H016–H028.
- 29 S-strategies.
- Every null-world result, failed synthetic test, owner approval and statistical threshold stays in place.

## 7. Status documentation updated

| File | Change |
|---|---|
| `CLAUDE.md` | A programme-status block at the top of *Current state* plus the D240 entry |
| `DECISIONS.md` | D240 |
| `RESEARCH_LOG.md` | Closure entry |
| `research/hypotheses/STATUS.md` (new) | Current status of H001–H030 with sources |
| `research/hypotheses/H029.md`, `H030.md` | Outcome notes above the unchanged pre-registration text (these files are not hash-pinned) |

**H022–H028 files are not edited.** Their pre-registration headers are hash-pinned (`qresearch.p7pred` … `p13h028`), so their current status lives in the index.

## 8. Final state

- **PHASES 13–14 CLOSED**
- **H028 REJECTED**
- **H029 / H030 NOT EVALUABLE**
- **NO PRODUCTION CANDIDATE**
- **NEXT RESEARCH PROGRAMME: DESIGN ONLY** (`docs/checkpoints/RM1_long_term_defensive_offensive_equity_roadmap.md`)
- **2022–2026 HOLDOUT SEALED** (never accessed; no `HOLDOUT_UNLOCK.md`)
- **AWAITING OWNER DECISION**
