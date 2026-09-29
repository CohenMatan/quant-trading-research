# Checkpoint 4b: infrastructure fixes after Research Cycle 1

| Field | Value |
|---|---|
| Status | **STOPPED. Awaiting owner approval before designing Research Cycle 2 (C02).** No new hypotheses and no strategy backtests have been started. |
| C01 | **Closed: No Production Candidate Found** (owner, D060). H005 v1.2 is not promoted further. |
| Tests | 267 passing |

## 1. D057: what changed (universe classification; decision D061)

**Problem.** Morningstar labels some closed-end funds, business development companies (BDCs) and partnership/LLC units as "common stock", so they entered the ≥ $2B universe.

**Change.** The harness's `is_us_common` now also calls `non_common_reason(security, date)`. It excludes:

| Rule | Excludes |
|---|---|
| Partnership flag, or a share class described as partnership units | MLPs such as BPL, MMP, PAA, WPZ, OKS; TGP |
| LLC flag **and** a share class described as LLC, or a share class "LLC … Class/Units" | OAK, MIC, KMR, ENLC, EEQ, FIG, MGP, CPNO, CQH; FTAI |
| Morningstar investment-vehicle template ("V") | Closed-end funds (NEA, NVG, NZF, DSL, BCAT, UTG, EVV, RVT, BXSL) and BDCs (MAIN, GBDC, FSK, ORCC, PSEC, HTGC, GSBD, AINV, CCT) |
| SIC 6726 / 6770 / 6792 | Closed-end fund offices, blank-check companies (SPACs), oil royalty trusts |
| A small dated override table | Yahoo is common until it became the fund Altaba (June 2017); Blackstone from 2019-07-01 and Carlyle from 2020-01-01 (before that, partnership units); Burford (operating company); ACAS (BDC) |

**A trap avoided.**

- Morningstar's company flags describe a company's **current** status, not its status on each date.
- Many ordinary corporations that were later acquired are now flagged "LLC", for example VMware, Sprint, BNSF, Level 3, Molex and Pandora.
- Excluding on that flag alone would have deleted acquired companies from history, which is a new survivorship bias. So the LLC rule also requires the share class to be LLC units. The corporations stay eligible.
- REITs, including those organised as trusts, stay eligible.

**Audit of other security types.**

- The probe E956-01 recorded Morningstar's classification of every security the old rule admitted, monthly from 2010 to 2021.
- **Known residuals:**
  - KFN (KKR Financial Holdings LLC) still passes, because its share-class record carries an old corporate name.
  - Because the flags describe current status, companies that converted *from* partnership or LLC to corporation are handled only where listed in the override table (Blackstone, Carlyle). KKR (converted 2018) and Apollo (2019) are flagged as corporations for their whole history.
- Depositary receipts and foreign secondary listings stay excluded as before (D030).

## 2. D059: what changed (dead positions; decision D062)

**Problem.** Some acquired companies get no delisting event in QuantConnect's data. The holding stays frozen at its last price and its sell order never fills (OAK, BPL in E005-28).

**Change.** The harness counts trading sessions and records each security's last **real** price bar (not a filled-forward one). If a held security has had no real bar for more than 10 sessions:

- it is taken out of the portfolio at **its last real close from the data stream**, the same price LEAN uses for a delisting. **No price is invented.**
- $7 commission is charged.
- Its open orders are cancelled and never re-issued.
- The event is logged (`QRSTALE`) and mirrored in the local accounting.

**It fails loudly:**

