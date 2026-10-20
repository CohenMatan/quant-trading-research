# RR6 — UR-2 strictly point-in-time SEC universe repair + re-audit (E806-01)

**Date:** 2026-10-20 · **Decisions:** owner D269 (UR-2 option A), D270 (implementation, minor), D271 (this result) · **Status: STOP (hard stop, D269 §4)**

## Result

**W1 2010-01 … 2021-11: INCONCLUSIVE** (every year INCONCLUSIVE; no year FAIL, no year PASS). W1a and W1b: INCONCLUSIVE.

- The repair removed the **confirmed** bias that failed RR5: confirmed gap 3.5–6.1% → 0.2–0.8% a year; confirmed survivorship bias 0.25–0.78 → about 0.00 points.
- What remains is the **unresolved** population (SEC registrants with float ≥ $2B that no strictly point-in-time identity rule can tie to a QuantConnect security) plus the "possible" class. Under the unchanged SCA-1 thresholds this risk is **not shown to be bounded**.
- Per D269 this is the one authorised repair and re-audit. Nothing more is repaired, no window is shortened, no rule is relaxed and no bias is accepted. **STOPPED awaiting the owner.**

## The run

- **Frozen before upload or run:** commit a539555 — protocol `research/rr/universe_repair/UCR_protocol.md` (SHA-256 9280813d…), host X806, `qr_ucr`, builder, evaluation rule; pins in `qresearch.rr_ucr`. The SCA-1 module and object are unchanged.
- **New point-in-time SEC object** `rr/ucr_sec_v1.json` (SHA-256 ba3ab515…; D270):
  - built from the same public SEC cache as SCA-1, laid out one record per periodic filing;
  - uploaded once, plain JSON;
  - the run started 36 minutes after the upload.
- **E806-01:** completed on the first attempt, so the retry was not used.
  - QuantConnect default build **18198** (recorded; RR5 ran on 18194). The snapshot check found **0** difference in vendor-eligible counts against E805-02 in every year.
  - 0 orders, 204 s, aggregates only, compliance-accepted.
  - The offline re-derivation of every verdict agrees with the in-run verdicts.

## What the repair did (2010–2021)

| | Total |
|---|---|
| Repaired stock-months | **8,191** (no fundamentals object 7,118; cap missing 1,073; blank classification 0) |
| Repaired securities per year | 28–128 (most in 2011–2014) |
| Validation on vendor-capped securities (independent vendor caps) | 168,850 shadow repairs; **99.78%** agree on ≥ $2B (99.67–99.90% each year); 97.8% within 5% |

**Rejected or ambiguous matches** (stock-months, all years; none was admitted):

| Reason | Count |
|---|---|
| No QuantConnect security with that ticker | 27,152 |
| Latest filing not common stock | 16,017 |
| Cap below $2B (SEC) | 5,528 |
| Float missing or below $0.5B | 2,896 |
| Prefix claimed by two or more live registrants | 2,433 |
| Two or more QuantConnect securities with that ticker | 1,701 |
| No fresh single-value cover count | 1,570 |
| Class-share ticker | 307 |
| Cap / float outside 0.5–10 | 216 |
| Split since the cover date | 77 |

Repaired names are the disappearing names: their 24-month exit rate is 11–24 points above the vendor universe's.

## Re-audit by year (unchanged SCA-1 rule)

| Year | Confirmed gap (orig → repaired) | Gap C+P | Gap C+P+U | b_C points (orig → repaired) | b_U points [95% CI] | Survivorship upper bound vs limit | Repaired exit diff (pts) |
|---|---|---|---|---|---|---|---|
| 2010 | 3.5% → 0.2% | 3.0% | 3.5% | 0.25 → −0.01 | 0.09 [−0.00, 0.20] | 0.56 (0.50) | +11.5 |
| 2011 | 5.5% → 0.4% | 2.8% | 3.6% | 0.64 → 0.00 | 0.21 [0.07, 0.37] | 0.61 (0.50) | +14.3 |
| 2012 | 6.1% → 0.7% | 2.6% | 4.4% | 0.63 → −0.03 | 0.42 [0.21, 0.66] | 1.04 (0.50) | +12.4 |
| 2013 | 4.3% → 0.5% | 2.1% | 3.2% | 0.34 → −0.01 | 0.17 [0.03, 0.35] | 0.75 (0.50) | +12.0 |
| 2014 | 4.0% → 0.6% | 2.2% | 3.6% | 0.68 → −0.00 | 0.23 [0.04, 0.44] | 0.62 (0.50) | +21.3 |
| 2015 | 3.7% → 0.7% | 2.5% | 4.3% | 0.78 → −0.00 | 0.34 [0.14, 0.58] | 0.89 (0.50) | +19.3 |
| 2016 | 2.9% → 0.8% | 2.3% | 4.4% | 0.32 → 0.03 | 0.49 [0.25, 0.75] | 1.26 (0.50) | +12.8 |
| 2017 | 2.3% → 0.8% | 2.1% | 4.1% | 0.22 → 0.01 | 0.52 [0.27, 0.79] | 0.96 (0.50) | +15.5 |
| 2018 | 2.1% → 0.6% | 2.1% | 4.3% | 0.34 → 0.04 | 0.45 [0.22, 0.69] | 1.06 (0.50) | +20.6 |
| 2019 | 1.6% → 0.5% | 1.8% | 4.0% | 0.36 → 0.02 | 0.41 [0.17, 0.70] | 0.98 (0.50) | +24.3 |
| 2020 | 1.2% → 0.5% | 1.5% | 3.9% | 0.16 → 0.00 | 0.17 [0.01, 0.38] | 0.44 (0.25, 12-month) | +16.6 |
| 2021 | 0.4% | 1.3% | 3.5% | not assessable (censoring) | — | — | — |

