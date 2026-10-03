# P2-CP14 — H017 Implementation and Canary Readiness Checkpoint (STOP)

- **Date:** 2026-10-03.
- **Owner authorisation:** "Phase 2 — Approve H017 Specification, Authorise Implementation + Canary Only" (2026-10-03; summary `docs/owner/2026-10-03_approve_H017_spec_implementation_canary.md`).
- **Done:**
  - implemented H017 exactly as approved;
  - froze the event table;
  - wrote every config;
  - ran **only** the non-candidate infrastructure canary E982-01.
- **Not done:**
  - no candidate, control or diagnostic run;
  - no candidate performance and no post-event return;
  - no Holdout access; no data purchase.
- **Phase 2 slot 3 is unused.**

## Verdict

**READY FOR E017-01.**

- **Implemented:** H017 exactly as approved.
- **Frozen and hash-pinned:** the event table and the spec. Amendment 3 and data infrastructure v1 are unchanged.
- **Tests:** 583 pass.
- **Canary:**
  - **E982-02**, the final canary on the exact code E017-01 will run: **all 25 offline checks pass**.
  - **E982-01**, the first canary, ran the same trading code. Its trades are byte-identical to E982-02 (equity, fills and trades hashes match).
  - E982-01 surfaced two checker definitions that were too narrow, and showed that the planned weight at placement needed logging (item 18).

**Nothing beyond the canary was run.**

---

## 1. H017 frozen specification hash

- **File:** `research/phase2/H017_spec.md`.
- **SHA-256:** `975baacb935fd2f06b6dca0f4cf2e17c7a5efd2b35caa6d3783edcd6f7e7efd1`.
- **Pinned in:** `qresearch.p2h017.SPEC_SHA256`; test `tests/test_p2h017.py::test_spec_is_frozen_and_hash_pinned`.
- **Content:**
  - §1–§8 restate the approved rules: events, universe, signal, holding, portfolio, controls and runs, evaluation / PbNQ / decision tree, and the E983-01 definition;
  - §9 lists ten implementation precisions that fill gaps without changing any approved rule (item 18 below).

## 2. Event Data v1 hash

**Event table v1 (H017):**

| Item | SHA-256 |
|---|---|
| Payload loaded by QuantConnect (`qr_h017_events*.py`) | `ebb287536bca42874d36b73443dc0e0c5e02fc78245351e36d7b1c37334a5c70` |
| Detailed table `research/phase2/h017/event_table_v1.csv.gz` (uncompressed CSV) | `5c20e58c7bd4b6a6047b5006569850330d6e029a63a911c551ffd246d83fb108` |
| Event rules `src/qresearch/sec_events.py` (unchanged since P2-CP12) | `59b30885d3d75c056f5994175be6ca9c410f94bcf3d574aec4415966a8459729` |
| Time-zone conventions `tz_conventions.json` (unchanged) | `a4bce819dc92173dbb803ecc97b00792ff35b3452f939c13e9a259b3da550b22` |

- **The payload hash is checked three times:**
  - by QuantConnect on every load (a mismatch aborts the run);
  - by `qresearch.p2h017.EVENT_TABLE_SHA256`;
  - by `tests/test_p2h017.py`.
- **Inputs hashed in the manifest** (`research/phase2/h017/event_table_v1.json`):
  - E981-01 universe export;
  - E976-04 session calendar;
  - time-zone conventions;
  - XBRL filing index.

## 3. Amendment 3 hash unchanged

`research/phase2/P2_amendment3_spec.md` = `10fe4cbe69c4bd9f3e8f2576f43ad03002f9b4c2ffd46cee5c143e048c9cb2ab`, equal to `qresearch.wealth.AMENDMENT3_SHA256` (`tests/test_wealth.py`, `tests/test_p2h017.py`). Data infrastructure v1 freeze test passes (`tests/test_data_freeze.py`; the harness is unchanged).

## 4. Files implemented

