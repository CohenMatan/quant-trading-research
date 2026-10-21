# X807 v1.0 — H032 / OS-1 revised canary C-OS1 (owner D278; research/os/H032_spec.md, frozen and SHA-256-pinned in
# qresearch.os1 with this host, qr_os1, qr_ucr and the two public SEC objects). Infrastructure only: NO orders, NO
# returns, NO subscriptions besides the harness's SPY clock. QuantConnect's DEFAULT build (recorded). Plain-text
# source, no compression or encoding.
# Reference data: two public SEC JSON objects in the Object Store (D257 / D278 item 6), each checked against its pinned
# SHA-256:
#   rr/ucr_sec_v1.json — the UCR-1 per-filing object (identity, cover counts, floats; the frozen UCR-1 repair);
#   rr/os1_sec_v1.json — the H032 extension (SIC per periodic filing; original 10-K / 10-KT OCF, revenue and the
#                        same-filing prior-year revenue comparative).
# Each selection day: every Fundamental object's appearance (last seen), ADV20, split factor and adjusted close; the
# SPY total-return close from the harness clock. Each month-end session 2010-01 .. 2021-11: the UCR-1 repaired
# universe (vendor E + repaired); point-in-time identity, SIC, split-adjusted net share issuance and the fiscal-year
# filters for every eligible security; coverage counts (repaired / vendor / restored; later-disappearing names at the
# end); the mechanical start (first review with joint coverage >= 70%); from the start, the H032 books by NAME only
# (B1, B0, B2 x5, random x5, beta-matched x5, momentum 12-1, vendor-universe B1) and their in-run recomputation.
# Aggregates only, published as plain JSON lines 'OS1|<section>|<json>'.
from AlgorithmImports import *
from bisect import bisect_left
from collections import deque
from datetime import date
import hashlib
import json
import time
import numpy as np
import qr_os1 as O
import qr_ucr as R
from qr_harness import COMMON_STOCK, EXCHANGES, QRAlgorithm, is_us_common, non_common_reason

ADV_DAYS = 20
MIN_PRICE, MIN_ADV = 5.0, 5e6
FIRST_POINT = (2010, 1)
LAST_POINT = (2021, 11)
RING = O.BETA_DAYS + 1
NSI_PAIR = (None, "split_unknown", "bound", "bound_split")
NSI_KNOWN = (None, "bound", "bound_split")


def _q(xs):
    if not xs:
        return None
    a = np.sort(np.array(xs, float))
    return [round(float(np.quantile(a, p)), 6) for p in (0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99)]


