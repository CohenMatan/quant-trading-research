# DECISIONS.md

Numbered decision records. Status values are **Proposed**, **Accepted** (owner-approved or minor/autonomous), **Superseded** and **Rejected**. Never delete a record; supersede it.

| ID | Date | Decision | Status | Rationale / Notes |
|---|---|---|---|---|
| D001 | 2026-09-27 | Use QuantConnect Cloud (LEAN + AlgoSeek prices + Security Master + Morningstar fundamentals) as the single data source and engine for Phase 1, driven via the REST API | Accepted (owner, CP1) | Survivorship-free, point-in-time market cap from 1998; realistic execution; about $10–$100/month; no local data to manage. See CP1 §1 and §2.7. |
| D002 | 2026-09-27 | No second, fast research engine initially; measure throughput at CP2 and propose one only if it is a bottleneck | Accepted | Owner instruction: build only what is demonstrably needed. |
| D003 | 2026-09-27 | Universe is defined by point-in-time MarketCap ≥ $2B nominal, not by index membership | Accepted (owner, CP1) | Avoids needing a paid historical-constituents dataset and index-committee effects; matches the owner's spec. |
| D004 | 2026-09-27 | Data split: IS 1999-01-04 → 2014-12-31; VAL 2015-01-01 → 2021-12-31; HOLDOUT 2022-01-01 → 2026-08-31 (locked in code) | Accepted (owner, CP1) | See CP1 §6. The alternative (2022 moved into VAL) was considered. |
| D005 | 2026-09-27 | Execution: signal on the T close, market-on-open fill on T+1; raw prices for fills, adjusted prices for signals | Accepted | Required for realism; no fills at the signal bar's close. |
| D006 | 2026-09-27 | Metrics computed locally with one shared module from the QC equity curve and trade list | Accepted | Consistency across strategies; independent of QC summary statistics. |
| D007 | 2026-09-27 | Storage is plain files in Git (Markdown, CSV, JSON, gzip); no database; no raw data in Git | Accepted | Simplicity; QC's licence forbids raw-data export. |
| D008 | 2026-09-27 | Official experiments run only from a clean git tree and record commit, params, dates, QC backtest ID, LEAN version and result hashes | Accepted | Reproducibility requirement. |
| D009 | 2026-09-27 | Checkpoints are approved by merging the checkpoint branch into `main` through a PR | Accepted (owner, CP1) | Gives a durable, auditable approval record. |
| D010 | 2026-09-27 | Assumed account size for cost modelling: $100,000 | Accepted (owner, CP1) | Affects only minimum-commission effects. |
| D011 | 2026-09-27 | QuantConnect subscription: Researcher seat ($10/month) plus B2-8 backtest node ($14/month), $24/month total | Accepted (owner) | Owner purchased. Within the budget target. |
| D012 | 2026-09-27 | Git: all checkpoint work is pushed; the owner approves checkpoints by merging into `main` through a PR | Accepted (owner, CP1) | Confirms D009. GitHub remains the permanent source of truth. |
