# CLAUDE.md — Operating instructions for this repository

This repo is a **private quantitative research workspace**. Claude Code works in it as an autonomous quant research engineer. The owner makes product decisions, approves stage transitions and reads reports. The owner does not review code.

Read this file first in every session, then read `RESEARCH_PLAN.md`, the latest entries of `RESEARCH_LOG.md`, and `DECISIONS.md`.

## Mission (Phase 1 — Research only)

Try to find **one** simple, explainable, robust **long-only swing-trading strategy for US equities** that survives rigorous validation. **"No Production Candidate Found" is an acceptable, honest outcome. Never force a positive result.**

## Hard scope limits

- Research only.
- **Do not build any of the following:**
  - Real-money trading or a broker integration.
  - A server, backend, REST API, web UI or dashboard.
  - A daemon or scheduler, a message queue, or authentication.
  - A database server, Kubernetes, microservices or any multi-user feature.
- Only write code that is needed for deterministic calculations, data processing, backtesting, validation, testing, experiment tracking, reproducibility or reporting.
- Universe rules:
  - US common stocks, long-only, no options, no leverage, no intraday trading.
  - One decision per trading day. Holding period of several days to several weeks; **Phase 2 (owner scope change 2026-09-30, D094): weeks to months** (H014 holds up to 63 sessions with horizon roll, or up to 126 sessions).
  - **Point-in-time market cap ≥ $2B.**
  - Price, volume and market-behaviour information, **and (owner scope expansion 2026-10-01, D106) point-in-time fundamental company data** (e.g. profitability, quality, balance-sheet strength, cash generation, capital efficiency, share issuance, valuation) — only fields the fundamental-data audit classifies as safe, used as known on the decision date. No news for selection.
- Budget: about $100/month target, $200/month hard ceiling. **Never purchase or commit to paid services without owner approval.**

## Current state

See `RESEARCH_LOG.md` (latest entry) and `docs/checkpoints/`.

- **CP1 was APPROVED by the owner on 2026-09-27.**
- **CP2 was APPROVED by the owner on 2026-09-27.**
- **Owner decision 2026-09-28 (D033):**
  - Official research uses the new Morningstar dataset **from 2010 only**, with MarketCap ≥ $2B.
  - The size proxy is rejected.
  - 1999–2009 is an optional finalist stress test only (D035).
