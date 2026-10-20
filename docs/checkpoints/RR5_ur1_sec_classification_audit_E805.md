# RR5 — UR-1 SEC classification audit (E805-02): is the universe credible enough to start K1?

**Date:** 2026-10-20.
**Decisions:**
- D267: owner, verbatim in `docs/owner/2026-10-20_rr4_review_decisions.md`.
- D268: this result.

**Status:** **STOPPED awaiting the owner.**

**Not done:**
- No strategy run or return, no repair (U-C), no change to any universe.
- No Holdout data (the run ends 2021-12-31). No purchase.
- No H031 registration or canary. Options B, C and D were not taken.

**Programme totals:** 30 hypothesis IDs; 30 research strategy folders; 417 experiment IDs (584 run records), including E805-01 and E805-02.

## 0. Answer

| Window | Frozen outcome | Meaning |
|---|---|---|
| **W1 2010-01 … 2021-11** | **FAIL** | In 2010–2015 public SEC data shows ≥ $2B US common stocks that QuantConnect's vendor universe misses: **3.7–6.1% of stock-months a year**, above the 3% gate. They leave the market far more often than included names (24-month exit rate +7 to +21 points), so survivorship bias exceeds the 0.50-point gate in 2011, 2012, 2014 and 2015 |
| W1a 2011–2021 (reported) | FAIL | The same years fail |
| W1b 2016–2021 (reported) | **INCONCLUSIVE** | The confirmed gap is 0.8–2.9% a year (inside 3%) and the confirmed survivorship bias is 0.16–0.36 points (inside the gate). But possible and unresolved names take the gap to 4.7–8.2%, and with the possible names the bias point estimate is 0.50–0.75 points (2016–2019) |

**Is the universe credible enough to start K1? No — not under the approved rules without a further owner decision (§5).**
- The vendor-market-cap universe is shown to be **survivorship-biased in 2010–2015**.
- It is **not shown to be acceptably bounded in 2016–2021**.
- Under D267 neither result may be accepted automatically. H031 is therefore **not** presented for approval (§7).

## 1. What ran

- **Frozen first** (commit c350dfc, before any upload or run):
  - the protocol `research/rr/sec_classification/SCA_protocol.md`;
  - host X805, module `qr_sca`, SEC builder and evaluation rule;
  - pins (`qresearch.rr_sca`);
  - the SEC object's SHA-256 (67bc9260…).
- **SEC reference:** `rr/sca_sec_v1.json`, 4.79 MB of public SEC EDGAR data only:
  - 3,999 registrants with ticker evidence, cover shares and public float, dated by filing date;
  - no QuantConnect identifier.
  - Uploaded once to the Object Store (owner-approved).
- **E805-01: documented infrastructure failure.** The backtest started 29 s after the upload and could not see the object; 26 s, nothing processed. Record: `research/rr/sec_classification/E805-01_failure.md`.
- **E805-02, the single permitted retry:** identical code and object, started 33 minutes later.
  - Completed: LEAN 18194, 155 s, 0 orders, 143 month-end points, 1,075,939 security rows classified in-cloud.
  - QuantConnect's compliance review accepted it.
  - Aggregates only.
- **Evaluation:** `SCA_eval.py` → `SCA_result_E805-02.json`. The offline re-application of the frozen rule agrees with every in-run verdict.

## 2. Results (stock-months; C = confirmed missing, P = possible missing, U = unresolved)

