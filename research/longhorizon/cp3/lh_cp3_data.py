"""LH-CP3 (owner D244): per-registrant SEC metadata (cut-off-safe LH-CP2 loaders only) and the Stage C P2 rebuild.
No price, return or surprise value. Label tiers L0 / L1 and the evidence lists for M-CMP (protocol 2-4)."""
from __future__ import annotations

import importlib.util
import pickle
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT / "research/longhorizon/cp2"), str(ROOT / "src"),
                str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase2/sec")]
import lh_cp2_safe as SAFE  # noqa: E402
import lh_cp3_rules as R  # noqa: E402

_spec = importlib.util.spec_from_file_location("lh_cp2_inv", ROOT / "research/longhorizon/cp2/LH_CP2_investigation.py")
INV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(INV)
SC, V3 = INV.SC, INV.V3
CACHE = ROOT / "data/lh_cp3"
FP_NUM = INV.FP_NUM
L1_FORMS = ("10-Q", "10-K", "10-K405")


def load_index():
    xb_by_cik = defaultdict(list)
    for r in SAFE.xbrl_filings():
        p = r.get("period") or ""
        if len(p) != 8:
            continue
        try:
            pdn = V3.dn(f"{p[:4]}-{p[4:6]}-{p[6:8]}")
        except ValueError:
            continue
        xb_by_cik[str(int(r["cik"]))].append((pdn, r.get("form"), V3.dn(r["filed"]), r.get("accn"), r.get("fye"), r.get("name")))
    return xb_by_cik


