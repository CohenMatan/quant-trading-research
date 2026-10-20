# qr_ucr v1.0 — narrow SEC-based universe repair UCR-1 (owner D269, UR-2 option A; research/rr/universe_repair/
# UCR_protocol.md, frozen and SHA-256-pinned in qresearch.rr_ucr). Pure logic on plain records: no QuantConnect object,
# no I/O. STRICTLY POINT-IN-TIME: at a decision day t it uses only SEC filings filed strictly before t (the per-filing
# public SEC object ucr_sec_v1.json) and QuantConnect values observed on or before t. It decides which liquid
# securities WITHOUT a usable vendor market cap (no fundamentals object, missing cap, or blank classification fields)
# enter the >= $2B universe on an SEC cover-share market cap, and counts why the others do not. Aggregates only leave.
import calendar
from bisect import bisect_left
from datetime import date

import numpy as np

MIN_CAP = 2e9
MIN_FLOAT = 5e8                  # point-in-time public float floor (identity plausibility and population membership)
ALIVE_DAYS = 200                 # the registrant's latest periodic filing at most 200 days before t
SHARES_DAYS = 200                # cover shares filed at most 200 days before t
FLOAT_ASOF_DAYS = 650            # public float as-of date at most 650 days before t: the float is measured at the end of
                                 # the second fiscal quarter and first published in the NEXT 10-K (due 60-90 days after
                                 # year-end), so a timely filer's latest float is up to 6 + 12 + 3 months old (~640 d)
BAND = (0.5, 10.0)               # SEC cap / public float inside this band
REPAIRABLE = ("N", "M", "B_blank")
REASONS = ("repaired", "already_eligible", "vendor_cap_below_2B", "vendor_non_common", "other_exchange", "illiquid",
           "no_qc_ticker", "ambiguous_qc_ticker", "contested_prefix", "multi_class_ticker", "no_fresh_shares",
           "split_since_cover", "split_factor_unknown", "float_missing_or_below_0.5B", "cap_below_2B",
           "identity_band_fail")


def norm(t):
    return "".join(ch for ch in str(t or "").upper() if ch not in ".-/ ")


def ordinal(iso):
    return date.fromisoformat(iso).toordinal()


class RepairRef:
    """Per registrant: periodic filings [filed, prefix, common_ok, shares, cover_end] and floats [filed, as_of, value],
    each usable only from the day after its filing date."""

    def __init__(self, doc):
        self.meta = doc["meta"]
        self.ciks = sorted(doc["r"], key=int)
        self.p_day, self.p_pref, self.p_ok, self.s_day, self.s_val, self.s_end = [], [], [], [], [], []
        self.f_day, self.f_asof, self.f_val = [], [], []
        for c in self.ciks:
            r = doc["r"][c]
            p = sorted(r["p"], key=lambda x: x[0])
            self.p_day.append([ordinal(x[0]) for x in p])
            self.p_pref.append([x[1] for x in p])
            self.p_ok.append([int(x[2]) for x in p])
            s = [(ordinal(x[0]), float(x[3]), ordinal(x[4])) for x in p if x[3] is not None and x[4]]
            self.s_day.append([a for a, _, _ in s])
            self.s_val.append([b for _, b, _ in s])
            self.s_end.append([e for _, _, e in s])
            f = sorted((ordinal(a), ordinal(b), float(v)) for a, b, v in r["f"])
            self.f_day.append([a for a, _, _ in f])
            self.f_asof.append([b for _, b, _ in f])
            self.f_val.append([v for _, _, v in f])

    def current(self, i, t):
        """(prefix, common_ok) of the latest periodic filing filed before t, if filed within ALIVE_DAYS; else None."""
        k = bisect_left(self.p_day[i], t) - 1
        if k < 0 or t - self.p_day[i][k] > ALIVE_DAYS:
            return None
        return self.p_pref[i][k], self.p_ok[i][k]

    def shares(self, i, t):
        k = bisect_left(self.s_day[i], t) - 1
        if k < 0 or t - self.s_day[i][k] > SHARES_DAYS:
            return None
        return self.s_val[i][k], self.s_end[i][k]

    def float_(self, i, t):
        k = bisect_left(self.f_day[i], t) - 1
        while k >= 0:
            if t - self.f_asof[i][k] <= FLOAT_ASOF_DAYS:
                return self.f_val[i][k]
            k -= 1
        return None


