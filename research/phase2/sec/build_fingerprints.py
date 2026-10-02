"""Inputs for the public-float fingerprint runs of the identity v2 links (D113, D113a).

For every identity v2 registrant that is linked or ambiguous: SEC public float observations (10-K cover, 2009-2021)
each paired with the nearest single-class cover share count (within 100 days); the strategy divides float by
(cover shares x QuantConnect raw close) at the float date — a contradiction check, never a match by itself.

  python research/phase2/sec/build_fingerprints.py X977   # all pairs (the E977-01 inputs, built inline before D113a)
  python research/phase2/sec/build_fingerprints.py X978   # only pairs no earlier fingerprint run measured
                                                          # (registrants found after the 2020-2021 RSS fix)
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pack import pack  # noqa: E402
from qresearch.sec_pit import index_facts  # noqa: E402

DIRS = {"X977": "X977_identity_fingerprints_v2", "X978": "X978_identity_fingerprints_v3"}


def float_obs(client, cik):
    f = index_facts(client.companyfacts(int(cik)))
    fl = [x for x in f.get("EntityPublicFloat", ()) if x.get("form", "").startswith("10-K") and "2009" <= x["end"] <= "2021-12-31"]
    sh = f.get("EntityCommonStockSharesOutstanding", ())
    obs = []
    for x in sorted(fl, key=lambda x: x["end"]):
        near = [s for s in sh if abs((date.fromisoformat(s["end"]) - date.fromisoformat(x["end"])).days) <= 100]
        if not near:
            continue
        s = min(near, key=lambda s: abs((date.fromisoformat(s["end"]) - date.fromisoformat(x["end"])).days))
        if len({y["val"] for y in sh if y["accn"] == s["accn"]}) > 1 or not s["val"]:
            continue                                        # multi-class cover: no single count
        obs.append([x["end"], float(x["val"]), float(s["val"]), s["end"]])
    return obs


def main(which="X978"):
    import identity_v2
    v2 = json.loads((Path(__file__).parent / "identity_v2.json").read_text())["links"]
    done = set(identity_v2.float_pairs()) if which == "X978" else set()
    client = SECClient()
    fobs, pairs = {}, {}
    for cik, L in v2.items():
        if L["status"] != "linked" and not L["status"].startswith("ambiguous"):
            continue
        todo = [s for s in L["hits"] if (cik, s) not in done]
        if not todo:
            continue
        obs = float_obs(client, cik)
        if obs:
            fobs[cik], pairs[cik] = obs, todo
    d = ROOT / "strategies" / DIRS[which]
    d.mkdir(exist_ok=True)
    for p in d.glob("fp_ref*.py"):
        p.unlink()
    for n, t in pack({"float_obs": fobs, "pairs": pairs}, "fp_ref").items():
        (d / n).write_text(t)
    print(which, len(pairs), "registrants", sum(len(v) for v in pairs.values()), "pairs")


if __name__ == "__main__":
    main(*sys.argv[1:])
