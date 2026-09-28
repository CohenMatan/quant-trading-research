# X953 v1.1 — size-proxy evaluation (infrastructure, not research). Places no orders.
# v1.1: share-class rule from the harness (is_us_common, D030) for the reference and exclusion E1.
#
# Compares survivorship-free, price/volume-only universe rules ("proxies") with the reference
# universe (harness eligible set: common primary share, major exchange, MarketCap >= $2B,
# price >= $5, ADV20 >= $5M) on the first trading day of each month. Plan and thresholds were
# pre-registered in docs/data/size_proxy_plan.md.
#
# Output (log lines, compact to respect QC's 100 KB log cap):
#   QRPX_Y|year|variant|months|nP|nR|TP|FP|FN|f1_min|f1_max      summed over the year's months
#   QRPX_C|year|variant|json      characterisation of the primary variants (E1 exclusion)
#   QRPX_S|year|json              sector counts: reference vs primary proxies (fundamental names)
#   QRPX_F|date|json              equal-weight forward returns of groups formed one month earlier
#   QRPX_X|year|variant|tickers   most-traded false positives without fundamentals
#   QRPX_T|json                   tracked failed/acquired companies: months in reference / pool / proxies
#   QRPX_CHK|json                 reference set vs harness eligible set (must agree)
from AlgorithmImports import *
from qr_harness import QRAlgorithm, COMMON_STOCK, EXCHANGES, is_us_common
from collections import deque
import json
import math
import numpy as np

A_N = (500, 750, 1000, 1250, 1500)
B_C = (80, 85, 90, 95)
C_X = (5, 10, 20, 40)                      # $M
PRIMARY = ("A1000", "B90", "C20")
EXCL_ALL_RULES = ("E1",)                   # full grid only under the base exclusion
EXCL_PRIMARY_ONLY = ("E0", "E2", "E3", "E4", "E5_90", "E5_95", "E5_98")
TWIN = (0.90, 0.95, 0.98)                  # E5 (added after the 2010 scratch test; see report)
TRACK = ("ENE", "WCOM", "LEH", "BSC", "MER", "CFC", "WM", "LU", "GM", "WB", "AOL", "TYC",
         "DELL", "HNZ", "SHLD", "EMC", "YHOO", "TWX", "MON", "CELG", "RTN", "ESRX")


def _mean(d):
    return sum(d) / len(d)