| File | Purpose |
|---|---|
| `research/phase2/h017/h017_event_table.py` | Event-table builder (Event Data v1 rules; `--verify` rebuilds and compares) |
| `research/phase2/h017/event_table_v1.csv.gz`, `event_table_v1.json` | Frozen table (one row per event) and manifest |
| `src/qresearch/lean/qr_h017_events.py` + `_00` … `_06` | Packed payload for QuantConnect (7 parts, each < 64,000 characters; SHA-256 checked on load) |
| `research/phase2/h017/h017_event_table_canary.py` / `.json` | Event-integrity canary (10 checks, incl. 50 EDGAR index pages) |
| `src/qresearch/lean/qr_h017.py` | Pure logic: reaction, trailing breakpoint (linear-interpolation percentile, ≥ 400 events, strictly earlier sessions), signal, capacity, random keys, entry planning, exit schedule, EW membership, deciles |
| `strategies/S017_earnings_continuation/main.py` | All books (candidate / random / EW), one code path |
| `strategies/X982_h017_canary/main.py` | Canary: **byte copy** of S017 |
| `strategies/X983_h017_event_diagnostic/main.py` | E983-01 diagnostic, **prepared, not run** |
| `src/qresearch/p2h017.py` | Evaluation: pins, aligned returns, Amendment 3 gates, month-clustered t, PbNQ rules 1–7, conditional-run rules, decision tree |
| `research/phase2/H017_spec.md` | Frozen specification |
| `research/phase2/H017_make_configs.py` | Writes every config |
| `research/phase2/H017_eval.py` | Development evaluation (committed before any result) |
| `research/phase2/h017/E983_analyse.py` | E983-01 analysis (prepared) |
| `research/phase2/H017_canary_check.py` / `.json` | Offline canary checks (mechanics only) |
| `src/qresearch/run.py` | Uploads `qr_h017*` only for strategies that import it; **owner-approval gate** (`owner_approval_required` configs refuse to run without `--owner-approved <decision id>`) |
| `src/qresearch/config.py`, `experiment.py` | `H017_PORTFOLIO`; S017 config validation (10 slots, P5/P6 variants only, $7 / 10 bps, H017 hypothesis) |
| `experiments/E982-01`, `E017-01` … `E017-17`, `E983-01` `/config.json` | Every run config |
| `tests/test_h017.py`, `tests/test_p2h017.py` | 30 new tests |
| `docs/owner/2026-10-03_approve_H017_spec_implementation_canary.md` | Owner message record |

## 5. Full test count and result

