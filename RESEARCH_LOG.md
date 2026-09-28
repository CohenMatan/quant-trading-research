# RESEARCH_LOG.md

Append-only chronological diary. The newest entry is at the bottom. Never delete entries.

Totals so far: hypotheses **0** · research strategies **0** · research experiments **0** (plus 14 registered infrastructure, benchmark and demo runs)

---

## 2026-09-27 — Session 1: Checkpoint 1 (Architecture & Data Plan)

**Done:**

- Reviewed the project brief.
- Researched data and engine options: QuantConnect Cloud/LEAN, Sharadar, Norgate, EODHD and free sources.
- Wrote the CP1 report (`docs/checkpoints/CP1_architecture_and_data_plan.md`).
- Created the project memory files: CLAUDE.md, README.md, RESEARCH_PLAN.md (draft), DECISIONS.md and this log.

**Findings:**

- QuantConnect provides survivorship-free daily prices, corporate actions and Morningstar point-in-time `MarketCap` from January 1998. That gives about 27.7 usable years.
- Morningstar replaced QC's entire fundamentals history with a new feed on 2026-09-23. Market-cap data must be audited at CP2.
- QC's licence prohibits exporting raw data, so everything runs inside QC Cloud and only derived results are stored.
- `www.quantconnect.com` and most vendor sites are **blocked by this environment's network egress policy**. The owner must allowlist the host before CP2.
- QC API access requires a paid tier. Public sources give conflicting prices ($8–$60/month), so the owner must confirm the price at signup.

**No experiments run. No money spent.**

**Next:** wait for owner approval of CP1 and the decisions in its §8.

---

## 2026-09-27 — CP1 approved; CP2 blocked on environment access

**Owner approvals:**

- CP1 approved.
- QuantConnect Cloud approved as the data source and engine.
- Split approved: IS 1999-01-04 → 2014-12-31; VAL 2015-01-01 → 2021-12-31; HOLDOUT 2022-01-01 → 2026-08-31.
- Market-cap threshold approved: $2B nominal.
- Simulated account size approved: $100,000.
- Checkpoints are approved by PR merge into `main`.

**Subscription:** QuantConnect Researcher seat ($10/month) plus B2-8 backtest node ($14/month), $24/month total.

**Owner's precondition for CP2:** verify QC API authentication and dataset access before implementing anything.

**Check result in the current session (the session that wrote CP1):**

- `QC_USER_ID` and `QC_API_TOKEN` are **not present** in this session's environment.
- `www.quantconnect.com` is **still denied** by the egress proxy (403 on CONNECT).
- Likely cause: environment settings only apply to newly started sessions.

**Consequence:** CP2 implementation has **not** started, per the owner's precondition.

**Next:** in a new session, run the session-start checklist in CLAUDE.md, then verify authentication and data access, then build CP2.

---

## 2026-09-27 — Session 2: CP2 precondition verified (QC API + dataset access)

**Session-start checklist:** `QC_USER_ID` and `QC_API_TOKEN` are present (values not displayed). `www.quantconnect.com` is reachable (HTTP 200).

**Authentication:** QuantConnect REST API v2 with hashed-timestamp auth → `authenticate` returned success. The organization reads back as tier `researcher`, billing `paid`, with a Researcher Seat ($10) and one B2-8 backtest node ($14) as the only paid subscriptions.

**Dataset access, via five tiny throwaway cloud backtests (scratch code, not part of the repo):**

| Dataset | Check | Result |
|---|---|---|
| US Equities daily, incl. delisted | Enron (ENE) daily closes 2001-11-20 → 12-10 ($6.90 → $0.26 → $0.81) | ✅ |
| Morningstar fundamentals / MarketCap | 2001-11-20: 7,017 securities, 408 with MarketCap ≥ $2B; top 3 = GE $361B, MSFT $313B, XOM $270B | ✅ (see finding 1) |
| US Equity Security Master | AAPL 2:1 split on 2005-02-28 (warning the day before, then "split occurred"); SPY dividend $0.47 on 2005-03-18 | ✅ |
| SPY | Daily bars 1999-01-04 → 2021-12-31 (5,788 trading days) | ✅ |
| Execution | Market-on-open order placed at the T close filled on T+1 at a price different from the T close; IB fees applied | ✅ (full canary to follow) |

**Findings that affect the design:**

