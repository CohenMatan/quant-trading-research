# LH-CP3 — Missing Fiscal Labels: Recovery & Validation — PROTOCOL (frozen before any new aggregate)

**Owner decision:** D244 (`docs/owner/2026-10-18_lh_cp3_missing_fiscal_labels_recovery.md`).

**Nature:** an SEC accounting-period metadata and data-integrity investigation.
- **Not computed:** prices, returns, surprise values, rankings or predictive statistics; no QuantConnect run.
- **Unchanged:**
  - LH-CP1 Stage C stays **C — NOT FEASIBLE**, with its protocol (`ff97789b…`) and artifacts.
  - LH-CP2 stays **C — INSUFFICIENT EVIDENCE**, with its protocol (`f7cbac94…`) and artifacts.
  - LH-CP3 is a new investigation, not a correction of either.

**Hash rule:**
- This file's SHA-256 is pinned in `tests/test_lh_cp3.py`.
- It is committed before any LH-CP3 script produces an aggregate.
- The reconstruction rules module `lh_cp3_rules.py` is frozen (SHA-256 in `LH_CP3_rules_freeze.json`) after development and before the held-back evaluation.
- The network sample manifest is committed (SHA-256 recorded) before the first EDGAR request.

## 1. Cut-off and point-in-time enforcement

1. **Local data.** Every local SEC record comes through the LH-CP2 loaders (`lh_cp2_safe`). They drop anything filed, ending, starting or reported after **2021-12-31** before a caller can see it.
2. **Network requests.** The request URL builder `lh_cp3_safe.header_url(cik, accession, manifest)` refuses to build a URL unless all of the following hold:
   - the accession is in the committed manifest;
   - its local filing date is ≤ 2021-12-31;
   - it is an original 10-Q or 10-K, not an amendment.
3. **Responses.** The header parser checks two things before extracting any other field:
   - the response's `FILED AS OF DATE` is ≤ 2021-12-31 and its `ACCESSION NUMBER` matches the request; otherwise the response is discarded;
   - if `DATE AS OF CHANGE` is after the cut-off, the company-data block (name, fiscal-year end) is not used, and only that fact is recorded.
4. **Body discarded.** Everything after `</SEC-HEADER>` (or `</IMS-HEADER>`) is discarded unread.
5. **Decision-time rule.** Evidence used for a decision day D was filed ≤ D − 1. This covers the period's own filing, bracketing 10-K filings and comparative-evidence filings. Amendments are never used.
6. **Outputs.** All outputs pass `assert_no_post_cutoff`.
7. **Ex-post exception.** Ground-truth checks may look at labels filed later than D but ≤ 2021-12-31. This applies only to evaluation:
   - the hidden labels of the validation in §5;
   - the rule P review in §8.
   Such checks never feed a history status.

## 2. Label sources (per chain period p)

A fiscal label is 1–3 (Q1–Q3) or 4 (FY).

| Tier | Source | Status |
|---|---|---|
| L0 direct | The modal `fp` of the companyfacts facts carrying the accession of p's original 10-Q / 10-K, found through the XBRL index (exactly LH-CP2 §4) | Verified |
| L1 recovered direct (Part A) | The same modal `fp`, but with the accession found through **local submissions** (see the rules below) | Verified |
| L2 reconstructed | Frozen rule R* (§4): two independent methods agree | Accepted only in Scenario B, and only if R* passes validation (§6) |
| L3 single-source inference | Exactly one method gives a label | Scenario C only (sensitivity) |
| — | Neither | Unknown |

**L1 rules.** The accession comes from local submissions:
- an original form 10-Q / 10-K / 10-K405, filed ≤ CUT and ≤ D − 1, whose `reportDate` is within ±7 days of p;
- if there are several, the earliest filed.

It is **Verified** only if **all** of the following hold:
- the mapping check M holds: the accession's facts contain a duration fact ending within ±7 days of p;
- the submissions filing date is within 3 days of the Data v2.1 original filing day;
- the CIK is the chain's registrant.