- **CP2 amendment** (2010 split, adjusted gates, $7/order): APPROVED by the owner on 2026-09-28. Research Cycle 1 was authorised.
- **CP3** (C01 in-sample): owner approved S005 v1.2 (H005) **for Validation only** on 2026-09-29 (D056). It is frozen exactly as tested. PBO 0.71 stays a visible, unchanged failing item.
- **C01 is CLOSED: No Production Candidate Found** (owner, D060). S005 v1.2 failed Validation (E005-28). H005 may never be re-validated on 2018–2021.
- **Infrastructure fixes after C01:** D057 universe (D061, dated overrides D065), D059 dead positions (D062), D063 price windows (verified end to end, E958-01). Approved in principle by the owner.
- **H001 remedial re-test:** all five variations fail the C01 screen (D067). H001 is rejected. CP4c was approved by the owner on 2026-09-29.
- **C02 COMPLETE: No Production Candidate Found** (D076/D078). Final report: `docs/checkpoints/CP3c_C02_final_report.md`. 17/18 fail the IS screen; E007-02 (H007 v1.1) fails robustness (5/8 plateau). Frozen rules: DSR N = cumulative selection candidates (D069, now 37); hard PBO gate = cycle-level PBO ≤ 0.30 (D073). Recovery of lost-runner backtests: `run.py --recover` (D077).
- **C03: plan APPROVED** (owner 2026-09-30: H012, H013, $100K primary / $200K S1+S2 sensitivity, budget cap 82; `docs/checkpoints/CP3e_C03_final_plan.md`). **Statistical methodology APPROVED and FROZEN (D082 final):** `research/cycles/C03_statistical_spec.md` (hash pinned by a test). PBO diagnostic only; DSR ≥ 0.90 at official N (43) AND conservative N (selection + H013 replicate seeds + robustness + Validation, from the registry) per deployable book; H013 every seed at every stage. Implemented in `registry.trial_accounting` and `qresearch.c03stats`. **Infrastructure built and verified** (S012, S013, canaries E963-03 and E964-01 pass; D083/D083a), committed-run configs and `research/cycles/C03_eval.py` written. CP3g approved in principle by the owner (2026-09-30); H012 Option 2 chosen. **Owner decisions after CP3h (D087):** H012 REMOVED from C03 (not evaluable with sufficient statistical power; not a failed hypothesis; configs withdrawn in `experiments/WITHDRAWN.json`). Statistical spec Amendment 1: official N = 40, N = 43 sensitivity only, conservative formula unchanged. H013 only; committed research runs 21 (`research/cycles/C03_plan_amendment_1.md`). **C03 CLOSED by the owner: No Production Candidate Found (2026-09-30).** H013 rejected (CP3i). Research-programme review C01–C03 written (`docs/checkpoints/CP3j_programme_review_C01_C03.md`, D090). **Phase 2 (new programme P2, not C04): research proposal written (`docs/checkpoints/P2_CP0_research_proposal.md`, H014 PROPOSED, D091); Revised evaluation methodology approved in principle (`docs/checkpoints/P2_CP0b_revised_evaluation_methodology.md`, D092/D092a: 2010–2021 development, DSR diagnostic, one-time 2022–2026 Holdout); amendment proposed (`docs/checkpoints/P2_CP0c_methodology_amendment.md`, D093: data from 2026-09-01 to the freeze is locked historical unseen data, and the forward clock starts at the freeze timestamp; hypothesis budget of 3 with a fixed +0.25 margin; combined return-risk G1). **Owner FINAL approval 2026-09-30 (D094):** methodology approved (data categories D 2010–2021 / H 2022-01-01 → 2026-08-31 locked / U after 2026-08-31 before the freeze timestamp, locked / F true forward only after full freeze + owner approval — pre-freeze data is never 'forward testing'); budget 3 hypotheses, fixed margin +0.25; gates G1–G4 (DSR and PBO diagnostic only). **H014 development authorised: frozen spec `research/phase2/P2_spec.md` (hash pinned in `qresearch.p2spec`), S014 + controls, committed DEV runs E014-01..14, conditional robustness E014-15..23 only per spec §9, canaries X965.** STOP after the development checkpoint: no Holdout, no post-2026-08-31 data, no forward test, no change to H014 after results.** **P2-CP1 written 2026-10-01 (D100): H014 NOT development-qualified (Candidate A chosen; fails G1, G2, G3; G4 not triggered). No Holdout request. Budget 1/3 used; Holdout unopened. STOPPED awaiting owner.** **2026-10-01: H014 CLOSED as Rejected by the owner (D101; preserved exactly as tested, never re-run with changes). Phase 2 budget 1/3 used. H015 (diversified low-turnover trend portfolio, hypothesis 2/3) pre-registration PROPOSED (`docs/checkpoints/P2_CP2_H015_preregistration_proposal.md`, D102) — not implemented, no H015 or control backtest; STOPPED awaiting owner approval.** **H015 implementation NOT approved by the owner; viability review written (`docs/checkpoints/P2_CP2b_H015_viability_review.md`, D103): recommends not adopting H015 and preserving slot 2. STOPPED awaiting the owner's decision; no H015/H016 implementation, no backtests, Holdout locked.** **2026-10-01 (D104): H015 NOT ADOPTED before implementation (no slot used; averaged-seed construction withdrawn; K2 not run). Phase 2: 1 of 3 slots consumed, 2 remain. Opportunity review written (`docs/checkpoints/P2_CP3_opportunity_review.md`, D105): shortlist = profitability/quality, net issuance, quality+value (all need a fundamentals scope change + PIT audit); stopping is a defensible outcome. STOPPED awaiting owner; no H016, no implementation, no backtests or diagnostics, Holdout locked.** **2026-10-01 (D106): owner approved the fundamental-data scope expansion (profitability/quality first) and a fundamental-data integrity AUDIT ONLY (X967, infrastructure, no slot). No H016, no strategy definition, no factor returns, no Holdout.** **Audit COMPLETE (D107, `docs/checkpoints/P2_CP4_fundamental_data_audit.md`): safe = statement totals + point-in-time market cap with file-date availability; UNSAFE = share counts and per-share values as levels (split-adjusted to today incl. Holdout-era splits), accession numbers, current-status metadata (fiscal-year end; probably sector); Visa wrongly excluded (OTCM). STOPPED awaiting owner; no H016.** **2026-10-01 (D108/D109): PIT fundamentals layer `src/qresearch/lean/qr_fundamentals.py` built (whitelist + hard failure, +90 for estimated dates, quarantine, freshness 200 d), Visa dated exchange correction (future runs only), filing-based financial-format rule; canary E969-01 clean. Readiness checkpoint `docs/checkpoints/P2_CP5_fundamental_infrastructure_readiness.md`: NOT yet safe for H016 — SEC verification blocked (network policy) and D043 survivorship gap unrepaired (needs EDGAR). STOPPED awaiting owner.** **2026-10-01 (D110): owner approved SEC verification + D043 remediation (still no H016), but SEC hosts remain blocked by the network policy in this session; nothing built or run (`docs/checkpoints/P2_CP6a_sec_access_blocked.md`). STOPPED awaiting owner: allow data.sec.gov + www.sec.gov, then new session.** **2026-10-01 (D111): SEC verification + D043 remediation done (P2-CP6, `docs/checkpoints/P2_CP6_sec_verification_survivorship_remediation.md`): timing verified (55 early reports held), values verified, restatement guard (479 reports blocked), 20 quarantined reports released by SEC-verified list, 163 securities repaired by an OPT-IN dated SEC correction layer (`universe.sec_corrections`); residual survivorship gap up to 11% (2010); vendor interim '*_ttm' = latest fiscal year. Verdict NOT yet safe to design H016. STOPPED awaiting owner (SEC contact email, twelve-month definition, residual-gap policy).** **2026-10-02 (D112): owner approved continuing SEC repair + True TTM + re-audit (still no H016), conditional on a project-specific SEC contact email; none exists (personal email excluded; not invented), `www.sec.gov` still 403 → nothing built or run (`docs/checkpoints/P2_CP7a_sec_contact_blocked.md`). STOPPED awaiting owner.** **2026-10-02 (D113/D113a): owner authorised their email as the SEC contact (run time only, never committed). P2-CP7 written (`docs/checkpoints/P2_CP7_fundamental_data_final_readiness.md`): identity v2 from SEC-dated ticker evidence → correction table v3.2 with 495 repaired securities; survivorship gap measured SEC-side at about 0.5–1.2% a year (plus about six pre-XBRL acquisitions in 2010); True TTM (`<base>_ttm4q`) built and validated — APPROVED H016 field set: revenue, gross profit, net income, operating cash flow (True TTM), total assets, stockholders' equity (snapshots), market cap; operating income, free cash flow, total debt and vendor '*_ttm' as twelve-month values NOT approved; financial/REIT exclusion by SEC SIC at filing (`qr_industry.py`); final canary E976-04 all checks 0. Verdict: SAFE ENOUGH TO BEGIN H016 DESIGN (pre-registration only) subject to owner decisions (same-universe rule, 2008-07 warm-up, health insurers, 2011 quarantine release, residual policy, freeze table v3.2). STOPPED awaiting owner; no H016, no backtests, slot 1/3, Holdout locked.** **2026-10-02 (D114/D114a): owner approved P2-CP7 + final data policies. 2011 cleanup done (E979-01; field-level releases of SEC-verified flows only); final canary E976-06 all checks 0; harness history-only warm-up (`warmup_start` ≥ 2008-07-01) with tests. **DATA INFRASTRUCTURE FROZEN v1** (`research/phase2/data_freeze_v1.json`, pinned in `qresearch.datafreeze`, `tests/test_data_freeze.py`): never change it because of H016 results; a genuine bug → stop, document, ask the owner, issue v2. H016 pre-registration PROPOSED (P2-CP8, `docs/checkpoints/P2_CP8_2011_cleanup_and_H016_preregistration_proposal.md`; `research/hypotheses/H016.md`): GP/A top-20 quarterly — NOT approved, NOT implemented, NOT run; slot 2 not consumed. STOPPED awaiting owner.** **2026-10-02 (D115): owner APPROVED the H016 pre-registration and authorised development execution conditional on prerequisites (scope updated: H016 holdings may last months to over a year). Prerequisite 7 FAILED (with D051's 15% gap reserve the $4,500 minimum blocks every first entry at $100K) → STOPPED before any run (`docs/checkpoints/P2_CP9a_H016_prerequisite_position_rule.md`; options A/B/C). Built: `qr_h016.py`, S016, `p2h016.py`, spec draft `research/phase2/H016_spec.md` (freeze after the decision). Slot 2 not consumed; Holdout locked.** **2026-10-02 (D116): owner approved option A with a one-time top-up ($4,000 minimum, 15% reserve kept, at most one top-up per new position, minimum $250, no other resizing); H016 spec FROZEN (hash-pinned in `qresearch.p2h016`); configs E980-01 (canary X980 = byte copy of S016) and E016-01..08 written; E016-09..17 only if G1–G3 pass. Execution authorised once the canary passes; STOP after the H016 development checkpoint; no Holdout.** **2026-10-02 (D117): canary E980-01 passed; E016-01..08 run. H016 NOT development-qualified (Sharpe 0.69 vs EW-H016 0.85, SPY 0.92, random median 0.75; G1, G2, G3 fail; G4 not triggered). P2-CP9 written (`docs/checkpoints/P2_CP9_H016_development_checkpoint.md`). Phase 2 slots: 2 of 3 used. No Holdout request. STOPPED awaiting owner; H016 preserved exactly as tested.** **2026-10-02 (D118/D119): H016 CLOSED as Rejected by the owner (preserved as tested). Objective made explicit: beat S&P 500 buy-and-hold after realistic costs (risk metrics are safeguards). P2-CP10 written (`docs/checkpoints/P2_CP10_final_hypothesis_opportunity_H017_proposal.md`): proposed Methodology Amendment 2 (hard gates G1.5 CAGR(H) > CAGR(SPY) in development and HO4 in the Holdout/forward test; nothing loosened); power analysis (≈ 7%/yr true edge over the universe needed for a 50% pass chance); H017 = Value (B/M) PROPOSED (`research/hypotheses/H017.md`) but the recommendation is to PRESERVE slot 3. Not implemented, not run; slot 3 unused; Holdout locked. STOPPED awaiting owner.** **2026-10-02 (D120): owner did NOT approve H017 = Value; slot 3 preserved; objective = terminal wealth above S&P 500 total-return buy-and-hold after costs (same capital and dates, no leverage). P2-CP11 written (`docs/checkpoints/P2_CP11_research_architecture_final_slot_review.md`): proposed Amendment 3 (W1 wealth > SPY, W2 evidence 1.645·TE/√years, W3 attribution, R1–R4 safeguards, rolling 1/3/5/10-year reports; +0.25 Sharpe gate to diagnostic); history extension to 2000 NOT feasible with current data (no market cap before Oct 2009; dead pre-2009 firms lack fundamentals); earnings-event continuation (SEC 8-K timestamps, free, from 2003–04) ranked first; recommendation: preserve slot 3, priced data study + non-return earnings-event audit first. Nothing run; Holdout locked. STOPPED awaiting owner.** Do not start any research cycle or strategy backtest. No Validation, Walk-Forward or Holdout without explicit approval. Budget accounting D085 (`research/cycles/C03_budget.py`): research budget ≤ 82, operational usage counted separately. No C03 strategy backtest, Validation, Walk-Forward or Holdout without explicit approval.
- QuantConnect subscription: Researcher seat ($10/month) plus one B2-8 backtest node ($14/month), **$24/month total**.
- Engine: every experiment pins `lean_version_id`. CP2 used build 18131, the branch that carries the new Morningstar dataset. QuantConnect switches master to the new dataset on 2026-10-10 and retires the old one on 2026-10-31.
- Known QuantConnect quirks, all handled in code:
  - Results (charts, order events) arrive asynchronously; the runner waits for them.
  - At most 10 custom chart series per algorithm.
  - Only one backtest at a time on our node. The runner refuses to start while any backtest runs, and detects stalls (D053). Never delete a stalled backtest without owner approval.
  - The orders endpoint first answers `loading`, and has transient outages; the runner retries within its window (D053).
  - LEAN cancels open orders on ticker changes and delistings, rewriting the order tag; the harness re-issues cancelled sells (D054).
  - Some acquisitions arrive with no delisting event; the harness closes a holding at its last real close after 10 sessions without data, and the run is marked with a warning (D062).
  - Morningstar company flags describe CURRENT status, not point-in-time status; see D061 before using them.
  - Never run a queue while editing code: its auto-commit sweeps the tree (D064).
  - QuantConnect may revise dividend data between days; exact reproduction holds within one data snapshot.
  - ObjectStore export is blocked.
  - **Do not use QuantConnect logs (daily quota).** Results travel as summary statistics, plus the Orders API and charts (D046).
  - Fundamentals' share-count fields (all of them) and per-share values are split-adjusted to today, including later splits (D107); never use them as levels or with raw prices. `market_cap` is point-in-time.
  - Reading an unpopulated fundamental property is fatal to a backtest (missing parquet file): use only an approved field list (D107).
  - Vendor '*_ttm' fields on interim reports are the latest completed fiscal year's totals, not rolling twelve months (D111).
  - Morningstar's CIK is current-status (successor registrants); never use it alone to date-match SEC filings (D111).
  - QuantConnect project files are limited to 64,000 characters each (D111a).
  - `www.sec.gov` needs a contact email in the User-Agent; `data.sec.gov` works with the project identifier (D111).
  - The SEC contact email is read at run time from `~/.config/qresearch/sec_contact` or `SEC_CONTACT_EMAIL`; never write it into the repository (D113).
  - SEC monthly XBRL RSS archives switched namespace (http → https) and to inline XBRL in late 2019; the parser handles both and fails on an empty month (D113a).
  - True TTM needs up to seven quarters of history: observe every company with fundamentals daily from an observation-only warm-up start, not only eligible names (D113).
  - Use `qr_fundamentals.observe_vendor` for that observation step, and the harness `warmup_start` (≥ 2008-07-01) for the history-only warm-up; no decisions, orders or equity exist before the official start (D114).
  - Quarantined reports may contribute SEC-verified flow fields only through `field_releases` (partial records feed True TTM only; never the current report) (D114).

## Session-start checklist

1. Check that `QC_USER_ID` and `QC_API_TOKEN` exist, e.g. `[ -n "$QC_USER_ID" ]`. **Never print, log, echo or commit their values**, and never include them in URLs, error messages or experiment records.
2. Check that `www.quantconnect.com` is reachable through the proxy.
3. If either check fails, stop and tell the owner. Environment settings (variables and the network allowlist) only take effect in a **new** session.

## Checkpoint discipline

The checkpoints are CP1 Architecture → CP2 Infrastructure → CP3 First research cycle → CP4 Advanced validation → CP5 Final holdout → Final report.

At each checkpoint:

1. **STOP.**
2. Write the report to `docs/checkpoints/CP#_*.md`.
3. Update the log and decisions.
4. Run the tests.
5. Commit and push.
6. **Wait for owner approval.**

Never roll on to the next stage automatically. Minor implementation decisions need no approval: decide, record the decision in `DECISIONS.md`, and continue.

## Research protocol (non-negotiable)

- IDs:
  - Hypotheses are `H###`.
  - Strategies are `S###`, with versions `vMAJOR.MINOR`.
  - Experiments are `E###-##`, where the first number is the strategy and the second is the run number.
  - Research cycles are `C##`.
- Every strategy starts from a written, explainable hypothesis in `research/hypotheses/H###.md`. **No blind parameter searches.** Use about 3–10 meaningful variations per hypothesis.
- **Log every experiment**, including failed, rejected and bugged runs, in `experiments/INDEX.csv`. Never delete one. Reports must state the total number of hypotheses, strategies and experiments tested.
- Signals must be **deterministic code**. LLM judgment may propose and analyse hypotheses but is never part of a signal.
- Data split (**2010 scheme, D034: proposed at the CP2 amendment, pending owner approval**; see `RESEARCH_PLAN.md`):
  - IS: 2010-01-04 → 2017-12-31.
  - VAL: 2018-01-01 → 2021-12-31.
  - Walk-forward: expanding window from 2010, annual test folds 2014–2021.
  - **HOLDOUT: 2022-01-01 → 2026-08-31, which is locked.**
  - Phase 2 (D094): development = `DEV` 2010-01-04 → 2021-12-31 (programme P2 configs only); no IS/VAL split inside it.
  - 1999–2009: optional STRESS test of finalists only. **Never** used for optimisation, selection or promotion.
- **Never touch the holdout** before written owner approval at CP5, recorded in `HOLDOUT_UNLOCK.md`. Never tune anything on validation or holdout results. After seeing holdout results, never modify the strategy.
- Hypotheses must not be motivated by knowledge of market events after 2017 (the end of IS), such as the 2018 Q4 sell-off, the 2020 crash, 2022 or the 2023–24 AI rally. Hindsight counts as data snooping.

## Engineering rules

- Engine and data: QuantConnect Cloud (LEAN), driven through the REST API. Credentials come only from the env vars `QC_USER_ID` and `QC_API_TOKEN`. **Never print, log, commit or otherwise expose them**, and never ask the owner to paste them into chat.
- **Never export raw QuantConnect data** (licence). Store only derived results: metrics, equity curves and trade lists.
- **Execution realism:**
  - A signal on bar T executes at the T+1 open or later, **never at T's close**.
  - Model commissions and slippage.
  - Use raw prices for fills and adjusted prices for signals.
  - Model delistings.
- Official experiments run only from a **clean, committed git tree**. Record for each:
  - commit hash, parameters, dates and split label;
  - QC backtest ID and LEAN version;
  - run date;
  - hashes of the trade list and equity curve.
- Compute metrics locally, with one shared module, from the equity curve and trades.
- **A task is not done until its tests pass.** Tests must cover:
  - look-ahead (the truncation test);
  - execution timing;
  - metrics;
  - portfolio accounting;
  - data integrity;
  - reproducibility;
  - the holdout lock.
- Keep things simple. Files (CSV, JSON, Markdown) are enough, with no database. Add a dependency or a tool only with a real, documented justification.
- Large data never goes in Git. Document how to re-acquire it.

## Persistence rule

Important information must never live only in chat, temp files or an uncommitted tree. Commit at milestones and push at checkpoints. Before claiming a stage is complete, verify with `git status` and confirm the push.

## Git

- Develop on the session's designated branch.
- **Claude merges its own pushed work into `main` through a PR (D048).** Checkpoint STOPs and owner approvals still apply.
- Use clear commit messages, e.g. `E003-02: …` for experiment runs.

## Communication

- Reports for the owner must be understandable without reading code.
- For technical issues, give: what the issue is → why it matters → the options → a recommendation.
- Ask the owner only about spending, scope changes, significant trade-offs, missing essential information, or checkpoints.
