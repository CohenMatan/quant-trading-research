# P14-CP4 — H029 Structural Turnover Post-Mortem

**Result: TURNOVER POST-MORTEM B — NULL TETHER MECHANICS PRIMARILY EXPLAIN THE TURNOVER ADEQUACY FAILURE.**

**Formal status, unchanged:**
- **H029 / H030 BLOCKED — SECTOR-STRATIFIED NULL ALSO INADEQUATE.**
- H029 and H030 are neither qualified nor rejected.
- No threshold exists. E031-10 was not run.
- The Holdout is sealed.

**Scope of this analysis:**
- Structural only: no return, wealth, capture or other performance quantity was read, derived or shown.
- No QuantConnect run. No new null. No third-null design.
- Analysis script: `research/phase14/cp4/P14_CP4_postmortem.py`. Result file: `P14_CP4_postmortem.json`.

## The magnitude in plain English

**The definition:** turnover is the number of **new** names in the month's Top-15 target list divided by 15, averaged over the 83 month-to-month transitions. Its exact formula is in item 6.

| | New names per monthly rebalance |
|---|---|
| Real H029 | **5.36** (0.3574 × 15) |
| Sector-null median | 5.60 |
| Sector-null lowest of 5,000 worlds | 5.43 |

**What the difference amounts to:**
- Compared with a typical null world, the real H029 replaces about **0.24 fewer names a month**: roughly **3 a year**, or **20 over the 83 rebalances**.
- Compared with the most persistent null world, it replaces **0.07 fewer a month** (about 1 a year).
- **In practical terms the difference is small.** It fails the rule because the null's spread is very narrow (standard deviation 0.0036, about 0.05 names a month): every one of the 5,000 null worlds trades slightly more than the real selection.

## Answers to the owner's questions

**Q1. Why does real H029 trade less than every sector-null world?**
- **Because of how the null works, not because of a special property of H029.** While a null stock keeps the same donor, the sector-stratified null is an exact relabelling of the real selection, and so trades exactly like it (proved and verified: item 26 below).
- **Where the null diverges:** about 40 stocks a month (5.3% of the eligible universe) must receive a new donor, mostly because another stock left or entered the eligible universe.
- **What the new donor does:** that stock suddenly carries an unrelated company's Business Improvement path. A real stock never does this; its own score evolves slowly between quarterly filings.
- **Size:** this alone predicts about **+0.0147** of extra null turnover (lower-bound inputs), against the observed **+0.0161** gap to the null median, i.e. about **92% of the gap**.

**Q2. Is the difference broad across time, or caused by a few months?**
- **NOT AVAILABLE FROM COMMITTED ARTIFACTS:** the runs exported only the 83-month averages.
- Structurally the mechanism acts every month: the universe changes and pairs are re-formed every month (about 40 a month on average). So a broad effect is expected, but this is not measured.

**Q3. Are H029's six fundamental signals naturally persistent from month to month?**
- **Yes.** Each signal changes in only 32–33% of stock-months, and runs of unchanged values last a median of 3 months (25th–75th percentile also 3), following the quarterly filing cycle (item 23).
- **But this persistence is not what separates real from null:** the null inherits exactly the same persistence through each persistent donor.

**Q4. Does donor rematching materially explain the failure?**
- **Yes, primarily.** The "99.85% persistence" in P14-CP3b counted only pairs whose donor was still eligible and in the same sector.
- Including the re-pairing forced by universe changes, **5.3% of recipients get a new donor every month**, not 0.15%.
- That rate is large enough to account for about 92% of the gap (items 29–31).

**Q5. Does the max-3-per-sector rule materially explain it?**
- **No.** In the sector null every recipient has its donor's sector, so the cap acts identically on the relabelled scores.
- The null therefore reproduces the real sector composition exactly: H029 sector HHI has zero spread across the 5,000 worlds, apart from tie-breaking.
- With the cap binding and no universe changes, null turnover equals real turnover exactly (synthetic verification, item 26).

**Q6. Do eligibility or missing-data changes materially explain it?**
- **Not directly.** The eligible sets and each recipient's eligibility are identical in the real and null worlds (canary: 0 changes).
- A missing-signal pattern moves with its vector, so it changes neither the eligible set nor its size.
- **Indirectly, yes:** eligibility churn is what forces the donor re-pairing in Q4. Churn is the trigger; the tether's response to it is the mechanism.

