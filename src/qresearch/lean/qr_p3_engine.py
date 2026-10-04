# qr_p3_engine.py — Phase 3 shadow-book engine (research/phase3/P3_spec.md). Pure numpy, no QuantConnect imports
# (tests/test_p3_engine.py). Simulates many virtual long-only slot-filling books with EXACTLY the harness mechanics of
# the verified H017/S017 books (qr_harness.plan_orders with D051 settled cash, slot_weight, FixedPerOrderFeeModel,
# ConstantSlippageModel, the D059 stale-exit and delisting conventions):
#   * decisions at a session's close; market-on-open fills at the next session with a bar: buys at open x (1 + slip),
#     sells at open x (1 - slip); $7 per executed order;
#   * sizing at the close: w = min(max(0.98/N, 1.01 x 4000 / pv), 0.10); quantity = int(w pv / close); a new position
#     must be worth >= $4,000; open positions (held + pending, incl. those being exited) <= min(N, pv x 0.98 // 4000);
#     settled cash only: plan = cash - $7 x sells placed now - 2% pv; buys need q p (1 + slip)(1 + 15%) + $7 each; if
#     short, every buy is scaled by plan / need, floored to whole shares, and dropped if below $4,000;
#   * fixed horizon: the exit order is placed at the close where sessions held >= H - 1 (fills at entry + H);
#   * splits: quantity / factor (whole shares; the fraction is paid in cash at the post-split reference price);
#     dividends: quantity x amount in cash; delisting: close at the last close, $7, no slippage; a holding without a
#     real bar for more than 10 sessions: closed at its last real close, $7.
# Per-book accounting state lives in (books x slots) arrays; per-stock prices in arrays indexed by a global stock index.
import numpy as np

EMPTY, PENDING, HELD = 0, 1, 2
STALE_SESSIONS = 10


