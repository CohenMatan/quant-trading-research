# RR3 — Universe Baseline Audit UB-1 (E804-01): can QuantConnect's current data support a trustworthy ≥ $2B universe?

**Date:** 2026-10-20.
**Decisions:**
- D263: owner direction, verbatim in `docs/owner/2026-10-20_rr2_controlled_approval_universe_baseline.md`.
- D264: this result.

**Status:** **STOPPED awaiting the owner.**

**Not done:**
- No strategy, return, SEC fallback (U-C) or D033 / D035 amendment.
- No Holdout data (the run ended 2021-12-31).
- No purchase. No retry used.

**Programme totals:** 30 hypothesis IDs; 30 research strategy folders; 415 experiment IDs (582 run records), including E804-01.

## 0. Result

| Window | Frozen outcome | Meaning |
|---|---|---|
| **W1 2010-01 … 2021-11** | **PASS-A** | QuantConnect's own market cap (no repair) passes the frozen coverage and survivorship gates in every year. There are **two disclosed blind spots** (§4); survivorship in 2021 could not be assessed (censoring) |
| **W0 1999-02 … 2009-12** | **FAIL** | QuantConnect has market caps before late 2009 for only 4–37 liquid US common stocks a month, all survivors; the U-B rebuild failed its validity tests |

**Consequences:**
- A QuantConnect universe with the approved rules is usable for **2010–2021**, under the stated limits. That is the period already examined heavily.
- **No 1999–2009 confirmation window exists on QuantConnect**, so no D033 / D035 amendment is proposed.
- U-B (shares × price × split factor) is **not valid** and must not be used.

## 1. What was run

- **Protocol:** `research/rr/universe_baseline/UB_protocol.md`, frozen and SHA-256-pinned (d5ce14e2…) together with the host, `qr_ub` and the evaluation rule, in commit 0f11c81, before the run.
- **Run E804-01:** X804 v1.0, LEAN **18194** (QuantConnect default build, recorded), 1999-01-04 … 2021-12-31.
  - Runtime 257 s, 0 orders, 23,876 securities seen.
  - 274 month-end audit points (1999-02 … 2021-11).
  - 627,225 liquid stock-months classified.
  - All integrity checks pass.
  - Accepted by QuantConnect's compliance review.
- **Output:** aggregates only (counts, rates, quantiles, bootstrap intervals, digests).
  - Monthly-count digest d0c2f430… serves as the future platform canary reference.
  - Stored in `experiments/E804-01/result.json`. The 26 `UB|` lines are extracted to `research/rr/universe_baseline/E804-01_ub_lines.txt`: the runner's `messages.txt` keeps only `QR` lines (a recording detail, D264).
- **Evaluation:** `research/rr/universe_baseline/UB_eval.py` (pinned), result in `UB_result_E804-01.json`.

## 2. W1 2010–2021: coverage and survivorship (view A, vendor market cap)

"Gap" is liquid US common stocks with no vendor market cap that are at least as liquid as the bottom 10% of eligible names. They are counted as if they were ≥ $2B, which makes it an upper bound.
- b is how much those excluded names raise the universe's later (24-month) exit rate.
- d is the difference between their exit rate and the eligible names' rate.
- Intervals are 95% security-cluster bootstrap intervals.

| Year | Eligible / month (min–max) | Gap_A (gate ≤ 3%) | b point | b upper (gate ≤ 0.50 points) | Excluded exit rate − eligible (d) |
|---|---|---|---|---|---|
| 2010 | 714–835 | 2.15% | −0.09 | −0.05 | −4.4 points |
| 2011 | 768–893 | 1.81% | −0.04 | +0.05 | −2.1 |
| 2012 | 840–895 | 1.74% | +0.09 | **+0.34** | +5.3 [−3.0, +21.7] |
| 2013 | 921–1,093 | 1.49% | +0.01 | +0.16 | +0.8 |
| 2014 | 1,082–1,175 | 1.28% | −0.08 | −0.04 | −6.2 |
| 2015 | 1,108–1,200 | 1.20% | −0.08 | −0.04 | −7.0 |
| 2016 | 1,076–1,212 | 0.67% | −0.04 | −0.01 | −6.1 |
| 2017 | 1,214–1,285 | 0.59% | −0.04 | −0.02 | −6.7 |
| 2018 | 1,217–1,368 | 0.48% | +0.04 | +0.15 | +7.3 [−6.3, +29.4] |
| 2019 | 1,261–1,358 | 0.35% | +0.09 | +0.25 | **+25.1** [−4.7, +66.7] |
| 2020 (12-month horizon; gate ≤ 0.25) | 1,105–1,492 | 0.56% | +0.03 | +0.12 | +6.7 |
| 2021 | 1,520–1,681 | 0.67% | — | **not assessable** | — |

**Reading:**
- The missing-cap residue is small: 55–200 stock-months a year against 9,000–18,000 eligible.
- Its bias bound on the universe's exit rate is at most 0.34 points (2012).
- It is **not proven unbiased**. In 2012 and 2018–2020 the excluded names exit more often than eligible ones (2019: +25 points, on 11 securities). The effect is bounded only because the residue is tiny.

