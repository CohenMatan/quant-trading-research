# Owner message 2026-10-02: "Phase 2 — Approve Final Fundamental Data Policies, Complete 2011 Cleanup, Then Design H016 Only"

This is a recorded summary; the full message is in the session transcript.

**Approved:** the P2-CP7 checkpoint and its verdict. The data infrastructure is safe enough to begin **designing** H016; H016 must not be backtested yet.

**Order of work:**
1. Complete the 2011 SEC cleanup.
2. Freeze the fundamental-data infrastructure.
3. Prepare an H016 pre-registration proposal only.
4. STOP.

## Owner decisions

1. **H016:** design-only work is approved. Not authorised:
   - implementation;
   - candidate or control runs;
   - factor-return analysis;
   - parameter comparison.

   H016 becomes Phase 2 hypothesis #2 only on explicit approval of its final pre-registration.
2. **Universe:** candidate, benchmark and all controls use exactly the same universe. It must be:
   - eligible under the point-in-time rules;
   - non-financial and non-REIT under the approved historical classification;
   - only companies for which **every field required by H016** is safely available on that date.

   Yearly coverage and missing-data bias continue to be reported. The strategy never gets a cleaner universe than its benchmark or controls.
3. **Warm-up approved:** history-only warm-up from July 2008, used only to initialise state. Not allowed:
   - performance before 2010;
   - parameter selection, hypothesis evaluation or ranking from 2008–2009.

   **Tests must prove that warm-up data cannot influence reported development performance before the official start.**
4. **Approved fields (frozen):**
   - True TTM revenue, gross profit, net income and operating cash flow;
   - total assets, shareholders' equity, market cap.

   Not allowed: operating income, free cash flow, EPS, unsafe share fields, vendor ratios, and anything off the whitelist. No field may be added to improve historical results.
5. **Exclusions approved:** banks and conventional financial institutions, health insurers, REITs, real-estate services, exchanges, brokers and asset managers. They are identified from historical SEC evidence, never present-day vendor metadata, and apply equally to candidate, EW benchmark and controls. All exception logic is documented.
6. **2011 cleanup approved:** one targeted SEC verification pass over the 135 held-back reports.
   - Release only verified quarterly income-statement figures, and only where SEC evidence confirms all of these:
     - the value was available at the historical date;
     - it is the original figure;
     - no later restatement is introduced;
     - the mismatched balance sheet cannot contaminate the released flow fields.
   - **Never release a whole report because one part is verified.** Use field-level availability rather than weakening the PIT rule.
   - Rerun the coverage and PIT audits afterwards.
7. **Residual ~1% survivorship gap accepted, conditionally.** The conditions:
   - the 2011 cleanup uncovers no broader problem;
   - unresolved names stay documented;
   - yearly missingness and bias continue to be reported;
   - candidate, benchmark and controls share the dataset;
   - no identity patch is ever made because of strategy performance.

   Never present the gap as zero or random. **If the 2011 work materially changes the residual-bias assessment, stop before H016 design.**
8. **Freeze after the cleanup** — with a version or hash for exact reproducibility:
   - identity mappings, correction table, Visa correction, repair layer and priority rules;
   - timing rules, the +90 fallback and 200-day freshness;
   - restatement blocking and quarantine/release rules;
   - True TTM, the field whitelist/blacklist and the financial/REIT rules.

   No changes based on H016 results. A genuine bug means: stop, document it, and ask before rerunning anything.
9. **H016 direction:** a simple Profitability/Quality hypothesis built on one primary, externally supported profitability concept. No multi-factor composite.
10. **No search for the best ratio:** never compute 2010–2021 performance of ROA, ROE, gross, operating or cash-flow profitability or composites to choose among them. The metric is chosen from external evidence, rationale and field compatibility, before any return calculation.
11. **Literature review** of:
    - gross profitability;
    - profitability factors;
    - quality;
    - cash-flow quality;
    - asset and equity denominators;
    - long-only large-cap implementation;
    - post-publication persistence;
    - costs;
    - sector comparability.

    Pre-2010 evidence, later replication, practitioner convention and our own hypotheses are kept distinct. Our 2010–2021 returns are never used.
12. **The proposal defines in advance:**
    - the measure, formula, denominator and negative/zero handling;
    - freshness, ranking, selection count and weighting;
    - rebalance frequency and holding behaviour;
    - missing values, benchmark and controls;
    - expected turnover, costs and concentration.

    No unnecessary timing rules; a low rebalance frequency matched to information arrival.
13. **Portfolio:**
    - $100K primary, with $200K as a sensitivity only;
    - long-only, no leverage, options or intraday trading;
    - realistic costs.

    Whether 12–15 positions or a broader portfolio is right must be decided on principle, never by return optimisation.
14. **Controls:** at minimum an EW benchmark on the exact H016 universe, SPY, and a random-stock control using the same universe and mechanics. Any further control must isolate the profitability ranking without changing several things at once.
15. **Phase 2 methodology unchanged:**
    - 2010–2021 development;
    - Holdout locked;
    - 3 hypotheses, of which H014 consumed 1 and H015 none (2 remain);
    - margin of EW Sharpe +0.25;
    - G1–G4 in force;
    - DSR and PBO diagnostic only.
16. **Deliverables:**
    - **A. Final 2011 Data Cleanup:**
      - records verified, fields/reports released, and records still quarantined;
      - coverage, bias, tests and canaries;
      - freeze confirmation.

      **Stop if the data verdict changes materially.**
    - **B. H016 Pre-Registration Proposal (17 items):**
      - hypothesis, rationale, literature and the single measure;
      - formula, universe, portfolio, rebalance, turnover/costs and controls;
      - candidate count, statistical feasibility and relationship to earlier work;
      - overfitting risks, run count, runtime/cost and the decisions needed.

**STOP CONDITION:**
- No H016 implementation and no H016 or control runs.
- No candidate or factor returns.
- No performance comparison of metrics.
- No slot consumed.
- No Holdout access.

Then wait for explicit approval.
