"""C03 backtest accounting (owner 2026-09-30): two transparent counts, from the registry.

research budget   = C03 research, control, capital-sensitivity and random-null backtests of the
                    approved design (every config with cycle C03 except the X963/X964 canaries);
                    cap 82 (32 committed + <= 48 conditional + ... as pre-declared). Technical retries
                    of an identical configuration are reported separately and are not new candidates.
operational usage = every QuantConnect execution of a C03 config (canaries, failed runs, retries).

    PYTHONPATH=src python research/cycles/C03_budget.py
"""
import json
import sys

sys.path.insert(0, "src")
from qresearch import config, registry  # noqa: E402

CAP = 82
CANARIES = ("X963", "X964")


def ledger():
    cfgs = {p.parent.name: json.loads(p.read_text()) for p in config.EXPERIMENTS_DIR.glob("E*/config.json")}
    c03 = {e: c for e, c in cfgs.items() if c.get("cycle") == "C03"}
    runs = [r for r in registry.read() if r["run_type"] == "original" and r["experiment_id"] in c03]
    research = [r for r in runs if c03[r["experiment_id"]]["strategy_id"] not in CANARIES]
    return dict(research_budget_used=len(research), research_budget_cap=CAP,
                research_configs_written=sum(1 for c in c03.values() if c["strategy_id"] not in CANARIES),
                operational_executions=len(runs) + sum(1 for r in registry.read()
                                                       if r["run_type"] == "recovery" and r["experiment_id"] in c03),
                operational_by_status={s: sum(1 for r in runs if r["status"] == s) for s in sorted({r["status"] for r in runs})},
                canary_executions=len(runs) - len(research))


if __name__ == "__main__":
    print(json.dumps(ledger(), indent=1))
