"""P4-CP1 design study: the PROPOSED Weekly stock-selection grammar (not frozen, not approved). Counts and graph only:
no data, no returns. Enumerates the configurations, their canonical ids, the one-step neighbour graph used by the plateau
rule, and the simplicity attributes.

Grammar (proposal):
  primary   : a Weekly TREND STATE (directional persistence). It defines BOTH the entry setup AND the exit: a position is
              held while its primary state stays true at weekly closes, and sold at the next session's open after the
              first weekly close at which it is false.
  confirm   : 0 or 1 ENTRY-ONLY condition from a different information group (relative strength, 52-week-high
              proximity, trend strength, momentum oscillator). Not used for exits ("let winners run").
  risk      : 0 or 1 ENTRY-ONLY volatility filter (ordinal: none -> rank <= 80% -> rank <= 50%).
  ranking   : fixed, not searched: 26-week return skipping the latest 4 weeks (relative strength), highest first.

    python research/phase4/P4_search_space.py -> P4_search_space.json
"""
import collections
import hashlib
import json
import math
from pathlib import Path

# type -> (information group, [(axis, ordered values)], meaning)
PRIMARY = {
    "WP1": ("direction", [("L", [20, 30, 40])], "weekly close > SMA(L weeks)"),
    "WP2": ("direction", [("SL", [(10, 30), (13, 40), (17, 52)])], "SMA(S) > SMA(L) on weekly closes"),
    "WP3": ("direction", [("K", [26, 52])], "time-series momentum: K-week return > 0"),
}
CONFIRM = {
    "CRS": ("relative_strength", [("q", [0.20, 0.40])], "26-week return (skip 4) in the top q of eligible stocks"),
    "CHI": ("range_position", [("x", [0.05, 0.15])], "weekly close >= (1 - x) x highest weekly close of 52 weeks"),
    "CADX": ("trend_strength", [("a", [20, 25])], "Wilder ADX(14 weeks) >= a"),
    "CRSI": ("oscillator", [("r", [50, 60])], "Wilder RSI(14 weeks) >= r"),
    "CMH": ("oscillator", [], "weekly MACD(12, 26) line above its 9-week signal (histogram > 0)"),
}
RISK = [None, 0.80, 0.50]          # 26-week realised volatility (weekly log returns), cross-sectional rank <= level


def variants(types):
    out = []
    for t, (grp, axes, _m) in types.items():
        idx = [[]]
        for _a, vals in axes:
            idx = [i + [k] for i in idx for k in range(len(vals))]
        out += [(t, grp, tuple(i)) for i in idx]
    return out


def key(p, c, r):
    return f"{p[0]}:{','.join(map(str, p[2]))}|" + ("-" if c is None else f"{c[0]}:{','.join(map(str, c[2]))}") + f"|R{r}"


def enumerate_configs():
    out = []
    for p in variants(PRIMARY):
        for c in [None] + [c for c in variants(CONFIRM) if c[1] != p[1]]:
            for r in range(len(RISK)):
                k = key(p, c, r)
                out.append(dict(id="W" + hashlib.sha256(k.encode()).hexdigest()[:10], key=k, primary=p, confirm=c,
                                risk=r))
    return out


def neighbours(cfgs):
    """One grid step on one axis (primary axis within the same primary type; confirmation axis within the same type;
    the risk axis). Same definition as the frozen Phase 3 rule."""
    by = {(c["primary"][0], c["primary"][2], None if c["confirm"] is None else (c["confirm"][0], c["confirm"][2]),
           c["risk"]): c["id"] for c in cfgs}
    out = {}
    for c in cfgs:
        pt, pi = c["primary"][0], c["primary"][2]
        cf = None if c["confirm"] is None else (c["confirm"][0], c["confirm"][2])
        nb = []
        for a in range(len(pi)):
            for d in (-1, 1):
                j = list(pi)
                j[a] += d
                if 0 <= j[a] < len(PRIMARY[pt][1][a][1]):
                    nb.append((pt, tuple(j), cf, c["risk"]))
        if cf is not None:
            for a in range(len(cf[1])):
                for d in (-1, 1):
                    j = list(cf[1])
                    j[a] += d
                    if 0 <= j[a] < len(CONFIRM[cf[0]][1][a][1]):
                        nb.append((pt, pi, (cf[0], tuple(j)), c["risk"]))
        for d in (-1, 1):
            if 0 <= c["risk"] + d < len(RISK):
                nb.append((pt, pi, cf, c["risk"] + d))
        out[c["id"]] = sorted(by[k] for k in nb if k in by)
    return out


def complexity(c):
    n_cond = 1 + (c["confirm"] is not None) + (c["risk"] > 0)
    n_par = len(PRIMARY[c["primary"][0]][1]) + (len(CONFIRM[c["confirm"][0]][1]) if c["confirm"] else 0) + (c["risk"] > 0)
    return n_cond, n_par


def main():
    C = enumerate_configs()
    nb = neighbours(C)
    deg = collections.Counter(len(v) for v in nb.values())
    # connected components of the full graph (upper bound on any cluster)
    seen, comps = set(), []
    for c in C:
        if c["id"] in seen:
            continue
        st, comp = [c["id"]], 0
        seen.add(c["id"])
        while st:
            x = st.pop()
            comp += 1
            for y in nb[x]:
                if y not in seen:
                    seen.add(y)
                    st.append(y)
        comps.append(comp)
    out = dict(
        status="PROPOSAL (P4-CP1); not frozen",
        primary={k: dict(group=v[0], axes=v[1], meaning=v[2]) for k, v in PRIMARY.items()},
        confirm={k: dict(group=v[0], axes=v[1], meaning=v[2]) for k, v in CONFIRM.items()},
        risk_levels=RISK, primary_variants=len(variants(PRIMARY)), confirm_variants=len(variants(CONFIRM)),
        configurations=len(C), ids_unique=len({c["id"] for c in C}) == len(C),
        by_primary_type=dict(collections.Counter(c["primary"][0] for c in C)),
        neighbour_degree=dict(sorted(deg.items())), edges=sum(len(v) for v in nb.values()) // 2,
        graph_components=dict(sorted(collections.Counter(comps).items())),
        complexity=dict(sorted(collections.Counter(map(str, (complexity(c) for c in C))).items())),
        list_sha256=hashlib.sha256("".join(f"{c['id']}|{c['key']}\n" for c in C).encode()).hexdigest(),
        free_and_combinations_up_to_3=sum(math.comb(19, k) for k in (1, 2, 3)),
        free_and_combinations_up_to_8=sum(math.comb(19, k) for k in range(1, 9)),
        free_note="free ANDs of the same 19 condition variants (8 primary + 9 confirmation + 2 risk), ignoring the "
                  "exit role; the grammar admits 240")
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("configurations", "by_primary_type", "neighbour_degree", "edges",
                                          "graph_components", "complexity")}, indent=1))


if __name__ == "__main__":
    main()
