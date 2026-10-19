# SYS1-CP1 — SYS-1 Platform Recovery Feasibility — Options A and B

**Date:** 2026-10-19.
**Decision:** D255 (owner direction, `docs/owner/2026-10-19_sys1_platform_recovery_feasibility.md`).
**Status:** read-only, documentation-only assessment. STOPPED awaiting the owner.

**Nothing was uploaded, moved, deleted, run or exported.**
- QuantConnect was only *read*: organisation plan metadata, an Object Store listing, and project names / dates. No project file was opened or downloaded.
- No backtest, no new result, no protocol or code change.
- E032-01 remains recorded as failed at upload, with no experimental result. E032-02 remains unauthorised.
- H028 remains REJECTED. The Holdout stays sealed.

## 1. Current state (verified)

- `main` = c0b26f5: PR #118 merged, which carries D254 and SYS1-CP0. D255 was recorded in 1744298 before this assessment.
- The frozen SYS-1 protocol (SHA-256 2a16618f…), engine, host and configuration are unchanged; their pins and tests pass.
- E032-01 is recorded in `experiments/INDEX.csv` as **failed** (stage upload, 0 s, no backtest id). It is preserved as is.

## 2. What the frozen chain needs (both options)

**The two blocked items (D254):**

| item | role | why blocked |
|---|---|---|
| Data v2.1 reference table (`qr_data_v21_00..20`, loader `qr_data_v21`) | frozen inputs of the universe, Score v1 and the H024 features behind H028 | lzma-compressed + base85-encoded (1.27M characters packed) |
| `qr_p7_export` | frozen Score v1 helpers, plus `pack` / `unpack` used to emit every result block | imports `zlib` and `base64` |

**What is inside the table** (decompressed: 5.48M characters as compact JSON; all components are read by the frozen host X801 and its data layer `qr_v2`):

| component | size | content and origin |
|---|---|---|
| `f` | 2.68M | periodic-filing dates and cover-page share counts of 3,941 registrants. **Public SEC EDGAR.** |
| `sec_v1` | 1.89M | SEC correction layer for 495 securities: 12,402 filing rows, 10 fundamental fields, all of which Score v1 / H024 use, plus dated SIC / CIK rows. **Public SEC data**, keyed by QuantConnect security identifiers. |
| `guard` | 0.53M | restatement guard, 2,172 registrants. **Public SEC company facts.** |
| `idv` | 0.23M | first-filed values for periods to 2010. **Public SEC.** |
| `ext` | 0.06M | verified identity extension, 1,807 rows. **SEC submissions**, keyed by QuantConnect security identifiers. |
| `diag` | 0.09M | data-v1 membership 2011–2017, target and residual lists. **Derived from our own earlier QuantConnect universe exports** (security identifiers and eligibility flags). |

**Provenance in short:**
- The builders (`research/phase7/data_v2/build_data_v2.py`, `research/phase11/data_v21/build_data_v21.py`) state "Public SEC data and our own tables only (no QuantConnect data)".
- The exceptions: the QuantConnect security identifiers used as keys, and the small `diag` membership lists. Those are derived from earlier QuantConnect runs.

## 3. Option B — reference table in QuantConnect's Object Store (investigated first)

**Facts established read-only:**
- **Access and quota:** our organisation (type *researcher*: Researcher seat, B2-8 node) has the **S-MICRO Object Store tier active**: 50 MB, 1,000 files, $0.
  - Current use is 8 bytes (one empty folder `/qr` from 2026-09-27).
  - Larger tiers cost $12–120 a month and are not needed.
