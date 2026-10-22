# qr_os1_trade v1.0 — H032 trading layer for R1 / R2 (owner D282; research/os/H032_R_protocol.md, frozen and SHA-256-
# pinned in qresearch.os1r). Pure logic on keys: no QuantConnect object, no I/O. The selection rules themselves are the
# frozen qr_os1 functions (plan, random_step, beta_step); this module only applies them to the books' ACTUAL holdings
# and turns targets into exits and slot-limited entries exactly as the harness does (D051: an exiting position keeps its
# slot until its sale executes; entries chosen at a review are retried at every later close until the next review).
import numpy as np
import qr_os1 as O

SHADOW = (("B1", "VB1", "B0", "MOM") + tuple(f"B2_{s}" for s in O.SEEDS_B2) + tuple(f"RND_{s}" for s in O.SEEDS_RND)
          + tuple(f"BETA_{s}" for s in O.SEEDS_BETA))     # shadow-engine books; "B1" = the shadow replay of LEAN B1


def ranked(scores, held):
    """Frozen Top-N with the 2N buffer on the book's held names -> (target keys sorted, entry priority = score order)."""
    if not scores:
        return [], []
    target = O.plan(scores, held)
    keep = set(target)
    return target, [k for k in O.order(scores) if k in keep]


def plans(rev, held, lean_held, pairs, k):
    """Targets of every book at review k. rev: s_b1, s_vb1, s_b0, mom (score dicts {key: (score, adv)}), pool_b2,
    pool_cov (key lists), quint ({key: 1..5}); held: {book: set of keys held after the orders already placed};
    lean_held: the same for the LEAN book; pairs: {beta seed: {B1 key: control key}}.
    -> (targets {book: (target, priority)} incl. 'LEAN', n_new = LEAN B1 entries, new pairs, beta attempted, matched)."""
    out = {"LEAN": ranked(rev["s_b1"], lean_held)}
    n_new = len(set(out["LEAN"][0]) - set(lean_held))
    out["B1"] = ranked(rev["s_b1"], held["B1"])
    out["VB1"] = ranked(rev["s_vb1"], held["VB1"])
    out["B0"] = ranked(rev["s_b0"], held["B0"])
    out["MOM"] = ranked(rev["mom"], held["MOM"])
    for s in O.SEEDS_B2:
        t = O.random_step(rev["pool_b2"], held[f"B2_{s}"], n_new, s, k)
        out[f"B2_{s}"] = (t, t)
    for s in O.SEEDS_RND:
        t = O.random_step(rev["pool_cov"], held[f"RND_{s}"], n_new, s, k)
        out[f"RND_{s}"] = (t, t)
    new_pairs, att, mat = {}, 0, 0
    for s in O.SEEDS_BETA:
        p, a, m = O.beta_step(pairs.get(s, {}), out["LEAN"][0], rev["quint"], s, k)
        new_pairs[s] = p
        att += a
        mat += m
        t = sorted(p.values())
        out[f"BETA_{s}"] = (t, t)
    return out, n_new, new_pairs, att, mat


def pending_after(priority, held):
    """Entries still to buy after a review: the target's names not yet held, in priority order."""
    h = set(held)
    return [x for x in priority if x not in h]


def exits_entries(target, pending, held, busy, n_slots=O.N, decision=False):
    """One close. held: names held and not already being sold; busy: every occupied slot (held incl. exiting names,
    pending buys). Exits (review closes only): held names outside the target. Entries: the first pending names that are
    not busy, at most the free slots; exiting names still occupy their slot until the sale executes (D051)."""
    tgt = set(target)
    exits = sorted(x for x in held if x not in tgt) if decision else []
    free = int(n_slots) - len(set(busy))
    entries = []
    b = set(busy)
    for x in pending:
        if free <= 0:
            break
        if x in b:
            continue
        entries.append(x)
        b.add(x)
        free -= 1
    return exits, entries


def ew_return(p0, p1):
    """Frictionless equal-weight return of the members with a usable start price: mean(p1 / p0 - 1); a member without
    an end price (no later price at all) counts as unchanged. -> (return, members used, members without end price)."""
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    ok = np.isfinite(p0) & (p0 > 0)
    if not ok.any():
        return None, 0, 0
    miss = ok & ~(np.isfinite(p1) & (p1 > 0))
    r = np.where(miss, 0.0, p1 / np.where(ok, p0, 1.0) - 1.0)
    return float(r[ok].mean()), int(ok.sum()), int(miss.sum())


class PnL:
    """Cash-flow P&L per stock of one shadow book (fills, dividends, split cash), closed at the final mark."""

    def __init__(self):
        self.flow = {}

    def add(self, g, x):
        self.flow[g] = self.flow.get(g, 0.0) + float(x)

    def fill(self, kind, g, q, px, fee):
        self.add(g, -q * px - fee)          # buys q > 0 (cash out); sells / delisting / stale q < 0 (cash in)

    def total(self, marks):
        """marks: {g: final value of the open position}. -> {g: P&L}."""
        out = dict(self.flow)
        for g, v in marks.items():
            out[g] = out.get(g, 0.0) + float(v)
        return out
