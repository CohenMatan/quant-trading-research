"""Inputs for X974 (D111): candidate pairs not tested by X971 — (a) registrants whose equity was still listed after
2021, (b) registrants whose QuantConnect security outlived them (holding-company successions) — restricted to
pairs passing the STRICT ticker-name rule (some ticker of the security, an in-order letter subsequence of a
registrant name in force at its float dates, same first letter). Float observations must be plausible
(float / cover shares <= $2,000 per share; XBRL unit errors excluded)."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch.sec_pack import pack  # noqa: E402
import e970_parse  # noqa: E402
from build_corrections import ticker_in_name  # noqa: E402

STRAT = ROOT / "strategies" / "X974_identity_fingerprints"


def main():
    t = e970_parse.load()
    cj = json.loads((Path(__file__).parent / "candidates.json").read_text())
    done = cj["pairs"]
    pairs, fobs = {}, {}
    for cik, c in cj["candidates"].items():
        if c["non_common_name"] or c["non_common_sic"]:
            continue
        obs = [o for o in c["float_obs"] if o[2] > 0 and o[1] / o[2] <= 2000]
        if not obs:
            continue
        months = {int(o[0][:4]) * 100 + int(o[0][5:7]) for o in obs}
        for sid, m in t["nofund"].items():
            if sid in done.get(cik, ()):
                continue                                   # already tested in X971
            if not any(m["first_ym"] <= ym <= m["last_ym"] for ym in months):
                continue
            tick = {x[0] for x in m["tickers"]} | {sid.split()[0]}
            if any(ticker_in_name(x, n) for x in tick for n in c["names"]):
                pairs.setdefault(cik, []).append(sid)
        if cik in pairs:
            fobs[cik] = obs
    for p in STRAT.glob("fp_ref*.py"):
        p.unlink()
    for name, text in pack({"float_obs": fobs, "pairs": pairs}, "fp_ref").items():
        (STRAT / name).write_text(text)
    (Path(__file__).parent / "x974_pairs.json").write_text(json.dumps(pairs, indent=1, sort_keys=True) + "\n")
    print(len(pairs), "registrants", sum(len(v) for v in pairs.values()), "pairs")


if __name__ == "__main__":
    main()
