"""P13-CP5 (owner D238), after the synthetic audit: the STRUCTURAL fields of the committed H028 artifacts ->
P13_CP5_artifacts.json. Reads only structural fields (population counts, tether persistence counts, trade counts,
turnover, coefficient vectors, risk-distribution summaries already committed); no return, wealth or S_WEALTH column of
any null world is read, nothing is recomputed on market data, no QuantConnect run.

    PYTHONPATH=src python research/phase13/cp5/P13_CP5_artifacts.py
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7"),
                str(ROOT / "research/phase13/cp1")]
import qr_h026 as H  # noqa: E402
import qr_h027 as G  # noqa: E402
import P13_CP1_null as N  # noqa: E402

STRUCTURAL_ROW_FIELDS = ("seed", "maxdd", "vol", "beta", "up_capture", "down_capture") + \
    tuple(f"lam_{y}" for y in H.OUTER_YEARS) + ("coef_sha",)
TURNOVER_LIKE = re.compile(r"turnover|trade|order|commission|slippage|cost|pick|hold", re.I)


def coef_structure(B):
    B = np.asarray(B, float)
    l1 = np.abs(B).sum(1)
    cos = [float(B[i] @ B[i + 1] / (np.linalg.norm(B[i]) * np.linalg.norm(B[i + 1]))) for i in range(len(B) - 1)]
    return dict(lowvol_l1_share=float(np.mean(np.abs(B[:, G.LOWVOL]) / l1)), coef_cos_consecutive=float(np.mean(cos)),
                coef_l2=float(np.mean(np.linalg.norm(B, axis=1))),
                lowvol_sign_negative_years=int((B[:, G.LOWVOL] < 0).sum()))


def main():
    out = dict(checkpoint="P13-CP5", decision="D238", structural_only=True, quantconnect_runs=0,
               null_return_columns_read=False, holdout_accessed=False)
    # 1. donor re-mapping on the real H026 / H027 / H028 population (E029-01 canary, frozen conditional_permuted)
    msg = (ROOT / "experiments/E029-01/messages.txt").read_text()
    m = re.search(r'"conditional_permutation": (\{[^{}]*\})', msg)
    pc = json.loads(m.group(1))
    cov = json.loads((ROOT / "research/phase13/cp1/P13_CP1_canary_E030-01.json").read_text())["coverage"]
    rows_year = {int(y): v["all_11_valid"] for y, v in cov["by_year"].items()}
    n_first_est = rows_year[2011] / 12.0
    after = pc["rows"] - len((1, 2, 3)) * n_first_est
    not_possible = after - pc["persistence_checked"]
    per_review = not_possible / (3 * (cov["decisions"] - 1))
    n_mean = sum(rows_year.values()) / cov["decisions"]
    net = (rows_year[2021] / 11.0 - rows_year[2011] / 12.0) / (cov["decisions"] - 1)
    out["donor_remapping_real"] = dict(
        source="E029-01 canary (frozen qr_h027.conditional_permuted on the real H026 population, tether seeds 1-3, "
               "131 reviews each); population counts from the E030-01 canary coverage",
        recipient_rows=pc["rows"], recipient_rows_after_first_review_est=after, possible_continuations=pc["persistence_checked"],
        retained=pc["persistence_checked"] - pc["persistence_broken"], broken_while_possible=pc["persistence_broken"],
        self_matches=pc["self_matches"], reformed_rows_est=not_possible, reform_share_est=not_possible / after,
        reformed_per_review_est=per_review, mean_population=n_mean, net_growth_per_review=net,
        entries_per_review_est=(per_review + net) / 2.0, exits_per_review_est=(per_review - net) / 2.0,
        note="re-formed = recipient new to the population (entry / re-entry) or previous donor absent; the committed "
             "canary does not separate the two causes; entries / exits are estimated from re-formed = entries + donor "
             "exits and the net growth of the population")
    # 2. real H028 structural fields (committed P13-CP1 result; no return field read)
    res = json.loads((ROOT / "research/phase13/cp1/P13_CP1_result.json").read_text())
    comp = res["comparison"]
    B_real = [res["coefficients"][str(y)]["beta"] for y in H.OUTER_YEARS]
    out["real_h028_structural"] = dict(trades=comp["trades"], value_turnover_monthly_mean=comp["turnover_monthly_mean"],
                                       coefficients=coef_structure(B_real),
                                       commissions_from_trades=7.0 * comp["trades"]["h028"])
    # 3. what the committed null worlds hold
    st, nb, _ = N.run("E030-04")
    fields = nb["fields"]
    out["null_fields_committed"] = fields
    out["null_turnover_trade_cost_fields"] = [f for f in fields if TURNOVER_LIKE.search(f)]
    out["null_turnover_trades_costs"] = ("NOT AVAILABLE FROM COMMITTED ARTIFACTS" if not out["null_turnover_trade_cost_fields"]
                                         else "available")
    # 4. coefficient structure of null worlds 1-25 (full coefficients committed for the determinism seeds)
    cs = {s: coef_structure(v) for s, v in nb["coef"].items()}
    out["null_coefficients_seeds_1_25"] = {k: dict(median=float(np.median([c[k] for c in cs.values()])),
                                                   min=float(min(c[k] for c in cs.values())),
                                                   max=float(max(c[k] for c in cs.values())))
                                           for k in ("lowvol_l1_share", "coef_cos_consecutive", "coef_l2",
                                                     "lowvol_sign_negative_years")}
    out["null_coefficients_seeds"] = len(cs)
    # 5. structural row fields of the 5,000 worlds: risk metrics only (already summarised in P13_CP1_null.json)
    nul = json.loads((ROOT / "research/phase13/cp1/P13_CP1_null.json").read_text())
    out["null_risk_distributions_committed"] = {k: {q: nul["risk_distributions"][k][q] for q in ("q01", "q50", "q99")}
                                                for k in nul["risk_distributions"]}
    out["real_h028_risk_committed"] = {k: res["adequacy_step2"][k]["real"] for k in ("vol", "maxdd", "beta",
                                                                                      "down_capture")}
    txt = json.dumps(out, indent=1, sort_keys=True, default=float)
    (HERE / "P13_CP5_artifacts.json").write_text(txt + "\n")
    print(hashlib.sha256(txt.encode()).hexdigest()[:16])


if __name__ == "__main__":
    main()
