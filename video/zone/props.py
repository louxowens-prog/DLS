"""Props: the medical pictures (painted, not real scans), the phone, Mae's lab slips, the calendar charts, rubber
stamps, placards, the monitor, the school bus front, the doors of the finale.
"""
import math

import numpy as np
import skia

import draw as D
import zkit as Z
from draw import INK, WHITE, ease, mix, paint, path
from zkit import BLACK, CHALK, GREY

FILM = (22, 24, 26)


def picture(c, kind, x, y, w, h, T=0.0, spot=False, tint=None, label=None):
    """A medical picture on a light box, painted: 'xray', 'mammo', 'ct', 'mri', 'retina', 'skin', 'slide', 'ecg'.
    spot: the tiny speck the Second Eye points at (returns its canvas position)."""
    c.save()
    c.translate(x, y)
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 - 14, -h / 2 - 14, w / 2 + 14, h / 2 + 14), paint((230, 230, 226)))
    c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint(FILM if kind not in ("skin", "slide", "ecg") else (220, 216, 208)))
    c.clipRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2))
    s = min(w, h) / 300
    bone = (214, 214, 210)
    ret = None
    if kind == "xray":
        c.drawLine(0, -h * 0.45, 0, h * 0.45, paint(bone, 0.8, stroke=18 * s))
        for k in range(7):
            yy = -h * 0.32 + k * h * 0.1
            for sx in (-1, 1):
                p = skia.Path()
                p.moveTo(0, yy)
                p.quadTo(sx * w * 0.42, yy - h * 0.06, sx * w * 0.36, yy + h * 0.1)
                c.drawPath(p, paint(bone, 0.75, stroke=8 * s))
        c.drawOval(skia.Rect.MakeLTRB(-w * 0.38, -h * 0.3, -w * 0.05, h * 0.36), paint(WHITE, 0.08))
        c.drawOval(skia.Rect.MakeLTRB(w * 0.05, -h * 0.3, w * 0.38, h * 0.36), paint(WHITE, 0.08))
        ret = (-w * 0.2, h * 0.02)
    elif kind == "mammo":
        p = skia.Path()
        p.moveTo(-w * 0.5, -h * 0.5)
        p.cubicTo(w * 0.5, -h * 0.4, w * 0.5, h * 0.4, -w * 0.5, h * 0.5)
        c.drawPath(p, paint((120, 120, 118)))
        rng = np.random.default_rng(4)
        for k in range(40):
            yy = rng.uniform(-h * 0.4, h * 0.4)
            p = skia.Path()
            p.moveTo(-w * 0.5, yy * 0.6)
            p.quadTo(0, yy, w * 0.2 * (1 - abs(yy) / h), yy * 1.1)
            c.drawPath(p, paint((190, 190, 186), 0.35, stroke=3 * s))
        ret = (w * 0.02, h * 0.1)
    elif kind == "ct":
        c.drawOval(skia.Rect.MakeLTRB(-w * 0.42, -h * 0.34, w * 0.42, h * 0.34), paint((150, 150, 146)))
        c.drawOval(skia.Rect.MakeLTRB(-w * 0.42, -h * 0.34, w * 0.42, h * 0.34), paint(bone, stroke=10 * s))
        c.drawCircle(0, h * 0.2, 22 * s, paint(bone))
        c.drawOval(skia.Rect.MakeLTRB(-w * 0.32, -h * 0.22, -w * 0.04, h * 0.14), paint((60, 60, 58)))
        c.drawOval(skia.Rect.MakeLTRB(w * 0.04, -h * 0.22, w * 0.32, h * 0.14), paint((60, 60, 58)))
        ret = (w * 0.18, -h * 0.05)
    elif kind == "mri":
        c.drawPath(D.smooth([(-w * 0.35, h * 0.1), (-w * 0.3, -h * 0.3), (0, -h * 0.42), (w * 0.34, -h * 0.28), (w * 0.4, h * 0.05),
                             (w * 0.2, h * 0.22), (-w * 0.1, h * 0.18)]), paint((170, 168, 164)))
        for k in range(9):
            a = k * 0.7
            c.drawArc(skia.Rect.MakeLTRB(-w * 0.28 + k * 8, -h * 0.34 + k * 6, w * 0.3 - k * 8, h * 0.1 - k * 4), 180 + k * 10, 150,
                      False, paint((90, 88, 86), stroke=4 * s))
        c.drawPath(D.smooth([(-w * 0.05, h * 0.16), (w * 0.02, h * 0.45), (w * 0.1, h * 0.45), (w * 0.08, h * 0.16)]), paint((150, 148, 144)))
        ret = (w * 0.12, -h * 0.12)
    elif kind == "retina":
        c.drawCircle(0, 0, min(w, h) * 0.46, paint((120, 116, 110)))
        c.drawCircle(-w * 0.14, 0, 20 * s, paint((230, 228, 220)))
        rng = np.random.default_rng(6)
        for k in range(8):
            a0 = k * math.pi / 4 + 0.3
            pts = [(-w * 0.14, 0)]
            for j in range(1, 5):
                pts.append((-w * 0.14 + j * 26 * s * math.cos(a0 + 0.2 * math.sin(j)), j * 26 * s * math.sin(a0 + 0.3 * math.cos(j))))
            c.drawPath(D.smooth(pts, closed=False), paint((40, 38, 36), stroke=4 * s))
        ret = (w * 0.16, h * 0.1)
    elif kind == "skin":
        c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint((200, 176, 160)))
        rng = np.random.default_rng(8)
        for k in range(40):
            c.drawLine(rng.uniform(-w / 2, w / 2), rng.uniform(-h / 2, h / 2), rng.uniform(-w / 2, w / 2), rng.uniform(-h / 2, h / 2),
                       paint((180, 156, 140), 0.3, stroke=2))
        c.drawPath(D.smooth([(-24 * s, -10 * s), (0, -26 * s), (26 * s, -12 * s), (20 * s, 18 * s), (-10 * s, 24 * s)]), paint((70, 50, 44)))
        ret = (0, 0)
    elif kind == "slide":
        c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint((236, 220, 234)))
        rng = np.random.default_rng(9)
        for k in range(70):
            cx, cy = rng.uniform(-w / 2, w / 2), rng.uniform(-h / 2, h / 2)
            r = rng.uniform(8, 16) * s
            c.drawCircle(cx, cy, r, paint((200, 150, 200)))
            c.drawCircle(cx, cy, r * 0.45, paint((90, 50, 120)))
        ret = (w * 0.1, -h * 0.1)
    elif kind == "ecg":
        c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint((240, 226, 222)))
        for gx in np.arange(-w / 2, w / 2, 20 * s):
            c.drawLine(gx, -h / 2, gx, h / 2, paint((220, 170, 170), 0.6, stroke=1.5))
        for gy in np.arange(-h / 2, h / 2, 20 * s):
            c.drawLine(-w / 2, gy, w / 2, gy, paint((220, 170, 170), 0.6, stroke=1.5))
        pts = []
        for i in range(160):
            xx = -w / 2 + w * i / 159
            ph = (i % 40) / 40
            yy = 0.0
            if 0.3 < ph < 0.34:
                yy = -h * 0.05
            if 0.40 < ph < 0.42:
                yy = h * 0.05
            if 0.42 <= ph < 0.45:
                yy = -h * 0.38
            if 0.45 <= ph < 0.48:
                yy = h * 0.12
            if 0.6 < ph < 0.72:
                yy = -h * 0.08 * math.sin((ph - 0.6) / 0.12 * math.pi)
            pts.append((xx, yy))
        c.drawPath(path(pts, closed=False), paint((30, 30, 30), stroke=4 * s))
        ret = (w * 0.1, -h * 0.1)
    if spot and ret is not None:
        c.drawCircle(ret[0], ret[1], 7 * s, paint((250, 250, 250)))
    m = c.getTotalMatrix()
    c.restore()
    if label:
        Z.letters(c, label, x, y + h / 2 + 64, 44, "londrina-900", WHITE, T=T, seed=len(label), tag="picl", outline=BLACK, ow=8)
    if ret is not None:
        p = m.mapXY(*ret)
        return (p.x(), p.y())
    return None


