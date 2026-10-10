"""P7-CP5e (D188): the X997 universe-repair host on a fake QuantConnect environment (SYNTHETIC prices, fundamentals and
SEC reference). Checked: the frozen-target digest; a security without a QuantConnect market cap is repaired by the
D111 SEC market cap only when that is >= $2B (and never with a cover count filed after the review); SEC-vs-QuantConnect
classification agreement; split continuity of the SEC market cap; identity extension used only in 'extended' mode;
survivorship and recovery aggregates; aggregate-only output; config rule and project file limit. Plus offline unit
tests of the identity-extension evidence rule."""
import copy
import hashlib
import json
import types
from datetime import date, datetime, timedelta

import pytest

from conftest import ROOT
from test_p7_export import _host
from test_p7_hosts import _market

X997 = "strategies/X997_universe_repair/main.py"
EPOCH = date(2000, 1, 1)
SHARES = {"c3": 5e7, "c7": 2e7}          # x $50 raw price: S03 $2.5B (repaired), S07 $1.0B (stays out)
OLD = {"2011-01-31": ["S00", "S01", "S03", "S99"], "2013-06-28": ["S00", "S01", "S03", "S99"]}
MISSING_FROM = date(2013, 1, 1)          # S03 and S07 lose their QuantConnect market cap from here


def g4(x):
    m, e = f"{abs(x):.3e}".split("e")
    return int(m.replace(".", "")) * 100 + int(e)


def _pes():
    out = []
    for y in range(2008, 2019):
        out += [date(y, 3, 31), date(y, 6, 30), date(y, 9, 30), date(y, 12, 31)]
    return out


def _split_date():
    import numpy as np
    return date.fromisoformat(str(np.datetime64(int(_market()["cal"][1800]), "D")))


def _ref():
    f, v = {}, {}
    split = _split_date()
    for j in range(12):
        cik = f"c{j}"
        flat, prev, vv = [], 0, {}
        for i, pe in enumerate(_pes()):
            if pe > date(2017, 12, 31):
                break
            d = (pe - EPOCH).days
            rec = [d - prev, 40, 2 if pe.month == 12 else 1]
            sh = SHARES.get(cik, 6e7)                      # $3.0B at $50 for everyone else
            if cik == "c4" and pe + timedelta(days=35) > split:
                sh *= 2                                    # S04 2:1 split: covers dated after it count post-split
            if (pe + timedelta(days=40)).isoformat() >= "2010-06-01":
                rec += [5, g4(sh)]                         # cover date 5 days before filing
            flat.append(rec)
            prev = d
            vv[str(d)] = [g4(100.0 + i), g4(5000.0)]
        f[cik], v[cik] = flat, vv
    sids = sorted({s for x in OLD.values() for s in x})
    oi = {s: i for i, s in enumerate(sids)}
    per = {t: sorted(set(x) - {"S99"} - ({"S03"} if t >= "2013" else set())) for t, x in OLD.items()}
    lost = {t: sorted(set(x) - set(per[t])) for t, x in OLD.items()}
    tsids = sorted({s for x in lost.values() for s in x})
    sha = hashlib.sha256(json.dumps([tsids, lost], sort_keys=True).encode()).hexdigest()
    return dict(f=f, v=v, ext={"S11": [(date(2008, 7, 1) - EPOCH).days, "c11"]},
                old={"sids": sids, "reviews": {t: [oi[s] for s in x] for t, x in OLD.items()}},
                tgt=[oi[s] for s in tsids], tgt_sha256=sha, epoch=str(EPOCH), forms={})


def _mutate(f, nd):
    f.security_reference = types.SimpleNamespace(security_type="ST00000001", is_depositary_receipt=False,
                                                 is_primary_share=True)
    f.company_reference.country_id = "USA"
    if f.symbol.id in ("S07", "S08"):          # one registrant (c7, two share classes in the fake)
        f.market_cap = 1e9                     # consistent with its SEC cover count ($1.0B)
    if f.symbol.id in ("S03", "S07") and nd >= MISSING_FROM:
        f.market_cap = 0.0


_CACHE = {}


def _run(monkeypatch, identity):
    if identity not in _CACHE:
        ref = types.ModuleType("p5e_ref")
        ref.load_table = _ref
        monkeypatch.setitem(__import__("sys").modules, "p5e_ref", ref)
        rows = {"S11": [["2010-06-01", 3570, "c11"]]}
        a = _host(monkeypatch, _market(), path=X997, cls="UniverseRepair", params=dict(identity=identity),
                  mutate=_mutate, sic_rows=rows)
        # the SEC identity CIKs of the fake are 'c<j>'; the reference table is keyed the same way
        a.qr_on_end()
        parts = sorted((m for m in a.msgs if m.startswith("QRP5E|")), key=lambda m: int(m.split("|")[1]))
        text = "".join(m.split("|", 2)[2] for m in parts)
        _CACHE[identity] = (a, json.loads(text), text)
    return _CACHE[identity]