**Q7. Is the persistence economically natural for quarterly Business Improvement data, or an implementation artifact?**
- **H029's persistence is natural:** quarterly filings, with signal values unchanged for about 3 months at a time.
- **The excess turnover of the null is the artifact:** it comes from the null's re-pairing rule, not from H029's code.

**Q8. Which structural property is the current null failing to preserve?**
- **Continuity of each stock's own score path when the eligible universe changes.**
- When a stock's donor leaves (or a pairing has to be re-formed), the recipient's score jumps to an unrelated company's level. Real scores do not jump at those moments.

**Q9. Can the existing sector null now be considered adequate?**
- **NO.** The pre-registered rule is unchanged, and no bug invalidates the committed result.
- Real H029 turnover (0.3574) is still below all 5,000 worlds (minimum 0.3622).

**Q10. What owner decision is required next?** See item 50:
- close H029 / H030 as not evaluable;
- or authorise a separate, design-only owner review of a third null;
- optionally, a structural-only confirmation run.

## 1–5. Status and confirmations

| # | Item | Status |
|---|---|---|
| 1 | Current status | **H029/H030 BLOCKED — SECTOR-STRATIFIED NULL ALSO INADEQUATE** (D234), unchanged |
| 2 | Real performance | None exists. No real-mode run was ever executed (E031-05 never; E031-10 not run). |
| 3 | Holdout | Sealed. Nothing dated 2022-01-01 → 2026-08-31 was accessed: no price, fundamental, return, metadata or diagnostic. |
| 4 | No return analysis | Only the structural columns (turn29, hhi29, turn30, hhi30) were extracted from the committed null rows; the return / wealth / capture / risk columns are dropped on load (`structural_columns`). Nothing return-based was computed. |
| 5 | No third null | None was designed, implemented, simulated, calibrated, recommended or compared. Synthetic panels were used only to verify the frozen code's behaviour (item 26). |

## 6–8. Turnover definition and reproduction

**6. Definition** (`qr_h029.selection_structure`, frozen):
- S_t = the Top-15 target list at review t: `qr_h026.pick` walks the score ranking, skips full FF12 sectors (at most 3 per sector) and stocks without a valid entry open, and breaks ties by security id.
- **turnover = (1 / 83) · Σ_{t=2..84} |S_t \ S_{t−1}| / 15**, the mean share of new names per rebalance.
- **Sector HHI** = the mean over months of Σ_s (n_s / |S_t|)².
- No return enters either quantity.

**7–8. Reproduction** (committed rows; real values identical in both null runs):

| Measure | Real | Sector null: min / 0.5% / median / 99.5% / max (sd) | Real percentile (sector) | Original null median | Real percentile (original) |
|---|---|---|---|---|---|
| H029 turnover | **0.3574** | 0.3622 / 0.3655 / **0.3735** / 0.3831 / 0.3880 (0.0036) | **0.0** (0 of 5,000 at or below) | 0.3582 | 41.9 |
| H029 sector HHI | 0.1630 | 0.1628 / 0.1628 / 0.1630 / 0.1630 / 0.1631 (0.0000) | 51.1 | 0.1523 | 99.96 |
| H030 turnover | 0.3598 | 0.3454 / 0.3590 / 0.3944 / 0.4297 / 0.4434 (0.0138) | 0.68 | 0.3928 | 1.33 |
| H030 sector HHI | 0.1674 | 0.1596 / 0.1617 / 0.1669 / 0.1720 / 0.1751 (0.0020) | 60.8 | 0.1631 | 96.7 |

All P14-CP3b values reproduce exactly.

## 9–13. Month-level real and null statistics

**Items:** 9 (month-by-month real turnover), 10 (month-by-month null comparison), 11 (persistence concentration), 12 (Top-15 survival at 1–12 months), 13 (holding-spell lengths).

**Status: NOT AVAILABLE FROM COMMITTED ARTIFACTS.**
- The S031 runs export only the 83-month averages of turnover and HHI per world, plus aggregate canary counts. Under QuantConnect's compliance rule, no per-stock or per-month score list leaves the cloud.
- No quantity in these items is estimated or invented here.
- **What the structure implies:** the mechanism (items 29–31) operates at every rebalance, because the eligible universe changes at every review (about 40 re-formed pairs a month on average). A broad rather than concentrated pattern is therefore expected, but **not measured**.