| Year | E (vendor-eligible) | C | P | U | Gap_C (gate 3%) | Gap_C+P | Gap_max | Survivorship b_C, points [95%] | Exit-rate gap of C vs E | Reach | Agreement | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2010 | 9,158 | 337 | 592 | 46 | **3.5%** | 9.2% | 9.6% | 0.25 [0.00, 0.56] | +6.9 | 79% | 99.5% | FAIL |
| 2011 | 10,183 | 590 | 873 | 104 | **5.5%** | 12.6% | 13.3% | **0.64** [0.28, 1.12] | +11.7 | 93% | 99.3% | FAIL |
| 2012 | 10,451 | 675 | 653 | 221 | **6.1%** | 11.3% | 12.9% | **0.63** [0.23, 1.08] | +10.3 | 94% | 99.5% | FAIL |
| 2013 | 12,158 | 542 | 837 | 162 | **4.3%** | 10.2% | 11.2% | 0.34 [0.07, 0.67] | +7.9 | 95% | 99.4% | FAIL |
| 2014 | 13,676 | 577 | 863 | 220 | **4.0%** | 9.5% | 10.8% | **0.68** [0.35, 1.06] | +16.8 | 95% | 99.5% | FAIL |
| 2015 | 14,140 | 540 | 713 | 282 | **3.7%** | 8.1% | 9.8% | **0.78** [0.43, 1.20] | +21.1 | 94% | 99.5% | FAIL |
| 2016 | 13,924 | 417 | 499 | 325 | 2.9% | 6.2% | 8.2% | 0.32 [0.09, 0.60] | +11.1 | 95% | 99.4% | INCONCLUSIVE |
| 2017 | 15,124 | 349 | 487 | 342 | 2.3% | 5.2% | 7.2% | 0.22 [0.00, 0.48] | +9.8 | 94% | 99.4% | INCONCLUSIVE |
| 2018 | 15,856 | 341 | 455 | 378 | 2.1% | 4.8% | 6.9% | 0.34 [0.10, 0.62] | +16.1 | 94% | 99.5% | INCONCLUSIVE |
| 2019 | 15,855 | 264 | 331 | 390 | 1.6% | 3.6% | 5.8% | 0.36 [0.13, 0.63] | +20.5 | 93% | 99.7% | INCONCLUSIVE |
| 2020 (12-month horizon; gate 0.25) | 15,785 | 199 | 256 | 401 | 1.2% | 2.8% | 5.1% | 0.16 [0.03, 0.34] | +12.1 | 92% | 99.6% | INCONCLUSIVE |
| 2021 | 18,202 | 140 | 327 | 429 | 0.8% | 2.5% | 4.7% | not assessable | — | 89% | 99.7% | INCONCLUSIVE |

**Distinct securities:**
- confirmed 22–95 a year;
- possible 57–154;
- unresolved registrants 11–83.

## 3. What the numbers mean

1. **The SEC measuring instrument works.**
   - Among vendor-eligible stocks matched by ticker, the SEC cap (cover shares × price) is ≥ $2B in 99.3–99.7% of cases, and within 5% of the vendor's cap in 96–98%.
   - 89–95% of vendor-eligible stock-months are matched to an SEC registrant (79% in 2010, the XBRL phase-in year that W1a was added for).
2. **The confirmed missing names are mostly securities with no fundamentals object at all (N):**
   - 280–514 stock-months a year in 2010–2015, falling to 60–283 later.
   - The rest are names with blank or non-common classification fields (B): 18–103 a year, the main group from 2017.
   - Only 0–83 are names whose vendor market cap is missing (M), the only group RR3 could measure.
3. **They are survivorship-relevant.** Their 24-month exit rate is 7–21 points above that of the included names.
4. **RR4's offline estimate is confirmed.** RR4 §2.2 put the gap at 5.5 / 5.1 / 4.7 / 4.4 / 3.5% (2011–2015) if the 18178 no-fundamentals group were still missing. The audit measures 5.5 / 6.1 / 4.3 / 4.0 / 3.7%.
5. **From 2016 the confirmed gap is inside the gate, but the bound is not.**
   - Possible names (SEC cap ≥ $2B but float below $2B, missing, or outside the identity band) add 2–3 points.
   - Unresolved registrants (public float ≥ $2B, no QuantConnect match) add another 2–3 points, and grow over time (46 → 429 a year).
   - Following the rule, unresolved names are **not** read as missing, but they cannot be ruled out either.

## 4. Disclosures

- **Snapshot.** The vendor-eligible counts are 0.8–1.6% higher than E804-01's from the same morning (+77 … +292 stock-months a year): the data snapshot moved within the day (a known quirk). Reported only.
- **Other exchanges.** 15–120 stock-months a year are strong SEC ≥ $2B registrants whose QuantConnect exchange code is present but outside {NYS, NYSE, NAS, ASE, AMEX}. They are classified as legitimately excluded, as frozen. It is possible some of them are NYSE / Nasdaq listings under a different code; this was **not** investigated.
- **Builder defect caught before the freeze.** The investment-vehicle filter would have dropped REITs named "… Trust" (SIC 6798); a unit test caught it and it was fixed before c350dfc.
  - The Phase 2 residual audit (`research/phase2/sec/residual_audit.py`, D113) used the same rule. Its historical counts may slightly understate missing REITs. Frozen history, not changed.
