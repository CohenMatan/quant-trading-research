"""C03 backtest accounting (owner 2026-09-30): two transparent counts, from the registry.

research budget   = C03 research, control, capital-sensitivity and random-null backtests of the
                    approved design (every config with cycle C03 except the X963/X964 canaries and the
                    configs withdrawn by D087); cap 82 (D087: 21 committed + H013's pre-declared conditional runs). Technical retries
                    of an identical configuration are reported separately and are not new candidates.
operational usage = every QuantConnect execution of a C03 config (canaries, failed runs, retries).

    PYTHONPATH=src python research/cycles/C03_budget.py
"""
import json
import sys

sys.path.insert(0, "src")
from qresearch import config, experiment, registry  # noqa: E402

CAP = 82
CANARIES = ("X963", "X964")


def ledger():
    cfgs = {p.parent.name: json.loads(p.read_text()) for p in config.EXPERIMENTS_DIR.glob("E*/config.json")}
    gone = experiment.withdrawn()                  # D087: H012's configs, withdrawn before any run
    c03 = {e: c for e, c in cfgs.items() if c.get("cycle") == "C03" and e not in gone}
    runs = [r for r in registry.read() if r["run_type"] == "original" and r["experiment_id"] in c03]
    def is_research(c):     # canaries and technical repeats (identical config re-run) are operational only
        return c["strategy_id"] not in CANARIES and not c.get("technical_repeat_of")
    research = [r for r in runs if is_research(c03[r["experiment_id"]])]
    return dict(research_budget_used=len(research), research_budget_cap=CAP,
                research_configs_written=sum(1 for c in c03.values() if is_research(c)),
                technical_repeat_executions=sum(1 for r in runs if c03[r["experiment_id"]].get("technical_repeat_of")),
                operational_executions=len(runs) + sum(1 for r in registry.read()
                                                       if r["run_type"] == "recovery" and r["experiment_id"] in c03),
                operational_by_status={s: sum(1 for r in runs if r["status"] == s) for s in sorted({r["status"] for r in runs})},
                canary_executions=len(runs) - len(research))


if __name__ == "__main__":
    print(json.dumps(ledger(), indent=1))
