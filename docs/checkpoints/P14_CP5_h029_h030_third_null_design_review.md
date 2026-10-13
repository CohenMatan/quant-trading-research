# P14-CP5 — H029 / H030 Third Null Design Review (design only)

**Result: THIRD NULL DESIGN REVIEW — ONE SCIENTIFICALLY PREFERRED DESIGN IDENTIFIED — AWAITING OWNER APPROVAL.**

**Recommended design:** "Event-Copy Relay" (family B, in a replacement form rather than the additive form). Each stock owns its null Business Improvement vector. That vector is rewritten only at the stock's **own** information events (filing update, entry, sector change), using a same-sector, same-review vector of another company chosen by rank-coupling. Between its own events, the stock keeps its copy, so no other stock's entry or exit can move it.

**Formal status, unchanged:**
- H029 / H030 BLOCKED, neither qualified nor rejected.
- No real performance exists. No threshold exists.
- The Holdout is sealed.

**Nothing was implemented or run:** no code, no canary, no null world, no QuantConnect run, no return of any kind (item 45).

---

## Answers to the owner's questions

**Q1. What must Null #3 preserve that Null #2 failed to preserve?**
- **The coupling between a name and its own signal path.** In the real data, when a company leaves the universe, its name and its Business Improvement path end together; the path of a company that stays is never disturbed by someone else's exit.
- **Null #2 broke this coupling.** Each stock *pointed* to a living donor and read that donor's current vector every month. When a donor exited, the recipient jumped to a new company's level. When a recipient exited, its donor's path had to move to a new name.
- **Null #3 must make every stock's null path end only when that stock leaves, and change only when that stock itself has new information.**

**Q2. Which designs were considered?**
- A, eligibility-spell / trajectory permutation;
- B1, additive innovation;
- **B2, Event-Copy Relay** (the replacement form of family B);
- C, whole-path identity permutation;
- D, block / segment permutation;
- E, Null #2 with level-matched rematching (the one additional candidate, which follows directly from the CP4 mechanism).

**Q3. Which are invalid, and why?**
- **A** assigns each spell a donor that covers it. This requires knowing when donors and recipients will leave the universe, and those exits are largely price-driven (market cap < $2B, acquisitions), so it conditions the null on future return-related events.
- **B1** adds one company's change to another company's level. That is mathematically invalid for bounded, heterogeneous ratios, it keeps the recipient's own starting level, and it drifts.
- **C** needs groups of stocks with identical eligibility and sector histories. Most such groups are singletons, and conditioning on the full future eligibility path partly conditions on the outcome.
- **D** adds a block-length tuning parameter (a new research fork), creates artificial joins at block boundaries, and does not cure churn.
- **E** keeps the pointer mechanism. Freed vectors still move to new names, so the CP4 artifact remains.
- **Common root (proved in section 9):** any rule that, at every review, hands each stock *some other company's current vector* through a fresh one-to-one assignment, without knowing the future, must create these artificial transfers.

**Q4. Which single design is recommended?** **B2, the Event-Copy Relay** (item 38).

**Q5. At what level should randomization occur?**
- **The whole pre-percentile six-signal vector** (F1, F2, F4, F5, F7, F8 values including the missing pattern), i.e. option A in its signal-level sense.
- The frozen `h029_score` then recomputes the percentiles on the null cross-section every month, exactly as for the real data.
- Matching uses only the *rank* of the final composite score, as a structural coupling key.

**Q6. How does it survive stocks entering or leaving without artificial jumps?**
- **Copy semantics:** a stock's null vector is a copy taken at its own last event, not a link to a living donor.
- **Lemma:** a stock that stays eligible, stays in the same sector and has no information update keeps exactly the same null vector, whatever any other stock does (section 18, with proof).
- **No transfers:** when a stock leaves, its null path simply ends, like the real path.

**Q7. How does it handle sector changes?**
- A sector change is one of the stock's own events.
- At that review, the stock receives a vector from its **new** sector. The donor is chosen by rank-matching to the stock's previous null score, so the level continues as closely as the new sector allows.
- There is never a cross-sector assignment at any review (section 21).

**Q8. Does it preserve quarterly persistence without preserving company-specific information?**
- **Yes.**
  - **Timing:** a null vector changes exactly when the stock's real vector changes (same months, same cadence).
  - **Size of changes:** at each event the stock takes the new vector of the company whose *real* previous rank matches the stock's *null* previous rank. The real "previous rank → new vector" pattern is therefore reproduced exactly among the stocks with events in that sector and month.
- **No own data:** a stock never receives its own data. Only timing and rank dynamics are kept, never content.

