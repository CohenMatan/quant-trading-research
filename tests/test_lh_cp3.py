"""LH-CP3 (owner D244): missing fiscal labels recovery & validation. Cut-off enforcement for local records and the
targeted EDGAR header requests; reconstruction rules (M-SEQ, M-CMP, R*, H-FYE); statistics; frozen protocol."""
import hashlib
import importlib.util
import sys
from datetime import date

import pytest

from conftest import ROOT

CP3 = ROOT / "research/longhorizon/cp3"
sys.path[:0] = [str(CP3), str(ROOT / "research/longhorizon/cp2")]
import lh_cp3_rules as R  # noqa: E402
import lh_cp3_safe as HS  # noqa: E402

PROTOCOL_SHA256 = "38d790e5efee56a256418372a9efc528827e2fcf148bbbb43eb27f0d797d75cb"


def dn(s):
    return (date.fromisoformat(s) - date(2000, 1, 1)).days


def test_protocol_hash_pinned():
    assert hashlib.sha256((CP3 / "LH_CP3_protocol.md").read_bytes()).hexdigest() == PROTOCOL_SHA256


def test_earlier_protocols_unchanged():
    sc = ROOT / "research/longhorizon/stage_c/LH_StageC_protocol.md"
    cp2 = ROOT / "research/longhorizon/cp2/LH_CP2_protocol.md"
    assert hashlib.sha256(sc.read_bytes()).hexdigest().startswith("ff97789b02007599")
    assert hashlib.sha256(cp2.read_bytes()).hexdigest().startswith("f7cbac944e433fcd")


# ----------------------------------------------------------------------------------------------- header cut-off
MAN = {"0000320193-09-000001": dict(filed="2009-07-22", form="10-Q", cik=320193),
       "0000320193-22-000001": dict(filed="2022-01-28", form="10-Q", cik=320193),
       "0000320193-09-000002": dict(filed="2009-08-01", form="10-Q/A", cik=320193)}


def test_header_url_refuses_unlisted_post_cutoff_and_amendments():
    u = HS.header_url(320193, "0000320193-09-000001", MAN)
    assert u == "https://www.sec.gov/Archives/edgar/data/320193/000032019309000001/0000320193-09-000001.hdr.sgml"
    for accn in ("0000320193-22-000001", "0000320193-09-000002", "0000320193-10-999999", "bad"):
        with pytest.raises(HS.CutoffError):
            HS.header_url(320193, accn, MAN)
    with pytest.raises(HS.CutoffError):
        HS.header_url(1234, "0000320193-09-000001", MAN)
    assert HS.fallback_url(320193, "0000320193-09-000001", MAN).endswith("0000320193-09-000001.txt")


def _hdr(filed, accn="0000320193-09-000001", changed=None, body=b"SECRET BODY 2023-05-05"):
    h = (f"<SEC-HEADER>0000320193-09-000001.hdr.sgml : {filed}\n"
         f"ACCESSION NUMBER:\t\t{accn}\nCONFORMED SUBMISSION TYPE:\t10-Q\nPUBLIC DOCUMENT COUNT:\t\t5\n"
         f"CONFORMED PERIOD OF REPORT:\t20090627\nFILED AS OF DATE:\t\t{filed}\n"
         + (f"DATE AS OF CHANGE:\t\t{changed}\n" if changed else "")
         + "FILER:\n\tCOMPANY DATA:\n\t\tCENTRAL INDEX KEY:\t\t\t0000320193\n\t\tFISCAL YEAR END:\t\t\t0926\n"
         "\tFILING VALUES:\n\t\tFORM TYPE:\t\t10-Q\n\tFORMER COMPANY:\n\t\tDATE OF NAME CHANGE:\t19970808\n"
         "</SEC-HEADER>\n").encode()
    return h + body


def test_parse_header_checks_cutoff_and_accession_first():
    ok = HS.parse_header(_hdr("20090722"), "0000320193-09-000001")
    assert ok["status"] == "ok"
    f = ok["fields"]
    assert (f["period"], f["fiscal_year_end"], f["form_type"], f["filed"]) == ("20090627", "0926", "10-Q", "20090722")
    assert f["former_name_change_dates"] == ["19970808"]
    assert HS.parse_header(_hdr("20220105"), "0000320193-09-000001") == dict(status="discarded:filed_after_cutoff", fields={})
    assert HS.parse_header(_hdr("20090722", accn="0000320193-09-000009"), "0000320193-09-000001")["status"] == \
        "discarded:accession_mismatch"
    late = HS.parse_header(_hdr("20090722", changed="20230101"), "0000320193-09-000001")
    assert late["status"] == "ok" and "fiscal_year_end" not in late["fields"]
    assert late["fields"]["date_as_of_change_after_cutoff"] is True and late["fields"]["date_as_of_change"] is None