class Reg:
    """Cut-off-safe metadata of one registrant: companyfacts by accession, submissions originals, XBRL index rows."""

    def __init__(self, cik, client, xb_by_cik, fv21):
        self.cik = str(int(cik))
        self.meta = INV.Meta(self.cik, client, xb_by_cik, fv21)      # LH-CP2 L0 route (unchanged)
        cf = SAFE.companyfacts(client, self.cik)
        self.fp = defaultdict(Counter)
        self.usd = defaultdict(set)                                    # accession -> {(end day, duration days)}
        self.ends = defaultdict(set)
        if cf:
            for tags in cf["facts"].values():
                for body in tags.values():
                    for unit, facts in body["units"].items():
                        for f in facts:
                            a = f.get("accn")
                            if not a:
                                continue
                            if f.get("fp"):
                                self.fp[a][f["fp"]] += 1
                            if f.get("start"):
                                e, s = V3.dn(f["end"]), V3.dn(f["start"])
                                self.ends[a].add(e)
                                if unit == "USD":
                                    self.usd[a].add((e, e - s))
        rows = SAFE.submissions(client, self.cik) or []
        self.first_filing = min((r["filingDate"] for r in rows), default=None)
        self.sub = []                                                  # (period, form, filed, accession, isXBRL)
        self.trans = []                                                # (report day, filed day)
        for r in rows:
            if not r.get("reportDate"):
                continue
            pdn, fdn = V3.dn(r["reportDate"]), V3.dn(r["filingDate"])
            if r.get("form") in R.ORIGINAL_FORMS:
                self.sub.append((pdn, r["form"], fdn, r["accessionNumber"], int(r.get("isXBRL") or 0)))
            if r.get("form") in R.T_FORMS:
                self.trans.append((pdn, fdn))
        self.sub.sort()
        self.orig = V3.originals(fv21) if fv21 else {}
        self._labels = {}

    # ---------------------------------------------------------------- L0 / L1 labels
    def acc_label(self, a):
        c = self.fp.get(a)
        return FP_NUM.get(c.most_common(1)[0][0]) if c else None

    def sub_row(self, p, D=None):
        c = [r for r in self.sub if abs(r[0] - p) <= 7 and r[1] in L1_FORMS and (D is None or r[2] <= D - 1)]
        return min(c, key=lambda r: r[2]) if c else None

    def label_l1(self, p):
        """-> (label or None, class) with class Verified / Invalid / Unknown-nonXBRL / Unknown-noFacts /
        Unknown-noAccession (protocol 2)."""
        r = self.sub_row(p)
        if r is None:
            return None, "Unknown-noAccession"
        a = r[3]
        if self.fp.get(a):
            fd = self.orig.get(p)
            m_ok = any(abs(e - p) <= 7 for e in self.ends.get(a, ()))
            if m_ok and (fd is None or abs(r[2] - fd) <= 3):
                return self.acc_label(a), "Verified"
            return None, "Invalid"
        return None, ("Unknown-nonXBRL" if r[4] == 0 else "Unknown-noFacts")

    def label(self, p):
        """Verified label (L0 else L1) and its source: (label, 'L0' | 'L1' | class of the failure)."""
        if p not in self._labels:
            l0 = self.meta.label(p)
            if l0 is not None:
                self._labels[p] = (l0, "L0")
            else:
                l1, cls = self.label_l1(p)
                self._labels[p] = (l1, "L1") if cls == "Verified" and l1 is not None else (None, cls)
        return self._labels[p]

    def accession(self, p):
        f = self.meta.filing(p)
        if f is not None:
            return f[3], f[2]
        r = self.sub_row(p)
        return (r[3], r[2]) if r else (None, None)

    # ---------------------------------------------------------------- evidence
    def evidence(self):
        """M-CMP evidence: (accession, period E, filed E, label E, [(end, duration)]) for original 10-Q / 10-K
        filings carrying facts (submissions rows; else XBRL-index rows)."""
        if not hasattr(self, "_ev"):
            seen, ev = set(), []
            for p, form, fd, a, _x in self.sub:
                if form in L1_FORMS and a in self.fp and a not in seen:
                    seen.add(a)
                    ev.append((a, p, fd, self.acc_label(a), sorted(self.usd.get(a, ()))))
            for p, form, fd, a, _fye, _n in self.meta.xb:
                if form in ("10-Q", "10-K") and a in self.fp and a not in seen:
                    seen.add(a)
                    ev.append((a, p, fd, self.acc_label(a), sorted(self.usd.get(a, ()))))
            self._ev = ev
        return self._ev

    def seq_filings(self):
        return [(p, f, fd) for p, f, fd, _a, _x in self.sub]

    def transitions(self, D):
        return [p for p, fd in self.trans if fd <= D - 1]

    def reconstruct(self, chain, D, hidden_from=None):
        """R* per chain period. hidden_from: pseudo-XBRL start day (validation) - filings filed before it carry no
        facts and no label. Returns [(label, tier, seq, cmp)] newest first."""
        ev = self.evidence()
        if hidden_from is not None:
            ev = [e for e in ev if e[2] >= hidden_from]
        seq = R.seq_labels(self.seq_filings(), D, self.transitions(D))
        out = []
        for p in chain:
            s = next((v for k, v in seq.items() if abs(k - p) <= 7), None)
            c = R.cmp_label(p, ev, D)
            lab, tier = R.combine(s, c)
            out.append((lab, tier, s, c))
        return out