Otherwise:
- **Invalid** if a fact-carrying accession fails M;
- **Unknown-nonXBRL** if `isXBRL` = 0;
- **Unknown-noFacts** if `isXBRL` = 1 but no fact carries the accession;
- **Unknown-noAccession** if no submissions row is found.

Part A never infers Q1 / Q2 / Q3 from the form type.

## 3. Information that exists for a pre-XBRL period

For an original filing with no XBRL, the following are available locally:
- its submissions row: form, filing date, report date, accession;
- the registrant's full filing sequence, with the same fields;
- facts from **later** XBRL filings whose period end equals p — prior-year comparatives in the face statements, as required by Reg S-X 10-01(c) / 3-02.

No fiscal-period label of the period's own filing exists. The EDGAR header adds the fiscal-year-end code at filing time (§7).

## 4. Reconstruction methods (defined now; implemented in `lh_cp3_rules.py`)

### M-SEQ — form-sequence bracketing

Uses only form type, report date and filing date.

- **Inputs.** The registrant's original filings (one per report period, deduplicated ±7 days, earliest filed), each filed ≤ D − 1.
- **Bracket.** p lies in an *annual bracket* [a, b] when:
  - a and b are consecutive 10-K / 10-K405 periods with b − a ∈ [357, 378] days;
  - b is filed ≤ D − 1;
  - between them lie exactly three original 10-Q periods;
  - all consecutive gaps a → … → b are 80–100 days;
  - no 10-KT / 10-QT (or their amendments) has a report date in [a − 7, b + 7].
- **Labels.** Inside a bracket the labels are a = 4, then 1, 2, 3, and b = 4.
  - A 10-Q period gets a label only from a bracket that contains it.
  - A 10-K period gets 4 only if it is an endpoint of at least one valid bracket.
  - Otherwise M-SEQ abstains.

### M-CMP — company-asserted comparative presentation

Uses later XBRL filings.

- **Evidence filings.** An original 10-Q / 10-K E of the same CIK that:
  - is filed ≤ D − 1;
  - is not hidden (§5);
  - is not p's own filing;
  - has its own period p_E (submissions report date; else the XBRL-index period) with p_E − p ∈ [357, 378] days.
- **Evidence condition.** E carries at least one USD duration fact ending within ±3 days of p, with a duration consistent with E's own label ℓ_E (the modal `fp`):
  - ℓ_E = 4: 350–380 days;
  - ℓ_E = 1: 80–100;
  - ℓ_E = 2: 80–100 or 170–190;
  - ℓ_E = 3: 80–100 or 260–280.
- **Label.** M-CMP(p) = ℓ_E.
  - If qualifying evidence filings disagree, M-CMP returns *conflict*.
  - If none qualifies, M-CMP abstains.

### R* — combined rule

| Case | Outcome |
|---|---|
| Both methods give the same label | **L2 corroborated label** |
| Both give labels that differ, or either returns conflict | **conflict** — no label; the history is unknown with a conflict flag (never valid) |
| Exactly one gives a label | **L3 single-source label** |
| Neither | Unknown |

### Header-implied quarter (H-FYE; inference only, never verification)

Inputs: a fiscal-year-end code MMDD and a report period P.

- Δ = (day-of-year(P) − day-of-year(fye)) mod 365.
- **10-K:** 4 if Δ ≤ 10 or Δ ≥ 355; otherwise "inconsistent".
- **10-Q:** q = round(Δ / 91.31). The result is q if q ∈ {1, 2, 3} and |Δ − 91.31·q| ≤ 15; otherwise none.

The same function is applied to:
- local XBRL-index fiscal-year-end codes, as an XBRL-era benchmark against L0 labels;
- header codes of the network sample (§7).

## 5. Validation design (hidden labels; registrant split)

### Split

- **Held-back:** registrant CIK where the first hex digit of sha256("LH-CP3-split|" + CIK) is in 8–f.
- **Development:** all other registrants.
- **Development use:** debugging and any rule changes happen on development registrants only. Each change is recorded in the development JSON before the freeze.
- **Held-back evaluation:** run **once**, with the frozen rules (hash asserted).

