# X971 v1.1 (v1.0 divided by a zero SEC cover count, E971-01) — SEC verification of QuantConnect fundamentals + identity fingerprints for the D043 repair
# (infrastructure; NO orders, no rankings, no returns; D111). 2010-2021.
# Inputs: sec_ref (packed SEC tables built offline by research/phase2/sec/build_x971.py; public SEC data).
#  V  for every vendor report of a SAMPLE company: the SEC original filing for the same period (accession, form,
#     filing date), the ratio vendor value / SEC as-first-filed value per whitelisted field, and which SEC filing's
#     value the vendor value matches (original, amendment, later comparative) -> value + restatement + accession audit
#  X  the date the PIT layer (qr_fundamentals.PITStore) first exposed each sample report
#  K  market-cap method check on sample companies (month starts): SEC cover shares (latest usable filing, age <=
#     135 days, live split adjustment) x raw close vs the vendor's point-in-time market cap -> ratio
#  S  split cross-check: live split events vs the vendor split-factor ratio between the cover date and today
#  P  identity fingerprints: for each candidate (SEC filer without vendor data, security without fundamentals) pair,
#     the SEC public float / (SEC cover shares x QuantConnect raw close at the float date)
# Outputs carry ratios, dates and identifiers only; never vendor values (licence).
from AlgorithmImports import *
import json
from datetime import date, timedelta
from qr_harness import QRAlgorithm
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, accession_year, available_from, read_values
from qr_sec_corrections import SECCorrections
from sec_ref import load_table

COMPARE = ("revenue_ttm", "net_income_ttm", "total_assets", "stockholders_equity", "operating_cash_flow_ttm",
           "gross_profit_ttm", "operating_income_ttm", "revenue_q", "net_income_q")
VERSION_MAP = {"total_assets": "total_assets", "stockholders_equity": "stockholders_equity",
               "revenue_q": "revenue_q", "net_income_q": "net_income_q", "revenue_ttm": "revenue_fy",
               "net_income_ttm": "net_income_fy", "operating_cash_flow_ttm": "operating_cash_flow_fy"}
TOL = 0.005


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


