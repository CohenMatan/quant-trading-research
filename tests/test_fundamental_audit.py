"""X967 fundamental-audit helpers (pure; no QuantConnect). The audit reports counts, buckets, dates, accession
years and ratios only, never raw fundamental values (licence)."""
from datetime import date

from conftest import ROOT, load_module

L = load_module(ROOT / "strategies/X967_fundamental_audit/audit_lib.py", "x967_lib")


def test_accession_year():
    assert L.accession_year("0000320193-14-000005") == 2014
    assert L.accession_year("0001193125-09-153165") == 2009
    assert L.accession_year("0000000000-99-000001") == 1999
    assert L.accession_year("garbage") is None and L.accession_year(None) is None


def test_present_and_finite():
    assert L.present(1.5) and not L.present(0.0) and not L.present(float("nan")) and not L.present(None)
    assert L.finite(0.0) and not L.finite("x")


def test_buckets_and_days():
    assert L.bucket(-3, L.LAG_BUCKETS) == "<=-1" and L.bucket(0, L.LAG_BUCKETS) == "<=0"
    assert L.bucket(45, L.GAP_BUCKETS) == "<=45" and L.bucket(46, L.GAP_BUCKETS) == "<=46"
    assert L.days(date(2021, 2, 15), date(2020, 12, 31)) == 46 and L.days(None, date(2020, 1, 1)) is None


def test_terciles_age_fingerprint():
    t = L.cap_tercile({"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6})
    assert [t[k] for k in "abcdef"] == ["T1", "T1", "T2", "T2", "T3", "T3"]
    assert L.age_bucket(2008, 2010) == "<3y" and L.age_bucket(None, 2010) == "unknown" and L.age_bucket(1990, 2010) == ">=10y"
    assert L.fingerprint([1.0000001, None]) == L.fingerprint([1.0000002, float("nan")])
    assert L.fingerprint([1.0]) != L.fingerprint([1.01])
    assert abs(L.rel_change(110, 100) - 0.10) < 1e-12 and L.rel_change(1, 0) is None


def test_audit_never_logs_raw_values():
    """The audit's log lines carry dates, accession numbers, buckets and ratios only: no raw field values."""
    src = (ROOT / "strategies/X967_fundamental_audit/main.py").read_text()
    for line in [l for l in src.splitlines() if "_qr_log(" in l or "self._ex(" in l]:
        assert "get(f, path)" not in line and ".three_months" not in line
