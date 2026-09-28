# X954 — post-2010 survivorship-gap measurement (infrastructure, not research). No orders.
#
# Securities that later ended have no Morningstar fundamentals, so they can never enter the
# MarketCap >= $2B universe (D043). This measures, monthly from 2010, using the survivorship-free
# PRICE universe:
#   * candidates: securities WITHOUT fundamentals, price >= $5, ADV20 >= $5M, 63-day history, and not
#     an ETF-like "return twin" (|corr| >= 0.95 with another pool security) -- by ADV63 bucket
#   * calibration: among KNOWN US common stocks with the same filters, the share with MarketCap >= $2B
#     in each ADV63 bucket (used locally to estimate how many candidates are >= $2B)
#   * per candidate: last date seen in the price data and its last price / trailing drop -> whether it
#     ended before 2021-11 and whether the end looks like distress (bankruptcy-type) or not (merger-type)
#   * forward 1-month returns (groups formed up to forward_returns_until only, i.e. IS years)
# Logs: QRSG_M (monthly counts), QRSG_F (monthly forward returns by later status), QRSG_EX (examples).
from AlgorithmImports import *
from qr_harness import QRAlgorithm, EXCHANGES, is_us_common
from collections import deque
import json
import numpy as np

BUCKETS = (5e6, 10e6, 20e6, 40e6, 80e6)       # ADV63 lower edges: 5-10, 10-20, 20-40, 40-80, 80+ ($)
ENDED_BEFORE = "2021-11-01"


def bucket(adv):
    b = 0
    for i, edge in enumerate(BUCKETS):
        if adv >= edge:
            b = i
    return b


