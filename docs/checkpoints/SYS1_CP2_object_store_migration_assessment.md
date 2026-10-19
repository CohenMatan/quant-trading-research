# SYS1-CP2 — Object Store migration assessment under QuantConnect Support's guidance

**Date:** 2026-10-19.
**Decisions:** D257 (owner: Support clarification and migration preparation, `docs/owner/2026-10-19_sys1_qc_support_clarification_migration.md`); D258 (this finding).
**Status:** documentation only. **STOPPED awaiting the owner.**

**Not done:**
- Nothing uploaded; no QuantConnect backtest; E032-02 not launched.
- No legacy project modified. No purchase. Holdout sealed.
- No change to the frozen SYS-1 protocol, H028, allocations, costs, benchmarks or gates.

## 0. Verdict

**Exact reproduction of frozen H028 is not achievable under Support's guidance (point 2).** As the owner instructed, I stopped before preparing a freeze, a migration or a canary that would imply otherwise.

**Why, in one paragraph:**
- Every stock's fundamentals, sector and SEC market-cap repair in the frozen chain pass through a **dated security-to-company identity table** (QuantConnect security id → SEC CIK and SIC). It covers 3,958 securities.
- That table was not built from SEC data alone. It was assembled offline from **earlier QuantConnect exports**:
  - the vendor CIK and dated-ticker export E970-01;
  - market-cap / float evidence from E971-02, E974–E978 and E976-03;
  - the E993-02 eligibility lists;
  - mostly produced on LEAN build 18131 and the old Morningstar dataset.
- **88% of its securities (3,470 of 3,958) carry a CIK that came from the vendor CIK or QuantConnect-derived evidence.** Only 488 rest on SEC ticker evidence alone, and even those need QuantConnect's dated tickers.
- Support says identifiers and universe membership must now be **generated inside the cloud** and that previously extracted QuantConnect data must not be reused. So the table cannot be uploaded.
- Regenerating it inside the cloud would need the same inputs. They cannot be obtained there any more:
  - build selection below the Trading Firm tier has been refused since 2026-10-06 (D180);
  - the old Morningstar dataset is retired on 2026-10-31;
  - the current default dataset differs materially. D183 / D187 showed missing market caps for about 18% of data-v1 stock-months, and different fundamental timing.
- Any difference for a single stock in the H026 population changes the pinned H026 feature / response panel digests. **C0 then fails and the E030-05 result ($328,294.91, 416 / 411 trades, $5,789 commissions) cannot be reproduced.**

**What is not impossible:** the SEC-only parts can be migrated compliantly (§1, §3–§5). What fails is the claim that the migrated chain *is* frozen H028.

## 1. Independently sourced SEC data that could be stored as plain JSON (item 1)

These are public SEC EDGAR data, keyed by SEC CIK. No QuantConnect identifier or value is involved.

| component | content | plain JSON |
|---|---|---|
| `f` | periodic-filing dates and D111 cover-page share counts, 3,941 registrants, 2008-03 → 2021-12 | 2.68M characters |
| `guard` | restatement guard (first-filed vs later SEC values), 2,172 registrants | 0.53M |
| `idv` | first-filed values for periods to 2010, 1,531 registrants | 0.23M |
| SEC correction filings | filing rows and 10 approved fundamental fields for the repaired registrants | about 1.70M |
| SEC SIC by filing | the SEC-assigned SIC per periodic filing (`sic_history.py` source) | small |
| SEC ticker evidence | instance-document prefixes per filing (`identity_v2.py` evidence T) | small |

**Total:** about 5–6M characters of plain JSON. One or a few objects, inside the free 50 MB Object Store tier.

**These would need re-keying.** The correction filings and SIC rows are currently keyed by QuantConnect security id. They would have to be keyed by CIK and filing.

## 2. Regenerating identifiers and universe membership inside the cloud (item 2)

**Mechanically possible:**
- Security ids come from the platform's own universe selection (`Fundamental` objects).
- Dated tickers come from each symbol's value on the day.
- The universe filters (US common, NYSE / Nasdaq, PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M) already run in-cloud each day.

**Not reproducible:** the identity rules the frozen table applied offline. Each depends on QuantConnect inputs that cannot be regenerated identically.

