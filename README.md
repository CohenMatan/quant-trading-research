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

- **Checkpoint 1 (Architecture & Data Plan):** approved 2026-09-27.
- **Checkpoint 2 (Research Infrastructure):** report delivered 2026-09-27, awaiting approval (`docs/checkpoints/CP2_research_infrastructure.md`). A data-coverage decision is pending before any research.

## Restore and reproduce

1. `git clone` this repository and use Python 3.11+.
2. `pip install -e ".[test]"`, then `python -m pytest` (every test runs offline).
3. Set the environment variables `QC_USER_ID` and `QC_API_TOKEN` (QuantConnect API credentials). Never commit them.
4. Run commands:
   - `python -m qresearch.run <EXPERIMENT_ID>` runs a registered experiment. It needs a clean, committed tree.
   - `python -m qresearch.run <EXPERIMENT_ID> --reproduce` re-runs a recorded experiment on QuantConnect Cloud from the committed code and config, then compares the result hashes.
   - `python -m qresearch.audit E951-03` re-renders the data audit tables.

Raw market data is not stored here. It is accessed inside QuantConnect Cloud, whose licence does not permit export. Each experiment is pinned to a LEAN engine build (`lean_version_id` in its config). If QuantConnect retires that build, the runner refuses to run instead of silently switching.

## Layout

| Path | Contents |
|---|---|
| `src/qresearch/` | Runner, QuantConnect client, metrics, statistics, registry, integrity checks |
| `src/qresearch/lean/qr_harness.py` | Shared algorithm harness uploaded into every backtest |
| `strategies/` | S### research (S000 = pipeline demo), B9## benchmarks, X9## infrastructure algorithms |
| `experiments/INDEX.csv` | Append-only registry of every run |
| `experiments/E###-##/` | Config, result, equity, fills, trades and report per experiment |
| `docs/data/` | Data audit outputs |
