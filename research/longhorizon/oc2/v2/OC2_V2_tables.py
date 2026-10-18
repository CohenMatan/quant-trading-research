"""OC-2 v2 (owner D250): format the committed confirmatory result `OC2_V2_results.json` into the OC-CP5 tables.
Formatting only: no statistic is recomputed and nothing in the frozen protocol, code or result is changed.

    python research/longhorizon/oc2/v2/OC2_V2_tables.py > tables.md
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent
STRENGTH = {"N5a": "controls' reliability 0.80", "N5b": "controls' reliability 0.60",
            "N2L1": "latent premium +1%/yr, corr 0.30", "N2L": "latent premium +3%/yr, corr 0.30",
            "N2L5": "latent premium +5%/yr, corr 0.30"}


def pct(x, d=2):
    return "—" if x is None else f"{100 * x:.{d}f}%"


def ci(c):
    return f"[{100 * c[0]:.2f}, {100 * c[1]:.2f}]"


def main():
    d = json.loads((HERE / "OC2_V2_results.json").read_text())
    S, roles, dec = d["scenarios"], d["roles"], d["decision_record"]
    print(f"Outcome: {dec['outcome']}\n")
    print("## Tier 1\n")
    print("| world | n | fail | rej 1% | 95% CI | rej 5% | 95% CI | mean t | sd t | bias (slope) | G2 mean | SE ratio "
          "| full rule | pass |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for n, s in S.items():
        if roles[n] != "gate":
            continue
        ok = n not in dec["tier1_size_failures"]
        print(f"| {n} | {s['n']} | {s['failures']} | {pct(s['rej_0.01'])} | {ci(s['rej_0.01_ci95'])} | "
              f"{pct(s['rej_0.05'])} | {ci(s['rej_0.05_ci95'])} | {s['mean_t']:.3f} | {s['sd_t']:.3f} | "
              f"{s['bias_mean_slope']:.5f} | {pct(s['tq_annual_mean'])} | {s['se_ratio']:.3f} | "
              f"{pct(s['full_rule'])} | {'PASS' if ok else 'FAIL'} |")
    print("\n## Tier 2\n")
    print("| world | strength | n | fail | rej 1% | rej 5% | full-rule approval | 95% CI | rule without G2 | "
          "bias (slope) | apparent effect | pass |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for n, s in S.items():
        if roles[n] != "ident":
            continue
        ok = n not in dec["tier2_failures"]
        print(f"| {n} | {STRENGTH[n.split('@')[0]]} | {s['n']} | {s['failures']} | {pct(s['rej_0.01'])} | "
              f"{pct(s['rej_0.05'])} | {pct(s['full_rule'])} | {ci(s['full_rule_ci95'])} | "
              f"{pct(s['rule_without_g2'])} | {s['bias_mean_slope']:.5f} | {pct(s['tq_annual_mean'])} | "
              f"{'PASS' if ok else 'FAIL'} |")
    o = S.get("N2L-oracle")
    if o:
        print(f"\nOracle (N2L +3% with the latent factor as a control): rej 1% {pct(o['rej_0.01'])}, 5% "
              f"{pct(o['rej_0.05'])}, full rule {pct(o['full_rule'])}, apparent effect {pct(o['tq_annual_mean'])}")
    print("\n## Power\n")
    print("| cell | n | Power A (1%) | Power A (5%) | Power B (full rule) | rule without G2 | G2 mean | T_eff |")
    print("|---|---|---|---|---|---|---|---|")
    for n, s in S.items():
        if roles[n] == "power":
            print(f"| {n} | {s['n']} | {pct(s['rej_0.01'], 1)} | {pct(s['rej_0.05'], 1)} | {pct(s['full_rule'], 1)} | "
                  f"{pct(s['rule_without_g2'], 1)} | {pct(s['tq_annual_mean'])} | {s['T_eff']:.0f} |")
    print("\n## MDE\n")
    for r, t in d["power"].items():
        fmt = lambda v: v if isinstance(v, str) or v is None else f"{100 * v:.2f}%"  # noqa: E731
        print(f"- IC sd {r}: test MDE50 {fmt(t['mde50_test'])}, MDE80 {fmt(t['mde80_test'])}; full-rule MDE50 "
              f"{fmt(t['mde50_rule'])}, MDE80 {fmt(t['mde80_rule'])}")
    print("\n## G2-floor sensitivity (report-only)\n")
    for n in ("P3-0.09", "P5-0.09", "N2L", "N2L5", "N2L5@0.12", "N5b"):
        if n in S:
            print(f"- {n}: " + ", ".join(f"floor {float(g) * 100:.1f}% → {pct(v)}"
                                       for g, v in S[n]["full_rule_g2_sensitivity"].items()))
    print("\n## Decision record\n")
    print(json.dumps(dec, indent=1, default=str))


if __name__ == "__main__":
    main()
