# Owner message 2026-10-10: "Phase 7 — P7-CP5d Score v1 Migration Feasibility on the New QuantConnect / Morningstar Data. In-Cloud PIT Validation Only — No H022, No Predictive Returns"

Recorded summary (the full message is in the session transcript). Decision id: **D186**.

- H022 is NOT closed. One final, materially different path is to be investigated:
  - run the exact frozen Score v1 on QuantConnect's new feed;
  - use the historical stream itself ("first seen in backtest time") as availability, instead of the vendor FileDate;
  - optionally gate it with the SEC filing date.
- **Score v1 and all mechanics are unchanged.** This checkpoint concerns the data-delivery layer only.
- **Required work:**
  - a complete Score v1 dependency map with migration classes A–G;
  - an in-cloud first-seen ledger prototype (values stay inside QuantConnect; only aggregates / digests leave);
  - truncation and determinism invariance;
  - restatement-vintage invariance against SEC-known restatements (aggregate match categories only);
  - first-seen vs SEC filing date by form and by 2009–2012 vs 2013–2017;
  - early cases vs earnings releases;
  - candidate architectures M1 (first seen), M2 (max(first seen, SEC filing + 1)) and M3 (hybrid; assess only);
  - coverage, H2 and score distributions (no returns);
  - universe migration and market-cap PIT safety;
  - programme-wide export feasibility (a harmless synthetic test).
- **Rules:**
  - deterministic samples frozen before results;
  - no raw vendor-data export;
  - respect every QuantConnect restriction — a rejected validation path is recorded as NOT VERIFIABLE, never worked around;
  - no loosening of PIT rules to raise coverage;
  - no future returns, IC, gates, CAGR or SPY comparison;
  - no 2018–2021; no Holdout; no purchase or upgrade.
- **Records preserved:**
  - Data v1 / LEAN 18131 (E993-02, P7-CP3R, P7-CP4, P7-CP5a/b/c, the old null worlds, c_IC = 2.390976216956) is preserved;
  - the old c_IC is never used on a new panel;
  - any migrated research is "Data Infrastructure v2".
- **Verdict:** GO only if all nine conditions hold; otherwise NO-GO with the failed requirement named.
- **After the verdict:**
  - if GO: provide the exact Data v2 specification, do not build or freeze it, and STOP;
  - if NO-GO: no Score redesign, no SEC-only move, no Score v2; STOP.
- **Deliverable:** P7-CP5d — Score v1 Migration Feasibility on New QuantConnect Data (47 items), then STOP.
