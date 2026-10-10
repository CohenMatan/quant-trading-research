# Owner message 2026-10-10: "Phase 7 — P7-CP5g Owner Acceptance of Identity Residual and Final Data v2 Freeze. Freeze Only — No H022 Canary, No Null Worlds, No Real Evaluation"

Recorded summary (the full message is in the session transcript). Decision id: **D192**.

**Decision:** the owner approves Option 1 of P7-CP5f item 56. The identity residual documented in P7-CP5f is accepted as an explicit **owner-approved exception to Gate K**, and Data Infrastructure v2 is frozen exactly as built.

**The accepted residual:**

| Item | Value |
|---|---|
| Affected securities | 161 |
| SEC identity REJECT | 105 |
| Without a usable SEC identity row | 56 |
| Affected share of eligible stock-months | about 3.4% in 2011, rising to 6.9% in 2017 |
| Pre-registered incidence criterion (≤ 3% every year) | **failed** |
| Estimated survivorship tilt from the exclusion | about +0.47 points |
| Pre-registered tilt limit (≤ 1.0 point) | passed |

**Permanent record of the failed criterion.** The record must say: "Gate K: FAILED under the original pre-registered 3%-per-year identity-incidence criterion." Then "OWNER-APPROVED EXCEPTION".
- The 3% criterion is not changed.
- The original result is not relabelled PASS.
- History is not rewritten.

**Reason given by the owner:**
- The incidence criterion failed, but the measured survivorship impact (+0.47 points) is below the pre-registered 1.0-point limit.
- It is also smaller than the +0.79-point overall Data v2 universe residual that was already accepted.
- The judgement is made before any H022 real return, real IC, null threshold or real gate result has been observed.

**Required wording (permanent):**

> Data v2 did not technically pass every original freeze criterion. Gate K failed because the identity-affected population exceeded the pre-registered 3%-per-year incidence threshold. The owner knowingly accepts this residual without changing the threshold because the measured survivorship effect is only +0.47 percentage points, below the 1.0-point materiality bound, every PIT/integrity gate passed, and no real H022 result has yet been observed.

**Constraints:**
- No change to:
  - code, data or the reference table;
  - the identity extension, the REJECT list or the no-identity list;
  - the market-cap repair, M2, the restatement guard or the $2B threshold;
  - Score v1, H1–H7 or the mechanics;
  - the research window, the universe rules or any threshold.
- No attempt to improve the 161-security residual.
- No rerun of E998-01..04; existing evidence is not recomputed.
- Pin the existing candidate manifest `research/phase7/data_v2/data_freeze_v2.json` with a final status such as "FROZEN — OWNER-APPROVED GATE K EXCEPTION" and record `MANIFEST_SHA256`. Do not regenerate the underlying inputs.
- Record the CP5f evidence:
  - PIT audit 0;
  - determinism, truncation and split audit;
  - M2 and the market-cap repair;
  - 2011–2012 operational;
  - compliance and export;
  - no real returns, IC or H022 gate.
- Record the CP5f structural results:
  - 90,370 universe stock-months;
  - survivor share 84.1%;
  - 304–728 fully scored stocks a month;
  - 7.07 candidates of 80+ a month;
  - 69% utilisation;
  - 46.6 orders a year;
  - 0.79% a year in costs at $100K.
- Record the synthetic power results (main scenario): 50% IC 0.034, 80% IC 0.049, false promotion 0.1%. The synthetic c_IC is not the empirical H022 threshold.
- The old c_IC = 2.390976216956 stays DATA_V1_ONLY / UNUSED_ON_V2.
- H022 is not authorised: no canary, real returns, null worlds, new c_IC, real IC, quintile or 80+ returns, G1–G4 or portfolio.
- 2018–2021 and the Holdout (2022-01-01 → 2026-08-31) stay sealed.
- Checkpoint "P7-CP5g — Owner Acceptance of Identity Residual and Final Data v2 Freeze" (39 items). Final status:

  ```
  FROZEN — Data Infrastructure v2
  Owner-approved Gate K identity residual exception
  ```

  Then STOP.

**Next stage (planning only, not authorised):** H022 on Data v2:
1. canary;
2. 5,000 new identity-tethered null worlds;
3. new empirical c_IC;
4. pin c_IC before any real run;
5. owner review;
6. one real H022 evaluation.