class OS1Canary(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 1000
        if self.qr["start"] != "2009-05-01" or self.qr["end"] != "2021-12-31" or self.qr.get("warmup_start"):
            raise Exception("X807: C-OS1 runs 2009-05-01 .. 2021-12-31 without warm-up")
        u = self._qr_u
        if u.get("sec_corrections") or (float(u.get("min_market_cap", 0)), float(u.get("min_price", 0)),
                                        float(u.get("min_avg_dollar_volume", 0)), int(u.get("adv_days", 0))) != \
                (R.MIN_CAP, MIN_PRICE, MIN_ADV, ADV_DAYS):
            raise Exception("X807: the approved universe filters without the SEC layer")
        p = self.qr["params"]
        docs = {}
        for name in ("ucr", "os1"):
            key, want = p[name + "_object_key"], p[name + "_reference_sha256"]
            if not self.object_store.contains_key(key):
                raise Exception(f"X807: the {name} SEC object is not in the Object Store")
            text = self.object_store.read(key)
            got = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if got != want:
                raise Exception(f"X807: {name} SEC object digest {got[:12]} differs from the pinned {want[:12]}")
            docs[name] = (got, json.loads(text))
            text = None
        self.sha = {k: v[0] for k, v in docs.items()}
        self.ref = R.RepairRef(docs["ucr"][1])
        self.ext = O.Ext(docs["os1"][1], self.ref)
        self.rep = R.Repair(self.ref)
        docs = None
        self.splits = O.Splits()
        self.dv, self.sf, self.sf_change, self.last_seen = {}, {}, {}, {}
        self.row = {}                                    # key -> row of the price matrices
        self.px = np.full((4096, RING), np.nan)          # daily adjusted closes, ring by session counter
        self.mpx = np.full((4096, 150), np.nan, dtype=np.float32)   # adjusted close at each review
        self.spy_px = np.full(RING, np.nan)
        self.spy_tr, self.spy_last = 1.0, None
        self.sess_n, self.ring_sess = -1, -1
        self.prev_session = None
        self.done_t = None
        self.k = -1
        self.start_k = None
        self.reviews = []                                # per-review counts
        self.years = {}                                  # per-year reason / split / sector counters and samples
        self.cov_rows = []                               # (k, key id, covered, restored) of denominator rows
        self.ids = {}
        self.books = {}
        self.inputs = []                                 # per-review book inputs for the in-run recomputation
        self.checks = dict(identity_duplicates=0, repaired_without_identity=0, repaired_rows=0,
                           nsi_filing_on_or_after_t=0, annual_filing_on_or_after_t=0)
        self.t0 = time.perf_counter()

    # ---------------------------------------------------------------- daily
    def on_data(self, data):
        super().on_data(data)
        if data.bars.count > 0 and self.time.hour >= 9:
            d = self.time.date()
            if d != self.prev_session and data.bars.contains_key(self.spy) \
                    and not data.bars[self.spy].is_fill_forward:
                c = float(data.bars[self.spy].close)
                div = float(data.dividends[self.spy].distribution) if data.dividends.contains_key(self.spy) else 0.0
                if self.spy_last is not None and self.spy_last > 0:
                    self.spy_tr *= (c + div) / self.spy_last
                self.spy_last = c
                self.prev_session = d
                self.sess_n += 1
                self.spy_px[self.sess_n % RING] = self.spy_tr

    def _row(self, key):
        r = self.row.get(key)
        if r is None:
            r = self.row[key] = len(self.row)
            if r >= self.px.shape[0]:
                n = self.px.shape[0]
                self.px = np.vstack([self.px, np.full((n, RING), np.nan)])
                self.mpx = np.vstack([self.mpx, np.full((n, self.mpx.shape[1]), np.nan, dtype=np.float32)])
        return r

    def _category(self, f, px, adv):
        """Point-in-time category: E / A_lt / M / X / B_blank / B_explicit / N / I (as X806)."""
        if adv is None or not (px >= MIN_PRICE and adv >= MIN_ADV):
            return "I"
        if not f.has_fundamental_data:
            return "N"
        try:
            sr = f.security_reference
            exch = str(sr.exchange_id or "").strip()
            st = str(sr.security_type or "").strip()
            dep = bool(sr.is_depositary_receipt)
            common = is_us_common(f, None)
            ncr = non_common_reason(f, None)
        except Exception:
            self.checks["struct_errors"] = self.checks.get("struct_errors", 0) + 1
            return "B_explicit"
        if common and exch:
            if exch not in EXCHANGES:
                return "X"
            try:
                mc = float(f.market_cap)
            except Exception:
                mc = 0.0
            if not mc > 0:
                return "M"
            return "E" if mc >= R.MIN_CAP else "A_lt"
        blank = (not st or not exch) and not dep and st in ("", COMMON_STOCK) and ncr is None \
            and (not exch or exch in EXCHANGES)
        return "B_blank" if blank else "B_explicit"

    def _qr_select(self, fundamental):
        today = self.time.date()
        o = today.toordinal()
        t = self.prev_session
        if t is None:
            return []
        so = t.toordinal() + 1                           # split-factor stamp: the day after the session it reflects
        if self.ring_sess != self.sess_n:
            self.px[:, self.sess_n % RING] = np.nan
            self.ring_sess = self.sess_n
        col = self.sess_n % RING
        audit = False
        if t != self.done_t and FIRST_POINT <= (t.year, t.month) <= LAST_POINT:
            nxt = self.securities[self.spy].exchange.hours.get_next_market_open(self.time, False).date()
            audit = nxt.month != t.month or nxt.year != t.year
        rows, rrows, advs = [], [], []
        for f in fundamental:
            key = str(f.symbol.id)
            self.last_seen[key] = o
            dq = self.dv.get(key)
            if dq is None:
                dq = self.dv[key] = deque(maxlen=ADV_DAYS)
            dv = float(f.dollar_volume)
            if dv == dv:
                dq.append(dv)
            try:
                sf = float(f.split_factor)
            except Exception:
                sf = float("nan")
            if sf == sf and sf > 0:
                last = self.sf.get(key)
                if last is not None and abs(sf / last - 1) > 1e-9:
                    self.sf_change[key] = o
                self.sf[key] = sf
                self.splits.observe(key, so, sf)
            try:
                ap = float(f.adjusted_price)
            except Exception:
                ap = float("nan")
            if ap == ap and ap > 0:
                r = self._row(key)                   # may grow (replace) self.px: index only after the call
                self.px[r, col] = ap
            if not audit:
                continue
            px = float(f.price)
            adv = sum(dq) / ADV_DAYS if len(dq) == ADV_DAYS else None
            cat = self._category(f, px, adv)
            try:
                mc = float(f.market_cap) if f.has_fundamental_data else 0.0
            except Exception:
                mc = 0.0
            tick = f.symbol.value
            rows.append((key, tick, cat))
            rrows.append((key, tick, cat, px, mc if mc > 0 else 0.0, self.sf_change.get(key), sf == sf and sf > 0))
            advs.append(adv or 0.0)
        if audit:
            self.done_t = t
            self._review(t, rows, rrows, advs)
        return []

    def qr_select_universe(self, eligible):
        return []

    # ---------------------------------------------------------------- monthly review
    def _yr(self, y):
        d = self.years.get(y)
        if d is None:
            d = self.years[y] = dict(nsi_reason={}, ocf_reason={}, rev_reason={}, ff12_den={}, ff12_pass={},
                                     ff12_b1={}, ff12_fin_removed={}, os=[], growth=[],
                                     identity_why={}, b1_entries=0)
        return d

    @staticmethod
    def _inc(d, k, n=1):
        d[k] = d.get(k, 0) + n

    def _review(self, t, rows, rrows, advs):
        self.k += 1
        k = self.k
        to = t.toordinal()
        y = t.year
        Y = self._yr(y)
        fixed = self.rep.repair(y, to, rrows)
        self.checks["repaired_rows"] += len(fixed)
        idmap, why = O.identity(self.ref, to, [(r[0], r[1]) for r in rows])
        for w, n in why.items():
            self._inc(Y["identity_why"], w, n)
        if len(set(idmap.values())) != len(idmap):
            self.checks["identity_duplicates"] += 1
        self.checks["repaired_without_identity"] += sum(1 for j in fixed if j not in idmap)
        ext, ref = self.ext, self.ref
        v0 = ext.pit_violations
        c = dict(t=t.isoformat(), elig=0, vendor=0, restored=0, fin=0, fin_unknown=0, den=0, cov=0, passed=0,
                 nsi=0, ocf_in=0, rev_in=0, ident=0, den_vendor=0, cov_vendor=0, den_restored=0, cov_restored=0,
                 vden=0, vcov=0, vpass=0, sp_pairs=0, sp_known=0, sp_unknown=0, sp_bound=0, sp_bound_split=0,
                 sp_adjusted=0, sp_adjusted_in_bound=0)
        s_b1, s_vb1, s_b0, cov_pool, sic_of, adv_of = {}, {}, {}, [], {}, {}
        for j, (key, tick, cat) in enumerate(rows):
            restored = j in fixed
            if not (cat == "E" or restored):
                continue
            i = idmap.get(j)
            c["elig"] += 1
            c["vendor" if cat == "E" else "restored"] += 1
            c["ident"] += int(i is not None)
            sic, fin, os_, nr, adj, ocf, g, ro, rr, covered, passed = O.classify(ref, ext, self.splits, to, key, i)
            if i is not None:
                q = bisect_left(ref.s_day[i], to) - 1
                if q >= 0 and ref.s_day[i][q] >= to:
                    self.checks["nsi_filing_on_or_after_t"] += 1
            adv = advs[j]
            if os_ is not None:
                s_b0[key] = (os_, adv)
            if fin is True:
                c["fin"] += 1
                self._inc(Y["ff12_fin_removed"], O.ff12(sic))
                continue
            c["fin_unknown"] += int(fin is None)
            c["den"] += 1
            g_ = "vendor" if cat == "E" else "restored"
            c["den_" + g_] += 1
            c["cov_" + g_] += int(covered)
            c["cov"] += int(covered)
            c["passed"] += int(passed)
            c["nsi"] += int(os_ is not None)
            c["ocf_in"] += int(fin is False and ocf is not None)
            c["rev_in"] += int(fin is False and g is not None)
            if cat == "E":
                c["vden"] += 1
                c["vcov"] += int(covered)
                c["vpass"] += int(passed)
            self._inc(Y["nsi_reason"], str(nr))
            self._inc(Y["ocf_reason"], str(ro))
            self._inc(Y["rev_reason"], str(rr))
            if nr in NSI_PAIR:
                c["sp_pairs"] += 1
                if nr in NSI_KNOWN:
                    c["sp_known"] += 1
                    c["sp_bound"] += int(nr == "bound")
                    c["sp_bound_split"] += int(nr == "bound_split")
                    c["sp_adjusted"] += int(adj)
                    c["sp_adjusted_in_bound"] += int(adj and nr is None)
                else:
                    c["sp_unknown"] += 1
            self._inc(Y["ff12_den"], O.ff12(sic))
            sic_of[key] = sic
            kid = self.ids.setdefault(key, len(self.ids))
            self.cov_rows.append((k, kid, int(covered), int(restored)))
            if covered:
                cov_pool.append(key)
                adv_of[key] = adv
                Y["os"].append(os_)
                Y["growth"].append(g)
            if passed:
                self._inc(Y["ff12_pass"], O.ff12(sic))
                s_b1[key] = (os_, adv)
                if cat == "E":
                    s_vb1[key] = (os_, adv)
        if ext.pit_violations != v0:
            self.checks["annual_filing_on_or_after_t"] += ext.pit_violations - v0
        # review-day adjusted closes for 12-1 momentum
        rcol = self.px[:, self.sess_n % RING]
        if k < self.mpx.shape[1]:
            self.mpx[:len(self.row), k] = rcol[:len(self.row)].astype(np.float32)
        cov_frac = c["cov"] / c["den"] if c["den"] else None
        if self.start_k is None and cov_frac is not None and cov_frac >= O.COV_START:
            self.start_k = k
        c["started"] = self.start_k is not None
        if self.start_k is not None:
            self._books(k, s_b1, s_vb1, s_b0, cov_pool, adv_of, c, Y, sic_of)
        self.reviews.append(c)

    # ---------------------------------------------------------------- books by name (no prices, no returns)
    def _betas(self, keys):
        n = self.sess_n
        order = [(n - RING + 1 + j) % RING for j in range(RING)]
        valid = [n - RING + 1 + j >= 0 for j in range(RING)]
        m = self.spy_px[order].copy()
        m[~np.array(valid)] = np.nan
        rows = [self.row.get(x) for x in keys]
        P = np.full((len(keys), RING), np.nan)
        idx = [a for a, r in enumerate(rows) if r is not None]
        if idx:
            P[idx] = self.px[[rows[a] for a in idx]][:, order]
        P[:, ~np.array(valid)] = np.nan
        b = O.betas(P, m)
        return {x: float(b[a]) for a, x in enumerate(keys) if b[a] == b[a]}

    def _books(self, k, s_b1, s_vb1, s_b0, cov_pool, adv_of, c, Y, sic_of):
        B = self.books
        if not B:
            B.update({name: dict(held=[], seq=[], size=[]) for name in
                      ["B1", "VB1", "B0", "MOM"] + [f"B2_{s}" for s in O.SEEDS_B2] +
                      [f"RND_{s}" for s in O.SEEDS_RND] + [f"BETA_{s}" for s in O.SEEDS_BETA]})
            for s in O.SEEDS_BETA:
                B[f"BETA_{s}"]["pairs"] = {}
            B["BETA_att"], B["BETA_mat"] = 0, 0
        prev = B["B1"]["held"]
        b1 = O.plan(s_b1, prev)
        n_new = len(set(b1) - set(prev))
        Y["b1_entries"] += n_new
        mom = {}
        if k >= O.MOM_BACK:
            for key in cov_pool:
                r = self.row.get(key)
                if r is None:
                    continue
                v = O.momentum(float(self.mpx[r, k - O.MOM_BACK]), float(self.mpx[r, k - O.MOM_SKIP]))
                if v is not None:
                    mom[key] = (v, adv_of.get(key, 0.0))
        bet = self._betas(sorted(cov_pool))
        quint = O.quintiles(bet)
        self.inputs.append((k, s_b1, s_vb1, s_b0, mom, sorted(s_b1), sorted(cov_pool), quint, n_new))
        new = dict(B1=b1, VB1=O.plan(s_vb1, B["VB1"]["held"]), B0=O.plan(s_b0, B["B0"]["held"]),
                   MOM=O.plan(mom, B["MOM"]["held"]) if mom else [])
        for s in O.SEEDS_B2:
            new[f"B2_{s}"] = O.random_step(list(s_b1), B[f"B2_{s}"]["held"], n_new, s, k)
        for s in O.SEEDS_RND:
            new[f"RND_{s}"] = O.random_step(cov_pool, B[f"RND_{s}"]["held"], n_new, s, k)
        for s in O.SEEDS_BETA:
            pairs, att, mat = O.beta_step(B[f"BETA_{s}"]["pairs"], b1, quint, s, k)
            B[f"BETA_{s}"]["pairs"] = pairs
            B["BETA_att"] += att
            B["BETA_mat"] += mat
            new[f"BETA_{s}"] = sorted(pairs.values())
        for name, h in new.items():
            B[name]["held"] = h
            B[name]["seq"].append((k, h))
            B[name]["size"].append(len(h))
        for key in b1:
            self._inc(Y["ff12_b1"], O.ff12(sic_of.get(key)))
        c.update(b1_new=n_new, pool_b1=len(s_b1), pool_vb1=len(s_vb1), pool_b0=len(s_b0), pool_cov=len(cov_pool),
                 pool_mom=len(mom), beta_n=len(bet), sizes={n: len(h) for n, h in new.items()})

    def _recompute(self):
        """Re-run every book from the stored inputs; digests must equal the online sequences."""
        held = {n: [] for n in self.books if isinstance(self.books[n], dict)}
        pairs = {s: {} for s in O.SEEDS_BETA}
        seq = {n: [] for n in held}
        for k, s_b1, s_vb1, s_b0, mom, pool_b2, pool_cov, quint, n_new in self.inputs:
            prev = held["B1"]
            b1 = O.plan(s_b1, prev)
            if len(set(b1) - set(prev)) != n_new:
                return False
            new = dict(B1=b1, VB1=O.plan(s_vb1, held["VB1"]), B0=O.plan(s_b0, held["B0"]),
                       MOM=O.plan(mom, held["MOM"]) if mom else [])
            for s in O.SEEDS_B2:
                new[f"B2_{s}"] = O.random_step(pool_b2, held[f"B2_{s}"], n_new, s, k)
            for s in O.SEEDS_RND:
                new[f"RND_{s}"] = O.random_step(pool_cov, held[f"RND_{s}"], n_new, s, k)
            for s in O.SEEDS_BETA:
                pairs[s] = O.beta_step(pairs[s], b1, quint, s, k)[0]
                new[f"BETA_{s}"] = sorted(pairs[s].values())
            for n, h in new.items():
                held[n] = h
                seq[n].append((k, h))
        return {n: O.digest(seq[n]) for n in seq}

    # ---------------------------------------------------------------- end
    def _gcov2(self):
        """Coverage of names that leave the stream within 24 months of the review vs the rest, per review; reviews
        whose horizon passes the last stream day (2021-12-31: the Holdout is never read) are censored."""
        final = max(self.last_seen.values())
        inv = {v: key for key, v in self.ids.items()}
        T = [O.ordinal(c["t"]) for c in self.reviews]
        hz = [O.add_months(x, O.EXIT_MONTHS) for x in T]
        out = [dict(assessable=hz[k] <= final, exit_den=0, exit_cov=0, stay_den=0, stay_cov=0,
                    exit_restored_den=0, exit_restored_cov=0) for k in range(len(T))]
        for k, kid, cov, rest in self.cov_rows:
            r = out[k]
            if not r["assessable"]:
                continue
            ex = self.last_seen[inv[kid]] < hz[k]
            g = "exit" if ex else "stay"
            r[g + "_den"] += 1
            r[g + "_cov"] += cov
            if ex and rest:
                r["exit_restored_den"] += 1
                r["exit_restored_cov"] += cov
        return out, final

    def qr_on_end(self):
        t1 = time.perf_counter()
        g2, final = self._gcov2()
        online = {n: O.digest(b["seq"]) for n, b in self.books.items() if isinstance(b, dict)}
        again = self._recompute() if self.books else {}
        b1_years = {}
        for k, h in self.books.get("B1", {}).get("seq", []):
            y = self.reviews[k]["t"][:4]
            b1_years.setdefault(y, set()).update(h)
        meta = dict(protocol="H032 C-OS1", ucr_reference_sha256=self.sha["ucr"], os1_reference_sha256=self.sha["os1"],
                    reviews=len(self.reviews), start_index=self.start_k,
                    start=self.reviews[self.start_k]["t"] if self.start_k is not None else None,
                    final_stream_day=date.fromordinal(final).isoformat() if self.last_seen else None,
                    checks=dict(self.checks, pit_violations_ext=self.ext.pit_violations),
                    beta_attempted=self.books.get("BETA_att", 0), beta_matched=self.books.get("BETA_mat", 0),
                    digests_online=online, digests_recomputed=again,
                    determinism=bool(again) and again == online,
                    b1_distinct_names_by_year={y: len(s) for y, s in sorted(b1_years.items())},
                    collect_s=round(t1 - self.t0, 1), summarize_s=round(time.perf_counter() - t1, 1),
                    experiment_id=self.qr.get("experiment_id"))
        dump = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"))
        self._qr_log("OS1|meta|" + dump(meta))
        for k, c in enumerate(self.reviews):
            c["gcov2"] = g2[k]
        for y in sorted(self.years):
            Y = dict(self.years[y])
            Y["os_q"], Y["growth_q"] = _q(Y.pop("os")), _q(Y.pop("growth"))
            Y["reviews"] = [c for c in self.reviews if c["t"][:4] == str(y)]
            self._qr_log(f"OS1|year|{y}|" + dump(Y))