**Q9. Which structural adequacy tests must it pass before any threshold?** (item 32)
- **Unchanged:** the existing H029 / H030 sector-HHI and turnover gates.
- **New:** two persistence gates on stocks eligible in both months (within-sector rank autocorrelation; Top-15 survival).
- **Pre-checks:** exact-by-construction checks of cadence, continuity, sector and identity, plus a constructibility audit.
- **One owner decision is needed here:** total turnover is partly driven by price-driven entries and exits that no valid null can reproduce. A one-off structural pre-check (no returns) should decide, before any null world, whether total turnover stays a gate.

**Q10. What approval would implementation need?** The six explicit owner approvals listed in item 44.

---

## 1–3. Status

| # | Item | Status |
|---|---|---|
| 1 | Current status | **H029 / H030 BLOCKED** (D234, D235), unchanged |
| 2 | Real performance | None exists. E031-05 and E031-10 were never run. `C_UP_H029` = `C_INCREMENTAL_H030` = `None`. |
| 3 | Holdout | Sealed. Nothing dated 2022-01-01 → 2026-08-31 was accessed. |

## 4–6. Why the first two nulls failed

**4. Null #1 (any-sector tether):**
- Donors came from any sector. Business Improvement clusters by sector, so null selections were more sector-diversified than the real one.
- Real H029 sector HHI was 0.1630 against a null 99.5th percentile of 0.1599 (2 of 5,000 worlds).

**5. Null #2 (same-sector tether):**
- Sector structure was fixed exactly: the null became a relabelling of the real selection.
- But real H029 turnover (0.3574) was below all 5,000 worlds (minimum 0.3622).

**6. P14-CP4 finding:**
- While a donor pair persists, Null #2 reproduces the real path exactly.
- About 5.3% of recipients (about 40 a review) are re-paired every month because of universe churn. At each re-pairing a recipient inherits an unrelated company's path, and a freed persistent vector moves to a new name.
- This alone predicts about 92% of the turnover gap.

## 7–8. Objective and formal null hypothesis

**7. Objective:**
- Destroy the link "company i's Business Improvement information → company i's future return".
- Keep everything about the signal that is not predictive skill:
  - the sector environment;
  - the calendar;
  - the eligibility path;
  - the filing cadence;
  - the joint structure of the six signals;
  - the missingness;
  - the persistence dynamics.

**8. Formal null hypothesis (for the recommended design)**

