"""D113 financial/REIT exclusion policy: historical SEC-assigned SIC first, filing structure as fallback."""
from datetime import date

from conftest import ROOT, load_module

I = load_module(ROOT / "src/qresearch/lean/qr_industry.py", "qr_industry_t")


def test_sic_is_point_in_time():
    h = I.SICHistory({"AMT": [["2009-08-07", 4899, 1], ["2012-03-01", 6798, 1]]})
    assert h.sic_on("AMT", date(2009, 8, 6)) is None
    assert h.sic_on("AMT", date(2011, 6, 1)) == 4899 and h.sic_on("AMT", date(2012, 3, 1)) == 6798


def test_classification_and_fallback():
    assert I.classify(6798, False) == ("REIT", "SIC")
    assert I.classify(6324, False) == ("financial", "SIC")          # health insurer
    assert I.classify(6021, None)[0] == "financial" and I.classify(3674, True) == ("operating", "SIC")
    assert I.classify(None, True) == ("financial-format", "filing structure")
    assert I.classify(None, False)[0] == "operating" and I.classify(None, None)[0] == "unclassified"
    assert I.excluded("REIT") and I.excluded("financial-format") and not I.excluded("operating")
