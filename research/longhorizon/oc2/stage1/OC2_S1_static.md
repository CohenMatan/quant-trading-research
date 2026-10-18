# OC-2 Stage 1 — Part A: static audit of the frozen F5 definition

**Protocol:** `OC2_S1_protocol.md` §1 (SHA-256 91da6f27…, committed in 819a7a1 before any aggregate).
**Method:** reading frozen code and specifications only. No data were read.

## Sources read (SHA-256 prefixes)

| File | Role | SHA-256 |
|---|---|---|
| `research/phase14/data_v3/DATA_V3_spec.md` | Frozen Data v3 specification (§2 fields, §4 view, §5 signals) | b4b8aa9b1c212e98 |
| `research/phase14/data_v3/data_freeze_v3.json` | Data v3 freeze manifest | 601d00623e97696b |
| `research/phase11/data_v21/data_freeze_v21.json` | Data v2.1 freeze manifest (the store under Data v3) | ef0a7a66f5ff1e74 |
| `src/qresearch/lean/qr_v3.py` | `signals()`, `V3Overlay.view()` | 40bcf98d3aa62f62 |
| `src/qresearch/lean/qr_h029a.py` | `Window`, `chain`, `ttm_at`, `_ratio_change` | 3cff1e0361fdae6b |
| `src/qresearch/lean/qr_fundamentals.py` | `PITStore.ttm_detail` / `_chain` (the frozen True-TTM rule, D113 / D114) | 0774343f24820ce4 |
| `src/qresearch/data_v3.py` | SEC-side reference construction `sec_signals` (validation only) | 6495dc021d692ef0 |

## The eight items (owner D248 §2)

1. **Formula.** F5 = NI_TTM(q0) / TA(q0) − NI_TTM(q4) / TA(q4). Oriented "+ = improvement". This is `qr_v3.signals` → `qr_h029a._ratio_change(a0, t0, a4, t4)` = a0 / t0 − a4 / t4.
2. **Fields.**
   - `net_income_q`: the vendor quarterly net income, guarded by guard v3;
   - `net_income_ttm`: the vendor fiscal-year total, used for reconciliation only;
   - `total_assets`: the vendor balance-sheet snapshot, guarded by guard v2.1 and v3.
3. **TTM construction** (`qr_h029a.ttm_at` = frozen `PITStore.ttm_detail`):
   - the four records ending at the reference record, on the net-income base history (visible records, including SEC-verified partial releases that carry `net_income_q`);
   - consecutive: every period-end gap is 80–100 days;
   - each has a quarterly value;
   - **and** a fiscal-year-end record inside the window (its `_ttm` changed from the previous record) whose own four consecutive quarters sum to that fiscal-year total within 1%. Otherwise the TTM is missing.
   - No interpolation or back-filling.
4. **Comparison period.**
   - `Window` grid: the visible full records of the v3 view, sorted by period end, anchored at the current report q0.
   - `span(8)` requires 8 consecutive grid records (q0 … q7, gaps of 80–100 days).
   - q4 = the record 4 positions before q0, so the two TTM windows are [q3 … q0] and [q7 … q4]: adjacent and non-overlapping.
   - TA snapshots are taken at q0 and q4.
5. **Missing / denominator rules:**
   - `no_fresh_report`: q0 is more than 200 days old, or q0 is not in the grid;
   - `short_history` / `not_consecutive`: the 8-quarter span fails;
   - `ttm_missing`: either TTM is missing (including a failed reconciliation);
   - `field_missing`: either TA snapshot is missing;
   - `denominator`: TA0 ≤ 0 or TA4 ≤ 0.
   - Net income may be negative. Nothing is imputed, winsorised or clipped.
6. **Availability** (Data v3 spec §2; Data v2.1 M2):
   - a vendor version is usable from max(first seen in QuantConnect's stream, original SEC 10-Q / 10-K / 10-KT filing + 1 day);
   - matched to the SEC period within ± 6 days by the frozen identity `Identity.m2` / `Reference.match`;
   - computed on the selection day (the calendar day after the review session) and traded at the next session's open.
   - `Window` counts records dated after today (must be 0).
7. **Guards:**
   - Data v2.1 restatement guard (quarterly revenue, total assets; 0.5%);
   - **guard v3** (revenue, gross profit, **net income**, operating cash flow, **total assets**): a version carrying a later-filed restated SEC value (> 1.5% restatement, 0.5% match) that was not yet public is blocked. Its period falls back to the latest earlier clean visible version, or is removed (`V3Overlay.view`);
   - freshness 200 days;
   - quarantine / field-release rules (D114).
8. **Differences from OC-CP2's description** (§10 item 6):
   - **None in substance.** OC-CP2 states the formula, the 80–100-day chain, the 200-day freshness and the missing rules, and refers to Data v3 spec §5 for the rest.
   - It does not restate the 1% fiscal-year reconciliation inside each TTM, which is part of the frozen definition (item 3). This is an omission in the description, not a different definition. OC-2 uses the frozen code unchanged.
   - Two OC-CP2 statements are about the test, not the signal. Converting F5 to a cross-sectional percentile within U_H029 is test design. The coverage figures OC-CP2 quotes (valid median 753 stocks a month) are P14-CP1's **F5-A** on the Data v2.1 store, before guard v3. The Data v3 F5 uses the same formula on the v3 view, whose by-period coverage is P14-CP2's 62.8% / 81.7% / 80.6%.

**G-DEF: PASS.** The code, the frozen specification and OC-CP2 agree. The audit continues.

## What the definition does and does not require (the basis of Part B)

- **F5 does not require fiscal-quarter labels to match.** Each TTM is the sum of four consecutive quarterly flows, so seasonality cancels within each window. The comparison is between two adjacent twelve-month windows ending about a year apart. A quarter-aligned fiscal-year change therefore leaves both windows economically valid.
- This differs from OF-A's seasonal surprises (RM2 §11), which compare the *same fiscal quarter* across years and need its label.
- **What F5 does require:**
  - (a) each quarterly value is a genuine roughly three-month flow;
  - (b) the four quarters are contiguous;
  - (c) each window spans about twelve months;
  - (d) the two windows are adjacent;
  - (e) both belong to the same economic entity;
  - (f) every value was public on the decision day.
- **What the frozen rules protect:**
  - the 80–100-day gaps protect (b) and bound (c);
  - the 1% fiscal-year reconciliation tests (a) for the reconciled fiscal year;
  - M2 timing plus guard v3 protect (f);
  - identity M2 protects (e) at the version level.
- **Part B measures what the rules alone cannot show:**
  - window lengths;
  - fiscal-year changes and transition forms;
  - SEC-verifiable quarter durations, including derived fourth quarters;
  - identity changes inside the span;
  - PIT ordering.