**583 passed, 0 failed** (`python -m pytest`), including 30 new H017 tests:
- **Look-ahead / truncation:**
  - the reaction uses only E−1 and E+1 closes (and SPY's);
  - the breakpoint uses only strictly earlier sessions within 252;
  - the 400-event minimum;
  - truncating or shocking future events never changes past signals.
- **Timing:** a day-by-day order-flow simulation mirroring S017; every entry at E+2, every exit exactly 60 sessions later.
- **Capacity:**
  - ≤ 10 holdings;
  - ≤ min(free, k_t) entries;
  - held / pending stocks skipped;
  - no queue, no top-up.
- **Determinism:** AR ranking with ties by id; SHA-256 random keys.
- **Controls:** candidate and random books share events, breakpoints and k_t and differ only in selection; the canary is a byte copy.
- **Wiring:**
  - runner uploads;
  - QuantConnect 64,000-character file limit;
  - config validation;
  - the approval gate.
- **Evaluation:**
  - spec / table / Amendment 3 pins;
  - clustered t (row-level = aggregated);
  - every PbNQ rule (an unevaluated item fails);
  - conditional-run rules;
  - decision tree (W1–R4 passing with G4′ failing → Case A).

## 6. Event-table generation result

- **Built** from the cached SEC submissions (no new downloads needed), the E981-01 universe export, the measured time-zone conventions and the XBRL ticker evidence.
- **Reproducibility:** rebuilt from scratch in the canary → identical payload hash.
- **Event-integrity canary (`research/phase2/h017/h017_event_table_canary.json`): all 10 checks pass.**

| Check | Result |
|---|---|
| Hashes (CSV, payload, packed parts, pins) | Pass; largest part 60,000 characters |
| Time-zone rules re-derived for all 88,723 events | 0 acceptance-time and 0 class mismatches |
| **EDGAR index pages, stratified sample of 50** | **50 / 50 exact matches** |
| 30-day de-duplication (security level) | 0 violations |
| Amendments excluded | 0 events that are not an original 8-K with Item 2.02/12 |
| Foreign private issuers excluded | 0 events from 6-K / 20-F / 40-F (8-K itself is domestic-filer evidence) |
| Identities | 2,359 verified by dated ticker evidence + 190 identity v2; 0 weak / unverified / contradicted |
| Predecessor links | 33 securities, 787 events; 0 non-unique; 0 inside the mapped registrant's filing span |
| Window | Decisions 2009-07-01 → 2021-12-30; 0 after 2021-12-31; every event session is a LEAN session |
| Rebuild | Identical payload |

## 7. Event count

**88,723 events** of **2,549 securities** (2,573 registrants), decision sessions 2009-07-01 → 2021-12-30. The table holds every event of a verified security; QuantConnect then keeps only those whose security is eligible on the decision session.

| Decision year | Events | | Decision year | Events |
|---|---|---|---|---|
| 2009 (Jul–Dec, warm-up) | 3,144 | | 2016 | 7,267 |
| 2010 | 6,516 | | 2017 | 7,230 |
| 2011 | 6,611 | | 2018 | 7,255 |
| 2012 | 6,735 | | 2019 | 7,302 |
| 2013 | 6,919 | | 2020 | 7,441 |
| 2014 | 7,214 | | 2021 | 7,775 |
| 2015 | 7,314 | | | |

- **Timing classes:**
  - after the close 44,612;
  - before the open 35,037;
  - during the session 8,226;
  - unknown time 715 (registrants whose convention was never measured, mostly predecessors);
  - non-session day 133.
- **Conventions:** UTC 64,189; Eastern 23,819; unmeasured 715.
- **Exclusions:**
  - 118 of the 2,719 universe securities by identity status (46 weak, 47 unverified, 25 contradicted);
  - 52 verified securities have no earnings 8-K in the window (e.g. foreign private issuers);
  - 12 securities with an ambiguous predecessor link (their own events kept, no predecessor events);
  - 1,285 linked-registrant events inside the mapped registrant's filing span (co-registrants);
  - 1 cross-registrant duplicate.

## 8. Canary E982-01 / E982-02 result

| Run | Code | QuantConnect | Runtime | Result |
|---|---|---|---|---|
| **E982-01** | S017 as first committed (`3035a88`) | Backtest `12c528de…`, LEAN 18131 | 872 s | Completed; run integrity checks all pass. Offline checker v1: 23 / 25 pass; C3 and D3 failed on **checker definitions**, not on mechanics (item 18). Kept on record (`research/phase2/H017_canary_check_E982-01_v1.json`) |
| **E982-02** | S017 + one logging line per entry (planned weight at placement, `EP\|…`); X982 byte copy (`e83ac46`) | Backtest `3209d578…`, LEAN 18131 | 807 s | Completed; run integrity checks all pass; **offline checks 25 / 25 pass** (`research/phase2/H017_canary_check.json`) |

- **Equity, fills and trades SHA-256 are identical** between the two runs: the logging change did not alter a single trade, and the canary reproduces exactly.
- **Book:** random-event book, seed 0 (not a control seed); full window with the history-only warm-up.
- **Activity, 2010-03-01 → 2021-12-31:**
  - 2,983 official sessions (3,149 including the warm-up);
  - **55,797 universe events** (eligible on the decision session), 55,793 with a valid reaction (4 missing a close);
  - 5,545 candidate-qualifying signals (counted only; ≈ 470 a year, as projected);
  - **472 entries** (≈ 40 a year, as projected); 458 normal 60-session exits; 4 forced exits; 10 positions open at the end;
  - 934 orders.

## 9. Every canary assertion (E982-02)

| # | Assertion | Evidence | Result |
|---|---|---|---|
| A1 | Event-table hash inside QuantConnect = pinned = manifest; all 88,723 events loaded | `ebb28753…` in the run summary | Pass |
| A2 | Offline event-table canary: time zones, EDGAR 50/50, de-duplication, amendments, foreign filers, identities, predecessor links, window, rebuild | §6 | Pass |
| A3 | Every table event session in the run window is a LEAN session | 0 of 88,723 not a session | Pass |
| A4 | No event after 2021-12-31 | Last decision 2021-12-30 | Pass |
| B1 | The breakpoint uses only strictly earlier decision sessions | 0 violations, every session checked in-algorithm | Pass |
| B2 | Reaction prices come only from bars dated on or before the decision close | 0 bars after the decision date; history always contained E+1's close | Pass |
| B3 | Breakpoint sample ≥ 400 events on every official decision day | Minimum 1,692 (2010-03-01); 0 days without a threshold | Pass |
| B4 | Warm-up is history only | First decision 2010-03-01, first equity 2010-03-01, first fill 2010-03-02; 166 warm-up sessions with no orders | Pass |
| B5 | No Holdout data | End 2021-12-31; last fill 2021-11-26; no table event after 2021-12-31 | Pass |
| — | Future events never change past signals | Unit truncation tests (item 5); in-algorithm the history is append-only in session order | Pass |
| C1 | Every entry fills at the open of E+2 of a table event, decided at the close of E+1, never earlier | 472 / 472; 0 violations | Pass |
| C2 | Every normal exit fills exactly 60 sessions after the entry | 458 / 458; every exit order placed at sessions held = 59 | Pass |
| C3 | Every other exit is a forced integrity exit | 4: QuantConnect delisting liquidations of acquired companies (Burger King 2010, Novellus 2012, Spansion 2015, SunTrust 2019), each after 30–38 sessions, each charged the $7 commission (4 QRFORCEDFEE debits) | Pass |
| D1 | At most 10 holdings | Maximum 10 | Pass |
| D2 | No leverage, no negative cash | Maximum gross 0.970; minimum cash 2.98% of equity ($3,141); no short quantity | Pass |
| D3 | Sizing: target 0.98/10, cap 10% at placement, ≥ $4,000 | Planned weight median 0.0978, maximum 0.0980; every buy has its plan line with the same quantity; smallest planned position $7,790; 64 buys scaled down by the cash reserve, none below the minimum. Weight at the next-open fill: maximum 11.06% (overnight gap; reported) | Pass |
| D4 | $7 per order | 934 / 934 orders | Pass |
| D5 | 10 bps slippage and fill timing | Harness self-check: maximum fill deviation 3 × 10⁻¹⁶; 0 timing violations | Pass |
| D6 | No top-ups | 0 buys of a held stock | Pass |
| D7 | No queued signals | Every entry decided on its own event's E+1 | Pass |
| D8 | No early replacement | Every normal exit order at sessions held = 59 | Pass |
| D9 | Held-stock events ignored | 9 events of held stocks skipped; 0 buys while held | Pass |
| D10 | All run integrity checks (cash, commission and accounting reconciliation, warm-up untouched, …) | All pass | Pass |
| E1 | Random entries ≤ k_t and ≤ free slots on every day | 2,855 decision days; 0 over k_t; 0 over free | Pass |
| E2 | Same code path | X982 is a byte copy of S017; book random, seed 0 | Pass |
| E3 | Event processing counts consistent | 88,716 seen, 55,797 universe, 55,793 valid | Pass |

## 10. Timing verification

- **Event timing:** SEC acceptance with the measured per-registrant time zone (0 mismatches across all events; 50 / 50 EDGAR pages).
- **Event session E:** before the open or during the session → the acceptance day; after the close or a non-session day → the next session; unknown time → after the close.
- **Decision and entry:** decision at the close of E+1; every one of the 472 entries filled at the open of E+2 (session-exact against the LEAN calendar).
- **Exit:** every one of the 458 normal exits filled exactly 60 sessions after its entry open.
- **Engine guards:** no order before the official start; orders only from the close hook; the harness's fill-date self-check found 0 fills on or before their signal date.

## 11. Portfolio and cash verification

- **Holdings:** at most 10.
- **No leverage:** maximum gross exposure 0.970.
- **Cash:** never negative (minimum 2.98% of equity, i.e. the 2% buffer held).
- **Sizing:**
  - every entry planned at ≤ 9.80% of equity (target 0.98/10);
  - 64 entries scaled down by the D051 settled-cash rule with its 15% gap reserve, none below $4,000;
  - no top-ups, no queued signals, no early replacement.
- **Slots:** free slots = 10 − holdings − pending buys. A position whose exit was ordered at a close kept its slot until the exit filled, as specified (spec §9.6).
- **Accounting:** the harness's cash, commission and position checks all pass.

## 12. Commission and slippage verification

- **Commission:** every one of 934 orders was charged exactly $7, including the 4 forced delisting liquidations (charged by the harness).
- **Slippage:** every harness fill is at the next open ± 10 bps exactly (maximum deviation 3 × 10⁻¹⁶).
- **Configs:** 10 bps base slippage is enforced by validation for every H017 book; stress runs use only the declared multiplier.

## 13. Random-control equivalence

- **One shared code file:** candidate, random, EW and the canary run the same `main.py` (X982 is a byte copy; test).
- **The canary computes the candidate's signals and k_t on every day exactly as the candidate book will;** the random book then selects by its SHA-256 key among the same universe events.
- **Unit tests:** candidate and random books share events, breakpoints and k_t and differ only in the selected stocks.
- **Daily limits:** the random book never exceeded k_t or the free slots on any of 2,855 decision days.
- **Seeds:** E017-03 … 07 = seeds 1–5 (test); canary = seed 0.

## 14. Confirmation: no strategy or post-event returns inspected

- **No candidate run, no control run, no E983-01 run.**
- **The canary's equity curve was used only for mechanics:**
  - session dates;
  - number of positions;
  - cash ≥ 0;
  - equity on the decision date, to check that each entry's weight was ≤ 10%.
- **Never computed or printed** for the canary: any return, CAGR, Sharpe ratio or drawdown. The runner's metric fields were suppressed when the results were read.
- **The candidate's qualifying signals** were computed inside the canary only to set the random book's daily k_t, and are logged only as counts.
- **The reaction breakpoint** (≈ 7% SPY-adjusted two-session move at the 90th percentile) is a property of the signal distribution, not a return of any strategy.
- **The scratch development run** (item 18) was read in the same way.

## 15. Phase 2 slot 3

**Unused.** E017-01 has not run. Its config carries `owner_approval_required`, and the runner refuses it without `--owner-approved <decision id>`.

## 16. Holdout

**Locked.**
- No config ends after 2021-12-31 (test).
- The event table holds nothing after 2021-12-31.
- The harness lock is unchanged.
- `HOLDOUT_UNLOCK.md` does not exist.

## 17. Runs waiting for approval (exact list)

| Run | Purpose | Condition |
|---|---|---|
| **E017-01** | Candidate, $100K | **Consumes Phase 2 slot 3**; separate approval |
| E017-02 | EW-H017, $10M paper | With E017-01 |
| E017-03 … E017-07 | Random-event books, seeds 1–5 | With E017-01 |
| E017-08 | Candidate, $200K (sensitivity only) | With E017-01 |
| E983-01 | Event-level diagnostic (post-event returns; aggregated) | Separate approval; used only within PbNQ rule 7 |
| E017-09 | 2× slippage | Only if PbNQ rules 1–5 or the Case C prerequisites hold |
| E017-10, E017-11 | 4×, 6× slippage | Only if W1–W3 and R1–R4 pass |
| E017-12 … E017-17 | P1 hold 40; P2 hold 80; P3 top quintile; P4 one-session reaction; P5 8 slots; P6 12 slots | Only if W1–W3 and R1–R4 pass |

All 18 configs exist, validate, and are gated by the runner.

## 18. Technical issues and deviations

None blocks E017-01. All are disclosed; none changes an approved rule.

1. **E982-01 offline checker, two definitions too narrow (fixed; canary re-run as E982-02):**
   - **C3 (forced exits):** the checker expected the harness's held-delisting counter or its QRDELIST log lines. QuantConnect liquidated the 4 acquired companies before the delisting event reached the harness. The liquidations are LEAN's standard delisting exit, debited $7 each by the harness. The check now accepts LEAN liquidations / harness stale exits, matched to the harness's forced-fill and forced-fee counts and occurring before the 60-session exit.
   - **D3 (10% cap):** the cap applies when an order is placed (decision-close price). The checker measured the weight at the next-open fill, where 6 of 472 entries exceeded 10% after an overnight gap (maximum 11.06%). Because placement prices are not exported, S017 now logs each entry's planned weight (`EP` lines). This is one logging line, no trading change: E982-02 is trade-for-trade identical.
   - **The same flaw existed in the evaluation's R4 limit check** (`H017_eval.py`), and could have failed the candidate's R4 spuriously. It now uses the planned weights. Fixed before any candidate run.
2. **Scratch development run (not registered):**
   - one uncommitted run of the canary book on 2009-07 → 2010-05 (seed 0, non-candidate), to catch QuantConnect API errors before the official canary;
   - no error; its output was read only for counters, never returns.
3. **Event-table implementation precisions (spec §9.1):**
   - Event-level time-disjointness for predecessor links: the frozen dated-ticker rule also links co-registrants (e.g. a utility holding company and its operating subsidiary filing combined 8-Ks). Such events (1,285 across all years) are used only outside the mapped registrant's filing span. 33 securities keep 787 genuine predecessor events.
   - Predecessor registrants whose time-zone convention was never measured get unknown time, as the frozen rule says for unresolved conventions (715 events). This is conservative: later, never earlier. No convention was re-measured: Event Data v1 is frozen.
   - The 2008–2009 NYSE early closes were added for warm-up events only.
4. **Foreign-issuer check definition:**
   - Form 8-K is not available to foreign private issuers, so an 8-K Item 2.02 is itself evidence of domestic filing.
   - 18 registrants changed filer status around their events (e.g. NXP and Signet moved to domestic filing; Venator and PartnerRe later became foreign filers). Their 32 events fall in domestic-filing periods and are listed in the canary file.
5. **Universe coverage of the table:** the E981-01 export lists securities eligible on at least one month start in 2010–2021. A security eligible only within a single month, or only in late 2009, is absent. The effect is negligible and identical for every book.
6. **EW-H017 membership (spec §9.7):** "verified domestic event filer" is defined point-in-time as an event decided in the trailing 252 sessions.
7. **k_t (spec §9.5):** k_t is counted before held stocks are skipped. The candidate and random books then both skip held or pending stocks.
8. **Runner approval gate (new):**
   - configs carrying `owner_approval_required` refuse to run without `--owner-approved <decision id>`, which is recorded in the run provenance;
   - this protects slot 3 and E983-01 from an accidental start.
9. **E983-01 is prepared, not executed:** it computes post-event returns. Its code mirrors S017's event selection and breakpoints but has not been exercised on QuantConnect, so a technical failure is possible at its first authorised run.
10. **SEC access:** the 50-page EDGAR check used `www.sec.gov` with the contact e-mail read at run time (never written to the repository).

## 19. Estimated runtime

Measured on the canary (same code, same universe, full window):
- ≈ 14 minutes of QuantConnect compute;
- ≈ 18 minutes wall time per run, including the download.

| Runs | Estimate |
|---|---|
| E017-01 (candidate) | ≈ 15–20 min |
| E017-01 … 08 (committed set) | ≈ 2.5 h sequential (E017-02 EW: ≈ 20–30 min, more orders to download) |
| E983-01 (diagnostic) | ≈ 20–30 min (extra history requests) |
| E017-09 … 17 (only if their conditions hold) | ≈ 2.5–3 h |

- One backtest at a time on the B2-8 node (QuantConnect $24/month, unchanged).
- No additional cost.

## 20. Final statement

**READY FOR E017-01.**

E017-01 consumes Phase 2 slot 3 and needs your explicit approval. The runner will refuse it without `--owner-approved <decision id>`.

The decisions you could take:
1. Approve **E017-01 … 08** (candidate, EW-H017, random seeds 1–5, $200K sensitivity) to run as one committed set.
2. Approve **E983-01** with them, or separately. It is needed only if PbNQ rule 7 is ever reached. Running it together avoids a later stop, but it shows event-level post-event returns.
3. Confirm that the conditional runs E017-09 … 17 may run automatically when their pre-registered conditions hold, or ask for a stop before them.

**STOP.** No E017 run; slot 3 unused; no candidate performance; Holdout locked; no data purchase.
