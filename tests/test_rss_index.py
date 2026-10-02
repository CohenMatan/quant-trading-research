"""XBRL RSS index parser (D113a): both archive namespaces, instance-name and inline-XBRL schema-name prefixes, and a
hard failure when an archive with items parses to nothing (the first index silently dropped 2020-2021)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "phase2" / "sec"))
import rss_index  # noqa: E402

ITEM = """<item><description>{form}</description>
<edgar:xbrlFiling xmlns:edgar="{ns}">
<edgar:companyName>Example Corp</edgar:companyName><edgar:formType>{form}</edgar:formType>
<edgar:filingDate>02/14/2020</edgar:filingDate><edgar:cikNumber>0000012345</edgar:cikNumber>
<edgar:accessionNumber>0000012345-20-000001</edgar:accessionNumber>
<edgar:acceptanceDatetime>20200214161500</edgar:acceptanceDatetime><edgar:period>20191231</edgar:period>
<edgar:assignedSic>3571</edgar:assignedSic><edgar:fiscalYearEnd>1231</edgar:fiscalYearEnd>
<edgar:xbrlFiles>{files}</edgar:xbrlFiles></edgar:xbrlFiling></item>"""
F = '<edgar:xbrlFile edgar:sequence="{i}" edgar:file="{name}" edgar:type="{typ}" />'


def doc(*items):
    return ('<?xml version="1.0" encoding="windows-1252"?><rss version="2.0"><channel>' + "".join(items)
            + "</channel></rss>").encode("cp1252")


def files(*pairs):
    return "".join(F.format(i=i, name=n, typ=t) for i, (n, t) in enumerate(pairs, 1))


@pytest.mark.parametrize("ns", rss_index.NAMESPACES)
def test_both_namespaces_and_instance_prefix(ns):
    rows = rss_index.parse(doc(ITEM.format(ns=ns, form="10-K", files=files(
        ("exm-20191231.xml", "EX-101.INS"), ("exm-20191231.xsd", "EX-101.SCH")))))
    assert len(rows) == 1
    r = rows[0]
    assert (r["cik"], r["form"], r["filed"], r["sic"], r["prefix"], r["instance"]) == \
        (12345, "10-K", "2020-02-14", 3571, "EXM", "exm-20191231.xml")


def test_inline_xbrl_uses_schema_name():
    ns = rss_index.NAMESPACES[1]
    rows = rss_index.parse(doc(ITEM.format(ns=ns, form="10-Q", files=files(
        ("d123d10q.htm", "10-Q"), ("exm-20200331.xsd", "EX-101.SCH"), ("exm-20200331_lab.xml", "EX-101.LAB")))))
    assert rows[0]["prefix"] == "EXM" and rows[0]["instance"] == "exm-20200331.xsd"


def test_instance_preferred_over_schema():
    rows = rss_index.parse(doc(ITEM.format(ns=rss_index.NAMESPACES[0], form="10-K", files=files(
        ("abc-20191231.xsd", "EX-101.SCH"), ("xyz-20191231.xml", "EX-101.INS")))))
    assert rows[0]["prefix"] == "XYZ"


def test_unknown_namespace_fails_loudly():
    with pytest.raises(ValueError):
        rss_index.parse(doc(ITEM.format(ns="https://example.invalid/edgar", form="10-K", files="")))
