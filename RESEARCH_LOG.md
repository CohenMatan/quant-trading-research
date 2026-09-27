# RESEARCH_LOG.md

Append-only chronological diary. The newest entry is at the bottom. Never delete entries.

Totals so far: hypotheses **0** · strategies **0** · experiments **0**

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
