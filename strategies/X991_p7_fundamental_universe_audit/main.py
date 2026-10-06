# X991 v1.1 (after E991-01): the year-over-year ledger is keyed by the SELECTION month (one snapshot per calendar
# month; E991-01 keyed it by the month of t, which shifts at weekend / holiday month boundaries and under-counted
# year-over-year availability), and the snapshot publishes the average cross-sectional Spearman correlation matrix of
# candidate fundamental inputs (feature-feature information overlap only; no return).
# X991 — Phase 7 (P7-CP1, D165) FUNDAMENTAL / UNIVERSE / SECTOR / ALIGNMENT DATA AUDIT (infrastructure; NO orders,
# NO returns, NO ranking, NO score). 2010-01-04 .. 2017-12-31 with the history-only warm-up from 2008-07-01; the frozen
# data-v1 universe (>= $2B, >= $5, ADV20 >= $5M, NYSE/Nasdaq, SEC correction layer). Built on the frozen X976 v1.3
# observation step (qr_fundamentals.observe_vendor): EVERY company with vendor fundamentals is observed daily; SEC-
# repaired securities are fed from the SEC table. Nothing after 2017-12-31 is requested.
# Monthly snapshot = the first universe selection of each month (data through the previous month-end close t);
# t = 2010-01-29 .. 2017-11-30 (95 month-ends). Per eligible security: point-in-time fundamental availability (approved
# fields, True TTM, snapshots), ages, field combinations, year-over-year availability (growth / deterioration),
# financial / REIT category and the SEC SIC (FF12), size tercile, listing age, later exit (characterisation only),
# Morningstar sector-code stability (current-status test), market-cap staleness, duplicate share classes, ticker
# changes, filing-date anomalies, and a deterministic sample of cross-domain snapshots (dates only).
# Outputs: counts, ages, dates and identifiers only (no vendor value is exported).
from AlgorithmImports import *
import json
from datetime import date, timedelta
from qr_harness import QRAlgorithm, _attr
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, TTM_BASES, financial_format, observe_vendor
from qr_industry import classify, excluded
import qr_p7 as P
import qr_xs_diag as XD
import numpy as np

COUNT_FROM = date(2010, 2, 1)       # first snapshot: data through the 2010-01-29 close
APPROVED_TTM = ("revenue", "gross_profit", "net_income", "operating_cash_flow")
SAMPLE_PER_MONTH = 3
SALT = "P7CP1-alignment"


def get(obj, path):
    for p in path.split("."):
        obj = getattr(obj, p)
    return obj


def add(h, k, n=1):
    h[k] = h.get(k, 0) + n


