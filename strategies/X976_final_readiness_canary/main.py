# X976 v1.3 — v1.3 uses the shared frozen observation step qr_fundamentals.observe_vendor (same logic as v1.2's
# inline code). X976 v1.2 — FINAL fundamental-data readiness canary (D113, D113a, D114). v1.2: the harness's history-only warm-up
# (config 'warmup_start') replaces the canary's own; D114 field-level releases feed the store; C11 accepts a
# quarantined TTM component only through a verified field release of that very field; new C12 (a partial record is
# never the current report); availability counts of each approved H016 field (coverage only, no returns).
# v1.1 header (unchanged below):
# X976 v1.1 — FINAL fundamental-data readiness canary (D113, D113a). Extends X972 v1.1 (post-remediation PIT canary)
# with the True TTM layer, the financial/REIT exclusion policy and final usable-coverage tables.
# v1.1 (after E976-01): (a) the PIT store observes EVERY company with fundamentals every day, not only eligible ones,
# so a company entering the >= $2B universe already has its quarterly history (E976-01 observed eligible names only:
# TTM was missing for every newly eligible company); (b) observation-only warm-up from the config start (2008-07-01):
# vendor reports seen before 2010-01-04 are history only — no coverage, returns or eligibility statistics are
# counted before 2010-01-04; (c) per-security TTM-missingness lines and size/return characterisation of the
# non-financial names without usable True TTM. Original X972 header:
# post-remediation PIT canary and coverage/bias re-audit (infrastructure; NO orders, no rankings,
# no factor returns; D111). Universe = harness universe WITH the opt-in dated SEC correction layer
# (universe.sec_corrections). 2010-2021.
# Checks (counts of violations; all must be 0):
#  C1 an SEC filing is never visible before the day after its filing date (corrected companies)
#  C2 SEC amendments are visible only after their own filing date
#  C3 quarantined vendor values stay hidden unless on the SEC-verified release list; timing holds respected
#  C4 a corrected company is eligible only with a usable cover count (filed before today, cover <= 135 days old,
#     status 'repaired') and a reconstructed market cap >= $2B
#  C5 no future share information: the count used was filed before today; split adjustments only for splits
#     already observed (ex-date <= today)
#  C6 split handling: reconstructed market cap continuity across split dates of corrected companies
#  C7 acquisitions/delistings: a corrected company is never eligible after its last trading day
#  C8 Visa correction (dated exchange override) still eligible on the corrected dates
#  C9 financial-format classification stability (flips per company)
# Coverage by year and size; corrected vs native; quarantine coverage loss; universe composition returns
# (equal-weight month returns of native vs corrected eligible names: the D043 bias measure, not a factor).
# Outputs: counts, dates, identifiers and ratios only (no vendor values).
from AlgorithmImports import *
import json
from datetime import date, timedelta
from qr_harness import QRAlgorithm, _attr
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, TTM_BASES, financial_format, observe_vendor
from qr_industry import classify, excluded
from qr_sec_corrections import MAX_SHARE_AGE_DAYS

USABLE = ("revenue_ttm", "net_income_ttm", "total_assets", "stockholders_equity")
COUNT_FROM = date(2010, 1, 4)       # development start; earlier days are observation-only warm-up


def get(obj, path):
    for p in path.split("."):
        obj = getattr(obj, p)
    return obj


def as_date(v):
    try:
        d = v.date() if callable(getattr(v, "date", None)) else v
        return d if d is not None and d.year > 1900 else None
    except Exception:
        return None


def add(h, k, n=1):
    h[k] = h.get(k, 0) + n