**The data changed since 10 October.**
- Eligible stock-months 2011–2017:

  | Source | Stock-months |
  |---|---|
  | Data v1 (old dataset, with SEC repairs) | 93,687 |
  | Build 18178, 10 October (D187) | 76,915 |
  | **This run, build 18194** | **88,773** |

- The October gap of about 18% is largely closed on today's data. This is our own measurement, not a documented change.
- It also shows the snapshot keeps moving. Any strategy run must re-check the digest (§6).

## 3. W0 1999–2009: why it fails

| Item | Finding |
|---|---|
| Vendor market cap | 4–37 liquid US common names a month until 2008 (7 in 1999); it begins in earnest only in late 2009 (2009: 29 → 723). This is our P2-CP11 finding (R4), now confirmed on the current data |
| Who has it | **survivors only**: the vendor-cap names of 1999–2007 have **0 exits** within 24 months, against 2–7% for the rest |
| Missing-cap names | 7,000–17,800 stock-months a year (≈ 99% of the liquid common set) |
| U-B rebuild | covers 98.5% of them (shares present), giving 430–840 eligible names a month and passing the plausibility and dead-company tests. But U-B **fails validity**: V1a only 8–47% of vendor-cap names within 2% before 2009; V2b insufficient; V3 lead share 9% in W0 (22 of 234) and **21% in W1** (853 of 4,095), meaning the share count moves before the vendor's point-in-time cap; V1b threshold agreement < 99% in most years |
| Outcome | U-B is not valid → best view is A → gap 47–99% a year → **FAIL** |

**U-B is not valid in W1 either.**
- V1a is 82–86% (gate 95%) and V3 lead is 21%.
- The restated share counts disagree with the vendor's point-in-time cap too often, and change too early.
- U-B must not repair any universe, and **its rebuilt 1999–2009 universe must not be used**.

## 4. Limits of the W1 pass (disclosed, not resolved)

1. **Names with no fundamentals object (N_x).**
   - 7,500–10,500 liquid stock-months a year that never carry fundamentals in the run.
   - Mostly ETFs, ADRs and funds, but they cannot be classified in-run, and none was ever structural common (N_c = 0).
   - Their 24-month exit rate (8–11%) is above the eligible names' (3–8%).
   - Any ≥ $2B US common stock hidden among them is an **unmeasured** gap.
   - On build 18178 (D187), "no fundamentals object" accounted for 42–445 data-v1 member stock-reviews a year. Today's figure is unknown.
2. **Names whose classification fields are blank** fail the structural-common test and are counted as non-common (46,693 liquid stock-months over the run, ≈ 170 a month). They include genuine ADRs, funds and partnerships, but also any common stock whose fields are missing.
3. **No dated overrides** were applied (keyed by old identifiers, D257): 12 securities.
4. **Survivorship in 2021 is not assessable.** 2020 rests on a 12-month horizon.
5. **This is evidence for one data snapshot.** Exact reproduction holds only within a snapshot (RR1 R5–R6).

Limits 1 and 2 could only be measured with an external source (SEC) or the old membership lists. The first is the SEC fallback, which is not authorised; the second cannot be reused (D257).

## 5. Answers to D263's required items

| Required | Answer |
|---|---|
| Delisting rates missing vs observed, comparable windows | Yes: 24-month exits on assessable months, the same horizon for both groups (§2, `exit_rates`) |
| Censoring, no Holdout follow-up | Follow-up ends at the run's last selection (2021-12-01); 2020 on 12 months, 2021 unassessable |
| Securities and stock-months | Both reported per group and year (UB lines; security-level Wilson intervals) |
| Yearly coverage, magnitude and uncertainty | §2 table; bootstrap intervals for b and d |
| Shares available at each decision date | Read from the stream at the decision date (V5: present for 98.5% of W0 / 15% of W1 missing-cap names). But V3 shows they **move before** the vendor's cap in 21% of changes: not reliable as point-in-time values |
| Split consistency shares vs prices | V2a: restated behaviour in 93% of W0 / 94.5% of W1 split events (consistent) |
| Vendor agreement ≠ PIT validity | Kept separate: U-B fails even vendor agreement (V1a), so no PIT claim is made |
| Not "unbiased" from a low rate alone | W1 passes on upper bounds, not significance; skew among the few excluded names is shown, plus two unmeasured blind spots (§4) |

## 6. Recommendation (owner decision)

1. **Accept W1 = PASS-A as the universe basis for 2010–2021**: vendor market cap, no repair, the approved filters, with §4's limits stated in every future report.
   - Include the monthly-count digest d0c2f430… as a cheap re-check whenever the default build or dataset changes. It is one aggregate run, and the next strategy host can carry the check itself.
2. **Record that QuantConnect offers no reliable 1999–2009 universe.**
   - Confirmation can therefore rest only on the sealed Holdout (once) and forward tracking.
   - No D033 / D035 amendment.
3. **Retire U-B.**
4. **Leave limit §4.1 open unless you decide otherwise.** Measuring it needs either the SEC fallback (U-C) or an owner-accepted residual.
5. **Next step, if you agree:** prepare the frozen candidate-screen / confirmation rules (D263 item 1) and the K1 / K2 feasibility demonstrations (D263 item 4). These are documentation and offline only; no strategy run.