def rel(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def fmt(x):
    return "na" if x is None else f"{x:.4f}"


class SECVerification(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        t = load_table()
        self.sample = t["sample"]
        self.sid_cik = {}
        corr = {}
        for cik, c in self.sample.items():
            for sid in c["sids"]:
                self.sid_cik[sid] = cik
                corr[sid] = {"status": "repaired", "filings": c["records"]}
        self.sec = SECCorrections(corr)
        self.recs = {cik: [dict(accn=r[0], form=r[1], filed=r[2], pe=date.fromisoformat(r[3]), values=r[6])
                           for r in c["records"]] for cik, c in self.sample.items()}
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS)
        self.seen = set()
        self.exposed = {}
        self.sf_hist = {}          # sid -> {date: vendor split factor}
        self.float_obs = t["float_obs"]
        self.pairs = t["pairs"]
        self.obs_queue = sorted((date.fromisoformat(o[0]), cik, i) for cik, obs in self.float_obs.items()
                                for i, o in enumerate(obs))
        self.qi = 0
        self.pair_stats = {}
        self.native_hits = {}
        self.native_obs = {}
        self.month = None
        self.counts = {"V": 0, "K": 0, "P_eval": 0, "split_events": 0, "split_disagree": 0}

    def on_data(self, data):
        super().on_data(data)
        for sym, sp in data.splits.items():
            if sp.type == SplitType.SPLIT_OCCURRED:
                sid = str(sym.id)
                if self.sec.has(sid):
                    self.sec.observe_split(sid, self.time.date(), float(sp.split_factor))
                    self.counts["split_events"] += 1
                    self._qr_log(f"SPLIT|{sid}|{self.time.date()}|{float(sp.split_factor):.6f}")

    def _verify(self, f, sid, cik, today):
        er = f.earning_reports
        pe, fd = as_date(er.period_ending_date.three_months), as_date(er.file_date.three_months)
        acc = str(er.accession_number.three_months or "")
        key = (sid, pe, fd)
        ay = accession_year(acc)
        vals = None
        if key not in self.seen:
            self.seen.add(key)
            vals = read_values(f, get)
            cands = [r for r in self.recs.get(cik, ()) if pe and abs((r["pe"] - pe).days) <= 6]
            orig = min((r for r in cands if not r["form"].endswith("/A")), key=lambda r: (r["filed"], r["accn"]),
                       default=None)
            parts = []
            if orig is not None:
                for k in COMPARE:
                    parts.append(f"{k}={fmt(rel(vals.get(k), orig['values'].get(k)))}")
            vers = self.sample[cik]["versions"].get(str(pe), [])
            vm = []
            for k, vk in VERSION_MAP.items():
                v = vals.get(k)
                if v is None:
                    continue
                hits = [(a, fo, fi) for a, fo, fi, vv in vers if vv.get(vk) and abs(v / vv[vk] - 1) <= TOL]
                vals_k = [(a, fo, fi, vv[vk]) for a, fo, fi, vv in vers if vv.get(vk)]
                if not vals_k:
                    continue
                first = vals_k[0]
                m0 = abs(v / first[3] - 1) <= TOL
                tag = "first" if m0 else ("later:" + ",".join(f"{a}/{fo}/{fi}" for a, fo, fi in hits[:2]) if hits
                                          else "none")
                distinct = len({round(x[3]) for x in vals_k})
                vm.append(f"{k}:{tag}:{distinct}")
            self._qr_log("V|" + "|".join(str(x) for x in (
                cik, sid, f.symbol.value, pe, fd, acc, today, available_from(pe, fd) if pe and fd else None,
                int(ay is not None and ay > today.year), int(pe is not None and fd is not None and (fd - pe).days == 45),
                orig["accn"] if orig else None, orig["form"] if orig else None, orig["filed"] if orig else None,
                ";".join(parts), ";".join(vm))))
            self.counts["V"] += 1
        if vals is not None:
            self.store.observe(sid, pe, fd, vals, ay, today)
        r = self.store.record(sid, today)
        if r is not None:
            k2 = (sid, r.period_end, r.file_date)
            if k2 not in self.exposed:
                self.exposed[k2] = today
                self._qr_log(f"X|{sid}|{r.period_end}|{r.file_date}|{today}")

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        today = self.time.date()
        monthly = (today.year, today.month) != self.month
        self.month = (today.year, today.month)
        by_sid = {}
        subs = []
        for f in fl:
            sid = str(f.symbol.id)
            by_sid[sid] = f
            cik = self.sid_cik.get(sid)
            if cik is None:
                continue
            subs.append(f.symbol)
            self.sf_hist.setdefault(sid, {})[today] = float(f.split_factor)
            if not f.has_fundamental_data:
                continue
            try:
                self._verify(f, sid, cik, today)
            except Exception as e:
                self._qr_log(f"VERR|{sid}|{today}|{type(e).__name__}")
            if monthly and float(f.market_cap or 0) > 0:
                fil, sh = self.sec.shares_on(sid, today)
                mc = sh * float(f.price) if sh else None
                ratio = rel(mc, float(f.market_cap))
                # vendor split-factor ratio between the cover date and today (cross-check of live events)
                sfr = None
                if fil is not None and fil.cover_date is not None:
                    hist = self.sf_hist.get(sid, {})
                    past = [d for d in hist if d <= fil.cover_date + timedelta(days=1)]
                    if past:
                        sf0 = hist[max(past)]
                        sfr = (sf0 / float(f.split_factor)) if float(f.split_factor) else None
                live = None
                if fil is not None and sh:
                    live = sh / fil.shares
                if sfr is not None and live is not None and abs(sfr / live - 1) > 0.01:
                    self.counts["split_disagree"] += 1
                self._qr_log(f"K|{cik}|{sid}|{today}|{fmt(ratio)}|{int(float(f.market_cap) >= 2e9)}|"
                             f"{int(mc is not None and mc >= 2e9)}|{fil.accn if fil else None}|"
                             f"{(today - fil.cover_date).days if fil and fil.cover_date else None}|{fmt(sfr)}|{fmt(live)}")
                self.counts["K"] += 1
        # identity fingerprints: process float observations whose date has passed (price = last close <= that date)
        nat = None
        if self.qi < len(self.obs_queue) and self.obs_queue[self.qi][0] < today:
            nat = {sid: (float(f.market_cap), float(f.price)) for sid, f in by_sid.items()
                   if f.has_fundamental_data and float(f.market_cap or 0) > 0 and float(f.price) > 0}
        while self.qi < len(self.obs_queue) and self.obs_queue[self.qi][0] < today:
            fdate, cik, i = self.obs_queue[self.qi]
            self.qi += 1
            if (today - fdate).days > 5:
                continue                      # warm-up gap: no close at the float date
            _, flt, shares, _sd = self.float_obs[cik][i]
            if not shares or shares <= 0 or not flt or flt <= 0:
                continue                      # unusable SEC observation (zero/blank count or float)
            # Q: is the registrant already covered natively (under another CIK)? SEC cover shares x raw close
            # within 3% of a native security's point-in-time market cap
            lo, hi = shares * 0.97, shares * 1.03
            for sid2, (mc, px) in nat.items():
                if lo * px <= mc <= hi * px:
                    st = self.native_hits.setdefault((cik, sid2), [0])
                    st[0] += 1
            self.native_obs[cik] = self.native_obs.get(cik, 0) + 1
            for sid in self.pairs.get(cik, ()):
                f = by_sid.get(sid)
                if f is None or float(f.price) <= 0:
                    continue
                ratio = flt / (shares * float(f.price))
                st = self.pair_stats.setdefault((cik, sid), [0, 0, []])
                st[0] += 1
                if 0.45 <= ratio <= 1.05:
                    st[1] += 1
                st[2].append(round(ratio, 3))
                self.counts["P_eval"] += 1
        return subs

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        for (cik, sid), (n, k, rs) in sorted(self.pair_stats.items()):
            if k >= 1:
                self._qr_log(f"P|{cik}|{sid}|{n}|{k}|{','.join(str(x) for x in rs)}")
        for (cik, sid), (k,) in sorted(self.native_hits.items()):
            if k >= 2 or k == self.native_obs.get(cik, 0):
                self._qr_log(f"Q|{cik}|{sid}|{self.native_obs.get(cik, 0)}|{k}")
        self._qr_log("C|" + json.dumps(self.counts, sort_keys=True))