| frozen rule (builder) | QuantConnect input it used | regenerable identically in-cloud today? |
|---|---|---|
| native identity = vendor CIK, restricted to filings while it was the filer (`sic_history.py`) | vendor CIK from E970-01 (old dataset, build 18131) | **no**: today's vendor CIK comes from the current dataset (current-status field, D111); equality is unknown |
| predecessor rule needs market-cap evidence E971-02 'Q' (cover shares × close within 3% of PIT market cap) | data-v1 market caps | **no**: build 18131 cannot be selected; the dataset is retired |
| identity v2 (SEC ticker evidence T + uniqueness U + float fingerprints F) | dated tickers (E970-01) and float fingerprints (E971–E978) | tickers probably yes (map files); fingerprints **no** |
| tier merge, F2 rule (SEC float ≥ 10% of the canary's reconstructed market cap) | E976-03 reconstructed market caps (data-v1 canary) | **no** |
| identity extension `ext` (P7-CP5e): every security eligible under E993-02 or E993-03 | E993-02 eligibility (old build) | **no**; widening the scope would add rows |
| repaired set (495 securities without vendor fundamentals) | E970-01 "no fundamentals" flags (old dataset) | only on today's data; equality unknown |
| diagnostics `diag` (data-v1 membership, targets, residual lists) | E993-02 / P7-CP5e | not needed for H028 inputs; would be dropped |

A cloud regeneration would therefore be a **re-implementation of the identity pipeline on current data**. Its output may coincide with the frozen table for most securities. There is no basis to expect it to coincide for all of them, and C0 tolerates no difference.

## 3. Compressed modules, embedded datasets and encoded outputs (item 3)

**For the S032 chain:**

| item | type | needed replacement |
|---|---|---|
| `qr_data_v21.py` + `qr_data_v21_00..20.py` | embedded dataset, lzma + base85 | Object Store loader for the SEC JSON (§1) + in-cloud identity regeneration (§2) |
| `qr_p7_export.py` `pack` / `unpack` | zlib + base64 | plain helpers; the result emission path changes (§5) |
| result blocks (`QRG`, `QRSY`, and `QRHR` in S030) | compressed, base64, chunked through runtime statistics | summary results only, through the official export (§5) |
| ETF identifier constants in `qresearch.sys1` (SPLV / USMV ids from E970) | previously extracted identifiers | drop the offline id comparison; resolve in-cloud with `Symbol.create` only |

**Not in this chain but packed:** `qr_sec_data*`, `qr_data_v2*`, `qr_data_v3_*`, `qr_v3val_*`, `qr_h017_events*`, `qr_h025_events*`, `qr_p3_replay`, `qr_v3`. Each would need the same treatment before any reuse.

## 4. Minimal data-loading changes, if a non-reproducing successor were ever wanted (item 4)

For completeness only. This is not proposed as SYS-1.

1. **Replace** `qr_data_v21` with an Object Store reader: plain `json`, a SHA-256 check against a pinned manifest of the uploaded object, no compression import.
2. **Replace** identity / SIC / repaired-set construction with an in-cloud builder applying pre-registered rules to platform symbols plus the uploaded SEC evidence.
3. **Remove** `diag`.
4. **Remove** zlib / base64 from `qr_p7_export`.
5. **Emit** summary scalars only.

That means a new data version (for example "Data v4 — cloud-generated identity"), new host versions (X801 → X8xx; S028–S030 can no longer be byte-identical modules) and new pins.

The resulting H028-like sleeve would be **a new implementation on a different universe**. It is not frozen H028, and any test on it would be a new research decision, not the recovery of SYS-1.

## 5. Permitted result exports (item 5)

- Results should come only through QuantConnect's official backtest result export (statistics, orders, charts as provided).
- The frozen hosts instead pack compressed JSON into custom runtime-statistic chunks. **That channel should be treated as no longer acceptable** for new runs (Terms v1.5 §2.6(c)).
- Any future host should report a small fixed set of scalar summary results computed in-host. That covers:
  - terminal wealth, CAGR, volatility, MaxDD;
  - beta and capture;
  - the FS screen statistics;
  - yearly relatives as numbers;
  - digests.
- It should not report daily or monthly paths that reconstruct SPY / SPLV / USMV prices.
- The frozen SYS-1 output section (§13 of the protocol) would need an owner-approved amendment either way.

## 6. How exact reproduction would have been verified (item 6)

The verification design remains valid and would stay exact; nothing would be relaxed:

| check | requirement |
|---|---|
| C0 | H026 feature and response panel digests equal the pinned values (10a54163… / e1503f9c…) |
| C1 | E030-05: wealth $328,294.90847351257, commissions $5,789, 416 buys, 411 sells, slippage $8,330.209577810972, 84 pick lists |
| C2 / C3 | SPY $262,325.455801514 (and $524,676.2761604529 at $200,000), LV15 $220,156.03484878788 |
| integrity | PIT audit 0, determinism (a rerun identical), runner integrity checks |

The pass rule is exact equality. Because §2 makes C0 failure the expected outcome, the honest consequence is **STOP**, not a tolerance.

## 7. Historical changes in QuantConnect's data and behaviour (item 7)

Even with an identical identity table, these limit exact reproduction:
- **Build:** E030-05 ran on LEAN 18178; the default build has since moved to 18179 (P14-CP2). Build selection is gated (D180), so a rerun runs on whatever build is current.
- **Dataset:**
  - the new Morningstar dataset has been the default since 2026-10-10, and the old one is retired 2026-10-31;
  - fundamental timing and market-cap coverage differ (D183, D187).
- **Snapshots:**
  - QuantConnect's data snapshot can change within a day (D202);
  - dividends can be revised between days (CLAUDE.md quirks).
- **Compliance review:**
  - code exporting data for probing or validation is rejected (D185);
  - the summary-statistics channel with packed payloads may now fall foul of §2.6(c).

Any of these alone could break C0 / C1 on a rerun. The identity regeneration requirement makes failure close to certain.

## 8. Options for the owner

| option | what it means | assessment |
|---|---|---|
| **A. Close SYS-1 as PLATFORM BLOCKED** | record: not run; frozen H028 cannot be reproduced on QuantConnect under its current terms and Support's guidance; no verdict on the architecture | **recommended**: honest, no cost, preserves integrity |
| B. One identity-regeneration feasibility canary | build the in-cloud identity pipeline (§2, §4), then one approved infrastructure run that reports only whether C0 and C1 match exactly; nothing else computed or exported | low prior of success; large effort (several sessions); if C0 / C1 match exactly, the migration could proceed under a new freeze; if not, A |
| C. A new, cloud-native successor test | new data version, new hosts, a newly frozen protocol; a new research question, not the recovery of SYS-1 | needs a separate owner decision; not proposed here |

**Recommended next decision:** A — close SYS-1 as PLATFORM BLOCKED. B is reasonable only if the owner values a definitive answer enough to fund several engineering sessions against a low expected chance of an exact match.
