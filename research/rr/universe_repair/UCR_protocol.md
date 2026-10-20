# Universe Repair + Re-audit UCR-1 — frozen protocol (owner D269, RR5 / UR-2 option A)

**Status:** FROZEN before any upload or run. The SHA-256 of this file is pinned in `qresearch.rr_ucr` together with:
- the host `strategies/X806_universe_repair_reaudit/main.py`;
- the repair module `src/qresearch/lean/qr_ucr.py`;
- the frozen SCA-1 audit module `src/qresearch/lean/qr_sca.py` (unchanged since SCA-1);
- the point-in-time SEC builder `research/rr/universe_repair/build_ucr_sec.py`;
- the offline evaluation rule `research/rr/universe_repair/UCR_eval.py`;
- the two public SEC objects (`rr/ucr_sec_v1.json` new; `rr/sca_sec_v1.json` = the SCA-1 object, unchanged).

**Scope (D269):**
- ONE repair implementation and ONE re-audit run: E806-01. E806-02 only as a single retry after a documented infrastructure failure.
- Existing resources only. No purchase, no subscription change, no strategy backtest, no Holdout, no H031 run.
- The approved universe rule is unchanged: US common stock, NYSE / Nasdaq / AMEX, point-in-time market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M.
- No threshold of SCA-1 is relaxed.
- **If the result is FAIL or INCONCLUSIVE: STOP.** No further repair, no window shortening, no relaxation, no accepted bias.
- RR5 / SCA-1 (E805-02) evidence stays as recorded; nothing in it is edited.

## 1. Question

Can securities that the vendor universe misses for **data** reasons be put back with **strictly point-in-time** public SEC data so that the 2010–2021 universe passes the unchanged SCA-1 rule?

## 2. Inputs

### 2.1 Point-in-time SEC object `ucr_sec_v1.json` (drives the repair)

- **Source:** the same local public SEC cache as SCA-1 (XBRL RSS filing index, companyfacts). No new source, no network, no QuantConnect output.
- **Why a new object (D270):** the SCA-1 object stores retrospective ticker windows (filings up to 100 days after t) and whole-history exclusions. D269 forbids both for a repair. The new object stores **one record per periodic filing**, with only what that filing made public on its filing date.
- **Per registrant (CIK):**
  - `p`: periodic filings (10-K, 10-Q, their /A and transition forms) as `[filed, prefix, common_ok, shares, cover_end]`:
    - `prefix` = that filing's XBRL instance prefix (the ticker the company itself used in that filing), normalised;
    - `common_ok` = that filing's own company name and SIC pass the SCA-1 non-common rules (partnership / LLC / fund / ETF / trust forms, blank-check, investment vehicles; REITs SIC 6798 kept);
    - `shares` = that filing's non-dimensional `EntityCommonStockSharesOutstanding` when **exactly one** value is reported (several values = multi-class or ambiguous → none);
    - `cover_end` = that value's as-of date.
  - `f`: public-float facts `[filed, as_of, value]`, kept only if plausible with information known at that filing (float per cover share $0.10–$5,000 with the same filing's or the latest earlier filing's shares within 200 days; otherwise float ≤ 100 × the largest total assets filed up to then).
- **Population:** periodic XBRL filers with at least one float fact ≥ $0.5B. The in-cloud rule requires a point-in-time float ≥ $0.5B, which implies membership, so the screen adds no look-ahead.
- **Counts** (manifest `ucr_sec_v1_manifest.json`): 3,858 registrants; 126,255 periodic filings (5,527 not common; 113,936 with a single cover-share value); 825 float facts dropped by the unit filter.

### 2.2 SCA-1 measurement object `sca_sec_v1.json` (measures only)

- Unchanged from SCA-1, SHA-256 pinned in `qresearch.rr_sca`.
- Used **only** to measure what is still missing, with the frozen SCA-1 audit. It never selects, repairs or admits a security.
- Its retrospective ticker evidence therefore never enters the repaired universe. It is kept because a re-audit must use the same instrument as the audit (comparability).

### 2.3 In-cloud (generated in the run, never exported)

QuantConnect identifiers, tickers (`symbol.value` on that day), raw prices, ADV20 (the harness rule), vendor category and vendor market cap, and the split factor of each security observed daily from 2009-05-01.

## 3. Repair rule at a decision point t (the month-end session, 2010-01 … 2021-11)

Only SEC filings filed **strictly before t** and QuantConnect values observed **on or before t** are used.

### 3.1 Host category (unchanged SCA-1 definitions)