def test_body_after_header_is_never_read():
    raw = _hdr("20090722")
    t = HS.truncate_header(raw)
    assert t.endswith(b"</SEC-HEADER>") and b"SECRET" not in t
    assert len(HS.truncate_header(b"x" * 200000)) == HS.MAX_BYTES


# ----------------------------------------------------------------------------------------------- M-SEQ
def _seq(start="2008-12-31", n=9, kform=4):
    """Calendar-year filer: quarter ends from start, 10-K every 4th (position 0 = 10-K)."""
    out, d = [], date.fromisoformat(start)
    ends = []
    for k in range(n):
        y, m = d.year, d.month + 3 * k
        y += (m - 1) // 12
        m = (m - 1) % 12 + 1
        e = date(y, m, 31 if m in (3, 12) else 30)
        ends.append(e)
    for k, e in enumerate(ends):
        form = "10-K" if k % kform == 0 else "10-Q"
        out.append(((e - date(2000, 1, 1)).days, form, (e - date(2000, 1, 1)).days + 40))
    return out


def test_seq_labels_brackets():
    f = _seq()
    labs = R.seq_labels(f, D=10**6)
    assert [labs[p] for p, _, _ in f] == [4, 1, 2, 3, 4, 1, 2, 3, 4]
    # the second 10-K not yet filed at D: only the first bracket counts
    D = f[4][2]
    labs = R.seq_labels(f, D=D)
    assert all(p not in labs for p, _, _ in f)
    labs = R.seq_labels(f, D=f[4][2] + 1)
    assert [labs.get(p) for p, _, _ in f[:5]] == [4, 1, 2, 3, 4] and f[5][0] not in labs


def test_seq_labels_abstains_on_missing_quarter_transition_and_non_annual():
    f = _seq()
    g = f[:2] + f[3:]                                     # a missing 10-Q breaks the first bracket
    labs = R.seq_labels(g, D=10**6)
    assert f[1][0] not in labs and [labs.get(p) for p, _, _ in f[4:]] == [4, 1, 2, 3, 4]
    labs = R.seq_labels(f, D=10**6, transitions=[f[2][0]])
    assert f[2][0] not in labs and f[6][0] in labs     # transition inside bracket 1 only (+-7 days)
    h = [(p, "10-K" if k in (0, 5) else "10-Q", fd) for k, (p, _, fd) in enumerate(f)]   # 4 10-Qs between 10-Ks
    assert R.seq_labels(h, D=10**6) == {}


def test_dedupe_originals_keeps_earliest_and_drops_other_forms():
    rows = [(100, "10-Q", 140), (103, "10-Q", 130), (190, "8-K", 200), (191, "10-Q/A", 220)]
    assert R.dedupe_originals(rows) == [(100, "10-Q", 130)]


# ----------------------------------------------------------------------------------------------- M-CMP / R*
def test_cmp_label_comparative_presentation():
    p = dn("2008-06-28")
    ev = [("E1", dn("2009-06-27"), dn("2009-07-22"), 3, [(p, 91), (p, 272)]),
          ("E2", dn("2009-09-26"), dn("2009-10-27"), 4, [(dn("2008-09-27"), 364)])]
    assert R.cmp_label(p, ev, D=dn("2010-01-01")) == 3
    assert R.cmp_label(p, ev, D=dn("2009-07-22")) is None              # evidence filed on D: not usable
    assert R.cmp_label(p, ev, D=dn("2010-01-01"), excluded={"E1"}) is None
    bad = [("E3", dn("2009-06-27"), dn("2009-07-22"), 2, [(p, 272)])]   # 9-month fact inconsistent with Q2
    assert R.cmp_label(p, bad, D=dn("2010-01-01")) is None
    two = ev + [("E4", dn("2009-06-30"), dn("2009-08-01"), 2, [(p, 91)])]
    assert R.cmp_label(p, two, D=dn("2010-01-01")) == "conflict"
    near = [("E5", dn("2008-09-27"), dn("2008-10-30"), 4, [(p, 91)])]    # not a prior-year comparative
    assert R.cmp_label(p, near, D=dn("2010-01-01")) is None