> **H0 (Null #3):** Conditional on
> - **(X)** every stock's own path of H029 eligibility, FF12 sector and information-update timing (the reviews at which its six-signal vector changes);
> - **(Y)** the realised pool, at each review and in each sector, of Business Improvement vectors released by the stocks that have an information event at that review; and
> - **(Z)** the realised within-sector rank-transition dynamics of the H029 score (the joint distribution of a company's previous rank and its newly released vector among same-sector, same-review event stocks),
>
> the assignment of Business Improvement vector paths to companies is exchangeable, and contains no company-specific information about that company's future returns.

## 9. The central tension, and why it forces the design

**Proposition (no online point-in-time bijection avoids artificial transfers).** Consider any null that:
- **(i)** is *online*: the assignment at review t uses only information available at t;
- **(ii)** at every review gives each eligible stock the *current* real vector of a *different* same-sector stock, through a one-to-one map of the eligible set onto itself (an exact cross-section every month); and
- **(iii)** keeps every stock's real eligibility path.

Then, whenever a stock x leaves while its donor d stays, d's continuing vector path must be handed to a different name at the next review. This is an artificial change of ownership that the real data never shows. Its expected cost is about (exits per review) × P(d is held) × P(d would have stayed held), which is the CP4 term.

**Sketch:**
- At t, d ∈ E(t) and the map is onto, so some recipient y must carry d's vector. y ≠ x, because x has left.
- If d's vector is in the Top-15, y enters the null Top-15 although nothing changed for d in the real data.
- Symmetrically, when a donor leaves while its recipient stays, the recipient must switch to another company's level.

**The only escape inside (i)–(iii)** is for every donor and its recipient to leave at the same time. An online rule cannot guarantee this. An offline rule can only arrange it by conditioning on future exit dates, and exits are largely price-driven (market cap falling below $2B, price below $5, acquisitions). That would build return-related future information into the null.

**Consequence:**
- A valid null must relax (ii): it must not insist that every stock reads a living donor's *current* vector every month.
- The recommended relaxation is **copy semantics**. Each stock holds a *copy* of a vector, taken at its own last information event, exactly as each real stock holds its own last-filed vector.
- The exact one-to-one assignment is kept only where it is natural: among the vectors *released* at each review. Exactness is given up only for held, stale copies (item 25).

## 10–14. Candidates

**10. Candidate A — eligibility-spell / trajectory permutation**
- **Mechanics:** each recipient spell (a run of eligible months in one sector) receives one donor whose own eligible, same-sector spell covers it; the donor's path is carried through the whole spell.
- **Constructibility:**
  - Covering donors must exist for every spell. Long spells can only take long-lived donors.
  - An exact one-to-one assignment month by month is generally impossible (proposition above). So donors must be reused, which creates duplicates and over-represents long-lived donors.
  - Exact spell matching (same start and end) leaves mostly singleton groups. About 21.5 entries and 17.9 exits a review are spread over 11 sectors and many end dates.
- **Properties:**
  - Calendar and sector are preserved. There is no reset inside a spell.
  - The cross-section is distorted, and the missingness of donor spells must match.
- **Decisive weakness:** the assignment uses each recipient's and donor's *future* exit date.
  - Recipients that will soon leave (often because their price is falling) can take any covering donor; recipients that will stay need long-lived donors.
  - A recipient's null score distribution therefore depends on its future eligibility, and so partly on its future price path.
  - **Rejected** (rejection criterion: uses future information).

**11. Candidate B — update-event / innovation permutation**
- **B1, additive innovation:** null_i(t) = null_i(t−1) + a same-sector random change taken from another updating company.
  - The six signals are heterogeneous, bounded or ratio-based values (revenue acceleration, gross-margin change, OCF / assets change, ROA change, share dilution, asset-turnover change), and they are already *differences*. Adding another company's change produces values with no economic meaning, unbounded drift and accumulating scale errors.
  - It also starts from the recipient's **own** real level, so part of its own signal is kept. That over-conditions the null.
  - Doing it on percentiles instead breaks the percentile grid, because percentiles are relative to a month's cross-section.
  - **Rejected.**
- **B2, Event-Copy Relay (replacement, not addition)** — **recommended** (item 38).
  - At each of a stock's own information events, its null vector is *replaced* by the newly released vector of another same-sector company with an event at the same review.
  - Donors and recipients are coupled by rank: recipient's null previous rank ↔ donor's real previous rank.
  - Between events the copy is held.

**12. Candidate C — whole-path identity permutation**
- **Mechanics:** permute entire company histories among companies with identical eligibility and sector histories.
- **Problems:**
  - It is the cleanest null in principle. But exact matching groups are almost all singletons at this level of churn. That forces self-assignment (the stock keeps its own signal) or non-constructibility.
  - The groups are defined by the full future eligibility path, which is price-driven, so the null partly conditions on the outcome. It would keep real signal content inside groups such as "companies that will fall below $2B in 2016-03".
- **Rejected** (non-constructible; conditions on future information; risks conditioning away the signal).

**13. Candidate D — block / segment permutation**
- **Same-calendar blocks:** donors are re-drawn every L months. This is Null #2 with *extra*, scheduled re-pairings, so it adds artificial joins at every block boundary and still breaks at churn.
- **Time-shifted blocks:** this violates R2, because a 2019 filing would be treated as known in 2015.
- **Block length L:** a new free parameter with no structural anchor. Choosing it after two failures is a research fork.
- **Rejected.**

**14. Additional candidate E — level-matched re-pairing tether (Null #2 plus level matching at forced re-pairings)**
- **Why it is distinct:** it attacks the CP4 discontinuity directly. When a pair must be re-formed, the recipient takes the free donor whose current level is closest to its lost donor's.
- **Why it fails:**
  - Only about 3–4 free donors a sector a review, so matches are poor near the Top-15 cutoff (top ≈ 2% of the cross-section).
  - It keeps pointer semantics, so a freed persistent vector still moves to a new name (the proposition).
- **Rejected:** repeated artificial resets remain.

## 15. Comparison matrix

| Candidate | Breaks identity ↔ return | Calendar month | FF12 sector | Recipient eligibility | Quarterly cadence | Score continuity | Within-sector cross-section | Missing-data semantics | Artificial reset at churn | Tuning parameter | Constructible on Data v3 | 5,000 worlds feasible | Main scientific weakness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A spell permutation | YES | YES | YES | YES | YES | YES within spells | NO (reuse, long-donor tilt) | APPROXIMATE | NO | NO | UNCERTAIN | YES | Uses future exit dates (price-driven) |
| B1 additive innovation | NO (keeps own starting level) | YES | YES | YES | YES | YES | NO (drift) | NO | NO | YES (scaling / bounds) | UNCERTAIN | YES | Invalid arithmetic on bounded ratios |
| **B2 Event-Copy Relay** | **YES** | **YES** | **YES** (at every assignment) | **YES (exact)** | **YES (exact timing)** | **YES at churn**; APPROXIMATE across filings (rank-coupled) | **APPROXIMATE** (released vectors exact; held copies approximate) | **YES** | **NO** | **NO** | **UNCERTAIN until the single-event audit** (fallback pre-defined) | **YES** | Held-copy cross-section approximate; total turnover confounded by price-driven exits (shared by any valid null) |
| C whole-path permutation | YES within groups | YES | Only with identical sector histories | YES | YES | YES | YES within groups | YES | NO | NO | NO (singleton groups) | YES | Conditions on future eligibility; non-constructible |
| D block permutation | YES | NO if shifted; YES if same-calendar | YES | YES | APPROXIMATE | NO (block joins) | YES (same-calendar) | YES | YES | YES (block length) | YES | YES | New tuning fork; resets |
| E level-matched tether | YES | YES | YES | YES | YES | APPROXIMATE (small free pool) | YES (exact) | YES | YES (vector transfers remain) | NO | YES | YES | Keeps the CP4 mechanism |

## 16–17. Over- and under-conditioning

**16. Over-conditioning (could the null keep the signal it should randomize?)**
- **A:** yes — future exits, which are price-driven, decide who can take which donor.
- **B1:** yes — the recipient's own starting level is kept.
- **C:** yes — groups defined by future eligibility keep group-level content.
- **D:** no.
- **E:** no.
- **B2:** no own content is ever used. B2 does condition on two things:
  - the recipient's own update **timing**. That is structure, not Business Improvement content. Effects tied only to timing, such as an earnings-announcement premium, appear in both the real and null worlds and are correctly removed from the test.
  - the **cross-sectional** rank-transition dynamics, which are a property of the data-generating process, not of any company. "Company fixed effects" survive only as rank persistence, never as identity.

**17. Under-conditioning (which non-predictive structure does each null destroy?)**
- **A:** the cross-section, through reuse and a survivor tilt.
- **B1:** the distributions.
- **C:** —
- **D:** continuity at block joins.
- **E:** continuity at churn.
- **B2 destroys:**
  - the exactness of the held-copy multiset (item 25);
  - the real association between a name's held vector and its *own* future entry or exit. That association is partly return-related, so it **should** be destroyed (item 32 explains the consequence for total turnover).
- **Every design destroys:** the relation between Business Improvement and size, which is not part of H029 and is not preserved (item 24).

## 18–21. Universe dynamics

**18. Sector handling:**
- Every assignment draws from the recipient's FF12 sector at that review: the frozen FF12 of the SEC SIC, as used by the strategy.
- There is no cross-sector fallback. The minimum sector size observed in the E031-06 canary was 12 stocks.

**19. Eligibility entry:**
- An entering stock is an event in its sector at its entry review.
- It joins the coupling with a seeded random rank key (it has no null history). It receives the vector of the event-donor at that rank: a same-sector, same-review vector.
- No future information is used.

**20. Eligibility exit — Lemma (no artificial reset):**
- **Statement:** if stock i is eligible at t − 1 and t, is in the same sector at both, and its real six-signal vector did not change, then i's null vector at t equals its null vector at t − 1, whatever other stocks do.
- **Proof:**
  - The algorithm rewrites null vectors only for members of the event set Ev_s(t): entrants, sector-changers and stocks whose own vector changed. i is not a member.
  - Donors are not tracked after a copy is made, so no later event of a donor reaches i.
- **Consequences:**
  - When a *recipient* exits, its null path ends together with its name. Nothing is handed to anyone.
  - When a *donor* exits, nothing happens to anyone.
  - Both CP4 artifact channels are therefore impossible by construction.

**21. Sector changes:**
- A stock whose FF12 at t differs from t − 1 is an event in its **new** sector.
- Its coupling key is its previous null score, so the level continues as far as the new sector's released vectors allow.
- This is a pre-declared, deterministic rule. A sector change is a classification event, so a small level adjustment is accepted rather than a cross-sector vector (R3 takes precedence).

## 22–24. Signals and randomization level

**22. Six signals:**
- The whole vector moves **together** at every assignment, with its missing pattern.
- This keeps the joint structure of the six signals and the at-least-5-of-6 semantics.

**23. Randomization-level analysis:**

| Level | Advantages | Disadvantages |
|---|---|---|
| Raw statement items (revenue, GP, …) | — | Signals need one company's coherent 6-quarter history; mixing companies is meaningless. **Invalid.** |
| **Pre-percentile six-signal vector** | Joint structure and missing pattern preserved. A held copy is just "last filed values", exactly like real staleness. The frozen `h029_score` recomputes percentiles monthly, so the per-column percentile grid is exact for the given valid counts. One unchanged code path for H029 and H030. | Held copies make the vector multiset approximate. |
| Post-percentile features | — | Percentiles belong to one month's cross-section. A held copy would not be a valid percentile later, and the frozen scoring code would have to be bypassed. |
| Final H029 score | Simple | Same staleness problem. Loses the missing-signal and coverage semantics. |

**24. Preferred level:**
- **A — the pre-percentile six-signal vector.** The final score's **rank** is used only as a structural coupling key.
- **Destroyed:**
  - stock identity ↔ H029 path;
  - H029 path ↔ that stock's future returns;
  - company-level fixed effects as identity;
  - the size relationship.
- **Preserved:**
  - sector-level Business Improvement conditions, which are sector structure;
  - rank persistence, which is the data-generating dynamics.
- **Size / liquidity:** there is no structural evidence that H029's null needs size or ADV matching. H029 neither uses size nor weights by size, and Null #2's risk distributions passed with no size matching. **Not added.** Any size effect would show in the unchanged risk-adequacy audit.

## 25–29. Exactness and integrity

**25. Cross-sectional preservation** (each review, each sector):
- **Exact:**
  - number of eligible stocks;
  - sector counts;
  - the multiset of vectors released at that review (updaters, entrants, sector-changers), through the one-to-one coupling;
  - per-column percentile grids, given the valid counts.
- **Approximate:**
  - the full vector multiset and the H029 score multiset. Stocks without an event hold copies taken at their own last event (≤ about 3 months ago). Those copies differ from the real held vectors only where a vector's originating company left or updated since.
  - valid counts per column, hence percentile denominators.
- **Expected scale:** small. Over a ≤ 3-month holding window with about 2.3% exits a month, only a few percent of held copies are affected.
- **Diagnostic:** report it as a per-review distance between the real and null score distributions (not a gate; item 32).

**26. Temporal preservation:**
- **Exact:** update timing and frequency; the age of each held vector at assignment (it is fresh, like the real filing).
- **Approximate (emergent, not forced):**
  - score and rank autocorrelation: the rank-transition kernel is exact among event stocks and unchanged for held vectors;
  - holding spells and turnover.
- **Turnover is not engineered** to match. It may still differ from the real value for legitimate reasons (item 32).

**27. Missingness:**
- Donors come from E29(t), so every assigned vector has at least 5 of 6 valid signals.
- The missing pattern travels with the vector.
- Recipient eligibility is the real one and is never altered. The Data v3 rules are untouched.

**28. PIT proof (induction):**
- **At the first review** the null vectors are a within-sector derangement of real vectors observed at that review.
- **At review t,** the algorithm reads only:
  - E29(t) and sectors at t and t − 1;
  - real vectors at t and t − 1 (to detect events);
  - real H029 scores at t − 1;
  - null scores at t − 1, which are functions of null vectors at t − 1 — real vectors observed ≤ t − 1 by the induction hypothesis;
  - the seed.
- **Every null vector at t** is therefore a real Data v3 vector observed at some date ≤ t.
- **Nothing reads beyond t:** no future filing, future eligibility or future donor state. There are no pointers. ∎

**29. Survivorship and corporate actions:**
- Donors are only stocks eligible at the review, so there is no conditioning on future survival.
- **New listings and identity changes** (Data v2.1 security-life rule: a new security id) are entrants.
- **Delistings and merger targets** are exits: their null path ends with the name.
- **Acquirers** continue unchanged.
- A held copy may originate from a company that has since left. This is known at t, so it is not future information, and it is the analogue of a stale filing.

## 30–33. H030, canaries, adequacy, risk

**30. H030 compatibility:**
- H030_null = 0.50 · centred(**real** H028) + 0.50 · centred(Null #3 H029 score) over the joint universe J(t).
- It is one null and one code path for both. H028 is never randomized.

**31. Synthetic-canary design** (to be built and run only if approved; synthetic panels, frozen pipeline):

| Canary | Construction | Pass criterion (fixed in advance) |
|---|---|---|
| A — pure noise | Quarterly-updating, persistent within-sector vectors with no relation to returns; 5 replications × 50 worlds | At most 1 of 5 with p ≤ 0.02, for S_UP and for S_INC |
| B — planted persistent within-sector predictor | Latent with quarterly persistence that predicts within-sector returns | S_UP above every null world (p = 1/51) |
| C — universe churn | Entries and exits with smooth paths | (1) The null vector of every continuing, non-event stock is unchanged — exact, 0 violations. (2) In a world with no signal and random exits, real turnover is exchangeable with the null (percentile within the null's central 99%). |
| C′ — vector-dependent exits, no return signal | Exits made more likely for low-vector stocks | Reported only. Demonstrates the total-turnover confound (item 32); the continuing-name gates must stay inside the null range. |
| D — sector change | A stock switches FF12 | At that review it is an event in the new sector; 0 cross-sector assignments; its null key is its previous null score |
| E — missingness | Signals temporarily unavailable | Recipient eligibility identical to the real data; every assigned vector valid at ≥ 5 of 6; the missing pattern travels with the vector |
| F — identity | Track the origin of every copy | 0 self-assignments (no recipient ever holds a vector originating from itself) |
| G — PIT truncation | Run on a panel truncated at month T | Null vectors identical through T |
| H — determinism | Same seed, run twice | Identical worlds |

**Real-data structural checks** (score-only, no returns), in the canary run:
- Data v3, H028, H029 and H030 unchanged (as in E031-06);
- cadence identity: null event months = real event months;
- 0 cross-sector assignments; 0 self-assignments;
- count of single-event sector-reviews (fallback use).

**32. Structural adequacy proposal** (formal gates fixed before any null world; each = the real value inside the null [0.5%, 99.5%] range):
- **Unchanged:**
  - **G-HHI-29 / G-HHI-30:** H029 and H030 sector HHI;
  - **G-TURN-30:** H030 name turnover.
- **New — persistence measured on continuing names** (eligible at t − 1 and t, same sector):
  - **P1:** mean monthly within-sector Spearman correlation of H029 scores between t − 1 and t.
  - **P2:** H029 Top-15 one-month survival, P(in Top-15 at t | in Top-15 at t − 1, still eligible).
  - Both detect the CP4 artifact directly: a held continuing stock losing its donor shows up as a survival failure and a rank jump.
- **H029 total turnover (G-TURN-29) — owner decision with a pre-registered rule.**
  - **The problem:** total turnover counts forced entries and exits. Those are partly price-driven ($2B threshold, acquisitions) and partly vector-driven (missing signals). A valid null keeps recipients' real eligibility but randomizes their vectors. It therefore cannot reproduce how often *real* held names leave or new names enter. If H029 genuinely avoids stocks about to fall out of the universe, a correct null can fail total turnover for a reason that is part of the signal.
  - **Recommended rule, fixed now:** compute two score-only rates on the real data, with no returns and no null:
    - q_exit = the share of exiting names that were in the previous Top-15;
    - q_entry = the share of entering names selected at entry.
  - **If** both lie within the 99% binomial interval of random holding (15 / n_t per review), total turnover stays a formal gate. **Otherwise** it becomes a reported diagnostic, and P1 / P2 carry the persistence requirement.
  - This is decided before any Null #3 world exists, so the rule cannot be chosen after seeing whether it passes.
- **Diagnostics (not gates):**
  - per-review Kolmogorov–Smirnov distance between the real and null H029 score distributions;
  - fallback rate;
  - number of duplicate vectors.
- **Constructibility bound (owner to confirm):** if fallback assignments exceed 5% of event-recipients → STOP — Null #3 NOT CONSTRUCTIBLE AS SPECIFIED.

**33. Risk adequacy:**
- The existing audit stays unchanged: beta, up / down capture and volatility must be finite with sd > 0, and the medians of beta / up / down capture must lie in [0.5, 1.5].
- **Mechanically abnormal risk is not expected:**
  - the null selections are sector-preserving and persistence-preserving, and random with respect to returns, like Null #2, whose risk distributions passed.
- **One expected, legitimate difference:**
  - null portfolios will hold names that are about to leave the universe at the random rate, rather than the real rate;
  - that difference is part of the information being tested, not a structural defect.

## 34–35. Feasibility and architecture

**34. Computational feasibility:**

| Item | Estimate |
|---|---|
| World-independent precomputation | Per review: event flags, real H029 scores at t − 1, previous sectors — about 84 × 1,000 × 17 bytes ≈ 1.5 MB |
| Per world | O(n) state updates plus sorting the event set per sector (≈ 260 event stocks a review), plus the same `h029_score`, selection and portfolio simulation as now. Expected ≈ 0.25–0.30 s per world (Null #2: 0.22–0.24 s). |
| 5,000 worlds | ≈ 2 runs × (≈ 10–13 min of worlds + ≈ 18 min of setup), as now |
| Memory | Peak ≈ 7.8 GB, unchanged, plus a few MB (node limit 8 GB; no headroom for anything larger) |
| Files | **0 additional** (50 / 50 unchanged) |

**35. Host architecture recommendation (not built):**
- Keep the **standalone S031** host (already a direct subclass of the frozen X801; no subclass chain).
- Implement Null #3 as a **new version of the `qr_h029` null functions**, plus new S031 canary checks: S031 v1.2, with new hash pins.
- Do not add a subclass or files.
- Before writing code, the amendment text, gates and canary must be committed and approved.

## 36–38. Selection and algorithm

**36. Rejection criteria applied:**

| Criterion | A | B1 | B2 | C | D | E |
|---|---|---|---|---|---|---|
| Uses future information | ✗ (exit dates) | | | ✗ (eligibility path) | | |
| Depends on returns | | | | | | |
| Systematic cross-sector assignment | | | | | | |
| Changes recipient eligibility | | | | | | |
| Repeated artificial donor resets | | | | | ✗ | ✗ |
| Cannot preserve quarterly persistence | | | | | | |
| Performance-based tuning | | | | | ✗ (L) | |
| Not deterministically reproducible | | | | | | |
| Conditions away the tested signal | ✗ | ✗ | | ✗ | | |
| Mathematically invalid | | ✗ | | | | |

✗ = criterion triggered (rejected on it). B2 triggers no criterion; its only open point is the constructibility audit.

**37. Recommended single design: B2 — the Event-Copy Relay.**

It is the only design that meets all of R1–R12 together with the online requirement the proposition shows is necessary. It does so by moving from pointer semantics to copy semantics. The price is that the held-copy cross-section is approximate rather than exact.

**38. Exact conceptual algorithm**

```
PRECOMPUTED (world-independent, point-in-time):
  for each evaluation review t = 1..84:
    E(t)        H029-eligible ids (frozen Data v3 / H029 rules)
    sec_t(i)    FF12 sector at t (frozen)
    v_t(i)      real pre-percentile six-signal vector (NaN = missing), Data v3 view
    y_{t-1}(i)  real H029 score at t-1 (for i in E(t-1))
  event set Ev_s(t), t >= 2, sector s:
    i in E(t), sec_t(i) = s, and ANY of:
      i not in E(t-1)                    (entry)
      sec_{t-1}(i) != s                  (sector change)
      v_t(i) != v_{t-1}(i)               (own information update: any of the six values or its missing flag)

WORLD(seed):
  rng = Generator(seed)
  t = 1:  for each sector s: N_1 = within-sector derangement of {v_1(j)}            # exact multiset
  for t = 2..84:
    z_{t-1} = h029_score(N_{t-1}) over E(t-1)                                        # frozen scorer, null panel
    for each sector s:
      Ev = Ev_s(t)
      keyR(i) = z_{t-1}(i) if i in E(t-1) else rng.uniform()     # recipients: null previous score
      keyD(j) = y_{t-1}(j) if j in E(t-1) else rng.uniform()     # donors: real previous score
      ties: broken by a seeded random key
      if |Ev| >= 2:
        order Ev by keyR -> r_1..r_m ; order Ev by keyD -> d_1..d_m
        pi(r_k) = d_k                                            # monotone rank coupling, a bijection on Ev
        for k = 1..m (in r-order): if pi(r_k) == r_k: swap pi(r_k) with pi(r_{k+1})
                                   (with pi(r_{k-1}) if k = m)   # never creates a new fixed point
        N_t(i) = v_t(pi(i)) for i in Ev                          # COPY of the donor's current vector
      if |Ev| == 1 (Ev = {i}):                                   # pre-declared fallback; counted
        j* = argmin over j in E(t) ∩ sector s, j != i, j in E(t-1) of |y_{t-1}(j) - keyR(i)|
        N_t(i) = v_t(j*)
    for every i in E(t) not in any Ev:  N_t(i) = N_{t-1}(i)      # held copy: no outside event can touch it
    stocks not in E(t): no state (path ended with the name)
  H029_null(t) = h029_score(N_t) over E(t)                       # frozen; at least 5 of 6, equal weights
  H030_null(t) = blend(real H028 over J(t), H029_null(t) restricted to J(t))
  then: frozen Top-15 / sector cap / costs / H029, H030 statistics, exactly as before
```

**Specification of every element:**
- **Unit randomized:** the whole six-signal vector.
- **Strata:** FF12 sector × review.
- **Initialization:** a derangement at the first evaluation review (exact multiset; no burn-in parameter).
- **Monthly evolution:** held copies.
- **Entry, exit, sector change:** items 19–21.
- **Missing values:** carried with the vector.
- **Percentiles:** recomputed monthly by the frozen scorer.
- **Self-match:** never; enforced by the swap rule and the fallback exclusion.
- **Seed:** drives the first-review derangement, the entrants' keys and tie-breaks. Given the seed, the Data v3 manifest and this specification, a world is fully deterministic.
- **Known transient:** in the first quarter after initialization, held copies carry the donor's staleness rather than the recipient's own (≤ 3 months). This is disclosed.

**Toy example** (one sector, stocks A, B, C, D; reviews t − 1 and t):
- **At t − 1,** the null copies are: A holds a copy of C's vector, B of D's, C of B's, D of A's.
- **At t:**
  - **A and B both file** (their real vectors change), so Ev = {A, B}. A's null previous score ranks above B's, and B's real previous score ranks above A's. The coupling therefore gives A the new vector of B, and B the new vector of A: no fixed point.
  - **D leaves the universe.** D's null path (its copy of A's old vector) ends with D. Nobody else changes: no stock was "pointing" at D.
  - **C has no event.** C keeps its copy of B's old vector, even though B released a new one.
- **In Null #2,** D's exit would have forced D's donor vector onto a new name, and the stock reading D's vector would have jumped to another company. Here neither can happen.

## 39–42. Interpretation and disclosure

**39. Meaning of a significant result** (if Null #3 were adequate and H029 beat it):
- **What it would show:** evidence that H029's ranking contains **within-sector stock-selection information beyond what is produced by same-sector Business Improvement paths with the same filing timing, eligibility path and rank dynamics, assigned to the wrong companies**.
- **What it would not show:**
  - sector-allocation skill;
  - universal "fundamentals alpha";
  - robustness outside 2015–2021 (development data only);
  - and it would not open the Holdout.

**40. Meaning of a non-significant result:**
- **What it would show:** no robust evidence that H029 adds within-sector stock-selection information beyond these preserved structural characteristics, given the 84-month sample and its limited power.
- **What it would not show:** that fundamentals are useless, or that every Business Improvement definition fails.

**41. Pre-performance amendment disclosure:**
- Null #3 would be a **second methodological amendment, made after two structural adequacy failures and before any real H029 / H030 performance was observed**.
- Its design is informed by:
  - sector concentration (Null #1);
  - turnover;
  - donor re-pairing (Null #2 and P14-CP4).
- **It is not informed by any H029 / H030 return**, because none exists.

**42. Anti-fork recommendation: YES, adopt the rule.**
- Null #3 is the final planned null for H029 / H030.
- If it fails a formal structural adequacy gate, or the constructibility bound → **close H029 / H030 as NOT EVALUABLE**. There is no Null #4.
- The P1 / P2 gates and the total-turnover rule (item 32) must be fixed **before** any Null #3 world, so this rule cannot be bypassed afterwards.

## 43. Q1–Q10

Answered at the top of this report.

## 44. Exact owner approvals required before implementation

1. **Approve B2 (the Event-Copy Relay)** as H029 / H030 Amendment 2, using the text of items 8, 18–29 and 38, which would be frozen and hash-pinned unchanged.
2. **Approve the formal adequacy gates:**
   - G-HHI-29, G-HHI-30, G-TURN-30 (unchanged);
   - P1, P2 (new);
   - the pre-registered q_exit / q_entry rule deciding whether G-TURN-29 stays a gate;
   - the unchanged risk-adequacy audit.
3. **Approve the constructibility bound:** fallback ≤ 5% of event-recipients, else STOP.
4. **Approve the canary suite A–H plus the real-data structural checks** (item 31). These are infrastructure runs; the real data is used score-only.
5. **Approve the run order:**
   - amendment and code committed and pinned;
   - canary (new experiment id);
   - 5,000 worlds (seeds 1–5,000) and the seeds 1–25 rerun;
   - adequacy;
   - only if adequate: c_UP_H029 / c_INCREMENTAL_H030 pinned and merged, then the ONE real 2015–2021 run with the unchanged N1–N5 / C1–C7.
6. **Approve the anti-fork rule** (item 42).

## 45. Confirmation

- No code was written for the null and no module was changed.
- No canary, null world, threshold or QuantConnect run was produced.
- No return or performance quantity was accessed.
- No committed null result file was read for this review.
- The Holdout is sealed.
- H029 / H030 remain **BLOCKED**.

---

**THIRD NULL DESIGN REVIEW — ONE SCIENTIFICALLY PREFERRED DESIGN IDENTIFIED — AWAITING OWNER APPROVAL**

H029 / H030 BLOCKED (unchanged). **STOP.**
