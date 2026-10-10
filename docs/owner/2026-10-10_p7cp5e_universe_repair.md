# Owner message 2026-10-10: "Phase 7 — P7-CP5e Universe Repair Feasibility Study. Infrastructure Only — No H022, No Returns, No Score Changes"

Recorded summary (the full message is in the session transcript). Decision id: **D188**.

- **Owner chose option (b) of P7-CP5d:** a universe-repair feasibility study only. H022 is not closed; Data Infrastructure v2 is not built.
- **Two questions only:**
  - **A.** Can PIT market cap be reconstructed for the securities whose QuantConnect market cap is missing, as SEC point-in-time shares outstanding × historical raw price, without look-ahead, survivorship bias or split errors?
  - **B.** Can a reliable dated CIK identity be established before each company's first XBRL filing, so that M2 works in 2011–2012? If not, quantify a 2013 start, but return that decision to the owner.
- **Frozen:**
  - Score v1 (all features, weights, thresholds, H1–H7, mechanics);
  - M2 timing (max(first seen, SEC original filing + 1 day));
  - the conceptual universe (US common, NYSE/Nasdaq, PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M).
- **Required work:**
  - freeze the target population before any repair result;
  - SEC shares source and timing (measurement vs publication date), split and issuance handling;
  - threshold sensitivity bands;
  - classification agreement vs QuantConnect market cap where both exist (aggregates only);
  - a shadow repaired universe (QuantConnect market cap if present, else SEC-repaired, else ineligible);
  - the survivorship re-test;
  - success criteria defined before results;
  - identity evidence per row (SAFE / SAFE WITH BOUNDED START / AMBIGUOUS / REJECT; no blind backdating);
  - M2 coverage before and after identity repair;
  - 2011, 2012 and 2013+ populations;
  - a 2013-start power implication (synthetic only);
  - compliance and file-budget assessment.
- **Rules:**
  - no future returns, IC, gates, CAGR, Sharpe or SPY comparison;
  - 0 orders;
  - no 2018–2021, no Holdout;
  - no null worlds, no new threshold; the old c_IC is never used on a new panel;
  - vendor data stays in QuantConnect, aggregates only;
  - no workaround of compliance controls;
  - nothing purchased or upgraded;
  - all earlier records preserved.
- **Verdict:**
  - GO (universe repairable PIT-safely; Data v2 design can proceed);
  - PARTIAL (market-cap repair works; owner must choose A = keep repairing identity, or B = 2013 start);
  - NO-GO.
- **Deliverable:** P7-CP5e — Universe Repair Feasibility Study (51 items), then STOP.