class Books:
    def __init__(self, n_books, slots, hold, cash, slip=0.001, fee=7.0, buffer=0.02, gap=0.15, min_pos=4000.0,
                 max_w=0.10):
        B, N = int(n_books), int(slots)
        self.B, self.N, self.H = B, N, int(hold)
        self.slip, self.fee, self.buffer, self.gap, self.min_pos, self.max_w = slip, fee, buffer, gap, min_pos, max_w
        self.state = np.zeros((B, N), dtype=np.int8)
        self.sid = np.full((B, N), -1, dtype=np.int64)
        self.qty = np.zeros((B, N))               # held shares (HELD) or planned quantity (PENDING)
        self.esess = np.zeros((B, N), dtype=np.int64)
        self.psell = np.zeros((B, N), dtype=bool)
        self.cash = np.full(B, float(cash))
        self.commission = np.zeros(B)             # accumulated since last reset_costs()
        self.slippage = np.zeros(B)
        self.notional = np.zeros(B)
        self.fills = None                         # optional list of fill records (fidelity mode)
        self.counts = dict(entries=0, exits=0, forced_delist=0, forced_stale=0, skipped_min=0, skipped_cap=0,
                           scaled=0, split_adjust=0, dividends=0, cancelled_buys=0)

    # ---------------------------------------------------------------- helpers
    def _record(self, b, kind, s, q, px, fee):
        if self.fills is not None:
            self.fills.append((int(b), kind, int(s), float(q), float(px), float(fee)))

    def held_mask(self):
        return self.state == HELD

    def blocked(self, b):
        """Stock indices held or pending in book b (their new events are ignored)."""
        return set(self.sid[b][self.state[b] != EMPTY].tolist())

    def free(self):
        return self.N - (self.state != EMPTY).sum(axis=1)

    def equity(self, last_close):
        h = self.state == HELD
        v = np.where(h, self.qty * last_close[np.where(h, self.sid, 0)], 0.0)
        return self.cash + v.sum(axis=1)

    # ---------------------------------------------------------------- corporate actions (before the open)
    def split(self, s, factor, reference_price):
        hit = (self.sid == s) & (self.state != EMPTY)
        for b, k in zip(*np.nonzero(hit)):
            if self.state[b, k] == HELD:
                q = self.qty[b, k] / factor
                whole = np.floor(q + 1e-9)
                self.cash[b] += (q - whole) * reference_price * factor
                self.qty[b, k] = whole
            else:
                self.qty[b, k] = np.floor(self.qty[b, k] / factor + 1e-9)
            self.counts["split_adjust"] += 1

    def dividend(self, s, amount):
        hit = (self.sid == s) & (self.state == HELD)
        if hit.any():
            self.cash += np.where(hit, self.qty * amount, 0.0).sum(axis=1)
            self.counts["dividends"] += int(hit.sum())

    def delist(self, s, last_close):
        hit = (self.sid == s) & (self.state != EMPTY)
        for b, k in zip(*np.nonzero(hit)):
            if self.state[b, k] == HELD:
                self.cash[b] += self.qty[b, k] * last_close - self.fee
                self.commission[b] += self.fee
                self.notional[b] += self.qty[b, k] * last_close
                self._record(b, "delist", s, -self.qty[b, k], last_close, self.fee)
                self.counts["forced_delist"] += 1
            else:
                self.counts["cancelled_buys"] += 1
            self._clear(b, k)

    def _clear(self, b, k):
        self.state[b, k] = EMPTY
        self.sid[b, k] = -1
        self.qty[b, k] = 0.0
        self.psell[b, k] = False

    # ---------------------------------------------------------------- the open: execute pending orders
    def open_fills(self, open_px, has_bar, session):
        """Execute every pending order whose stock has a bar today (market-on-open)."""
        act = (self.state != EMPTY) & ((self.state == PENDING) | self.psell)
        if not act.any():
            return
        ok = act & has_bar[np.where(self.sid >= 0, self.sid, 0)]
        for b, k in zip(*np.nonzero(ok)):
            s = self.sid[b, k]
            o = open_px[s]
            if self.state[b, k] == HELD:                      # exit
                px = o * (1 - self.slip)
                q = self.qty[b, k]
                self.cash[b] += q * px - self.fee
                self.slippage[b] += q * o * self.slip
                self._record(b, "sell", s, -q, px, self.fee)
                self._clear(b, k)
                self.counts["exits"] += 1
            else:                                             # entry
                px = o * (1 + self.slip)
                q = self.qty[b, k]
                self.cash[b] -= q * px + self.fee
                self.slippage[b] += q * o * self.slip
                self.state[b, k] = HELD
                self.esess[b, k] = session
                self._record(b, "buy", s, q, px, self.fee)
                self.counts["entries"] += 1
            self.commission[b] += self.fee
            self.notional[b] += q * o

    # ---------------------------------------------------------------- the close
    def stale_exits(self, session, last_real_session, last_real_close):
        h = self.state == HELD
        if not h.any():
            return
        idx = np.where(h, self.sid, 0)
        stale = h & (session - last_real_session[idx] > STALE_SESSIONS)
        for b, k in zip(*np.nonzero(stale)):
            s = self.sid[b, k]
            px = last_real_close[s]
            self.cash[b] += self.qty[b, k] * px - self.fee
            self.commission[b] += self.fee
            self.notional[b] += self.qty[b, k] * px
            self._record(b, "stale", s, -self.qty[b, k], px, self.fee)
            self.counts["forced_stale"] += 1
            self._clear(b, k)

    def exits_due(self, session, extra=None):
        """Mark fixed-horizon exits (sessions held >= H - 1), plus optional extra (books x slots) exit flags."""
        due = (self.state == HELD) & ~self.psell & (session - self.esess >= self.H - 1)
        if extra is not None:
            due |= (self.state == HELD) & ~self.psell & extra
        self.psell |= due
        return due

    def plan_entries(self, b, stocks, price, pv, n_sells_now, skip=()):
        """Harness plan_orders (settled cash, gap reserve, min position, slot cap) for book b's new entries `stocks`
        (priority order, already limited to the free slots). Stocks in `skip` (delisting warned) are silently not bought,
        as the harness does; their slot stays free (no queue). Creates PENDING slots; returns the planned quantities."""
        if not len(stocks):
            return []
        w = min(max((1.0 - self.buffer) / self.N, 1.01 * self.min_pos / pv), self.max_w) if pv > 0 else 0.0
        cap = min(self.N, int(pv * (1.0 - self.buffer) // self.min_pos)) if self.min_pos > 0 else self.N
        positions = int((self.state[b] != EMPTY).sum())
        plan = []
        for s in stocks:
            p = float(price[s])
            if s in skip or not p > 0:
                continue
            q = int(w * pv / p)
            if q * p < self.min_pos:
                self.counts["skipped_min"] += 1
                continue
            if positions >= cap:
                self.counts["skipped_cap"] += 1
                continue
            plan.append([s, q, p])
            positions += 1
        cash_plan = self.cash[b] - self.fee * n_sells_now - self.buffer * pv
        need = sum(q * p * (1 + self.slip) * (1 + self.gap) + self.fee for _, q, p in plan)
        scale = 1.0
        if need > 0 and cash_plan < need:
            scale = max(0.0, cash_plan / need)
            self.counts["scaled"] += 1
        out = []
        free = np.nonzero(self.state[b] == EMPTY)[0]
        j = 0
        for s, q, p in plan:
            q = int(q * scale)
            if q <= 0:
                continue
            if q * p < self.min_pos:
                self.counts["skipped_min"] += 1
                continue
            k = free[j]
            j += 1
            self.state[b, k] = PENDING
            self.sid[b, k] = s
            self.qty[b, k] = q
            self.psell[b, k] = False
            out.append((s, q))
        return out

    def reset_costs(self):
        c = (self.commission.copy(), self.slippage.copy(), self.notional.copy())
        self.commission[:] = 0.0
        self.slippage[:] = 0.0
        self.notional[:] = 0.0
        return c


def select_candidates(order, mask_row, perm, blocked, free):
    """Entries of one book at a close: walk the primary's strength order (signal rows, best first), keep rows passing
    the configuration mask, map each signal row to its traded stock (perm; identity in the real world), skip blocked
    stocks (held / pending), take at most `free`. Nothing is queued."""
    out = []
    if free <= 0:
        return out
    for r in order[mask_row[order]]:
        s = int(perm[r])
        if s in blocked or s in out:
            continue
        out.append(s)
        if len(out) >= free:
            break
    return out


def strength_order(strength):
    """Signal rows by strength, highest first; ties by row (= security-id order); NaN last (never selected: masks are
    False where the strength is undefined)."""
    s = np.where(np.isfinite(strength), -strength, np.inf)
    return np.lexsort((np.arange(len(s)), s))


def null_permutation(seed, day_index, n, block=None):
    """Primary null: a fresh within-date permutation of the eligible signal rows onto the eligible traded stocks,
    seeded by (seed, day). Secondary diagnostic: block permutation, constant within `block` sessions."""
    k = day_index if block is None else day_index // int(block)
    return np.random.default_rng([int(seed), int(k), 7919]).permutation(n)
