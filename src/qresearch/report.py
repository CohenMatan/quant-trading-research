"""Human-readable per-experiment report (report.md next to result.json)."""
from __future__ import annotations

from pathlib import Path


def _pct(x) -> str:
    return "n/a" if x is None or x != x else f"{x * 100:.2f}%"


def _num(x, nd=2) -> str:
    return "n/a" if x is None or x != x else f"{x:.{nd}f}"


def metrics_table(m: dict) -> list[str]:
    rows = [
        ("Period", f"{m.get('start')} → {m.get('end')} ({m.get('n_days')} trading days)"),
        ("CAGR", _pct(m.get("cagr"))), ("Annualised volatility", _pct(m.get("ann_volatility"))),
        ("Sharpe (rf = 0)", _num(m.get("sharpe"))), ("Sortino", _num(m.get("sortino"))),
        ("Max drawdown", _pct(m.get("max_drawdown"))),
        ("Longest drawdown (trading days)", str(m.get("max_drawdown_duration_days"))),
        ("Calmar", _num(m.get("calmar"))), ("Worst year", _pct(m.get("worst_year"))),
        ("Worst month", _pct(m.get("worst_month"))),
    ]
    if "n_trades" in m:
        rows += [("Closed trades", str(m.get("n_trades"))), ("Win rate", _pct(m.get("win_rate"))),
                 ("Average winner", _pct(m.get("avg_win"))), ("Average loser", _pct(m.get("avg_loss"))),
                 ("Expectancy per trade", _pct(m.get("expectancy"))),
                 ("Profit factor", _num(m.get("profit_factor"))),
                 ("Average holding (calendar days)", _num(m.get("avg_holding_days"), 1))]
    if "exposure_mean" in m:
        rows += [("Average exposure", _pct(m.get("exposure_mean"))), ("Turnover (1-way, per year)", _num(m.get("turnover")))]
    out = ["| Metric | Value |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in rows]
    return out


def write_report(outdir: Path, cfg: dict, result: dict) -> None:
    p = result["provenance"]
    lines = [f"# {cfg['experiment_id']} — {cfg['strategy_id']} {cfg['strategy_version']} ({cfg['kind']})", "",
             cfg.get("description", ""), "",
             f"- **Status:** {result['status']}",
             f"- **Split:** {cfg['split']} ({cfg['start']} → {cfg['end']})",
             f"- **Commit:** `{p['git_commit']}` · **QC backtest:** `{p.get('qc_backtest_id')}` · "
             f"**LEAN:** {p.get('lean_version')} · **run:** {p['run_utc']} · **runtime:** {p.get('runtime_s', 0):.0f}s",
             f"- **Parameters:** `{cfg['params']}`",
             f"- **Costs:** `{cfg['costs']}` · **Universe:** `{cfg['universe']}` · **Portfolio:** `{cfg['portfolio']}`", ""]
    if result["status"] == "failed":
        lines += ["## Error", "", "```", str(result.get("error", ""))[:3000], "```"]
    else:
        lines += ["## Metrics", ""] + metrics_table(result["metrics"]) + [""]
        for seg, m in (result.get("segments") or {}).items():
            lines += [f"### Segment {seg}", ""] + metrics_table(m) + [""]
        if result.get("relative"):
            lines += ["## Relative to benchmarks", "", "| Benchmark | Excess CAGR | Beta | Correlation |", "|---|---|---|---|"]
            for k, v in result["relative"].items():
                lines.append(f"| {k} | {_pct(v['excess_cagr'])} | {_num(v['beta'])} | {_num(v['correlation'])} |")
            lines.append("")
        yr = result["metrics"].get("yearly_returns", {})
        if yr:
            lines += ["## Calendar-year returns", "", "| Year | Return |", "|---|---|"]
            lines += [f"| {y} | {_pct(v)} |" for y, v in yr.items()] + [""]
        lines += ["## Integrity checks", "", "| Check | Result | Detail |", "|---|---|---|"]
        for c in result["integrity"]:
            mark = "pass" if c["ok"] else ("FAIL" if c["level"] == "fail" else "warn")
            lines.append(f"| {c['check']} | {mark} | {c['detail']} |")
        lines += ["", "## Result hashes (SHA-256 of canonical CSV)", ""]
        lines += [f"- {k}: `{v}`" for k, v in result["hashes"].items()]
    if "reproduction" in result:
        lines += ["", "## Reproduction", "", f"- Original backtest: `{result['reproduction']['original_backtest']}`",
                  f"- Identical: **{result['reproduction']['identical']}** {result['reproduction']['hashes_match']}"]
    (outdir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