Every year fails the PASS conditions in the same two ways:
1. Gap C+P+U above 3% (3.2–4.4%).
2. The survivorship upper bound is above the limit (2010–2020).

2010 also misses instrument reach (79.3% < 80%; a disclosed limit).

## Counts vs references (reported, not gating)

**Repaired vendor-eligible counts against the earlier universes:**
- **Data v1 (2011–2017):** the repaired count is **1.7–3.1% above** Data v1. The original vendor count was about 5% below it (RR4).
- **Data v2.1 (2018–2021):** 0.5–3.0% above.

**Why the excess is unexplained:**
- Data v1 had its own measured residual gap (about 0.5–1.2% a year, P2-CP7), which accounts for only part of it.
- The repaired names' caps are validated: 99.8% agreement against vendor caps.
- But their **identity and common-stock status are validated only by the same SEC filings**. Some over-inclusion therefore cannot be ruled out.

**Exchange proxy:**
- Among uniquely matched vendor-classified securities, 1.2–2.7% a year are on non-approved exchanges.
- By analogy, perhaps 2% of repaired stock-months (about 160) could be on such exchanges.

## Independent evidence vs the same SEC data

| Finding | Basis |
|---|---|
| Repaired caps are accurate (99.8% at $2B) | **Independent:** vendor caps of the same securities |
| Repaired names are disappearing names (exit +11..+24 points) | **Independent:** QuantConnect's own exit dates |
| Snapshot unchanged vs E805-02 | QuantConnect vs QuantConnect |
| Remaining confirmed / possible / unresolved; b_CP; b_U | **Same SEC sources** as the repair (SCA-1 object) |
| Identity and common-stock status of repaired names | **Same SEC sources** |
| Count comparison with Data v1 | Partly the same SEC sources (Data v1's SEC layer) |

## The owner's five questions

**1. Did the SEC repair work with strictly point-in-time data?**
Yes, within its stated limits:
- **What it used:** only filings filed before each decision day; the ticker of the latest filing; QuantConnect identifiers generated in the run; cover shares as of their filing date; a stale count after a split excluded; class shares and multi-value counts excluded; unique matches only.
- **What it achieved:** 8,191 stock-months restored, with independently validated caps. The confirmed bias that failed RR5 is gone in every year.
- **Disclosed limits:**
  - the float-age rule was corrected before the freeze (650 days, D270);
  - the exchange requirement holds only by proxy for names without vendor fields.

**2. Is the 2010–2021 universe now credible enough for research?**
**Not under the frozen rule: INCONCLUSIVE.**
- It is much better than the vendor universe: the confirmed gap is ≤ 0.8% and the confirmed bias is about 0.
- But the remaining possible plus unresolved population (3.2–4.4% of eligible stock-months) cannot be shown to be harmless.

**3. What measurable bias or uncertainty remains?**
- **Point estimates:**
  - confirmed bias about 0.00 points;
  - unresolved SEC-side bias 0.09–0.52 points a year (largest in 2012 and 2016–2019);
  - confirmed + possible point about 0.0–0.22.
- **Upper bounds:** confirmed + possible + unresolved 0.56–1.26 points a year against a 0.50 limit.
- **In words:** a plausible universe-level survivorship bias of about 0.2–0.5 points a year, and up to about 1 point at the upper bound.
- **Not quantified independently:** the 1.7–3.1% excess over Data v1, and the exchange proxy (about 2%).

**4. Is any additional repair actually necessary?**
- Under D269 none is authorised, and none was done.
- **What remains is mainly an identity problem, not a missing-data problem.** The unresolved registrants are those whose filed ticker matches no QuantConnect security under a strict point-in-time rule. They may be in the universe under another ticker, or not listed at all.
- A further repair would need point-in-time ticker history beyond the XBRL file prefix. Cover-page trading-symbol tags exist only from 2019, and nothing else in the free public SEC data supplies it. So more repair of this kind is unlikely to reach PASS.
- Whether to accept the residual, or reconsider the research design, is the owner's decision (D269 §4).

**5. Can we now freeze the programme protocol and proceed to the H031 event canary?**
**No.** The universe and window are not settled (INCONCLUSIVE):
- RR screen v2 stays approved in principle only, not frozen;
- H031 stays DRAFT;
- no canary or strategy run.

## Not done

- No further repair, retry, window change, threshold change or accepted bias.
- No strategy run, Holdout access, subscription or purchase.
- Nothing in RR5 / SCA-1 was changed.

**STOPPED awaiting the owner.**
