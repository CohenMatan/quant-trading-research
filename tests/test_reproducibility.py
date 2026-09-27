import gzip
import json
import random

import pandas as pd

from qresearch import results, run
from conftest import ROOT
from test_data_integrity import ORDER


def test_fill_hash_independent_of_payload_order():
    orders = []
    for i in range(20):
        o = json.loads(json.dumps(ORDER))
        o["id"] = i
        o["events"][1]["time"] += 86400 * (i % 5)
        orders.append(o)
    h1 = results.sha256_text(results.canonical_csv(results.parse_fills(orders)))
    random.Random(1).shuffle(orders)
    h2 = results.sha256_text(results.canonical_csv(results.parse_fills(orders)))
    assert h1 == h2


def test_canonical_csv_formats_are_fixed():
    df = pd.DataFrame(dict(date=["2001-01-02"], equity=[100.004999], cash=[1 / 3], npos=[2], nelig=[0]))
    assert results.canonical_csv(df) == "date,equity,cash,npos,nelig\n2001-01-02,100.00,0.33,2,0\n"


def test_gzip_is_byte_deterministic(tmp_path):
    results.write_gz(tmp_path / "a.gz", "x,y\n1,2\n")
    results.write_gz(tmp_path / "b.gz", "x,y\n1,2\n")
    assert (tmp_path / "a.gz").read_bytes() == (tmp_path / "b.gz").read_bytes()
    assert gzip.decompress((tmp_path / "a.gz").read_bytes()) == b"x,y\n1,2\n"


def test_code_hash_is_order_independent():
    a = {"main.py": "x", "qr_params.py": "y"}
    b = {"qr_params.py": "y", "main.py": "x"}
    assert run.code_hash(a) == run.code_hash(b) != run.code_hash({"main.py": "x", "qr_params.py": "z"})


def test_recorded_reproductions_are_identical():
    """Every reproduction run on record must have reproduced its original bit-for-bit."""
    reps = list(ROOT.glob("experiments/E*/reproductions/*/result.json"))
    for p in reps:
        r = json.loads(p.read_text())
        if not r["status"].startswith("completed"):
            continue   # a failed attempt (e.g. download race) stays on record but compares nothing
        assert r["reproduction"]["identical"], p
    assert any(json.loads(p.read_text())["status"].startswith("completed") for p in reps) or not reps