- **Size:** one plain, readable JSON object of about 5.5 MB is needed. With self-describing field names it could reach about 10 MB. That is one object of the 1,000 allowed, and it fits well inside 50 MB.
- **Published rules** ([Object Store docs](https://www.quantconnect.com/docs/v2/cloud-platform/organizations/object-store); [Terms v1.5, 2026-10-08](https://www.quantconnect.com/terms)):
  - storage is available to paid organisations;
  - "all Object Store contents are treated as Platform Data", including files we upload, so they can never be retrieved outside QuantConnect;
  - the Terms permit storing, caching and reusing data inside the Site (§2.6(b)).
- **No prohibited code is needed.** An algorithm reads an object as text and parses it with the standard `json` module. The loader and `qr_p7_export` can be readable Python without zlib / lzma / base64.

**Assessment:**
- **Provenance and migration:** the content is SEC public data and our own identifiers. It is not QuantConnect Platform Data being moved out. Uploading it is a movement *into* the Site.
  - Once stored, it becomes "Platform Data" by the Terms' definition. That is harmless for SYS-1 because we keep the SEC originals.
  - However, the keys and the `diag` lists are derived from earlier QuantConnect exports. Whether that derived material may be re-uploaded (or kept locally at all) under v1.5 is **not settled by the published text**.
- **Encoding:** the current table uses compact numeric codes (day numbers, delta-coded dates, 4-significant-digit integers). That is readable, but a compliance reviewer could read it as "encoding". A compliant migration should store a plain, self-describing JSON layout, not the current packed string.
- **Result export: a second, larger compliance question.**
  - The frozen hosts emit results through summary statistics in 9,000-character chunks of zlib-compressed text.
  - The output includes **daily equity paths, among them SPY buy-and-hold** (E030-05 exported `daily_spy`, about 35K characters).
  - Under v1.5:
    - "Platform Data" includes any derivative "from which the original values can be reconstructed or approximated";
    - compressing or encoding is listed as a prohibited extraction method (§2.6(c));
    - "any attempt to get around technical limits on logs, output…" is a breach (§2.6(c)).
  - A SPY buy-and-hold daily path reconstructs SPY's total-return series.
  - The SYS-1 evaluation as frozen emits daily paths of A0 (SPY), A3 (SPLV + SPY) and D2, and month-end marks for every arm. **That output design would need an owner-approved protocol amendment:**
    - summary statistics only;
    - rolling and yearly measures computed in-host;
    - no ETF-reconstructing paths, no compression, no chunking beyond what QuantConnect documents.
- **Runtime, memory, files:**
  - Removing the 21 data files leaves about 28 project files.
  - Parsing 5–10 MB of JSON costs about what the current decompression costs. The host peak was 7.7–7.8 GB on an 8 GB node, so memory needs re-measurement in the canary.
  - Object Store reads in backtests are fast (the docs say live access is slower).
  - No extra cost.
- **Exact H028 reproduction:**
  - The loaded objects can be made identical to today's `load_table()` output, checked in-host against the pinned component SHA-256s.
  - The frozen hosts S028–S030 / X801 stay byte-identical, because only `qr_data_v21` (loader) and `qr_p7_export` (no zlib) are replaced.
  - The existing canary checks C0 (H026 panel digests) and C1 (E030-05 to the cent, 416 / 411 trades) would prove it. Risk: **low**.
- **Versioning:** this needs a new data version ("Data v2.1-OS"), with a manifest, component hashes, new module pins and a **full canary**.
  - It also needs an amended SYS-1 output section, which is a protocol change and needs owner approval.
  - The frozen SYS-1 strategy, arms and FS screens would not change.

**Scorecard B:**

| item | assessment |
|---|---|
| Technically feasible | **YES** (quota confirmed; standard read API; reproduction checkable to the cent) |
| Terms compliance | **UNCERTAIN** (storage of our SEC-derived table looks permitted; re-upload of the QuantConnect-derived keys / `diag`, and the result-export channel and content, need explicit confirmation) |
| Fits existing plan | **YES** (S-MICRO 50 MB active, 8 bytes used) |
| Expected additional cost | **$0** a month |
| Required changes | readable Object Store loader replacing `qr_data_v21*`; `qr_p7_export` without zlib / base64; plain-JSON summary-only result emission; upload of one JSON object (owner-approved, via the QuantConnect API); runner rule; manifest "Data v2.1-OS" + pins + tests; SYS-1 output amendment |
| Risk to exact H028 reproduction | **LOW** (same in-memory table; verified by C0 / C1) |
| Engineering effort | **MODERATE**: about 1–2 working sessions plus one canary |
| Unresolved dependencies | (1) QuantConnect confirmation that the stored table and the identifier keys are acceptable; (2) a compliant result-export format and channel; (3) owner approval of the output amendment and the upload; (4) memory headroom in the canary |
| Recommendation | the only viable technical path, **but not before the compliance questions are answered** |

## 4. Option A — minimal readable plain-text data in project files

**Size:**
- **Capacity:** 50 files × 64,000 characters = 3.2M. The plain code needs about 28 files and about 0.5M characters. That leaves **at most 22 files ≈ 1.41M characters** for data.
- **Need:** 5.48M characters as compact JSON. A readable layout would be larger.
- **Pruning cannot close the gap.**
  - All 10 SEC fundamental fields are used by Score v1 / H024. All components are read by the frozen host.
  - The 2008–2021 depth is needed: 2011–2014 training plus warm-up.
  - Restricting rows to "what SYS-1 actually touches" would require usage information that only a QuantConnect run reveals. It would also change the frozen inputs.
- **Exact reproduction of E030-05** could be proven only by C0 / C1, and only if nothing used were removed. That is unattainable at a 74% cut.
- **Compliance:** splitting a data table over many source files to stay under the per-file and per-project limits is exactly what Terms §2.6(c) calls an attempt to "get around technical limits". QuantConnect's own refusal message recommends splitting *code*, not data. **BLOCKED**, independent of the size problem.

**Scorecard A:**

| item | assessment |
|---|---|
| Technically feasible | **NO** (5.48M needed vs ≤ 1.41M available) |
| Terms compliance | **BLOCKED** (data split across files to circumvent limits) |
| Fits existing plan | **NO** (would need a higher tier, i.e. a plan upgrade, which is not allowed) |
| Expected additional cost | not applicable |
| Required changes | a new reduced data version; changes to frozen inputs |
| Risk to exact H028 reproduction | **HIGH** (any reduction of used rows changes inputs) |
| Engineering effort | large, with an uncertain outcome |
| Unresolved dependencies | none that would make it viable |
| Recommendation | **do not pursue** |

## 5. Legacy QuantConnect projects (read-only inventory; nothing touched)

**Inventory:**
- **91 projects:** 32 strategy / benchmark projects (qr-B90x, qr-S0xx), 52 infrastructure projects (qr-X8xx / qr-X9xx) and 7 temporary `qr-gate-*` engine tests. Names and dates were read only.
- **Last recorded upload per strategy** (from `experiments/*/result.json`; no QuantConnect file read): 35 of 83 contain packed or encoding modules.
  - `qr_sec_data` (SEC correction table; S016–S023, X972–X997);
  - `qr_data_v2` / `qr_data_v21` / `qr_data_v3` / `qr_v3val` (S024–S031, X801–X803, X998 / X999);
  - event ledgers `qr_h017_events` / `qr_h025_events` (S017, X982, S027);
  - `qr_p3_replay` (S018, X984);
  - `qr_p7_export` (zlib, from X993 onward).
- **qr-S032 (E032-01, refused):** the upload stops at the first refused file. From the runner's upload order it should hold only plain modules (host, harness, `qr_p7`, `qr_p7_score`). This is unverified, because checking would mean reading project files.

**Classification:**

| category | where | status |
|---|---|---|
| Historical project source code | the 91 projects; identical copies in git | our own code; permitted to keep (§2.6(e)) |
| Reference data in project files | packed SEC tables / event ledgers in 35 projects | our SEC-derived content, but packed in a form QuantConnect now refuses to save; keys partly QuantConnect-derived |
| Backtest records / research evidence | inside each project on QuantConnect; extracted summaries in `experiments/` and `research/` | the QuantConnect-side records stay where they are |
| Possibly restricted under v1.5 | (i) packed project files; (ii) **locally committed exports that contain series derived from QuantConnect data**: daily SPY / benchmark equity paths (e.g. E030-05 `daily_spy`, B900 / B901 equity curves), per-stock score / eligibility tables (E993), ETF probe aggregates | previously treated as "derived results" (CLAUDE.md engineering rules); v1.5's "reconstructed or approximated" definition may now cover some of them |

**Does leaving the projects untouched raise compliance uncertainty?**
- **Yes, moderately.** The Terms do not require removal of earlier files, and nothing in them is downloaded or reused. But QuantConnect monitors project contents (§2.6(g)), and the packed files are now of a kind it refuses to save.
- A previously accepted upload is **not** assumed compliant for new use: none of these projects should be re-run as they are.

**Proposed safe procedure (only after separate owner authorisation):**
1. Ask QuantConnect support (see §6) whether existing packed reference files and our local derived exports are acceptable to keep.
2. If remediation is advised, delete **only the packed data files** inside each listed project with the API `files/delete`. That keeps the projects and their backtest records. Never read or download them first.
3. Record every deletion in `DECISIONS.md` with the project and file name.
4. Keep git as the authoritative copy of our own code and SEC tables.
5. Treat any locally committed QuantConnect-derived export the same way: a separate owner decision after clarification, not deleted unilaterally.

## 6. Conclusion

**Recommended: 3 — Request explicit platform clarification.**
- Option A is not feasible and is blocked.
- Option B is technically sound, costs nothing on the current plan and should reproduce H028 exactly. But its compliance turns on points the published Terms do not settle, and preparing it before they are settled would risk exactly the breach the owner wants to avoid.

**Questions to put to QuantConnect support** (owner-sent or owner-approved):
1. May a paid organisation store a reference table built from **public SEC EDGAR** data in the Object Store, keyed partly by QuantConnect security identifiers, and read it in backtests?
2. Is plain, self-describing JSON in the Object Store the expected form, as opposed to data embedded in project files?
3. Which result-export channel and content are acceptable? Specifically:
   - Are runtime / summary statistics in multiple plain-text entries acceptable?
   - Are yearly or monthly portfolio returns, and the equity curve of a portfolio that includes or tracks SPY, considered "summary results" (§2.6(e))?
4. Do the existing packed files in older projects, and our previously exported equity curves of benchmark portfolios, need to be removed?

**If the answers support Option B:** conclusion 1 (prepare a compliant Object Store migration), under a separately approved implementation freeze, an output amendment and an exact-reproduction canary.

**If not:** conclusion 4, close SYS-1 as **PLATFORM BLOCKED**. That is not a verdict on the architecture, because it was never tested.
