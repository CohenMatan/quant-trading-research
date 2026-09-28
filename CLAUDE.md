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
  - One decision per trading day. Holding period of several days to several weeks.
  - **Point-in-time market cap ≥ $2B.**
  - Technical price, volume and market-behaviour information only. No news for selection.
- Budget: about $100/month target, $200/month hard ceiling. **Never purchase or commit to paid services without owner approval.**

## Current state

See `RESEARCH_LOG.md` (latest entry) and `docs/checkpoints/`.

- **CP1 was APPROVED by the owner on 2026-09-27.**
- **CP2 was APPROVED by the owner on 2026-09-27.**
- **Owner decision 2026-09-28 (D033):**
  - Official research uses the new Morningstar dataset **from 2010 only**, with MarketCap ≥ $2B.
  - The size proxy is rejected.
  - 1999–2009 is an optional finalist stress test only (D035).
- **CP2 amendment** (`docs/checkpoints/CP2_amendment_2010_split.md`, which covers the 2010 split, adjusted gates and the fixed $7/order commission): **STOPPED, awaiting owner approval.** No research campaign until approved.
- QuantConnect subscription: Researcher seat ($10/month) plus one B2-8 backtest node ($14/month), **$24/month total**.
- Engine: every experiment pins `lean_version_id`. CP2 used build 18131, the branch that carries the new Morningstar dataset. QuantConnect switches master to the new dataset on 2026-10-10 and retires the old one on 2026-10-31.
- Known QuantConnect quirks, all handled in code:
  - Results (charts, order events) arrive asynchronously; the runner waits for them.
  - At most 10 custom chart series per algorithm.
  - Only one backtest at a time on our node.
  - ObjectStore export is blocked.
  - **Do not use QuantConnect logs (daily quota).** Results travel as summary statistics, plus the Orders API and charts (D046).
  - Fundamentals' shares-outstanding fields are split-adjusted to today; never use price × shares naively.

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