def _med(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


class SizeProxyEval(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 2000
        self.fwd_until = str(self.qr_params.get("forward_returns_until", ""))
        self.eval_from = str(self.qr_params.get("eval_from", "0000-00-00"))   # after a >= 63-day pre-roll
        self.dv20, self.dv63, self.px = {}, {}, {}
        self.last_month = None
        self.acc = {}          # (year, variant) -> [months, nP, nR, TP, FP, FN, f1min, f1max]
        self.char = {}         # (year, primary) -> dict of accumulators
        self.sector = {}       # year -> {"R": {code: n}, primary: {code: n}}
        self.prev = None       # (datetime, {group: [symbols]})
        self.track_sid = {}
        self.track = {}
        self.chk = {"months": 0, "max_diff": 0, "sum_diff": 0}
        self.examples_done = set()

    # ------------------------------------------------------------------ daily
    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)                                # harness reference set (qr_eligible)
        for f in fl:
            s = f.symbol
            dv = float(f.dollar_volume)
            if dv == dv:
                d = self.dv20.get(s)
                if d is None:
                    d = self.dv20[s] = deque(maxlen=20)
                    self.dv63[s] = deque(maxlen=63)
                d.append(dv)
                self.dv63[s].append(dv)
            p = float(f.price)
            if p == p and p > 0:
                q = self.px.get(s)
                if q is None:
                    q = self.px[s] = deque(maxlen=64)
                q.append(p)
            v = s.value
            if v in TRACK and v not in self.track_sid:
                self.track_sid[v] = str(s.id)
                self.track[v] = {"ref": 0, "pool": 0, "A1000": 0, "B90": 0, "C20": 0, "months": 0,
                                 "first": None, "last": None}
        month = self.time.strftime("%Y-%m")
        if month != self.last_month and self.time.strftime("%Y-%m-%d") >= self.eval_from:
            self.last_month = month
            self._evaluate(fl)
        return []

    # ------------------------------------------------------------------ monthly
    def _evaluate(self, fl):
        day = self.time.strftime("%Y-%m-%d")
        year = day[:4]
        meta, ref, pool = {}, set(), []
        for f in fl:
            s = f.symbol
            fund = bool(f.has_fundamental_data)
            common = major = None
            mcap, exch, sector = 0.0, "", None
            if fund:
                sr = f.security_reference
                common = is_us_common(f)
                exch = str(sr.exchange_id)
                major = exch in EXCHANGES
                mcap = float(f.market_cap)
                try:
                    sector = int(f.asset_classification.morningstar_sector_code)
                except Exception:
                    sector = None
            price = float(f.price)
            d20, d63 = self.dv20.get(s), self.dv63.get(s)
            adv20 = _mean(d20) if d20 is not None and len(d20) == 20 else float("nan")
            if fund and common and major and mcap >= 2e9 and price >= 5 and adv20 >= 5e6:
                ref.add(s)
            in_pool = price >= 5 and adv20 >= 5e6 and d63 is not None and len(d63) == 63
            adv63 = _mean(d63) if in_pool else 0.0
            meta[s] = (fund, common, major, mcap, exch, sector, adv63, in_pool)
            if in_pool:
                pool.append((adv63, str(s.id), s))
        harness = set(self.qr_eligible)
        diff = len(ref ^ harness)
        self.chk["months"] += 1
        self.chk["sum_diff"] += diff
        self.chk["max_diff"] = max(self.chk["max_diff"], diff)

        pool.sort(key=lambda t: (-t[0], t[1]))                # deterministic: ADV desc, then SID
        corr_spy = self._etf_like([s for _, _, s in pool])
        corr_hi = {s for s, c in corr_spy.items() if c >= 0.90}
        excl = {
            "E0": pool,
            "E1": [t for t in pool if meta[t[2]][1] is not False],
        }
        excl["E2"] = [t for t in excl["E1"] if meta[t[2]][2] is not False]
        excl["E3"] = [t for t in excl["E1"] if meta[t[2]][0]]
        excl["E4"] = [t for t in excl["E1"] if t[2] not in corr_hi]
        twin = self._twin_max([s for _, _, s in pool], meta)
        for thr in TWIN:
            excl[f"E5_{int(thr * 100)}"] = [t for t in excl["E1"] if twin.get(t[2], 0.0) < thr]

        variants = {}
        for e, lst in excl.items():
            rules = self._rules(lst)
            for name, members in rules.items():
                if e in EXCL_ALL_RULES or name in PRIMARY:
                    variants[f"{e}-{name}"] = members
        for v, P in variants.items():
            tp = len(P & ref)
            fp, fn = len(P) - tp, len(ref) - tp
            f1 = 2 * tp / (2 * tp + fp + fn) if (tp + fp + fn) else 1.0
            a = self.acc.get((year, v))
            if a is None:
                a = self.acc[(year, v)] = [0, 0, 0, 0, 0, 0, 1.0, 0.0]
            a[0] += 1; a[1] += len(P); a[2] += len(ref); a[3] += tp; a[4] += fp; a[5] += fn
            a[6] = min(a[6], f1); a[7] = max(a[7], f1)

        if day[5:7] == "06":
            self._sample(day, variants, ref, meta, twin, corr_spy)
        for p in PRIMARY:
            self._characterise(year, p, variants[f"E1-{p}"], variants[f"E0-{p}"], ref, meta)
            key = (year, "E5_95-" + p)
            if key not in self.examples_done:
                self.examples_done.add(key)
                left = sorted((meta[s][6], s.value) for s in variants[f"E5_95-{p}"] - ref if not meta[s][0])[::-1][:25]
                self._qr_log(f"QRPX_X|{year}|E5_95-{p}|" + ",".join(t for _, t in left))
        self._sectors(year, ref, {p: variants[f"E1-{p}"] for p in PRIMARY}, meta)
        self._track(ref, pool, {p: variants[f"E1-{p}"] for p in PRIMARY})
        self._forward(day, ref, {p: variants[f"E1-{p}"] for p in PRIMARY})

    def _rules(self, lst):
        out = {}
        for n in A_N:
            out[f"A{n}"] = {s for _, _, s in lst[:n]}
        total = sum(a for a, _, _ in lst)
        for c in B_C:
            cut, run, members = total * c / 100.0, 0.0, set()
            for a, _, s in lst:
                if run >= cut:
                    break
                members.add(s)
                run += a
            out[f"B{c}"] = members
        for x in C_X:
            out[f"C{x}"] = {s for a, _, s in lst if a >= x * 1e6}
        return out

    def _etf_like(self, symbols):
        """63-day correlation of daily returns with SPY for each pool member (price-only)."""
        spy = self.px.get(self.spy)
        if spy is None or len(spy) < 64:
            return {}
        rs = np.diff(np.log(np.array(spy)))
        rows, syms = [], []
        for s in symbols:
            q = self.px.get(s)
            if q is not None and len(q) == 64:
                rows.append(q)
                syms.append(s)
        if not rows:
            return {}
        m = np.diff(np.log(np.array(rows, dtype=float)), axis=1)
        m = np.clip(m, -0.25, 0.25)                       # damp split-day jumps in raw prices
        m = m - m.mean(axis=1, keepdims=True)
        b = rs - rs.mean()
        den = np.sqrt((m * m).sum(axis=1) * (b * b).sum())
        with np.errstate(invalid="ignore", divide="ignore"):
            corr = (m @ b) / den
        return {s: float(c) for s, c in zip(syms, corr) if c == c}

    def _twin_max(self, symbols, meta):
        """For pool members WITHOUT fundamentals: the highest |correlation| of their 63-day daily
        returns with any other pool member. Index funds, leveraged/inverse and commodity ETFs have
        near-duplicates; individual companies almost never do. Uses past prices only."""
        rows, syms = [], []
        for s in symbols:
            q = self.px.get(s)
            if q is not None and len(q) == 64:
                rows.append(q)
                syms.append(s)
        if not rows:
            return {}
        m = np.diff(np.log(np.array(rows, dtype=float)), axis=1)
        m = np.clip(m, -0.25, 0.25)
        m = m - m.mean(axis=1, keepdims=True)
        sd = np.sqrt((m * m).sum(axis=1))
        ok = sd > 0
        z = np.zeros_like(m)
        z[ok] = m[ok] / sd[ok, None]
        nf = [i for i, s in enumerate(syms) if not meta[s][0] and ok[i]]
        if not nf:
            return {}
        c = np.abs(z[nf] @ z.T)
        for r, i in enumerate(nf):
            c[r, i] = 0.0
        best = c.max(axis=1)
        return {syms[i]: float(b) for i, b in zip(nf, best)}

    def _sample(self, day, variants, ref, meta, twin, corr_spy):
        """Deterministic sample (by SID order) of false positives WITHOUT fundamentals under the
        E5_95 primaries, for manual type classification in the report (evaluation only)."""
        fps = set()
        for p in PRIMARY:
            fps |= {s for s in variants[f"E5_95-{p}"] - ref if not meta[s][0]}
        ordered = sorted(fps, key=lambda s: str(s.id))
        step = max(1, len(ordered) // 60)
        pick = ordered[::step][:60]
        cells = [f"{s.value}:{str(s.id).split(' ')[1] if ' ' in str(s.id) else ''}:{meta[s][6] / 1e6:.0f}:"
                 f"{twin.get(s, 0):.2f}:{corr_spy.get(s, float('nan')):.2f}" for s in pick]
        self._qr_log(f"QRPX_SAMPLE|{day}|n={len(ordered)}|" + ";".join(cells))

    def _vol(self, s):
        q = self.px.get(s)
        if q is None or len(q) < 20:
            return None
        v = list(q)
        return _med([abs(v[i] / v[i - 1] - 1.0) for i in range(1, len(v))])

    def _characterise(self, year, p, P, P0, ref, meta):
        c = self.char.get((year, p))
        if c is None:
            c = self.char[(year, p)] = {
                "m": 0, "tp": 0, "fp": 0, "fn": 0, "fp_nofund": 0, "fp_nonmajor": 0, "fp_zerocap": 0,
                "fp_1_2b": 0, "fp_05_1b": 0, "fp_lt05b": 0, "fp_other": 0, "e0_extra_nontype": 0,
                "fn_notpool": 0, "fn_2_3b": 0, "fn_3_5b": 0, "fn_5_10b": 0, "fn_gt10b": 0,
                "turn_tp": [], "turn_fn": [], "turn_fpsmall": [], "vol_tp": [], "vol_fn": [], "vol_fp": [],
                "nas_tp": 0, "nas_fn": 0, "nas_fp": 0, "fund_fp": 0}
        c["m"] += 1
        tp, fp, fn = P & ref, P - ref, ref - P
        c["tp"] += len(tp); c["fp"] += len(fp); c["fn"] += len(fn)
        c["e0_extra_nontype"] += len(P0 - P)
        for s in fp:
            fund, common, major, mcap, exch, _, _, _ = meta[s]
            if not fund:
                c["fp_nofund"] += 1
                continue
            c["fund_fp"] += 1
            c["nas_fp"] += exch == "NAS"
            if not major:
                c["fp_nonmajor"] += 1
            elif mcap <= 0:
                c["fp_zerocap"] += 1
            elif mcap < 5e8:
                c["fp_lt05b"] += 1
            elif mcap < 1e9:
                c["fp_05_1b"] += 1
            elif mcap < 2e9:
                c["fp_1_2b"] += 1
            else:
                c["fp_other"] += 1
        for s in fn:
            fund, common, major, mcap, exch, _, adv63, in_pool = meta[s]
            c["nas_fn"] += exch == "NAS"
            if not in_pool:
                c["fn_notpool"] += 1
            if mcap < 3e9:
                c["fn_2_3b"] += 1
            elif mcap < 5e9:
                c["fn_3_5b"] += 1
            elif mcap < 1e10:
                c["fn_5_10b"] += 1
            else:
                c["fn_gt10b"] += 1
        for s in tp:
            c["nas_tp"] += meta[s][4] == "NAS"
        med = lambda xs: _med([x for x in xs if x is not None])
        turn = lambda s: meta[s][6] * 252 / meta[s][3] if meta[s][3] > 0 and meta[s][7] else None
        c["turn_tp"].append(med(turn(s) for s in tp))
        c["turn_fn"].append(med(turn(s) for s in fn))
        c["turn_fpsmall"].append(med(turn(s) for s in fp if meta[s][0] and 0 < meta[s][3] < 2e9))
        c["vol_tp"].append(med(self._vol(s) for s in tp))
        c["vol_fn"].append(med(self._vol(s) for s in fn))
        c["vol_fp"].append(med(self._vol(s) for s in fp))
        key = (year, p)
        if key not in self.examples_done:
            self.examples_done.add(key)
            nf = sorted((meta[s][6], s.value) for s in fp if not meta[s][0])[::-1][:15]
            self._qr_log(f"QRPX_X|{year}|{p}|" + ",".join(t for _, t in nf))

    def _sectors(self, year, ref, primaries, meta):
        d = self.sector.setdefault(year, {})
        for name, S in [("R", ref)] + list(primaries.items()):
            cnt = d.setdefault(name, {})
            for s in S:
                sec = meta[s][5]
                k = str(sec) if sec is not None else "none"
                cnt[k] = cnt.get(k, 0) + 1

    def _track(self, ref, pool, primaries):
        sids = {sid: t for t, sid in self.track_sid.items()}
        pool_set = {s for _, _, s in pool}
        seen = {}
        for s in pool_set | ref:
            t = sids.get(str(s.id))
            if t:
                seen[t] = s
        day = self.time.strftime("%Y-%m-%d")
        for t, s in seen.items():
            r = self.track[t]
            r["months"] += 1
            r["first"] = r["first"] or day
            r["last"] = day
            r["ref"] += s in ref
            r["pool"] += s in pool_set
            for p, P in primaries.items():
                r[p] += s in P

    def _forward(self, day, ref, primaries):
        now = self.time
        if self.prev is not None:
            t0, groups = self.prev
            allsyms = sorted({s for g in groups.values() for s in g}, key=lambda s: str(s.id))
            rets = {}
            if allsyms:
                h = self.history(allsyms, t0, now, Resolution.DAILY)
                if h is not None and not h.empty:
                    for sym, df in h["close"].groupby(level=0):
                        v = df.values
                        if len(v) >= 2 and v[0] > 0:
                            rets[sym] = float(v[-1] / v[0] - 1.0)
            out = {}
            for g, members in groups.items():
                rs = [rets[s] for s in members if s in rets]
                out[g] = [round(sum(rs) / len(rs), 6) if rs else None, len(rs), len(members)]
            self._qr_log(f"QRPX_F|{t0:%Y-%m-%d}|" + json.dumps(out, sort_keys=True, separators=(",", ":")))
            self.prev = None
        if self.fwd_until and day <= self.fwd_until:
            groups = {"R": list(ref)}
            for p, P in primaries.items():
                groups[f"{p}_P"] = list(P)
                groups[f"{p}_PnotR"] = list(P - ref)
                groups[f"{p}_RnotP"] = list(ref - P)
            self.prev = (now, groups)

    # ------------------------------------------------------------------ end
    def qr_on_end(self):
        for (year, v), a in sorted(self.acc.items()):
            self._qr_log(f"QRPX_Y|{year}|{v}|{a[0]}|{a[1]}|{a[2]}|{a[3]}|{a[4]}|{a[5]}|{a[6]:.4f}|{a[7]:.4f}")
        for (year, p), c in sorted(self.char.items()):
            out = {}
            for k, v in c.items():
                if isinstance(v, list):
                    xs = [x for x in v if x is not None]
                    out[k] = round(sum(xs) / len(xs), 5) if xs else None
                else:
                    out[k] = v
            self._qr_log(f"QRPX_C|{year}|{p}|" + json.dumps(out, sort_keys=True, separators=(",", ":")))
        for year, d in sorted(self.sector.items()):
            self._qr_log(f"QRPX_S|{year}|" + json.dumps(d, sort_keys=True, separators=(",", ":")))
        self.log("QRPX_T|" + json.dumps(self.track, sort_keys=True, separators=(",", ":")))
        self.log("QRPX_CHK|" + json.dumps(self.chk, sort_keys=True))
