"""X967 pure helpers (no QuantConnect imports; unit-tested offline in tests/test_fundamental_audit.py).
Every helper returns counts, buckets, dates or ratios: never raw fundamental values (licence)."""
import math
import re

ACCESSION = re.compile(r"^\d{10}-(\d{2})-\d{6}$")
LAG_BUCKETS = (-1, 0, 1, 2, 5, 10, 30, 60, 120, 10 ** 6)          # days; first bucket = negative (look-ahead)
GAP_BUCKETS = (0, 20, 30, 40, 44, 45, 46, 60, 75, 90, 120, 180, 10 ** 6)  # file date - period end, days
RATIO_BUCKETS = (0.0, 0.2, 0.45, 0.9, 0.98, 1.02, 1.1, 2.2, 5.0, 1e18)


def finite(v):
    try:
        return v is not None and isinstance(v, (int, float)) and math.isfinite(float(v))
    except Exception:
        return False


def present(v):
    """A numeric field counts as present if finite and non-zero (Morningstar uses 0/NaN for missing)."""
    return finite(v) and float(v) != 0.0


def accession_year(acc):
    """Filing year encoded in an SEC accession number 'CCCCCCCCCC-YY-NNNNNN' (None if not parseable)."""
    m = ACCESSION.match(str(acc or "").strip())
    if not m:
        return None
    yy = int(m.group(1))
    return 2000 + yy if yy < 50 else 1900 + yy


def bucket(x, edges):
    """Label of the first edge >= x ('<=edge'); edges ascending."""
    for e in edges:
        if x <= e:
            return f"<={e}"
    return f">{edges[-1]}"


def add(hist, key, n=1):
    hist[key] = hist.get(key, 0) + n


def days(a, b):
    """(a - b) in days for date-like objects with .toordinal(), else None."""
    try:
        return a.toordinal() - b.toordinal()
    except Exception:
        return None


def cap_tercile(caps):
    """Map id -> tercile label (T1 smallest) from a dict id -> market cap."""
    order = sorted(caps, key=lambda k: (caps[k], k))
    n = len(order)
    return {k: ("T1" if i < n / 3 else "T2" if i < 2 * n / 3 else "T3") for i, k in enumerate(order)}


def age_bucket(ipo_year, year):
    if ipo_year is None or ipo_year < 1900:
        return "unknown"
    a = year - ipo_year
    return "<3y" if a < 3 else "3-10y" if a < 10 else ">=10y"


def fingerprint(values):
    """Tuple used only to detect CHANGES of a period's values (rounded to 6 significant digits)."""
    out = []
    for v in values:
        out.append(None if not finite(v) else float(f"{float(v):.6g}"))
    return tuple(out)


def rel_change(a, b):
    if not (finite(a) and finite(b)) or b == 0:
        return None
    return abs(float(a) / float(b) - 1.0)
