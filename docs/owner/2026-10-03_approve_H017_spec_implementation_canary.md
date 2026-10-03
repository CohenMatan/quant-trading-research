# Owner message 2026-10-03: "Phase 2 — Approve H017 Specification, Authorise Implementation + Canary Only"

This is a recorded summary; the full message is in the session transcript.

- **State that must remain:**
  - H014 rejected; H016 rejected and preserved exactly as tested;
  - Phase 2 slots: 2 of 3 consumed; slot 3 unused;
  - Holdout locked;
  - Amendment 3 frozen; Event Data v1 frozen;
  - no additional data purchase.
- **H017 specification approved exactly as proposed** in `research/hypotheses/H017.md`:
  - signal: two-session SPY-adjusted reaction AR = [Close(E+1)/Close(E−1) − 1] − [SPY Close(E+1)/SPY Close(E−1) − 1];
  - threshold: AR ≥ the trailing 252-session 90th percentile AND AR > 0;
  - timing: entry at the open of E+2; holding exactly 60 trading sessions;
  - exit: the fixed holding-period exit plus the existing forced integrity exits;
  - no volume filter, no technical filters (RSI, moving averages, momentum, 52-week rules), no stops or targets, no alternative reaction definitions, holding periods or thresholds.
- **Events:** Event Data v1 exactly (SEC acceptance timestamp; BMO / during / AMC rules; foreign private issuers excluded; ambiguous, contradicted or unverified mappings excluded; frozen predecessor linking; 30-day de-duplication; amendments ignored; no inferred dates).
- **Portfolio:**
  - $100K primary, $200K sensitivity; at most 10 positions;
  - target 0.98/10 of current equity (≈ $9,800); maximum position weight 10%; $4,000 reference minimum;
  - settled cash only, 2% buffer, 15% gap reserve; no top-up; no leverage.
- **Capacity:** rank by AR (highest first, ties by security id); fill only free slots; drop the excess; never queue; never replace early. Later events of a held stock are ignored.
- **Controls:**
  - SPY;
  - EW-H017 (same-universe equal weight);
  - random-event books, seeds 1–5: identical timing, sizing, holding, costs, cash, opportunity dates and daily k_t capacity; deterministic hash rule; not averaged; W3 uses the median CAGR;
  - canary seed 0.
- **E983-01 event-level diagnostic:** approved as a diagnostic only, used only within the PbNQ rule; it must not qualify, alter or select anything.
- **PbNQ rule approved exactly** (all must hold):
  1. W1 passes;
  2. excess CAGR ≥ +1.0 point a year;
  3. g/SE ≥ 1.0 while full W2 at 2.15 fails;
  4. W3 passes;
  5. R1–R4 pass;
  6. W1 passes at 2× slippage;
  7. the event-level top-decile mean excess is > 0, with clustered t ≥ 2.0, and exceeds the mean of deciles 2–9.

  PbNQ means NO Holdout, NO production, NO declaration of success.
- **Decision tree frozen:**
  - Case A (failure): reject; no tuning; no data purchase;
  - Case B (PbNQ): frozen; Holdout locked; stop; option to buy data to re-test the same strategy;
  - Case C (qualified incl. G4′): freeze; stop; request Holdout approval.
- **Robustness (pre-declared; not run now):** P1 40-session hold; P2 80-session hold; P3 top quintile; P4 one-session reaction; P5 8 slots; P6 12 slots; 2× / 4× / 6× slippage.
- **Authorised now:**
  1. implement the event table;
  2. hash-pin / freeze it;
  3. implement `qr_h017`;
  4. implement S017;
  5. candidate / random / EW modes through one shared code path;
  6. all required tests;
  7. evaluation scripts;
  8. all run configs;
  9. run the infrastructure canary E982-01 only;
  10. verify the canary requirements offline.

  E983-01 may be prepared, but not executed if it computes post-event returns.
- **Required canary checks:**
  - event integrity: table hash, time-zone rules, de-duplication, amendments excluded, foreign filers excluded, predecessor mapping valid, no event after 2021-12-31;
  - PIT / leakage: AR uses only information available by the close of E+1; the trailing threshold uses only earlier decision sessions; future events cannot change past signals; no Holdout data in thresholds or warm-up;
  - execution: every entry at the open of E+2 (never earlier); normal exits exactly 60 sessions later;
  - portfolio: at most 10 holdings; no leverage; no negative cash; correct sizing; $7 per order; 10 bps slippage; no top-ups; no queued signals; no early replacement; held-stock events ignored;
  - controls: the seed-0 canary uses the same mechanics; random and candidate differ only in selection; same shared code path.
- **Do NOT run:** E017-01 (it consumes slot 3; a separate approval is required), E017-02, E017-03..07, E017-08, E983-01 (if it computes event returns), E017-09..17.
- **Required checkpoint:** "P2-CP14 — H017 Implementation and Canary Readiness Checkpoint", 20 items, ending with "READY FOR E017-01" or "NOT READY".
- **STOP** after implementation and the E982-01 validation: no E017-01, slot 3 not consumed, no candidate performance, no Holdout access, no data purchase; wait for explicit approval.