## 14–15, 22, 27, 30–33. Score and rank persistence — answered by an exact identity

**Item 26 below proves:** for every recipient whose donor is unchanged between two reviews, the null score path is **exactly** the donor's real score path. The null cross-section is a permutation of the real one, so:
- null score of A at t = real score of σ_t(A);
- null rank of A at t = real rank of σ_t(A);
- this holds within sectors too, because the donor is always in the same sector.

**Consequences for the requested comparisons:**
- **14 (rank autocorrelation), 15 (raw-score persistence), 22 (composite persistence), 31 (|Δ score|), 32 (|Δ rank|), 33 (|Δ within-sector rank|):** over the transitions where a recipient keeps its donor (≈ 94.7% of recipient-transitions per review), the null distribution of these quantities is **identical by construction** to the real distribution over the matching donors. All real-vs-null differences come from the ≈ 5.3% of transitions where a pair is re-formed. There, the null score changes from one company's level to an unrelated company's, while the real score continues.
- **27 (stock-specific persistence beyond sector) and 30 (sign stability):** the same identity applies. The null preserves stock-level persistence exactly while pairs persist, and breaks it only at re-formations.
- **Numerical values** of these statistics for the real H029 (e.g. the median monthly Spearman ρ): **NOT AVAILABLE FROM COMMITTED ARTIFACTS** (per-stock scores were never exported).

## 16–21, 23–24. The six signals

**23. Update cadence** (P14-CP1 audit, E802-01: the same canonical forms on the Data v2.1 view, before the Data v3 guard; 131 reviews 2011–2021):

| Signal | Form | Stock-months with a changed value | Unchanged | Months between changes (25th / 50th / 75th percentile) | Report age in days (median / 90th percentile / maximum) |
|---|---|---|---|---|---|
| 16. F1 revenue-growth acceleration | F1-Q | 33.2% | 66.8% | 3 / 3 / 3 | 50 / 88 / 168 |
| 17. F2 gross-margin improvement | F2 | 33.0% | 67.0% | 3 / 3 / 3 | 49 / 87 / 166 |
| 18. F4 OCF / assets improvement | F4-B | 33.3% | 66.7% | 3 / 3 / 3 | 49 / 87 / 166 |
| 19. F5 ROA improvement | F5-A | 33.2% | 66.8% | 3 / 3 / 3 | 49 / 87 / 166 |
| 20. F7 share dilution | F7 | 31.7% | 68.3% | 3 / 3 / 3 | 50 / 87 / 133 |
| 21. F8 asset-turnover improvement | F8 | 33.1% | 66.9% | 3 / 3 / 3 | 50 / 87 / 166 |

**Typical update cadence:** quarterly (one new filing about every 3 months) for every signal.

**What these values can and cannot tell:**
- **The signals are naturally sticky.** Each stock's raw value is unchanged in about two thirds of month-to-month pairs. Its percentile can still move slightly as other stocks' values change.
- **Per-signal rank persistence (Spearman):** NOT AVAILABLE FROM COMMITTED ARTIFACTS.
- **Joint changes:** the fraction of stock-months in which 0, 1, …, 6 signals changed is NOT AVAILABLE (only per-signal shares were exported). Since all six signals come from the same quarterly report, the changes are expected to largely coincide, giving about two thirds of stock-months with no change at all. **This is an expectation, not a measurement.**

**22. Composite vs components:**
- The composite is the mean of up to six centred percentiles that mostly update at the same filing.
- Averaging reduces noise from any one signal. It cannot make the composite change more often than its components, which change only at filings.
- A numerical comparison is NOT AVAILABLE.

**24. Filing-driven updates:**
- Classifying monthly score changes as new filing / new share count / eligibility / sector / no underlying update is NOT AVAILABLE FROM COMMITTED ARTIFACTS: no per-stock update log was exported.
- From item 23: about one third of stock-months bring a new value for each signal. In the other two thirds, any score change comes only from other stocks' updates moving the percentiles.

## 25–28. Entries / exits, sector cap, margins, rank depth

**25. Real Top-15 entry and exit causes:** NOT AVAILABLE FROM COMMITTED ARTIFACTS (no per-stock target lists were exported).

