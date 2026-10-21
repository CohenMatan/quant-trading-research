"""H032 / OS-1 revised (owner D278): offline evaluation of the ONE canary C-OS1 (E807-01; E807-02 only as the documented
retry). Frozen with the specification (research/os/H032_spec.md section 8, pinned in qresearch.os1). It reads only the
run's aggregate 'OS1|' lines (counts, book sizes, digests; no prices, no returns, no identifiers) and applies the frozen
canary gates C1-C10. Nothing here computes or reads a return.

  C1  point in time: 0 SEC rows used on or after the review day (cover counts, annual reports, SIC filings).
  C2  identity: 0 reviews with a registrant matched twice; 0 repaired (restored) securities without the point-in-time
      identity.
  C3  annual inputs (same-filing comparative): from the start review, every calendar year's pooled F-OCF input
      coverage and F-REV input coverage (same-filing prior-year revenue) >= 70% of the H032 denominator.
  C4  share counts and splits, pooled from the start review: unknown split factor <= 5% of count pairs; sanity-bound
      exclusions <= 5% of pairs with known factors; split-adjusted pairs inside the bound >= 90% (at least 20
      split-adjusted pairs, else not verifiable -> fail).
  C5  G-COV1: a start review exists (first review with joint coverage >= 70%, equal to the in-run start) and joint
      coverage >= 65% at every review from it.
  C6  G-COV2: pooled over the reviews from the start whose 24-month horizon ends on or before the last stream day
      (2021-12-31; later reviews are CENSORED: the Holdout is never read), coverage of names still in the stream 24
      months later minus coverage of names that left <= 10 points (at least 30 leaving stock-months, else
      UNEVALUABLE, which is not a pass).
  C7  G-COV3: pooled from the start, coverage of restored (SEC-repaired) stock-months >= coverage of vendor stock-
      months - 10 points (at least 30 restored stock-months, else UNEVALUABLE, not a pass).
  C8  book feasibility: from the start, B1, the vendor-universe B1, B0, the five B2 and the five random books hold 15
      names at >= 99% of reviews; the momentum book at >= 99% of reviews with momentum available; the beta-matched
      books matched >= 95% of the B1 entries.
  C9  determinism: every book's in-run recomputation from the stored inputs gives the online digest.
  C10 subperiod A (start .. 2015-12) has >= 36 reviews; otherwise SHORT: reported before any return analysis and STOP
      for the owner (D278 item 4). Subperiod B is 2016-01 .. 2021-11.
Outcome: PASS when C1-C10 all pass; SHORT when only C10 fails; otherwise FAIL (STOP; no redesign or relaxation).
Writes research/os/OS1_canary_<run>.json and the extracted lines.

    PYTHONPATH=src python research/os/OS1_eval.py E807-01"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_os1 as O  # noqa: E402

COV_INPUT_MIN = 0.70
UNKNOWN_MAX, BOUND_MAX, SPLIT_IN_MIN, SPLIT_MIN_N = 0.05, 0.05, 0.90, 20
FULL_MIN, BETA_MIN_RATE = 0.99, 0.95
MIN_GROUP = 30
FULL_BOOKS = ["B1", "VB1", "B0"] + [f"B2_{s}" for s in O.SEEDS_B2] + [f"RND_{s}" for s in O.SEEDS_RND]


def parse(lines):
    res = dict(years={})
    for ln in lines:
        if not ln.startswith("OS1|"):
            continue
        _, sec, rest = ln.split("|", 2)
        if sec == "year":
            y, body = rest.split("|", 1)
            res["years"][y] = json.loads(body)
        else:
            res[sec] = json.loads(rest)
    return res


def _r(a, b):
    return a / b if b else None


def evaluate(res):
    meta = res["meta"]
    revs = [c for y in sorted(res["years"]) for c in res["years"][y]["reviews"]]
    cov = [_r(c["cov"], c["den"]) for c in revs]
    start = O.coverage_start(cov)
    after = revs[start:] if start is not None else []
    gates = {}
    ch = meta["checks"]
    gates["C1"] = dict(passed=ch["nsi_filing_on_or_after_t"] == 0 and ch["annual_filing_on_or_after_t"] == 0
                       and ch["pit_violations_ext"] == 0,
                       detail={k: ch[k] for k in ("nsi_filing_on_or_after_t", "annual_filing_on_or_after_t",
                                                  "pit_violations_ext")})
    gates["C2"] = dict(passed=ch["identity_duplicates"] == 0 and ch["repaired_without_identity"] == 0,
                       detail={k: ch[k] for k in ("identity_duplicates", "repaired_without_identity", "repaired_rows")})
    yrs = {}
    for c in after:
        a = yrs.setdefault(c["t"][:4], dict(den=0, ocf_in=0, rev_in=0))
        for k in a:
            a[k] += c[k]
    c3 = {y: dict(ocf=_r(a["ocf_in"], a["den"]), rev=_r(a["rev_in"], a["den"])) for y, a in yrs.items()}
    gates["C3"] = dict(passed=bool(c3) and all(v["ocf"] is not None and v["ocf"] >= COV_INPUT_MIN and
                                               v["rev"] >= COV_INPUT_MIN for v in c3.values()), detail=c3)
    S = {k: sum(c[k] for c in after) for k in ("sp_pairs", "sp_known", "sp_unknown", "sp_bound", "sp_bound_split",
                                              "sp_adjusted", "sp_adjusted_in_bound")}
    unk = _r(S["sp_unknown"], S["sp_pairs"])
    bnd = _r(S["sp_bound"] + S["sp_bound_split"], S["sp_known"])
    sin = _r(S["sp_adjusted_in_bound"], S["sp_adjusted"])
    gates["C4"] = dict(passed=unk is not None and unk <= UNKNOWN_MAX and bnd is not None and bnd <= BOUND_MAX
                       and S["sp_adjusted"] >= SPLIT_MIN_N and sin >= SPLIT_IN_MIN,
                       detail=dict(S, unknown_share=unk, bound_share=bnd, split_adjusted_in_bound=sin))
    low = [c["t"] for c in after if _r(c["cov"], c["den"]) < O.COV_MIN]
    gates["C5"] = dict(passed=start is not None and start == meta["start_index"] and not low,
                       detail=dict(start=revs[start]["t"] if start is not None else None,
                                   in_run_start_index=meta["start_index"], start_index=start, below_65=low,
                                   min_after_start=min((_r(c["cov"], c["den"]) for c in after), default=None)))
    g2 = dict(exit_den=0, exit_cov=0, stay_den=0, stay_cov=0, exit_restored_den=0, exit_restored_cov=0)
    censored = []
    for c in after:
        g = c["gcov2"]
        if not g["assessable"]:
            censored.append(c["t"])
            continue
        for k in g2:
            g2[k] += g[k]
    gap2 = None
    if g2["exit_den"] >= MIN_GROUP and g2["stay_den"]:
        gap2 = g2["stay_cov"] / g2["stay_den"] - g2["exit_cov"] / g2["exit_den"]
    gates["C6"] = dict(passed=gap2 is not None and gap2 <= O.GAP_MAX,
                       status="UNEVALUABLE" if gap2 is None else ("PASS" if gap2 <= O.GAP_MAX else "FAIL"),
                       detail=dict(g2, gap=gap2, censored_reviews=len(censored),
                                   censored_from=censored[0] if censored else None,
                                   censored_to=censored[-1] if censored else None))
    R = {k: sum(c[k] for c in after) for k in ("den_vendor", "cov_vendor", "den_restored", "cov_restored")}
    gap3 = None
    if R["den_restored"] >= MIN_GROUP and R["den_vendor"]:
        gap3 = R["cov_vendor"] / R["den_vendor"] - R["cov_restored"] / R["den_restored"]
    gates["C7"] = dict(passed=gap3 is not None and gap3 <= O.GAP_MAX,
                       status="UNEVALUABLE" if gap3 is None else ("PASS" if gap3 <= O.GAP_MAX else "FAIL"),
                       detail=dict(R, gap=gap3))
    full = {}
    for b in FULL_BOOKS:
        sz = [c["sizes"][b] for c in after]
        full[b] = _r(sum(1 for x in sz if x == O.N), len(sz))
    mom = [c["sizes"]["MOM"] for c in after if c.get("pool_mom")]
    full["MOM"] = _r(sum(1 for x in mom if x == O.N), len(mom))
    beta_rate = _r(meta["beta_matched"], meta["beta_attempted"])
    gates["C8"] = dict(passed=bool(after) and all(v is not None and v >= FULL_MIN for v in full.values())
                       and beta_rate is not None and beta_rate >= BETA_MIN_RATE,
                       detail=dict(full_share=full, beta_match_rate=beta_rate,
                                   beta_attempted=meta["beta_attempted"], beta_matched=meta["beta_matched"]))
    dig = meta["digests_online"] == meta["digests_recomputed"] and bool(meta["digests_online"])
    gates["C9"] = dict(passed=bool(meta["determinism"]) and dig, detail=dict(books=len(meta["digests_online"])))
    nA = sum(1 for c in after if c["t"][:7] <= "%04d-%02d" % O.SUB_A_END)
    nB = sum(1 for c in after if c["t"][:7] > "%04d-%02d" % O.SUB_A_END)
    gates["C10"] = dict(passed=nA >= O.SHORT_A_MONTHS, detail=dict(subperiod_A_reviews=nA, subperiod_B_reviews=nB))
    failed = [g for g, v in gates.items() if not v["passed"]]
    outcome = "PASS" if not failed else ("SHORT" if failed == ["C10"] else "FAIL")
    return dict(outcome=outcome, failed=failed, gates=gates, reported=_reported(res, revs, start))


def _reported(res, revs, start):
    """Non-gating reports: financial removal, vendor / restored / universe coverage, sector shares, NSI and growth
    quantiles, reasons, B1 entries and distinct names, coverage of later-disappearing names by year."""
    out = {}
    for y, Y in sorted(res["years"].items()):
        rv = Y["reviews"]
        el = sum(c["elig"] for c in rv)
        fin = sum(c["fin"] for c in rv)
        den = sum(c["den"] for c in rv)
        e = {k: sum(c["gcov2"][k] for c in rv) for k in ("exit_den", "exit_cov", "stay_den", "stay_cov")}
        out[y] = dict(
            eligible_mean=round(el / len(rv), 1), financial_removed_share=_r(fin, el),
            fin_unknown_share=_r(sum(c["fin_unknown"] for c in rv), den),
            joint_coverage=_r(sum(c["cov"] for c in rv), den),
            joint_coverage_known_non_financial=_r(sum(c["cov"] for c in rv), den - sum(c["fin_unknown"] for c in rv)),
            identity_share=_r(sum(c["ident"] for c in rv), el), pass_share=_r(sum(c["passed"] for c in rv), den),
            nsi_coverage=_r(sum(c["nsi"] for c in rv), den),
            vendor_universe_coverage=_r(sum(c["vcov"] for c in rv), sum(c["vden"] for c in rv)),
            vendor_coverage=_r(sum(c["cov_vendor"] for c in rv), sum(c["den_vendor"] for c in rv)),
            restored_coverage=_r(sum(c["cov_restored"] for c in rv), sum(c["den_restored"] for c in rv)),
            restored_den=sum(c["den_restored"] for c in rv),
            exit24_coverage=_r(e["exit_cov"], e["exit_den"]), stay24_coverage=_r(e["stay_cov"], e["stay_den"]),
            exit24_den=e["exit_den"], censored=not all(c["gcov2"]["assessable"] for c in rv),
            ff12_den=Y["ff12_den"], ff12_pass=Y["ff12_pass"], ff12_b1=Y["ff12_b1"],
            ff12_fin_removed=Y["ff12_fin_removed"], os_quantiles=Y["os_q"], growth_quantiles=Y["growth_q"],
            nsi_reasons=Y["nsi_reason"], ocf_reasons=Y["ocf_reason"], rev_reasons=Y["rev_reason"],
            identity=Y["identity_why"], b1_entries=Y["b1_entries"],
            b1_distinct=res["meta"]["b1_distinct_names_by_year"].get(y))
    return dict(start=revs[start]["t"] if start is not None else None, years=out)


def main(eid):
    from qresearch import results
    r = json.loads((ROOT / "experiments" / eid / "result.json").read_text())
    lines = results.lines_from_statistics(r["qc_statistics"])
    res = parse(lines)
    out = dict(run=eid, meta=res.get("meta"), evaluation=evaluate(res))
    (ROOT / f"research/os/{eid}_os1_lines.txt").write_text("\n".join(ln for ln in lines if ln.startswith("OS1|")) + "\n")
    (ROOT / f"research/os/OS1_canary_{eid}.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    o = main(sys.argv[1])
    print(json.dumps(dict(outcome=o["evaluation"]["outcome"], failed=o["evaluation"]["failed"]), indent=1))
