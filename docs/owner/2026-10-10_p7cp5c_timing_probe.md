# Owner message 2026-10-10: "Phase 7 — Option C, Step 1 Only. P7-CP5c — QuantConnect New Dataset Fundamental-Timing Probe. Infrastructure Investigation Only — No H022 Evaluation"

Recorded summary (the full message is in the session transcript). Decision id: **D184**.

- **Approved:** option C, step 1 only — determine whether QuantConnect's new default Morningstar dataset (or an independently verifiable point-in-time source) can supply the date each fundamental report became public. Answer YES / PARTIAL / NO; never force a positive answer.
- **Principle:** a value may be used at t only if it was demonstrably public before t. No replacement assumption (e.g. period end + delay) unless independently justified, conservative and later approved by the owner. Investigate only; no production timing rule changes.
- **Scope of the probe (28 items):**
  - inspect the new schema systematically (all timing-like fields, nested objects, period windows);
  - old-vs-new comparison on a deterministic sample chosen before results (categories in item 8);
  - SEC EDGAR as the independent truth (filing date, form, period, CIK);
  - earnings-release vs filing semantics;
  - value checks (not only dates);
  - vendor semantics;
  - truncation, restatement, revision and determinism tests;
  - SEC-replacement feasibility (coverage, CIK mapping, successors, cost, runtime, rate limits, storage, reproducibility);
  - revenue True-TTM feasibility;
  - the restatement-vintage stop condition;
  - estimated-date fallback analysis;
  - coverage per method;
  - a method comparison table;
  - data-v2 implications.
- **Frozen and untouched:**
  - Score v1 and all its parts, H1–H7, mechanics, the H022 response / horizon / gates / null / α;
  - c_IC = 2.390976216956 (preserved, never used on the new dataset).
- **Not authorised:**
  - any real return, IC, quintile, 80+ excess, H022 gate, CAGR, wealth, SPY comparison, Sharpe, drawdown or portfolio;
  - Data Infrastructure v2 implementation;
  - a P7-CP3R re-run, H022 canary, null or c_IC;
  - 2018–2021 inspection for research (schema mechanics only if unavoidable, pre-2018 preferred);
  - the Holdout;
  - any purchase.
- **Records:** every run records the LEAN build actually used. The old research record (E993-02, P7-CP3R, P7-CP4, P7-CP5a, the old null worlds, the old c_IC) stays a valid record of data infrastructure v1 / LEAN 18131.
- **Deliverable:** P7-CP5c — New Dataset Fundamental-Timing Probe (38 items), with GO or NO-GO and the next owner decision. Then STOP.