### Population

All Data v2.1 registrants. Validation is not restricted to the eligible universe, so that the sample is large enough.

### Pseudo-XBRL start

- f1 = the registrant's first original 10-Q / 10-K that has an L0 or L1 label.
- Pseudo-starts: S_j = f1 + j × 365.25 days, for j = 3, 4, 5, …
- Decision days: D = S_j + 400 days, and D = S_j + 765 days.
- Every combination with D ≤ 2021-12-31 is used.

### Pseudo-history

- At D, take the frozen Stage C chain: the 13 original periods ending at the latest period visible at D, fresh within 200 days, with gaps of 80–100 days (`V3.chain_back`).
- Periods whose original filing day is earlier than S_j are **hidden**:
  - their labels are removed;
  - their accessions' facts are deleted from the evidence set;
  - their filings remain only as submissions rows (form, dates).
  This reproduces exactly the information available for a genuine pre-XBRL period.
- A pseudo-history is **evaluable** if:
  - all 13 periods have a true L0/L1 label;
  - at least one period is hidden.

### Trial

A trial is one hidden period of one evaluable pseudo-history. Its outcome is one of:
- **correct:** accepted and equal to the true label;
- **incorrect:** accepted and different;
- **abstained:** no label, conflict or unknown.

These are reported for R* (L2) and for each single method.

### History-level outcomes

- **True status:** LH-CP2 rule V applied to the true labels and the true transition and mapping flags.
- **Reconstructed status:** rule V applied to the labels available after hiding (L2 only), the same transition flag, and the mapping flag of the non-hidden periods.
- **False-valid:** reconstructed status is valid while the true status is not.

### Strata

Results are reported by each of:
- form (10-Q / 10-K);
- period year;
- 52/53-week registrant: any original period end more than 3 days from a calendar month-end;
- fiscal-transition registrant:
  - any 10-KT / 10-QT ≤ CUT; or
  - a *genuine fiscal change* in its true labels: rule P outcome "persistent_rebasing" or "multiple_off_cycle" on any 13-period window;
- hidden depth (1–4 / 5–8 / 9–12 hidden periods);
- pseudo-start year;
- entrant / leaver / stayer / not in the universe:
  - the registrant's E981-01 securities, through Data v2.1 identity;
  - entrant: first eligible month after 2011-01;
  - leaver: last eligible month before 2021-12.

### Pre-XBRL-like assessment

1. **M-SEQ** uses only fields that exist identically for pre-XBRL filings.
2. **M-CMP** evidence quality: compare a registrant's **first four** L0/L1-labelled filings with its later filings. The metric is the share of labels that are isolated off-cycle (one label off the cycle of its labelled neighbours on both sides). The real pre-XBRL evidence comes from the first XBRL filings.
3. **Header check V5** on genuine pre-XBRL filings (§7).
4. Error rates by pseudo-start year.

### Confidence intervals

Registrants are the independent units.
- **Label error rate:** registrant-cluster bootstrap (2,000 replicates, seed 20261018), one-sided 95% upper bound.
- **Registrant-level shares** (any wrong accepted label; any false-valid history): one-sided 95% Clopper–Pearson upper bound.
- **Zero observed errors** are reported with their upper bound, never as zero error.

## 6. Acceptance thresholds (frozen now, before any validation output)

All criteria are evaluated on the **held-back** set, for R* L2 labels.

| ID | Criterion | Minimum sample |
|---|---|---|
| V1 | Label error rate among accepted labels: cluster-bootstrap one-sided 95% upper bound ≤ **0.5%** | ≥ 300 registrants with an accepted trial |
| V2 | Share of registrants with ≥ 1 incorrect accepted label: Clopper–Pearson upper bound ≤ **2.0%** | Same as V1 |
| V3 | **Fiscal changes.** Among held-back registrants with a genuine fiscal change or a transition form inside the **hidden** part of an evaluable pseudo-history: share with any such history rated valid. Clopper–Pearson upper bound ≤ **10%** | ≥ 20 registrants |
| V4 | **First-year XBRL evidence quality.** The isolated off-cycle label rate in first-four filings is ≤ max(2 × the later-filing rate, later rate + 0.5 pp), and its cluster upper bound is ≤ **2.0%** | ≥ 200 registrants |
| V5 | **Header check on genuine pre-XBRL filings.** Among sampled filings with an R* L2 label and a usable header H-FYE quarter: disagreement rate ≤ (held-back XBRL-era benchmark disagreement of H-FYE vs L0 labels) + **5 pp** | ≥ 60 usable filings |