1. **Enron's MarketCap reads $0** in Nov 2001 while the stock still traded, so MarketCap has gaps. The data audit must measure how often this happens.
2. **ObjectStore export is blocked** for non-Institutional accounts (data licensing), so it cannot carry results out of QC.
3. **Logs are capped** at 100 KB per backtest and about 3 MB/day, so they are only suitable for small summaries.
4. **The orders API** returns every order with fill events, fees and times. **Custom chart series** return full daily resolution (5,788 points, no downsampling). These become the result channels.
5. The B2-8 node reports an "assets: 500" figure, but a 900-security universe ran without error. Full-scale memory and runtime will be measured.
6. The LEAN version is available per backtest in `serverStatistics` (currently v2.5.0.0.18130).
7. The product list shows a "Tradier" module line at $1 that does not appear among the active subscriptions. Flagged for the owner to check.

**Conclusion:** the owner's precondition is **met**, and CP2 implementation starts now.

---

## 2026-09-27 — Session 2 (continued): CP2 built. STOP for owner approval.

**Built:**

- QuantConnect API client.
- Shared LEAN harness: universe, market-on-open execution, cash planning, fill self-check, holdout lock, equity export.
- Experiment runner: clean-tree check, holdout lock, LEAN build pinning, provenance, reproduce mode.
- Append-only registry.
- Metrics module; PSR/DSR/PBO statistics; split-aware trade builder; integrity checks; truncation look-ahead checker.
- Data-audit algorithm and renderer; execution-timing canary; corporate-action and delisting check.
- SPY and equal-weight ≥ $2B benchmarks; the S000 pipeline demo.
- 81 tests, all passing.

**Runs (registered):**

| Experiments | Result |
|---|---|
| E951-01/02/03 | Audit |
| E950-01 | Canary: integrity-failed, chart read race |
| E950-02 | Canary: ✅ 4,628 fills, 0 timing violations |
| E952-01 | Corporate actions: check bug |
| E952-02 | Corporate actions: ✅ |
| E900-01 | SPY: integrity-failed, chart read race |
| E900-02 | SPY: ✅ |
| E901-01 | Equal-weight benchmark, 2010–2021 |
| E000-01 | Demo, 2010–2014 |
| Reproductions | E950-02 identical; E000-01 one failed read race, then identical |

In addition, 14 unregistered infrastructure development runs: 11 API/data probes and 3 harness scratch runs. None were research.

**Key finding: universe data blocker.**

- Old Morningstar dataset: MarketCap from 1999, but never for companies that later failed or were acquired (Enron, WorldCom, Lehman, Bear, Merrill, Countrywide, Lucent, …). That is survivorship bias.
- New dataset (the only one after 2026-10-31): almost no MarketCap before 2009 (4–27 names ≥ $2B per year); good from 2010; 9 of 12 companies that disappeared later in 2013–2020 are present.
- Options and recommendation are in CP2 §7.

**Throughput:** about 20 s for small backtests; 3–7 min for full-universe backtests; one at a time. That is about 150–300 universe backtests per day.

**Cost:** $24/month, unchanged.

**Proposed for approval:** tradability filters, base slippage, portfolio constraints and gates (D023–D026); data remedy (D027).

**Status:** STOPPED at CP2. No research campaign started. Waiting for the owner.

---

## 2026-09-27 — Session 3: CP2 approved; size-proxy addendum started

**Owner decisions:**

- CP2 infrastructure is approved.
- Do not contact QuantConnect support.
- Build and evaluate a survivorship-free size proxy from price and volume only, compared against MarketCap ≥ $2B in at least 2010–2014.
- Compare several variants; do not over-optimise.
- Stop after the evaluation.

**Checklist:** credentials present (values not displayed); QuantConnect reachable.

**Done before any result:** evaluation plan, variants and decision thresholds pre-registered in `docs/data/size_proxy_plan.md`.

---

## 2026-09-28 — Size proxy: provisional report written

**Runs:**

- E953-01 (2010–14) and E953-02 (2015–21) completed, X953 v1.0.
- E953-03 (1999–2009, old dataset) **failed**: QuantConnect's daily log allowance of about 3 MB ran out.

**Findings:**

- **The reference is survivorship-biased even in 2010–14.** Later-ended companies (Alcoa, Time Warner, DuPont, SanDisk, …) have no fundamentals in either dataset.
- **Wrong primary-share flags.** The new dataset flags many US companies (GE, BAC, V, …) as non-primary. Fixed in D030; the fix requires v1.1 re-runs E953-04..07.
- **Provisional result, C20 + E5 proxy:** F1 0.75 measured; about 0.80 estimated against a complete reference; 0.85 on known-type names; 2015–21 F1 0.80. The universe return gap is −0.2%/year, not significant.
- **Provisional verdict:** APPROVE WITH LIMITATIONS.

**Operational issue:** the log allowance did not reset at 00:00 UTC (still 0 at 05:00 UTC). The v1.1 runs start automatically when it returns.

Report: `docs/data/size_proxy_evaluation.md`, marked PROVISIONAL.