def test_repair_comparison_and_survivorship(monkeypatch):
    a, st, text = _run(monkeypatch, "extended")
    assert st["target_check"]["sha256_match"] and st["target_check"]["stock_months"] == 3
    rep = st["repair"]
    assert rep["repaired"] > 0 and rep["below_2B"] > 0 and rep["no_fresh_shares"] == 0
    assert set(rep["bands"]) == {"gt2.5B", "lt1.5B"} or set(rep["bands"]) <= set(("gt2.5B", "lt1.5B", "2.2-2.5B"))
    # S03 repaired from 2013: its review rows are flagged; S07 ($1.0B) never enters
    yr = st["per_year"]
    assert yr["2013"]["repaired"] > 0 and yr["2011"]["repaired"] == 0
    cmp_ = st["mcap_comparison"]
    assert cmp_["n_away"] > 100 and cmp_["agree_away"] == cmp_["n_away"] and cmp_["abs_rel_median"] < 0.01
    sv = st["survivorship"]
    assert sv["2013"]["lost"][0] == 2 and sv["2013"]["recovered"][0] == 1 and sv["2013"]["still_lost"][0] == 1
    assert st["target_mcap_missing_status"] == {"repaired": [1, 0]}
    ts = st["target_securities"]
    assert ts["targets"] == 2 and ts["recovered_at_least_once"] == 1 and ts["with_mcap_missing_month"] == 1
    assert ts["never_recovered_by_last_reason"] == {"not_in_feed|in_universe_end_2017": 1}
    rec = st["target_recovery_by_reason"]
    assert rec["mcap_missing"][:2] == [1, 1] and rec["not_in_feed"][1] == 0
    assert st["sec_split_check"].get("continuous", 0) >= 1 and not st["sec_split_check"].get("jumps_with_price")
    plain = json.dumps({k: v for k, v in st.items() if k != "digests"})
    for bad in ('"S0', '"S1', '"c3', "5000.0", "2500000000"):
        assert bad not in plain, bad


def test_identity_extension_only_in_extended_mode(monkeypatch):
    _, ext, _ = _run(monkeypatch, "extended")
    _, v2, _ = _run(monkeypatch, "v2")
    assert any(k.startswith("mapped|ext|") for k in ext["identity_mapping"])
    assert not any(k.startswith("mapped|ext|") for k in v2["identity_mapping"])
    assert v2["identity_mapping"].get("unmapped|no_cik|2009", 0) > 0
    assert ext["identity_value_check"].get("ext|revenue_q|match", 0) > 0
    # the universe repair does not depend on the identity extension (MC9)
    assert ext["digests"]["universe_by_year"] == v2["digests"]["universe_by_year"]


def test_sec_market_cap_is_point_in_time(monkeypatch):
    """A cover count is used only from its filing date + 1; nothing filed after the review day; stale counts give
    nothing (D111 method, unchanged)."""
    from qr_sec_corrections import SECCorrections, SECFiling
    s = SECCorrections({})
    s.filings["k"] = [SECFiling(["a1", "10-Q", "2014-05-01", "2014-03-31", "2014-04-25", 1e8, {}]),
                      SECFiling(["a2", "10-Q", "2014-08-01", "2014-06-30", "2014-07-25", 3e8, {}])]
    s.splits["k"] = [(date(2014, 6, 2), 0.5)]
    assert s.market_cap("k", date(2014, 5, 1), 10.0) is None              # filed that day: not yet usable
    assert s.market_cap("k", date(2014, 5, 2), 10.0) == 1e9
    assert s.market_cap("k", date(2014, 6, 3), 5.0) == 1e9                # 2:1 split applied after the cover date
    assert s.market_cap("k", date(2014, 8, 2), 5.0) == 1.5e9              # new cover count, filed 08-01
    assert s.market_cap("k", date(2014, 12, 31), 5.0) is None             # 159 days old: stale


def test_identity_extension_rule():
    import sys
    sys.path.insert(0, str(ROOT / "research/phase7/cp5e"))
    import identity_extension as I

    def sub(filings, former=(), name="ACME CORP"):
        cols = {k: [] for k in ("form", "filingDate", "reportDate", "accessionNumber")}
        for fm, fd in filings:
            cols["form"].append(fm)
            cols["filingDate"].append(fd)
            cols["reportDate"].append(fd)
            cols["accessionNumber"].append(fd)
        return dict(name=name, formerNames=list(former), filings_all=cols)
    q = [("10-Q", f"{y}-{m:02d}-10") for y in range(2007, 2011) for m in (2, 5, 8, 11)]
    rows = [["2010-08-01", 3570, "123"]]
    r = I.evidence("X", rows, sub(q), {})
    assert r["category"] == "SAFE" and r["start"] == "2008-07-01"
    r = I.evidence("X", rows, sub(q, former=[{"name": "OLD SHELL HOLDINGS", "from": "2001-01-01",
                                               "to": "2009-03-01"}]), {})
    assert r["category"] == "BOUNDED" and r["start"] == "2009-03-02"
    r = I.evidence("X", rows, sub(q, former=[{"name": "ACME CORPORATION", "from": "2001-01-01",
                                               "to": "2009-03-01"}]), {})
    assert r["category"] == "SAFE"                                        # trivial renaming is not a change
    r = I.evidence("X", rows, sub(q, former=[{"name": "SPINCO", "from": "2001-01-01", "to": "2010-06-01"}]), {})
    assert r["category"] == "REJECT"                                      # discontinuity right before D0
    r = I.evidence("X", rows, sub([("10-Q", "2010-07-10")]), {})
    assert r["category"] == "BOUNDED" and r["start"] == "2010-07-10"      # registrant begins filing: chain start
    r = I.evidence("X", rows, sub([("8-K", "2009-01-01")]), {})
    assert r["category"] == "REJECT"                                      # no periodic filing before D0
    r = I.evidence("X", rows, None, {})
    assert r["category"] == "AMBIGUOUS"


def test_config_rule_and_file_limit():
    from qresearch import experiment, run
    for e in ("E997-01", "E997-02", "E997-03"):
        c = json.loads((ROOT / f"experiments/{e}/config.json").read_text())
        experiment.validate(c)
        files = run.assemble_files(c, None, False)
        assert len(files) <= 50 and all(len(v) <= 64_000 for v in files.values())
    for k, v in (("end", "2013-12-31"), ("start", "2010-01-04"), ("params", {"identity": "all"})):
        bad = copy.deepcopy(c)
        bad[k] = v
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)