- **V4 scope:** V4 is computed on held-back registrants.
- **V5 if headers are unavailable:** if the network portion is blocked or stopped, V5 is "not evaluated".
- **Insufficient sample:** a criterion whose minimum sample is not met is "insufficient". It is neither pass nor fail.

## 7. Network sample (EDGAR headers)

### Population

- Distinct original 10-Q / 10-K accessions of chain periods whose label is still unknown after Part A, where the filing has no XBRL (submissions `isXBRL` = 0).
- The periods belong to label-unknown C1- or C2-complete histories of Stage C P2 stock-months in **2013 or 2014**.
- Every accession is filed ≤ 2021-12-31, and is filed ≤ D − 1 for every decision day that uses it.

### Strata and quotas (drawn in this order, without replacement)

| Stratum | Quota |
|---|---|
| Base: form {10-K, 10-Q} × filing year {≤ 2009, 2010, ≥ 2011}, 10 each, from accessions whose R* outcome is an L2 label | 60 |
| R* single-source | 10 |
| R* conflict or none | 10 |
| 52/53-week registrants | 10 |
| Fiscal-transition registrants (any 10-KT / 10-QT ≤ CUT) | 10 |
| Securities that are entrants (§5) | 10 |
| Securities that are leavers | 10 |

- **Total:** 120 accessions.
- **Ordering:** within each stratum, by sha256("LH-CP3-sample|" + accession).
- **Registrant cap:** at most 2 accessions per registrant over the whole manifest.
- **Short strata:** a stratum with fewer eligible accessions takes all of them. There is no top-up from other strata, and no replacement after outcomes are seen.

### Request budget and conduct

- At most **150 HTTP requests**, counting retries and fallbacks; at most 2 per second (minimum interval 0.6 s).
- **Fallback:** if `<accession>.hdr.sgml` returns 404, one bounded streaming read of `<accession>.txt` follows, stopping at `</SEC-HEADER>` or 64 KB, whichever comes first.
- **Backoff:** 429 / 5xx responses back off for 2 s, then 4 s, then 8 s; at most 2 retries.
- **Blocking:** a 403 or any block stops the network portion immediately.
- **User-Agent:** the existing authorised configuration (`sec_edgar.contact_user_agent`, read at run time; never written to the repository or logs).
- **Cache:** responses are cached under `data/sec_cache` (outside Git; re-acquirable).
- **Request log:** accession, URL, local filing date, HTTP status, bytes read, time. Committed as `LH_CP3_request_log.json`.
- **Committed metadata:** the extracted header fields (§7 list) are committed as `LH_CP3_headers.json`.

### Header fields read

- ACCESSION NUMBER
- CONFORMED SUBMISSION TYPE
- CONFORMED PERIOD OF REPORT
- FILED AS OF DATE
- DATE AS OF CHANGE
- ACCEPTANCE-DATETIME
- the filer CIK
- FISCAL YEAR END
- FORM TYPE
- FORMER COMPANY name-change dates (only the dates ≤ CUT)

Nothing else is read.

### Header checks reported

- whether the period of report equals the submissions report date;
- whether the form agrees;
- whether the header fiscal-year end differs from the current-status code;
- the H-FYE quarter versus the R* label (V5) and versus each single method.

## 8. Rule P review (proposal only; not applied to any official coverage)

