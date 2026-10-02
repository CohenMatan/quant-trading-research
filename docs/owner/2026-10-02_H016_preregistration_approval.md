# Owner message 2026-10-02: "Approve H016 Pre-Registration and Authorize Development Execution"

This is a recorded summary; the full message is in the session transcript.

## Approved

1. **Measure:** Gross Profitability = True TTM gross profit / latest historically available total assets. It is the only H016 candidate:
   - no cash flow/assets in parallel;
   - no alternative formula after results.
2. **Portfolio:**
   - 20 positions, equal weighting;
   - $100K primary, $200K sensitivity only;
   - long-only, no leverage;
   - **minimum new position $5,000 → $4,500 for H016 only**, without rewriting earlier experiments.
3. **Formation:** the first portfolio forms on the first trading day of March 2010. Before that the warm-up may run, the account stays in cash, and no selection or performance exists.
   - **Common evaluation start** = the first H016 investable portfolio date.
   - Start and end dates are identical for H016, the same-universe EW, the random controls and every directly comparable control; SPY may be reported from the same date.
4. **Rebalancing:** quarterly, on the first trading day of March, June, September and December.
   - Steps: universe → GP/A → rank → top 20 → equal weight.
   - No intra-quarter exits for profitability, price or technical reasons; normal forced exits under the existing infrastructure apply.
5. **Holding horizon:** months, possibly over a year. Holdings are not force-sold after a year (Phase 2 scope updated for H016).
6. **Primary benchmark:** EW of the exact same H016 universe (eligibility, exclusions, data constraints, survivorship layer, date range). The broad EW is a reference only; SPY is the passive reference.
7. **Controls:** the same-universe EW, SPY, and **5 frozen random seeds**.
   - The random books use the same universe, 20 stocks, equal weights, schedule, account size, costs and forced-exit rules.
   - Only the ranking differs.
   - The seeds are frozen before candidate execution.
8. **G2:** report all five random results individually. The gate baseline is the **median Sharpe** of the five; return streams are never averaged; dispersion is kept.
9. **Survivorship caveat corrected.** Same-universe use substantially reduces comparability bias, but the remaining non-random missingness may still influence the measured profitability premium. Coverage, missing counts and bias characteristics continue to be reported.
10. **One pre-declared survivorship sensitivity diagnostic.**
    - It may use only information from the completed data audit; no invented fundamentals; not chosen after results.
    - It is frozen before the first candidate run. Diagnostic only.
11. **Data infrastructure v1** is used exactly as frozen and identically for every book. If the fingerprint changes, stop. A genuine bug means: stop, document, preserve the affected runs, request approval.
12. **G1–G4 unchanged** except the approved H016 benchmark and control definitions.
    - Primary requirement: Sharpe(H016) ≥ Sharpe(same-universe EW) + 0.25.
    - The SPY comparison and the G1 return/risk items are retained; so are consistency, robustness, 2× slippage and the cost limit.
    - DSR and PBO are diagnostic. Thresholds are never weakened.
13. **Candidate count:** one; no alternatives of any kind.
14. **$200K:** sensitivity only. It never decides, changes N or the formula, or rescues a $100K failure.
15. **Prerequisites before the candidate backtest:**
    - freeze the spec;
    - implement S016, the same-universe benchmark, the five random controls and the sensitivity diagnostic;
    - add tests;
    - **verify the $4,500 minimum-position rule**;
    - verify the March 2010 common start;
    - verify PIT quarterly ranking, and True TTM and assets timing;
    - verify no Holdout access;
    - run a non-candidate canary that does not reveal candidate performance.

    **If any prerequisite fails, stop rather than bypass it.**
16. **Runs authorised** if every prerequisite and the canary pass:
    - 1 canary;
    - 8 committed runs;
    - up to 9 conditional robustness runs, only on the approved trigger.

    Nothing else. The first candidate backtest consumes Phase 2 slot 2.
17. **Development checkpoint:** 23 items, with the classes profitable / benchmark-beating / random-control-beating / development-qualified. Stop afterwards; ask before any Holdout.