E (vendor cap ≥ $2B, eligible), A_lt (vendor cap < $2B), M (common, approved exchange, cap missing), X (other exchange), B_blank (blank exchange / security-type fields, nothing marking it non-common), B_explicit (fields mark it non-common), N (no fundamentals object), I (illiquid: price < $5 or ADV20 < $5M or fewer than 20 volume days).

**Repairable categories: N, M, B_blank only.** E / A_lt are used for validation only (§3.4). X, B_explicit and I are never repaired.

### 3.2 Point-in-time identity (unique, documented)

For each registrant r:
1. **Alive:** r's latest periodic filing filed before t is at most 200 days old. Otherwise r is not considered.
2. **Current ticker:** the prefix of that latest filing. No earlier or later filing's ticker is used.
3. **Common at t:** that latest filing's `common_ok`. Otherwise counted `registrant_not_common_pit`.
4. **Unique claim:** the prefix is claimed by exactly one live registrant at t (else `contested_prefix`, all claimants rejected).
5. **Unique QuantConnect match:** exactly one security passed to selection at t has the normalised ticker equal to the prefix (else `no_qc_ticker` / `ambiguous_qc_ticker`).
6. **Class shares:** a QuantConnect ticker containing '.' or '-' (a share class) is rejected (`multi_class_ticker`).

Weak or ambiguous matches are never admitted. Nothing labelled "possible" in SCA-1 is admitted because of that label.

### 3.3 Point-in-time market cap and plausibility

For a uniquely matched security in N / M / B_blank:
1. **Shares:** the single-value cover-share count of the latest filing with such a count, filed at most 200 days before t (`no_fresh_shares`). Multi-class filers with several values never have one.
2. **Splits:** the split factor must be known (`split_factor_unknown`). If QuantConnect's split factor for the security changed on or after the cover date, the count is stale relative to the raw price → rejected (`split_since_cover`). No split adjustment is computed.
3. **Float:** the latest float fact filed before t with an as-of date at most **650 days** before t must be ≥ $0.5B (`float_missing_or_below_0.5B`).
   - Why 650 and not SCA-1's 456: the float is measured at the end of the second fiscal quarter and first published in the next 10-K (due 60–90 days after year-end), so a timely filer's latest float is up to about 6 + 12 + 3 months (~640 days) old. Found in a returns-blind pre-freeze check: with 456 days only 427–511 of about 2,700 live registrants had a usable float at the October–December 2012 month-ends (2,235 at September; 2,476–2,489 with 650 days). Recorded in D270.
4. **Cap:** cap = cover shares × QuantConnect's raw price at t. Admitted only if cap ≥ $2B (`cap_below_2B`) **and** 0.5 ≤ cap / float ≤ 10 (`identity_band_fail`; the SCA-1 strong-evidence band, used here as an identity / unit plausibility check).
5. Admitted rows enter the universe at t with this cap (`repaired`, by category). Price ≥ $5 and ADV20 ≥ $5M are already met (category ≠ I).

### 3.4 Repair-rule validation (independent vendor values)

The same rule (§3.2–3.3) is applied in **shadow** to uniquely matched vendor-capped securities (E and A_lt) whose SEC cap / float lies in the band:
- `validation_n`, agreement with the vendor at $2B (`validation_agree_2B`), within 5%, within 2×.
- The vendor cap is an independent measurement of the same quantity, so this is the rule's out-of-sample accuracy check.
- **Required per year:** n ≥ 30 and agreement ≥ 95%. Otherwise the year cannot PASS.

### 3.5 Exchange requirement (disclosed proxy)

- N and blank-exchange names carry no vendor exchange. QuantConnect's US equity data covers exchange-listed securities only, so OTC names cannot enter. A primary listing on NYSE Arca or Cboe BZX cannot be told apart point-in-time from SEC filings for 2010–2018.
- **Rough measure:** among uniquely matched vendor-classified securities, the share in X (`other_exchange`) relative to E / A_lt matches. Reported, not gating.

## 4. Re-audit (unchanged SCA-1 instrument and thresholds)

The frozen SCA-1 audit runs twice in the same run, on the same rows:
- **A0:** the original vendor universe (as SCA-1);
- **A1:** the repaired universe (repaired rows become E with the SEC cap).

**Year verdict** = `qr_ucr.reaudit_verdict`:
1. The SCA-1 year rule (`qr_sca.year_verdict`, unchanged: Gap_C > 3% or b_C point > threshold → FAIL; PASS needs Gap_max ≤ 3%, the survivorship upper bound (b_CP + max(0, b_U)) ≤ threshold, reach ≥ 80%, agreement ≥ 95%) on A1's record.
2. Reach and agreement are taken from **A0**: repaired names would otherwise validate themselves.
3. Unless FAIL: the repair validation of §3.4 must hold (n ≥ 30, agreement ≥ 95%), else INCONCLUSIVE.

