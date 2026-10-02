# qr_h016.py — H016 (gross profitability) pure decision logic (research/phase2/H016_spec.md). No QuantConnect
# imports: unit-tested offline (tests/test_h016.py). Used identically by the candidate, the same-universe EW
# benchmark and the random controls (S016, one code path; only the ranking differs).
#
# GP/A(T) = gross_profit_ttm4q(T) / total_assets(T)
#   * gross_profit_ttm4q: frozen True TTM (data infrastructure v1, qr_fundamentals.PITStore.ttm_detail)
#   * total_assets: the current point-in-time report's snapshot, which must be the SAME fiscal quarter as the newest
#     quarter of the TTM window (no mixed periods); must exist and be > 0. Negative gross profit is allowed.
#   * optional stricter freshness (perturbation P6): newest TTM quarter at most `max_age_days` old on T.
import hashlib
from datetime import date

REBALANCE_MONTHS = (3, 6, 9, 12)


def gpa(store, key, today, max_age_days=None):
    """(GP/A, detail) or (None, reason) on decision date `today`, from historically available data only."""
    v, det = store.ttm_detail(key, "gross_profit", today)
    if v is None:
        return None, f"no gross-profit TTM: {det}"
    newest = det["quarters"][-1]
    if max_age_days is not None and (today - date.fromisoformat(newest)).days > int(max_age_days):
        return None, "newest quarter older than the freshness limit"
    r = store.record(key, today)
    if r is None or str(r.period_end) != newest:
        return None, "total assets not from the newest TTM quarter"
    ta = r.values.get("total_assets")
    if ta is None or not ta > 0:
        return None, "total assets missing or not positive"
    return v / ta, {"quarters": det["quarters"], "filed": det["filed"], "assets_period": str(r.period_end),
                    "assets_filed": str(r.file_date)}


def is_rebalance_day(today, prev_session, months=REBALANCE_MONTHS):
    """True on the first trading session of a rebalance month (`prev_session` = the previous session's date)."""
    return today.month in months and (prev_session is None or (prev_session.year, prev_session.month) !=
                                      (today.year, today.month))


def rank_gpa(values):
    """{key: GP/A} -> keys ordered by GP/A, highest first; ties by key ascending."""
    return sorted(values, key=lambda k: (-values[k], k))


def random_key(seed, key):
    """Frozen pseudo-random key of a security for a seed (independent of any data): SHA-256 of 'seed|id'."""
    return int(hashlib.sha256(f"{int(seed)}|{key}".encode()).hexdigest()[:16], 16)


def rank_random(keys, seed):
    """Keys ordered by their fixed random key for `seed` (persistent across rebalances); ties by key."""
    return sorted(keys, key=lambda k: (random_key(seed, k), k))


def plan_selection(ranked, held, n):
    """At a rebalance: the top-n of `ranked` is the selection; holdings outside it are exits; selected names not yet
    held are entries, in rank order. Continuing holdings are kept as they are."""
    sel = list(ranked[:n])
    s = set(sel)
    exits = sorted(k for k in held if k not in s)
    entries = [k for k in sel if k not in held]
    return sel, exits, entries


# ---------------------------------------------------------------- one-time top-up (owner 2026-10-02, option A)
# A newly opened position (initial formation or a later replacement) gets AT MOST ONE top-up, evaluated once, at the
# first close after its initial (reserve-scaled) fill. The top-up moves it toward its ORIGINAL slot target (slot weight
# x equity at the rebalance decision), never above it, funded only from settled cash after the 2% buffer, with the
# same D051 15% gap reserve, slippage and $7 commission as every purchase. When cash cannot fund every top-up of that
# close, all are scaled by one common factor. A top-up worth less than MIN_TOPUP_USD after scaling is not placed.
# MIN_TOPUP_USD = $250, from the fixed $7 commission alone (no strategy result was used): a top-up of X dollars removes
# X of idle cash for at least a quarter and typically a year; at a generic 6% a year equity premium its expected one-year
# benefit 0.06 X must be at least twice the commission, X >= 2 x $7 / 0.06 = $233, rounded up to $250 (commission at
# most 2.8% of the amount). This excludes economically trivial orders ($150-$200) while letting the typical reserve
# correction qualify ($500-$650 at $100K, $1,100-$1,300 at $200K). Offline stress (random share prices, +-8% open
# gaps): a $500 threshold would have dropped most $100K top-ups (about 2 of 20 placed, 87% invested); $250 places
# about 15 of 20 (93% invested). The same dollar rule applies to every book and account size.
MIN_TOPUP_USD = 250.0


def plan_topups(cands, cash, pv, buffer, gap, slip, fee, reserved=0.0, min_topup=MIN_TOPUP_USD):
    """cands: [(key, target_value, current_value, price)] — the positions whose single top-up is evaluated now.
    cash: settled cash; reserved: cash already committed at this close (entries). Returns {key: quantity}."""
    short = {}
    for key, target, value, price in cands:
        s = float(target) - float(value)
        if price > 0 and s >= min_topup:
            short[key] = (s, float(price))
    avail = float(cash) - float(reserved) - float(buffer) * float(pv)
    while short:
        need = sum(s * (1 + slip) * (1 + gap) + fee for s, _ in short.values())
        scale = 1.0 if need <= avail else max(0.0, (avail - fee * len(short)) / (need - fee * len(short)))
        small = [k for k, (s, p) in short.items() if int(s * scale / p) * p < min_topup]
        if not small:
            return {k: int(s * scale / p) for k, (s, p) in short.items()}
        for k in small:
            del short[k]
    return {}