- **Lower bounds.** Registrants below a $0.5B float, multi-class registrants without one cover-share count, and non-XBRL filers are outside the SEC list. C and P are lower bounds.
- **Object Store quirk.** An object uploaded through the API was not visible to a backtest started 29 s later, but was visible 33 minutes later. The organisation's usage counter did not reflect the upload for at least 30 minutes.

## 5. Owner decision UR-2: what to do about the universe (nothing is done automatically)

| Option | What | Cost | Expected result |
|---|---|---|---|
| **A (recommended)** | **Narrow SEC-cap inclusion (U-C, scoped):** add to the universe, in-cloud and point-in-time, the liquid names this audit identifies as confirmed or possible missing with an SEC cap ≥ $2B (the audit's frozen ticker / fingerprint matching, the D111 cover-share method), using the same Object Store JSON. Then one re-audit with the frozen SCA-1 rules | about 2–3 sessions, 1 re-audit run (+ ≤ 1 retry), $0 | Removes most of C and P. U (2–3%) remains, so 2016–2021 may still be INCONCLUSIVE and need an explicit owner acceptance of the unresolved residual. Foundational: every later RR hypothesis uses the same universe |
| B | Develop on **2016-01 → 2021-12 only** with an **owner exception** for the INCONCLUSIVE residual (confirmed gap ≤ 2.9%, confirmed bias ≤ 0.36 points; with possible names up to 0.75 points) | none | 6 years: the edge needed for a 50% development pass is roughly 9% a year. A known, disclosed bias remains |
| C | Pause the price-first programme; revisit D123 (licensed point-in-time data, RR1 Option 3) | separate decision | — |
| D | Accept the vendor universe for 2010–2021 as is | none | **Not recommended**: the audit FAILS 2010–2015 under the frozen rule |

**Why A:**
- The audit shows the missing names can be identified from public SEC data with 99%+ agreement on known cases.
- Without them, 2010–2015 is biased and 2016–2021 alone is underpowered.

**Caveats:**
- A is a universe repair (U-C), which D267 excluded from this step, so it needs your explicit approval.
- It uses ticker evidence that is about 99% reliable, so a small mismatch risk remains.

## 6. Screen and confirmation rules: corrected, ready to freeze

`research/rr/programme/RR_screen_confirmation_PROPOSED.md` v2 applies D267:
- **A:** the Holdout is for at most **one** candidate across the whole programme, on separate written approval.
- **B:** every report states that D1 / D2 are exposed-data results, not independent significance or investable alpha, and that Holm does not erase the 30-hypothesis history. A trial-history ledger is required.
- **Run budget, closed list per hypothesis:**
  - canary C, primary R1, determinism rerun R1d, 20 bps R2 (P5 and G4′'s 2× slippage), $200K R3;
  - G4′ perturbations G1–G6 only on separate approval;
  - at most one infrastructure retry;
  - nothing implicit.
- It will be frozen (renamed and hash-pinned) on your confirmation, before any strategy return.

## 7. K1 / H031

- A frozen-ready specification is drafted (`research/rr/h031/H031_spec_DRAFT.md`). It covers every item D267 listed:
  - initiation and ≥ 25% regular-increase definitions;
  - ex-date availability and next-open execution;
  - special, spin-off and cadence exclusions;
  - total-return handling;
  - a fixed 126-session hold;
  - 15 slots, queue and tie-break;
  - event-matched unchanged-dividend controls;
  - costs ≈ 0.8% a year;
  - an aggregate-only event canary;
  - stopping conditions.
- **It is not presented for approval**, because the universe did not pass (D267: present only if the universe passes). No hypothesis ID is registered, and no canary or strategy run is requested.

## 8. Decisions requested

1. **UR-2:** A (recommended), B, C or D (§5).
2. Confirm the corrected screen / confirmation protocol v2 for freezing (§6), or ask for changes.
3. After the universe is resolved: H031 approval (§7) and its event canary.
