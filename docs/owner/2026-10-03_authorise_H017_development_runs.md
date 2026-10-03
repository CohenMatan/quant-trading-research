# Owner message 2026-10-03: "Phase 2 — Authorise H017 Development Runs Under the Frozen Decision Tree"

This is a recorded summary; the full message is in the session transcript.

- **Confirmed state:**
  - H017 implementation complete;
  - canary E982-02 passed 25/25;
  - no candidate performance viewed;
  - slot 3 unused; Holdout locked;
  - Amendment 3 and Event Data v1 unchanged;
  - no data purchase.
- **Authorised: the committed set, in order, with frozen code / spec / configs only:**
  - E017-01 (candidate, $100K);
  - E017-02 (EW-H017);
  - E017-03 … 07 (random-event seeds 1–5);
  - E017-08 (candidate, $200K sensitivity).

  No modification of H017 based on intermediate results; do not stop after E017-01.
- **Slot accounting:** the moment E017-01 starts successfully, Phase 2 slot 3 = consumed (recorded explicitly). Technical crashes before meaningful execution may be repeated under the technical-repeat rules; they are not new trials.
- **No Holdout access** (2022-01-01 → 2026-08-31) for any run, diagnostic, robustness run or analysis. Evaluation on 2010-03-01 → 2021-12-31 only.
- **Evaluation under Amendment 3:**
  - W1, with the wealth table (initial capital, final H017 and SPY values, terminal-wealth ratio, total return, CAGR, excess CAGR);
  - W2, exactly as frozen (g ≥ 2.15 × max(SE_iid, SE_stationary-bootstrap), block 126);
  - W3 vs EW-H017 and the median of seeds 1–5 (every seed reported);
  - R1–R4, exactly as frozen.
- **Decision tree only:**
  - **Case A:** Rejected; no tuning, no data, no unnecessary diagnostics or robustness; checkpoint and STOP.
  - **Case B:** if PbNQ rules 1–5 hold, run only E017-09 (2× slippage) and E983-01 (event-level diagnostic). PbNQ if rules 1–7 all pass, otherwise Rejected. STOP; no E017-10..17.
  - **Case C:** if W1, W2, W3 and R1–R4 all pass, automatically run E017-09 … E017-17 and E983-01. Apply G4′ exactly (≥ 5 of 6 perturbations keep W1; W1 at 2× slippage); 4× / 6× reported.
- **E983-01:** only under Cases B / C; report exactly the pre-declared outputs. Never used to change the threshold or holding period, add volume, redesign H017 or create H018.
- **$200K:** sensitivity only. It never selects, rescues, overrides W1–W3 or changes the classification.
- **Rolling 1/3/5/10-year reports vs SPY, with EW-H017 and the random controls (diagnostics only):**
  - share of start dates beating SPY;
  - mean and median excess CAGR;
  - 10th / 90th percentiles;
  - worst and best windows;
  - independent windows.
- **No paid data:** under PbNQ, only state that more history may be worth considering.
- **No tuning after E017-01 starts:** every listed element is immutable; no rescue variation.
- **Required: P2-CP15 — H017 Development Result and Phase 2 Final Checkpoint** (23 items).
- **STOP** after the A/B/C path; no Holdout, no tuning, no new hypothesis, no new phase, no data purchase. Wait for the owner:
  - Development Qualified → Holdout approval;
  - PbNQ → data-extension decision;
  - Rejected → close exactly as tested.
