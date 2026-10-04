# qr_p3_grammar.py — Phase 3 constrained strategy grammar (research/phase3/P3_spec.md). Pure Python, no QuantConnect
# imports; shared by the LEAN engine and the local pipeline/tests. Enumerates the FINITE Stage-1 search space:
#     Strategy = 1 primary setup  AND  0/1 confirmation from a DIFFERENT information family  AND  0/1 volatility filter
# Ranking = the primary's own strength. Every configuration has a stable id derived from its canonical key.
# Nothing here reads data or returns.
import hashlib

# ---------------------------------------------------------------- primary setups: type -> (family, axes)
# axes: ordered list of (axis name, ordered values); neighbours differ by one step on one axis
PRIMARY_TYPES = {
    "T1": ("trend", [("L", [50, 100, 150, 200])]),                                   # close > SMA(L)
    "T2": ("trend", [("SL", [(20, 100), (50, 150), (50, 200)])]),                    # SMA(S) > SMA(L)
    "T3": ("trend", [("L", [100, 200])]),                                            # 21-session slope of SMA(L) > 0
    "M1": ("momentum", [("K", [63, 126, 252]), ("q", [0.10, 0.20, 0.30])]),          # top q rank of return(K, skip 21)
    "M2": ("momentum", [("K", [63, 126, 252])]),                                     # return(K) > 0
    "M3": ("momentum", [("K", [63, 126, 252])]),                                     # return(K) - SPY return(K) > 0
    "B1": ("breakout", [("N", [63, 126, 252]), ("x", [0.0, 0.05, 0.10])]),           # close >= (1-x) max close(N)
    "R1": ("pullback", [("nt", [(2, 10), (2, 20), (5, 30), (14, 40)])]),             # RSI(n) <= theta
    "R2": ("pullback", [("y", [0.03, 0.06])]),                                       # close <= SMA20 (1-y)
    "R3": ("pullback", [("z", [0.0, 0.2])]),                                         # Bollinger %b(20,2) <= z
}
# ---------------------------------------------------------------- confirmations: type -> (family, axes)
CONFIRM_TYPES = {
    "cT_sma200": ("trend", []),                                                      # close > SMA200
    "cT_cross": ("trend", []),                                                       # SMA50 > SMA200
    "cT_adx": ("trend", [("a", [20, 25])]),                                          # ADX(14) >= a
    "cT_macd0": ("trend", []),                                                       # EMA12 > EMA26
    "cM_r126": ("momentum", []),                                                     # return(126) > 0
    "cM_r252s": ("momentum", []),                                                    # return(252, skip 21) > 0
    "cM_rsi": ("momentum", [("r", [50, 60])]),                                       # RSI(14) >= r
    "cM_macdsig": ("momentum", []),                                                  # MACD(12,26) > signal(9)
    "cB_hi252": ("breakout", []),                                                    # close >= 0.9 max close(252)
    "cR_rsi5": ("pullback", []),                                                     # RSI(5) <= 30
    "cR_sma20": ("pullback", []),                                                    # close < SMA20
    "cP_rv": ("participation", [("v", [1.0, 1.25])]),                                # mean vol(20) / mean vol(120) >= v
}
# ---------------------------------------------------------------- risk filter: ordinal axis none -> 80% -> 50%
RISK_LEVELS = [None, 0.80, 0.50]        # realised-vol(63) cross-sectional rank (ascending) <= level

FAMILIES = ("trend", "momentum", "breakout", "pullback", "participation", "volatility")


def _variants(types):
    out = []
    for t, (fam, axes) in types.items():
        if not axes:
            out.append((t, fam, ()))
            continue
        idx = [[]]
        for _name, vals in axes:
            idx = [i + [k] for i in idx for k in range(len(vals))]
        for i in idx:
            out.append((t, fam, tuple(i)))
    return out


def primary_variants():
    return _variants(PRIMARY_TYPES)


def confirm_variants():
    return _variants(CONFIRM_TYPES)


def params_of(types, t, idx):
    """{axis name: value} of a variant."""
    return {name: vals[i] for (name, vals), i in zip(types[t][1], idx)}


def key_of(p, c, r):
    """Canonical key of a configuration: primary (type, axis indices), confirmation or None, risk level index."""
    ps = f"{p[0]}:{','.join(map(str, p[2]))}"
    cs = "-" if c is None else f"{c[0]}:{','.join(map(str, c[2]))}"
    return f"{ps}|{cs}|R{r}"


def config_id(key):
    return "C" + hashlib.sha256(key.encode()).hexdigest()[:10]


def enumerate_configs():
    """The frozen Stage-1 configuration list, in canonical order: [dict(id, key, primary, confirm, risk)]."""
    out = []
    confs = confirm_variants()
    for p in primary_variants():
        for c in [None] + [c for c in confs if c[1] != p[1]]:          # confirmation from a DIFFERENT family
            for r in range(len(RISK_LEVELS)):
                k = key_of(p, c, r)
                out.append(dict(id=config_id(k), key=k, primary=p, confirm=c, risk=r))
    return out


def neighbours(configs):
    """Neighbourhood graph: two configurations are neighbours iff they differ by exactly ONE step: one grid step on
    one ordinal axis of the primary (same primary type), or of the confirmation (same confirmation type), or one step of
    the risk axis (none <-> 80% <-> 50%). Returns {id: sorted list of neighbour ids}."""
    by_key = {(c["primary"][0], c["primary"][2], None if c["confirm"] is None else (c["confirm"][0], c["confirm"][2]),
               c["risk"]): c["id"] for c in configs}
    out = {}
    for c in configs:
        pt, pi = c["primary"][0], c["primary"][2]
        cf = None if c["confirm"] is None else (c["confirm"][0], c["confirm"][2])
        r = c["risk"]
        nb = []
        for a in range(len(pi)):
            for d in (-1, 1):
                j = list(pi)
                j[a] += d
                if 0 <= j[a] < len(PRIMARY_TYPES[pt][1][a][1]):
                    nb.append((pt, tuple(j), cf, r))
        if cf is not None:
            ct, ci = cf
            for a in range(len(ci)):
                for d in (-1, 1):
                    j = list(ci)
                    j[a] += d
                    if 0 <= j[a] < len(CONFIRM_TYPES[ct][1][a][1]):
                        nb.append((pt, pi, (ct, tuple(j)), r))
        for d in (-1, 1):
            if 0 <= r + d < len(RISK_LEVELS):
                nb.append((pt, pi, cf, r + d))
        out[c["id"]] = sorted(by_key[k] for k in nb if k in by_key)
    return out


def complexity(c):
    """Lexicographic simplicity key (smaller = simpler): (number of active conditions / information families,
    number of tunable parameters = grid axes of the active components)."""
    n_cond = 1 + (c["confirm"] is not None) + (c["risk"] > 0)
    n_par = len(PRIMARY_TYPES[c["primary"][0]][1])
    if c["confirm"] is not None:
        n_par += len(CONFIRM_TYPES[c["confirm"][0]][1])
    if c["risk"] > 0:
        n_par += 1
    return n_cond, n_par