**26. Sector-cap interaction — exact relabelling identity.**
- **Proof.** Let σ_t be the recipient→donor map at review t. It is a bijection of E29(t) that preserves sectors.
  - The null permutes whole six-signal vectors, so every column keeps its multiset of values. Each vector keeps its centred percentiles and its H029 score.
  - Hence null score(A) = real score(σ_t(A)). Since sector(A) = sector(σ_t(A)), the frozen `pick` with its max-3-per-sector rule selects **S′_t = σ_t⁻¹(S_t)**. The only exceptions are score ties broken by recipient id and a recipient without a valid entry open.
  - If σ_t = σ_{t−1} for the stocks involved, |S′_t \ S′_{t−1}| = |S_t \ S_{t−1}|.
  - **Therefore the sector cap acts identically in the real and null worlds.** The cap cannot create the turnover gap, and the null sector HHI equals the real one up to ties: observed spread 0.1628–0.1631 around the real 0.1630.
- **Verified with the frozen `qr_h029` / `qr_h026` code on synthetic panels** (no market data):
  - With tie-free scores and no universe change, null turnover and HHI equal the real values in **every** world, both with unclustered scores and with sector-clustered scores where the cap binds.
  - With churn (18 exits / 22 entries a month), HHI stays identical and turnover rises.
- **Per-month counts of cap-displaced names:** NOT AVAILABLE FROM COMMITTED ARTIFACTS. By the identity they would be identical in the real and null worlds wherever pairs persist.

**27. Score margin near the cutoff** (ranks 15–20): NOT AVAILABLE FROM COMMITTED ARTIFACTS. By the identity, the null's margins in a given month are the real margins with the stocks relabelled.

**28. Next-month rank depth** (remained / 16–20 / 21–30 / below 30 / ineligible): NOT AVAILABLE FROM COMMITTED ARTIFACTS. By the identity, a null holding keeps the real rank path of its donor while its pair persists. A null holding falls out more often than a real one only when its pair is re-formed.

## 29–32. Donor persistence — the central finding

**29. Donor persistence, verified and expanded** (canary E031-06, seeds 1 and 2; the eligibility path is identical in every world):

| Per seed, reviews 2–84 | Count | Per review |
|---|---|---|
| Recipient-months | 63,595 | 766 |
| Previous donor still eligible and in the same sector ("possible", the canary metric) | 60,327 | 727 |
| … kept | 60,236 (99.85% of possible) | 726 |
| … broken by the tether's no-self-match splice | 91 | 1.1 |
| **Not possible: re-formed by eligibility entry / exit or a sector change** | **3,268** | **39.4** |
| **All re-formed pairs** | **3,359 (5.28% of recipient-months)** | **40.5** |

**Correction to how P14-CP3b's 99.85% could be read:**
- That figure is the share of *possible* pairs kept. Its denominator excludes, by the amendment's definition, the pairs that had to be re-formed because a stock entered or left the universe or changed sector.
- **The overall re-pairing rate is 5.3% of recipients per month, not 0.15%.**
- This is not a code defect: the canary metric is exactly as specified in Amendment 1 section A5.

**30. Donor-rematch causes:**
- The causes of the 39.4 per review cannot be split exactly from the committed counts (per-month entries and exits were not exported).
- What the counts do pin down:
  - net universe growth is +3.65 a review, so entries − exits = 3.65;
  - entries + (old recipients whose donor exited or crossed sectors) = 39.4;
  - with no sector changes, that gives about **21.5 entries** and **17.9 exits** a review;
  - each exit forces one existing recipient to take a new donor, and frees one donor vector to a new carrier;
  - sector changes, if any, would shift count from exits to sector-change re-pairings without lowering the 17.9 disrupted old pairs (a lower bound).
- Splices: 1.1 a review.

**31. Explanatory power of donor rematching:**
- **Exact decomposition** (follows from item 26; verified on synthetic panels with `exact_identity_holds = true` for every month and seed):
  - null new names − real new names = Σ over target names B ∈ S_t whose recipient pair was re-formed of (1[recipient not in S′_{t−1}] − 1[B not in S_{t−1}]);
  - kept pairs contribute exactly zero;
  - in the synthetic decomposition, essentially **all** of the extra entries come from donors freed because their previous recipient left the universe (seeds 1–3: freed donors +24 / +20 / +20, new-entrant donors −1 / 0 / 0, other re-formed pairs 0 / +1 / +1; totals 23 / 21 / 21).