class P7FundamentalAudit(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        if self.qr_sec is None or self.qr_sic is None:
            raise Exception("X991 needs universe.sec_corrections (frozen data infrastructure v1)")
        if self.qr["end"] > "2017-12-31":
            raise Exception("X991: P7-CP1 audits end on or before 2017-12-31")
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS, holds=self.qr_timing_holds, releases=self.qr_quarantine_releases,
                              blocked=self.qr_restatement_blocks, field_releases=self.qr_field_releases)
        self.c = {k: 0 for k in ("C1_sec_visible_before_filing", "C3_quarantine_exposed", "C3_restatement_block_exposed",
                                 "C3_hold_violated", "C10_ttm_before_component_available",
                                 "C11_ttm_uses_blocked_component", "C12_partial_record_is_current",
                                 "A_alignment_violations", "F_file_date_after_first_seen", "F_file_before_period_end",
                                 "F_reports_observed", "stock_months")}
        self.y = {}                      # year -> counters
        self.seen_q, self.q_keys = set(), set()
        self.month = None
        self.first_seen, self.last_seen = {}, {}       # sid -> first / last day present in the fundamental feed
        self.tickers = {}                # sid -> set of tickers seen
        self.msec = {}                   # sid -> set of Morningstar sector codes seen (current-status test)
        self.prev_sic = {}               # sid -> last FF12 / SIC seen at a snapshot
        self.prev_mc = {}                # sid -> (implied shares, market cap, price) at the previous snapshot
        self.ttm_ledger = {}             # sid -> {selection ym: {base: True TTM value at that snapshot}} (in-host only)
        self.corr_sum, self.corr_n = None, 0
        self.miss = []                   # (y, ym, sid, missing core?, tercile, ff12, listing-age bucket, group)
        self.prev_session = None
        self.prev_elig = None            # previous snapshot's eligible set (universe dynamics)

    def on_data(self, data):
        super().on_data(data)
        if data.bars.count > 0 and self.time.hour >= 9:      # a real session (not a midnight corporate-action slice)
            self.prev_session = self.time.date()

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        out = super()._qr_select(fl)
        today = self.time.date()
        elig = set(self.qr_eligible)
        corr_sids = {str(s.id) for s in self.qr_corrected}
        by = {}
        for f in fl:
            sid = str(f.symbol.id)
            self.first_seen.setdefault(sid, today)
            self.last_seen[sid] = today
            if f.symbol in elig:
                by[sid] = f
            if sid in corr_sids or not f.has_fundamental_data:
                continue
            obs = observe_vendor(self.store, sid, f, today, get, self.seen_q)
            if obs is None:
                continue
            pe, fd, q = obs
            self.c["F_reports_observed"] += 1
            if fd is not None and fd > today:
                self.c["F_file_date_after_first_seen"] += 1     # vendor shows a report before its filing date
            if pe is not None and fd is not None and fd < pe:
                self.c["F_file_before_period_end"] += 1
            if q:
                self.q_keys.add((sid, pe, fd))
        for sid, f in by.items():
            if sid in corr_sids:
                self.qr_sec.feed(sid, today, self.store)
        monthly = (today.year, today.month) != self.month
        self.month = (today.year, today.month)
        if monthly and today >= COUNT_FROM:
            self._snapshot(fl, by, corr_sids, today)
        return out

    def qr_select_universe(self, eligible):
        return []

    # ------------------------------------------------------------------------------------------------ snapshot
    def _snapshot(self, fl, by, corr, today):
        t = self.prev_session or (today - timedelta(days=1))   # the month-end session whose close the data reflects
        y = str(t.year)
        ym = today.year * 100 + today.month        # v1.1: the selection month (exactly one snapshot per month)
        Y = self.y.setdefault(y, {})
        rows_f = []                                 # candidate fundamental inputs for the overlap matrix
        caps = {str(s.id): v[0] for s, v in self.qr_eligible_info.items()}
        order = sorted(caps, key=lambda k: (caps[k], k))
        terc = {k: ("T1" if i < len(order) / 3 else "T2" if i < 2 * len(order) / 3 else "T3") for i, k in enumerate(order)}
        add(Y, "snapshots")
        comp = {}                       # company id -> eligible share classes (duplicate-company check)
        ages = Y.setdefault("_ages", {})
        sample = set(P.pick(sorted(by), SAMPLE_PER_MONTH, f"{SALT}|{t}"))
        for sid, f in by.items():
            self.c["stock_months"] += 1
            grp = "corrected" if sid in corr else "native"
            add(Y, f"eligible_{grp}")
            self.tickers.setdefault(sid, set()).add(f.symbol.value)
            try:
                cid = str(f.company_reference.company_id)
                comp.setdefault(cid, []).append(sid)
            except Exception:
                pass
            try:
                ms = int(f.asset_classification.morningstar_sector_code)
                self.msec.setdefault(sid, set()).add(ms)
            except Exception:
                pass
            # ---- market cap (point-in-time vendor field / SEC reconstruction) staleness checks
            mc = caps.get(sid)
            px = float(f.price or 0)
            if mc and px > 0:
                sh = mc / px
                pm = self.prev_mc.get(sid)
                if pm is not None:
                    add(Y, "mcap_pairs")
                    if pm[1] == mc and pm[2] != px:
                        add(Y, "mcap_unchanged_price_changed")
                    if abs(sh / pm[0] - 1) > 0.25:
                        add(Y, "implied_shares_jump_gt25pct")
                self.prev_mc[sid] = (sh, mc, px)
            # ---- fundamentals point in time
            r = self.store.record(sid, today)
            if r is not None:
                if r.file_date >= today or r.available > today:
                    self.c["C1_sec_visible_before_filing"] += 1
                if (sid, r.period_end, r.file_date) in self.q_keys and grp == "native":
                    self.c["C3_quarantine_exposed"] += 1
                if (str(r.period_end), str(r.file_date)) in self.store.blocked.get(sid, ()):
                    self.c["C3_restatement_block_exposed"] += 1
                hold = self.store.holds.get(sid, {}).get(str(r.period_end))
                if hold is not None and str(today) < hold:
                    self.c["C3_hold_violated"] += 1
                if r.partial:
                    self.c["C12_partial_record_is_current"] += 1
                ages.setdefault("record_age_period_end", []).append((t - r.period_end).days)
                ages.setdefault("record_age_since_available", []).append((t - r.available).days + 1)
            have = set()
            ttm_new = None
            vals = {}
            for b in APPROVED_TTM:
                v, det = self.store.ttm_detail(sid, b, today)
                if v is None:
                    add(Y, f"ttm_missing|{b}|{det}")
                    continue
                vals[b] = v
                have.add(b + "_ttm4q")
                if any(fd >= str(today) for fd in det["filed"]):
                    self.c["C10_ttm_before_component_available"] += 1
                for pe, fd in zip(det["quarters"], det["filed"]):
                    if (pe, fd) in self.store.blocked.get(sid, ()):
                        self.c["C11_ttm_uses_blocked_component"] += 1
                    elif (sid, date.fromisoformat(pe), date.fromisoformat(fd)) in self.q_keys:
                        if b + "_q" not in self.store.field_releases.get(sid, {}).get((pe, fd), ()):
                            self.c["C11_ttm_uses_blocked_component"] += 1
                if b == "net_income":
                    ttm_new = det
                    ages.setdefault("ttm_newest_quarter_age", []).append((t - date.fromisoformat(det["quarters"][-1])).days)
                    ages.setdefault("ttm_newest_filing_age", []).append((t - date.fromisoformat(det["filed"][-1])).days)
            ta = r.values.get("total_assets") if r is not None else None
            eq = r.values.get("stockholders_equity") if r is not None else None
            if ta is not None and ta > 0:
                have.add("total_assets")
            if eq is not None:
                have.add("stockholders_equity")
            # ---- category / sector (SEC SIC at filing; filing-structure fallback)
            ff = financial_format(r.values) if r is not None else None
            sic = self.qr_sic.sic_on(sid, today)
            cat, src = classify(sic, ff)
            ff12 = XD.ff12(sic)
            add(Y, f"cat|{cat}")
            add(Y, f"catsrc|{src}")
            add(Y, f"ff12|{ff12}")
            ps = self.prev_sic.get(sid)
            if ps is not None and sic is not None and ps != sic:
                add(Y, "sic_changes")
                if (ps == 6798) != (sic == 6798):
                    add(Y, "sic_changes_reit_boundary")
                if XD.ff12(ps) != ff12:
                    add(Y, "ff12_changes")
            if sic is not None:
                self.prev_sic[sid] = sic
            nonfin = not excluded(cat)
            scope = "nonfin" if nonfin else "fin"
            add(Y, f"{scope}_eligible")
            add(Y, f"{scope}_eligible_{terc.get(sid, '?')}")
            for fld in P.FUND_FIELDS:
                if fld in have:
                    add(Y, f"{scope}_has|{fld}")
            for k, ok in P.combos(have).items():
                if ok:
                    add(Y, f"{scope}_combo|{k}")
            # year-over-year availability (growth / deterioration): True TTM now AND at the snapshot 12 months earlier,
            # each as it was known at its own date (ledger of earlier snapshots; nothing recomputed backwards)
            led = self.ttm_ledger.setdefault(sid, {})
            led[ym] = dict(vals)
            prev = led.get(ym - 100) or {}
            for b in APPROVED_TTM:
                if b in vals and b in prev:
                    add(Y, f"{scope}_yoy|{b}")
            if nonfin and ta is not None and ta > 0 and eq is not None and mc and all(b in vals for b in APPROVED_TTM) \
                    and all(b in prev for b in ("revenue", "net_income")):
                ni, oc, rv, gp = vals["net_income"], vals["operating_cash_flow"], vals["revenue"], vals["gross_profit"]
                rows_f.append([gp / ta, ni / ta, oc / ta, (ni - oc) / ta, eq / ta, ni / mc, oc / mc, rv / mc, eq / mc,
                               rv / prev["revenue"] - 1 if prev["revenue"] > 0 else np.nan,
                               (ni - prev["net_income"]) / ta])
            # valuation inputs (point-in-time market cap with the approved fields)
            if mc:
                for b in ("net_income", "operating_cash_flow", "revenue", "gross_profit"):
                    if b + "_ttm4q" in have:
                        add(Y, f"{scope}_valuation|{b}_to_mcap")
                if "stockholders_equity" in have:
                    add(Y, f"{scope}_valuation|equity_to_mcap")
            # missingness characterisation (non-financial; core = tech+all_core)
            if nonfin:
                fs = self.first_seen.get(sid)
                months_seen = (t - fs).days // 30 if fs else -1
                age_b = "seen_since_warmup_start" if fs is not None and fs <= date(2008, 7, 15) else \
                    ("lt12m" if months_seen < 12 else "12_24m" if months_seen < 24 else "ge24m")
                self.miss.append((y, ym, sid, int(not P.combos(have)["tech+all_core"]), terc.get(sid, "?"), ff12,
                                  age_b, grp))
            # ---- cross-domain alignment sample (dates only). Decision moment = the morning of `today` (the first
            # session after month-end t, before its open). Each component is dated by the day it became public:
            # filing day (usable from the next day), SIC filing day (effective the next day), the close of t for
            # prices and market cap. All must be <= today - 1 day.
            if sid in sample:
                sic_eff = None
                for eff, s_ in self.qr_sic.t.get(sid, ()):
                    if eff <= today:
                        sic_eff = eff
                comps = dict(fundamental_period_end=str(r.period_end) if r else None,
                             fundamental_filed=str(r.file_date) if r else None,
                             fundamental_usable_from=str(r.available) if r else None,
                             ttm_newest_quarter=ttm_new["quarters"][-1] if ttm_new else None,
                             ttm_newest_filed=ttm_new["filed"][-1] if ttm_new else None,
                             sic_filed=str(sic_eff - timedelta(days=1)) if sic_eff else None,
                             market_cap_close=str(t), price_close=str(t))
                known = {k: v for k, v in comps.items() if k != "fundamental_usable_from"}
                ok, late = P.alignment(str(today - timedelta(days=1)), **known)
                if r is not None and r.available > today:
                    ok, late = False, late + ["fundamental_usable_from"]
                if not ok:
                    self.c["A_alignment_violations"] += 1
                self._qr_log("A|" + json.dumps(dict(t=str(t), decision_morning=str(today), sid=sid,
                                                    ticker=f.symbol.value, group=grp, cat=cat, ff12=ff12, ok=ok,
                                                    late=late, **comps), sort_keys=True))
        # ---- feature-feature overlap (average cross-sectional Spearman; no return involved)
        if len(rows_f) >= 30:
            X = np.array(rows_f, float)
            X = X[np.isfinite(X).all(axis=1)]
            if X.shape[0] >= 30:
                R = np.argsort(np.argsort(X, axis=0), axis=0).astype(float)
                cm = np.corrcoef(R, rowvar=False)
                self.corr_sum = cm if self.corr_sum is None else self.corr_sum + cm
                self.corr_n += 1
                add(Y, "overlap_rows", X.shape[0])
        # ---- universe dynamics (entrants / exits between consecutive month-end snapshots)
        cur = set(by)
        feed_now = {str(f_.symbol.id) for f_ in fl}
        if self.prev_elig is not None:
            ent, ex = cur - self.prev_elig, self.prev_elig - cur
            add(Y, "entrants", len(ent))
            add(Y, "entrants_first_seen_within_365d",
                sum(1 for s_ in ent if self.first_seen.get(s_) and (t - self.first_seen[s_]).days <= 365
                    and self.first_seen[s_] > date(2008, 7, 15)))
            add(Y, "exits", len(ex))
            add(Y, "exits_stopped_trading", sum(1 for s_ in ex if s_ not in feed_now))
        self.prev_elig = cur
        dup = [v for v in comp.values() if len(v) > 1]
        add(Y, "companies_with_multiple_eligible_classes", len(dup))
        if dup and t.month in (1, 7):
            self._qr_log(f"DUP|{t}|" + ";".join(",".join(sorted(v)) for v in sorted(dup)))

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        c = self.c
        out = {"checks": c, "store_stats": dict(self.store.stats), "years": {}}
        for y, Y in sorted(self.y.items()):
            ages = Y.pop("_ages", {})
            Y["ages"] = {k: P.qstats(v) for k, v in ages.items()}
            out["years"][y] = Y
        # universe dynamics: entrants / exits by month from the monthly eligible sets are derived offline from 'M'
        # lines; exits from the fundamental feed (stopped trading) by year
        end = date(2017, 12, 28)
        exits = {}
        for sid, d in self.last_seen.items():
            if d < end:
                add(exits, str(d.year))
        out["feed_exits_by_year"] = exits
        out["tickers_changed"] = sum(1 for v in self.tickers.values() if len(v) > 1)
        out["tickers_securities"] = len(self.tickers)
        out["msector_securities"] = len(self.msec)
        out["msector_changed"] = sum(1 for v in self.msec.values() if len(v) > 1)
        # missingness characterisation: core missing share by tercile / FF12 / listing age / group, and exit from the
        # feed within the 12 months after t (snapshots up to 2016-11 only; characterisation, never a signal input)
        mc = {}
        for y, ym, sid, miss, tc, ff12, ab, grp in self.miss:
            for dim, val in (("tercile", tc), ("ff12", ff12), ("listing_age", ab), ("group", grp)):
                cell = mc.setdefault(f"{dim}|{val}", [0, 0])
                cell[0] += 1
                cell[1] += miss
            if ym <= 201611:
                ls = self.last_seen.get(sid)
                t0 = date(ym // 100, ym % 100, 28)
                ex = int(ls is not None and ls < end and ls <= t0 + timedelta(days=365))
                cell = mc.setdefault(f"exit12m|missing={miss}", [0, 0])
                cell[0] += 1
                cell[1] += ex
            cell = mc.setdefault(f"year|{y}", [0, 0])
            cell[0] += 1
            cell[1] += miss
        out["missingness"] = mc
        out["overlap"] = dict(names=["GP/A", "NI/A", "OCF/A", "accruals (NI-OCF)/A", "E/A", "NI/mcap", "OCF/mcap",
                                     "Rev/mcap", "E/mcap (B/M)", "revenue YoY growth", "change NI / A"],
                              snapshots=self.corr_n,
                              mean_spearman=(self.corr_sum / self.corr_n).round(3).tolist() if self.corr_n else None)
        text = json.dumps(out, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRP7F|{i // 9000}|{text[i:i + 9000]}")