# ----------------------------------------------------------------------------------------------- Stage C P2 rebuild
def build_p2(client, t, xb_by_cik, fmap, progress=True):
    """Exactly the LH-CP2 P2 rebuild (frozen Stage C functions). Returns den, recs, chains, regs."""
    ident = SC.Ident(t)
    U = SC.load_universe()
    revs = [dict(T=T, D=D, Dn=V3.dn(str(D)), m=T.year * 12 + T.month - 1 + 1, year=T.year) for T, D in V3.review_days()]
    den = Counter()
    items_by_cik = defaultdict(list)
    first_m = {sid: min(u["months"]) for sid, u in U.items() if u["months"]}
    last_m = {sid: max(u["months"]) for sid, u in U.items() if u["months"]}
    DEC21 = 2021 * 12 + 11
    for sid, u in U.items():
        for j, r in enumerate(revs):
            if r["m"] not in u["months"]:
                continue
            cik, sic, _src = ident.at(sid, r["Dn"])
            if sic is not None and 6000 <= sic <= 6999:
                continue
            den[r["year"]] += 1
            if cik is not None and sic is not None:
                items_by_cik[cik].append((sid, j, sic))
    recs, chains, regs = [], {}, {}
    for ci, (cik, items) in enumerate(sorted(items_by_cik.items(), key=lambda kv: int(kv[0]))):
        cols = t["f"].get(cik)
        if not cols:
            continue
        cf = SAFE.companyfacts(client, cik)
        fx = V3.Facts(cf) if cf else V3.Facts({})
        orig = V3.originals(cols)
        memo = {}

        def known(con, p, vd):
            k = (con, p, vd)
            if k not in memo:
                memo[k] = SC.q_detail(fx, con, p, vd)[0] is not None
            return memo[k]
        reg = None
        for sid, j, sic in items:
            r = revs[j]
            D, y = r["Dn"], r["year"]
            vd = D - 1
            vis = sorted(p for p, fd in orig.items() if fd + 1 <= D)
            if not vis or D - vis[-1] > V3.MAX_AGE:
                continue
            c13 = V3.chain_back(vis, len(vis) - 1, 13)
            if not c13:
                continue
            ok1 = all(known("net_income", p, vd) for p in c13)
            ok2 = all(known("revenue", p, vd) for p in c13)
            if not (ok1 or ok2):
                continue
            if reg is None:
                reg = Reg(cik, client, xb_by_cik, cols)
                regs[cik] = reg
            key = (cik, tuple(c13))
            if key not in chains:
                chains[key] = dict(INV.chain_meta(reg.meta, c13, D, fmap), D=D, sms=0, identity=False, years=set(),
                                   sids=set())
            ch = chains[key]
            ch["sms"] += 1
            ch["years"].add(y)
            ch["sids"].add(sid)
            c_id, _s, _src = ident.at(sid, c13[-1])
            if (c_id is not None and c_id != cik) or (U[sid]["ciks"] and int(cik) not in U[sid]["ciks"]):
                ch["identity"] = True
            ta = fx.ta_known(c13[0], vd)
            age = None
            if reg.first_filing:
                age = (r["D"] - date.fromisoformat(reg.first_filing)).days / 365.25
            depth = sum(1 for p in orig if p < c13[-1])
            recs.append(dict(year=y, j=j, sid=sid, key=key, ok1=ok1, ok2=ok2, sic=sic, ta=ta, age=age, D=D,
                             depth=depth,
                             entrant=first_m.get(sid, 0) > SC.M0 + 12 and r["m"] - first_m[sid] < 12,
                             leaver=last_m.get(sid, DEC21) < DEC21))
        if progress and ci % 250 == 0:
            print("registrants", ci, len(items_by_cik), flush=True)
    return den, recs, chains, regs


def check_repro(den, recs):
    import json
    stage_c = json.loads((ROOT / "research/longhorizon/stage_c/LH_StageC_audit.json").read_text())["candidates"]
    cov = {c: Counter() for c in ("C1", "C2", "C6")}
    for rec in recs:
        cov["C1"][rec["year"]] += rec["ok1"]
        cov["C2"][rec["year"]] += rec["ok2"]
        cov["C6"][rec["year"]] += rec["ok1"] and rec["ok2"]
    repro = {c: {str(y): round(cov[c][y] / den[y], 4) if den[y] else None for y in range(2011, 2022)} for c in cov}
    ok = all(repro[c][str(y)] == stage_c[c]["by_year"][str(y)] for c in cov for y in range(2011, 2022))
    return ok, repro


def save_cache(name, obj):
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / name).write_bytes(pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL))


def load_cache(name):
    p = CACHE / name
    return pickle.loads(p.read_bytes()) if p.exists() else None