- **Size on the real data** (descriptive estimate from committed counts):
  - extra turnover ≈ mean_t f · (p − 15/n_t) / n_t, where:
    - f = 17.9 disrupted old pairs a review (lower bound);
    - p = 1 − 0.3574 = 0.643 (a lower bound on the chance that a real Top-15 name was also in last month's list);
    - n_t = the eligible count, 616–1,001 (mean 765);
  - result: **+0.0147**, against the observed gap to the null median of **+0.0161**, i.e. **≈ 92%**.
- **The same formula on synthetic panels** (frozen pick, 20 worlds each) tracks the simulated gap:

| Exits / entries per month | Quarterly persistence | Estimate | Simulated median gap | Real below all 20 worlds |
|---|---|---|---|---|
| 9 / 11 | 0.90 | 0.0088 | 0.0084 | yes |
| 18 / 22 | 0.90 | 0.0160 | 0.0145 | yes |
| 36 / 40 | 0.90 | 0.0295 | 0.0313 | yes |
| 18 / 22 | 0.70 | 0.0135 | 0.0096 | yes |
| 18 / 22 | 0.97 | 0.0177 | 0.0181 | yes |

- **Every month with a re-formed pair can contribute.** On average about 40 pairs a month are re-formed, so in the synthetic checks (constant churn) every month was exposed. A per-month count for the real panel is NOT AVAILABLE.

**32. Same-donor score persistence:** the score path of a null recipient that keeps its donor is **identical** to the donor's real score path (item 26). This is not an estimate. The null loses persistence only at re-pairings.

## 33–40. Remaining comparisons

**33. Stock-specific persistence beyond sector:** preserved exactly by the null while pairs persist (item 26). Real-data rank statistics are NOT AVAILABLE.

**34. Eligibility contribution:**
- Recipient eligibility, eligible sets and their sizes are identical in the real and null worlds (canary: 0 changes).
- The share of real Top-15 turnover forced directly by eligibility exits is NOT AVAILABLE.
- In the null, eligibility churn works through the tether: each exit breaks one pair and frees one donor (item 31), which the real world does not experience.

**35. Missing-feature contribution:**
- The missing pattern moves with the vector, so the at-least-5-of-6 rule gives every recipient a valid score in every world (canary: eligibility changes 0).
- Missingness cannot change E29(t). It can change percentile denominators only identically in the real and null worlds, because each column keeps its multiset.
- Per-stock missingness transitions: NOT AVAILABLE.

**36. Signal-sign stability:** identical between the real and null worlds for kept pairs (item 26). Real-data values are NOT AVAILABLE.

**37–39. Score-, rank- and within-sector rank-change magnitudes:** identical distributions over kept pairs (item 26). At re-formed pairs, the null jumps to an unrelated same-sector company's level. Real-data values are NOT AVAILABLE.

**40. H030 blending** (structure only):
- **The H030 null is not a relabelling.** H030_null(A) = 0.5 · centred(real H028 of A) + 0.5 · centred(H029 of σ(A)). Each world therefore pairs A's own H028 score with another company's H029 score, so the selections differ widely between worlds. The null turnover spread is about 4× wider (sd 0.0138 vs 0.0036).
- **The re-pairing shock is halved.** It affects only the H029 half of the score, and the H028 half stays continuous for every stock.
- **The real H030 is on the same side of the null.** It sits at the 0.68th percentile (0.3598 vs median 0.3944): low, but inside the [0.5%, 99.5%] range.
- **Synthetic illustration** (same mechanism, synthetic H028-like score):
  - H029-style: real 3.9 null-sd below the null median, below all worlds;
  - H030-style blend: 0.6 null-sd below, at the 30th percentile.
- **Conclusion:** H030 passes the turnover rule because blending with the continuous H028 score dilutes the shock and widens the null's spread. The direction of the effect is the same as for H029.

## 41–42. Classification and attribution

**41. Dominant mechanism: B — DONOR-REMATCH MECHANICS.**
- The persistent tether is re-formed for about 5.3% of recipients every month, almost entirely because of eligibility churn.
- At each re-formation the null breaks the continuity of a stock's score path, which the real data never does.
- This is enough to explain about 92% of the gap.
- **Elements of the other categories:**
  - **A, real persistence:** a necessary condition. Re-pairing costs turnover only because real scores are persistent, but the null carries that persistence wherever pairs persist.
  - **D, eligibility:** the trigger for the re-pairing.
  - **C, sector cap and ranking:** ruled out by the identity.

**42. DESCRIPTIVE ATTRIBUTION — NOT CAUSAL** (shares of the 0.0161 gap to the null median):

| Mechanism | Share |
|---|---|
| Re-pairing at universe churn (donor exits / entries) | **≈ 92%** (lower-bound estimate) |
| Tether splices (1.1 a review) | small; not separately estimated |
| Sector changes | unknown (counts not exported); included in the re-pairing total |
| Sector cap / ranking mechanics | **0** (identical in the real and null worlds by construction) |
| Score ties (id tie-break) and recipient entry-open availability | small; this is where the residual null HHI spread comes from; not quantified |
| Feature persistence in itself | 0 directly (carried by the null); it is what makes each re-pairing costly |
| Residual / estimation error | ≈ 8% |

## 43. What any future null would have to preserve (conceptual only; no design)

Any future valid null would need to preserve:
- **each stock's FF12 sector structure at every review**, as the sector-stratified null already does;
- **the continuity of each stock's score path through changes in the eligible universe:** a stock's assigned score must not jump to an unrelated company's level merely because some other stock entered or left;
- **the quarterly update cadence** of the six signals, so values change about every three months, at filings;
- **the eligible-universe path and missing patterns**, unchanged.

The real selection's month-to-month persistence then follows from these.

## 44. Q1–Q10

Answered at the top of this report.

## 45. Artifact limitations

**What the committed artifacts contain:**
- per-world 83-month averages of turnover and HHI;
- aggregate canary counts;
- per-review eligible counts;
- per-signal update-cadence aggregates from P14-CP1.

**What they do not contain:** per-month or per-stock scores, ranks, target lists, entries / exits, cap displacements, rematch causes or joint signal changes. These were not exported (QuantConnect's compliance rule allows only aggregates and digests).

**Items marked NOT AVAILABLE:** 9–15 (numerical values), 16–21 (rank persistence), 18 (joint changes), 19 (filing classification), 20, 21 (cap counts), 22 (numerical comparison), 25, 27, 28, the numerical parts of 30–39, and the per-month split of 31.

**What the conclusion rests on:**
- the exact identity, proved and verified on the frozen code;
- the committed tether counts;
- the descriptive size estimate.

**Optional structural-only confirmation run (proposed, NOT executed, needs owner approval):**
- an S031 mode that exports per-review aggregates only: the real and null new-name counts for a few seeds, and the item-31 decomposition split by kept / re-formed pairs and by cause;
- no returns, no thresholds, no new null.
- It would confirm the ~92% figure month by month. It is not needed for the classification, which follows from the identity.

## 46. Bug status

**No bug found** in the H029 score, Top-15 construction, sector null, turnover calculation or donor mapping:
- the null behaves exactly as Amendment 1 specifies;
- the turnover is computed as defined;
- the canary persistence metric is as specified (denominator = possible pairs).

The only clarification concerns the **reading** of P14-CP3b's 99.85%, which excludes eligibility-driven re-pairing (item 29). The committed result stands.

## 47–49. Confirmations

| # | Item | Status |
|---|---|---|
| 47 | Thresholds | `C_UP_H029 = None`, `C_INCREMENTAL_H030 = None`, `THRESHOLD_COMMIT = None` (test-checked) |
| 48 | E031-10 | Not run; no config exists |
| 49 | H029 / H030 | Neither qualified nor rejected |

## 50. Exact next owner decision

H029 / H030 remain **BLOCKED**. Choose one:

1. **Close H029 / H030 as not evaluable** under the pre-registered adequacy standard.
2. **Authorise a separate, design-only owner review of a third null** that preserves the properties in item 43. No design is proposed here. Any such null would again be calibrated without any real return, and would need its own canary, 5,000 worlds and the unchanged adequacy rule.
3. **Optionally first:** the structural-only confirmation run (item 45).

**Recommendation:** the evidence shows the failure is a property of the null's re-pairing mechanics at universe churn, not of H029's signal or code. That makes option 2 scientifically reasonable. Option 1 remains defensible if the owner prefers to limit further methodological forks after two null amendments.

**STOP.** No null #3, no thresholds, no H029 / H030 run, no Holdout, no H031.
