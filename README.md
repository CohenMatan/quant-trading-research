# quant-trading-research

This is a private research workspace for **Phase 1** of a US-equity swing-trading research project. It is **not** a software product: there is no server, service, UI or trading connection.

Claude Code operates the research, using QuantConnect Cloud (LEAN) as its backtesting engine and data source. This repo is the permanent record of the code, experiments, results and decisions.

## Where to look

| File | Purpose |
|---|---|
| `CLAUDE.md` | Stable operating rules for the research agent |
| `RESEARCH_PLAN.md` | Methodology, data split, validation protocol |
| `RESEARCH_LOG.md` | Chronological research diary (append-only) |
| `DECISIONS.md` | Numbered decision records |
| `docs/checkpoints/` | Checkpoint reports for the owner |

## Status

**Checkpoint 1 (Architecture & Data Plan): submitted and awaiting approval.** See `docs/checkpoints/CP1_architecture_and_data_plan.md`.

## Restore and reproduce

These instructions will be completed at Checkpoint 2, once the tooling exists.

1. `git clone` this repository and use Python 3.11.
2. `pip install -e .`
3. Set the environment variables `QC_USER_ID` and `QC_API_TOKEN` (QuantConnect API credentials).
4. `python -m qresearch.run <EXPERIMENT_ID> --reproduce` re-runs a recorded experiment and verifies its result hashes.

Raw market data is not stored here. It is accessed inside QuantConnect Cloud, whose licence does not permit export.