Measured outcomes:
1. Rule P strict / assume outcomes on held-back pseudo-histories, compared with the true status.
2. **Boundary weakness.** Count all-registrant 13-period windows with exactly one isolated off-cycle label at position 0 or 12. Each is classified ex-post (labels ≤ CUT) as a genuine re-basing or a reverting mis-tag by extending the window by 4 periods on that side.
3. **Interior isolated labels.** The same ex-post classification for single off-cycle labels at positions 1–11.

Rule P is not changed, either to improve coverage or otherwise. Any suggested revision is described with its accounting justification and left to the owner.

## 9. Stage C population (P2) histories and scenarios

### Rebuild and reproduction check

- P2 is rebuilt exactly as in LH-CP2.
- The C1 / C2 / C6 coverage must reproduce `LH_StageC_audit.json` exactly; otherwise STOP.
- **Denominator:** non-financial eligible stock-months of the **E981-01 (Data v1) universe**, unchanged. The Data v2.1 per-stock-month universe was never exported, and the difference is disclosed.

### History classes (per C1 / C2 / C6-complete stock-month)

| Class | Definition |
|---|---|
| Verified valid | Rule V valid with L0 + L1 labels, and no identity flag |
| Verified invalid | Rule V invalid with L0 + L1 labels: label-broken, transition or mapping failure |
| Conditionally valid B | Valid only with L2 labels (assumption: the R* error rate and no undisclosed fiscal change); no identity flag |
| Conditionally valid C | Valid only with L3 labels, or carrying the identity flag |
| Invalid (reconstructed) | Broken once L2 / L3 labels are added |
| Unknown | Everything else, including conflicts |

### Scenarios (C1, C2, C6; annual 2013–2021; denominator, numerator, share, minimum year, 70% floor)

| Scenario | Includes |
|---|---|
| A | Verified valid |
| B | A + conditionally valid B, **only if R* is validated** (§10 class A or B). Otherwise B = A, labelled "R* not validated" |
| C | A + conditionally valid B + conditionally valid C (sensitivity only) |
| D | The LH-CP1 original coverage (copied, unchanged) |

### Composition reported for each scenario

- FF12 sector;
- size tercile (SEC total assets at the anchor, as in LH-CP2);
- registrant age;
- entrant / leaver shares.

### Selection bias

Among label-unknown (L0 + L1) C1-complete stock-months, those **recovered** (verified or conditionally valid under B) are compared with those **unrecovered**, by:
- anchor year;
- FF12 sector;
- registrant age;
- entrant / leaver status;
- size tercile;
- history depth (original periods before the chain's oldest period).

## 10. Final classification (mechanical)

Let the **resolution share** be the share of LH-CP2 label-unknown C1-complete stock-months whose history becomes verified valid, verified invalid, conditionally valid B or invalid (reconstructed).

| Class | Rule |
|---|---|
| D — INSUFFICIENT EVIDENCE | V1's minimum sample fails, or at least two of V3, V4 and V5 are insufficient or not evaluated |
| C — METHOD NOT VALIDATED | Not D, and any evaluated criterion among V1–V5 fails |
| A — RECOVERY METHOD VALIDATED | V1–V5 all pass (none insufficient or not evaluated), and the resolution share is ≥ 90% |
| B — PARTIAL RECOVERY | Otherwise |

- **A does not make OF-A feasible.** It does not change Stage C or LH-CP2.
- **Exceptions** require an owner decision.

## 11. Outputs

All under `research/longhorizon/cp3/`:
- `lh_cp3_safe.py` and `lh_cp3_rules.py`, with tests in `tests/test_lh_cp3.py`;
- `LH_CP3_part_a.{py,json}`;
- `LH_CP3_validation.py`, giving `LH_CP3_development.json` (development) and `LH_CP3_final.json` (held-back + V5 + scenarios);
- `LH_CP3_rules_freeze.json`;
- `LH_CP3_manifest.{py,json}`;
- `LH_CP3_fetch_headers.py`, `LH_CP3_request_log.json`, `LH_CP3_headers.json`.

The checkpoint is `docs/checkpoints/LH_CP3_missing_fiscal_labels_recovery_validation.md`.