def test_combine():
    assert R.combine(2, 2) == (2, "L2")
    assert R.combine(2, 3) == (None, "conflict")
    assert R.combine("conflict", 2) == (None, "conflict")
    assert R.combine(None, 4) == (4, "L3") and R.combine(1, None) == (1, "L3")
    assert R.combine(None, None) == (None, "none")


# ----------------------------------------------------------------------------------------------- H-FYE
def test_h_fye():
    assert R.h_fye("1231", dn("2009-12-31"), "10-K") == 4
    assert R.h_fye("1231", dn("2009-09-30"), "10-Q") == 3
    assert R.h_fye("1231", dn("2009-03-31"), "10-Q") == 1
    assert R.h_fye("0926", dn("2009-06-27"), "10-Q") == 3            # 52/53-week filer
    assert R.h_fye("0102", dn("2009-12-29"), "10-K") == 4            # code drift across the year end
    assert R.h_fye("1231", dn("2009-06-30"), "10-K") == "inconsistent"
    assert R.h_fye("1231", dn("2009-12-31"), "10-Q") is None
    assert R.h_fye("bad", dn("2009-12-31"), "10-Q") is None


# ----------------------------------------------------------------------------------------------- shared rules
def test_label_status_and_rule_v_match_lh_cp2():
    spec = importlib.util.spec_from_file_location("cp2rules_src", ROOT / "research/longhorizon/cp2/LH_CP2_investigation.py")
    src = spec.loader.get_source("cp2rules_src")
    ns = {}
    start = src.index("def label_status")
    end = src.index("def categorize")
    exec(src[start:end], ns)
    rv_s = src.index("def rule_v")
    exec(src[rv_s:src.index("# ---", rv_s)], ns)
    cases = [[4, 3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4], [4, 3, 2, 1, 4, 3, 1, 1, 4, 3, 2, 1, 4],
             [4, 3, None, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4], [1, 4, 3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1]]
    for c in cases:
        assert R.label_status(c) == ns["label_status"](c)
        for t in (False, True):
            for m in (False, True):
                assert R.rule_v(R.label_status(c), t, m) == ns["rule_v"](ns["label_status"](c), t, m)


def test_isolated_off_cycle():
    seq = [1, 2, 3, 4, 1, 2, 3, 4]
    assert R.isolated_off_cycle(seq) == []
    assert R.isolated_off_cycle([1, 2, 2, 4, 1]) == [2]               # Q3 tagged Q2
    assert R.isolated_off_cycle([1, 2, 3, 1, 2, 3]) == []             # persistent shift: neighbours disagree
    assert R.isolated_off_cycle([1, None, 3]) == []


def test_split_is_deterministic_and_balanced():
    assert R.split(320193) == R.split("0000320193")
    s = [R.split(c) for c in range(1, 4001)]
    assert 0.45 < s.count("heldback") / len(s) < 0.55


def test_statistics():
    assert R.cp_upper(0, 300) == pytest.approx(0.00994, abs=2e-4)     # 'rule of three' regime, not zero
    assert R.cp_upper(5, 5) == 1.0 and R.cp_upper(0, 0) is None
    u = R.cluster_upper({i: (0, 10) for i in range(50)} | {"x": (1, 10)})
    assert 0 < u < 0.02
    assert R.cluster_upper({i: (0, 10) for i in range(20)}) == 0.0


@pytest.mark.skipif(not (ROOT / "data/sec_cache").exists(), reason="SEC cache not present")
def test_reg_metadata_cutoff_and_no_network():
    import lh_cp3_data as DATA
    c = DATA.SAFE.client()
    from qr_data_v21 import load_table
    t = load_table()
    reg = DATA.Reg("320193", c, {}, t["f"].get("320193"))
    cut = dn("2021-12-31")
    assert all(p <= cut and fd <= cut for p, _f, fd, _a, _x in reg.sub)
    assert all(e <= cut for v in reg.usd.values() for e, _d in v)
    assert c.fetched == 0