class Repair:
    """At each decision day: repair(t, rows) -> {row index: SEC cap} for the repaired rows; reason counters per year.
    rows: (key, raw ticker, category, raw price, vendor cap, split-change ordinal or None, split factor known)
    category in E / A_lt / M / X / B_blank / B_explicit / N / I (the host's point-in-time classification)."""

    def __init__(self, ref):
        self.ref = ref
        self.year = {}
        self.rep_rows = []                     # (k, key)  repaired stock-months, for exits
        self.k = -1

    def _cnt(self, y, name, n=1):
        d = self.year.setdefault(y, {})
        d[name] = d.get(name, 0) + n

    def repair(self, year, t, rows):
        self.k += 1
        ref = self.ref
        claims = {}
        for i in range(len(ref.ciks)):
            cur = ref.current(i, t)
            if cur is None:
                continue
            pref, ok = cur
            if not pref:
                continue
            if not ok:
                self._cnt(year, "registrant_not_common_pit")
                continue
            claims.setdefault(pref, []).append(i)
        tmap = {}
        for j, r in enumerate(rows):
            t_ = norm(r[1])
            if t_:
                tmap.setdefault(t_, []).append(j)
        out = {}
        for pref, regs in claims.items():
            if len(regs) > 1:
                self._cnt(year, "contested_prefix", len(regs))
                continue
            i = regs[0]
            js = tmap.get(pref, [])
            if not js:
                self._cnt(year, "no_qc_ticker")
                continue
            if len(js) > 1:
                self._cnt(year, "ambiguous_qc_ticker")
                continue
            j = js[0]
            key, raw, cat, px, mc, sf_change, sf_known = rows[j]
            if cat == "I":
                self._cnt(year, "illiquid")
                continue
            if cat == "X":
                self._cnt(year, "other_exchange")
                continue
            if cat == "B_explicit":
                self._cnt(year, "vendor_non_common")
                continue
            if any(ch in str(raw) for ch in ".-"):
                self._cnt(year, "multi_class_ticker")
                continue
            sh = ref.shares(i, t)
            if sh is None:
                self._cnt(year, "no_fresh_shares" if cat in REPAIRABLE else "validation_no_shares")
                continue
            S, cover_end = sh
            if not sf_known:
                self._cnt(year, "split_factor_unknown" if cat in REPAIRABLE else "validation_split_unknown")
                continue
            if sf_change is not None and sf_change >= cover_end:
                self._cnt(year, "split_since_cover" if cat in REPAIRABLE else "validation_split")
                continue
            F = ref.float_(i, t)
            if F is None or F < MIN_FLOAT:
                self._cnt(year, "float_missing_or_below_0.5B" if cat in REPAIRABLE else "validation_no_float")
                continue
            cap = S * px
            if cat in ("E", "A_lt"):
                # shadow repair on vendor-capped securities: the repair rule against an independent vendor value
                self._cnt(year, "already_eligible" if cat == "E" else "vendor_cap_below_2B")
                if BAND[0] <= cap / F <= BAND[1]:
                    self._cnt(year, "validation_n")
                    self._cnt(year, "validation_agree_2B", int((cap >= MIN_CAP) == (mc >= MIN_CAP)))
                    self._cnt(year, "validation_within_5pct", int(abs(cap / mc - 1) <= 0.05))
                    self._cnt(year, "validation_within_2x", int(0.5 <= cap / mc <= 2.0))
                continue
            if cap < MIN_CAP:
                self._cnt(year, "cap_below_2B")
                continue
            if not BAND[0] <= cap / F <= BAND[1]:
                self._cnt(year, "identity_band_fail")
                continue
            self._cnt(year, "repaired")
            self._cnt(year, "repaired_" + cat)
            out[j] = cap
            self.rep_rows.append((self.k, key))
        return out


def reaudit_verdict(rec_repaired, rec_original, repair_year, year_verdict):
    """Frozen UCR-1 rule: the SCA-1 year rule on the REPAIRED universe's record, with the SCA-1 instrument taken from
    the ORIGINAL universe (repaired names would validate themselves), plus the repair-rule validation on
    vendor-capped securities (n >= 30 and >= 95% agreement at $2B)."""
    rec = dict(rec_repaired, instrument=rec_original["instrument"])
    v = year_verdict(rec)
    n = repair_year.get("validation_n", 0)
    agree = repair_year.get("validation_agree_2B", 0) / n if n else None
    why = list(v["reasons"])
    out = v["verdict"]
    if out != "FAIL" and (n < 30 or agree is None or agree < 0.95):
        out = "INCONCLUSIVE"
        why.append("repair rule not validated on vendor-capped securities (n >= 30, agreement >= 95%)")
    return dict(verdict=out, reasons=why, repair_validation=dict(n=n, agree_2B=None if agree is None else
                                                                 round(agree, 6)))