**Windows:** W1 2010-01 … 2021-11 is the decision (FAIL if any year FAILs; PASS if every year PASSes; else INCONCLUSIVE). W1a 2011–2021 and W1b 2016–2021 are reported only (as in SCA-1).

**Also reported, never gating:**
- **Exits of repaired stock-months:** exit-rate difference vs the matched E stock-months over the same horizon (24 / 12 months), with the security bootstrap (B = 1,000, seed 20261020).
- **Snapshot check:** A0's E counts vs E805-02.
- **External reference:** A1's E counts vs Data v1 (2011–2017) and Data v2.1 (2018–2021) from the RR4 reconciliation.
- **In-run vs offline:** `UCR_eval.py` re-derives every year verdict from the exported records; any mismatch is reported.

## 5. Interpretation

- **PASS** (W1): the repaired 2010–2021 universe meets the unchanged SCA-1 rule in every year, and the repair rule is validated each year. The checkpoint may then recommend freezing the programme protocol (owner decision).
- **FAIL / INCONCLUSIVE:** the universe-bias risk is still not shown to be acceptably bounded. **STOP** (D269). Nothing is repaired further, no window is shortened and no bias is accepted by Claude.
- Every outcome STOPS for owner review. A QuantConnect compliance refusal STOPS the work, with no workaround.

## 6. Independence of the evidence

| Finding | Evidence base |
|---|---|
| Repaired caps (§3.3) | SEC cover shares × QuantConnect raw price; identity from the company's own filings |
| Repair-rule accuracy (§3.4) | **Independent:** vendor market caps of the same securities |
| Remaining confirmed / possible / unresolved (§4) | The SCA-1 SEC object: **same SEC sources** as the repair (not independent) |
| Survivorship of repaired names | QuantConnect exits (independent of SEC) |
| External reference counts | Data v1 (old vendor dataset + our earlier SEC layer: **partly the same SEC sources**) and Data v2.1 |

## 7. Exported aggregates

- **Per year:** A0 and A1 SCA-1 records (counts, gaps, survivorship, instrument); repair reason counters and validation counters; repaired stock-months and securities; repaired-exit statistics; verdict and reasons.
- **Per window:** outcome. **Run:** both SEC objects' SHA-256, timings, experiment id.
- **Excluded:** no identifier, ticker, CIK, per-security value, price or return.

## 8. What this run does not do

- No strategy, order, return or performance figure. No Holdout data (the run ends 2021-12-31).
- No change to SCA-1, its object, or any frozen experiment. No change to any approved universe threshold.

## 9. Known limits (stated before the run)

1. **2010 reach:** XBRL for large accelerated filers with $2–5B float started with periods after 2010-06-15, so few ≥ $2B registrants have per-filing data in early 2010 (472 registrants have a periodic filing within 200 days on 2010-06-30). 2010 may therefore stay FAIL or INCONCLUSIVE even after the repair; W1 would then not PASS.
2. **Unresolved floor:** SCA-1's unresolved class (2–2.5% of eligible stock-months a year) is measured with retrospective tickers and is largely not repairable under the strict PIT rule. Gap_max ≤ 3% may therefore be unattainable in some years: the result may be INCONCLUSIVE even if the repair works.
3. **Exchange proxy** (§3.5).
4. **Multi-class:** filers with several cover values, and class-share tickers, are not repaired (conservative). A filer reporting one class's count only understates its cap (conservative), guarded by the cap / float band.
5. **Split history before 2009-05-01** is not observed; cover dates are at most a few weeks before filing, and filings are at most 200 days before t ≥ 2010-01-29, so the exposure is small.
6. **One data snapshot** (D202): the snapshot check against E805-02 is reported.
7. **SCA-1 instrument float age:** the frozen SCA-1 audit keeps its 456-day float rule (not changed: it is the measurement instrument). From about October to January, most December-year-end registrants therefore have no usable float in the audit, so SCA-1's **strong** evidence (confirmed) moves to **weak** (possible) in those months. Gap_C is understated and Gap_CP / Gap_max are unaffected. PASS needs Gap_max ≤ 3%, so a PASS is not made easier; a year could read INCONCLUSIVE where a correct instrument would read FAIL. The same applies to RR5's E805-02 (its 2010–2015 FAIL stands, since C is a lower bound).
8. **Sources:** C / P / U after repair are measured with the same SEC sources as the repair (§6). The only fully independent checks are the vendor-cap validation and QuantConnect exits.
