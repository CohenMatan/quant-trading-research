# qr_chart_render.py — H020 frozen-format chart renderer (research/phase5/H020_spec.md section 13; P5-CP2). Pure numpy
# + stdlib PNG encoder (struct, zlib): byte-reproducible, no plotting library, no fonts, no labels. For inspection / audit
# only; no chart image is an input to the H020 score (the score is computed from the numbers in qr_chart). Images of
# QuantConnect data never leave the platform (licence).
#
# Frozen format: panel 1000 x 640 px, white background; price area = top 74% on a LOG scale whose range is the min low /
# max high of the DRAWN bars, widened only to keep the active levels (base pivot, defined support) on screen (all known at
# t), +4% padding; the decision bar t is the last drawn bar, then a blank margin of 6 bar slots; volume panel = bottom
# 20%, scaled to the max volume of the drawn bars; overlays are clipped to their panel; no ticker, date, price or score
# text. Daily panel: last 126 sessions; Weekly panel: last 104 weeks.
import math
import struct
import zlib

import numpy as np

W_PX, H_PX = 1000, 640
PAD = 10
MARGIN_SLOTS = 6
PRICE_FRAC, GAP_FRAC, VOL_FRAC = 0.74, 0.04, 0.20
Y_PAD = 0.04
COL = dict(bg=(255, 255, 255), up=(22, 140, 60), down=(200, 40, 40), vol_up=(150, 205, 165), vol_down=(230, 160, 160),
           ma_fast=(30, 90, 200), ma_mid=(235, 140, 20), ma_slow=(130, 60, 170), zone=(120, 120, 120),
           trend=(0, 0, 0), level=(20, 40, 140), hi52=(150, 150, 150), base=(225, 185, 60), grid=(235, 235, 235))


