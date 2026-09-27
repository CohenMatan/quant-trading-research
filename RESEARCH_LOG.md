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