def phone(c, x, y, s, T, lit=True, msg=None, buzz=0.0):
    """Her phone, face up on the table, buzzing, a message on the screen."""
    c.save()
    c.translate(x + (math.sin(T * 70) * 5 * buzz), y)
    c.scale(s, s)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-190, -380, 190, 380), 40, 40), paint((20, 20, 22)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-170, -350, 170, 350), 26, 26), paint((230, 232, 236) if lit else (30, 30, 34)))
    if lit and msg:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-155, -260, 155, 150), 20, 20), paint(WHITE))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-155, -260, 155, 150), 20, 20), paint((150, 150, 150), stroke=3))
        D.text(c, msg[0], -130, -212, 32, "inter-700", (30, 30, 34), align="left", tag="phone")
        for j, ln in enumerate(msg[1:]):
            D.text(c, ln, -130, -160 + j * 44, 29, "inter-500", (40, 40, 44), align="left", tag="phone")
    c.restore()


def slip(c, x, y, s, year, value, T=0.0, rot=0.0, stamp_k=1.0, label="HEMOGLOBIN"):
    """One lab slip: the year, the test, the value, and a NORMAL stamp."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-120, -150, 120, 150), paint((240, 238, 230)))
    c.drawRect(skia.Rect.MakeLTRB(-120, -150, 120, 150), paint((90, 90, 90), stroke=3))
    D.text(c, str(year), 0, -100, 40, "special-elite-400", (40, 40, 40), tag="slip")
    D.text(c, label, 0, -50, 22, "special-elite-400", (60, 60, 60), tag="slip")
    D.text(c, value, 0, 20, 54, "special-elite-400", (20, 20, 20), tag="slip")
    if stamp_k > 0:
        c.save()
        c.translate(0, 95)
        c.rotate(-8)
        c.drawRect(skia.Rect.MakeLTRB(-90, -30, 90, 26), paint((60, 60, 60), stamp_k, stroke=5))
        D.text(c, "NORMAL", 0, 12, 36, "special-elite-400", (60, 60, 60), tag="slip", a=stamp_k)
        c.restore()
    c.restore()


def chart(c, x0, y0, w, h, vals, T, k=1.0, title="", unit="", col=CHALK, tint=None, tint_col=(230, 40, 40), fine=0.0, warn=0.0,
          seed=0, labels=None):
    """A chalk chart on a black flat: one line of values over ten years, drawn in up to k (0..1)."""
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + w, y0 + h), paint((24, 24, 24)))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + w, y0 + h), paint(BLACK, stroke=8))
    Z.letters(c, title, x0 + 20, y0 + 54, 42, "londrina-900", CHALK, T=T, seed=seed, align="left", tag="chartt")
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.3 + 1e-6
    lo, hi = lo - pad, hi + pad
    pts = [(x0 + 40 + (w - 80) * i / (len(vals) - 1), y0 + h - 40 - (h - 120) * (v - lo) / (hi - lo)) for i, v in enumerate(vals)]
    n = max(1, int(round(k * (len(pts) - 1))) + 1)
    c.drawPath(path(Z.wob(pts[:n], 2, seed, T), closed=False), paint(col, stroke=7))
    for px, py in pts[:n]:
        c.drawCircle(px, py, 8, paint(col))
    if labels:
        Z.letters(c, labels[0], pts[0][0] + 10, pts[0][1] - 24, 34, "londrina-400", CHALK, T=T, seed=seed + 1, tag="chartv")
        if n == len(pts):
            Z.letters(c, labels[1], pts[-1][0] - 10, pts[-1][1] - 24, 34, "londrina-400", CHALK, T=T, seed=seed + 2, tag="chartv")
    if fine > 0:
        stamp(c, "FINE", x0 + w / 2, y0 + h / 2 + 40, 70, fine, rot=-10)
    if warn > 0:
        Z.tinted(tint, c, lambda t: t.drawPath(path(pts[:n], closed=False), paint(tint_col, warn, stroke=22)))
    return pts


def stamp(c, text, x, y, size, k, rot=-12, col=BLACK, tint=None, tint_col=(230, 40, 40), T=0.0):
    """A rubber stamp slammed down: overshoots, lands, a double border."""
    if k <= 0:
        return
    sc = 1 + 1.4 * (1 - ease(min(1.0, k * 3)))
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(sc, sc)
    f = D.font("londrina-900", size)
    w = f.measureText(text) + size * 0.6
    r = skia.Rect.MakeLTRB(-w / 2, -size * 0.85, w / 2, size * 0.45)
    c.drawRect(r, paint(WHITE, 0.85))
    c.drawRect(r, paint(col, stroke=size * 0.1))
    D.text(c, text, 0, size * 0.2, size, "londrina-900", col, tag="stamp")
    Z.tinted(tint, c, lambda t: t.drawRect(r, paint(tint_col, 0.9)))
    c.restore()


def placard(c, x, y, w, lines, src=None, T=0.0, k=1.0, rot=0.0, seed=0, size=58, tag="plate", dark=False):
    """A cardboard placard, hand-lettered: the fact, big; the source, small, at the bottom."""
    if k <= 0:
        return
    sizes = [size] + [size * 0.74] * (len(lines) - 1)
    hh = sum(sz * 1.15 for sz in sizes) + (84 if src else 20) + 50
    c.save()
    c.translate(x, y)
    c.rotate(rot + 2 * math.sin(T * 1.3 + seed))
    c.scale(0.4 + 0.6 * ease(k), 0.4 + 0.6 * ease(k))
    bg, fg = ((236, 232, 220), BLACK) if not dark else ((20, 20, 20), CHALK)
    Z.cardboard(c, [(-w / 2, -hh / 2), (w / 2, -hh / 2 + 6), (w / 2 - 4, hh / 2), (-w / 2 + 6, hh / 2 - 4)], bg, T=T, seed=seed, corrugate=False)
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 + 14, -hh / 2 + 14, w / 2 - 14, hh / 2 - 14), paint(fg, stroke=4))
    yy = -hh / 2 + 34
    for j, (ln, sz) in enumerate(zip(lines, sizes)):
        sz = Z.fit(ln, "londrina-900" if j == 0 else "londrina-400", sz, w - 70)
        yy += sz * 1.12
        Z.letters(c, ln, 0, yy, sz, "londrina-900" if j == 0 else "londrina-400", fg, T=T, seed=seed + j, tag=tag, jitter=0.6)
    if src:
        ss = Z.fit(src, "londrina-400", 30, w - 70)
        D.text(c, src, 0, hh / 2 - 34, ss, "londrina-400", mix(fg, (128, 128, 128), 0.4), tag=tag + "s")
    c.restore()


def monitor(c, x, y, w, h, draw_fn):
    """A cardboard monitor on a pole, its screen showing draw_fn(c) (in screen coords 0..w, 0..h)."""
    c.drawRect(skia.Rect.MakeLTRB(x + w / 2 - 12, y + h, x + w / 2 + 12, y + h + 500), paint((70, 70, 70)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 24, y - 24, x + w + 24, y + h + 24), 20, 20), paint((40, 40, 42)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 24, y - 24, x + w + 24, y + h + 24), 20, 20), paint(BLACK, stroke=7))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x, y, x + w, y + h))
    c.translate(x, y)
    draw_fn(c)
    c.restore()


def door2(c, x, y, w, h, label, sub, k_open, T, seed=0, lit=False):
    """A painted doorway in the finale with a sign over it."""
    Z.cardboard(c, [(x - 20, y - 20), (x + w + 20, y - 26), (x + w + 24, y + h), (x - 24, y + h)], (60, 58, 56), T=T, seed=seed)
    c.drawRect(skia.Rect.MakeLTRB(x, y, x + w, y + h), paint((250, 250, 240) if lit else (20, 20, 20)))
    if k_open < 1:
        c.drawRect(skia.Rect.MakeLTRB(x, y, x + w * (1 - k_open), y + h), paint((150, 146, 140)))
        c.drawCircle(x + w * (1 - k_open) - 30, y + h / 2, 12, paint(BLACK))
    Z.letters(c, label, x + w / 2, y - 60, 56, "londrina-900", WHITE, T=T, seed=seed, tag="door" + str(seed), outline=BLACK, ow=8)
    Z.letters(c, sub, x + w / 2, y - 10, 38, "londrina-400", WHITE, T=T, seed=seed + 1, tag="doors" + str(seed), outline=BLACK, ow=6)


def bus_front(c, x, y, s, T, tint=None):
    """The school bus, from the front: Mae at the wheel behind the windscreen (drawn by the caller in between)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    body = (240, 196, 40)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-440, -900, 440, 200), 60, 60), paint(body))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-440, -900, 440, 200), 60, 60), paint(BLACK, stroke=10))
    c.drawRect(skia.Rect.MakeLTRB(-380, -820, 380, -380), paint((200, 226, 240), 0.35))
    c.drawRect(skia.Rect.MakeLTRB(-380, -820, 380, -380), paint(BLACK, stroke=10))
    c.drawLine(0, -820, 0, -380, paint(BLACK, stroke=10))
    c.drawRect(skia.Rect.MakeLTRB(-300, -960, 300, -900), paint(BLACK))
    D.text(c, "SCHOOL BUS", 0, -915, 48, "londrina-900", body, tag="bus")
    for sx in (-1, 1):
        c.drawCircle(sx * 330, -120, 60, paint((250, 250, 230)))
        c.drawCircle(sx * 330, -120, 60, paint(BLACK, stroke=8))
        c.drawRect(skia.Rect.MakeLTRB(sx * 400 - 60, 150, sx * 400 + 60, 320), paint(BLACK))
    for k in range(5):
        c.drawLine(-200, -200 + k * 30, 200, -200 + k * 30, paint(BLACK, stroke=8))
    c.drawRect(skia.Rect.MakeLTRB(-460, 60, 460, 140), paint((60, 60, 60)))
    c.restore()


def windshield_mask(x, y, s):
    return skia.Rect.MakeLTRB(x - 380 * s, y - 820 * s, x + 380 * s, y - 380 * s)
