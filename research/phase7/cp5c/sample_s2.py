"""P7-CP5c (D184): the PRE-REGISTERED supplementary probe sample S2, chosen from score tables only (no timing result,
no return), before any new-dataset timing probe ran. The main probe sample is the P2-CP6 X971 sample (seed 20261004,
fixed on 2026-10-01), which has an old-build (LEAN 18131) report-level record (E971-02). S2 adds the categories the
owner asked for (P7-CP5c item 8) from the E993-02 (LEAN 18131) and E993-03 (LEAN 18178) X993 exports:

  C1  became H2 only after the migration: in the H022 population (eligible, kept class, fully scorable) at some
      review under 18131 and disqualified by H2 at the same review under 18178 -> 4 per FF12 group (non-financial);
  C2  continuously inside the universe (eligible at all 84 reviews under 18131) -> 10;
  C3  grew into the universe (first eligible review 2012-01 or later under 18131, eligible at >= 12 reviews) -> 10;
  C4  SEC-repaired securities of the frozen correction layer that were eligible under 18131 -> 10.

Order inside each category: SHA-256 of "P7CP5c-S2|<category>|<sid>" (salt fixed here), excluding companies already
in the X971 sample or already chosen. CIK = the SEC-dated CIK in force at the sid's first review in the category
(sic_history), or the correction layer's CIK for C4; a sid without a CIK is skipped and counted.
Output: research/phase7/cp5c/sample_s2.json. No price, no return, no timing information is read."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
import qr_p7_export as E  # noqa: E402
import qr_sec_data as D  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402

SALT = "P7CP5c-S2"
PER_FF12, N_C2, N_C3, N_C4 = 4, 10, 10, 10


def tables(pay):
    sids = pay["sids"]
    return {t: {sids[r["i"]]: r for r in E.decode_rows(enc)} for t, tk, enc in pay["reviews"]}, pay["ff12_names"]


def order(cat, sids):
    return sorted(sids, key=lambda s: hashlib.sha256(f"{SALT}|{cat}|{s}".encode()).hexdigest())


def main():
    old_pay = json.loads(gzip.open(ROOT / "research/phase7/P7_CP3R_E993_payload.json.gz").read())
    new_pay = json.loads(E.unpack(joined(lines("E993-03"), "QRP7X")))
    old, ffn = tables(old_pay)
    new, _ = tables(new_pay)
    sec = D.load_table()
    hist = sec["sic_history"]
    x971 = json.loads((ROOT / "research/phase2/sec/x971_sample.json").read_text())
    taken_cik = {int(c) for c in x971}
    reviews = sorted(old)

    def cik_on(sid, day):
        out = None
        for eff, _sic, c in hist.get(sid, ()):
            if eff <= day and c not in (None, ""):
                out = int(c)
        return out

    chosen, skipped = [], {"no_cik": 0}

    def take(cat, cands, n, day_of, cik_fn=cik_on):
        got = 0
        for sid in order(cat, cands):
            if got >= n:
                break
            if any(sid == c["sid"] for c in chosen):
                continue
            cik = cik_fn(sid, day_of(sid))
            if cik is None:
                skipped["no_cik"] += 1
                continue
            if cik in taken_cik:
                continue
            taken_cik.add(cik)
            chosen.append(dict(sid=sid, cik=cik, category=cat, day=day_of(sid)))
            got += 1

    # C1 by FF12 group
    first_h2 = {}
    ff_of = {}
    for t in reviews:
        for sid, r in old[t].items():
            if E.eligible_flag(r["bits"], r["total"]):
                n = new.get(t, {}).get(sid)
                if n is not None and n["bits"] & E.BIT["H2"]:
                    first_h2.setdefault(sid, t)
                    ff_of.setdefault(sid, ffn[r["ff"]])
    for g in sorted(set(ff_of.values())):
        take(f"C1:{g}", [s for s in first_h2 if ff_of[s] == g], PER_FF12, lambda s: first_h2[s])
    elig = {}
    for t in reviews:
        for sid in old[t]:
            elig.setdefault(sid, []).append(t)
    take("C2", [s for s, ts in elig.items() if len(ts) == len(reviews)], N_C2, lambda s: elig[s][0])
    take("C3", [s for s, ts in elig.items() if ts[0] >= "2012-01" and len(ts) >= 12], N_C3, lambda s: elig[s][0])
    rep = {s: c for s, c in sec["corrections"].items() if c.get("status") == "repaired"}
    take("C4", [s for s in rep if s in elig], N_C4, lambda s: elig[s][0], lambda s, d: int(rep[s]["cik"][0]))
    out = dict(salt=SALT, rule=__doc__, n=len(chosen), skipped=skipped,
               by_category={c: sum(1 for x in chosen if x["category"].split(":")[0] == c) for c in ("C1", "C2", "C3", "C4")},
               c1_groups=sorted({x["category"] for x in chosen if x["category"].startswith("C1")}),
               sample=chosen)
    (Path(__file__).parent / "sample_s2.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["n"], out["by_category"], out["skipped"], len(out["c1_groups"]))


if __name__ == "__main__":
    main()