class Canvas:
    def __init__(self, w=W_PX, h=H_PX):
        self.a = np.empty((h, w, 3), np.uint8)
        self.a[:] = COL["bg"]
        self.w, self.h = w, h
        self.clip = (0, h - 1)                         # vertical clip band (price area while drawing price overlays)

    def rect(self, x0, x1, y0, y1, col, alpha=1.0):
        x0, x1 = sorted((int(round(x0)), int(round(x1))))
        y0, y1 = sorted((int(round(y0)), int(round(y1))))
        x0, y0 = max(x0, 0), max(y0, self.clip[0])
        x1, y1 = min(x1, self.w - 1), min(y1, self.clip[1])
        if x1 < x0 or y1 < y0:
            return
        if alpha >= 1.0:
            self.a[y0:y1 + 1, x0:x1 + 1] = col
        else:   # integer blend: deterministic
            reg = self.a[y0:y1 + 1, x0:x1 + 1].astype(np.int32)
            k = int(round(alpha * 256))
            self.a[y0:y1 + 1, x0:x1 + 1] = ((reg * (256 - k) + np.array(col, np.int32) * k) >> 8).astype(np.uint8)

    def line(self, x0, y0, x1, y1, col, dash=0):
        """Integer Bresenham line (1 px); dash = on/off period in px (0 = solid)."""
        x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err, step = dx + dy, 0
        while True:
            if 0 <= x0 < self.w and self.clip[0] <= y0 <= self.clip[1] and (dash == 0 or (step // dash) % 2 == 0):
                self.a[y0, x0] = col
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
            step += 1

    def png(self):
        raw = b"".join(b"\x00" + self.a[r].tobytes() for r in range(self.h))
        def chunk(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)) +
                chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def render(o, h, l, c, v, n_show, overlays=None):
    """Render the last n_show bars (the decision bar t last). overlays (all optional, all computed from bars <= t):
      mas: list of (series aligned to the input bars, colour key)
      zones: list of (lo_log, hi_log) horizontal S/R zones
      trendlines: list of (i1, log value at i1, slope per bar, dash px; 0 = solid) in input-bar indices
      level: log price of the breakout level; hi52: log price; base_start: input-bar index where the base begins.
    Returns a Canvas."""
    o, h, l, c, v = (np.asarray(a, float)[-n_show:] for a in (o, h, l, c, v))
    n = c.size
    ov = overlays or {}
    cv = Canvas()
    price_h = (H_PX - 2 * PAD) * PRICE_FRAC
    vol_top = PAD + (H_PX - 2 * PAD) * (PRICE_FRAC + GAP_FRAC)
    vol_h = (H_PX - 2 * PAD) * VOL_FRAC
    lo, hi = math.log(l.min()), math.log(h.max())
    for lv in ov.get("include_levels", []):           # active levels (all known at t) are always on screen
        if lv is not None and np.isfinite(lv):
            lo, hi = min(lo, lv), max(hi, lv)
    span = max(hi - lo, 1e-9)
    ymin, ymax = lo - Y_PAD * span, hi + Y_PAD * span
    slot = (W_PX - 2 * PAD) / (n_show + MARGIN_SLOTS)
    body = max(1, int(slot * 0.6))

    def X(j):
        return PAD + (j + 0.5) * slot

    def Y(lp):
        return PAD + (ymax - lp) / (ymax - ymin) * price_h

    n_in = ov.get("n_input", n)
    off = n_in - n                                     # input index of the first drawn bar
    cv.clip = (PAD, int(PAD + price_h))                # price overlays never spill into the volume panel
    for g in range(1, 4):                              # light horizontal grid (fixed fractions)
        cv.line(PAD, PAD + g * price_h / 4, W_PX - PAD, PAD + g * price_h / 4, COL["grid"])
    if ov.get("base_start") is not None and ov["base_start"] - off < n:   # base span: a thin strip under the prices
        j0 = max(0, ov["base_start"] - off)
        cv.rect(X(j0) - slot / 2, X(n - 1) + slot / 2, PAD + price_h - 5, PAD + price_h, COL["base"])
    for zlo, zhi in ov.get("zones", []):
        cv.rect(PAD, X(n - 1) + slot / 2, Y(zhi), Y(zlo), COL["zone"], alpha=0.25)
    if ov.get("hi52") is not None:
        y = Y(ov["hi52"])
        cv.line(PAD, y, W_PX - PAD, y, COL["hi52"], dash=3)
    if ov.get("level") is not None:
        y = Y(ov["level"])
        cv.line(PAD, y, W_PX - PAD, y, COL["level"], dash=6)
    for j in range(n):                                 # candles (price area)
        up = c[j] >= o[j]
        col = COL["up"] if up else COL["down"]
        x = X(j)
        cv.line(x, Y(math.log(h[j])), x, Y(math.log(l[j])), col)
        cv.rect(x - body / 2, x + body / 2 - 1, Y(math.log(max(o[j], c[j]))), Y(math.log(min(o[j], c[j]))), col)
    cv.clip = (0, H_PX - 1)
    vmax = v.max() if v.max() > 0 else 1.0
    for j in range(n):                                 # volume (volume area)
        up = c[j] >= o[j]
        x = X(j)
        vh = v[j] / vmax * vol_h
        cv.rect(x - body / 2, x + body / 2 - 1, vol_top + vol_h - vh, vol_top + vol_h, COL["vol_up" if up else "vol_down"])
    cv.clip = (PAD, int(PAD + price_h))
    for series, key in ov.get("mas", []):
        s = np.asarray(series, float)[-n:]
        pts = [(X(j), Y(math.log(s[j]))) for j in range(n) if np.isfinite(s[j]) and s[j] > 0]
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            if min(ya, yb) >= PAD and max(ya, yb) <= PAD + price_h:
                cv.line(xa, ya, xb, yb, COL[key])
    for i1, p1, slope, dash in ov.get("trendlines", []):
        ja = max(0, i1 - off)
        pa = p1 + slope * (ja + off - i1)
        pb = p1 + slope * (n - 1 + off - i1)
        cv.line(X(ja), Y(pa), X(n - 1), Y(pb), COL["trend"], dash=dash)
    cv.clip = (0, H_PX - 1)
    return cv


def _line(tl, n_input):
    """A qr_chart trendline (value at t) -> (i1, log value at i1, slope)."""
    return tl["i1"], tl["value"] - tl["slope"] * (n_input - 1 - tl["i1"]), tl["slope"]


def daily_overlays(snap, sma_fn, c, n_input):
    """H020 DAILY overlay set: MA20 / MA50 / MA200; the nearest daily resistance and support zones only (at most 2);
    the support trendline (solid) and resistance trendline (dashed); the base pivot level P (dashed); the 52-week high
    (dotted); the base span strip (from the anchor week's last session). The pivot level and the defined support are kept
    on screen."""
    bs = snap["base"]
    lvl = bs["level"] if (bs is not None and bs["valid"]) else None
    tls = []
    if snap["trend_support"] is not None:
        tls.append(_line(snap["trend_support"], n_input) + (0,))
    if snap["trend_resistance"] is not None:
        tls.append(_line(snap["trend_resistance"], n_input) + (4,))
    return dict(n_input=n_input,
                mas=[(sma_fn(c, 20), "ma_fast"), (sma_fn(c, 50), "ma_mid"), (sma_fn(c, 200), "ma_slow")],
                zones=[(z["lo"], z["hi"]) for z in (snap["resistance"], snap["support_zone"]) if z is not None],
                trendlines=tls, level=lvl, hi52=math.log(snap["hi52"]),
                include_levels=[lvl, None if snap["support"] is None else math.log(snap["support"])],
                base_start=snap.get("base_start_day"))


def weekly_overlays(snap, W, sma_fn):
    """H020 WEEKLY overlay set: MA10w / MA30w / MA40w; the nearest weekly (major) resistance and support zones; the base
    pivot level P (dashed). Structure is read from the bars."""
    bs = snap["base"]
    lvl = bs["level"] if (bs is not None and bs["valid"]) else None
    return dict(n_input=len(W["c"]),
                mas=[(sma_fn(W["c"], 10), "ma_fast"), (sma_fn(W["c"], 30), "ma_mid"), (sma_fn(W["c"], 40), "ma_slow")],
                zones=[(z["lo"], z["hi"]) for z in (snap["weekly_resistance"], snap["weekly_support"]) if z is not None],
                level=lvl, include_levels=[lvl])


def render_snapshot(o, h, l, c, v, week_id, snap, sma_fn, weekly_fn):
    """(daily PNG bytes, weekly PNG bytes) of one H020 snapshot."""
    d = render(o, h, l, c, v, 126, daily_overlays(snap, sma_fn, c, len(c))).png()
    W = weekly_fn(o, h, l, c, v, week_id)
    w = render(W["o"], W["h"], W["l"], W["c"], W["v"], 104, weekly_overlays(snap, W, sma_fn)).png()
    return d, w
