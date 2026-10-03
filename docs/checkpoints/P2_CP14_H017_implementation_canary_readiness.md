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

__VERDICT__

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

__CANARY_SECTIONS__

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

__ISSUES__

## 19. Estimated runtime

__RUNTIME__

## 20. Final statement

__FINAL__
