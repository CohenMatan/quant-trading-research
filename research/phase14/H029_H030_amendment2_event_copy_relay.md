# H029 / H030 — Amendment 2: Null #3 "Event-Copy Relay" (owner D237)

> **DRAFT — NOT FROZEN, NOT PINNED, NOT USED.** P14-CP6a stopped before any real-data Null #3 world. The
> pre-implementation synthetic feasibility check (`research/phase14/cp6/P14_CP6a_synthetic_feasibility.json`) showed
> that B2, as specified in section B, cannot reproduce the persistence of a no-signal selection under realistic
> universe churn. Its null turnover is +0.10 to +0.15 above the real value, against +0.012 to +0.019 for Null #2. The
> text below is kept as the record of the approved design and of the owner's amendments (sections C–F).

## Status

- **Nature:** an **owner-approved second methodological amendment**. It is made after two structural adequacy failures and **before any real H029 / H030 performance was observed**.
- **Approval:** owner D237 approved B2 (P14-CP5) in principle, subject to two pre-implementation amendments, both included here:
  - a formal cross-sectional adequacy gate (section E);
  - fallback reporting by review and sector (section D).
- **What informed the design:** the structural findings on sector concentration (Null #1), turnover and donor re-pairing (Null #2, P14-CP4). **Not** any H029 / H030 return; none exists.
- **Freezing:** this text is frozen and SHA-256-pinned in `qresearch.p14h029` before any Null #3 world. Every bound below is fixed now, from sampling theory or from the owner's decision. None is chosen after seeing a Null #3 result.
- **Unchanged:** the original specification and Amendment 1 stay byte-identical as records. Amendment 2 replaces only the null, its adequacy rules and the run ids.

## A. What changes and what does not

**Changes:**
- the null construction (section B);
- the structural adequacy rules (sections D–F);
- the run ids (section H).

**Unchanged:**
- H029: F1, F2, F4, F5, F7, F8; at least 5 of 6; equal weights; no model;
- H030: exactly 0.50 / 0.50; H028 frozen;
- Data v3: frozen;
- mechanics: Top-15, at most 3 per FF12, monthly, next open, $7 / $7, 10 bps, $100,000;
- gates N1–N5 / C1–C7;
- the threshold convention (50th largest of 5,000 = the 99th percentile) and the empirical p;
- the risk-adequacy audit (spec section 9 C);
- the synthetic long-horizon rule (only if C1–C7 all pass);
- **the Holdout stays sealed.**

## B. Null #3: Event-Copy Relay (exact algorithm)

### B.1 Notation

- **Evaluation months** t = 1..84 (the H029 evaluation months, 2015–2021).
- **E(t):** the frozen H029-eligible ids at t.
- **sec_t(i):** the frozen FF12 sector at t.
- **v_t(i):** the real pre-percentile six-signal vector at t (NaN = missing), from the Data v3 view.
- **y_t(i):** the real H029 score, `qr_v3.h029_score` on {v_t}.
- **prev_t(i):** i's position at t − 1, if i ∈ E(t − 1).

### B.2 Events (world-independent)

- **At t = 1,** every stock is an event.
- **At t ≥ 2,** i ∈ E(t) is an event if any of the following holds:
  - **entry:** i ∉ E(t − 1);
  - **sector change:** sec_{t−1}(i) ≠ sec_t(i);
  - **own information update:** v_t(i) ≠ v_{t−1}(i), compared NaN-aware; any of the six values, or its missing flag, differs.
- **Ev_s(t)** = the events of sector s at t, ordered by position (ids sorted).

### B.3 One world (seed s)

**Random draws:**
- The generator is `numpy.random.default_rng(s)`.
- Months are processed in date order. Within a month, sectors are processed in ascending FF12 index.
- For each sector with m = |Ev_s(t)| events, draw in this order:
  - uR = uniform(−1, 1, m);
  - uD = uniform(−1, 1, m);
  - tR = random(m);
  - tD = random(m);
  - if m = 1, additionally tF = random(number of fallback candidates).

**Keys:**
- **Recipient key** keyR(i) = z_{t−1}(prev(i)) if i ∈ E(t − 1); otherwise uR(i).
  - z_{t−1} is the **null** H029 score at t − 1: the frozen `h029_score` applied to the null vectors at t − 1.
  - At t = 1, keyR = uR.
- **Donor key** keyD(j) = y_{t−1}(prev(j)) if j ∈ E(t − 1); otherwise uD(j). At t = 1, keyD = uD.

**Coupling, if m ≥ 2:**
- Order the recipients by (keyR, tR) ascending → r_1..r_m. Order the donors by (keyD, tD) ascending → d_1..d_m.
- π(r_k) = d_k.
- **Self-match removal:** in r-order, if π(r_k) = r_k, swap π(r_k) with π(r_{k+1}) (with π(r_{k−1}) when k = m). This never creates a new fixed point.
- Every i ∈ Ev_s(t) receives a **copy** of v_t(π(i)).

**Fallback, if m = 1** (Ev_s(t) = {i}):
- Candidates: j ∈ E(t) ∩ E(t − 1), sec_t(j) = s, j ≠ i.
- j* = the candidate with the smallest |y_{t−1}(j) − keyR(i)|, ties broken by tF.
- i receives a copy of v_t(j*).
- No candidate → **STOP — NULL #3 NOT CONSTRUCTIBLE**. (At t = 1, a sector with one stock → STOP as well.)

**Non-events (t ≥ 2):** i keeps its copy from t − 1 unchanged.

**Scores:** the null H029 score at t = the frozen `h029_score` on the null vectors over E(t).

**H030_null(t)** = 0.50 · centred(real H028 on J(t)) + 0.50 · centred(null H029 restricted to J(t)).

**Then:** the frozen Top-15 / sector cap / costs / statistics, exactly as for every earlier null.

### B.4 Origins (for section E)

- Every copy carries an origin (company, vintage).
- **Vintage** = the latest evaluation month τ ≤ t at which the donor's real vector differed from its previous **observed** real vector, or the month it was first observed.
- **Exact duplicate:** two slots at the same review sharing the same (company, vintage), i.e. the same company's same information.
- **Company multiplicity:** two slots sharing the same company (any vintages).

### B.5 Guarantees, proved and test-checked

1. **No artificial reset:** a continuing stock with no event keeps an identical null vector, whatever other stocks do.
2. **Same sector:** every copy comes from the recipient's own FF12 sector at the review of copying.
3. **No self-copy:** a stock never holds a copy of its own data.
4. **Eligibility:** E(t) is never altered; each copied vector is a real eligible vector with at least 5 of 6 valid signals.
5. **Exact bijection:** for m ≥ 2, the copies assigned at t are exactly the multiset of vectors of Ev_s(t).
6. **Point-in-time:** everything read at t is dated ≤ t.
7. **Determinism:** a world is fully determined by (seed, Data v3 panel, this text).

## C. G-TURN-29 status rule (decided before any Null #3 world; owner-approved)

**Computed on the real H029 Top-15 target lists** S_t (frozen `pick`; scores only, no returns) over t = 2..84:

| Quantity | Definition |
|---|---|
| X | number of exits (i ∈ E(t − 1) \ E(t)) that were in S_{t−1} |
| E_x | Σ over exits of p = \|S_{t−1}\| / n_{t−1} |
| V_x | Σ over exits of p(1 − p) |
| z_exit | (X − E_x) / √V_x |
| Y, E_y, V_y, z_entry | the same, for entries (i ∈ E(t) \ E(t − 1)) and S_t, with p = \|S_t\| / n_t |

**Rule:**
- If |z_exit| ≤ 2.576 **and** |z_entry| ≤ 2.576 (both inside the 99% interval of random holding), then **G-TURN-29 is a formal adequacy gate**.
- Otherwise G-TURN-29 is a **reported diagnostic**, and P1 / P2 carry the persistence requirement.
- **Pinning:** the result is computed in the structural pre-run E031-11 and permanently pinned (`qresearch.p14h029.G_TURN_29_STATUS`) before any Null #3 world. No canary or null config validates until it is pinned.

## D. Constructibility (owner amendment 2)

- **Fallback share** = (number of fallback events) / (number of event recipients), over t = 2..84.
- **Bound:** fallback share ≤ **0.05**. Otherwise → **STOP — NULL #3 NOT CONSTRUCTIBLE**, which under the anti-fork rule means H029 / H030 NOT EVALUABLE.
- **Fallback events are world-independent** (they depend only on the real event sets). Their exact frequency **by review and by sector** is computed in E031-11 and reported in full in the checkpoint.

## E. Cross-sectional adequacy (owner amendment 1; bounds fixed now)

**How the statistics are computed:**
- In every null world, for every review t, by comparing the null cross-section with the real one over the same E(t).
- **World statistic** = the mean over t = 1..84.
- **A gate passes** if the **99.5th percentile over the 5,000 worlds** is ≤ its bound.

| Gate | Statistic per review | Bound (fixed now) | Basis of the bound |
|---|---|---|---|
| **S1 composite-score distribution** | two-sample Kolmogorov–Smirnov distance between the real and null H029 scores | B1 = mean_t 1.6276 · √(2 / n_t) | The 1% two-sample KS critical distance for equal sizes: the null distribution must not be distinguishable from the real at 1%, on average |
| **S2 joint six-feature structure** | mean over the 15 signal pairs of \|Spearman(null) − Spearman(real)\|, on complete cases (all six valid) | B2 = mean_t 1 / √(c_t − 3), c_t = the real complete-case count | One Fisher-z standard error of a single correlation |
| **S3 duplicate origins** | share of slots holding an **exact duplicate** origin (B.4) | **0.05** | The constructibility tolerance (D): exact duplicates can only arise from fallback copies and re-entries |
| **S4 valid-count / missing pattern** | max over 7 proportions (each signal's missing rate; the share with all six valid) of \|p_null − p_real\| / √(2 q (1 − q) / n_t), q = p_real clipped to [1/n_t, 1 − 1/n_t] | **2.576** | Two-proportion 1% critical value |

**Company multiplicity is reported, not gated.** Two different vintages of one company are different information sets: a company's old and new filings. Any distortion they cause shows in S1, S2 and S4, which are gated.

## F. Formal adequacy (all must pass before any threshold)

1. **Constructibility (D).**
2. **Structure** (real value inside the null [0.5%, 99.5%] range of the 5,000 worlds):
   - H029 sector HHI and H030 sector HHI (unchanged);
   - H030 name turnover (unchanged);
   - H029 name turnover **only if C makes it a gate**;
   - **P1:** within-sector persistence. For t = 2..84 and each sector with ≥ 3 continuing names (eligible at t − 1 and t, same sector), take the Spearman correlation of H029 scores between t − 1 and t. Average over sectors, weighted by the number of names, then over t.
   - **P2:** Top-15 survival among continuing names = Σ_t |S_t ∩ S_{t−1} ∩ C_t| / Σ_t |S_{t−1} ∩ C_t|, where C_t = the stocks eligible at both t − 1 and t.
3. **Cross-section:** S1–S4 (E).
4. **Risk:** spec section 9 C, unchanged.
5. **Determinism:** the seeds 1–25 rerun is identical in every stored field.

**Any failure → H029 / H030 NOT EVALUABLE** (anti-fork rule, owner D237): STOP; no Null #4; no threshold; no real run.

## G. Canary (E031-12; synthetic panels use the real event schedule and real churn)

| Canary | Construction | Pass |
|---|---|---|
| **A** pure noise | Six identical columns; value N(0, 1) at t = 1 and at entry; at each other event 0.9 · previous + √0.19 · N(0, 1); held otherwise. 5 replications (seeds 7101–7105) × 50 Null #3 worlds | At most 1 of 5 with p ≤ 0.02 for S_UP; same for S_INC |
| **C** exchangeability (on the A replications) | Synthetic-real H029 turnover, P1 and P2 vs the 50 null worlds | Each lies within the null [min, max] in at least 4 of 5 replications |
| **B** planted persistent within-sector predictor | At each event, value = mean over h = 0..2 of the stock's (r_oo − its sector's mean r_oo) × 1[SPY month up] at t + h (absent = 0), + N(0, 0.01²); held otherwise. Seed 7201; 50 worlds. Deliberate look-ahead, canary only | S_UP above every null world (p = 1/51) |
| **C′** vector-dependent exits | Replication 7101's values minus 1.0 for stocks that leave E within the next 3 months | Reported only (turnover / P1 / P2 percentiles) |
| **D** sector change | Real data, seeds 1–2 | Every sector-change stock is an event; 0 cross-sector copies |
| **E** missingness | Real data | 0 null vectors with fewer than 5 valid signals; E(t) unchanged |
| **F** identity | Real data | 0 self-origin copies |
| **G** PIT truncation | Relay run on months 1..42 only | Null vectors and scores identical to the full run's months 1..42 |
| **H** determinism | Same seed, twice | Identical |

**Plus the E031-06 checks, unchanged:**
- Data v3 panel digests;
- H026 panels;
- H028 / LV15 reproduction;
- score / blend mechanics;
- entry timing;
- H028 scores and recipient data unchanged by the null;
- B.5 guarantees 1 and 5 (no artificial reset; exact bijection).

**Constructibility (D)** must hold, and **G-TURN-29 must already be pinned** (C).

**Any failure → STOP.**

## H. Run order and ids

| Step | Run | Content |
|---|---|---|
| 1 | **E031-11** | Structural pre-run (scores, events and target lists only; no null world, no return): q rule (C), fallback table (D), event counts, real P1 / P2. Then **pin G-TURN-29**. |
| 2 | **E031-12** | Canary (G) |
| 3 | **E031-13 / E031-14** | Null #3 worlds, seeds 1–2,500 / 2,501–5,000 |
| 4 | **E031-15** | Rerun of seeds 1–25 |
| 5 | — | Adequacy (F). Only if everything passes: c_UP_H029 / c_INCREMENTAL_H030 = the 99th percentiles of the Null #3 worlds, pinned, committed and merged |
| 6 | **E031-16** | The ONE real 2015–2021 evaluation; N1–N5 / C1–C7 unchanged |

**Records:** E031-01..04 (Null #1) and E031-06..09 (Null #2) stay as records and are never reused. Their thresholds are invalid.

## I. Interpretation

**A significant result (N1 / C1)** means: within-sector stock-selection information beyond what is produced by same-sector Business Improvement vectors that are assigned to the wrong companies with the same filing timing, eligibility path and rank dynamics. It does not mean:
- sector-allocation skill;
- universal fundamentals alpha;
- validation (2015–2021 is development data).

**A non-significant result** means: no robust evidence beyond these preserved structures. It does not mean fundamentals are useless.

**Status wording (unchanged):**
- "H029 UPSIDE SIGNAL REJECTED" / "H029 UPSIDE SIGNAL CANDIDATE";
- "H030 REJECTED — PRE-REGISTERED 50/50 COMBINATION DOES NOT SUFFICIENTLY IMPROVE H028" / "H030 DEVELOPMENT CANDIDATE — PRE-REGISTERED H028 + H029 COMBINATION".