class RemediationCanary(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        if self.qr_sec is None:
            raise Exception("X972 needs universe.sec_corrections")
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS, holds=self.qr_timing_holds, releases=self.qr_quarantine_releases,
                              blocked=self.qr_restatement_blocks, field_releases=self.qr_field_releases)
        self.c = {k: 0 for k in ("C1_sec_visible_before_filing", "C2_amendment_early", "C3_quarantine_exposed",
                                 "C3_hold_violated", "C4_unjustified_entry", "C5_future_share_info",
                                 "C6_split_jumps", "C7_eligible_after_last_trade", "C3_restatement_block_exposed",
                                 "C10_ttm_before_component_available", "C11_ttm_uses_blocked_component",
                                 "C12_partial_record_is_current",
                                 "stock_days", "corrected_days")}
        self.c.update(coverage={}, fin_flips={}, visa={}, exchange={}, split_checks=[], ret={}, size={},
                      corrected_first={}, corrected_last={}, quarantine_lost={}, ttm_reasons={}, sic_vs_structure={})
        self.q_keys_str = set()
        self.month = None
        self.prev_cls = {}
        self.prev_mc = {}
        self.last_px = {}            # sid -> (adjusted price, month) for month returns
        self.month_members = {}      # previous month's eligible: sid -> group
        self.delisted = {}
        self.seen_q = set()
        self.q_keys = set()          # vendor reports observed while quarantined (and not on the release list)
        self.q_latest = {}           # sid -> newest vendor report is quarantined
        self.member_px = {}          # sid -> last adjusted price seen this month (members of last month)
        self.ttm_members = {}        # previous month's non-financial eligible: sid -> 'ttm_usable' | 'ttm_missing'
        self.ttm_px = {}
        self.ttm_sec = {}            # sid -> [group, months non-financial eligible, months final-usable, {reason: n}]

    def on_data(self, data):
        super().on_data(data)
        for sym, dl in data.delistings.items():
            if dl.type == DelistingType.DELISTED:
                self.delisted[str(sym.id)] = self.time.date()
        for sym, sp in data.splits.items():
            if sp.type == SplitType.SPLIT_OCCURRED and self.qr_sec.has(str(sym.id)):
                self.c["split_checks"].append([str(sym.id), str(self.time.date()), float(sp.split_factor)])

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        out = super()._qr_select(fl)
        today = self.time.date()
        day = str(today)
        sec = self.qr_sec
        elig = set(self.qr_eligible)
        corr = self.qr_corrected
        c = self.c
        monthly = (today.year, today.month) != self.month
        self.month = (today.year, today.month)
        by = {}
        corr_sids = {str(s.id) for s in corr}
        for f in fl:
            sid = str(f.symbol.id)
            if f.symbol in elig:
                by[sid] = f
            if sid in corr_sids or not f.has_fundamental_data:
                continue
            # v1.3: the shared frozen observation step (qr_fundamentals.observe_vendor), EVERY company daily
            obs = observe_vendor(self.store, sid, f, today, get, self.seen_q)
            if obs is None:
                continue
            pe, fd, q = obs
            if q:
                self.q_keys.add((sid, pe, fd))
                self.q_keys_str.add((sid, str(pe), str(fd)))
            self.q_latest[sid] = q
        for sid, f in by.items():
            c["stock_days"] += 1
            fix = f.symbol in corr
            if fix:
                c["corrected_days"] += 1
                c["corrected_first"].setdefault(sid, day)
                c["corrected_last"][sid] = day
                fil, sh = sec.shares_on(sid, today)
                # C4 / C5: recompute the justification from first principles
                if (fil is None or sh is None or fil.available > today or fil.filed >= today
                        or (today - fil.cover_date).days > MAX_SHARE_AGE_DAYS
                        or sec.meta.get(sid, {}).get("status") != "repaired"
                        or sh * float(f.price) < 2e9):
                    c["C4_unjustified_entry"] += 1
                if fil is not None and any(ex > today for ex, _ in sec.splits.get(sid, ())):
                    c["C5_future_share_info"] += 1
                if sid in self.delisted and self.delisted[sid] < today:
                    c["C7_eligible_after_last_trade"] += 1
                # C6: market-cap continuity around split events
                mc = self.qr_eligible_info[f.symbol][0]
                pm = self.prev_mc.get(sid)
                if pm is not None and any(pm[0] < ex <= today for ex, _ in sec.splits.get(sid, ())):
                    if abs(mc / pm[1] - 1) > 0.35:
                        c["C6_split_jumps"] += 1
                    c["split_checks"].append([sid, day, round(mc / pm[1], 4)])
                self.prev_mc[sid] = (today, mc)
                sec.feed(sid, today, self.store)
                r = self.store.record(sid, today)
                if r is not None and r.file_date >= today:
                    c["C1_sec_visible_before_filing"] += 1
                if r is not None:
                    for fi in sec.filings.get(sid, ()):
                        if fi.form.endswith("/A") and fi.period_end == r.period_end and fi.filed == r.file_date \
                                and fi.filed >= today:
                            c["C2_amendment_early"] += 1
            else:
                r = self.store.record(sid, today)
                if r is not None:
                    if (sid, r.period_end, r.file_date) in self.q_keys:
                        c["C3_quarantine_exposed"] += 1
                    if (str(r.period_end), str(r.file_date)) in self.store.blocked.get(sid, ()):
                        c["C3_restatement_block_exposed"] += 1
                    h = self.store.holds.get(sid, {}).get(str(r.period_end))
                    if h is not None and str(today) < h:
                        c["C3_hold_violated"] += 1
        if self.month_members or self.ttm_members:
            for f in fl:
                sid = str(f.symbol.id)
                if (sid in self.month_members or sid in self.ttm_members) and float(f.adjusted_price or 0) > 0:
                    self.member_px[sid] = float(f.adjusted_price)
        if monthly and today >= COUNT_FROM:
            self._monthly(fl, by, today)
        return out

    def qr_select_universe(self, eligible):
        return []

    def _monthly(self, fl, by, today):
        c = self.c
        y = str(today.year)
        ym = today.year * 100 + today.month
        cov = c["coverage"].setdefault(y, {})
        corr = {str(s.id) for s in self.qr_corrected}
        caps = {str(s.id): v[0] for s, v in self.qr_eligible_info.items()}
        order = sorted(caps, key=lambda k: (caps[k], k))
        terc = {k: ("T1" if i < len(order) / 3 else "T2" if i < 2 * len(order) / 3 else "T3") for i, k in enumerate(order)}
        # universe-composition returns: previous month's members, equal weight, adjusted prices (characterisation)
        # (a member that stopped trading during the month counts at its last traded price)
        px = {str(f.symbol.id): float(f.adjusted_price) for f in fl if float(f.adjusted_price or 0) > 0}
        for sid, grp in self.month_members.items():
            p0 = self.last_px.get(sid)
            p1 = px.get(sid, self.member_px.get(sid))
            if p0 is None or p1 is None:
                add(c["ret"], f"{grp}|missing_price")
                continue
            if sid not in px:
                add(c["ret"], f"{grp}|ended_in_month")
            cell = c["ret"].setdefault(f"{grp}|{y}", [0, 0.0])
            cell[0] += 1
            cell[1] += p1 / p0 - 1
        for sid, grp in self.ttm_members.items():   # same measure for non-financial names with/without True TTM
            p0, p1 = self.ttm_px.get(sid), px.get(sid, self.member_px.get(sid))
            if p0 is None or p1 is None:
                continue
            cell = c["ret"].setdefault(f"{grp}|{y}", [0, 0.0])
            cell[0] += 1
            cell[1] += p1 / p0 - 1
        self.month_members = {sid: ("corrected" if sid in corr else "native") for sid in by}
        self.last_px = {sid: px[sid] for sid in by if sid in px}
        self.ttm_members = {}
        self.ttm_px = {}
        self.member_px = {}
        for sid, f in by.items():
            grp = "corrected" if sid in corr else "native"
            add(cov, f"eligible_{grp}")
            add(c["size"], f"{y}|{terc.get(sid, '?')}|{grp}")
            r = self.store.record(sid, today)
            if r is not None and all(r.values.get(k) is not None for k in USABLE):
                add(cov, f"usable_{grp}")
                ff = financial_format(r.values)
                add(cov, f"financial_format_{grp}" if ff else f"operating_format_{grp}" if ff is False
                    else f"unclassifiable_{grp}")
                prev = self.prev_cls.get(sid)
                if prev is not None and prev != ff:
                    add(c["fin_flips"], sid)
                self.prev_cls[sid] = ff
            elif r is None and grp == "native":
                cur = self.store.current.get(sid)
                if cur is None and any(p for p in self.store.pending.get(sid, []) or []):
                    add(cov, "withheld_timing_native")
                else:
                    add(cov, f"no_usable_record_{grp}")
            else:
                add(cov, f"no_usable_record_{grp}")
            # ---- D113: True TTM availability, financial/REIT policy, final usable coverage
            core = []
            have = {}
            if r is not None and r.partial:
                c["C12_partial_record_is_current"] += 1
            for b in TTM_BASES:
                v, det = self.store.ttm_detail(sid, b, today)
                if v is None:
                    add(c["ttm_reasons"], f"{y}|{b}|{det}")
                    continue
                add(cov, f"ttm_{b}_{grp}")
                have[b] = v
                if any(fd >= str(today) for fd in det["filed"]):
                    c["C10_ttm_before_component_available"] += 1
                for pe, fd in zip(det["quarters"], det["filed"]):
                    if (pe, fd) in self.store.blocked.get(sid, ()):
                        c["C11_ttm_uses_blocked_component"] += 1
                    elif (sid, pe, fd) in self.q_keys_str:
                        rel = self.store.field_releases.get(sid, {}).get((pe, fd), ())
                        if b + "_q" not in rel:
                            c["C11_ttm_uses_blocked_component"] += 1
                        else:
                            add(cov, f"ttm_uses_field_release_{b}")
                if b in ("revenue", "net_income", "operating_cash_flow"):
                    core.append(b)
            ff = financial_format(r.values) if r is not None else None
            sic = self.qr_sic.sic_on(sid, today) if self.qr_sic is not None else None
            cat, src = classify(sic, ff)
            add(cov, f"cat_{cat}_{grp}")
            add(cov, f"catsrc_{src}")
            if sic is not None and ff is not None:
                sc = "REIT" if sic == 6798 else "fin" if 6000 <= sic <= 6999 else "op"
                add(c["sic_vs_structure"], f"sic={sc}|structure_fin={ff}|sic2={sic // 100}" if sc != "op" or ff
                    else f"sic={sc}|structure_fin={ff}")
            snap = r is not None and r.values.get("total_assets") is not None and \
                r.values.get("stockholders_equity") is not None
            if not excluded(cat):
                add(cov, f"nonfin_eligible_{grp}")
                ok = len(core) == 3 and snap
                tc = terc.get(sid, "?")
                add(cov, f"nonfin_eligible_{tc}")
                # D114: availability of each approved H016 field and of the profitability ratios they allow
                # (coverage only; no ranking, no returns)
                ta = r.values.get("total_assets") if r is not None else None
                eq = r.values.get("stockholders_equity") if r is not None else None
                for b in ("revenue", "gross_profit", "net_income", "operating_cash_flow"):
                    if b in have:
                        add(cov, f"avail_{b}_ttm4q")
                        if ta is not None and ta > 0:
                            add(cov, f"avail_{b}_ttm4q_and_assets_pos")
                if ta is not None and ta > 0:
                    add(cov, "avail_assets_pos")
                if eq is not None:
                    add(cov, "avail_equity")
                    if eq > 0:
                        add(cov, "avail_equity_pos")
                        if "net_income" in have:
                            add(cov, "avail_net_income_ttm4q_and_equity_pos")
                ts = self.ttm_sec.setdefault(sid, [grp, 0, 0, {}])
                ts[1] += 1
                if ok:
                    add(cov, f"final_usable_{grp}")
                    add(cov, f"final_usable_{tc}")
                    ts[2] += 1
                else:
                    why = "no balance-sheet snapshot" if len(core) == 3 else \
                        self.store.ttm_detail(sid, [b for b in ("revenue", "net_income", "operating_cash_flow")
                                                    if b not in core][0], today)[1]
                    add(ts[3], why)
                    add(cov, f"not_usable|{why}")
                if sid in px:
                    self.ttm_members[sid] = "ttm_usable" if ok else "ttm_missing"
                    self.ttm_px[sid] = px[sid]
            if grp == "corrected" and today.day <= 7:
                try:
                    ex = str(self.securities[f.symbol].primary_exchange)
                except Exception:
                    ex = "unsubscribed"
                add(c["exchange"], ex)
                if ex not in ("NYSE", "NASDAQ", "AMEX", "ARCA", "BATS"):
                    self._qr_log(f"EXCH|{sid}|{today}|{ex}")
        # quarantine coverage loss: native eligible names whose newest vendor report is quarantined and no usable
        # earlier record remains (counted from the store's statistics per month)
        add(c["quarantine_lost"], y, sum(1 for sid in by if sid not in corr and self.store.record(sid, today) is None
                                        and self.q_latest.get(sid)))
        for f in fl:
            if f.symbol.value == "V" and today.day <= 7:
                c["visa"][str(today)] = int(str(f.symbol.id) in by)
        for sid in corr:
            self._qr_log(f"M|{ym}|{sid}|{int(caps.get(sid, 0) / 1e6)}|{terc.get(sid, '?')}")

    def qr_on_end(self):
        c = self.c
        c["store_stats"] = dict(self.store.stats)
        c["fin_flips_summary"] = {"companies_with_flips": len(c["fin_flips"]),
                                  "flips": sum(c["fin_flips"].values())}
        c["delisted_corrected"] = {sid: str(d) for sid, d in self.delisted.items() if self.qr_sec.has(sid)}
        for sid, (grp, n, u, why) in sorted(self.ttm_sec.items()):   # every non-financial eligible security
            self._qr_log("T|%s|%s|%d|%d|%s" % (sid, grp, n, u, ";".join(f"{k}={v}" for k, v in sorted(why.items()))))
        c["ttm_sec_summary"] = {"securities": len(self.ttm_sec),
                                "with_missing_months": sum(1 for v in self.ttm_sec.values() if v[2] < v[1])}
        text = json.dumps(c, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRC76|{i // 9000}|{text[i:i + 9000]}")
