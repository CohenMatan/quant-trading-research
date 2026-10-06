# qr_p7_mech.py — P7-CP3R (owner D173) PROVISIONAL portfolio mechanics planner for Conviction Score v1. Pure python, no
# QuantConnect imports (tests/test_p7_cp3r.py). It does not touch the frozen score or the frozen P7-CP2 planner
# (qr_p7_score.plan_review stays the reference); it adds the owner's provisional rules:
#   * ranking / tie-break: total score, then Fundamental subtotal, then Technical subtotal, then PIT ADV20 (higher
#     first), then the security id (P7-CP2 used total, ADV20, id; difference documented in P7-CP3R);
#   * market-regime position limits (STRONG 10 / NORMAL 8 / WEAK 5 / RISK_OFF 2): excess holdings are reduced at the
#     monthly review by exiting the lowest-ranked (reverse of the ranking key); the regime never changes a score;
#   * at most SECTOR_MAX holdings per PIT FF12 sector: a candidate from a full sector is skipped and the next one taken;
#   * one class per company: a candidate whose company is already held (any class) is skipped (the caller supplies the
#     held class's own record, so a held class is kept while it stays eligible);
#   * no relaxation ladder, no forced filling; weekly checks remain qr_p7_score.weekly_check (no entries).
# The grown-winner hard ceiling (20% of equity, trim back to 20% at the next monthly review) needs prices and is a
# recorded future rule only; no price, equity or return exists in this module.
SECTOR_MAX = 3
REGIME_POSITIONS = dict(STRONG=10, NORMAL=8, WEAK=5, RISK_OFF=2)
INITIAL_POSITION_CAP = 0.10
GROWN_WINNER_CAP = 0.20


def rank_key(rec, adv, sid):
    """Best first."""
    return (-rec["total"], -rec["fund"], -rec["tech"], -adv.get(sid, 0.0), sid)


def weak_key(rec, adv, sid):
    """Weakest first (the exact reverse of the ranking order)."""
    return (rec["total"], rec["fund"], rec["tech"], adv.get(sid, 0.0), _rev(sid))


def _rev(sid):
    return tuple(-ord(c) for c in sid)


def plan(holdings, records, adv, sector, company, entry, exit_, buffer, max_positions, regime_positions,
         frozen=frozenset(), universe=None, sector_max=SECTOR_MAX):
    """One monthly review. records: {sid: dict(total, fund, tech, eligible, dq)}; sector / company: {sid: key}.
    Returns dict(sell, buy, reasons, skipped_sector, skipped_company)."""
    assert exit_ < entry, "hysteresis: the exit threshold must be below the entry threshold"
    sell, keep, reasons = [], [], {}
    for h in sorted(holdings):
        r = records.get(h)
        if universe is not None and h not in universe:
            sell.append(h)
            reasons[h] = "left the eligible universe"
        elif h in frozen:
            keep.append(h)
            reasons[h] = "frozen (corporate-event contamination)"
        elif r is None or r.get("total") is None:
            sell.append(h)
            reasons[h] = "hard disqualifier: " + ", ".join(r["dq"] if r else ["no data"])
        elif not r["eligible"]:
            sell.append(h)
            reasons[h] = "hard disqualifier: " + ", ".join(r["dq"])
        elif r["total"] < exit_:
            sell.append(h)
            reasons[h] = f"score {r['total']} < exit {exit_}"
        else:
            keep.append(h)

    def wk(h):
        r = records.get(h)
        if r is None or r.get("total") is None:
            return (float("inf"),)
        return weak_key(r, adv, h)
    cap = min(max_positions, regime_positions)
    while len(keep) > cap:
        pool = [h for h in keep if h not in frozen]
        if not pool:
            break
        w = min(pool, key=wk)
        keep.remove(w)
        sell.append(w)
        reasons[w] = "regime position limit"
    book = list(keep)
    buy, skipped_sector, skipped_company = [], [], []
    cands = sorted((k for k, r in records.items() if r.get("eligible") and r["total"] >= entry and k not in holdings),
                   key=lambda k: rank_key(records[k], adv, k))

    def n_sector(g, excl=None):
        if g is None:                               # no PIT sector: no sector cap applies
            return 0
        return sum(1 for h in book if sector.get(h) == g and h != excl)
    for k in cands:
        if any(company.get(h, h) == company.get(k, k) for h in book):
            skipped_company.append(k)
            continue
        g = sector.get(k)
        if len(book) < cap:
            if n_sector(g) >= sector_max:
                skipped_sector.append(k)
                continue
            book.append(k)
            buy.append(k)
            reasons[k] = f"entry (score {records[k]['total']} >= {entry})"
            continue
        pool = [h for h in book if h not in frozen and h not in buy]
        if not pool:
            break
        w = min(pool, key=wk)
        if records[k]["total"] < records[w]["total"] + buffer:
            break                                   # candidates are sorted: no later one clears the buffer
        if n_sector(g, excl=w) >= sector_max:
            skipped_sector.append(k)
            continue
        book.remove(w)
        sell.append(w)
        reasons[w] = f"replaced by {k} ({records[k]['total']} >= {records[w]['total']} + {buffer})"
        book.append(k)
        buy.append(k)
        reasons[k] = f"replacement (score {records[k]['total']})"
    return dict(sell=sell, buy=buy, reasons=reasons, skipped_sector=skipped_sector, skipped_company=skipped_company)