| Situation | Result |
|---|---|
| Any fallback exit | Run marked `completed_with_warnings`, with every exit listed |
| An order still open more than 10 days before the end (checked independently from QuantConnect's order records) | **FAIL** |
| A dead holding with no known real price | **FAIL**; the position is not closed at a made-up price |

## 3. D063: found during the C01 audit, fixed (decision D063)

**Problem.** A security picked at the close that left the universe overnight lost its price history before its buy filled the next morning. Exit rules that read price history then never saw the position.

**Effect in C01.** Every H001 run (S001's exits read price history) ended with **7 to 15 of its 15 slots stranded**, some since 2010. H002–H005 are unaffected: their exits come from rebalancing or a day count.

**Change.**

- A security's history is kept while an order for it is pending.
- As a daily safety net, any holding found without history gets its point-in-time history reloaded. The event is counted and flagged with a warning.

## 4. Tests proving the fixes

| Fix | Automated tests (all passing) | End-to-end verification run |
|---|---|---|
| D057 | 68 real Morningstar classification records (`tests/test_universe_classification.py`), covering the named examples MIC, NEA, NVG, NZF, DSL, BCAT, UTG, BPL, OAK and other funds, BDCs and partnerships (excluded), acquired corporations flagged LLC today, REITs and EXC/BAC (eligible), and the dated Yahoo/Blackstone/Carlyle cases | **E956-02**: 90 securities removed from the 2010–2021 universe, none added. No partnership-flagged or fund-template security remains, except the four dated overrides. All named examples absent. Controls present. |
| D059 | Replays of OAK (filled-forward data after the deal) and BPL (no data at all): exit on the 11th session without data, at the last real close. A 10-session gap is not terminated. No real price means no exit and a failed run. Local mirror closes the trade and reconciles cash. A never-filling order fails the run (`tests/test_stale_holdings.py`). | **E957-01 canary**: held 9 securities that die without a delisting event (CPNO, SEP, VLP, ELLI, APU, OAK, BPL, EQM, HOME). All 9 were taken out 11 sessions after their last real price at that price. OAK's stuck sell was cancelled. TIF was delisted normally by LEAN. KO was held to the end. No order was left open. |
| D063 | Window kept while a buy is pending; missing window restored and flagged (`tests/test_window_retention.py`) | Unit tests only. An end-to-end proof needs a strategy run, which you have not approved yet. |
| Regression | Timing canary **E950-07** passes all checks. **SPY E900-07** is unchanged. | **Equal-weight benchmark E901-06** passes every hard check. It is marked "with warnings" for 4 fallback exits, which is the intended behaviour: HCBK 2015, ELLI 2019, ADSW 2020, HOME 2021. |

## 5. Did any C01 in-sample conclusion change?

The audit covered all C01 research runs, re-checked with the **new** code and data, not the earlier audit: `research/audits/C01_D057_D059_D063_audit.csv`.

**D057: every C01 in-sample run held securities the corrected universe excludes.**

| Hypothesis (final runs) | Share of capital in excluded securities | Their net P&L |
|---|---|---|
| H001 | 5–20% (mostly energy partnerships) | −$3.9K to +$2.8K |
| H002 | 1–2% | |
| H003 | 3–5% | |
| H004 | about 2% | |
| H005 | 5–6% (funds, BDCs, partnerships) | −$4.8K to −$0.6K |

- The equal-weight benchmark re-run on the corrected universe barely moves: IS Sharpe 0.915 → 0.921, CAGR 13.7% → 14.0%, max drawdown −22.1% → −22.3%.
- **Conclusion unchanged for H002, H003, H004 and H005.** H002–H004 failed the in-sample gates by margins far larger than these holdings. H005 passed in sample and then failed Validation, which is final.
- All affected runs carry `flagged` registry annotations.

**D059: no C01 in-sample run was affected.**

- Re-run on the corrected universe, the new data-based detector found four securities in the equal-weight benchmark that died without a delisting event (HCBK 2015, ELLI 2019, ADSW 2020, HOME 2021). Only HCBK falls inside 2010–2017, and no C01 run held it at the time.
- The earlier order-based audit had missed HCBK and ADSW entirely. The new detector is stronger.

**D063: the H001 conclusion changes.**

- H001's C01 runs are **not a valid test** of the hypothesis. Up to all 15 slots were stranded. H001's reported CAGR, Sharpe and gate failures reflect accidental buy-and-hold positions, not the rule.
- **H001's C01 verdict changes from "fail" to INCONCLUSIVE (implementation bug).**
- All H001 runs are annotated `bugged`; nothing was deleted.
- Re-testing H001 would need a new, approved research step. It has not been started.

**C01's final outcome is unchanged: No Production Candidate Found.**

## 6. Confirmations

- **C01 remains closed.** H005 v1.2 was not promoted, retuned or re-run on 2018–2021. E005-28 is annotated: Validation FAIL under the pre-declared gates, and not a faithful implementation from late 2019 onward because of D057/D059.
- **Validation and Holdout data were not used for strategy tuning.**
  - No strategy parameter or rule changed.
  - The only 2018–2021 runs in this step are infrastructure probes and canaries that trade no strategy (E956-02, E957-01), plus the benchmark re-runs (E950-07, E900-07, E901-06).
  - Nothing after 2021-12-31 was accessed.
- **All experiment history is preserved.** 62 annotation rows were added for D057 and D063, and nothing was overwritten.
- **Record-keeping note (D064).** The D063 code was accidentally committed under the label "E956-02: official run", because a queue auto-commit swept the working tree. Run records confirm each verification run used the intended code. History was not rewritten.

## 7. Decision needed

Approve these infrastructure fixes, and decide whether and how to design **Research Cycle 2**. That includes whether a corrected H001 should be re-tested in sample as part of it.