class SurvivorshipGap(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 900
        p = self.qr_params
        self.eval_from = str(p.get("eval_from", "2010-01-01"))
        self.fwd_until = str(p.get("forward_returns_until", ""))
        self.dv20, self.dv63, self.px = {}, {}, {}
        self.last_seen = {}                 # sid -> (date, price, ticker, price 126 obs earlier)
        self.hist126 = {}                   # sid -> deque of prices (126 obs)
        self.cand_months = {}               # sid -> list of (month, bucket)
        self.fwd = {}                       # formation date -> {"R": [rets], sid: ret}
        self.prev = None
        self.last_month = None

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        day = self.time.strftime("%Y-%m-%d")
        for f in fl:
            s = f.symbol
            dv, p = float(f.dollar_volume), float(f.price)
            if dv == dv:
                if s not in self.dv20:
                    self.dv20[s], self.dv63[s] = deque(maxlen=20), deque(maxlen=63)
                self.dv20[s].append(dv)
                self.dv63[s].append(dv)
            if p == p and p > 0:
                q = self.px.get(s)
                if q is None:
                    q = self.px[s] = deque(maxlen=64)
                    self.hist126[s] = deque(maxlen=126)
                q.append(p)
                self.hist126[s].append(p)
                self.last_seen[str(s.id)] = (day, p, s.value, self.hist126[s][0])
        month = day[:7]
        if month != self.last_month and day >= self.eval_from:
            self.last_month = month
            self._month(fl, day)
        return []

    def _month(self, fl, day):
        pool, known = [], {}
        for f in fl:
            s = f.symbol
            d20, d63 = self.dv20.get(s), self.dv63.get(s)
            if d20 is None or len(d20) < 20 or d63 is None or len(d63) < 63 or float(f.price) < 5:
                continue
            adv20, adv63 = sum(d20) / 20, sum(d63) / 63
            if not adv20 >= 5e6:
                continue
            if f.has_fundamental_data:
                if is_us_common(f) and str(f.security_reference.exchange_id) in EXCHANGES:
                    known[s] = (bucket(adv63), float(f.market_cap) >= 2e9)
            else:
                pool.append((s, adv63))
        twin = self._twin([s for s, _ in pool] + list(known))
        cands = [(s, a) for s, a in pool if twin.get(s, 0.0) < 0.95]
        n_c = [0] * len(BUCKETS)
        for s, a in cands:
            b = bucket(a)
            n_c[b] += 1
            self.cand_months.setdefault(str(s.id), []).append((day[:7], b))
        k_n, k_big = [0] * len(BUCKETS), [0] * len(BUCKETS)
        for b, big in known.values():
            k_n[b] += 1
            k_big[b] += int(big)
        self._qr_log(f"QRSG_M|{day}|" + json.dumps({"ref": len(self.qr_eligible), "cand": n_c, "known": k_n,
                                                     "known_big": k_big}, separators=(",", ":")))
        self._forward(day, [s for s, _ in cands])

    def _twin(self, symbols):
        rows, syms = [], []
        for s in symbols:
            q = self.px.get(s)
            if q is not None and len(q) == 64:
                rows.append(q)
                syms.append(s)
        if not rows:
            return {}
        m = np.clip(np.diff(np.log(np.array(rows, dtype=float)), axis=1), -0.25, 0.25)
        m = m - m.mean(axis=1, keepdims=True)
        sd = np.sqrt((m * m).sum(axis=1))
        ok = sd > 0
        z = np.zeros_like(m)
        z[ok] = m[ok] / sd[ok, None]
        c = np.abs(z @ z.T)
        np.fill_diagonal(c, 0.0)
        best = c.max(axis=1)
        return {s: float(b) for s, b in zip(syms, best)}

    def _forward(self, day, cands):
        now = self.time
        if self.prev is not None:
            t0, groups = self.prev
            syms = sorted({s for g in groups.values() for s in g}, key=lambda s: str(s.id))
            rets = {}
            h = self.history(syms, t0, now, Resolution.DAILY) if syms else None
            if h is not None and not h.empty:
                for sym, df in h["close"].groupby(level=0):
                    v = df.values
                    if len(v) >= 2 and v[0] > 0:
                        rets[sym] = float(v[-1] / v[0] - 1.0)
            r_ref = [rets[s] for s in groups["R"] if s in rets]
            self.fwd[f"{t0:%Y-%m-%d}"] = {"R": [round(sum(r_ref) / len(r_ref), 6) if r_ref else None, len(r_ref)],
                                          "C": {str(s.id): round(rets[s], 6) for s in groups["C"] if s in rets}}
            self.prev = None
        if self.fwd_until and day <= self.fwd_until:
            self.prev = (now, {"R": list(self.qr_eligible), "C": cands})

    def qr_on_end(self):
        status = {}
        for sid, (last, price, tick, p126) in self.last_seen.items():
            if sid not in self.cand_months:
                continue
            ended = last < ENDED_BEFORE
            distress = ended and (price < 5 or (p126 > 0 and price / p126 - 1 <= -0.5))
            status[sid] = "live" if not ended else ("end_distress" if distress else "end_other")
        per_year = {}
        for sid, months in self.cand_months.items():
            st = status.get(sid, "live")
            for m, b in months:
                y = per_year.setdefault(m[:4], {})
                key = f"{st}_{b}"
                y[key] = y.get(key, 0) + 1
        for y, d in sorted(per_year.items()):
            self._qr_log(f"QRSG_Y|{y}|" + json.dumps(d, sort_keys=True, separators=(",", ":")))
        for t0, d in sorted(self.fwd.items()):
            g = {"live": [], "end_distress": [], "end_other": []}
            for sid, r in d["C"].items():
                g[status.get(sid, "live")].append(r)
            out = {"R": d["R"]}
            for k, v in g.items():
                out[k] = [round(sum(v) / len(v), 6) if v else None, len(v)]
            self._qr_log(f"QRSG_F|{t0}|" + json.dumps(out, sort_keys=True, separators=(",", ":")))
        by_year = {}
        for sid, months in self.cand_months.items():
            if status.get(sid) in ("end_distress", "end_other"):
                last, price, tick, _ = self.last_seen[sid]
                y0 = months[0][0][:4]
                by_year.setdefault(y0, []).append((max(b for _, b in months), len(months), tick, last, price, status[sid]))
        for y, lst in sorted(by_year.items()):
            lst.sort(reverse=True)
            self._qr_log(f"QRSG_EX|{y}|n_ended={len(lst)}|" + ";".join(
                f"{t}:{l}:{p:.2f}:{'D' if s == 'end_distress' else 'O'}" for _, _, t, l, p, s in lst[:14]))
