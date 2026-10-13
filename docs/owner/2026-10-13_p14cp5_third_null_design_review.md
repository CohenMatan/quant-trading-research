# Owner message 2026-10-13: "Phase 14 — P14-CP5 Third Null Design Review Only"

Decision id: **D236**.

## What the owner approved
- **A design-only review** of a possible third null for H029 / H030. The checkpoint ends with a proposed methodology for owner review.
- **Not authorised:** implementation, QuantConnect execution, null worlds, thresholds, any real H029 / H030 evaluation, performance inspection, Holdout access, or H031.

## Status and constraints
- **Status (unchanged):** H029 / H030 BLOCKED, neither qualified nor rejected. No real performance run exists, no threshold exists, and the Holdout is sealed.
- **Hard constraints:**
  - no return information of any kind, including return columns of existing null files;
  - no Holdout data (2022-01-01 → 2026-08-31);
  - no production code (no qr_h029 null v3, S031 v1.2, E031-11 or equivalent);
  - toy examples and pseudocode only;
  - no 5,000-world experiment.

## Owner sections 7–8: established constraints and requirements
- **Constraints already established (section 7):**
  - the six signals update about quarterly;
  - sector structure matters;
  - the sector cap is not the turnover problem;
  - recipient eligibility is not the direct problem;
  - donor rematching is the primary problem.
- **Requirements R1–R12 (section 8):**
  - R1: break signal / return identity;
  - R2: preserve calendar time;
  - R3: preserve FF12 sector, with no silent cross-sector fallback;
  - R4: preserve the recipient eligibility path;
  - R5: preserve temporal continuity (no artificial jumps at other stocks' entries or exits);
  - R6: preserve quarterly update cadence;
  - R7: preserve cross-sectional structure, stating what is exact and what is approximate;
  - R8: preserve the ≥ 5 of 6 rule and Data v3 eligibility semantics;
  - R9: no self-assignment by default;
  - R10: no return-based matching;
  - R11: deterministic reproducibility;
  - R12: usable for the full 5,000-world pipeline including H030.

## Owner sections 9–43: what the review must cover
- the central tension of continuous randomized paths in a changing universe;
- candidate families:
  - A: eligibility-spell / trajectory permutation;
  - B: update-event / innovation permutation;
  - C: whole-path identity permutation;
  - D: block / segment permutation;
  - one further candidate, only if justified by the structural problem;
- a comparison matrix;
- over- and under-conditioning;
- sector changes, eligibility entry and exit;
- six-signal joint handling;
- the percentile level and the preferred randomization level;
- cross-sectional and temporal exactness;
- which relationships must be destroyed;
- size / liquidity matching (only if structurally required);
- filing clusters, corporate actions, PIT proof;
- synthetic canaries A–E;
- structural adequacy (without weakening the existing rules) and risk adequacy;
- H030 compatibility;
- computational feasibility and host architecture (recommendation only);
- rejection criteria;
- **at most one recommended design**, with an exact conceptual algorithm and a formal null hypothesis;
- interpretation of significance and of non-significance;
- the pre-performance amendment disclosure;
- the anti-fork rule (default YES).

## Required output
- **Checkpoint P14-CP5** (45 items, Q1–Q10 at the top).
- **Final status — one of:**
  - "THIRD NULL DESIGN REVIEW — ONE SCIENTIFICALLY PREFERRED DESIGN IDENTIFIED — AWAITING OWNER APPROVAL", or
  - "THIRD NULL DESIGN REVIEW — NO SCIENTIFICALLY SATISFACTORY DESIGN IDENTIFIED — H029/H030 SHOULD CLOSE AS NOT EVALUABLE".
- **Then STOP:** no implementation, canary, null worlds, thresholds, H029 / H030 run, Holdout access or H031.

Recorded with the P14-CP5 design review. No code, null world, QuantConnect run or performance quantity was produced.
