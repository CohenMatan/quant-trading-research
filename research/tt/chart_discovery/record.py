"""Append chart observations (OBSERVATION_protocol.md) to observations.jsonl, enforcing the fixed vocabulary.

Input lines on stdin: id|trend_252|trend_recent|location|ma_state|ma_slope|vol_regime|volume|gaps|setup|clarity|notes
"""
import json
import sys
from pathlib import Path

OUT = Path(__file__).parent / "observations.jsonl"
FIELDS = ("trend_252", "trend_recent", "location", "ma_state", "ma_slope", "vol_regime", "volume", "gaps", "setup",
          "clarity")
VOCAB = {
    "trend_252": {"UP", "DOWN", "SIDEWAYS", "V_UP", "INV_V"},
    "trend_recent": {"UP", "DOWN", "FLAT"},
    "location": {"AT_HIGH", "UPPER", "MIDDLE", "LOWER", "AT_LOW"},
    "ma_state": {"ABOVE_BOTH", "BETWEEN", "BELOW_BOTH", "NA"},
    "ma_slope": {"BOTH_RISING", "BOTH_FALLING", "MIXED", "FLAT", "NA"},
    "vol_regime": {"CONTRACTING", "EXPANDING", "STABLE"},
    "volume": {"RISING", "FALLING", "STABLE", "RECENT_SPIKE"},
    "gaps": {"NONE", "UP_GAP", "DOWN_GAP", "BOTH"},
    "setup": {"BREAKOUT_FROM_BASE", "TIGHT_RANGE_NEAR_HIGH", "PULLBACK_IN_UPTREND", "EXTENDED_RUN", "STEADY_UPTREND",
              "GAP_AND_HOLD", "BREAKDOWN", "DOWNTREND", "BASE_AFTER_DECLINE", "RANGE_BOUND", "RECOVERY_ATTEMPT",
              "NONE"},
    "clarity": {"CLEAR", "WEAK", "NONE"},
}


def parse(line: str) -> dict:
    p = [x.strip() for x in line.split("|", 11)]
    if len(p) != 12 or not (p[0].startswith("C") and p[0][1:].isdigit()):
        raise ValueError(f"bad line: {line!r}")
    rec = {"chart_id": p[0], **dict(zip(FIELDS, p[1:11])), "notes": p[11]}
    for k in FIELDS:
        if rec[k] not in VOCAB[k]:
            raise ValueError(f"{p[0]}: {k}={rec[k]!r} not in vocabulary")
    return rec


if __name__ == "__main__":
    seen = {json.loads(x)["chart_id"] for x in OUT.read_text().splitlines()} if OUT.exists() else set()
    recs = [parse(x) for x in sys.stdin.read().splitlines() if x.strip()]
    for r in recs:
        if r["chart_id"] in seen:
            raise SystemExit(f"{r['chart_id']} already recorded")
        seen.add(r["chart_id"])
    with OUT.open("a") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"recorded {len(recs)}; total {len(seen)}")
