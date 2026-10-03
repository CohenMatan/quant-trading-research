# Owner message 2026-10-02 (received 2026-10-03): "Approve Amendment 3 With Two Refinements, Preserve Slot 3, and Proceed With Preparatory Studies Only"

This is a recorded summary; the full message is in the session transcript.

- **State to keep:**
  - H014 and H016 rejected (H016 preserved as tested);
  - Phase 2: 2 of 3 slots used; slot 3 unused;
  - H017 Value only a proposal; no candidate authorised;
  - Holdout 2022-01-01 → 2026-08-31 locked;
  - data infrastructure v1 frozen unless a separately approved extension creates a new version.

1. **Objective approved:** starting with the same capital on the same date, terminal wealth above S&P 500 buy-and-hold total return after realistic costs, without leverage.
   - $100K primary; $200K sensitivity only.
   - Every candidate report begins with the terminal-wealth table (starting capital, final values, total returns, CAGRs, excess CAGR, terminal wealth ratio).
   - The strategy need not beat SPY every year or every window.
2. **Amendment 3 approved conceptually.** Keep W1, W2, W3, R1–R4, G4′, Holdout/forward confirmation and rolling reporting. The +0.25 Sharpe-over-EW hurdle is retired as a hard gate and kept as a diagnostic.
3. **Refinement 1 (R2):** do not require Sharpe(H) ≥ Sharpe(SPY) exactly.
   - Example that must not fail on Sharpe alone: SPY 10.5% CAGR / 0.80 Sharpe / −35% MaxDD vs strategy 13.5% / 0.77 / −39%.
   - Use a small pre-declared tolerance derived from sampling uncertainty, control books, the objective and false-positive behaviour (or a better justified safeguard). Never chosen from candidate results.
   - Frozen before any hypothesis is selected or run.
4. **Refinement 2 (W2):** do not assume independent annual observations.
   - Test block bootstrap / HAC / another serial-correlation-aware method, preferably consistent with the Phase 2 block bootstrap.
   - Account for serial correlation, overlapping holdings, persistence and finite samples, at about 5% one-sided false-positive protection. Not more permissive because power is low.
   - Report the false-pass rate, the pass probability at +1/2/3/4%, and the edges for 50% / 80% power.
5. **Freeze Amendment 3 after both refinements:**
   - W1 CAGR > SPY;
   - W2 the final method;
   - W3 beats same-universe EW and the median of five random books (CAGR);
   - R1–R4; G4′.

   Nothing changes after a candidate result.
6. **Rolling 1/3/5/10-year windows are reporting only:**
   - statistics: share beating SPY, mean, median, p10, p90, worst and best;
   - always shown against the EW and five random books;
   - 10-year windows from a 12-year sample are not independent evidence.
7. **Preserve slot 3.** No H017 Value run, no earnings-event run.
8. **Preparatory Study A:** historical data-extension options toward about 2000–2021.
   - Requirements: shares / market cap, dead companies, identifiers, corporate actions, point-in-time, licence, Python, integration.
   - Per-provider table: start, coverage, dead companies, shares, market cap, fundamentals, events, point-in-time, survivorship, format, QuantConnect compatibility, licence, price, effort, risks.
   - Compare with the EDGAR reconstruction (time, identity mapping, extraction errors, audit, maintenance).
   - No purchase.
9. **Preparatory Study B:** the SEC earnings-event audit for 2010–2021, with no post-event returns:
   - coverage by year and by continuing / acquired / delisted / bankrupt;
   - timing classes (BMO / during / AMC / unknown) and the earliest legal execution;
   - duplicates and amendments, with deterministic de-duplication;
   - missing events (no invented dates);
   - point-in-time identifier mapping;
   - canaries: not visible before acceptance; no same-day trades after the close; amendments do not modify signals; no duplicate opportunities.
10. **Do not define the earnings strategy yet:** no thresholds, Top X%, holdings, holding period, stops, ranking or entry delay.
11. **Account model unchanged for now** (the $4,000 minimum is a reference only, not inherited automatically). Propose it per family later.
12. **Relative-strength swing dropped.**
13. **Candidate families remain open** (earnings-event continuation, value; net issuance only if point-in-time-safe). Not ranked by strategy returns.
14. **Deliverable:** P2-CP12, "Amendment 3 Freeze, Data Extension Options, and Earnings Event Data Audit" (21 items).

**STOP CONDITION:**
- no H017 or earnings strategy;
- no candidates;
- no factor or post-earnings returns;
- no optimisation;
- no Holdout;
- no slot 3;
- no purchase.

Methodology freezing, control-book calibration, metadata, SEC audit, data-option research, tests and infrastructure-only audit code are allowed. Commit and STOP.
